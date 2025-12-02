"""move_parser_rules_to_engine

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-02 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add engine_id column (nullable initially)
    op.add_column(
        'engine_tool_parser_rule',
        sa.Column('engine_id', UUID(), nullable=True)
    )

    # Step 2: Populate engine_id from engine_version relationship
    op.execute("""
        UPDATE engine_tool_parser_rule
        SET engine_id = (
            SELECT engine_id FROM engine_version
            WHERE engine_version.id = engine_tool_parser_rule.engine_version_id
        )
    """)

    # Step 3: Deduplicate rules - keep one per engine + pattern + match_type
    # Keep the rule with lowest priority (highest precedence), then most recent
    op.execute("""
        DELETE FROM engine_tool_parser_rule
        WHERE id IN (
            SELECT id FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                           PARTITION BY engine_id, pattern, match_type
                           ORDER BY priority ASC, created_at DESC
                       ) as rn
                FROM engine_tool_parser_rule
            ) ranked
            WHERE rn > 1
        )
    """)

    # Step 4: Make engine_id NOT NULL
    op.alter_column('engine_tool_parser_rule', 'engine_id', nullable=False)

    # Step 5: Add foreign key constraint
    op.create_foreign_key(
        'fk_engine_tool_parser_rule_engine_id',
        'engine_tool_parser_rule', 'engine',
        ['engine_id'], ['id'],
        ondelete='CASCADE'
    )

    # Step 6: Drop old index on engine_version_id
    op.drop_index('ix_engine_tool_parser_rule_engine_version_id', table_name='engine_tool_parser_rule')

    # Step 7: Drop engine_version_id column (also drops implicit FK)
    op.drop_column('engine_tool_parser_rule', 'engine_version_id')

    # Step 8: Create new index on engine_id
    op.create_index(
        'ix_engine_tool_parser_rule_engine_id',
        'engine_tool_parser_rule',
        ['engine_id']
    )


def downgrade() -> None:
    # Step 1: Drop the new index
    op.drop_index('ix_engine_tool_parser_rule_engine_id', table_name='engine_tool_parser_rule')

    # Step 2: Add engine_version_id column back (nullable initially)
    op.add_column(
        'engine_tool_parser_rule',
        sa.Column('engine_version_id', UUID(), nullable=True)
    )

    # Step 3: Populate engine_version_id from engine relationship
    # Pick the first engine_version for each engine (by created_at desc = latest)
    op.execute("""
        UPDATE engine_tool_parser_rule
        SET engine_version_id = (
            SELECT id FROM engine_version
            WHERE engine_version.engine_id = engine_tool_parser_rule.engine_id
            ORDER BY created_at DESC
            LIMIT 1
        )
    """)

    # Step 4: Make engine_version_id NOT NULL
    op.alter_column('engine_tool_parser_rule', 'engine_version_id', nullable=False)

    # Step 5: Add back index on engine_version_id
    op.create_index(
        'ix_engine_tool_parser_rule_engine_version_id',
        'engine_tool_parser_rule',
        ['engine_version_id']
    )

    # Step 6: Add back foreign key constraint
    op.create_foreign_key(
        'fk_engine_tool_parser_rule_engine_version_id',
        'engine_tool_parser_rule', 'engine_version',
        ['engine_version_id'], ['id'],
        ondelete='CASCADE'
    )

    # Step 7: Drop engine_id FK constraint
    op.drop_constraint('fk_engine_tool_parser_rule_engine_id', 'engine_tool_parser_rule', type_='foreignkey')

    # Step 8: Drop engine_id column
    op.drop_column('engine_tool_parser_rule', 'engine_id')
