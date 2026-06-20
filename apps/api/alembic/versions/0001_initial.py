"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-20
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("message_count", sa.Integer(), nullable=False, default=0),
        sa.Column("tool_call_count", sa.Integer(), nullable=False, default=0),
        sa.Column("total_input_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("total_output_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("has_compaction", sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content_summary", sa.String(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("output_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("cache_creation_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("cache_read_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_session_id", "messages", ["session_id"])

    op.create_table(
        "tool_usages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("tool_name", sa.String(), nullable=False),
        sa.Column("execution_count", sa.Integer(), nullable=False, default=1),
        sa.Column("is_error_count", sa.Integer(), nullable=False, default=0),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tool_usages_session_id", "tool_usages", ["session_id"])

    op.create_table(
        "daily_aggregates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("output_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("cache_creation_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("cache_read_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("session_count", sa.Integer(), nullable=False, default=0),
        sa.Column("message_count", sa.Integer(), nullable=False, default=0),
        sa.Column("estimated_cost", sa.Float(), nullable=False, default=0.0),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_daily_aggregates_date", "daily_aggregates", ["date"])
    op.create_index("ix_daily_aggregates_project_date", "daily_aggregates", ["project_id", "date"])

    op.create_table(
        "tracked_files",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("checksum", sa.String(), nullable=True),
        sa.Column("last_modified", sa.Float(), nullable=True),
        sa.Column("last_processed", sa.DateTime(), nullable=True),
        sa.Column("session_db_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["session_db_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("path"),
    )


def downgrade() -> None:
    op.drop_table("tracked_files")
    op.drop_index("ix_daily_aggregates_project_date", "daily_aggregates")
    op.drop_index("ix_daily_aggregates_date", "daily_aggregates")
    op.drop_table("daily_aggregates")
    op.drop_index("ix_tool_usages_session_id", "tool_usages")
    op.drop_table("tool_usages")
    op.drop_index("ix_messages_session_id", "messages")
    op.drop_table("messages")
    op.drop_table("sessions")
    op.drop_table("projects")
