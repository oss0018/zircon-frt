from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class NotificationPreference(Base, TimestampMixin):
    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    # Email
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_types: Mapped[list | None] = mapped_column(JSON, nullable=True)  # which notification types
    # Telegram
    telegram_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    telegram_bot_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telegram_types: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # Digest
    digest_mode: Mapped[str] = mapped_column(String(50), default="immediate", nullable=False)

    user: Mapped["User"] = relationship("User")  # type: ignore[name-defined]
