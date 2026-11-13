"""Bud-Decision-Runtime engine rows (bud-runtime spec 031 DM4, D-41, WP-DM4.3).

A decision-only checkpoint (Laya, Julia, GLiNER) has no root ``config.json`` naming an HF architecture class, so
budsim cannot look its engine up the usual way. Instead budmodel detects the family from the checkpoint's own files
and budsim asks ``/engine/get-compatible-engines`` for ``model_architecture = "decision:<family>"``, keeping only
the rows whose engine is ``bud-decision``. These rows are what makes that lookup answer; without them budsim reports
the model as "deployable once the Bud-Decision-Runtime engine is listed for the <family> family".

The seed file is read as data and ``engine/crud.py`` as source, as ``test_engine_kv_features`` does: the CRUD reaches
the ORM and cannot be imported standalone.
"""

import json
import pathlib


ROOT = pathlib.Path(__file__).parent.parent / "budconnect"
ENGINES_JSON = ROOT / "seeders" / "data" / "engines.json"
CRUD = ROOT / "engine" / "crud.py"

#: the engine name budsim's `engine_ops/bud_decision.py` and budcluster's `ENGINE_PROCESSORS` both key on
ENGINE_NAME = "bud-decision"
#: spec 031 D-41. `decision:kev` joins them with runtime v0.2.0 (D-43), which Kev's kept states need.
ARCHITECTURES = ["decision:laya", "decision:julia", "decision:gliner"]
#: CONTRACTS C9: the published images, one per device architecture
IMAGES = {
    "CUDA": "registry.bud.studio/runtime/decision-runtime-cuda:0.1.0",
    "CPU": "registry.bud.studio/runtime/decision-runtime-cpu:0.1.0",
}


def _engine(name):
    for entry in json.loads(ENGINES_JSON.read_text()):
        if entry.get("name") == name:
            return entry
    raise AssertionError(f"{name} is not in engines.json")


def test_the_runtime_is_listed_for_cuda_and_cpu_at_its_published_images():
    """One version per device architecture, at the image the runtime's release publishes (CONTRACTS C9)."""
    versions = _engine(ENGINE_NAME)["versions"]
    assert {v["device_architecture"]: v["container_image"] for v in versions} == IMAGES
    assert {v["version"] for v in versions} == {"0.1.0"}


def test_every_version_lists_the_decision_family_keys():
    """The lookup is by `decision:<family>` alone, so each version must carry all three keys."""
    for version in _engine(ENGINE_NAME)["versions"]:
        (compatibility,) = version["compatibilities"]
        assert compatibility["architecture"] == ARCHITECTURES
        assert compatibility["supported_endpoints"] == ["DECISIONS"]
        # No KV feature and no parser rule: the runtime holds no KV cache and answers no chat
        assert compatibility["features"] == []


def test_the_keys_name_no_hf_architecture_class():
    """A `decision:` key is budmodel's family, not an HF class, so it can never collide with a real one."""
    classes = {
        arch
        for version in _engine("vllm")["versions"]
        for compatibility in version["compatibilities"]
        for arch in compatibility["architecture"]
    }
    assert not classes & set(ARCHITECTURES)
    assert all(key.startswith("decision:") for key in ARCHITECTURES)


def test_the_runtime_is_never_offered_for_a_chat_model_that_also_serves_decisions():
    """The architecture list must stay non-empty, which is what keeps the endpoint query off these rows.

    `get_compatible_engines` matches an engine either by architecture (a non-empty `architectures` list) or by
    endpoint (an empty one). A vLLM chat model that also answers /v1/decisions asks with `model_endpoints`
    including DECISIONS; were these rows endpoint-matched they would be offered for it, and budcluster would try to
    serve a decoder LLM on an engine that only loads the four decision families. The non-empty list is the guard,
    so `supported_endpoints` above is documentation rather than a matching key.
    """
    for version in _engine(ENGINE_NAME)["versions"]:
        for compatibility in version["compatibilities"]:
            assert compatibility["architecture"], "an empty list would make these rows endpoint-matched"

    # The rule this relies on, read from the CRUD: the endpoint query admits only empty architecture lists.
    source = CRUD.read_text()
    endpoint_query = source[source.index("# Query 2: Endpoint-based matching") : source.index("# Apply optional")]
    assert "jsonb_array_length" in endpoint_query and "== 0" in endpoint_query
