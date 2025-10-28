"""add_tool_calling_parser_type_to_model_info

Revision ID: h3c4d5e6f7g8
Revises: g2b3c4d5e6f7
Create Date: 2025-09-25 14:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h3c4d5e6f7g8'
down_revision: Union[str, None] = 'g2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('model_info', sa.Column('tool_calling_parser_type', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('model_info', 'tool_calling_parser_type')
