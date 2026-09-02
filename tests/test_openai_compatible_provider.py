"""Seed-data + seeder-source contract tests for the ``openai_compatible`` provider.

These tests are deliberately dependency free: they read the seed JSON and parse the
seeder source with :mod:`ast`.  Importing ``budconnect.seeders.tensorzero`` would pull
in the DB/config stack, so the seeder is never imported here.

Covers:
  * C11 - ``tensorzero_providers.json`` carries an ``openai_compatible`` entry with the
    right name/icon/capabilities and exactly two credential fields.
  * C12 - the explicit "no catalog models" provider list inside
    ``budconnect/seeders/tensorzero.py`` includes ``openai_compatible``.  Providers absent
    from that list are never inserted, because the main loop only walks providers that
    have catalog models.
  * A drift guard: every provider named in that list must exist in the JSON.
  * Cross-repo consistency with budapp's bootstrap copy of the same provider entry.
"""

import ast
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
PROVIDERS_JSON_PATH = REPO_ROOT / "budconnect" / "seeders" / "data" / "tensorzero" / "tensorzero_providers.json"
SEEDER_SOURCE_PATH = REPO_ROOT / "budconnect" / "seeders" / "tensorzero.py"
CONSTANTS_SOURCE_PATH = SEEDER_SOURCE_PATH.parent / "constants.py"

PROVIDER_KEY = "openai_compatible"
EXPECTED_NAME = "OpenAI-Compatible"
EXPECTED_ICON = "icons/providers/openai_compatible.png"
EXPECTED_CAPABILITIES = ["model"]

# budapp keeps a bootstrap copy of the provider seed so a fresh install works before the
# first bud-connect sync.  The sync overwrites it from this repo, so the two must agree.
#
# budapp lives in a DIFFERENT repository, so its checkout has to be located rather than
# assumed.  Order: an explicit env var, then the ordinary side-by-side clone layout.  A
# hardcoded absolute default is worse than nothing -- it exists on exactly one machine and
# turns the cross-repo checks into silent skips everywhere else, CI included.
BUDAPP_SEEDER_ENV_VAR = "BUDAPP_PROVIDERS_SEEDER_PATH"
BUDAPP_RUNTIME_ROOT_ENV_VAR = "BUD_RUNTIME_ROOT"
BUDAPP_SEEDER_RELATIVE_PATH = Path("services/budapp/budapp/initializers/data/providers_seeder.json")
BUDAPP_RUNTIME_DIR_NAMES = ("bud-runtime", "bud-stack", "budruntime")

# A neighbouring provider whose credential-field dicts define the house shape.
REFERENCE_PROVIDER_KEY = "azure"


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------


def _load_providers() -> Dict[str, Any]:
    with PROVIDERS_JSON_PATH.open() as handle:
        return json.load(handle)


def _reference_field_keys(providers: Dict[str, Any]) -> frozenset:
    """Keys every credential field of the reference provider carries.

    Optional extras (e.g. ``dependencies``) only appear on some fields, so the shared
    shape is the intersection across all of that provider's fields.
    """
    reference = providers[REFERENCE_PROVIDER_KEY]["credentials"]
    assert reference, f"{REFERENCE_PROVIDER_KEY!r} has no credential fields to compare against"
    shared = frozenset(reference[0].keys())
    for field in reference[1:]:
        shared &= frozenset(field.keys())
    return shared


def _fields_by_name(entry: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {field["field"]: field for field in entry["credentials"]}


def _no_model_provider_list() -> List[str]:
    """Extract the literal provider list the seeder iterates for catalog-less providers.

    Parsed out of the source with :mod:`ast` - importing the seeder would drag in the
    database and settings stack.

    FRD-018 moved this list out of the ``for provider_type in [...]`` literal in the seeder and
    into ``budconnect/seeders/constants.py`` as ``NO_MODEL_PROVIDERS``, so that the voice
    providers could be added alongside a test guarding the omission. The extraction follows it;
    the guarantee this helper provides is unchanged.
    """
    tree = ast.parse(CONSTANTS_SOURCE_PATH.read_text(), filename=str(CONSTANTS_SOURCE_PATH))

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "NO_MODEL_PROVIDERS" for t in node.targets):
            continue
        try:
            values = ast.literal_eval(node.value)
        except ValueError:
            continue
        if isinstance(values, list) and all(isinstance(v, str) for v in values):
            return values

    pytest.fail(
        "Could not locate the `NO_MODEL_PROVIDERS` string list in "
        f"{CONSTANTS_SOURCE_PATH}. If the seeder was refactored again, update this test."
    )


