"""`modified_at` on INSERT ... ON CONFLICT DO UPDATE.

The defect: `TimestampMixin.modified_at` relies on an ORM `onupdate` hook, which SQLAlchemy
does not apply to the SET clause of a Core `on_conflict_do_update`. Every upsert in this
service is Core-level, so the column held insert time forever. Seen live: seven corrupted
rows restored by a 09:20-09:28 sync all still reported `modified_at` from 08:04 or 08:35.

These compile the statements with the postgres dialect rather than running them, so they
need no database, and then check the whole codebase for upserts that skip the helper.
"""

import ast
import pathlib
import re

import pytest
from sqlalchemy import ARRAY, Column, DateTime, MetaData, String, Table
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB, UUID, insert

from budconnect.commons.upsert import conflict_set_clause


ROOT = pathlib.Path(__file__).parent.parent / "budconnect"

_meta = MetaData()

#: Shaped like model_info: a conflict key, jsonb, an array, and the mixin's timestamps.
MODEL_INFO_LIKE = Table(
    "model_info_like",
    _meta,
    Column("id", UUID, primary_key=True),
    Column("uri", String, unique=True),
    Column("input_cost", JSONB),
    Column("modality", ARRAY(String)),
    Column("created_at", DateTime(timezone=True)),
    Column("modified_at", DateTime(timezone=True)),
)

#: A table with no modified_at at all.
NO_TIMESTAMPS = Table("no_timestamps", _meta, Column("key", String, primary_key=True), Column("value", String))


def compile_upsert(table: Table, row: dict, conflict_target: list, set_: dict | None = None) -> str:
    stmt = insert(table).values(row)
    clause = conflict_set_clause(
        stmt, row if set_ is None else set_(stmt) if callable(set_) else set_, conflict_target
    )
    stmt = stmt.on_conflict_do_update(index_elements=conflict_target, set_=clause)
    return str(stmt.compile(dialect=postgresql.dialect()))


def on_conflict_part(sql: str) -> str:
    return sql.split("ON CONFLICT", 1)[1]


ROW = {"id": "00000000-0000-0000-0000-000000000001", "uri": "a/b", "input_cost": {"x": 1}, "modality": ["TEXT"]}


def test_modified_at_is_written_on_conflict():
    """The defect itself: before the fix `modified_at` did not appear in the SET clause."""
    assert "modified_at =" in on_conflict_part(compile_upsert(MODEL_INFO_LIKE, ROW, ["uri"]))


def test_modified_at_moves_only_when_a_value_changed():
    """ "Last changed", not "last touched".

    The catalog sync rewrites every row every 24 hours. Bumping unconditionally would make
    every row look freshly modified after each sync, which hides a real price change just
    as thoroughly as never bumping it did.
    """
    sql = on_conflict_part(compile_upsert(MODEL_INFO_LIKE, ROW, ["uri"]))
    assert "CASE WHEN" in sql
    assert "IS DISTINCT FROM excluded.input_cost" in sql
    assert "IS DISTINCT FROM excluded.modality" in sql
    # otherwise it keeps what it had
    assert re.search(r"ELSE model_info_like\.modified_at END", sql)


def test_the_conflict_key_and_id_are_not_compared():
    """Equal by definition on a conflict; comparing them is noise."""
    sql = on_conflict_part(compile_upsert(MODEL_INFO_LIKE, ROW, ["uri"]))
    assert "model_info_like.uri IS DISTINCT FROM" not in sql
    assert "model_info_like.id IS DISTINCT FROM" not in sql


def test_created_at_is_never_overwritten_on_conflict():
    """A conflict means the row already existed, so its creation time cannot change."""
    row = {**ROW, "created_at": "2030-01-01T00:00:00+00:00"}
    sql = on_conflict_part(compile_upsert(MODEL_INFO_LIKE, row, ["uri"]))
    assert "created_at =" not in sql


def test_a_table_without_modified_at_is_left_alone():
    sql = on_conflict_part(compile_upsert(NO_TIMESTAMPS, {"key": "k", "value": "v"}, ["key"]))
    assert "modified_at" not in sql
    assert "value = excluded.value" in sql or "value = %(" in sql


def test_a_caller_setting_modified_at_explicitly_is_respected():
    """Some caller may one day manage it deliberately; the helper must not fight it."""
    stmt = insert(MODEL_INFO_LIKE).values(ROW)
    clause = conflict_set_clause(stmt, {**ROW, "modified_at": "2020-01-01T00:00:00+00:00"}, ["uri"])
    assert clause["modified_at"] == "2020-01-01T00:00:00+00:00"


def test_nothing_to_compare_adds_no_case():
    """Only the conflict key in the SET clause: nothing can change, so nothing to track."""
    stmt = insert(MODEL_INFO_LIKE).values(ROW)
    clause = conflict_set_clause(stmt, {"uri": "a/b"}, ["uri"])
    assert "modified_at" not in clause


