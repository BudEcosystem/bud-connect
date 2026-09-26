"""The ``azure`` provider must only collect credential fields the runtime can actually use.

Dependency free, like its ``openai_compatible`` neighbour: it reads the seed JSON only.

Background -- this is a regression pin for a live outage, not a style rule. The catalog
declared ``api_version`` as a REQUIRED azure credential field, so every Azure OpenAI
deployment published one to budgateway. budgateway's ``UninitializedProviderConfig::Azure``
(``tensorzero-internal/src/model.rs``) declares exactly
``deployment_id`` / ``endpoint`` / ``api_key_location`` and the enum is
``#[serde(deny_unknown_fields)]``, so the extra key made the WHOLE ``model_table`` entry fail
to deserialise. The gateway logged ``Failed to parse model '<id>' from redis``, dropped the
model, and answered every request with
``Invalid model name: Model name '<id>' not found in model table`` -- while budapp still
reported the endpoint RUNNING.

Why these fields cannot come back:

``api_version``
    Versions the Azure REST *contract*, not the model, and is identical on every Azure
    resource -- a property of the gateway's integration, not of a customer's deployment.
    budgateway supplies it itself (hardcoded ``api-version=2024-10-21``, the last dated GA;
    Azure's successor is the undated ``/openai/v1/`` route). Asking a user for it can only
    produce a value that is ignored, or fatal.

``azure_ad_token`` / ``tenant_id`` / ``client_id`` / ``client_secret``
    budgateway's Azure provider only ever sends an ``api-key`` header and has no Microsoft
    Entra path at all, so these could not authenticate anything even if they parsed. Offering
    them promises an auth mode the runtime does not implement.

If budgateway later grows support for any of them, delete it from ``RETIRED_FIELDS`` here AND
emit it from ``budapp``'s ``_create_provider_config`` in the same release -- not before.

``deployment_id`` is the one addition, and it is safe for the opposite reason: budgateway's
Azure variant DECLARES it, and ``_create_provider_config`` already copies a credential's
``deployment_id`` over its default (the model name). It is optional -- most Azure OpenAI
deployments are named after the model -- and the voice contract (2026-09-26) reuses it for WaaV's
``azure_openai`` vendor, where it names the deployment in the ``/openai/deployments/{id}`` path.
"""

import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
PROVIDERS_JSON_PATH = REPO_ROOT / "budconnect" / "seeders" / "data" / "tensorzero" / "tensorzero_providers.json"

PROVIDER_KEY = "azure"

# Everything budgateway's Azure variant declares, expressed as credential fields.
# `api_key_location` is not collected -- budapp derives it from the endpoint id.
SUPPORTED_FIELDS = {"api_base", "api_key", "deployment_id"}

# Without these the deployment cannot authenticate or route.
REQUIRED_FIELDS = {"api_base", "api_key"}

# Defaults to the model name in budapp, so requiring it would demand a value that is
# usually a copy of one the user has already chosen.
OPTIONAL_FIELDS = SUPPORTED_FIELDS - REQUIRED_FIELDS

RETIRED_FIELDS = {"api_version", "azure_ad_token", "tenant_id", "client_id", "client_secret"}


def _azure_credentials():
    with PROVIDERS_JSON_PATH.open() as handle:
        providers = json.load(handle)
    assert PROVIDER_KEY in providers, f"{PROVIDER_KEY!r} missing from {PROVIDERS_JSON_PATH}"
    return providers[PROVIDER_KEY]["credentials"]


def test_azure_collects_only_fields_budgateway_can_consume():
    fields = {field["field"] for field in _azure_credentials()}
    assert fields == SUPPORTED_FIELDS, (
        "the azure provider must collect exactly the credential fields budgateway can use. "
        f"got={sorted(fields)}"
    )


@pytest.mark.parametrize("retired", sorted(RETIRED_FIELDS))
def test_retired_azure_field_is_not_reintroduced(retired):
    """Each one on its own is enough to drop every Azure model, so each is pinned on its own."""
    fields = {field["field"] for field in _azure_credentials()}
    assert retired not in fields, (
        f"{retired!r} is back in the azure credential schema. budgateway's Azure variant is "
        "#[serde(deny_unknown_fields)], so budapp publishing it makes the whole model_table "
        "entry fail to parse and every Azure deployment 400s 'not found in model table'. "
        "See this module's docstring."
    )


def test_both_surviving_azure_fields_are_still_required():
    """Neither survivor is optional: without them the deployment cannot authenticate or route."""
    by_name = {field["field"]: field for field in _azure_credentials()}
    for name in sorted(REQUIRED_FIELDS):
        assert by_name[name]["required"] is True, f"azure {name!r} must stay required"


def test_azure_deployment_id_is_an_optional_text_field():
    """Required would break every existing Azure credential, which was stored without it.

    budapp validates a credential against this schema on every write, so a newly required field
    turns each saved Azure credential into one that cannot be edited without inventing a value.
    """
    by_name = {field["field"]: field for field in _azure_credentials()}
    assert {"deployment_id"} == OPTIONAL_FIELDS
    deployment_id = by_name["deployment_id"]
    assert deployment_id["required"] is False
    assert deployment_id["type"] == "text", "a deployment name is not a secret; masking it only hides typos"


def test_azure_credential_order_has_no_gaps_after_the_removals():
    """Removing fields renumbered the rest; the UI renders by `order`, so it must stay dense."""
    orders = sorted(field["order"] for field in _azure_credentials())
    assert orders == list(range(1, len(orders) + 1)), f"azure credential `order` is not dense: {orders}"
