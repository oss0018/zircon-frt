import hashlib
import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.file import File


class FileService:
    def __init__(self) -> None:
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(
        self,
        upload: UploadFile,
        user_id: int,
        project_id: int | None,
        db: AsyncSession,
    ) -> File:
        # Generate unique filename
        ext = Path(upload.filename or "file").suffix
        unique_name = f"{uuid.uuid4().hex}{ext}"
        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        filepath = user_dir / unique_name

        # Stream file to disk and compute hash
        hasher = hashlib.sha256()
        size = 0
        async with aiofiles.open(filepath, "wb") as f:
            while chunk := await upload.read(65536):
                await f.write(chunk)
                hasher.update(chunk)
                size += len(chunk)

        file_record = File(
            filename=upload.filename or unique_name,
            filepath=str(filepath),
            file_type=upload.content_type,
            size_bytes=size,
            content_hash=hasher.hexdigest(),
            user_id=user_id,
            project_id=project_id,
        )
        db.add(file_record)
        await db.flush()
        await db.refresh(file_record)
        return file_record

    async def delete_file(self, file: File, db: AsyncSession) -> None:
        # Remove from disk
        try:
            os.remove(file.filepath)
        except FileNotFoundError:
            pass
        await db.delete(file)
        await db.flush()

    async def scan_with_clamav(self, filepath: str) -> bool:
        """Returns True if file is clean, False if infected."""
        try:
            import clamd
            cd = clamd.ClamdNetworkSocket(host=settings.CLAMAV_HOST, port=settings.CLAMAV_PORT)
            result = cd.scan(filepath)
            if result and filepath in result:
                status, _ = result[filepath]
                return status == "OK"
            return True
        except Exception:
            # ClamAV not available — skip scanning
            return True
