"""add icon column to guardrail_probes and guardrail_rules tables

Revision ID: g2h3i4j5k6l7
Revises: f1g2h3i4j5k6
Create Date: 2026-02-13 10:00:00.000000

This migration:
- Adds icon column to guardrail_probes table
- Adds icon column to guardrail_rules table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g2h3i4j5k6l7'
down_revision: Union[str, None] = 'f1g2h3i4j5k6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add icon column to guardrail_probes table
    op.add_column(
        'guardrail_probes',
        sa.Column('icon', sa.String(length=512), nullable=True)
    )

    # Add icon column to guardrail_rules table
    op.add_column(
        'guardrail_rules',
        sa.Column('icon', sa.String(length=512), nullable=True)
    )


def downgrade() -> None:
    # Drop icon column from guardrail_rules table
    op.drop_column('guardrail_rules', 'icon')

    # Drop icon column from guardrail_probes table
    op.drop_column('guardrail_probes', 'icon')
