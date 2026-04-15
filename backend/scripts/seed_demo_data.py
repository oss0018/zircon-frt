#!/usr/bin/env python3
"""Seed demo data for development."""
import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.project import Project
from app.models.user import User
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        # Get or create demo user
        result = await db.execute(select(User).where(User.email == "demo@zircon.local"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                email="demo@zircon.local",
                username="demo",
                hashed_password=hash_password("demo123"),
            )
            db.add(user)
            await db.flush()
            logger.info("Created demo user")

        # Create demo projects
        projects = ["OSINT Investigation Alpha", "Brand Monitoring", "Threat Intel"]
        for name in projects:
            result = await db.execute(
                select(Project).where(Project.name == name, Project.user_id == user.id)
            )
            if not result.scalar_one_or_none():
                db.add(Project(name=name, description=f"Demo project: {name}", user_id=user.id))
                logger.info("Created project: %s", name)

        await db.commit()
        logger.info("Demo data seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
