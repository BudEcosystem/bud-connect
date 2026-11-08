"""``ModelDetailsCRUD.upsert`` must work against a real session, not only a mocked CRUD.

budmicroframe's generic ``CRUDMixin.upsert`` calls ``insert`` without importing it, so every CRUD
here overrides ``upsert``. ``ModelDetailsCRUD`` did not: the curated decision details (spec 031)
reached it through the TensorZero seeder and failed live with ``NameError: name 'insert' is not
defined``, while the seeder tests passed on a mocked CRUD. This drives the real method with a
session that records the statement, compiled for postgres; no database needed.
"""

import uuid
from types import SimpleNamespace

from sqlalchemy.dialects import postgresql

from budconnect.model.crud import ModelDetailsCRUD
from budconnect.model.models import ModelDetails


ROW_ID = uuid.UUID("00000000-0000-0000-0000-0000000000aa")


class RecordingSession:
    """A session that keeps every statement it is asked to execute."""

    def __init__(self) -> None:
        """Start with no statements."""
        self.statements = []

    def execute(self, stmt):
        """Record the statement and return a row with a known id."""
        self.statements.append(stmt)
        return SimpleNamespace(first=lambda: SimpleNamespace(id=ROW_ID))

    def commit(self) -> None:
        """Nothing to commit."""

    def rollback(self) -> None:
        """Nothing to roll back."""


def test_upsert_writes_on_conflict_of_model_info_id():
    """The details row is written with ON CONFLICT (model_info_id) and its id is returned."""
    crud = ModelDetailsCRUD.__new__(ModelDetailsCRUD)
    crud.model = ModelDetails
    session = RecordingSession()
    model_info_id = uuid.uuid4()

    returned = crud.upsert(
        data={"model_info_id": model_info_id, "description": "Typed answers with probabilities."},
        conflict_target=["model_info_id"],
        session=session,
    )

    assert returned == ROW_ID
    (stmt,) = session.statements
    sql = str(stmt.compile(dialect=postgresql.dialect()))
    assert sql.startswith("INSERT INTO model_details")
    assert "ON CONFLICT (model_info_id) DO UPDATE" in sql
    set_clause = sql.split("DO UPDATE SET", 1)[1]
    assert "description = %(" in set_clause
    assert "modified_at = CASE WHEN" in set_clause, "modified_at moves only when a value changes"


def test_model_details_overrides_the_broken_base_upsert():
    """ModelDetailsCRUD has its own upsert rather than budmicroframe's."""
    assert "upsert" in vars(ModelDetailsCRUD), "inherits budmicroframe's upsert, which never imports insert"
