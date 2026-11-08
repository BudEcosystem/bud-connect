"""Add the decisions route and the decisions capability.

Revision ID: n9o0p1q2r3s4
Revises: m8n9o0p1q2r3
Create Date: 2026-11-08

bud-runtime spec 031 (decision models): the catalog now says which models are served at
``/v1/decisions`` and which providers budgateway can serve that route for -- natively (OpenAI,
Azure) or through the System One route at the provider's ``decisions_url``.

Labels are the enum MEMBER NAMES, uppercase -- ``DECISIONS`` for ``/v1/decisions`` and for
``decisions`` -- because ``model_info.endpoints`` and ``provider.capabilities`` are
``ARRAY(Enum(...))`` with no ``values_callable``, so SQLAlchemy stores names (see l7m8n9o0p1q2,
which this copies). ALTER TYPE ADD VALUE in an autocommit block needs no type rewrite and no cast
of the dependent ARRAY columns.

Order of deployment:

* **budapp release N first** (spec 031 D-15). budapp N knows the capability and the route; an
  older budapp aborts its provider sync on a capability it does not know.
* **The writer is the catalog data, not this revision.** Nothing carries either label until
  ``tensorzero_providers.json`` declares ``decisions`` and the curated seed lists the route, which
  ship in the same change as this revision. Rolling bud-connect back past it leaves rows an older
  image cannot read: SQLAlchemy's enum processor raises ``LookupError`` on ``DECISIONS`` in any API
  read of those models or providers. The older image's own sync repairs them (it reads existing
  rows by ``uri``/``id`` columns only and upserts with Core inserts, so it never loads the unknown
  label), so run that sync immediately after such a rollback.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "n9o0p1q2r3s4"
down_revision: Union[str, None] = "m8n9o0p1q2r3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the DECISIONS label to both enums."""
    # ADD VALUE cannot run inside a transaction block on older PostgreSQL, and even on 12+
    # the value is unusable in the transaction that added it.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE modelendpointenum ADD VALUE IF NOT EXISTS 'DECISIONS'")
        op.execute("ALTER TYPE providercapabilityenum ADD VALUE IF NOT EXISTS 'DECISIONS'")


def downgrade() -> None:
    """Leave the labels in place."""
    # PostgreSQL cannot drop an enum value; removing one means recreating the type and
    # casting every dependent column. The unused labels are harmless.
    pass
