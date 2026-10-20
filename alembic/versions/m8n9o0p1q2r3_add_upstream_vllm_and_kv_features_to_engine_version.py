"""Add upstream_vllm and kv_features to engine_version.

Revision ID: m8n9o0p1q2r3
Revises: l7m8n9o0p1q2
Create Date: 2026-10-20

bud-runtime FRD-023 (KV-cache tiering): ``/engine/get-compatible-engines`` now tells budsim each engine build's
upstream vLLM base and the KV-cache features verified on it. budsim picks the planner's engine record by version and
upstream minor, and budsim and budcluster render a KV setting (KV events, the cache salt, the CPU tier, FP8 KV) only
for a feature the build lists.

Additive, so the previous image keeps running against it: ``upstream_vllm`` is nullable, and ``kv_features`` is
``NOT NULL`` with a server default of ``[]``, so a row the previous image inserts (it never names the column) lists no
features, which renders exactly as today. The values are written by the seeder (``engines.json``) for the builds it
lists, or through the version API; this revision writes no rows.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "m8n9o0p1q2r3"
down_revision: Union[str, None] = "l7m8n9o0p1q2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the two columns."""
    op.add_column("engine_version", sa.Column("upstream_vllm", sa.String(), nullable=True))
    op.add_column(
        "engine_version",
        sa.Column(
            "kv_features",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    """Drop the two columns."""
    op.drop_column("engine_version", "kv_features")
    op.drop_column("engine_version", "upstream_vllm")
