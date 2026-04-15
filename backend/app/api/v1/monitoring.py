"""Monitoring API — watchlist, saved searches, folder monitoring, jobs."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.monitoring_job import MonitoringJob
from app.models.user import User
from app.models.watchlist import WatchlistItem, WatchlistResult
from app.services import watchlist_service as wl_svc
from app.services import search_template_service as st_svc

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# ──────────────────────────────────────────────
# Monitoring jobs (kept for compat)
# ──────────────────────────────────────────────


class MonitoringJobCreate(BaseModel):
    name: str
    type: str
    schedule: str | None = None


class MonitoringJobResponse(BaseModel):
    id: int
    name: str
    type: str
    schedule: str | None
    status: str

    model_config = {"from_attributes": True}


@router.get("/jobs", response_model=list[MonitoringJobResponse])
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MonitoringJobResponse]:
    result = await db.execute(
        select(MonitoringJob).where(MonitoringJob.user_id == current_user.id)
    )
    jobs = result.scalars().all()
    return [MonitoringJobResponse.model_validate(j) for j in jobs]


@router.get("/history")
async def monitoring_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    """Return recent watchlist check results as activity history."""
    result = await db.execute(
        select(WatchlistResult)
        .join(WatchlistItem, WatchlistResult.watchlist_item_id == WatchlistItem.id)
        .where(WatchlistItem.user_id == current_user.id)
        .order_by(WatchlistResult.checked_at.desc())
        .limit(limit)
    )
    records = result.scalars().all()
    return {
        "history": [
            {
                "id": r.id,
                "watchlist_item_id": r.watchlist_item_id,
                "has_findings": r.has_findings,
                "checked_at": r.checked_at.isoformat(),
            }
            for r in records
        ]
    }


# ──────────────────────────────────────────────
# Watchlist
# ──────────────────────────────────────────────


class WatchlistItemCreate(BaseModel):
    type: str
    value: str
    services: list[str] | None = None
    schedule: str | None = None


class WatchlistItemUpdate(BaseModel):
    type: str | None = None
    value: str | None = None
    services: list[str] | None = None
    schedule: str | None = None
    is_active: bool | None = None


class WatchlistResultResponse(BaseModel):
    id: int
    has_findings: bool
    result_data: dict | None
    checked_at: str


class WatchlistItemResponse(BaseModel):
    id: int
    type: str
    value: str
    services: list | None
    schedule: str | None
    is_active: bool
    last_checked: str | None
    created_at: str
    history: list[WatchlistResultResponse] | None = None


def _wl_response(item: WatchlistItem, history: list | None = None) -> WatchlistItemResponse:
    return WatchlistItemResponse(
        id=item.id,
        type=item.type,
        value=item.value,
        services=item.services,
        schedule=item.schedule,
        is_active=item.is_active,
        last_checked=item.last_checked.isoformat() if item.last_checked else None,
        created_at=item.created_at.isoformat(),
        history=[
            WatchlistResultResponse(
                id=r.id,
                has_findings=r.has_findings,
                result_data=r.result_data,
                checked_at=r.checked_at.isoformat(),
            )
            for r in history
        ] if history is not None else None,
    )


@router.post("/watchlist", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist_item(
    body: WatchlistItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WatchlistItemResponse:
    item = await wl_svc.create_watchlist_item(
        db,
        user_id=current_user.id,
        type_=body.type,
        value=body.value,
        services=body.services,
        schedule=body.schedule,
    )
    return _wl_response(item)


@router.get("/watchlist", response_model=list[WatchlistItemResponse])
async def list_watchlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[WatchlistItemResponse]:
    items = await wl_svc.get_user_watchlist(db, current_user.id)
    return [_wl_response(i) for i in items]


@router.get("/watchlist/{item_id}", response_model=WatchlistItemResponse)
async def get_watchlist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WatchlistItemResponse:
    item = await wl_svc.get_watchlist_item(db, item_id, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    history = await wl_svc.get_watchlist_history(db, item_id)
    return _wl_response(item, history)


@router.put("/watchlist/{item_id}", response_model=WatchlistItemResponse)
async def update_watchlist_item(
    item_id: int,
    body: WatchlistItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WatchlistItemResponse:
    item = await wl_svc.get_watchlist_item(db, item_id, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    item = await wl_svc.update_watchlist_item(db, item, **body.model_dump(exclude_none=True))
    return _wl_response(item)


@router.delete("/watchlist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    item = await wl_svc.get_watchlist_item(db, item_id, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    await wl_svc.delete_watchlist_item(db, item)


@router.post("/watchlist/{item_id}/check", status_code=status.HTTP_202_ACCEPTED)
async def force_check_watchlist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    item = await wl_svc.get_watchlist_item(db, item_id, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    from app.tasks.monitoring_tasks import check_watchlist_item

    task = check_watchlist_item.delay(item_id)
    return {"task_id": task.id, "status": "queued"}


# ──────────────────────────────────────────────
# Saved Search Templates
# ──────────────────────────────────────────────


class SearchTemplateCreate(BaseModel):
    name: str
    query: str
    filters: dict | None = None
    schedule: str | None = None


class SearchTemplateUpdate(BaseModel):
    name: str | None = None
    query: str | None = None
    filters: dict | None = None
    schedule: str | None = None
    is_active: bool | None = None


class SearchTemplateResponse(BaseModel):
    id: int
    name: str
    query: str
    filters: dict | None
    schedule: str | None
    is_active: bool
    created_at: str


def _tmpl_response(t) -> SearchTemplateResponse:
    return SearchTemplateResponse(
        id=t.id,
        name=t.name,
        query=t.query,
        filters=t.filters,
        schedule=t.schedule,
        is_active=t.is_active,
        created_at=t.created_at.isoformat(),
    )


@router.post("/searches", response_model=SearchTemplateResponse, status_code=status.HTTP_201_CREATED)
async def save_search_template(
    body: SearchTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SearchTemplateResponse:
    tmpl = await st_svc.create_template(
        db,
        user_id=current_user.id,
        name=body.name,
        query=body.query,
        filters=body.filters,
        schedule=body.schedule,
    )
    return _tmpl_response(tmpl)


@router.get("/searches", response_model=list[SearchTemplateResponse])
async def list_search_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SearchTemplateResponse]:
    templates = await st_svc.get_user_templates(db, current_user.id)
    return [_tmpl_response(t) for t in templates]


@router.put("/searches/{template_id}", response_model=SearchTemplateResponse)
async def update_search_template(
    template_id: int,
    body: SearchTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SearchTemplateResponse:
    tmpl = await st_svc.get_template(db, template_id, current_user.id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Search template not found")
    tmpl = await st_svc.update_template(db, tmpl, **body.model_dump(exclude_none=True))
    return _tmpl_response(tmpl)


@router.delete("/searches/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    tmpl = await st_svc.get_template(db, template_id, current_user.id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Search template not found")
    await st_svc.delete_template(db, tmpl)


@router.post("/searches/{template_id}/run")
async def run_search_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    tmpl = await st_svc.get_template(db, template_id, current_user.id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Search template not found")
    result = await st_svc.run_template(db, tmpl)
    return result


# ──────────────────────────────────────────────
# Folder monitoring
# ──────────────────────────────────────────────


@router.get("/folder/status")
async def folder_status(
    current_user: User = Depends(get_current_user),
) -> dict:
    from app.services.monitoring_service import get_folder_status

    return get_folder_status()


@router.post("/folder/scan", status_code=status.HTTP_202_ACCEPTED)
async def trigger_folder_scan(
    current_user: User = Depends(get_current_user),
) -> dict:
    from app.tasks.monitoring_tasks import rescan_monitored_folder

    task = rescan_monitored_folder.delay()
    return {"task_id": task.id, "status": "queued"}
