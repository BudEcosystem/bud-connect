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

#: Every provider that exists for WaaV's sake. Written out rather than derived from
#: NO_MODEL_PROVIDERS: deriving it would make `test_every_no_model_provider_is_seeded`
#: assert that a list contains itself.
VOICE_PROVIDERS = [
    "deepgram",
    "elevenlabs",
    "cartesia",
    "waav_self_hosted",
    "fireworks",
    "together_ai",
    "acapela",
    "alibaba_cloud",
    "amivoice",
    "assemblyai",
    "aws_polly",
    "aws_transcribe",
    "baidu",
    "bhashini",
    "cereproc",
    "fpt_ai",
    "gladia",
    "gnani",
    "google_speech",
    "groq",
    "huawei_cloud",
    "hume",
    "ibm_watson",
    "iflytek",
    "lmnt",
    "murf",
    "naver_clova",
    "nectec",
    "phonexia",
    "playht",
    "prosa_ai",
    "resemble",
    "revai",
    "reverie",
    "sarvam",
    "sberdevices",
    "smallest",
    "speechify",
    "speechmatics",
    "tencent",
    "tinkoff",
    "unrealspeech",
    "viettel_ai",
    "wellsaid",
    "yandex",
    "zalo_ai",
]

#: The M8 vendors WaaV has no native provider for. budapp maps both onto
#: `openai_compatible`, WaaV's self-hosted path, which has no endpoint of its own — so
#: unlike a native vendor these MUST offer an api_base field or the endpoint can never serve.
OPENAI_COMPATIBLE_VOICE_PROVIDERS = ["fireworks", "together_ai"]


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


#: Everything ``ProviderCapabilityEnum`` accepts, on BOTH sides of the wire. A value outside
#: this set is rejected at insert here, and — worse — aborts budapp's whole provider sync,
#: because it validates each incoming string inside an unguarded loop.
KNOWN_CAPABILITIES = {
    "model",
    "moderation",
    "local",
    "text_to_speech",
    "audio_transcription",
    "audio_translation",
}


@pytest.mark.parametrize("provider", VOICE_PROVIDERS)
def test_capabilities_are_recognised(providers, provider):
    """Every value must be one both catalogs know.

    The vocabulary gained the three audio capabilities when the TTS/STT split moved out of a
    hand-written map in budapp and into this catalog; before that it was model | moderation |
    local.
    """
    assert set(providers[provider]["capabilities"]) <= KNOWN_CAPABILITIES


@pytest.mark.parametrize("provider", OPENAI_COMPATIBLE_VOICE_PROVIDERS)
def test_an_openai_compatible_vendor_requires_an_api_base(providers, provider):
    """WaaV's self-hosted provider is REFUSED at construction without api_base, and budapp now
    refuses to publish without one. If the catalog offers no field for it, the operator has no
    way to supply it and the endpoint cannot be created at all — a dead end reached only after
    they have filled in a key.
    """
    fields = {c["field"]: c for c in providers[provider]["credentials"]}
    assert "api_base" in fields, (
        f"{provider} is served through openai_compatible, which has no endpoint of its own; "
        "without an api_base field the operator cannot supply one"
    )
    assert fields["api_base"]["required"] is True
    assert fields["api_base"]["type"] == "url"


@pytest.mark.parametrize("provider", OPENAI_COMPATIBLE_VOICE_PROVIDERS)
def test_an_openai_compatible_vendor_still_requires_a_key(providers, provider):
    """Unlike a self-hosted deployment behind network policy, these are public paid APIs: a
    blank key is never correct, so the field is required rather than optional.
    """
    fields = {c["field"]: c for c in providers[provider]["credentials"]}
    assert fields["api_key"]["required"] is True
    assert fields["api_key"]["type"] == "password"


@pytest.mark.parametrize("provider", OPENAI_COMPATIBLE_VOICE_PROVIDERS)
def test_the_api_base_description_warns_against_the_full_path(providers, provider):
    """Same trap as the self-hosted entry: pasting the full /audio/transcriptions URL yields
    .../audio/transcriptions/audio/transcriptions, which 404s and reads as a bad credential.
    """
    fields = {c["field"]: c for c in providers[provider]["credentials"]}
    assert "do not include" in fields["api_base"]["description"].lower()


