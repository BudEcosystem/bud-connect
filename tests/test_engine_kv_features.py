"""Engine versions carry ``upstream_vllm`` and ``kv_features`` (FRD-023 Phase 0 in bud-runtime).

budsim and budcluster render KV-cache settings (KV events, the cache salt, the CPU tier, FP8 KV) only for the
features the engine build lists, and pick the planner's engine record by version and upstream vLLM base. A feature is
listed only once it has been verified on that build, so the names are validated against the closed set the consumers
know, and every path that copies a version into a response must carry both fields:
``/engine/get-compatible-engines`` is how budsim learns them.

As in ``test_compatible_models_payload``, the services and routes are read as source: they reach the ORM and cannot
be imported standalone.
"""

import ast
import json
import pathlib

import pytest
from pydantic import ValidationError

from budconnect.engine.schemas import (
    KV_FEATURES,
    CompatibleEngine,
    EngineVersion,
    EngineVersionCreate,
    EngineVersionUpdate,
)


ROOT = pathlib.Path(__file__).parent.parent / "budconnect"
ENGINE = ROOT / "engine"
FIELDS = ("upstream_vllm", "kv_features")
ENGINE_ID = "5b6a3a8e-6d55-4f4a-9b3a-1f2e3d4c5b6a"
VERSION_ID = "0f1e2d3c-4b5a-4968-8776-655443322110"


# ---------------------------------------------------------------------- the closed set and validation


def test_the_feature_names_are_the_set_budsim_and_budcluster_know():
    """The names must match the simulator's ``KV_FEATURES`` (engine/record.py) one for one."""
    assert (
        frozenset(
            {
                "kv_events",
                "cache_salt",
                "cpu_offload_shm",
                "cpu_offload_host_alloc",
                "cpu_offload_shm_per_copy",
                "kv_fp8",
                "tiering_fs",
            }
        )
        == KV_FEATURES
    )


def test_a_version_s_features_are_validated_deduplicated_and_sorted():
    """A known name is kept, a repeat collapses, and the order is canonical."""
    version = EngineVersionCreate(
        engine_id=ENGINE_ID,
        version="0.10.0",
        device_architecture="CUDA",
        container_image="registry.bud.studio/runtime/vllm-cuda:0.10.0",
        upstream_vllm="0.31.0",
        kv_features=["kv_events", "cpu_offload_shm", "kv_events", "cache_salt"],
    )
    assert version.kv_features == ["cache_salt", "cpu_offload_shm", "kv_events"]
    assert version.upstream_vllm == "0.31.0"


def test_an_unknown_feature_name_is_refused():
    """A typo would silently render nothing downstream, so it is a 422, not a stored row."""
    with pytest.raises(ValidationError, match="kv_offload"):
        EngineVersionCreate(
            engine_id=ENGINE_ID,
            version="0.10.0",
            device_architecture="CUDA",
            container_image="x",
            kv_features=["kv_offload"],
        )


@pytest.mark.parametrize("value", ["0.31.0", "0.30", "0.26.0.dev+481e481be", "0.31.0rc1"])
def test_upstream_vllm_accepts_release_and_dev_versions(value):
    """The planner matches the upstream minor; a fork records its dev build and commit."""
    assert (
        EngineVersionCreate(
            engine_id=ENGINE_ID, version="0.10.0", device_architecture="CUDA", container_image="x", upstream_vllm=value
        ).upstream_vllm
        == value
    )


@pytest.mark.parametrize("value", ["v0.31.0", "latest", "0.31 0", ""])
def test_upstream_vllm_refuses_what_is_not_a_version(value):
    """A tag-style or free-text value would never match a planner record."""
    with pytest.raises(ValidationError):
        EngineVersionCreate(
            engine_id=ENGINE_ID, version="0.10.0", device_architecture="CUDA", container_image="x", upstream_vllm=value
        )


def test_defaults_mean_no_upstream_and_no_features():
    """A version created without the fields lists nothing: every KV setting stays off for it."""
    version = EngineVersionCreate(engine_id=ENGINE_ID, version="1.0", device_architecture="CPU", container_image="x")
    assert version.upstream_vllm is None and version.kv_features == []
    assert (
        CompatibleEngine(engine="vllm", device_architecture="CUDA", version="1", container_image="x").kv_features == []
    )


def test_an_update_leaves_unset_fields_alone_and_can_clear_the_features():
    """``None`` keeps the stored value; an empty list withdraws every feature."""
    assert EngineVersionUpdate().kv_features is None and EngineVersionUpdate().upstream_vllm is None
    assert EngineVersionUpdate(kv_features=[]).kv_features == []
    with pytest.raises(ValidationError):
        EngineVersionUpdate(kv_features=["not_a_feature"])


def test_the_response_schemas_carry_both_fields():
    """The version and the compatible-engine payloads declare both fields."""
    for schema in (EngineVersion, CompatibleEngine):
        assert set(FIELDS) <= set(schema.model_fields)
    shown = EngineVersion(
        id=VERSION_ID,
        version="0.10.0",
        device_architecture="CUDA",
        container_image="x",
        engine_id=ENGINE_ID,
        upstream_vllm="0.31.0",
        kv_features=["kv_events"],
    )
    assert shown.model_dump()["kv_features"] == ["kv_events"]


# ---------------------------------------------------------------------- every copy carries the fields


def _calls(path: pathlib.Path, names):
    tree = ast.parse(path.read_text())
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
            if name in names:
                out.append(node)
    return out


