"""add_supported_endpoints_to_engine_compatibility

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2025-12-23 10:00:00.000000

This migration adds supported_endpoints column to engine_compatibility table
to allow engines to specify compatibility by model endpoint types (e.g., EMBEDDING)
instead of specific architectures.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h8i9j0'
down_revision: Union[str, None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'engine_compatibility',
        sa.Column('supported_endpoints', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('engine_compatibility', 'supported_endpoints')
