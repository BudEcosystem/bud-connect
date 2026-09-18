"""Seeder constants that must be importable without pulling in the ORM.

Kept separate from ``tensorzero.py`` so tests (and any tooling) can assert on this data without
importing the seeder module, which reaches the SQLAlchemy models and cannot be imported
standalone.
"""

# Providers with no entry in the LiteLLM/TensorZero model catalog, which must therefore be
# inserted explicitly by the seeder.
#
# The seeder discovers providers by walking the model catalog. A provider with no models is
# never reached by that loop, so omitting it here is a **silent no-op**: the entry stays in
# ``tensorzero_providers.json``, seeding reports success, and the provider never appears in
# budadmin with nothing in any log to explain it.
#
# The voice providers (FRD-018) are all in that position — WaaV serves them, so they have no
# TensorZero models. ``tests/test_voice_providers.py`` guards the omission.
NO_MODEL_PROVIDERS = [
    "huggingface",
    "bud_sentinel",
    "openai",
    "azure_content_safety",
    # FRD-019 M3: `openai_compatible` also serves a self-hosted AUDIO deployment now. It is the
    # same server either way -- WaaV resolves `self_hosted`, `self-hosted`, `waav_self_hosted`
    # and `openai_compatible` to one implementation -- and the plane is chosen by what the
    # deployment declares, not by which entry the user clicked.
    "openai_compatible",
    # FRD-018 voice providers.
    #
    # `waav_self_hosted` was here and is RETIRED (FRD-019 M3): it was `openai_compatible`
    # described twice, and existed only so budapp could pick the audio plane from the PROVIDER.
    # Removing it from THIS list is what retires it -- `deactivate_stale_providers` drops the
    # engine-version association for anything seeded before and not seeded now, and this list is
    # the only thing that seeds a provider with no catalog models. The provider ROW stays (three
    # foreign keys reference it and none cascade), which is also why budapp keeps the source
    # mapped: deployments created before the merge must still publish.
    "deepgram",
    "elevenlabs",
    "cartesia",
    # FRD-018 M8 added `fireworks` and `together_ai` here as AUDIO providers, and FRD-019 M3
    # withdrew both. WaaV has no module for either -- no `stt/fireworks`, no `stt/together` in
    # the gateway -- so M8 re-pointed them at the self-hosted path, which implements
    # `/v1/audio/speech` and nothing on the transcription side while the catalog declared them
    # transcription-only. That is the same empty promise as the self-hosted entry itself, with
    # a vendor's name on it.
    #
    # `fireworks` is gone from the catalog entirely: it was created for that migration and has
    # no models (the Fireworks LLM provider is the separate `fireworks_ai-embedding-models`).
    # `together_ai` is NOT listed here any more because it never needed to be -- it carries 40
    # catalog models, so the seeder's model walk reaches it -- and its entry is restored to the
    # LLM provider it was before M8 rewrote it.
    # Every other vendor WaaV can dispatch. None of them has TensorZero catalog models -- WaaV
    # serves them directly -- so each one has to be named here or the seeder's catalog walk
    # never reaches it and it is skipped without a word. See tests/test_voice_providers.py.
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