@pytest.mark.parametrize(
    "path, names, minimum",
    [
        (ENGINE / "routes.py", {"EngineVersion"}, 3),  # create, get and update responses
        (ENGINE / "services.py", {"EngineVersionSchema"}, 1),  # the paginated listing
        (ENGINE / "services.py", {"EngineVersion"}, 1),  # the ORM row a create inserts
        (ENGINE / "crud.py", {"CompatibleEngine"}, 1),  # /engine/get-compatible-engines
    ],
)
def test_every_copy_of_a_version_passes_both_fields(path, names, minimum):
    """A field left out of a hand-built payload arrives as its default.

    The column is set and the consumer sees nothing. Every construction of these objects must name both fields.
    """
    calls = _calls(path, names)
    assert len(calls) >= minimum, f"expected {minimum} constructions in {path.name}"
    for call in calls:
        keywords = {kw.arg for kw in call.keywords}
        assert set(FIELDS) <= keywords, f"{path.name}:{call.lineno} omits {set(FIELDS) - keywords}"


def test_the_compatible_engines_query_selects_both_columns():
    """The query builds ``CompatibleEngine`` from labelled columns; a column it does not select cannot be passed."""
    source = (ENGINE / "crud.py").read_text()
    for field in FIELDS:
        assert f'EngineVersion.{field}.label("{field}")' in source


def test_an_update_applies_both_fields():
    """``update_engine_version`` copies each set field into the UPDATE; one it skips is never written."""
    tree = ast.parse((ENGINE / "services.py").read_text())
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "update_engine_version")
    written = {
        node.slice.value
        for node in ast.walk(fn)
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
    }
    assert set(FIELDS) <= written


# ---------------------------------------------------------------------- storage


def test_the_engine_version_table_has_both_columns():
    """The table has both columns, and ``kv_features`` defaults to ``[]`` on the server.

    So a row an older image inserts still lists nothing rather than failing the NOT NULL. Read as source: the models
    import the package's ORM graph.
    """
    tree = ast.parse((ENGINE / "models.py").read_text())
    cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "EngineVersion")
    columns = {
        node.target.id: ast.unparse(node.value)
        for node in cls.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None
    }
    assert "nullable=True" in columns["upstream_vllm"]
    kv = columns["kv_features"]
    assert "JSONB" in kv and "nullable=False" in kv and "'[]'::jsonb" in kv


def test_a_migration_adds_the_columns_additively_at_the_head():
    """One new revision at the head adds both columns.

    Each is nullable or has a server default, and the upgrade drops nothing.
    """
    versions = pathlib.Path(__file__).parent.parent / "alembic" / "versions"
    files = [p for p in versions.glob("*.py") if "kv_features" in p.read_text()]
    assert len(files) == 1, files
    source = files[0].read_text()
    upgrade = source.split("def upgrade", 1)[1].split("def downgrade", 1)[0]
    assert 'op.add_column(\n        "engine_version"' in upgrade or 'op.add_column("engine_version"' in upgrade
    assert "upstream_vllm" in upgrade and "kv_features" in upgrade and "server_default" in upgrade
    assert "drop_" not in upgrade
    downs = {}
    for p in versions.glob("*.py"):
        text = p.read_text()
        rev = text.split('revision: str = "', 1)[1].split('"', 1)[0] if 'revision: str = "' in text else None
        if rev:
            downs[rev] = text
    revision = source.split('revision: str = "', 1)[1].split('"', 1)[0]
    referenced = {
        r for r, t in downs.items() for other in downs if f'down_revision: Union[str, None] = "{r}"' in downs[other]
    }
    assert revision not in referenced, "the KV revision must be the head"


# ---------------------------------------------------------------------- the seeded builds


def _vllm_versions():
    engines = json.loads((ROOT / "seeders" / "data" / "engines.json").read_text())
    return {(v["version"], v["device_architecture"]): v for e in engines if e["name"] == "vllm" for v in e["versions"]}


def test_the_seeded_cuda_build_lists_what_was_verified_on_it():
    """bud-vllm 0.10.0 (upstream v0.31.0) on CUDA.

    KV events and the cache salt, and the CPU tier in register mode, which passed on bare metal. Not the alloc-mode
    tier or per-copy transfers (both need a fork patch the build does not carry), not FP8 KV (no 128K needle-in-a-
    haystack record on this build yet), not the fs tier (vLLM #49829).
    """
    cuda = _vllm_versions()[("0.10.0", "CUDA")]
    assert cuda["upstream_vllm"] == "0.31.0"
    assert cuda["kv_features"] == ["cache_salt", "cpu_offload_shm", "kv_events"]


def test_every_seeded_feature_name_is_known():
    """The seeder writes engines.json as is; a name the consumers don't know would be refused by the API."""
    for (version, device), data in _vllm_versions().items():
        assert set(data.get("kv_features", [])) <= KV_FEATURES, (version, device)


def test_the_seeder_writes_both_fields_for_new_and_existing_versions():
    """The seeder writes both fields for new and existing versions.

    A new version is inserted with them, and an existing one is brought in line with engines.json: the seed is the
    source of truth for the versions it lists, as it is for their compatibilities.
    """
    source = (ROOT / "seeders" / "engine.py").read_text()
    seed_fn = source.split("async def _seed_engine", 1)[1].split("\n    @staticmethod", 1)[0]
    for field in FIELDS:
        assert f'"{field}"' in seed_fn
    assert "_version_kv_fields" in seed_fn
