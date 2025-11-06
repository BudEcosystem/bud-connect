"""add_lora_and_pipeline_parallelism_to_architecture

Revision ID: a1b2c3d4e5f6
Revises: 7c38d2f7df0d
Create Date: 2025-11-03 06:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '7c38d2f7df0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add supports_lora column to model_architecture_class table
    op.add_column(
        'model_architecture_class',
        sa.Column(
            'supports_lora',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false')
        )
    )

    # Add supports_pipeline_parallelism column to model_architecture_class table
    op.add_column(
        'model_architecture_class',
        sa.Column(
            'supports_pipeline_parallelism',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false')
        )
    )


def downgrade() -> None:
    # Remove supports_pipeline_parallelism column
    op.drop_column('model_architecture_class', 'supports_pipeline_parallelism')

    # Remove supports_lora column
    op.drop_column('model_architecture_class', 'supports_lora')
