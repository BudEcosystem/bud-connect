"""Add the realtime route and the realtime_session capability.

Revision ID: l7m8n9o0p1q2
Revises: k6l7m8n9o0p1
Create Date: 2026-09-28

FRD-023 (realtime voice sessions): the catalog now says which models are served at
``/v1/realtime`` and which providers the audio gateway can open a realtime session for.

Labels are the enum MEMBER NAMES, uppercase -- ``REALTIME`` for ``/v1/realtime`` and
``REALTIME_SESSION`` for ``realtime_session`` -- because ``model_info.endpoints`` and
``provider.capabilities`` are ``ARRAY(Enum(...))`` with no ``values_callable``, so SQLAlchemy
stores names (see j5k6l7m8n9o0). Same shape as that migration: ALTER TYPE ADD VALUE in an
autocommit block, which needs no type rewrite and no cast of the dependent ARRAY columns.

Order of deployment:

* **budapp release N first.** budapp's catalog sync skips a provider with a capability it
  does not know and drops an endpoint value it does not know (FRD-023 D-20).
* **The writer is the provider catalog, not this revision.** The seeder drops ``/v1/realtime``
  from every model whose provider lacks ``realtime_session`` (``gate_realtime_route``), so
  nothing carries either label until ``tensorzero_providers.json`` grants it -- which the
  change after this one does, for openai and azure. Shipped a release apart, each step rolls
  back cleanly. Shipped together, rolling bud-connect back past this revision leaves rows an
  older image cannot read: SQLAlchemy's enum processor raises ``LookupError`` on ``REALTIME``
  in any API read of those models or providers. The older image's own sync repairs them (it
  reads existing rows by ``uri``/``id`` columns only and upserts with Core inserts, so it
  never loads the unknown label), so run that sync immediately after such a rollback.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "l7m8n9o0p1q2"
down_revision: Union[str, None] = "k6l7m8n9o0p1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the REALTIME and REALTIME_SESSION labels."""
    # ADD VALUE cannot run inside a transaction block on older PostgreSQL, and even on 12+
    # the value is unusable in the transaction that added it.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE modelendpointenum ADD VALUE IF NOT EXISTS 'REALTIME'")
        op.execute("ALTER TYPE providercapabilityenum ADD VALUE IF NOT EXISTS 'REALTIME_SESSION'")


def downgrade() -> None:
    """Leave the labels in place."""
    # PostgreSQL cannot drop an enum value; removing one means recreating the type and
    # casting every dependent column. The unused labels are harmless.
    pass
