"""add the billing rules column to model_info

Revision ID: k6l7m8n9o0p1
Revises: j5k6l7m8n9o0
Create Date: 2026-09-22

``input_cost`` and ``output_cost`` carry one float per cost field. Metering a voice
vendor needs more than a float, and the gap is not academic:

* AWS Transcribe publishes four volume tiers per SKU, per region. We store one.
* Rev AI bills "rounded up to the nearest second, 15 second minimum", so a 3-second
  clip costs the same as a 15-second one. A flat per-second rate bills 3.
* Rev AI quotes Reverb per HOUR and Whisper Large per MINUTE -- two units inside one
  vendor -- while the column says only "0.0000556".
* Cartesia sells credits. There is no per-unit price to store at all.

Billing from the flat rate alone understates short requests and overstates committed
volume, in opposite directions, so the errors do not cancel.

This column carries the RULES and the PROVENANCE; the rate itself stays where it is.
That is deliberate: every existing consumer keeps reading ``input_cost`` and keeps
getting the same number it got yesterday, and only a consumer that opts into
``billing`` changes behaviour. The flat rate is defined to equal the first (most
expensive, undiscounted) tier, so a consumer that ignores tiers errs towards the list
price rather than towards a volume discount nobody has earned.

Nullable and additive, so no backfill: a model with no ``billing`` behaves exactly as
it did before. ``confidence`` is the load-bearing field -- ``UNKNOWN`` means no rate
could be obtained, which a consumer MUST surface rather than bill as zero.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "k6l7m8n9o0p1"
down_revision: Union[str, None] = "j5k6l7m8n9o0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("model_info", sa.Column("billing", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column("model_info", "billing")
