"""Add decision_limits to model_info.

Revision ID: o0p1q2r3s4t5
Revises: n9o0p1q2r3s4
Create Date: 2026-11-08

bud-runtime spec 031 (FRD D-24, CONTRACTS C7.2): a hosted decision vendor caps what one request may
ask -- SubQ answers at most 16 questions, Embedding Studio at most 128 options per choice, TypeSafe
at most 10 score levels. budapp copies these onto the deployment's ``system_one`` gateway entry and
budgateway refuses an oversized request before calling the vendor, instead of surfacing the
vendor's own 400 (or, for Embedding Studio, a CUDA out-of-memory message).

``{max_questions, max_choices, max_levels, images}``, each optional; an absent key means no limit
beyond the gateway's own. Nullable and additive, so the previous image keeps running against it:
it never names the column. Written by the seeder from ``seeders/data/decisions/decision_models.json``.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "o0p1q2r3s4t5"
down_revision: Union[str, None] = "n9o0p1q2r3s4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the column."""
    op.add_column("model_info", sa.Column("decision_limits", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    """Drop the column."""
    op.drop_column("model_info", "decision_limits")
