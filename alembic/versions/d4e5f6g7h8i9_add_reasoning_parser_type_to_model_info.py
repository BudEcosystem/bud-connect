"""add_reasoning_parser_type_to_model_info

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2025-12-02 14:00:00.000000

This migration adds reasoning_parser_type column to model_info table
to support per-model reasoning parser configuration, similar to
tool_calling_parser_type.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('model_info', sa.Column('reasoning_parser_type', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('model_info', 'reasoning_parser_type')
