"""Folder monitoring service — watches /app/monitored/ for new/changed files."""
from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

MONITORED_DIR = Path(os.getenv("MONITORED_DIR", "/app/monitored"))

# In-memory state for file hashes (persisted via Celery task state)
_file_hashes: dict[str, str] = {}


def _hash_file(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def scan_monitored_folder() -> dict:
    """Scan the monitored folder and return new/changed files."""
    global _file_hashes

    if not MONITORED_DIR.exists():
        MONITORED_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("Created monitored directory: %s", MONITORED_DIR)

    new_files: list[str] = []
    changed_files: list[str] = []
    all_paths: set[str] = set()

    for entry in MONITORED_DIR.rglob("*"):
        if not entry.is_file():
            continue

        path_str = str(entry)
        all_paths.add(path_str)

        try:
            current_hash = _hash_file(entry)
        except OSError as exc:
            logger.warning("Cannot hash %s: %s", path_str, exc)
            continue

        if path_str not in _file_hashes:
            new_files.append(path_str)
            logger.info("New file detected: %s", path_str)
        elif _file_hashes[path_str] != current_hash:
            changed_files.append(path_str)
            logger.info("Changed file detected: %s", path_str)

        _file_hashes[path_str] = current_hash

    # Remove stale entries
    removed = set(_file_hashes.keys()) - all_paths
    for p in removed:
        del _file_hashes[p]

    return {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "total_files": len(all_paths),
        "new_files": new_files,
        "changed_files": changed_files,
        "monitored_dir": str(MONITORED_DIR),
    }


def get_folder_status() -> dict:
    return {
        "monitored_dir": str(MONITORED_DIR),
        "exists": MONITORED_DIR.exists(),
        "tracked_files": len(_file_hashes),
        "last_known_hashes": list(_file_hashes.keys()),
    }
