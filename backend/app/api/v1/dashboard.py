from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.file import File
from app.models.monitoring_job import MonitoringJob
from app.models.notification import Notification
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    total_files: int
    indexed_files: int
    alerts_today: int
    active_monitors: int


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    total_files = (
        await db.execute(select(func.count()).select_from(File).where(File.user_id == current_user.id))
    ).scalar_one()

    indexed_files = (
        await db.execute(
            select(func.count()).select_from(File).where(
                File.user_id == current_user.id, File.indexed == True  # noqa: E712
            )
        )
    ).scalar_one()

    from datetime import date, datetime, timezone
    today_start = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)
    alerts_today = (
        await db.execute(
            select(func.count()).select_from(Notification).where(
                Notification.user_id == current_user.id,
                Notification.created_at >= today_start,
            )
        )
    ).scalar_one()

    active_monitors = (
        await db.execute(
            select(func.count()).select_from(MonitoringJob).where(
                MonitoringJob.user_id == current_user.id,
                MonitoringJob.status == "active",
            )
        )
    ).scalar_one()

    return DashboardStats(
        total_files=total_files,
        indexed_files=indexed_files,
        alerts_today=alerts_today,
        active_monitors=active_monitors,
    )
