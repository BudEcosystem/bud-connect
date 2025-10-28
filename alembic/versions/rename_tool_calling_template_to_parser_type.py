"""rename_tool_calling_template_to_tool_calling_parser_type

Revision ID: f1a2b3c4d5e6
Revises: e1cf9740a622
Create Date: 2025-09-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'e1cf9740a622'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename column in model_architecture_class table
    op.alter_column('model_architecture_class', 'tool_calling_template',
                    new_column_name='tool_calling_parser_type',
                    existing_type=sa.String(),
                    existing_nullable=True)

    # Rename column in model_capability table
    op.alter_column('model_capability', 'tool_calling_template',
                    new_column_name='tool_calling_parser_type',
                    existing_type=sa.String(),
                    existing_nullable=True)

    # Rename column in engine_compatibility table
    op.alter_column('engine_compatibility', 'supported_tool_calling_templates',
                    new_column_name='supported_tool_calling_parser_types',
                    existing_type=sa.dialects.postgresql.JSONB(astext_type=sa.Text()),
                    existing_nullable=True)


def downgrade() -> None:
    # Rename column back in engine_compatibility table
    op.alter_column('engine_compatibility', 'supported_tool_calling_parser_types',
                    new_column_name='supported_tool_calling_templates',
                    existing_type=sa.dialects.postgresql.JSONB(astext_type=sa.Text()),
                    existing_nullable=True)

    # Rename column back in model_capability table
    op.alter_column('model_capability', 'tool_calling_parser_type',
                    new_column_name='tool_calling_template',
                    existing_type=sa.String(),
                    existing_nullable=True)

    # Rename column back in model_architecture_class table
    op.alter_column('model_architecture_class', 'tool_calling_parser_type',
                    new_column_name='tool_calling_template',
                    existing_type=sa.String(),
                    existing_nullable=True)