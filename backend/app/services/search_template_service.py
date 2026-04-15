"""Search template service — save/schedule/run search templates."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_template import SearchTemplate

logger = logging.getLogger(__name__)


async def get_user_templates(db: AsyncSession, user_id: int) -> list[SearchTemplate]:
    result = await db.execute(
        select(SearchTemplate).where(SearchTemplate.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_template(
    db: AsyncSession, template_id: int, user_id: int
) -> SearchTemplate | None:
    result = await db.execute(
        select(SearchTemplate).where(
            SearchTemplate.id == template_id, SearchTemplate.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def create_template(
    db: AsyncSession,
    user_id: int,
    name: str,
    query: str,
    filters: dict | None = None,
    schedule: str | None = None,
) -> SearchTemplate:
    tmpl = SearchTemplate(
        user_id=user_id,
        name=name,
        query=query,
        filters=filters,
        schedule=schedule,
    )
    db.add(tmpl)
    await db.flush()
    await db.refresh(tmpl)
    return tmpl


async def update_template(
    db: AsyncSession, template: SearchTemplate, **kwargs
) -> SearchTemplate:
    for key, val in kwargs.items():
        if hasattr(template, key):
            setattr(template, key, val)
    await db.flush()
    await db.refresh(template)
    return template


async def delete_template(db: AsyncSession, template: SearchTemplate) -> None:
    await db.delete(template)


async def run_template(db: AsyncSession, template: SearchTemplate) -> dict:
    """Execute the saved search and return results."""
    from app.services.search_service import search_documents

    logger.info("Running scheduled search template %d: %s", template.id, template.name)
    try:
        results = await search_documents(
            query=template.query,
            filters=template.filters or {},
            page=1,
            page_size=20,
        )
        return {
            "template_id": template.id,
            "query": template.query,
            "run_at": datetime.now(timezone.utc).isoformat(),
            "total": results.get("total", 0),
            "hits": results.get("hits", []),
        }
    except Exception as exc:
        logger.error("Search template run failed: %s", exc)
        return {"error": str(exc), "template_id": template.id}
