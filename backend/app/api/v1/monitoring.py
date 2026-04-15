from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.monitoring_job import MonitoringJob
from app.models.user import User

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


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


@router.get("/", response_model=list[MonitoringJobResponse])
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MonitoringJobResponse]:
    result = await db.execute(
        select(MonitoringJob).where(MonitoringJob.user_id == current_user.id)
    )
    jobs = result.scalars().all()
    return [MonitoringJobResponse.model_validate(j) for j in jobs]


@router.post("/", response_model=MonitoringJobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: MonitoringJobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MonitoringJobResponse:
    job = MonitoringJob(
        name=request.name,
        type=request.type,
        schedule=request.schedule,
        user_id=current_user.id,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return MonitoringJobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(MonitoringJob).where(
            MonitoringJob.id == job_id, MonitoringJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    await db.delete(job)
