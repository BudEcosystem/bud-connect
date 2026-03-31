"""Add a2a_registry_agent table.

Revision ID: h4i5j6k7l8m9
Revises: g1h2i3j4k5l6
Create Date: 2026-03-31 00:00:00.000000

This migration creates the a2a_registry_agent table for storing
A2A agents fetched from a2aregistry.org.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "h4i5j6k7l8m9"
down_revision: Union[str, None] = "g1h2i3j4k5l6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create a2a_registry_agent table."""
    op.create_table(
        "a2a_registry_agent",
        sa.Column("id", sa.UUID(), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("registry_id", sa.String(), nullable=True),
        sa.Column("base_url", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("version", sa.String(), nullable=True),
        sa.Column("protocol_version", sa.String(), nullable=True),
        sa.Column("provider", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("capabilities", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("security_schemes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("security", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("icon_url", sa.String(), nullable=True),
        sa.Column("default_input_modes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("default_output_modes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("documentation_url", sa.String(), nullable=True),
        sa.Column("conformance", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("is_healthy", sa.Boolean(), nullable=True),
        sa.Column("uptime_percentage", sa.Float(), nullable=True),
        sa.Column("avg_response_time_ms", sa.Integer(), nullable=True),
        sa.Column("last_health_check", sa.DateTime(timezone=True), nullable=True),
        sa.Column("supports_authenticated_extended_card", sa.Boolean(), nullable=True),
        sa.Column("maintainer_notes", sa.Text(), nullable=True),
        sa.Column("homepage", sa.String(), nullable=True),
        sa.Column("repository", sa.String(), nullable=True),
        sa.Column("license", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("base_url"),
    )


def downgrade() -> None:
    """Drop a2a_registry_agent table."""
    op.drop_table("a2a_registry_agent")
