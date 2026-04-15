"""Full integration management API — CRUD, health check, unified search, usage stats."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.core.cache import cache_get, cache_set
from app.db.session import get_db
from app.integrations import registry
from app.models.api_usage_log import APIUsageLog
from app.models.integration import Integration
from app.models.user import User
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationDetailResponse,
    IntegrationResponse,
    IntegrationUpdate,
    ServiceCatalogueEntry,
    TestConnectionResponse,
    UnifiedSearchRequest,
    UnifiedSearchResponse,
    UnifiedSearchResult,
    UsageStatsEntry,
)
from app.services.crypto import CryptoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _crypto() -> CryptoService:
    return CryptoService()


async def _get_user_integration(
    integration_id: int, user: User, db: AsyncSession
) -> Integration:
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id, Integration.user_id == user.id
        )
    )
    obj = result.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    return obj


async def _log_usage(
    db: AsyncSession,
    service: str,
    endpoint: str,
    status_code: int,
    response_time_ms: float,
    user_id: int,
) -> None:
    log = APIUsageLog(
        service_name=service,
        endpoint=endpoint,
        status_code=status_code,
        response_time_ms=response_time_ms,
        user_id=user_id,
    )
    db.add(log)


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.get("/available", response_model=list[ServiceCatalogueEntry])
async def list_available_services(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ServiceCatalogueEntry]:
    """Return all available integration services with configuration status."""
    result = await db.execute(
        select(Integration).where(Integration.user_id == current_user.id)
    )
    configured = {i.service_name: i for i in result.scalars().all()}

    entries = []
    for info in registry.list_available():
        name = info["name"]
        integration = configured.get(name)
        entries.append(
            ServiceCatalogueEntry(
                name=name,
                display_name=info.get("display_name", name),
                description=info.get("description", ""),
                category=info.get("category", ""),
                website=info.get("website", ""),
                query_types=info.get("query_types", []),
                rate_limit=info.get("rate_limit", 60),
                docs_url=info.get("docs_url", ""),
                is_configured=integration is not None,
                is_active=integration.is_active if integration else False,
            )
        )
    return entries


@router.get("/", response_model=list[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[IntegrationResponse]:
    result = await db.execute(
        select(Integration).where(Integration.user_id == current_user.id)
    )
    return [IntegrationResponse.model_validate(i) for i in result.scalars().all()]


@router.post("/", response_model=IntegrationDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    request: IntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IntegrationDetailResponse:
    existing = await db.execute(
        select(Integration).where(
            Integration.user_id == current_user.id,
            Integration.service_name == request.service_name,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Integration '{request.service_name}' already exists",
        )

    crypto = _crypto()
    encrypted_key = crypto.encrypt(request.api_key) if request.api_key else None
    integration = Integration(
        service_name=request.service_name,
        api_key_encrypted=encrypted_key,
        user_id=current_user.id,
    )
    db.add(integration)
    await db.flush()
    await db.refresh(integration)
    return IntegrationDetailResponse.model_validate(integration)


@router.get("/{integration_id}", response_model=IntegrationDetailResponse)
async def get_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IntegrationDetailResponse:
    obj = await _get_user_integration(integration_id, current_user, db)
    return IntegrationDetailResponse.model_validate(obj)


@router.put("/{integration_id}", response_model=IntegrationDetailResponse)
async def update_integration(
    integration_id: int,
    request: IntegrationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IntegrationDetailResponse:
    obj = await _get_user_integration(integration_id, current_user, db)
    if request.api_key is not None:
        crypto = _crypto()
        obj.api_key_encrypted = crypto.encrypt(request.api_key)
    if request.is_active is not None:
        obj.is_active = request.is_active
    await db.flush()
    await db.refresh(obj)
    return IntegrationDetailResponse.model_validate(obj)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    obj = await _get_user_integration(integration_id, current_user, db)
    await db.delete(obj)


# ---------------------------------------------------------------------------
# Test connection / health check
# ---------------------------------------------------------------------------

@router.post("/{integration_id}/test", response_model=TestConnectionResponse)
async def test_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TestConnectionResponse:
    obj = await _get_user_integration(integration_id, current_user, db)
    if not obj.api_key_encrypted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No API key configured"
        )

    crypto = _crypto()
    api_key = crypto.decrypt(obj.api_key_encrypted)
    adapter = registry.get_integration(obj.service_name, api_key)
    if adapter is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown service: {obj.service_name}",
        )

    start = time.monotonic()
    try:
        health = await adapter.check_health()
        elapsed_ms = (time.monotonic() - start) * 1000
        ok = health.get("status") == "ok"
        obj.last_check = datetime.now(timezone.utc)
        await db.flush()
        await _log_usage(db, obj.service_name, "check_health", health.get("code", 200), elapsed_ms, current_user.id)
        return TestConnectionResponse(
            service=obj.service_name,
            status="ok" if ok else "error",
            message="Connection successful" if ok else f"HTTP {health.get('code')}",
            details=health,
        )
    except Exception as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        obj.last_check = datetime.now(timezone.utc)
        await db.flush()
        await _log_usage(db, obj.service_name, "check_health", 500, elapsed_ms, current_user.id)
        logger.warning("Health check failed for %s: %s", obj.service_name, exc)
        return TestConnectionResponse(
            service=obj.service_name,
            status="error",
            message=str(exc),
        )


# ---------------------------------------------------------------------------
# Unified search
# ---------------------------------------------------------------------------

async def _search_one(
    service_name: str,
    api_key: str,
    query: str,
    query_type: str,
    use_cache: bool,
    db: AsyncSession,
    user_id: int,
) -> UnifiedSearchResult:
    catalogue = registry.get_catalogue_entry(service_name)
    display_name = catalogue.get("display_name", service_name)

    cache_key = f"{service_name}:{query_type}:{hashlib.sha256(query.encode()).hexdigest()}"

    if use_cache:
        cached = await cache_get(cache_key)
        if cached is not None:
            return UnifiedSearchResult(
                service=service_name,
                display_name=display_name,
                results=cached,
                cached=True,
            )

    adapter = registry.get_integration(service_name, api_key)
    if adapter is None:
        return UnifiedSearchResult(
            service=service_name,
            display_name=display_name,
            results=[],
            error="Unknown service",
        )

    start = time.monotonic()
    try:
        results = await adapter.search(query, query_type)
        elapsed_ms = (time.monotonic() - start) * 1000
        await _log_usage(db, service_name, f"search/{query_type}", 200, elapsed_ms, user_id)
        ttl = getattr(adapter, "cache_ttl", 300)
        if use_cache:
            await cache_set(cache_key, results, ttl)
        return UnifiedSearchResult(
            service=service_name,
            display_name=display_name,
            results=results,
            duration_ms=elapsed_ms,
        )
    except Exception as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        await _log_usage(db, service_name, f"search/{query_type}", 500, elapsed_ms, user_id)
        logger.warning("Search failed for %s: %s", service_name, exc)
        return UnifiedSearchResult(
            service=service_name,
            display_name=display_name,
            results=[],
            error=str(exc),
            duration_ms=elapsed_ms,
        )


@router.post("/search", response_model=UnifiedSearchResponse)
async def unified_search(
    request: UnifiedSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UnifiedSearchResponse:
    """Run a query across multiple OSINT services in parallel."""
    stmt = select(Integration).where(
        Integration.user_id == current_user.id, Integration.is_active.is_(True)
    )
    if request.services:
        stmt = stmt.where(Integration.service_name.in_(request.services))
    result = await db.execute(stmt)
    integrations = result.scalars().all()

    if not integrations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active integrations found for the requested services",
        )

    crypto = _crypto()

    async def _run(integ: Integration) -> UnifiedSearchResult:
        if not integ.api_key_encrypted:
            return UnifiedSearchResult(
                service=integ.service_name,
                display_name=registry.get_catalogue_entry(integ.service_name).get("display_name", integ.service_name),
                results=[],
                error="No API key configured",
            )
        api_key = crypto.decrypt(integ.api_key_encrypted)
        return await _search_one(
            integ.service_name,
            api_key,
            request.query,
            request.query_type,
            request.use_cache,
            db,
            current_user.id,
        )

    search_results = await asyncio.gather(*[_run(i) for i in integrations])
    successful = sum(1 for r in search_results if r.error is None)

    return UnifiedSearchResponse(
        query=request.query,
        query_type=request.query_type,
        results=list(search_results),
        total_services=len(search_results),
        successful_services=successful,
    )


# ---------------------------------------------------------------------------
# Usage statistics
# ---------------------------------------------------------------------------

@router.get("/usage", response_model=list[UsageStatsEntry])
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[UsageStatsEntry]:
    """Return API usage statistics per service for the current user."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    entries: dict[str, dict[str, int]] = {}

    for period_name, since in [
        ("today", today_start),
        ("this_week", week_start),
        ("this_month", month_start),
    ]:
        rows = await db.execute(
            select(APIUsageLog.service_name, func.count().label("cnt"))
            .where(APIUsageLog.user_id == current_user.id, APIUsageLog.created_at >= since)
            .group_by(APIUsageLog.service_name)
        )
        for row in rows.all():
            svc = row[0]
            cnt = row[1]
            if svc not in entries:
                entries[svc] = {"today": 0, "this_week": 0, "this_month": 0, "total": 0}
            entries[svc][period_name] = cnt

    rows = await db.execute(
        select(APIUsageLog.service_name, func.count().label("cnt"))
        .where(APIUsageLog.user_id == current_user.id)
        .group_by(APIUsageLog.service_name)
    )
    for row in rows.all():
        svc = row[0]
        if svc not in entries:
            entries[svc] = {"today": 0, "this_week": 0, "this_month": 0, "total": 0}
        entries[svc]["total"] = row[1]

    return [
        UsageStatsEntry(service=svc, **counts)
        for svc, counts in entries.items()
    ]


@router.get("/usage/{service}", response_model=UsageStatsEntry)
async def get_service_usage(
    service: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UsageStatsEntry:
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    async def _count(since: datetime) -> int:
        row = await db.execute(
            select(func.count()).where(
                APIUsageLog.user_id == current_user.id,
                APIUsageLog.service_name == service,
                APIUsageLog.created_at >= since,
            )
        )
        return row.scalar() or 0

    today = await _count(today_start)
    this_week = await _count(week_start)
    this_month = await _count(month_start)
    total_row = await db.execute(
        select(func.count()).where(
            APIUsageLog.user_id == current_user.id,
            APIUsageLog.service_name == service,
        )
    )
    total = total_row.scalar() or 0

    return UsageStatsEntry(
        service=service, today=today, this_week=this_week, this_month=this_month, total=total
    )
