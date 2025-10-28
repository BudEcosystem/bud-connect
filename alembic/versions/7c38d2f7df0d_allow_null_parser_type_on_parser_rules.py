"""allow_null_parser_type_on_parser_rules

Revision ID: 7c38d2f7df0d
Revises: 6cefe1d5ab34
Create Date: 2025-10-05 13:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c38d2f7df0d'
down_revision: Union[str, None] = '6cefe1d5ab34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('engine_tool_parser_rule', 'parser_type', existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    op.alter_column('engine_tool_parser_rule', 'parser_type', existing_type=sa.String(), nullable=False)
