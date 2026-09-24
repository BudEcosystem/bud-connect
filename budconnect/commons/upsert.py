#  -----------------------------------------------------------------------------
#  Copyright (c) 2024 Bud Ecosystem Inc.
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#      http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  -----------------------------------------------------------------------------

"""Keep ``modified_at`` honest on ``INSERT ... ON CONFLICT DO UPDATE``.

``TimestampMixin.modified_at`` is declared with ``onupdate=lambda: datetime.now(UTC)``. That
hook fires when the ORM flushes an UPDATE, and not otherwise. Every upsert in this service is
Core-level instead -- ``insert(table).values(...).on_conflict_do_update(set_=...)`` -- and
SQLAlchemy does not apply Python-side ``onupdate`` callables to an ``on_conflict_do_update``
SET clause. None of the callers passed ``modified_at`` themselves either, so on every table
that goes through this path the column recorded insert time and never moved again.

That was found by accident: seven deliberately corrupted rows were restored by a sync that
ran 09:20-09:28 UTC, and every one of them still reported ``modified_at`` from 08:04 or
08:35. Anything reading the column to judge staleness was being told nothing.

The fix bumps ``modified_at`` only when a value in the SET clause actually differs from what
the row holds. Bumping it unconditionally would be just as uninformative in the other
direction: the catalog sync touches every row every 24 hours, so every row would look
freshly modified and a real price change would be indistinguishable from a no-op refresh.
"Last changed" is also what the ORM hook it replaces would have meant, since the ORM only
emits an UPDATE for dirty attributes.

The comparison uses ``IS DISTINCT FROM`` so NULLs compare sanely, against ``excluded`` --
the row the INSERT proposed -- which is what every caller's SET clause writes. Every
column this runs over is jsonb, an array, an enum or a scalar, all of which support it. A
plain ``json`` column would not (Postgres has no equality operator for it); none exist on
these tables today.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Sequence

from sqlalchemy import case, literal, or_
from sqlalchemy.dialects.postgresql import Insert


#: Columns that describe the row's own history rather than its data. Neither is compared,
#: and ``created_at`` is never written on conflict: a conflict means the row already exists,
#: so its creation time is by definition not something this statement can change.
_BOOKKEEPING = frozenset({"id", "created_at", "modified_at"})


def conflict_set_clause(
    stmt: Insert,
    set_: Dict[str, Any],
    conflict_target: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Return the SET clause for ``stmt.on_conflict_do_update``, keeping timestamps correct.

    Args:
        stmt: The postgres ``insert(...)`` the clause is for. Needed for ``stmt.excluded``.
        set_: The columns the caller wants written on conflict, exactly as it would have
            passed them to ``on_conflict_do_update``.
        conflict_target: The conflict columns. They are equal by definition on a conflict,
            so comparing them would only add noise to the generated SQL.

    Returns:
        ``set_`` without ``created_at``, and with ``modified_at`` set to the current time if
        any other written column changed and left as it was otherwise. Tables without a
        ``modified_at`` column get ``set_`` back with only ``created_at`` removed.
    """
    table = stmt.table
    clause = {k: v for k, v in set_.items() if k != "created_at"}

    if "modified_at" not in table.c or "modified_at" in set_:
        # Nothing to maintain, or the caller is managing it deliberately.
        return clause

    skip = _BOOKKEEPING | set(conflict_target or ())
    compared = [k for k in clause if k not in skip and k in table.c]
    if not compared:
        return clause

    changed = or_(*(table.c[k].is_distinct_from(stmt.excluded[k]) for k in compared))
    now = literal(datetime.now(timezone.utc), type_=table.c.modified_at.type)
    clause["modified_at"] = case((changed, now), else_=table.c.modified_at)
    return clause