def test_it_works_for_callers_that_set_from_excluded():
    """model_details and model_architecture write `stmt.excluded.<col>` rather than values."""
    sql = on_conflict_part(
        compile_upsert(
            MODEL_INFO_LIKE,
            ROW,
            ["uri"],
            set_=lambda s: {"input_cost": s.excluded.input_cost, "modality": s.excluded.modality},
        )
    )
    assert "CASE WHEN" in sql
    assert "IS DISTINCT FROM excluded.input_cost" in sql


def test_it_works_for_a_batch_insert():
    """model_architecture inserts a list of records in one statement."""
    stmt = insert(MODEL_INFO_LIKE).values([ROW, {**ROW, "id": "00000000-0000-0000-0000-000000000002", "uri": "c/d"}])
    clause = conflict_set_clause(stmt, {"input_cost": stmt.excluded.input_cost}, ["uri"])
    sql = str(stmt.on_conflict_do_update(index_elements=["uri"], set_=clause).compile(dialect=postgresql.dialect()))
    assert "CASE WHEN" in on_conflict_part(sql)


# --------------------------------------------------------------------------------- #
# every upsert in the codebase has to go through the helper
# --------------------------------------------------------------------------------- #


def _upsert_calls() -> list[tuple[pathlib.Path, int, ast.Call]]:
    found = []
    for path in sorted(ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "on_conflict_do_update"
            ):
                found.append((path, node.lineno, node))
    return found


def test_there_are_upserts_to_check():
    """If this drops to zero the next test is vacuous, not passing."""
    assert len(_upsert_calls()) >= 8


@pytest.mark.parametrize(
    "path_line_call",
    _upsert_calls(),
    ids=lambda plc: f"{plc[0].relative_to(ROOT)}:{plc[1]}",
)
def test_every_upsert_routes_its_set_clause_through_the_helper(path_line_call):
    """A new upsert written the obvious way reintroduces the bug silently.

    `on_conflict_do_update(set_=obj)` reads as complete and correct, and the only symptom is
    a timestamp nobody looks at until they need it. So this is enforced, not reviewed.
    """
    path, line, call = path_line_call
    set_kw = next((kw for kw in call.keywords if kw.arg == "set_"), None)
    assert set_kw is not None, f"{path.name}:{line} passes no set_"
    assert isinstance(set_kw.value, ast.Call) and ast.unparse(set_kw.value.func).endswith("conflict_set_clause"), (
        f"{path.relative_to(ROOT)}:{line} builds its SET clause directly; wrap it in "
        "conflict_set_clause() or modified_at will never move on conflict"
    )


@pytest.mark.parametrize(
    "path_line_call",
    _upsert_calls(),
    ids=lambda plc: f"{plc[0].relative_to(ROOT)}:{plc[1]}",
)
def test_no_upsert_hands_the_helper_a_modified_at(path_line_call):
    """No caller passes modified_at, which would opt it out of change detection.

    The helper respects an explicit value and so bumps the column on every run.
    `seeders/model_details.py` did exactly that with `stmt.excluded.modified_at`.
    """
    path, line, call = path_line_call
    set_kw = next(kw for kw in call.keywords if kw.arg == "set_")
    assert "'modified_at'" not in ast.unparse(set_kw.value), (
        f"{path.relative_to(ROOT)}:{line} sets modified_at itself, so it moves on every sync"
    )


#: model_info's billing column, where the catalog stamps provenance dates.
WITH_BILLING = Table(
    "model_info_billing",
    _meta,
    Column("uri", String, unique=True),
    Column("billing", JSONB),
    Column("modified_at", DateTime(timezone=True)),
)


def test_the_date_a_price_was_read_is_not_a_change_to_it():
    """A change to billing provenance alone does not move modified_at.

    `billing.source.checked_on` is the date of every sync. Compared raw, every billed row
    changed once a day and modified_at meant "last synced" for the rows that matter most.
    Verified in Postgres: a checked_on/published-only difference compares as not distinct;
    a rate difference compares as distinct.
    """
    sql = on_conflict_part(compile_upsert(WITH_BILLING, {"uri": "a/b", "billing": {}}, ["uri"]))
    assert "#-" in sql
    assert sql.count("CAST(") >= 4  # both provenance paths, stripped on both sides


def test_provenance_is_only_stripped_from_an_object():
    """Provenance paths are stripped only from a JSON object.

    `#-` on a JSON scalar raises "cannot delete path in scalar", and most rows store billing
    as JSON null -- stripping unconditionally would fail every upsert.
    """
    sql = on_conflict_part(compile_upsert(WITH_BILLING, {"uri": "a/b", "billing": {}}, ["uri"]))
    assert "jsonb_typeof(model_info_billing.billing)" in sql
    assert "jsonb_typeof(excluded.billing)" in sql


def test_columns_without_provenance_compare_as_before():
    """Only billing has provenance paths; other columns compare as they did."""
    sql = on_conflict_part(compile_upsert(MODEL_INFO_LIKE, ROW, ["uri"]))
    assert "#-" not in sql
