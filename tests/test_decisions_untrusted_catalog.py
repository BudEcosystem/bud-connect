"""The curated decision models still land when the catalog SDK's fetch cannot be trusted.

bud-runtime spec 031 (C7.2). The SDK guards in ``TensorZeroParser.parse_model_data`` turn an empty
or LiteLLM-only fetch into a failed sync, so yesterday's rows are kept rather than retired. On
2026-11-08 the ai-models source (``truefoundry/models``) started answering 404, so every sync now
trips that guard -- and the curated decision models, merged after it, could never be seeded.

The curated file is ours and is validated on load, so applying it ADDITIVELY is safe while the
SDK is untrusted: upsert its providers and models, retire nothing, and still fail the sync so the
cron reports the outage.
"""

import asyncio
import importlib
import sys
import types
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from budconnect.commons.exceptions import SeederException


@pytest.fixture(scope="module")
def tz():
    """Load the real seeder module without its package's import side effects (as test_decisions_catalog)."""
    saved = {k: sys.modules.get(k) for k in ("budconnect.seeders", "budconnect.seeders.tensorzero")}
    import budconnect

    pkg = types.ModuleType("budconnect.seeders")
    pkg.__path__ = [str(Path(budconnect.__file__).parent / "seeders")]
    sys.modules["budconnect.seeders"] = pkg
    sys.modules.pop("budconnect.seeders.tensorzero", None)
    try:
        yield importlib.import_module("budconnect.seeders.tensorzero")
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


class _RecordingCRUD:
    """A ProviderCRUD / ModelInfoCRUD double that records every upsert."""

    def __init__(self, sink: List[Dict[str, Any]]) -> None:
        self.sink = sink

    def __enter__(self) -> "_RecordingCRUD":
        return self

    def __exit__(self, *exc: Any) -> None:
        return None

    def upsert(self, data: Dict[str, Any], conflict_target: List[str]) -> Any:
        self.sink.append(data)
        return uuid4()

    def add_engine_version(self, row_id: Any, version_id: Any) -> None:
        return None


class _EngineCRUD:
    def __init__(self, engine: Any) -> None:
        self.engine = engine

    def __enter__(self) -> "_EngineCRUD":
        return self

    def __exit__(self, *exc: Any) -> None:
        return None

    @contextmanager
    def get_session(self) -> Any:
        yield MagicMock()

    def fetch_one(self, conditions: Dict[str, Any], session: Any) -> Any:
        return self.engine


@pytest.fixture
def seeded(tz, monkeypatch, tmp_path):
    """Run ``TensorZeroSeeder.seed`` with the SDK untrusted; return what was written and retired."""
    providers: List[Dict[str, Any]] = []
    models: List[Dict[str, Any]] = []
    engine = SimpleNamespace(versions=[SimpleNamespace(version="0.1.0", id=uuid4())])
    data_file = tmp_path / "models.json"
    data_file.write_text("{}")

    tensorzero = tz
    TensorZeroParser, TensorZeroSeeder = tz.TensorZeroParser, tz.TensorZeroSeeder

    async def untrusted() -> Any:
        raise tz.UntrustedCatalogError("ai-models source was unavailable")

    async def no_licenses(self) -> Dict[str, Any]:
        return {}

    async def version_file(version: str) -> str:
        return str(data_file)

    monkeypatch.setattr(tensorzero, "EngineCRUD", lambda: _EngineCRUD(engine))
    monkeypatch.setattr(tensorzero, "ProviderCRUD", lambda: _RecordingCRUD(providers))
    monkeypatch.setattr(tensorzero, "ModelInfoCRUD", lambda: _RecordingCRUD(models))
    monkeypatch.setattr(TensorZeroParser, "parse_model_data", staticmethod(untrusted))
    monkeypatch.setattr(TensorZeroSeeder, "get_license_id_map", no_licenses)
    monkeypatch.setattr(TensorZeroSeeder, "get_version_file_path", staticmethod(version_file))
    monkeypatch.setattr(TensorZeroSeeder, "get_existing_provider_types", lambda self, vid: {"retired_vendor": uuid4()})
    monkeypatch.setattr(TensorZeroSeeder, "get_existing_model_uris", lambda self, vid: {"retired_vendor/m": uuid4()})
    retire_providers = MagicMock(return_value=0)
    retire_models = MagicMock(return_value=0)
    monkeypatch.setattr(TensorZeroSeeder, "deactivate_stale_providers", retire_providers)
    monkeypatch.setattr(TensorZeroSeeder, "deactivate_stale_models", retire_models)

    raised = None
    try:
        asyncio.run(TensorZeroSeeder().seed())
    except SeederException as exc:  # BaseException subclass
        raised = exc
    return SimpleNamespace(
        providers=providers,
        models=models,
        raised=raised,
        retire_providers=retire_providers,
        retire_models=retire_models,
    )


def test_the_sync_still_fails_so_the_outage_is_reported(tz, seeded):
    """The cron must still see a failed sync, or nobody learns the SDK is down."""
    assert isinstance(seeded.raised, tz.UntrustedCatalogError)
    assert "ai-models" in str(seeded.raised)


def test_nothing_is_retired_while_the_catalog_is_untrusted(seeded):
    """The run never saw the real catalog, so its absences mean nothing."""
    seeded.retire_providers.assert_not_called()
    seeded.retire_models.assert_not_called()


def test_every_curated_decision_model_is_upserted(tz, seeded):
    """Every curated entry lands, including the tier-1 vendors the spike verified."""
    curated = {entry["uri"] for entry in tz.load_decision_models()}
    written = {row["uri"] for row in seeded.models}
    assert curated <= written, f"missing: {sorted(curated - written)}"
    assert {"typesafe/jev-latest", "embedding_space/laya", "openai/gpt-6-luna"} <= written


def test_only_curated_models_are_written(tz, seeded):
    """Nothing else is written: the LiteLLM-only fetch is not applied."""
    curated = {entry["uri"] for entry in tz.load_decision_models()}
    assert {row["uri"] for row in seeded.models} == curated


def test_curated_models_keep_their_decisions_route_and_limits(seeded):
    """The fallback goes through the real ``create_model_info``, routes and limits intact."""
    laya = next(row for row in seeded.models if row["uri"] == "embedding_space/laya")
    assert "/v1/decisions" in [str(getattr(e, "value", e)) for e in laya["endpoints"]]
    assert laya["decision_limits"]["max_choices"] == 128


def test_decision_providers_and_the_generic_source_are_upserted(seeded):
    """Their credential forms must exist for budapp, the generic source included."""
    written = {row["provider_type"] for row in seeded.providers}
    assert {"typesafe", "embedding_space", "system_one_compatible", "openai"} <= written
