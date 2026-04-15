from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class BrandWatch(Base, TimestampMixin):
    __tablename__ = "brand_watches"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_url: Mapped[str] = mapped_column(String(500), nullable=False)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    similarity_threshold: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)
    scan_schedule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_scan: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User")  # type: ignore[name-defined]
    alerts: Mapped[list["BrandAlert"]] = relationship(
        "BrandAlert", back_populates="brand_watch", cascade="all, delete-orphan"
    )


class BrandAlert(Base):
    __tablename__ = "brand_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_watch_id: Mapped[int] = mapped_column(
        ForeignKey("brand_watches.id", ondelete="CASCADE"), nullable=False
    )
    found_domain: Mapped[str] = mapped_column(String(500), nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    detection_sources: Mapped[list | None] = mapped_column(JSON, nullable=True)
    screenshot_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False)  # new/reviewed/dismissed
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=__import__("sqlalchemy").func.now(),
        nullable=False,
    )

    brand_watch: Mapped["BrandWatch"] = relationship("BrandWatch", back_populates="alerts")
