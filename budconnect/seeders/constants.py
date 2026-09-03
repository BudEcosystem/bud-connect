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
    "openai_compatible",
    # FRD-018 voice providers.
    "deepgram",
    "elevenlabs",
    "cartesia",
    "waav_self_hosted",
    # FRD-018 M8: the two budgateway audio vendors WaaV has no native provider for. Both speak
    # the OpenAI audio API, so budapp maps them onto `openai_compatible` rather than duplicating
    # that path twice. Neither has models in the catalog, so both must be listed here.
    "fireworks",
    "together",
]
