"""add the audio capabilities to providercapabilityenum

Revision ID: j5k6l7m8n9o0
Revises: i4j5k6l7m8n9
Create Date: 2026-09-05

The provider catalog now says which voice capabilities each vendor serves, so the
add-model wizard can offer a transcription vendor for transcription and a synthesis
vendor for synthesis. Those values live in ``provider.capabilities`` alongside MODEL
rather than in a second field: budapp already filters providers on this column.

Labels are the enum MEMBER NAMES, uppercase. This column is
``ARRAY(Enum(ProviderCapabilityEnum))`` with no ``values_callable``, so SQLAlchemy
stores names here -- unlike budapp, which stores the lowercase values. Only the JSON
wire (``.value``) reconciles the two, which is why the strings must not drift.

ALTER TYPE ADD VALUE rather than ``op.sync_enum_values``: adding labels needs no type
rewrite and no cast of the dependent ARRAY column. Same shape as
h3i4j5k6l7m8, including the autocommit block -- ADD VALUE cannot run inside a
transaction block on older PostgreSQL, and even on 12+ the value is unusable in the
transaction that added it.

**budapp must be migrated and deployed before this catalog ships the new values.**
budapp validates each incoming capability against its own enum inside an unguarded
loop, so an unknown one stops its whole provider sync half-way.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "j5k6l7m8n9o0"
down_revision: Union[str, None] = "i4j5k6l7m8n9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


VOICE_CAPABILITIES = ("TEXT_TO_SPEECH", "AUDIO_TRANSCRIPTION", "AUDIO_TRANSLATION")


def upgrade() -> None:
    with op.get_context().autocommit_block():
        for value in VOICE_CAPABILITIES:
            op.execute(f"ALTER TYPE providercapabilityenum ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # PostgreSQL cannot drop an enum value; removing one means recreating the type and
    # casting every dependent column. The unused labels are harmless.
    pass
