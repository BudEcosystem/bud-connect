"""Voice provider catalog entries (FRD-018 T3.1/T3.2).

These are pure data tests — no database, no seeding run — because the failure they guard against
is a *data* failure that produces no error at all.

**The trap.** ``TensorZeroSeeder`` inserts providers by walking the LiteLLM model catalog. A
provider with no catalog models is never reached by that loop, so it is only inserted if it also
appears in ``NO_MODEL_PROVIDERS``. Most voice providers are in that position: WaaV serves them, so
they have no TensorZero models. Omit one and the seeder runs green, ``tensorzero_providers.json``
still contains the entry, and the provider simply never appears in budadmin — with nothing in any
log to say why.

Five of them — ``deepgram``, ``elevenlabs``, ``assemblyai``, ``aws_polly`` and ``groq`` — gained
catalog models in BudModelCatalog-SDK #5 and are reached by the model walk today. They stay in
``NO_MODEL_PROVIDERS`` regardless, so these tests still require them there: leaving the catalog is
as silent as never being in it. See ``budconnect/seeders/constants.py``.
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
#:
#: `waav_self_hosted` is NOT here: FRD-019 M3 retired it into `openai_compatible`, which is a
#: general-purpose provider rather than one that exists for WaaV's sake. Its retirement is
#: asserted by the TC-MERGE tests below, and the audio shape it used to carry is asserted of
#: the merged entry — so dropping it from this list loses no coverage.
VOICE_PROVIDERS = [
    "deepgram",
    "elevenlabs",
    "cartesia",
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
    "murf",
    "naver_clova",
    "nectec",
    "phonexia",
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

#: FRD-018 M8 added `fireworks` and `together_ai` as audio providers re-pointed onto
#: `openai_compatible`, WaaV's self-hosted path. FRD-019 M3 WITHDREW both: WaaV has no module
#: for either vendor, and the path they were aimed at implements `/v1/audio/speech` and nothing
#: on the transcription side — the one direction the catalog declared them for.
#:
#: `fireworks` was created for that migration and is gone from the catalog; `together_ai`
#: pre-dates it and is restored to the LLM provider it was.
WITHDRAWN_AUDIO_VENDORS = ["fireworks", "together_ai"]


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
        # `textarea` is what `vertex_ai-*` has always used for a pasted service-account key, and
        # budapp's credential validator accepts it as a string. google_speech's key is the same
        # kind of value, so it takes the same type rather than inventing a new one.
        assert field["type"] in {"password", "url", "string", "text", "textarea"}, (
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


# --------------------------------------------------------------------------- #
# Vendors whose whole credential is collected by the form (voice contract, 2026-09-26)
#
# `aws_polly`, `aws_transcribe` and `google_speech` used to ask for a single "API key" and say
# the rest came from WaaV's own gateway configuration. Neither vendor HAS an API key: AWS signs
# every request with an access key pair (SigV4), and Google Speech authenticates with a service
# account. The one field the form collected could not authenticate anything, and the "operator
# configures the rest" escape hatch meant every tenant ran as the gateway's cloud identity.
# budapp now carries the real credential to WaaV per endpoint, so the form has to ask for it.
# --------------------------------------------------------------------------- #

AWS_VOICE_PROVIDERS = ["aws_polly", "aws_transcribe"]

#: The names `bedrock` uses, in bedrock's order. budapp's `_pack_aws_credentials` reads
#: `aws_access_key_id` / `aws_secret_access_key` / `aws_session_token` by exactly these names,
#: and the region travels as `provider_params.region`. A new spelling here would be a field
#: budapp never reads -- the credential would save and the endpoint would refuse to publish.
AWS_VOICE_FIELDS = ["aws_access_key_id", "aws_secret_access_key", "aws_session_token", "aws_region_name"]

#: Of those, the ones that are secrets and must render masked.
AWS_SECRET_FIELDS = {"aws_secret_access_key", "aws_session_token"}

#: Only the session token is optional: it exists for temporary (STS) credentials alone.
AWS_OPTIONAL_FIELDS = {"aws_session_token"}

#: Wording that sent users to an operator for the part of the credential the form did not
#: collect. Matched case-insensitively.
OWN_CONFIG_CLAIM = "from its own gateway configuration"

#: Voice vendors whose credential form still carries that claim. A RATCHET, not an endorsement:
#: each of these asks for one key where the vendor needs two or more, and each should get the
#: treatment the three above got. Remove a vendor from this list when its form is fixed; never add
#: one.
PENDING_OWN_CONFIG_VENDORS = {
    "baidu",
    "bhashini",
    "gnani",
    "huawei_cloud",
    "ibm_watson",
    "iflytek",
    "naver_clova",
    "reverie",
    "tencent",
    "tinkoff",
}


def _creds_by_field(providers, provider):
    return {f["field"]: f for f in providers[provider]["credentials"]}


@pytest.mark.parametrize("provider", AWS_VOICE_PROVIDERS)
def test_aws_voice_provider_collects_exactly_the_four_bedrock_named_fields(providers, provider):
    """Access key pair, optional session token, region -- and no `api_key`."""
    fields = [f["field"] for f in sorted(providers[provider]["credentials"], key=lambda f: f["order"])]
    assert fields == AWS_VOICE_FIELDS, f"{provider} collects {fields}"
    assert "api_key" not in fields, (
        f"{provider} asks for an `api_key`; AWS has no such thing, and budapp would publish it as the "
        "credential WaaV signs with"
    )


@pytest.mark.parametrize("provider", AWS_VOICE_PROVIDERS)
def test_aws_voice_fields_match_bedrock(providers, provider):
    """Same name, label, type and required-ness as bedrock.

    budadmin and budapp then treat the two AWS forms identically. Descriptions may differ -- they
    name the service being called.
    """
    bedrock = _creds_by_field(providers, "bedrock")
    for name, field in _creds_by_field(providers, provider).items():
        assert name in bedrock, f"{provider}.{name} is not a field bedrock has"
        for key in ("label", "type", "required", "order"):
            assert field[key] == bedrock[name][key], (
                f"{provider}.{name} {key}={field[key]!r}, bedrock has {bedrock[name][key]!r}"
            )


@pytest.mark.parametrize("provider", AWS_VOICE_PROVIDERS)
def test_aws_voice_secrets_are_password_fields_and_only_the_token_is_optional(providers, provider):
    """Secrets render masked; everything but the STS session token is required."""
    by_field = _creds_by_field(providers, provider)
    for name in AWS_VOICE_FIELDS:
        expected_type = "password" if name in AWS_SECRET_FIELDS else "text"
        assert by_field[name]["type"] == expected_type, f"{provider}.{name} must be {expected_type}"
        assert by_field[name]["required"] is (name not in AWS_OPTIONAL_FIELDS), (
            f"{provider}.{name} required={by_field[name]['required']}"
        )


def test_google_speech_asks_for_a_service_account_key(providers):
    """The whole service-account JSON, in the field budapp publishes as the credential."""
    by_field = _creds_by_field(providers, "google_speech")
    fields = [f["field"] for f in sorted(providers["google_speech"]["credentials"], key=lambda f: f["order"])]
    assert fields == ["api_key", "project_id", "location"], fields

    key = by_field["api_key"]
    # Still `api_key`: it is the field budapp encrypts and publishes as the endpoint's credential.
    assert key["type"] == "textarea", "a service-account key is a multi-line JSON document"
    assert key["required"] is True
    assert key["label"] == "Service account key (JSON)"
    assert "service_account" in key["description"], "the form should say which kind of JSON it wants"


def test_google_speech_project_and_location_are_optional_text(providers):
    """Both have working defaults: the key names its own project, and WaaV defaults `global`."""
    by_field = _creds_by_field(providers, "google_speech")
    for name in ("project_id", "location"):
        assert by_field[name]["type"] == "text", f"google_speech.{name} is not a secret"
        assert by_field[name]["required"] is False, f"google_speech.{name} must stay optional"
    # chirp_3 is served from the `us` and `eu` multi-regions only, so an empty location fails it;
    # the form is the only place a user learns that before the first request does.
    assert "chirp_3" in by_field["location"]["description"]


@pytest.mark.parametrize("provider", AWS_VOICE_PROVIDERS + ["google_speech"])
def test_a_fully_collected_credential_does_not_defer_to_the_operator(providers, provider):
    """The form collects the whole credential now, so nothing may say otherwise."""
    for field in providers[provider]["credentials"]:
        description = field.get("description", "").lower()
        assert OWN_CONFIG_CLAIM not in description, (
            f"{provider}.{field['field']} still says WaaV reads the rest of the credential from its own "
            "configuration; the form now collects all of it"
        )
        assert "check with your operator" not in description


def test_no_new_vendor_defers_its_credential_to_the_operator(providers):
    """The ratchet on PENDING_OWN_CONFIG_VENDORS: the list may shrink, never grow."""
    claiming = {
        provider
        for provider, entry in providers.items()
        if any(OWN_CONFIG_CLAIM in f.get("description", "").lower() for f in entry["credentials"])
    }
    unexpected = claiming - PENDING_OWN_CONFIG_VENDORS
    assert not unexpected, (
        f"{sorted(unexpected)} tell the user WaaV reads part of the credential from its own gateway "
        "configuration. Collect the whole credential in the form instead."
    )


def test_every_catalog_entry_builds_the_seeders_provider_schema(providers):
    """Build each entry exactly as `TensorZeroSeeder.seed` does, through the same schema.

    The per-key checks above cannot see a value `ProviderCreate` rejects -- an unknown capability,
    a credentials list that is not a list of objects -- and the seeder raises on the first one,
    aborting the run for every provider after it.
    """
    from budconnect.model.schemas import ProviderCreate

    for provider_type, entry in providers.items():
        ProviderCreate(
            name=entry["name"],
            provider_type=provider_type,
            icon=entry["icon"],
            description=entry["description"],
            credentials=entry["credentials"],
            capabilities=entry["capabilities"],
        )


def test_a_reseed_rewrites_an_existing_providers_credentials(providers):
    """Why changing a credential form needs no migration.

    The seeder upserts providers through `ProviderCRUD.upsert` on `provider_type`, and the SET
    clause carries every column it inserts -- `credentials` included -- so the next startup seed or
    24h `/cron-tensorzero-sync` replaces the stored form. Drives the real method with a session
    that only records the statement, then compiles it for postgres; no database. If the upsert ever
    narrows its SET clause, a changed form would reach new installs only.
    """
    from unittest.mock import MagicMock
    from uuid import uuid4

    from sqlalchemy.dialects import postgresql

    import budconnect.commons  # noqa: F401  -- must precede model.crud (circular import)
    from budconnect.model.crud import ProviderCRUD
    from budconnect.model.schemas import ProviderCreate

    entry = providers["aws_polly"]
    row = ProviderCreate(
        name=entry["name"],
        provider_type="aws_polly",
        icon=entry["icon"],
        description=entry["description"],
        credentials=entry["credentials"],
        capabilities=entry["capabilities"],
    ).model_dump()

    session = MagicMock()
    session.execute.return_value.first.return_value = (uuid4(),)
    ProviderCRUD().upsert(data=row, conflict_target=["provider_type"], session=session)

    stmt = session.execute.call_args.args[0]
    on_conflict = str(stmt.compile(dialect=postgresql.dialect())).split("ON CONFLICT", 1)[1]
    assert "credentials =" in on_conflict, "a re-seed would leave an existing provider's old credential form"


# --------------------------------------------------------------------------- #
# FRD-019 M3 — the audio modalities offer VENDORS, and nothing else
#
# `waav_self_hosted` ("Self-hosted audio model") let a user point Bud at an audio server they
# run. It is WITHDRAWN, and deliberately not merged into `openai_compatible`: there is no
# standard audio API to point such an entry at. One wire format is near-universal for chat,
# which is what makes `openai_compatible` an honest promise there; audio has no equivalent.
# WaaV's self-hosted provider implements OpenAI `POST /v1/audio/speech` and has no
# transcription side at all (`src/core/tts/self_hosted.rs` exists; there is no
# `src/core/stt/self_hosted.rs` in the deployed binary), so an entry offering all three audio
# capabilities would accept a URL, publish cleanly, and fail at REQUEST time for two of them.
# --------------------------------------------------------------------------- #

#: The withdrawn "bring your own audio server" entry. Gone from the catalog; budapp keeps the
#: source mapped and its credential form so a deployment created before the withdrawal still
#: publishes, and `proprietary_credential_type_enum` keeps the label forever because PostgreSQL
#: cannot drop one.
RETIRED_SELF_HOSTED = "waav_self_hosted"

#: The general-purpose chat entry it must NOT be folded into.
CHAT_SELF_HOSTED = "openai_compatible"


def test_the_migration_vendors_claim_no_audio(providers):
    """FRD-019 M3, the other half of the withdrawal.

    `fireworks` and `together_ai` were never vendors WaaV serves: M8 aimed both at the
    self-hosted path, which is the entry this spec withdrew. `fireworks` existed only for that
    migration and is gone; `together_ai` is a real LLM provider whose entry M8 rewrote, so it
    stays — as the LLM provider it was, with no audio capability and no audio api_base field.
    """
    assert "fireworks" not in providers, (
        "the `fireworks` entry was created for the audio migration; the Fireworks LLM provider "
        "is `fireworks_ai-embedding-models` and is untouched"
    )

    together = providers["together_ai"]
    assert set(together["capabilities"]) == {"model"}
    assert [c["field"] for c in together["credentials"]] == ["api_key"], (
        "M8 added a required audio api_base to a chat provider; withdrawing the audio job must "
        "take that field with it, or every Together deployment demands a URL it does not need"
    )


def test_the_chat_self_hosted_entry_claims_no_audio(providers):
    """The withdrawal is only real if the audio capabilities do not reappear next door.

    `openai_compatible` is the obvious place to put them — same credential shape, same icon,
    and WaaV resolves both names to one implementation. That implementation speaks OpenAI
    `/v1/audio/speech` and nothing on the transcription side, so declaring audio here offers
    modalities the deployment cannot serve.
    """
    declared = set(providers[CHAT_SELF_HOSTED]["capabilities"])

    assert declared == {"model"}, (
        f"{CHAT_SELF_HOSTED} declares {sorted(declared)}; the audio modalities offer vendors "
        "Bud can dispatch, and a user-supplied audio server is not one of them"
    )


def test_tc_merge_2_the_retired_entry_is_gone_from_the_catalog(providers):
    """TC-MERGE-2, half one. A catalog entry nothing seeds is dead data.

    Removing it from ``NO_MODEL_PROVIDERS`` alone would retire the provider (the seeder's
    stale set is what it did NOT seed this run), but leave a description, an icon and a
    credential form in the JSON for a provider that can never be selected again — the next
    reader has no way to tell that from an entry someone forgot to wire up.
    """
    assert RETIRED_SELF_HOSTED not in providers


def test_tc_merge_2_the_retired_entry_is_gone_from_no_model_providers():
    """TC-MERGE-2, half two, and the half that actually retires it.

    ``deactivate_stale_providers`` computes the stale set as "seeded before, not seeded now",
    and the only thing that seeds a provider with no catalog models is this list. Leaving the
    name here while the JSON entry is gone is worse than doing nothing: the seeder indexes the
    dict directly, so it raises ``KeyError`` and aborts the entire run.
    """
    assert RETIRED_SELF_HOSTED not in NO_MODEL_PROVIDERS


def test_the_chat_self_hosted_entry_keeps_its_own_credential_shape(providers):
    """Withdrawing the audio entry must not disturb the chat one it sits next to.

    `openai_compatible` is the most-used provider in the catalog: a URL the user chooses, and
    a key that is optional because a server behind network policy often has none. Requiring a
    key would make the common case unconfigurable.
    """
    by_field = {f["field"]: f for f in providers[CHAT_SELF_HOSTED]["credentials"]}

    assert by_field["api_base"]["required"] is True
    assert by_field["api_base"]["type"] == "url"
    assert by_field["api_key"]["required"] is False
    assert "do not include" in by_field["api_base"]["description"].lower(), (
        "pasting the full endpoint path double-appends and 404s in a way that reads as a bad credential"
    )


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


# The three tests that lived here pinned the credential shape of an audio vendor served
# through `openai_compatible` — api_base required, api_key required, the "do not paste the full
# path" warning. FRD-019 M3 withdrew the only two vendors in that position, so they had no
# subject left; an empty `parametrize` would have kept them in the file as three permanent
# skips, which reads as coverage and is not. What replaced them is
# `test_the_migration_vendors_claim_no_audio`, which asserts the state that made them moot.


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
    "acapela",
    "aws_polly",
    "cereproc",
    # WaaV serves Huawei for text-to-speech only; it has no Huawei STT driver.
    "huawei_cloud",
    "hume",
    "murf",
    "resemble",
    "smallest",
    "speechify",
    "unrealspeech",
    "wellsaid",
    "zalo_ai",
}
TRANSCRIPTION_ONLY = {
    "amivoice",
    "assemblyai",
    "aws_transcribe",
    "gladia",
    "groq",
    "phonexia",
    "revai",
    "sarvam",
    # `fireworks` and `together_ai` were here. FRD-019 M3 withdrew both: WaaV has no module for
    # either, so they were only ever the self-hosted path under a vendor's name.
}
#: Vendors withdrawn because the COMPANY is gone, not because WaaV stopped dispatching them.
#: Checked 2026-09-22:
#:   * `lmnt`   -- docs.lmnt.com and app.lmnt.com serve "LMNT has shut down"; api.lmnt.com no
#:                 longer completes a TLS handshake.
#:   * `playht` -- Meta acquihired the team in July 2025, the API went offline that month and
#:                 the service terminated 2025-12-31. play.ht has no DNS answer at all.
#: Kept as a named list so a future catalog edit cannot quietly reinstate either one.
DEAD_VENDORS = ("lmnt", "playht")
#: Vendors that still exist, and that WaaV still dispatches, but that Bud no longer offers.
#:   * `prosa_ai` -- withdrawn on request, 2026-09-25. WaaV still serves it, which is why it stays
#:                   in the WAAV_* snapshots below.
WITHDRAWN_VOICE_VENDORS = ("prosa_ai",)

AUDIO_CAPABILITIES = {"text_to_speech", "audio_transcription", "audio_translation"}


@pytest.mark.parametrize("provider", DEAD_VENDORS + WITHDRAWN_VOICE_VENDORS)
def test_a_dead_vendor_is_gone_from_the_catalog(providers, provider):
    """An entry for a vendor that no longer exists is a credential form no key can reach.

    The user fills it in, the deployment is created, and the failure surfaces as a runtime
    error against a host that does not resolve.
    """
    assert provider not in providers, (
        f"{provider} is back in tensorzero_providers.json; the vendor is gone -- an entry for "
        "it offers a modality nothing can serve"
    )


@pytest.mark.parametrize("provider", DEAD_VENDORS + WITHDRAWN_VOICE_VENDORS)
def test_a_dead_vendor_is_gone_from_no_model_providers(provider):
    """The half that actually retires it.

    ``deactivate_stale_providers`` computes the stale set as "seeded before, not seeded now",
    and this list is the only thing that seeds a provider with no catalog models. Leaving the
    name here while the JSON entry is gone is worse than doing nothing: the seeder indexes the
    dict directly, so it would raise ``KeyError`` and abort the whole run.
    """
    assert provider not in NO_MODEL_PROVIDERS


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


# --------------------------------------------------------------------------------- #
# claims pinned to what WaaV can actually do
# --------------------------------------------------------------------------------- #
#
# These are snapshots of WaaV's gateway at 77ff9c6 (2026-09-21), which is the component that
# serves every one of these capabilities. A claim here that WaaV cannot honour is not merely
# decorative: budapp offers the route, the user calls it, and the failure is at best an error
# and at worst a plausible wrong answer. Update a set when WaaV changes, not to make a claim
# pass.

#: `TranslationConfig::warnings_for` in gateway/src/core/stt/standard.rs. Five of WaaV's 31
#: STT vendors translate: speechmatics and gladia to arbitrary targets, assemblyai on batch
#: only, openai and groq to English only. Every other vendor falls into its `other =>` arm:
#: "translation not supported ... transcript only".
WAAV_TRANSLATES = frozenset({"speechmatics", "gladia", "assemblyai", "openai", "groq"})

#: STT_FEATURE_SUPPORT in gateway/src/core/capabilities.rs, the table behind
#: GET /capabilities/features, with WaaV's names mapped to bud-connect's (hyphens to
#: underscores, `google` to `google_speech`).
WAAV_TRANSCRIBES = frozenset(
    {
        "alibaba_cloud",
        "amivoice",
        "assemblyai",
        "aws_transcribe",
        "azure",
        "baidu",
        "bhashini",
        "cartesia",
        "deepgram",
        "elevenlabs",
        "fpt_ai",
        "gladia",
        "gnani",
        "google_speech",
        "groq",
        "ibm_watson",
        "iflytek",
        "naver_clova",
        "nectec",
        "openai",
        "phonexia",
        "prosa_ai",
        "revai",
        "reverie",
        "sarvam",
        "sberdevices",
        "speechmatics",
        "tencent",
        "tinkoff",
        "viettel_ai",
        "yandex",
    }
)

#: TTS_FEATURE_SUPPORT in the same file, mapped the same way.
WAAV_SYNTHESISES = frozenset(
    {
        "acapela",
        "alibaba_cloud",
        "aws_polly",
        "azure",
        "baidu",
        "bhashini",
        "cartesia",
        "cereproc",
        "deepgram",
        "elevenlabs",
        "fpt_ai",
        "gnani",
        "google_speech",
        "huawei_cloud",
        "hume",
        "ibm_watson",
        "iflytek",
        "lmnt",
        "murf",
        "naver_clova",
        "nectec",
        "openai",
        "playht",
        "prosa_ai",
        "resemble",
        "reverie",
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
    }
)


def test_only_vendors_waav_can_translate_through_declare_translation(providers):
    """Replaces "transcription and translation travel together", whose premise was false.

    That test asserted "no vendor implements one without the other" and so forced
    `audio_translation` onto all 32 transcription vendors. 27 of them cannot translate. WaaV
    passes a translation request through to the vendor rather than translating itself, and on
    a vendor that cannot, the response is a transcript in the SOURCE language -- which until
    recently was byte-identical to a successful translation, and is now distinguished only by
    an advisory. So the claim steered users to a route returning plausible wrong output.
    """
    for provider, entry in providers.items():
        declares = "audio_translation" in entry["capabilities"]
        assert declares == (provider in WAAV_TRANSLATES), (
            f"{provider} {'declares' if declares else 'omits'} audio_translation, but WaaV "
            f"{'cannot' if declares else 'can'} translate through it"
        )


def test_every_transcription_claim_is_one_waav_can_serve(providers):
    """huawei_cloud claimed transcription; WaaV has no Huawei STT driver."""
    for provider, entry in providers.items():
        if "audio_transcription" in entry["capabilities"]:
            assert provider in WAAV_TRANSCRIBES, f"{provider} claims transcription WaaV cannot serve"


def test_every_synthesis_claim_is_one_waav_can_serve(providers):
    """None fails today; kept so a new vendor cannot claim synthesis WaaV has no driver for."""
    for provider, entry in providers.items():
        if "text_to_speech" in entry["capabilities"]:
            assert provider in WAAV_SYNTHESISES, f"{provider} claims synthesis WaaV cannot serve"


#: Providers that may declare audio capabilities: the ones that exist for WaaV's sake, plus
#: the two general-purpose vendors WaaV also serves audio for through its native providers of
#: the same name. `openai_compatible` is deliberately NOT here — a user-supplied audio server
#: is not a vendor Bud can dispatch (FRD-019 M3). Anything else claiming speech would be
#: offered for a modality it cannot serve.
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
    """Budapp validates each string against its own enum inside an unguarded loop.

    A value it does not know raises mid-sync: providers already upserted are committed, the
    rest stay stale, the cloud-model refresh never runs, and the Dapr activity swallows the
    error so nothing retries for a week.
    """
    for provider, entry in providers.items():
        unknown = set(entry["capabilities"]) - KNOWN_CAPABILITIES
        assert not unknown, f"{provider} declares {sorted(unknown)}, which budapp's ProviderCapabilityEnum rejects"
