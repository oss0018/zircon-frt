"""Monitoring Celery tasks — folder scan, watchlist polling, scheduled searches."""
from __future__ import annotations

import asyncio
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="app.tasks.monitoring_tasks.rescan_monitored_folder",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def rescan_monitored_folder(self):
    """Scan /app/monitored/ for new or changed files."""
    logger.info("[monitoring] Starting folder rescan")
    try:
        from app.services.monitoring_service import scan_monitored_folder

        result = scan_monitored_folder()
        new_count = len(result["new_files"])
        changed_count = len(result["changed_files"])

        logger.info(
            "[monitoring] Folder scan done: %d new, %d changed",
            new_count,
            changed_count,
        )

        if new_count or changed_count:
            _run_async(_notify_folder_findings(result))

        return result
    except Exception as exc:
        logger.error("[monitoring] Folder rescan error: %s", exc)
        raise self.retry(exc=exc)


async def _notify_folder_findings(scan_result: dict) -> None:
    from app.db.session import AsyncSessionLocal
    from app.services.notification_service import create_notification
    from app.models.user import User
    from sqlalchemy import select

    new_files = scan_result.get("new_files", [])
    changed_files = scan_result.get("changed_files", [])

    async with AsyncSessionLocal() as db:
        async with db.begin():
            result = await db.execute(select(User).where(User.is_admin == True))  # noqa: E712
            admins = result.scalars().all()
            for admin in admins:
                msg = ""
                if new_files:
                    msg += f"New files: {', '.join(new_files[:3])}"
                    if len(new_files) > 3:
                        msg += f" (+{len(new_files) - 3} more)"
                if changed_files:
                    if msg:
                        msg += "\n"
                    msg += f"Changed files: {', '.join(changed_files[:3])}"
                await create_notification(
                    db=db,
                    user_id=admin.id,
                    type_="info",
                    title=f"Folder Monitor: {len(new_files)} new, {len(changed_files)} changed",
                    message=msg,
                )


@celery_app.task(
    name="app.tasks.monitoring_tasks.check_watchlist_item",
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def check_watchlist_item(self, item_id: int):
    """Run OSINT checks for a single watchlist item."""
    logger.info("[watchlist] Checking item %d", item_id)
    try:
        return _run_async(_check_watchlist_item_async(item_id))
    except Exception as exc:
        logger.error("[watchlist] Error checking item %d: %s", item_id, exc)
        raise self.retry(exc=exc)


async def _check_watchlist_item_async(item_id: int) -> dict:
    from app.db.session import AsyncSessionLocal
    from app.models.watchlist import WatchlistItem
    from app.services.watchlist_service import record_watchlist_result
    from app.services.notification_service import create_notification
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        async with db.begin():
            result = await db.execute(
                select(WatchlistItem).where(WatchlistItem.id == item_id)
            )
            item = result.scalar_one_or_none()
            if not item:
                logger.warning("[watchlist] Item %d not found", item_id)
                return {"error": "not_found"}

            # Placeholder — in production, call actual OSINT services
            mock_result = {
                "item_id": item_id,
                "type": item.type,
                "value": item.value,
                "services_checked": item.services or [],
                "findings": [],
            }

            record, is_new_finding = await record_watchlist_result(db, item, mock_result)

            if is_new_finding:
                await create_notification(
                    db=db,
                    user_id=item.user_id,
                    type_="alert",
                    title=f"Watchlist Alert: {item.type} — {item.value}",
                    message=f"New findings for {item.value}",
                )
                logger.info("[watchlist] New findings for item %d", item_id)

            return mock_result


@celery_app.task(
    name="app.tasks.monitoring_tasks.run_scheduled_search",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def run_scheduled_search(self, template_id: int):
    """Execute a saved search template."""
    logger.info("[search] Running scheduled search template %d", template_id)
    try:
        return _run_async(_run_scheduled_search_async(template_id))
    except Exception as exc:
        logger.error("[search] Error running template %d: %s", template_id, exc)
        raise self.retry(exc=exc)


async def _run_scheduled_search_async(template_id: int) -> dict:
    from app.db.session import AsyncSessionLocal
    from app.models.search_template import SearchTemplate
    from app.services.search_template_service import run_template
    from app.services.notification_service import create_notification
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        async with db.begin():
            result = await db.execute(
                select(SearchTemplate).where(SearchTemplate.id == template_id)
            )
            template = result.scalar_one_or_none()
            if not template:
                return {"error": "not_found"}

            search_result = await run_template(db, template)
            total = search_result.get("total", 0)

            if total > 0:
                await create_notification(
                    db=db,
                    user_id=template.user_id,
                    type_="info",
                    title=f"Saved Search: {template.name}",
                    message=f"Found {total} results for query: {template.query}",
                )

            return search_result


@celery_app.task(
    name="app.tasks.monitoring_tasks.poll_osint_watchlist",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def poll_osint_watchlist(self):
    """Iterate all active watchlist items due for check and dispatch individual tasks."""
    logger.info("[watchlist] Starting watchlist poll")
    try:
        return _run_async(_poll_watchlist_async())
    except Exception as exc:
        logger.error("[watchlist] Poll error: %s", exc)
        raise self.retry(exc=exc)


async def _poll_watchlist_async() -> dict:
    from app.db.session import AsyncSessionLocal
    from app.services.watchlist_service import get_active_due_items

    async with AsyncSessionLocal() as db:
        items = await get_active_due_items(db)

    dispatched = 0
    for item in items:
        check_watchlist_item.delay(item.id)
        dispatched += 1

    logger.info("[watchlist] Dispatched %d check tasks", dispatched)
    return {"dispatched": dispatched}