def test_no_provider_duplicates_another_vendor():
    """Two entries for one vendor show up twice in the picker.

    `together` was added for FRD-018 M8 while `together_ai` already existed for the same
    vendor — identical name, identical icon — so Together AI rendered twice in the provider
    list, one of them with a broken image. The catalog is keyed by provider_type, so nothing
    upstream can notice that two keys describe the same company.

    Compares on the display NAME, which is what a user actually sees duplicated.
    """
    import collections
    import json
    import pathlib

    catalog = json.loads(
        (
            pathlib.Path(__file__).resolve().parents[1]
            / "budconnect/seeders/data/tensorzero/tensorzero_providers.json"
        ).read_text()
    )
    by_name = collections.defaultdict(list)
    for key, entry in catalog.items():
        by_name[entry["name"].strip().casefold()].append(key)

    dupes = {name: keys for name, keys in by_name.items() if len(keys) > 1}
    assert not dupes, f"these vendors have more than one provider entry: {dupes}"


class TestStaleProviderRetirement:
    """A provider removed from the catalog must stop being served.

    Removing `together` from tensorzero_providers.json did nothing to the running system: the
    seeder only ever upserts providers, so the row stayed, kept its engine_version_provider
    association, and Together AI went on appearing twice in the picker. Deleting it through the
    API fails too — three foreign keys point at `provider` and none cascades, so the
    association blocks the delete.

    Models already have this: `deactivate_stale_models` drops their association when they leave
    the catalog. Providers had no counterpart, which made every provider ever added permanent.

    Parsed with `ast` rather than imported: importing the seeder module hits a circular import
    through budconnect.commons. Parsing also means these assertions cannot be satisfied by a
    comment that merely mentions the name.
    """

    @staticmethod
    def _seeder_class():
        import ast
        import pathlib

        src = (pathlib.Path(__file__).resolve().parents[1] / "budconnect/seeders/tensorzero.py").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "TensorZeroSeeder":
                return node
        raise AssertionError("TensorZeroSeeder class not found")

    def _method(self, name):
        import ast

        for node in self._seeder_class().body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                return node
        return None

    def test_the_seeder_can_retire_a_provider(self):
        assert self._method("deactivate_stale_providers") is not None, (
            "the seeder cannot retire a provider; anything removed from the catalog is served "
            "forever and cannot be deleted through the API either"
        )

    def test_retirement_is_actually_called(self):
        # A method nothing calls leaves the defect exactly as it was. Looks for a real Call
        # node, so a mention in a docstring or comment cannot satisfy it.
        import ast

        seed = self._method("seed")
        assert seed is not None, "seed() not found"
        called = {n.func.attr for n in ast.walk(seed) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        assert "deactivate_stale_providers" in called, "deactivate_stale_providers exists but seed() never calls it"

    def test_it_mirrors_the_model_signature(self):
        # Same shape as deactivate_stale_models, so the two read as one pattern.
        m = self._method("deactivate_stale_providers")
        assert m is not None
        args = [a.arg for a in m.args.args]
        assert args == ["self", "engine_version_id", "stale_provider_ids"], args

    def test_it_removes_the_association_not_the_provider_row(self):
        # Deleting the provider itself is what the API already fails at: model_info and
        # guardrail_probe (RESTRICT) also point at it. Dropping the association is both
        # sufficient and safe, and this pins that choice.
        import ast

        m = self._method("deactivate_stale_providers")
        names = {n.id for n in ast.walk(m) if isinstance(n, ast.Name)}
        assert "engine_version_provider" in names, "must delete from the association table"
        assert "Provider" not in names, (
            "must NOT delete the provider row — three foreign keys reference it and none cascade"
        )


# --------------------------------------------------------------------------- #
# What each voice provider can serve
#
# The catalog is now the source of truth for the TTS/STT split, replacing a
# hand-written map inside budapp. That makes these entries load-bearing: the
# add-model wizard decides which providers to offer a modality from this field.
# --------------------------------------------------------------------------- #

#: From WaaV's registry (gateway/src/plugin/builtin/mod.rs): a vendor registered only under
#: ``ProviderMetadata::tts`` cannot transcribe, and one registered only under ``::stt``
#: cannot speak. Written out rather than derived from the catalog under test — deriving the
#: expectation from the data it checks proves nothing.
SYNTHESIS_ONLY = {
    "acapela", "aws_polly", "cereproc", "hume", "lmnt", "murf", "playht", "resemble",
    "smallest", "speechify", "unrealspeech", "wellsaid", "zalo_ai",
}
TRANSCRIPTION_ONLY = {
    "amivoice", "assemblyai", "aws_transcribe", "gladia", "groq", "phonexia", "revai",
    "sarvam", "fireworks", "together_ai",
}
AUDIO_CAPABILITIES = {"text_to_speech", "audio_transcription", "audio_translation"}


@pytest.mark.parametrize("provider", VOICE_PROVIDERS)
def test_a_voice_provider_declares_at_least_one_audio_capability(providers, provider):
    """Without this the provider is invisible in both audio modalities.

    budapp offers a provider for a modality when its capabilities array names that
    capability; a voice vendor carrying only ``model`` is a vendor nobody can select for the
    thing it exists to do.
    """
    declared = set(providers[provider]["capabilities"])
    assert declared & AUDIO_CAPABILITIES, (
        f"{provider} declares {sorted(declared)} — no audio capability, so it will not appear "
        "under Text to Speech or Speech to text"
    )


@pytest.mark.parametrize("provider", VOICE_PROVIDERS)
def test_a_voice_provider_still_declares_model(providers, provider):
    """`model` is what keeps it visible at all.

    budconnect's /model/get-compatible-models only returns providers carrying MODEL, and
    every budadmin provider fetch sends ``capabilities=model``. Replacing `model` with the
    audio values — rather than adding them — removes the vendor from the picker entirely.
    """
    assert "model" in providers[provider]["capabilities"], f"{provider} lost its `model` capability"


@pytest.mark.parametrize("provider", sorted(SYNTHESIS_ONLY))
def test_a_synthesis_only_vendor_does_not_claim_transcription(providers, provider):
    declared = set(providers[provider]["capabilities"])
    assert "text_to_speech" in declared
    assert not (declared & {"audio_transcription", "audio_translation"}), (
        f"{provider} only synthesises; claiming transcription offers it for a modality it cannot serve"
    )


@pytest.mark.parametrize("provider", sorted(TRANSCRIPTION_ONLY))
def test_a_transcription_only_vendor_does_not_claim_synthesis(providers, provider):
    declared = set(providers[provider]["capabilities"])
    assert "audio_transcription" in declared
    assert "text_to_speech" not in declared, f"{provider} cannot speak; claiming synthesis is a dead end"


def test_transcription_and_translation_travel_together(providers):
    """WaaV routes both to the same provider; no vendor implements one without the other."""
    for provider, entry in providers.items():
        declared = set(entry["capabilities"])
        assert ("audio_transcription" in declared) == ("audio_translation" in declared), (
            f"{provider} declares only one half of transcription/translation: {sorted(declared)}"
        )


#: Providers that may declare audio capabilities: the ones that exist for WaaV's sake, plus
#: the two general-purpose vendors WaaV also serves audio for natively. Anything else
#: claiming speech would be offered for a modality it cannot serve.
AUDIO_PROVIDERS = set(VOICE_PROVIDERS) | {"azure", "openai"}


def test_only_voice_providers_declare_audio_capabilities(providers):
    """A text provider claiming speech would be offered for a modality it cannot serve."""
    for provider, entry in providers.items():
        if provider in AUDIO_PROVIDERS:
            continue
        assert not (set(entry["capabilities"]) & AUDIO_CAPABILITIES), (
            f"{provider} is not a voice provider but declares audio capabilities"
        )


def test_every_declared_capability_is_one_budapp_knows(providers):
    """budapp validates each string against its own enum inside an unguarded loop.

    A value it does not know raises mid-sync: providers already upserted are committed, the
    rest stay stale, the cloud-model refresh never runs, and the Dapr activity swallows the
    error so nothing retries for a week.
    """
    for provider, entry in providers.items():
        unknown = set(entry["capabilities"]) - KNOWN_CAPABILITIES
        assert not unknown, f"{provider} declares {sorted(unknown)}, which budapp's ProviderCapabilityEnum rejects"
