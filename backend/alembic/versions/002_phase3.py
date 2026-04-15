"""Phase 3 — watchlist, brand protection, notification preferences

Revision ID: 002_phase3
Revises: 001_initial
Create Date: 2026-04-15 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "002_phase3"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # watchlist_items
    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("value", sa.String(500), nullable=False),
        sa.Column("services", sa.JSON(), nullable=True),
        sa.Column("schedule", sa.String(100), nullable=True),
        sa.Column("last_checked", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_result_hash", sa.String(64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # watchlist_results
    op.create_table(
        "watchlist_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_item_id", sa.Integer(), nullable=False),
        sa.Column("result_data", sa.JSON(), nullable=True),
        sa.Column("result_hash", sa.String(64), nullable=True),
        sa.Column("has_findings", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["watchlist_item_id"], ["watchlist_items.id"], ondelete="CASCADE"),
    )

    # brand_watches
    op.create_table(
        "brand_watches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("original_url", sa.String(500), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("similarity_threshold", sa.Float(), nullable=False, server_default="70.0"),
        sa.Column("scan_schedule", sa.String(100), nullable=True),
        sa.Column("last_scan", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # brand_alerts
    op.create_table(
        "brand_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("brand_watch_id", sa.Integer(), nullable=False),
        sa.Column("found_domain", sa.String(500), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("detection_sources", sa.JSON(), nullable=True),
        sa.Column("screenshot_url", sa.String(500), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="new"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["brand_watch_id"], ["brand_watches.id"], ondelete="CASCADE"),
    )

    # notification_preferences
    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("email_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("email_address", sa.String(255), nullable=True),
        sa.Column("email_types", sa.JSON(), nullable=True),
        sa.Column("telegram_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("telegram_bot_token", sa.String(255), nullable=True),
        sa.Column("telegram_chat_id", sa.String(100), nullable=True),
        sa.Column("telegram_types", sa.JSON(), nullable=True),
        sa.Column("digest_mode", sa.String(50), nullable=False, server_default="immediate"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("notification_preferences")
    op.drop_table("brand_alerts")
    op.drop_table("brand_watches")
    op.drop_table("watchlist_results")
    op.drop_table("watchlist_items")
