"""add_chat_template_to_model_info

Revision ID: g2b3c4d5e6f7
Revises: e1cf9740a622
Create Date: 2025-09-25 13:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g2b3c4d5e6f7'
down_revision: Union[str, None] = 'e1cf9740a622'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add chat_template column to model_info table
    op.add_column('model_info', sa.Column('chat_template', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove chat_template column from model_info table
    op.drop_column('model_info', 'chat_template')