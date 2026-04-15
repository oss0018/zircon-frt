"""Notification service — in-app, email (SMTP), Telegram notifications."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference

logger = logging.getLogger(__name__)

VALID_TYPES = {"info", "warning", "alert", "breach", "phishing", "brand"}


async def create_notification(
    db: AsyncSession,
    user_id: int,
    type_: str,
    title: str,
    message: str | None = None,
) -> Notification:
    notif = Notification(
        user_id=user_id,
        type=type_,
        title=title,
        message=message,
    )
    db.add(notif)
    await db.flush()
    await db.refresh(notif)

    # Attempt external notifications asynchronously (best-effort)
    try:
        prefs = await _get_prefs(db, user_id)
        if prefs:
            if prefs.email_enabled and prefs.email_address:
                if prefs.email_types is None or type_ in prefs.email_types:
                    await _send_email(prefs.email_address, title, message or "")
            if prefs.telegram_enabled and prefs.telegram_chat_id:
                if prefs.telegram_types is None or type_ in prefs.telegram_types:
                    await _send_telegram(prefs.telegram_chat_id, title, message or "")
    except Exception as exc:
        logger.warning("External notification failed: %s", exc)

    return notif


async def _get_prefs(db: AsyncSession, user_id: int) -> NotificationPreference | None:
    result = await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def _send_email(to: str, subject: str, body: str) -> None:
    """Send email via SMTP using aiosmtplib if configured."""
    if not settings.SMTP_HOST:
        return
    try:
        import aiosmtplib  # type: ignore[import-untyped]
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to
        msg["Subject"] = f"[Zircon FRT] {subject}"
        msg.set_content(body)

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=True,
        )
        logger.info("Email sent to %s: %s", to, subject)
    except Exception as exc:
        logger.warning("Email send failed: %s", exc)


async def _send_telegram(chat_id: str, title: str, body: str) -> None:
    """Send Telegram message via Bot API if configured."""
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    try:
        import httpx

        token = settings.TELEGRAM_BOT_TOKEN
        text = f"*[Zircon FRT]* {title}\n{body}"
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
                timeout=10,
            )
        logger.info("Telegram notification sent to %s", chat_id)
    except Exception as exc:
        logger.warning("Telegram send failed: %s", exc)


async def list_notifications(
    db: AsyncSession,
    user_id: int,
    unread_only: bool = False,
    type_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Notification]:
    q = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        q = q.where(Notification.is_read == False)  # noqa: E712
    if type_filter:
        q = q.where(Notification.type == type_filter)
    q = q.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


async def count_unread(db: AsyncSession, user_id: int) -> int:
    from sqlalchemy import func

    result = await db.execute(
        select(func.count()).where(
            Notification.user_id == user_id, Notification.is_read == False  # noqa: E712
        )
    )
    return result.scalar_one()


async def mark_read(db: AsyncSession, notification_id: int, user_id: int) -> bool:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        return False
    notif.is_read = True
    await db.flush()
    return True


async def mark_all_read(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        .values(is_read=True)
        .returning(Notification.id)
    )
    return len(result.fetchall())


async def delete_notification(db: AsyncSession, notification_id: int, user_id: int) -> bool:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        return False
    await db.delete(notif)
    return True


async def get_or_create_prefs(db: AsyncSession, user_id: int) -> NotificationPreference:
    prefs = await _get_prefs(db, user_id)
    if not prefs:
        prefs = NotificationPreference(user_id=user_id)
        db.add(prefs)
        await db.flush()
        await db.refresh(prefs)
    return prefs


async def update_prefs(
    db: AsyncSession, user_id: int, **kwargs
) -> NotificationPreference:
    prefs = await get_or_create_prefs(db, user_id)
    for key, val in kwargs.items():
        if hasattr(prefs, key):
            setattr(prefs, key, val)
    await db.flush()
    await db.refresh(prefs)
    return prefs
