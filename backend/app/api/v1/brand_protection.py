"""Brand Protection API endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.brand import BrandAlert, BrandWatch
from app.models.user import User

router = APIRouter(prefix="/brand", tags=["brand-protection"])


class BrandWatchCreate(BaseModel):
    name: str
    original_url: str
    keywords: list[str] | None = None
    description: str | None = None
    similarity_threshold: float = 70.0
    scan_schedule: str | None = None


class BrandWatchUpdate(BaseModel):
    name: str | None = None
    original_url: str | None = None
    keywords: list[str] | None = None
    description: str | None = None
    similarity_threshold: float | None = None
    scan_schedule: str | None = None
    is_active: bool | None = None


class BrandWatchResponse(BaseModel):
    id: int
    name: str
    original_url: str
    keywords: list | None
    description: str | None
    similarity_threshold: float
    scan_schedule: str | None
    last_scan: str | None
    is_active: bool
    alert_count: int = 0
    new_alert_count: int = 0
    created_at: str

    model_config = {"from_attributes": True}


class BrandAlertResponse(BaseModel):
    id: int
    brand_watch_id: int
    found_domain: str
    similarity_score: float
    detection_sources: list | None
    screenshot_url: str | None
    status: str
    notes: str | None
    created_at: str

    model_config = {"from_attributes": True}


class BrandAlertStatusUpdate(BaseModel):
    status: str  # reviewed / dismissed
    notes: str | None = None


def _watch_response(watch: BrandWatch, alerts: list[BrandAlert] | None = None) -> BrandWatchResponse:
    all_alerts = alerts or watch.alerts if hasattr(watch, "alerts") and watch.alerts is not None else []
    return BrandWatchResponse(
        id=watch.id,
        name=watch.name,
        original_url=watch.original_url,
        keywords=watch.keywords,
        description=watch.description,
        similarity_threshold=watch.similarity_threshold,
        scan_schedule=watch.scan_schedule,
        last_scan=watch.last_scan.isoformat() if watch.last_scan else None,
        is_active=watch.is_active,
        alert_count=len(all_alerts),
        new_alert_count=sum(1 for a in all_alerts if a.status == "new"),
        created_at=watch.created_at.isoformat(),
    )


def _alert_response(alert: BrandAlert) -> BrandAlertResponse:
    return BrandAlertResponse(
        id=alert.id,
        brand_watch_id=alert.brand_watch_id,
        found_domain=alert.found_domain,
        similarity_score=alert.similarity_score,
        detection_sources=alert.detection_sources,
        screenshot_url=alert.screenshot_url,
        status=alert.status,
        notes=alert.notes,
        created_at=alert.created_at.isoformat(),
    )


@router.post("/watches", response_model=BrandWatchResponse, status_code=status.HTTP_201_CREATED)
async def create_brand_watch(
    body: BrandWatchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BrandWatchResponse:
    watch = BrandWatch(
        user_id=current_user.id,
        **body.model_dump(),
    )
    db.add(watch)
    await db.flush()
    await db.refresh(watch)
    return _watch_response(watch, [])


@router.get("/watches", response_model=list[BrandWatchResponse])
async def list_brand_watches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BrandWatchResponse]:
    result = await db.execute(
        select(BrandWatch).where(BrandWatch.user_id == current_user.id)
    )
    watches = result.scalars().all()
    out = []
    for watch in watches:
        alerts_result = await db.execute(
            select(BrandAlert).where(BrandAlert.brand_watch_id == watch.id)
        )
        alerts = list(alerts_result.scalars().all())
        out.append(_watch_response(watch, alerts))
    return out


@router.get("/watches/{watch_id}", response_model=BrandWatchResponse)
async def get_brand_watch(
    watch_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BrandWatchResponse:
    result = await db.execute(
        select(BrandWatch).where(
            BrandWatch.id == watch_id, BrandWatch.user_id == current_user.id
        )
    )
    watch = result.scalar_one_or_none()
    if not watch:
        raise HTTPException(status_code=404, detail="Brand watch not found")
    alerts_result = await db.execute(
        select(BrandAlert).where(BrandAlert.brand_watch_id == watch_id)
    )
    alerts = list(alerts_result.scalars().all())
    return _watch_response(watch, alerts)


@router.put("/watches/{watch_id}", response_model=BrandWatchResponse)
async def update_brand_watch(
    watch_id: int,
    body: BrandWatchUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BrandWatchResponse:
    result = await db.execute(
        select(BrandWatch).where(
            BrandWatch.id == watch_id, BrandWatch.user_id == current_user.id
        )
    )
    watch = result.scalar_one_or_none()
    if not watch:
        raise HTTPException(status_code=404, detail="Brand watch not found")
    for key, val in body.model_dump(exclude_none=True).items():
        setattr(watch, key, val)
    await db.flush()
    await db.refresh(watch)
    alerts_result = await db.execute(
        select(BrandAlert).where(BrandAlert.brand_watch_id == watch_id)
    )
    alerts = list(alerts_result.scalars().all())
    return _watch_response(watch, alerts)


@router.delete("/watches/{watch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand_watch(
    watch_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(BrandWatch).where(
            BrandWatch.id == watch_id, BrandWatch.user_id == current_user.id
        )
    )
    watch = result.scalar_one_or_none()
    if not watch:
        raise HTTPException(status_code=404, detail="Brand watch not found")
    await db.delete(watch)


@router.post("/watches/{watch_id}/scan", status_code=status.HTTP_202_ACCEPTED)
async def trigger_brand_scan(
    watch_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(BrandWatch).where(
            BrandWatch.id == watch_id, BrandWatch.user_id == current_user.id
        )
    )
    watch = result.scalar_one_or_none()
    if not watch:
        raise HTTPException(status_code=404, detail="Brand watch not found")
    from app.tasks.brand_tasks import deep_brand_scan

    task = deep_brand_scan.delay(watch_id)
    return {"task_id": task.id, "status": "queued"}


@router.get("/watches/{watch_id}/alerts", response_model=list[BrandAlertResponse])
async def list_brand_alerts(
    watch_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BrandAlertResponse]:
    result = await db.execute(
        select(BrandWatch).where(
            BrandWatch.id == watch_id, BrandWatch.user_id == current_user.id
        )
    )
    watch = result.scalar_one_or_none()
    if not watch:
        raise HTTPException(status_code=404, detail="Brand watch not found")
    alerts_result = await db.execute(
        select(BrandAlert)
        .where(BrandAlert.brand_watch_id == watch_id)
        .order_by(BrandAlert.created_at.desc())
    )
    return [_alert_response(a) for a in alerts_result.scalars().all()]


@router.put("/alerts/{alert_id}/status", response_model=BrandAlertResponse)
async def update_alert_status(
    alert_id: int,
    body: BrandAlertStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BrandAlertResponse:
    if body.status not in ("reviewed", "dismissed", "new"):
        raise HTTPException(status_code=400, detail="Invalid status")
    # Verify ownership via brand_watch
    result = await db.execute(
        select(BrandAlert)
        .join(BrandWatch, BrandAlert.brand_watch_id == BrandWatch.id)
        .where(BrandAlert.id == alert_id, BrandWatch.user_id == current_user.id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = body.status
    if body.notes is not None:
        alert.notes = body.notes
    await db.flush()
    await db.refresh(alert)
    return _alert_response(alert)


@router.get("/report/{watch_id}")
async def get_brand_report(
    watch_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(BrandWatch).where(
            BrandWatch.id == watch_id, BrandWatch.user_id == current_user.id
        )
    )
    watch = result.scalar_one_or_none()
    if not watch:
        raise HTTPException(status_code=404, detail="Brand watch not found")
    alerts_result = await db.execute(
        select(BrandAlert).where(BrandAlert.brand_watch_id == watch_id)
    )
    alerts = list(alerts_result.scalars().all())
    return {
        "brand_watch": _watch_response(watch, alerts).model_dump(),
        "alerts": [_alert_response(a).model_dump() for a in alerts],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_alerts": len(alerts),
            "new": sum(1 for a in alerts if a.status == "new"),
            "reviewed": sum(1 for a in alerts if a.status == "reviewed"),
            "dismissed": sum(1 for a in alerts if a.status == "dismissed"),
            "avg_similarity": round(
                sum(a.similarity_score for a in alerts) / len(alerts), 1
            ) if alerts else 0,
        },
    }
