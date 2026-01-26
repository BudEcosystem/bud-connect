"""change scanner_types to scanner_type and add model fields

Revision ID: f1g2h3i4j5k6
Revises: e5f6g7h8i9j0
Create Date: 2026-01-25 10:00:00.000000

This migration:
- Drops the scanner_types ARRAY column from guardrail_rules
- Adds scanner_type as an enum column (ScannerTypeEnum)
- Adds model_id, model_provider_type, and is_gated columns for model-related rules
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f1g2h3i4j5k6'
down_revision: Union[str, None] = 'e5f6g7h8i9j0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the scanner_type_enum type
    scanner_type_enum = postgresql.ENUM(
        'classifier', 'llm', 'pattern', 'static_classifier',
        name='scanner_type_enum'
    )
    scanner_type_enum.create(op.get_bind(), checkfirst=True)

    # Create the model_provider_type_enum type
    model_provider_type_enum = postgresql.ENUM(
        'cloud_model', 'hugging_face', 'url', 'disk',
        name='model_provider_type_enum'
    )
    model_provider_type_enum.create(op.get_bind(), checkfirst=True)

    # Drop the scanner_types column (ARRAY)
    op.drop_column('guardrail_rules', 'scanner_types')

    # Add scanner_type column (enum)
    op.add_column(
        'guardrail_rules',
        sa.Column('scanner_type', scanner_type_enum, nullable=True)
    )

    # Add model_id column
    op.add_column(
        'guardrail_rules',
        sa.Column('model_id', sa.String(length=255), nullable=True)
    )

    # Add model_provider_type column
    op.add_column(
        'guardrail_rules',
        sa.Column('model_provider_type', model_provider_type_enum, nullable=True)
    )

    # Add is_gated column
    op.add_column(
        'guardrail_rules',
        sa.Column('is_gated', sa.Boolean(), nullable=True)
    )


def downgrade() -> None:
    # Drop the new columns
    op.drop_column('guardrail_rules', 'is_gated')
    op.drop_column('guardrail_rules', 'model_provider_type')
    op.drop_column('guardrail_rules', 'model_id')
    op.drop_column('guardrail_rules', 'scanner_type')

    # Add back the scanner_types column (ARRAY)
    op.add_column(
        'guardrail_rules',
        sa.Column('scanner_types', postgresql.ARRAY(sa.String()), nullable=True)
    )

    # Drop the enum types
    sa.Enum(name='model_provider_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='scanner_type_enum').drop(op.get_bind(), checkfirst=True)
