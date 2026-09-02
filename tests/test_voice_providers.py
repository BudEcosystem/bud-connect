"""Voice provider catalog entries (FRD-018 T3.1/T3.2).

These are pure data tests — no database, no seeding run — because the failure they guard against
is a *data* failure that produces no error at all.

**The trap.** ``TensorZeroSeeder`` inserts providers by walking the LiteLLM model catalog. A
provider with no catalog models is never reached by that loop, so it is only inserted if it also
appears in ``NO_MODEL_PROVIDERS``. Voice providers are all in that position: WaaV serves them, so
they have no TensorZero models. Omit one and the seeder runs green, ``tensorzero_providers.json``
still contains the entry, and the provider simply never appears in budadmin — with nothing in any
log to say why.
"""

import ast
import json
import pathlib

import pytest


CONSTANTS_PATH = pathlib.Path(__file__).parent.parent / "budconnect" / "seeders" / "constants.py"


def _no_model_providers() -> list:
    """Read the constant by parsing the source rather than importing it.

    ``budconnect/seeders/__init__.py`` imports every seeder, so any import reaching into that
    package pulls in the ORM and hits a pre-existing circular import. ``ast`` sidesteps it —
    the same approach ``test_openai_compatible_provider.py`` already takes for the same reason.
    """
    tree = ast.parse(CONSTANTS_PATH.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "NO_MODEL_PROVIDERS" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("NO_MODEL_PROVIDERS not found in budconnect/seeders/constants.py")


NO_MODEL_PROVIDERS = _no_model_providers()


PROVIDERS_PATH = (
    pathlib.Path(__file__).parent.parent
    / "budconnect"
    / "seeders"
    / "data"
    / "tensorzero"
    / "tensorzero_providers.json"
)

VOICE_PROVIDERS = ["deepgram", "elevenlabs", "cartesia", "waav_self_hosted"]


@pytest.fixture(scope="module")
def providers():
    return json.loads(PROVIDERS_PATH.read_text())


@pytest.mark.parametrize("provider", VOICE_PROVIDERS)
def test_voice_provider_is_in_the_catalog(providers, provider):
    assert provider in providers, f"{provider} missing from tensorzero_providers.json"


@pytest.mark.parametrize("provider", VOICE_PROVIDERS)
def test_every_no_model_provider_is_seeded(provider):
    """THE guard for this milestone's silent-failure mode.

    A voice provider present in the JSON but absent from ``NO_MODEL_PROVIDERS`` is never
    inserted, and nothing anywhere reports it.
    """
    assert provider in NO_MODEL_PROVIDERS, (
        f"{provider} is in tensorzero_providers.json but not in NO_MODEL_PROVIDERS. "
        "The seeder walks the LiteLLM catalog to find providers, and a voice provider has no "
        "catalog models, so it will never be inserted — silently. Add it to the list."
    )


def test_no_model_providers_all_exist_in_the_catalog(providers):
    """The inverse: a name in the list but not in the JSON raises ``KeyError`` mid-seed, which
    aborts the whole run rather than skipping one provider.
    """
    missing = [p for p in NO_MODEL_PROVIDERS if p not in providers]
    assert not missing, (
        f"{missing} are listed in NO_MODEL_PROVIDERS but absent from tensorzero_providers.json. "
        "The seeder indexes the dict directly, so this raises KeyError and aborts seeding entirely."
    )


@pytest.mark.parametrize("provider", VOICE_PROVIDERS)
def test_entry_has_every_field_the_seeder_reads(providers, provider):
    """``ProviderCreate`` indexes these five keys directly; a missing one is a ``KeyError``
    during seeding, not a validation message.
    """
    entry = providers[provider]
    for key in ("name", "icon", "description", "credentials", "capabilities"):
        assert key in entry, f"{provider} is missing {key!r}, which the seeder indexes directly"


@pytest.mark.parametrize("provider", VOICE_PROVIDERS)
def test_credentials_array_is_a_renderable_form(providers, provider):
    """The credentials array *is* the form budadmin renders — there is no separate schema."""
    creds = providers[provider]["credentials"]
    assert creds, f"{provider} has no credential fields; the form would render empty"

    for field in creds:
        for key in ("field", "label", "type", "required", "order"):
            assert key in field, f"{provider} credential {field.get('field')!r} is missing {key!r}"
        assert field["type"] in {"password", "url", "string", "text"}, (
            f"{provider} credential {field['field']!r} has type {field['type']!r}, which budadmin has no input for"
        )

    orders = [f["order"] for f in creds]
    assert len(set(orders)) == len(orders), f"{provider} has duplicate credential `order` values"


@pytest.mark.parametrize("provider", ["deepgram", "elevenlabs", "cartesia"])
def test_vendor_secrets_are_password_fields(providers, provider):
    """A vendor key rendered as a plain text input is shoulder-surfable and lands in browser
    autofill history.
    """
    api_key = next(f for f in providers[provider]["credentials"] if f["field"] == "api_key")
    assert api_key["type"] == "password", f"{provider}'s api_key must render masked"


def test_self_hosted_requires_a_url_but_not_a_key():
    """FRD §5.2 — a cluster deployment is reached by URL and frequently needs no credential at
    all. Requiring one would make the common case unconfigurable.
    """
    entry = json.loads(PROVIDERS_PATH.read_text())["waav_self_hosted"]
    by_field = {f["field"]: f for f in entry["credentials"]}

    assert by_field["api_base"]["required"] is True
    assert by_field["api_base"]["type"] == "url"
    assert by_field["api_key"]["required"] is False, (
        "a self-hosted Whisper on vLLM usually has no auth; requiring a key blocks the common case"
    )


def test_self_hosted_description_warns_against_the_full_path():
    """The most common misconfiguration for a base URL is pasting the full endpoint path, which
    then double-appends. `openai_compatible` warns about it; so should this.
    """
    entry = json.loads(PROVIDERS_PATH.read_text())["waav_self_hosted"]
    api_base = next(f for f in entry["credentials"] if f["field"] == "api_base")
    assert "do not include" in api_base["description"].lower()


@pytest.mark.parametrize("provider", VOICE_PROVIDERS)
def test_capabilities_are_recognised(providers, provider):
    """``ProviderCapabilityEnum`` is model | moderation | local. A value outside it is rejected
    at insert.
    """
    assert set(providers[provider]["capabilities"]) <= {"model", "moderation", "local"}
