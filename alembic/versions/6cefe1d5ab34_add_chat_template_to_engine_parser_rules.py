"""add_chat_template_to_engine_parser_rules

Revision ID: 6cefe1d5ab34
Revises: 1249fdebad1e
Create Date: 2025-10-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cefe1d5ab34'
down_revision: Union[str, None] = '1249fdebad1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('engine_tool_parser_rule', sa.Column('chat_template', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('engine_tool_parser_rule', 'chat_template')
