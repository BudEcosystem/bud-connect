"""add_new_model_endpoints

Revision ID: 6c82a81a1806
Revises: fbe0470fc004
Create Date: 2025-09-17 08:45:36.411619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6c82a81a1806'
down_revision: Union[str, None] = 'fbe0470fc004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to modelendpointenum type
    # Using both path values and attribute names for backward compatibility
    op.execute("ALTER TYPE modelendpointenum ADD VALUE IF NOT EXISTS '/v1/audio/translations'")
    op.execute("ALTER TYPE modelendpointenum ADD VALUE IF NOT EXISTS '/v1/documents'")
    op.execute("ALTER TYPE modelendpointenum ADD VALUE IF NOT EXISTS '/v1/images/edits'")
    op.execute("ALTER TYPE modelendpointenum ADD VALUE IF NOT EXISTS '/v1/images/variations'")
    op.execute("ALTER TYPE modelendpointenum ADD VALUE IF NOT EXISTS 'AUDIO_TRANSLATION'")
    op.execute("ALTER TYPE modelendpointenum ADD VALUE IF NOT EXISTS 'DOCUMENT'")
    op.execute("ALTER TYPE modelendpointenum ADD VALUE IF NOT EXISTS 'IMAGE_EDIT'")
    op.execute("ALTER TYPE modelendpointenum ADD VALUE IF NOT EXISTS 'IMAGE_VARIATION'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # You would need to recreate the type and update all columns using it
    # This is a complex operation and typically not done in production
    pass