"""rename static_classifier scanner type to bud_raa_classifier

Revision ID: i4j5k6l7m8n9
Revises: h3i4j5k6l7m8
Create Date: 2026-06-26 00:00:00.000000

Renames the ``static_classifier`` value of ``scanner_type_enum`` to
``bud_raa_classifier`` to match the bud-sentinel catalog, where the blazeemb
scanner is now advertised as ``bud_raa_classifier``. PostgreSQL's
``ALTER TYPE ... RENAME VALUE`` rewrites the label in place, so existing
guardrail_rules rows keep their association without a data migration.
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'i4j5k6l7m8n9'
down_revision: Union[str, None] = 'h3i4j5k6l7m8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE scanner_type_enum "
        "RENAME VALUE 'static_classifier' TO 'bud_raa_classifier'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TYPE scanner_type_enum "
        "RENAME VALUE 'bud_raa_classifier' TO 'static_classifier'"
    )
