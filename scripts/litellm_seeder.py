import json
import logging
import os

import requests


# Set logging level
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Get parent directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Destination file path
destination_file_path = os.path.join(root_dir, "budconnect", "seeders", "data", "litellm_seeder.json")


def get_lite_llm_model_list(source_url: str) -> dict:
    """Get the list of models from the github url.

    Args:
        source_url: The url of the github repo
    Returns:
        The list of models
    Raises:
        Exception: If there is an error fetching or parsing the model data
    """
    try:
        logger.debug("Fetching model list from github")
        response = requests.get(source_url)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise Exception("Response data is not a valid json object")
        return data
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        logger.error("Error getting model list from github: %s", e)
        raise Exception("Error getting model list from github") from e
    except json.JSONDecodeError as e:
        logger.error("Invalid model list JSON getting from github: %s", e)
        raise Exception("Invalid model list JSON getting from github") from e
    except Exception as e:
        logger.error("Error getting model list from github: %s", e)
        raise Exception("Error getting model list from github") from e


def main():
    """Execute the script to fetch and save LiteLLM model data."""
    try:
        # lite llm model info json
        lite_llm_model_seeder = "https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json"

        # convert the github url to a raw url
        lite_llm_model_seeder_json = lite_llm_model_seeder.replace("github.com", "raw.githubusercontent.com").replace(
            "/blob/", "/"
        )

        # get the model list from the github url
        model_prices_and_context_window = get_lite_llm_model_list(lite_llm_model_seeder_json)

        # remove the sample_spec from the model list
        if "sample_spec" in model_prices_and_context_window:
            model_prices_and_context_window.pop("sample_spec")

        logger.debug("Found %s models from github", len(model_prices_and_context_window))

        # ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)

        # save the model list to the destination file path
        with open(destination_file_path, "w") as f:
            json.dump(model_prices_and_context_window, f, indent=4)

        logger.info(f"Successfully saved model data to {destination_file_path}")
    except Exception as e:
        logger.error("Error saving model data to %s: %s", destination_file_path, e)
        raise e


if __name__ == "__main__":
    main()

    # python -m scripts.litellm_seeder
