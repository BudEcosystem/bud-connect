"""add_engine_tool_parser_rules

Revision ID: 1249fdebad1e
Revises: h3c4d5e6f7g8
Create Date: 2025-09-28 16:10:09.456162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1249fdebad1e'
down_revision: Union[str, None] = 'h3c4d5e6f7g8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type with lowercase values
    parser_match_type = sa.Enum(
        'exact', 'prefix', 'regex', name='engine_tool_parser_match_type'
    )

    op.create_table(
        'engine_tool_parser_rule',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('engine_version_id', sa.UUID(), nullable=False),
        sa.Column('parser_type', sa.String(), nullable=False),
        sa.Column('match_type', parser_match_type, nullable=False),
        sa.Column('pattern', sa.String(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['engine_version_id'], ['engine_version.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        'ix_engine_tool_parser_rule_engine_version_id',
        'engine_tool_parser_rule',
        ['engine_version_id'],
    )
    op.create_index(
        'ix_engine_tool_parser_rule_priority',
        'engine_tool_parser_rule',
        ['priority'],
    )
    op.create_index(
        'ix_engine_tool_parser_rule_enabled',
        'engine_tool_parser_rule',
        ['enabled'],
    )


def downgrade() -> None:
    op.drop_index('ix_engine_tool_parser_rule_enabled', table_name='engine_tool_parser_rule')
    op.drop_index('ix_engine_tool_parser_rule_priority', table_name='engine_tool_parser_rule')
    op.drop_index('ix_engine_tool_parser_rule_engine_version_id', table_name='engine_tool_parser_rule')
    op.drop_table('engine_tool_parser_rule')
    # Drop enum type - SQLAlchemy will handle this with the table drop
    sa.Enum(name='engine_tool_parser_match_type').drop(op.get_bind(), checkfirst=True)
