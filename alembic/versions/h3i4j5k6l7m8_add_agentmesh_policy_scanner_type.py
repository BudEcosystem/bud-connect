"""add agentmesh_policy scanner type

Revision ID: h3i4j5k6l7m8
Revises: h4i5j6k7l8m9
Create Date: 2026-06-09 00:00:00.000000

Adds the ``agentmesh_policy`` value to ``scanner_type_enum`` so agent-governance
policy rules (bud-sentinel's agentmesh engine) seed with a real scanner_type
instead of NULL. These rules carry a governance policy body rather than a
scanner model, but the catalog advertises them under scanner_type like any
other rule.
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'h3i4j5k6l7m8'
down_revision: Union[str, None] = 'h4i5j6k7l8m9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the agentmesh_policy value to scanner_type_enum.
    # ALTER TYPE ... ADD VALUE cannot run inside a transaction block on older
    # PostgreSQL versions (and the value can't be used in the same transaction
    # even on 12+), so run it in an autocommit block outside Alembic's transaction.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE scanner_type_enum ADD VALUE IF NOT EXISTS 'agentmesh_policy'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # You would need to recreate the type and update all columns using it
    # This is a complex operation and typically not done in production
    pass