def _normalise_credentials(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Credential fields ordered by their declared ``order`` for order-insensitive compare."""
    return sorted(
        (dict(field) for field in entry["credentials"]),
        key=lambda field: (field.get("order", 0), field.get("field", "")),
    )


# --------------------------------------------------------------------------------------
# C11 - seed data
# --------------------------------------------------------------------------------------


def test_openai_compatible_provider_present_in_seed_json():
    providers = _load_providers()
    assert PROVIDER_KEY in providers, (
        f"{PROVIDER_KEY!r} missing from {PROVIDERS_JSON_PATH}. Present keys: {sorted(providers)}"
    )


def test_openai_compatible_provider_metadata():
    providers = _load_providers()
    entry = providers.get(PROVIDER_KEY)
    assert entry is not None, f"{PROVIDER_KEY!r} missing from {PROVIDERS_JSON_PATH}"

    assert entry["name"] == EXPECTED_NAME
    assert entry["icon"] == EXPECTED_ICON
    assert entry["capabilities"] == EXPECTED_CAPABILITIES
    assert isinstance(entry.get("description"), str) and entry["description"].strip(), (
        "provider description must be a non-empty string"
    )


def test_openai_compatible_entry_keys_match_neighbouring_provider():
    providers = _load_providers()
    entry = providers.get(PROVIDER_KEY)
    assert entry is not None, f"{PROVIDER_KEY!r} missing from {PROVIDERS_JSON_PATH}"

    reference_keys = set(providers[REFERENCE_PROVIDER_KEY].keys())
    assert set(entry.keys()) == reference_keys, (
        f"top-level keys drifted from {REFERENCE_PROVIDER_KEY!r}: "
        f"missing={sorted(reference_keys - set(entry))}, extra={sorted(set(entry) - reference_keys)}"
    )


def test_openai_compatible_credential_fields():
    providers = _load_providers()
    entry = providers.get(PROVIDER_KEY)
    assert entry is not None, f"{PROVIDER_KEY!r} missing from {PROVIDERS_JSON_PATH}"

    credentials = entry["credentials"]
    assert [field["field"] for field in credentials] == ["api_base", "api_key"], (
        "expected exactly two credential fields, api_base then api_key"
    )

    fields = _fields_by_name(entry)

    api_base = fields["api_base"]
    assert api_base["label"] == "Base URL"
    assert api_base["type"] == "url"
    assert api_base["required"] is True
    assert api_base["order"] == 1

    api_key = fields["api_key"]
    assert api_key["label"] == "API Key"
    assert api_key["type"] == "password"
    assert api_key["required"] is False, (
        "api_key must be optional - unauthenticated llama.cpp/vLLM/Ollama servers are the main use case"
    )
    assert api_key["order"] == 2


def test_openai_compatible_api_base_description_warns_about_chat_completions():
    """The single most common misconfiguration is pasting the /chat/completions URL."""
    providers = _load_providers()
    entry = providers.get(PROVIDER_KEY)
    assert entry is not None, f"{PROVIDER_KEY!r} missing from {PROVIDERS_JSON_PATH}"

    description = _fields_by_name(entry)["api_base"].get("description", "")
    assert "chat/completions" in description.lower(), (
        f"api_base description must tell the user not to include /chat/completions; got: {description!r}"
    )


def test_openai_compatible_credential_field_shape_matches_neighbouring_provider():
    providers = _load_providers()
    entry = providers.get(PROVIDER_KEY)
    assert entry is not None, f"{PROVIDER_KEY!r} missing from {PROVIDERS_JSON_PATH}"

    expected_keys = _reference_field_keys(providers)
    for field in entry["credentials"]:
        assert frozenset(field.keys()) == expected_keys, (
            f"credential field {field.get('field')!r} shape drifted from {REFERENCE_PROVIDER_KEY!r}: "
            f"missing={sorted(expected_keys - set(field))}, extra={sorted(set(field) - expected_keys)}"
        )


# --------------------------------------------------------------------------------------
# C12 - seeder source
# --------------------------------------------------------------------------------------


def test_seeder_seeds_openai_compatible_without_catalog_models():
    """openai_compatible ships no catalog models, so it must be in the explicit list.

    The main seeding loop only iterates providers returned by the model catalog parser;
    a provider missing from this list is never inserted at all.
    """
    provider_types = _no_model_provider_list()
    assert PROVIDER_KEY in provider_types, (
        f"{PROVIDER_KEY!r} missing from the catalog-less provider list in {SEEDER_SOURCE_PATH}. "
        f"Current list: {provider_types}"
    )


# --------------------------------------------------------------------------------------
# drift guard
# --------------------------------------------------------------------------------------


def test_every_seeded_no_model_provider_exists_in_seed_json():
    """The seeder indexes the JSON by key - a missing key is a KeyError at seed time."""
    providers = _load_providers()
    missing = [name for name in _no_model_provider_list() if name not in providers]
    assert not missing, (
        f"providers seeded explicitly but absent from {PROVIDERS_JSON_PATH}: {missing}. "
        "The seeder does predefined_providers[provider_type][...] and will raise KeyError."
    )


# --------------------------------------------------------------------------------------
# cross-repo consistency with budapp's bootstrap copy
# --------------------------------------------------------------------------------------


def _budapp_seeder_candidates() -> List[Path]:
    """Every place budapp's bootstrap seed is looked for, in priority order.

    An explicit ``BUDAPP_PROVIDERS_SEEDER_PATH`` is taken as final: if it is set and wrong,
    searching on anyway would quietly compare against some other checkout.  Otherwise the
    ordinary layouts are tried -- ``BUD_RUNTIME_ROOT``, then a bud-runtime clone sitting
    beside, one level above, or under ``$HOME`` next to this repo.
    """
    env_value = os.environ.get(BUDAPP_SEEDER_ENV_VAR)
    if env_value:
        return [Path(env_value).expanduser()]

    roots: List[Path] = []
    runtime_root = os.environ.get(BUDAPP_RUNTIME_ROOT_ENV_VAR)
    if runtime_root:
        roots.append(Path(runtime_root).expanduser())
    for parent in (REPO_ROOT.parent, REPO_ROOT.parent.parent, Path.home()):
        roots.extend(parent / name for name in BUDAPP_RUNTIME_DIR_NAMES)

    seen = set()
    candidates: List[Path] = []
    for root in roots:
        candidate = root / BUDAPP_SEEDER_RELATIVE_PATH
        if candidate not in seen:
            seen.add(candidate)
            candidates.append(candidate)
    return candidates


def resolve_budapp_providers_seeder_path() -> Optional[Path]:
    """The first candidate that exists on disk, or ``None`` if budapp is not checked out."""
    for candidate in _budapp_seeder_candidates():
        if candidate.is_file():
            return candidate
    return None


def _load_budapp_providers() -> Dict[str, Any]:
    path = resolve_budapp_providers_seeder_path()
    if path is None:
        searched = "\n".join(f"    {candidate}" for candidate in _budapp_seeder_candidates())
        pytest.skip(
            "CROSS-REPO DRIFT CHECK NOT RUN: budapp's bootstrap providers_seeder.json was not "
            f"found, so the {PROVIDER_KEY!r} provider entry in this repo was NOT compared against "
            "budapp's copy of it. The two seeds can silently diverge while this reports green.\n"
            f"Set {BUDAPP_SEEDER_ENV_VAR} to budapp's "
            f"{BUDAPP_SEEDER_RELATIVE_PATH} (or {BUDAPP_RUNTIME_ROOT_ENV_VAR} to a bud-runtime "
            "checkout) to enable it.\nLooked in:\n" + searched
        )
    with path.open() as handle:
        return json.load(handle)


def test_budapp_bootstrap_seed_has_openai_compatible():
    """Budapp's bootstrap copy should carry the provider -- but its ABSENCE is not a failure here.

    bud-connect is the source of truth: budapp's ``providers_seeder.json`` is a bootstrap that
    budapp's own sync (``model_ops/scheduler.py``) overwrites wholesale from
    ``/model/get-compatible-models``. And the release ordering REQUIRES bud-connect to ship first --
    shipping budapp first makes that sync soft-delete the provider row and erase the seed entry.

    So there is a legitimate window in which this repo has the provider and budapp does not, and
    failing here would deadlock it: bud-connect's CI could not go green until budapp merged, while
    budapp must not merge until bud-connect has. budapp asserts its own copy in
    ``tests/test_openai_compatible_provider.py::test_providers_seeder_json_declares_openai_compatible``,
    which is where that belongs.

    What must NOT be softened is the equivalence check in
    ``test_budapp_bootstrap_seed_matches_budconnect_seed``: once both sides have the key, they have
    to agree, and that is the drift this pair of tests exists to catch.
    """
    budapp_providers = _load_budapp_providers()
    if PROVIDER_KEY not in budapp_providers:
        pytest.skip(
            f"{PROVIDER_KEY!r} not yet in budapp bootstrap seed "
            f"{resolve_budapp_providers_seeder_path()} -- expected while the budapp half of this "
            f"change is unmerged, since bud-connect ships first by design. Point "
            f"{BUDAPP_SEEDER_ENV_VAR} at a checkout that has it to exercise this."
        )


# --------------------------------------------------------------------------------------
# the discovery of budapp's checkout is itself under test
#
# The two tests below are the ones that matter most -- they are the only thing standing
# between the two repos and silent seed drift -- and they are also the two that vanish
# first: if the budapp seed file cannot be found they `pytest.skip`, which reads as green.
# CI is precisely where budapp is not checked out next to bud-connect, and precisely where
# the drift would appear.  So the resolver gets its own coverage, and the skip has to say
# loudly what was skipped and how to fix it.
# --------------------------------------------------------------------------------------


# Assembled rather than written out so this guard cannot match itself.
_DEV_PATH_MARKERS = ("/data" + "disk/", ".claude/" + "worktrees", "/home/", "/Users/")


def test_budapp_seeder_path_is_not_a_hardcoded_developer_path():
    """A machine-specific absolute default silently disables the cross-repo checks.

    Anywhere but the machine it was written on, the path does not exist, `_load_budapp_providers`
    skips, and the two checks below report green while guarding nothing.
    """
    offenders = [
        f"{number}: {line.strip()}"
        for number, line in enumerate(Path(__file__).read_text().splitlines(), start=1)
        if "_DEV_PATH_MARKERS" not in line and any(marker in line for marker in _DEV_PATH_MARKERS)
    ]
    assert not offenders, (
        "the budapp seed path must be discovered, not hardcoded to one developer's checkout:\n" + "\n".join(offenders)
    )


def test_env_var_pins_the_budapp_seeder_path(tmp_path, monkeypatch):
    """An explicit env var wins outright -- no search, no second-guessing."""
    pinned = tmp_path / "somewhere" / "providers_seeder.json"
    pinned.parent.mkdir(parents=True)
    pinned.write_text("{}")

    monkeypatch.setenv(BUDAPP_SEEDER_ENV_VAR, str(pinned))
    assert resolve_budapp_providers_seeder_path() == pinned


def test_discovery_finds_a_sibling_bud_runtime_checkout(tmp_path, monkeypatch):
    """The normal dev layout: bud-connect and bud-runtime cloned side by side."""
    monkeypatch.delenv(BUDAPP_SEEDER_ENV_VAR, raising=False)
    monkeypatch.delenv("BUD_RUNTIME_ROOT", raising=False)

    connect_root = tmp_path / "bud-connect"
    connect_root.mkdir()
    seeder = tmp_path / "bud-runtime" / BUDAPP_SEEDER_RELATIVE_PATH
    seeder.parent.mkdir(parents=True)
    seeder.write_text("{}")

    monkeypatch.setattr(sys.modules[__name__], "REPO_ROOT", connect_root)
    assert resolve_budapp_providers_seeder_path() == seeder


def test_skip_names_what_was_skipped_and_where_it_looked(tmp_path, monkeypatch):
    """A bare `SKIPPED` next to a drift guard is indistinguishable from a pass."""
    monkeypatch.delenv(BUDAPP_SEEDER_ENV_VAR, raising=False)
    monkeypatch.delenv("BUD_RUNTIME_ROOT", raising=False)

    empty_root = tmp_path / "bud-connect"
    empty_root.mkdir()
    monkeypatch.setattr(sys.modules[__name__], "REPO_ROOT", empty_root)

    with pytest.raises(pytest.skip.Exception) as excinfo:
        _load_budapp_providers()

    message = str(excinfo.value)
    assert BUDAPP_SEEDER_ENV_VAR in message, message
    assert "openai_compatible" in message, message
    assert "budapp" in message, message
    # It must list the places it actually looked, or the reader cannot tell whether the
    # search was wrong or the checkout is genuinely absent.
    assert str(BUDAPP_SEEDER_RELATIVE_PATH) in message, message
    assert "bud-runtime" in message, message


def test_budapp_bootstrap_seed_matches_budconnect_seed():
    budapp_providers = _load_budapp_providers()
    connect_entry = _load_providers().get(PROVIDER_KEY)
    budapp_entry = budapp_providers.get(PROVIDER_KEY)

    # bud-connect is the source of truth, so a missing entry HERE is always a failure.
    assert connect_entry is not None, f"{PROVIDER_KEY!r} missing from {PROVIDERS_JSON_PATH}"

    # budapp's copy legitimately lags until its half merges -- see the docstring on
    # test_budapp_bootstrap_seed_has_openai_compatible for why failing on that would deadlock
    # the release ordering. The moment budapp HAS the key, the equivalence below is enforced.
    if budapp_entry is None:
        pytest.skip(
            f"{PROVIDER_KEY!r} not yet in {resolve_budapp_providers_seeder_path()} -- nothing to "
            f"compare against while the budapp half is unmerged. Point {BUDAPP_SEEDER_ENV_VAR} at "
            f"a checkout that has it to exercise the drift guard."
        )

    assert budapp_entry["name"] == connect_entry["name"]
    assert budapp_entry["icon"] == connect_entry["icon"]
    assert budapp_entry["capabilities"] == connect_entry["capabilities"]
    assert _normalise_credentials(budapp_entry) == _normalise_credentials(connect_entry), (
        "credential field definitions diverge between bud-connect and budapp; the sync "
        "overwrites budapp's copy, so the bootstrap install would behave differently."
    )
