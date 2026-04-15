from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    files: Mapped[list["File"]] = relationship("File", back_populates="user", lazy="select")  # type: ignore[name-defined]
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user", lazy="select")  # type: ignore[name-defined]
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user", lazy="select")  # type: ignore[name-defined]
