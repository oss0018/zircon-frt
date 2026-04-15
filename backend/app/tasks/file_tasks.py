import asyncio
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_uploaded_file(self, file_id: int) -> dict:
    """Process uploaded file: scan → parse → index."""
    try:
        return asyncio.run(_process_file(file_id))
    except Exception as exc:
        logger.error("Failed to process file %d: %s", file_id, exc)
        raise self.retry(exc=exc)


async def _process_file(file_id: int) -> dict:
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    from app.models.file import File
    from app.services.file_service import FileService
    from app.services.indexer import index_file
    from app.parsers.factory import get_parser

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(File).where(File.id == file_id))
        file = result.scalar_one_or_none()
        if not file:
            return {"status": "not_found", "file_id": file_id}

        # 1. ClamAV scan
        service = FileService()
        is_clean = await service.scan_with_clamav(file.filepath)
        if not is_clean:
            file.quarantined = True
            await db.commit()
            logger.warning("File %d quarantined (virus detected)", file_id)
            return {"status": "quarantined", "file_id": file_id}

        # 2. Parse content
        parser = get_parser(file.filepath)
        content = parser.parse(file.filepath) if parser else ""

        # 3. Index in Elasticsearch
        await index_file(
            file_id=file.id,
            filename=file.filename,
            content=content,
            file_type=file.file_type,
            project_id=file.project_id,
            user_id=file.user_id,
            size_bytes=file.size_bytes,
            created_at=file.created_at,
        )

        file.indexed = True
        await db.commit()
        return {"status": "indexed", "file_id": file_id}
