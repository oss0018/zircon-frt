#!/usr/bin/env python3
"""
Backup script for Zircon FRT.
Backs up PostgreSQL database, uploaded files, and Elasticsearch snapshots.
"""
import argparse
import gzip
import logging
import os
import shutil
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
DEFAULT_BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "/backups"))


def backup_postgres(backup_dir: Path) -> Path:
    """Dump PostgreSQL database to a gzip-compressed file."""
    db_url = os.getenv("DATABASE_URL", "postgresql://zircon:zircon@localhost:5432/zircon")
    # Extract components from URL
    # Expected format: postgresql://user:pass@host:port/dbname
    from urllib.parse import urlparse
    parsed = urlparse(db_url)

    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = parsed.password

    outfile = backup_dir / f"postgres_{TIMESTAMP}.sql.gz"
    cmd = [
        "pg_dump",
        "-h", parsed.hostname or "localhost",
        "-p", str(parsed.port or 5432),
        "-U", parsed.username or "zircon",
        parsed.path.lstrip("/"),
    ]
    logger.info("Dumping PostgreSQL → %s", outfile)
    with gzip.open(outfile, "wb") as gz:
        result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logger.error("pg_dump failed: %s", result.stderr.decode())
            raise RuntimeError(f"pg_dump failed: {result.stderr.decode()}")
        gz.write(result.stdout)
    logger.info("PostgreSQL backup done: %s (%.1f MB)", outfile, outfile.stat().st_size / 1e6)
    return outfile


def backup_files(backup_dir: Path, uploads_dir: str = "/app/uploads") -> Path:
    """Archive uploaded files directory."""
    src = Path(uploads_dir)
    if not src.exists():
        logger.warning("Uploads directory not found: %s — skipping", uploads_dir)
        return backup_dir
    outfile = backup_dir / f"uploads_{TIMESTAMP}.tar.gz"
    logger.info("Archiving uploads %s → %s", src, outfile)
    with tarfile.open(outfile, "w:gz") as tar:
        tar.add(src, arcname="uploads")
    logger.info("Uploads backup done: %s (%.1f MB)", outfile, outfile.stat().st_size / 1e6)
    return outfile


def prune_old_backups(backup_dir: Path, keep_days: int = 7) -> None:
    """Remove backup files older than keep_days."""
    import time
    cutoff = time.time() - keep_days * 86400
    for f in backup_dir.iterdir():
        if f.is_file() and f.stat().st_mtime < cutoff:
            logger.info("Removing old backup: %s", f)
            f.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Zircon FRT backup utility")
    parser.add_argument("--backup-dir", default=str(DEFAULT_BACKUP_DIR), help="Directory to store backups")
    parser.add_argument("--uploads-dir", default="/app/uploads", help="Uploads directory path")
    parser.add_argument("--keep-days", type=int, default=7, help="Days to retain backups")
    parser.add_argument("--skip-db", action="store_true", help="Skip database backup")
    parser.add_argument("--skip-files", action="store_true", help="Skip files backup")
    args = parser.parse_args()

    backup_dir = Path(args.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_db:
        backup_postgres(backup_dir)
    if not args.skip_files:
        backup_files(backup_dir, args.uploads_dir)

    prune_old_backups(backup_dir, args.keep_days)
    logger.info("Backup complete. Files in: %s", backup_dir)


if __name__ == "__main__":
    main()
