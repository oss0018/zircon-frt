#!/usr/bin/env python3
"""Initialize the database with admin user and Elasticsearch indices."""
import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.services.indexer import ensure_index

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
        existing = result.scalar_one_or_none()
        if existing:
            logger.info("Admin user already exists: %s", settings.ADMIN_EMAIL)
            return

        admin = User(
            email=settings.ADMIN_EMAIL,
            username=settings.ADMIN_USERNAME,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_active=True,
            is_admin=True,
        )
        db.add(admin)
        await db.commit()
        logger.info("Created admin user: %s", settings.ADMIN_EMAIL)


async def main() -> None:
    logger.info("Initializing database...")
    await create_admin()
    logger.info("Ensuring Elasticsearch indices...")
    await ensure_index()
    logger.info("Initialization complete.")


if __name__ == "__main__":
    asyncio.run(main())
