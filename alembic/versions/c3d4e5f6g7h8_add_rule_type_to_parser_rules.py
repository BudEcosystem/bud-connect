"""add_rule_type_to_parser_rules

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2025-12-02 12:00:00.000000

This migration adds rule_type column to parser rules to support both
tool calling and reasoning parser rules in a unified table. It also
renames the table from engine_tool_parser_rule to engine_parser_rule.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create the parser_rule_type enum
    parser_rule_type_enum = sa.Enum('tool', 'reasoning', name='parser_rule_type')
    parser_rule_type_enum.create(op.get_bind(), checkfirst=True)

    # Step 2: Add rule_type column (nullable initially)
    op.add_column(
        'engine_tool_parser_rule',
        sa.Column('rule_type', sa.Enum('tool', 'reasoning', name='parser_rule_type'), nullable=True)
    )

    # Step 3: Set all existing records to 'tool'
    op.execute("UPDATE engine_tool_parser_rule SET rule_type = 'tool'")

    # Step 4: Make rule_type NOT NULL
    op.alter_column('engine_tool_parser_rule', 'rule_type', nullable=False)

    # Step 5: Rename the table from engine_tool_parser_rule to engine_parser_rule
    op.rename_table('engine_tool_parser_rule', 'engine_parser_rule')

    # Step 6: Rename indexes (if they exist - use IF EXISTS for safety)
    op.execute("ALTER INDEX IF EXISTS ix_engine_tool_parser_rule_engine_id RENAME TO ix_engine_parser_rule_engine_id")
    op.execute("ALTER INDEX IF EXISTS ix_engine_tool_parser_rule_priority RENAME TO ix_engine_parser_rule_priority")
    op.execute("ALTER INDEX IF EXISTS ix_engine_tool_parser_rule_enabled RENAME TO ix_engine_parser_rule_enabled")

    # Step 7: Rename foreign key constraint
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_engine_tool_parser_rule_engine_id') THEN
                ALTER TABLE engine_parser_rule
                RENAME CONSTRAINT fk_engine_tool_parser_rule_engine_id
                TO fk_engine_parser_rule_engine_id;
            END IF;
        END $$;
    """)

    # Step 8: Add index on rule_type for efficient filtering
    op.create_index('ix_engine_parser_rule_rule_type', 'engine_parser_rule', ['rule_type'])


def downgrade() -> None:
    # Step 1: Drop the rule_type index
    op.drop_index('ix_engine_parser_rule_rule_type', table_name='engine_parser_rule')

    # Step 2: Rename foreign key constraint back
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_engine_parser_rule_engine_id') THEN
                ALTER TABLE engine_parser_rule
                RENAME CONSTRAINT fk_engine_parser_rule_engine_id
                TO fk_engine_tool_parser_rule_engine_id;
            END IF;
        END $$;
    """)

    # Step 3: Rename indexes back
    op.execute("ALTER INDEX IF EXISTS ix_engine_parser_rule_enabled RENAME TO ix_engine_tool_parser_rule_enabled")
    op.execute("ALTER INDEX IF EXISTS ix_engine_parser_rule_priority RENAME TO ix_engine_tool_parser_rule_priority")
    op.execute("ALTER INDEX IF EXISTS ix_engine_parser_rule_engine_id RENAME TO ix_engine_tool_parser_rule_engine_id")

    # Step 4: Rename the table back
    op.rename_table('engine_parser_rule', 'engine_tool_parser_rule')

    # Step 5: Drop rule_type column
    op.drop_column('engine_tool_parser_rule', 'rule_type')

    # Step 6: Drop the enum type
    sa.Enum(name='parser_rule_type').drop(op.get_bind(), checkfirst=True)
