#!/usr/bin/env python3
"""Create consolidated model_details.json from extracted model documentation.

This script reads the extracted model information from the model_docs_workflow
and creates a single JSON file for the model details seeder.
"""

import json
from pathlib import Path
from typing import Any, Dict


def load_extracted_data(extracted_dir: Path) -> Dict[str, Any]:
    """Load all extracted model data from the directory.

    Args:
        extracted_dir: Path to the extracted_info directory

    Returns:
        Dictionary mapping model URIs to their details
    """
    all_models = {}

    # Read individual provider directories (prioritize this over all_models.json)
    for provider_dir in extracted_dir.iterdir():
        if provider_dir.is_dir() and provider_dir.name not in ["all_models.json", "extraction_summary.json"]:
            for model_file in provider_dir.glob("*.json"):
                try:
                    with open(model_file, "r") as f:
                        data = json.load(f)

                    model_name = model_file.stem
                    model_info = data.get("model_info", {})

                    model_details = {
                        "description": model_info.get("description"),
                        "advantages": model_info.get("strengths", []),
                        "disadvantages": model_info.get("limitations", []),
                        "use_cases": model_info.get("use_cases", []),
                        "evaluations": data.get("model_evals", []),
                        "languages": model_info.get("languages", []),
                        "tags": model_info.get("tags", []),
                        "tasks": model_info.get("tasks", []),
                        "papers": model_info.get("papers", []),
                        "github_url": model_info.get("github_url"),
                        "website_url": model_info.get("website_url"),
                        "logo_url": model_info.get("logo_url"),
                        "architecture": model_info.get("architecture"),
                        "model_tree": model_info.get("model_tree"),
                        "extraction_metadata": {
                            "extraction_date": data.get("extraction_date"),
                            "provider": data.get("provider"),
                            "model_metadata": data.get("model_metadata", {}),
                        },
                    }

                    # Use provider/model format as URI to match tensorzero_v_0_1_0.json
                    model_uri = f"{provider_dir.name}/{model_name}"
                    all_models[model_uri] = model_details
                    print(f"  Loaded: {model_uri}")
                except Exception as e:
                    print(f"  Error loading {model_file}: {e}")

    return all_models


def main():
    """Main function to create model_details.json."""
    # Paths
    script_dir = Path(__file__).parent
    extracted_dir = script_dir / "extracted_info"
    output_file = script_dir.parent.parent / "budconnect" / "seeders" / "data" / "model_details.json"

    # Check if extracted directory exists
    if not extracted_dir.exists():
        print(f"Error: Extracted info directory not found: {extracted_dir}")
        return

    # Load all extracted data
    print(f"Loading extracted data from: {extracted_dir}")
    all_models = load_extracted_data(extracted_dir)

    if not all_models:
        print("No model data found to process")
        return

    print(f"Found {len(all_models)} models")

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write consolidated JSON
    with open(output_file, "w") as f:
        json.dump(all_models, f, indent=2, sort_keys=True)

    print(f"Successfully created: {output_file}")
    print(f"Total models: {len(all_models)}")

    # Print sample of models
    print("\nSample models included:")
    for _i, model_uri in enumerate(list(all_models.keys())[:5]):
        print(f"  - {model_uri}")
    if len(all_models) > 5:
        print(f"  ... and {len(all_models) - 5} more")


if __name__ == "__main__":
    main()
