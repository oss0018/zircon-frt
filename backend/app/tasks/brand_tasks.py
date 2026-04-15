"""Brand protection Celery tasks."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="app.tasks.brand_tasks.daily_brand_scan",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def daily_brand_scan(self):
    """Run brand scan for all active brand watches."""
    logger.info("[brand] Starting daily brand scan")
    try:
        return _run_async(_daily_brand_scan_async())
    except Exception as exc:
        logger.error("[brand] Daily scan error: %s", exc)
        raise self.retry(exc=exc)


async def _daily_brand_scan_async() -> dict:
    from app.db.session import AsyncSessionLocal
    from app.models.brand import BrandWatch
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(BrandWatch).where(BrandWatch.is_active == True)  # noqa: E712
        )
        watches = result.scalars().all()

    dispatched = 0
    for watch in watches:
        deep_brand_scan.delay(watch.id)
        dispatched += 1

    logger.info("[brand] Dispatched %d brand scan tasks", dispatched)
    return {"dispatched": dispatched}


@celery_app.task(
    name="app.tasks.brand_tasks.deep_brand_scan",
    bind=True,
    max_retries=2,
    default_retry_delay=120,
)
def deep_brand_scan(self, brand_watch_id: int):
    """Comprehensive scan for a single brand watch."""
    logger.info("[brand] Deep scan for brand_watch %d", brand_watch_id)
    try:
        return _run_async(_deep_brand_scan_async(brand_watch_id))
    except Exception as exc:
        logger.error("[brand] Deep scan error for %d: %s", brand_watch_id, exc)
        raise self.retry(exc=exc)


async def _deep_brand_scan_async(brand_watch_id: int) -> dict:
    from app.db.session import AsyncSessionLocal
    from app.models.brand import BrandWatch, BrandAlert
    from app.services.brand_service import run_brand_scan
    from app.services.notification_service import create_notification
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        async with db.begin():
            result = await db.execute(
                select(BrandWatch).where(BrandWatch.id == brand_watch_id)
            )
            watch = result.scalar_one_or_none()
            if not watch:
                return {"error": "not_found"}

            findings = await run_brand_scan(
                original_url=watch.original_url,
                keywords=watch.keywords or [],
                threshold=watch.similarity_threshold,
            )

            new_alert_count = 0
            for finding in findings:
                # Check if alert already exists for this domain
                existing = await db.execute(
                    select(BrandAlert).where(
                        BrandAlert.brand_watch_id == brand_watch_id,
                        BrandAlert.found_domain == finding["found_domain"],
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                alert = BrandAlert(
                    brand_watch_id=brand_watch_id,
                    found_domain=finding["found_domain"],
                    similarity_score=finding["similarity_score"],
                    detection_sources=finding["detection_sources"],
                    screenshot_url=finding.get("screenshot_url"),
                )
                db.add(alert)
                new_alert_count += 1

            watch.last_scan = datetime.now(timezone.utc)

            await db.flush()

            if new_alert_count:
                await create_notification(
                    db=db,
                    user_id=watch.user_id,
                    type_="brand",
                    title=f"Brand Alert: {watch.name}",
                    message=f"{new_alert_count} new look-alike domain(s) detected",
                )

            return {
                "brand_watch_id": brand_watch_id,
                "findings": len(findings),
                "new_alerts": new_alert_count,
            }


@celery_app.task(
    name="app.tasks.brand_tasks.generate_typosquats",
    bind=True,
)
def generate_typosquats(self, domain: str) -> list[str]:
    """Generate typosquatting variations for a domain."""
    from app.services.brand_service import generate_typosquats as _gen

    variants = _gen(domain)
    logger.info("[brand] Generated %d typosquats for %s", len(variants), domain)
    return variants
