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
# Most voice providers (FRD-018) are in that position — WaaV serves them, so they have no
# TensorZero models. Five are no longer: see the note above the vendor block below.
# ``tests/test_voice_providers.py`` guards the omission.
NO_MODEL_PROVIDERS = [
    "huggingface",
    "bud_sentinel",
    "openai",
    "azure_content_safety",
    # `openai_compatible` is whatever server the user points Bud at, so it has no catalog models
    # of its own and has to be named here.
    #
    # It serves the CHAT plane only. FRD-019 M3 proposed folding the self-hosted audio entry into
    # it and then withdrew that: one wire format is near-universal for chat, which is what makes
    # this entry an honest promise there, and audio has no equivalent.
    # `test_the_chat_self_hosted_entry_claims_no_audio` holds it to that.
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
    # `together_ai` is NOT listed here any more because it never needed to be -- it carries
    # catalog models, so the seeder's model walk reaches it -- and its entry is restored to the
    # LLM provider it was before M8 rewrote it.
    # Every other vendor WaaV can dispatch. Most have no TensorZero catalog models -- WaaV serves
    # them directly -- so each one has to be named here or the seeder's catalog walk never reaches
    # it and it is skipped without a word. See tests/test_voice_providers.py.
    #
    # Five are exceptions as of BudModelCatalog-SDK #5 (2026-09-21), which added them to the
    # catalog: `deepgram`, `elevenlabs` (listed above) and `assemblyai`, `aws_polly`, `groq`
    # (below). The model walk now reaches those five, so their entries here are redundant -- the
    # same harmless double-upsert `openai` has always had, since upsert keys on `provider_type`.
    #
    # They stay listed on purpose. This list is the only thing that keeps a provider seeded if it
    # leaves the catalog again, and leaving is as silent as never arriving:
    # `deactivate_stale_providers` would drop the engine-version association and the vendor would
    # vanish from budadmin with nothing in any log. Do not prune an entry just because the catalog
    # covers it today.
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
    # `lmnt` and `playht` were here and are WITHDRAWN: both vendors are gone, not merely
    # unreachable. LMNT's docs and app both serve "LMNT has shut down" and api.lmnt.com no
    # longer completes a TLS handshake. Play.ht was acquihired by Meta in July 2025, its API
    # went offline that month, the service terminated on 2025-12-31, and play.ht does not
    # resolve at all -- 1.1.1.1 has no answer for it.
    #
    # Offering either is the same empty promise the self-hosted entry was withdrawn for: a
    # credential form for a vendor no key can reach. Removing the name from THIS list is what
    # retires it; the entry is deleted from tensorzero_providers.json in the same change so no
    # description, icon or credential form is left behind for a provider that can never be
    # selected again. See `test_a_dead_vendor_is_gone_from_the_catalog`.
    "murf",
    "naver_clova",
    "nectec",
    "phonexia",
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
