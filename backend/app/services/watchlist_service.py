"""Watchlist service — manages watchlist items and triggers OSINT checks."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.watchlist import WatchlistItem, WatchlistResult
from app.models.notification import Notification

logger = logging.getLogger(__name__)

# Map watchlist type → default services to query
TYPE_DEFAULT_SERVICES: dict[str, list[str]] = {
    "email": ["hibp", "intelx", "hudsonrock"],
    "domain": ["virustotal", "urlhaus", "securitytrails", "censys"],
    "ip": ["shodan", "abuseipdb", "alienvault_otx"],
    "keyword": ["intelx"],
    "brand": ["securitytrails", "virustotal", "urlhaus"],
}


def _hash_result(data: dict | list) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


async def get_user_watchlist(db: AsyncSession, user_id: int) -> list[WatchlistItem]:
    result = await db.execute(
        select(WatchlistItem).where(WatchlistItem.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_watchlist_item(db: AsyncSession, item_id: int, user_id: int) -> WatchlistItem | None:
    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.id == item_id, WatchlistItem.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def create_watchlist_item(
    db: AsyncSession,
    user_id: int,
    type_: str,
    value: str,
    services: list[str] | None = None,
    schedule: str | None = None,
) -> WatchlistItem:
    if services is None:
        services = TYPE_DEFAULT_SERVICES.get(type_, [])
    item = WatchlistItem(
        user_id=user_id,
        type=type_,
        value=value,
        services=services,
        schedule=schedule,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def update_watchlist_item(
    db: AsyncSession,
    item: WatchlistItem,
    **kwargs,
) -> WatchlistItem:
    for key, val in kwargs.items():
        if hasattr(item, key):
            setattr(item, key, val)
    await db.flush()
    await db.refresh(item)
    return item


async def delete_watchlist_item(db: AsyncSession, item: WatchlistItem) -> None:
    await db.delete(item)


async def get_watchlist_history(
    db: AsyncSession, item_id: int, limit: int = 20
) -> list[WatchlistResult]:
    result = await db.execute(
        select(WatchlistResult)
        .where(WatchlistResult.watchlist_item_id == item_id)
        .order_by(WatchlistResult.checked_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def record_watchlist_result(
    db: AsyncSession,
    item: WatchlistItem,
    result_data: dict,
) -> tuple[WatchlistResult, bool]:
    """Store result and return (result_record, is_new_finding)."""
    new_hash = _hash_result(result_data)
    is_new = item.last_result_hash != new_hash
    has_findings = bool(result_data.get("findings"))

    record = WatchlistResult(
        watchlist_item_id=item.id,
        result_data=result_data,
        result_hash=new_hash,
        has_findings=has_findings,
    )
    db.add(record)

    item.last_checked = datetime.now(timezone.utc)
    item.last_result_hash = new_hash

    await db.flush()
    return record, is_new and has_findings


async def get_active_due_items(db: AsyncSession) -> list[WatchlistItem]:
    """Return active watchlist items that are due for a check (simplified: all active)."""
    result = await db.execute(
        select(WatchlistItem).where(WatchlistItem.is_active == True)  # noqa: E712
    )
    return list(result.scalars().all())
