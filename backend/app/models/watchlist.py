from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class WatchlistItem(Base, TimestampMixin):
    __tablename__ = "watchlist_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # email/domain/ip/keyword/brand
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    services: Mapped[list | None] = mapped_column(JSON, nullable=True)  # which OSINT services to check
    schedule: Mapped[str | None] = mapped_column(String(100), nullable=True)  # cron or preset
    last_checked: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_result_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User")  # type: ignore[name-defined]
    results: Mapped[list["WatchlistResult"]] = relationship(
        "WatchlistResult", back_populates="watchlist_item", cascade="all, delete-orphan"
    )


class WatchlistResult(Base):
    __tablename__ = "watchlist_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_item_id: Mapped[int] = mapped_column(
        ForeignKey("watchlist_items.id", ondelete="CASCADE"), nullable=False
    )
    result_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    has_findings: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    watchlist_item: Mapped["WatchlistItem"] = relationship("WatchlistItem", back_populates="results")
