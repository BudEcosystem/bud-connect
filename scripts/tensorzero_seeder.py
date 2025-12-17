import json
import logging
import os

import requests


# Set logging level
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Get parent directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Source URL (same as litellm_seeder.py)
LITELLM_GITHUB_URL = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"

# Paths
TZ_PROVIDERS_PATH = os.path.join(root_dir, "budconnect", "seeders", "data", "tensorzero", "tensorzero_providers.json")
OUTPUT_PATH = os.path.join(root_dir, "budconnect", "seeders", "data", "tensorzero", "tensorzero_v_0_1_0.json")

# Provider mapping (LiteLLM provider → TensorZero provider)
PROVIDER_MAP = {
    "anthropic": "anthropic",
    "azure": "azure",
    "bedrock": "bedrock",
    "bedrock_converse": "bedrock",
    "deepseek": "deepseek",
    "fireworks_ai": "fireworks_ai-embedding-models",
    "fireworks_ai-embedding-models": "fireworks_ai-embedding-models",
    "gemini": "gemini",
    "hyperbolic": "hyperbolicai",
    "mistral": "mistral",
    "openai": "openai",
    "sagemaker": "sagemaker",
    "together_ai": "together_ai",
    "vertex_ai-anthropic_models": "vertex_ai-anthropic_models",
    "vertex_ai-language-models": "vertex_ai-gemini-models",
    "xai": "xai",
}

# License mapping (TensorZero provider → license_id)
# These map to license keys in budconnect/seeders/data/licenses.json
PROVIDER_LICENSE_MAP = {
    "anthropic": "Anthropic",
    "deepseek": "deepseek-custom",
    "gemini": "Google",
    "mistral": "mistral ai",
    "openai": "openai-api",
    "vertex_ai-anthropic_models": "Anthropic",
    "vertex_ai-gemini-models": "Google",
    "xai": "xAI",
}


def fetch_litellm_model_list(source_url: str) -> dict:
    """Fetch the list of models from the GitHub URL.

    Args:
        source_url: The URL of the GitHub repo

    Returns:
        The dictionary of models

    Raises:
        Exception: If there is an error fetching or parsing the model data
    """
    try:
        logger.debug("Fetching model list from GitHub")
        response = requests.get(source_url)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise Exception("Response data is not a valid JSON object")
        return data
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        logger.error("Error getting model list from GitHub: %s", e)
        raise Exception("Error getting model list from GitHub") from e
    except json.JSONDecodeError as e:
        logger.error("Invalid model list JSON from GitHub: %s", e)
        raise Exception("Invalid model list JSON from GitHub") from e
    except Exception as e:
        logger.error("Error getting model list from GitHub: %s", e)
        raise Exception("Error getting model list from GitHub") from e


def load_tensorzero_providers(providers_path: str) -> set:
    """Load TensorZero providers from the providers JSON file.

    Args:
        providers_path: Path to the tensorzero_providers.json file

    Returns:
        Set of allowed TensorZero provider keys
    """
    with open(providers_path, "r") as f:
        providers_data = json.load(f)
    return set(providers_data.keys())


def transform_model(original_key: str, model_data: dict, tz_provider: str) -> dict:
    """Transform a LiteLLM model entry to TensorZero format.

    Args:
        original_key: The original model key from LiteLLM
        model_data: The model data dictionary
        tz_provider: The mapped TensorZero provider

    Returns:
        Transformed model data dictionary
    """
    # Copy all fields from original
    transformed = dict(model_data)

    # Update litellm_provider to TensorZero provider name
    transformed["litellm_provider"] = tz_provider

    # Add metadata with original key
    transformed["metadata"] = {"original_key": original_key}

    # Add license_id if applicable
    if tz_provider in PROVIDER_LICENSE_MAP:
        transformed["license_id"] = PROVIDER_LICENSE_MAP[tz_provider]

    return transformed


def main():
    """Execute the script to fetch LiteLLM data and transform to TensorZero format."""
    try:
        # Fetch model data from GitHub
        logger.info("Fetching model data from GitHub...")
        litellm_data = fetch_litellm_model_list(LITELLM_GITHUB_URL)

        # Remove sample_spec if present
        if "sample_spec" in litellm_data:
            litellm_data.pop("sample_spec")

        logger.info("Fetched %d models from GitHub", len(litellm_data))

        # Load TensorZero providers for validation
        tz_providers = load_tensorzero_providers(TZ_PROVIDERS_PATH)
        logger.debug("Loaded %d TensorZero providers", len(tz_providers))

        # Transform models
        tensorzero_data = {}
        skipped_count = 0
        provider_counts = {}

        for original_key, model_data in litellm_data.items():
            litellm_provider = model_data.get("litellm_provider")

            if not litellm_provider:
                skipped_count += 1
                continue

            # Check if provider is in our mapping
            if litellm_provider not in PROVIDER_MAP:
                skipped_count += 1
                continue

            tz_provider = PROVIDER_MAP[litellm_provider]

            # Validate that mapped provider exists in TensorZero providers
            if tz_provider not in tz_providers:
                logger.warning("Mapped provider %s not in TensorZero providers, skipping", tz_provider)
                skipped_count += 1
                continue

            # Special case: vertex_ai-language-models → only include Gemini models
            if litellm_provider == "vertex_ai-language-models":
                if "gemini" not in original_key.lower():
                    skipped_count += 1
                    continue

            # Create new key with provider prefix
            new_key = f"{tz_provider}/{original_key}"

            # Transform the model data
            transformed_data = transform_model(original_key, model_data, tz_provider)

            tensorzero_data[new_key] = transformed_data

            # Track counts per provider
            if tz_provider not in provider_counts:
                provider_counts[tz_provider] = 0
            provider_counts[tz_provider] += 1

        logger.info("Transformed %d models, skipped %d", len(tensorzero_data), skipped_count)

        # Log provider breakdown
        logger.info("Models per provider:")
        for provider, count in sorted(provider_counts.items()):
            logger.info("  %s: %d", provider, count)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

        # Save to output file
        with open(OUTPUT_PATH, "w") as f:
            json.dump(tensorzero_data, f, indent=2)

        logger.info("Successfully saved %d models to %s", len(tensorzero_data), OUTPUT_PATH)

    except Exception as e:
        logger.error("Error during TensorZero seeder execution: %s", e)
        raise e


if __name__ == "__main__":
    main()

    # python -m scripts.tensorzero_seeder
