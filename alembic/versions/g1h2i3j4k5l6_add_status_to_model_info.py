"""Add status field to model_info.

Revision ID: g1h2i3j4k5l6
Revises: f1g2h3i4j5k6
Create Date: 2026-02-23 00:00:00.000000

This migration adds a status column to model_info table to support
marking stale models as inactive instead of deleting them.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'g1h2i3j4k5l6'
down_revision: Union[str, None] = 'f1g2h3i4j5k6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add modelstatusenum type and status column to model_info."""
    model_status_enum = postgresql.ENUM('ACTIVE', 'INACTIVE', name='modelstatusenum', create_type=False)
    model_status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'model_info',
        sa.Column('status', model_status_enum, nullable=False, server_default='ACTIVE'),
    )


def downgrade() -> None:
    """Remove status column and modelstatusenum type."""
    op.drop_column('model_info', 'status')
    sa.Enum(name='modelstatusenum').drop(op.get_bind(), checkfirst=True)
