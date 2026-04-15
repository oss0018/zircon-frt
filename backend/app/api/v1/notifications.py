"""Notification API endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services import notification_service as svc

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str | None
    is_read: bool
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, obj) -> "NotificationResponse":
        return cls(
            id=obj.id,
            type=obj.type,
            title=obj.title,
            message=obj.message,
            is_read=obj.is_read,
            created_at=obj.created_at.isoformat(),
        )


class UnreadCountResponse(BaseModel):
    count: int


class NotificationPrefsResponse(BaseModel):
    email_enabled: bool
    email_address: str | None
    email_types: list[str] | None
    telegram_enabled: bool
    telegram_chat_id: str | None
    telegram_types: list[str] | None
    digest_mode: str

    model_config = {"from_attributes": True}


class NotificationPrefsUpdate(BaseModel):
    email_enabled: bool | None = None
    email_address: str | None = None
    email_types: list[str] | None = None
    telegram_enabled: bool | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_types: list[str] | None = None
    digest_mode: str | None = None


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(
    unread_only: bool = Query(False),
    type_filter: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[NotificationResponse]:
    items = await svc.list_notifications(
        db,
        user_id=current_user.id,
        unread_only=unread_only,
        type_filter=type_filter,
        limit=limit,
        offset=offset,
    )
    return [NotificationResponse.from_orm(n) for n in items]


@router.get("/unread", response_model=UnreadCountResponse)
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UnreadCountResponse:
    count = await svc.count_unread(db, current_user.id)
    return UnreadCountResponse(count=count)


@router.put("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    ok = await svc.mark_read(db, notification_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")


@router.put("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await svc.mark_all_read(db, current_user.id)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    ok = await svc.delete_notification(db, notification_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")


@router.get("/settings", response_model=NotificationPrefsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationPrefsResponse:
    prefs = await svc.get_or_create_prefs(db, current_user.id)
    return NotificationPrefsResponse.model_validate(prefs)


@router.put("/settings", response_model=NotificationPrefsResponse)
async def update_settings(
    body: NotificationPrefsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationPrefsResponse:
    updates = body.model_dump(exclude_none=True)
    prefs = await svc.update_prefs(db, current_user.id, **updates)
    return NotificationPrefsResponse.model_validate(prefs)
