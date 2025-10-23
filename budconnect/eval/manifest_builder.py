#  -----------------------------------------------------------------------------
#  Copyright (c) 2024 Bud Ecosystem Inc.
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#      http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  -----------------------------------------------------------------------------

"""Manifest builder for eval_manifest.json - fetches data from OpenCompass APIs."""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import httpx
from openai.helpers.local_audio_player import SAMPLE_RATE

from budconnect.eval.dataset_analyzer import DatasetAnalyzer
from budconnect.eval.dataset_sampler import get_dataset_sample


logger = logging.getLogger(__name__)
SAMPLE_SIZE = 5

class EvalManifestBuilder:
    """Builds eval_manifest.json from OpenCompass API data."""

    TRAITS_API_URL = "https://hub.opencompass.org.cn/gw/opencompass-be/api/v1/bench/listTopicDimensionTag"
    DATASETS_API_URL = "https://hub.opencompass.org.cn/gw/opencompass-be/api/v1/bench/listIndexCards"

    def __init__(self, output_path: str, enable_analysis: bool = False) -> None:
        """Initialize the manifest builder.

        Args:
            output_path: Path to save the eval_manifest.json file
            enable_analysis: Whether to analyze datasets with LLM (default: False)
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.client = httpx.AsyncClient(timeout=60.0, follow_redirects=True)
        self.enable_analysis = enable_analysis

        # Initialize analyzer if enabled
        if self.enable_analysis:
            self.analyzer = DatasetAnalyzer()
            logger.info("Dataset analysis enabled")
        else:
            self.analyzer = None
            logger.info("Dataset analysis disabled")

    async def fetch_traits_data(self) -> List[Dict[str, Any]]:
        """Fetch traits data from OpenCompass API.

        Returns:
            List of trait definitions
        """
        try:
            logger.info(f"Fetching traits data from: {self.TRAITS_API_URL}")

            # POST request with headers
            headers = {
                "Content-Type": "application/json",
            }

            response = await self.client.post(self.TRAITS_API_URL, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("success") and data.get("data"):
                # Traits are in data.dimensions
                dimensions = data.get("data", {}).get("dimensions", [])
                logger.info(f"Successfully fetched {len(dimensions)} traits")
                return cast(List[Dict[str, Any]], dimensions)
            else:
                logger.warning(f"API returned unsuccessful response: {data.get('msg')}")
                return []
        except Exception as e:
            logger.error(f"Failed to fetch traits data: {e}")
            return []

    async def fetch_datasets_data(self) -> List[Dict[str, Any]]:
        """Fetch datasets data from OpenCompass API with pagination.

        Returns:
            List of dataset definitions
        """
        all_datasets = []
        page_number = 1
        page_size = 50  # Fetch 100 records per page

        try:
            logger.info(f"Fetching datasets data from: {self.DATASETS_API_URL}")

            while True:
                # POST request with pagination payload
                payload = {
                    "pageNumber": page_number,
                    "pageSize": page_size,
                    "filter": None,
                    "sort": {"sortRule": 3, "asc": False},
                }

                headers = {
                    "Content-Type": "application/json",
                }

                logger.info(f"Fetching page {page_number} with {page_size} items per page")
                response = await self.client.post(self.DATASETS_API_URL, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data.get("success") and data.get("data"):
                    page_data = data["data"]
                    if not page_data:
                        # No more data
                        break

                    all_datasets.extend(page_data)
                    logger.info(
                        f"Fetched {len(page_data)} datasets from page {page_number}, total so far: {len(all_datasets)}"
                    )

                    # Check if we got less than page_size, meaning this is the last page
                    if len(page_data) < page_size:
                        break

                    page_number += 1
                else:
                    logger.warning(f"API returned unsuccessful response: {data.get('msg')}")
                    break

            logger.info(f"Successfully fetched {len(all_datasets)} total datasets")
            return all_datasets

        except Exception as e:
            logger.error(f"Failed to fetch datasets data: {e}")
            return all_datasets  # Return what we got so far

    def transform_traits(self, api_traits: List[Any]) -> Dict[str, Any]:
        """Transform API traits data to manifest format.

        Args:
            api_traits: Raw traits data from API (objects with id and name fields)

        Returns:
            Transformed traits section
        """
        definitions = []

        for trait in api_traits:
            # Handle the nested structure: trait.name.en or trait.name.cn
            if isinstance(trait, dict):
                name_obj = trait.get("name", {})
                if isinstance(name_obj, dict):
                    # Extract English name (prefer 'en' field, fallback to 'cn')
                    name = name_obj.get("en") or name_obj.get("cn", "Unknown")
                elif isinstance(name_obj, str):
                    name = name_obj
                else:
                    logger.warning(f"Unexpected trait name format: {trait}")
                    continue
            elif isinstance(trait, str):
                # Fallback for simple string format
                name = trait
            else:
                logger.warning(f"Unexpected trait format: {trait}")
                continue

            definitions.append(
                {
                    "name": name,
                    "description": f"Evaluation trait: {name}",  # Static description
                    "icon": f"icons/traits/{name.lower().replace(' ', '_').replace('-', '_')}.png",
                }
            )

        # Calculate checksum
        checksum_data = json.dumps(definitions, sort_keys=True).encode()
        checksum = hashlib.sha256(checksum_data).hexdigest()

        return {
            "version": "1.0.0",
            "checksum": f"sha256:{checksum[:16]}",
            "url": "traits/traits_v1.json",
            "count": len(definitions),
            "definitions": definitions,
        }

    async def transform_datasets(self, api_datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform API datasets data to manifest format.

        Optionally analyzes datasets using LLM if enable_analysis is True.

        Args:
            api_datasets: Raw datasets data from API

        Returns:
            Transformed datasets section
        """
        datasets = []

        for dataset in api_datasets:
            dataset_id = dataset.get("id")
            name = dataset.get("name", "Unknown")

            # Extract traits/dimensions
            # In datasets, dimensions are objects with "cn" and "en" directly (not nested under "name")
            dimensions = dataset.get("dimensions", [])
            traits = []
            for dim in dimensions:
                if isinstance(dim, dict):
                    trait_name = dim.get("en") or dim.get("cn", "")
                    if trait_name:
                        traits.append(trait_name)

            # Extract description from desc field
            desc_obj = dataset.get("desc", {})
            description = (desc_obj.get("en") or desc_obj.get("cn", "")) if isinstance(desc_obj, dict) else ""
            description = description[:500] if description else f"Evaluation dataset: {name}"

            # Build dataset entry
            dataset_entry = {
                "id": f"opencompass_{dataset_id}",
                "name": name,
                "version": "1.0.0",
                "description": description,
                "url": f"opencompass/opencompass_{dataset_id}.jsonl",
                "size_mb": 1.0,  # Static - needs calculation
                "checksum": f"sha256:placeholder_opencompass_{dataset_id}",
                "sample_count": 1000,  # Static - needs calculation
                "traits": traits,
                "metadata": {
                    "format": "jsonl",
                    "language": "English",  # Static
                    "domain": "General",  # Static
                    "difficulty": "medium",  # Static
                    "requires_auth": False,
                    "estimated_input_tokens": 1000,  # Static
                    "estimated_output_tokens": 500,  # Static
                },
                # Use Python's ** unpacking operator (like spread in JavaScript)
                # to include all fields from the original API response
                # Ensure specific keys have defaults if not present in API
                "original_data": {
                    **dataset,
                    "modalities": dataset.get("modalities", ["text"]),
                    "sample_questions_answers": dataset.get(
                        "sample_questions_answers",
                        {
                            "examples": [],
                            "total_questions": 1000,
                            "question_format": "Various formats",
                            "difficulty_levels": ["Beginner", "Intermediate", "Advanced"],
                        },
                    ),
                    "advantages_disadvantages": dataset.get(
                        "advantages_disadvantages", {"advantages": [], "disadvantages": []}
                    ),
                },
            }

            # Optionally analyze dataset questions
            if self.enable_analysis and self.analyzer:
                try:
                    logger.info(f"Starting analysis for dataset {dataset_id}: {name}")

                    # Try to sample questions from the dataset
                    dataset_name = f"opencompass/{name.lower().replace(' ', '_').replace('-', '_')}"

                    try:
                        # Get 200 sample questions
                        samples = get_dataset_sample(
                            dataset_name=dataset_name, sample_size=SAMPLE_SIZE, split="test", seed=42
                        )

                        logger.info(f"Successfully sampled {len(samples)} questions for {name}")

                        # Analyze the samples
                        analysis_data = await self.analyzer.analyze_dataset(
                            dataset_id=f"opencompass_{dataset_id}", samples=samples, max_questions=SAMPLE_SIZE
                        )

                        # Save analysis to file
                        analysis_file = await self.analyzer.save_analysis(
                            dataset_id=f"opencompass_{dataset_id}", analysis_data=analysis_data
                        )

                        # Add analysis file path to dataset entry
                        dataset_entry["analysis_file"] = str(analysis_file.relative_to(self.output_path.parent))
                        dataset_entry["analysis_summary"] = {
                            "total_analyzed": analysis_data.get("analyzed_count", 0),
                            "successful": analysis_data.get("successful", 0),
                            "failed": analysis_data.get("failed", 0),
                        }

                        logger.info(
                            f"Analysis complete for {name}: {analysis_data.get('successful', 0)}/{analysis_data.get('analyzed_count', 0)} successful"
                        )

                    except Exception as sample_error:
                        logger.warning(f"Could not sample dataset {name}: {sample_error}")
                        dataset_entry["analysis_file"] = None
                        dataset_entry["analysis_summary"] = {"error": str(sample_error)}

                except Exception as e:
                    logger.error(f"Failed to analyze dataset {name}: {e}")
                    dataset_entry["analysis_file"] = None
                    dataset_entry["analysis_summary"] = {"error": str(e)}

            datasets.append(dataset_entry)

        return {
            "opencompass": {
                "version": "2.0.0",
                "license": "Various - See individual dataset licenses",
                "source": "OpenCompass Evaluation Platform",
                "checksum": "sha256:placeholder_opencompass_v2",
                "count": len(datasets),
                "datasets": datasets,
            }
        }

    def increment_version(self, version: str) -> str:
        """Increment semantic version (MAJOR.MINOR.PATCH).

        Args:
            version: Current version string (e.g., "1.0.0")

        Returns:
            Incremented version string (PATCH version incremented)
        """
        try:
            parts = version.split(".")
            if len(parts) == 3:
                major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                # Increment patch version for data changes
                return f"{major}.{minor}.{patch + 1}"
            else:
                logger.warning(f"Invalid version format: {version}, using default")
                return "1.0.0"
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse version {version}: {e}, using default")
            return "1.0.0"

    async def build_manifest(self, existing_manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build the complete eval_manifest.json structure.

        Args:
            existing_manifest: Optional existing manifest for version continuity

        Returns:
            Complete manifest dictionary
        """
        logger.info("Starting manifest build process")

        # Fetch data from APIs
        traits_data = await self.fetch_traits_data()
        datasets_data = await self.fetch_datasets_data()

        # Use fallback empty lists if API calls fail
        if not traits_data:
            logger.warning("Using empty traits data due to API failure")
        if not datasets_data:
            logger.warning("Using empty datasets data due to API failure")

        # Transform data
        traits_section = self.transform_traits(traits_data)
        datasets_section = await self.transform_datasets(datasets_data)

        # Determine version based on existing manifest
        if existing_manifest:
            current_version = existing_manifest.get("manifest_version", "1.0.0")
            previous_versions = existing_manifest.get("version_info", {}).get("previous_versions", [])
        else:
            # First version
            current_version = "1.0.0"
            previous_versions = []

        # Build complete manifest
        manifest = {
            "manifest_version": current_version,
            "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "schema_version": "1.0",
            "repository": {
                "name": "Bud Evaluation Datasets",
                "description": f"Official evaluation datasets for model testing - {datasets_section['opencompass']['count']} datasets from OpenCompass",
                "maintainer": "Bud Ecosystem",
                "base_url": "https://eval-datasets.bud.eco/v2",
                "bundle_url": None,
                "bundle_checksum": None,
                "bundle_size_mb": None,
            },
            "version_info": {
                "current_version": current_version,
                "previous_versions": previous_versions,
            },
            "traits": traits_section,
            "datasets": datasets_section,
        }

        logger.info(
            f"Manifest built successfully: {traits_section['count']} traits, {datasets_section['opencompass']['count']} datasets"
        )
        return manifest

    def read_existing_manifest(self) -> Optional[Dict[str, Any]]:
        """Read existing manifest file if it exists.

        Returns:
            Existing manifest dictionary or None if file doesn't exist
        """
        if not self.output_path.exists():
            logger.info(f"No existing manifest file found at: {self.output_path}")
            return None

        try:
            with open(self.output_path, "r") as f:
                manifest = json.load(f)
            logger.info(f"Existing manifest loaded from: {self.output_path}")
            return cast(Dict[str, Any], manifest)
        except Exception as e:
            logger.error(f"Failed to read existing manifest: {e}")
            return None

    def has_changes(self, old_manifest: Dict[str, Any], new_manifest: Dict[str, Any]) -> bool:
        """Compare old and new manifests to detect changes.

        Ignores dynamic fields like 'last_updated', 'current_version', 'manifest_version', and 'previous_versions'.

        Args:
            old_manifest: Existing manifest data
            new_manifest: Newly built manifest data

        Returns:
            True if there are meaningful changes, False otherwise
        """
        # Create copies to avoid modifying originals
        old_copy = json.loads(json.dumps(old_manifest))
        new_copy = json.loads(json.dumps(new_manifest))

        # Remove dynamic fields that always change
        old_copy.pop("last_updated", None)
        new_copy.pop("last_updated", None)
        old_copy.pop("manifest_version", None)
        new_copy.pop("manifest_version", None)

        # Remove entire version_info section for comparison
        old_copy.pop("version_info", None)
        new_copy.pop("version_info", None)

        # Compare using JSON serialization for consistency
        old_json = json.dumps(old_copy, sort_keys=True)
        new_json = json.dumps(new_copy, sort_keys=True)

        has_diff = old_json != new_json

        if has_diff:
            logger.info("Changes detected in manifest data")
        else:
            logger.info("No changes detected in manifest data")

        return has_diff

    async def save_manifest(self, manifest: Dict[str, Any]) -> Path:
        """Save manifest to JSON file.

        Args:
            manifest: Manifest dictionary to save

        Returns:
            Path to saved file
        """
        try:
            with open(self.output_path, "w") as f:
                json.dump(manifest, f, indent=4, ensure_ascii=False)
            logger.info(f"Manifest saved to: {self.output_path}")
            return self.output_path
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")
            raise

    async def run(self) -> Dict[str, Any]:
        """Run the complete manifest building process.

        Only writes a new file if there are changes compared to the existing file.
        Increments version and updates previous_versions when changes are detected.

        Returns:
            Summary of the build process
        """
        try:
            # Read existing manifest if it exists
            existing_manifest = self.read_existing_manifest()

            # Build new manifest (with existing version info if available)
            new_manifest = await self.build_manifest(existing_manifest)

            # Check if there are changes
            if existing_manifest is not None and not self.has_changes(existing_manifest, new_manifest):
                logger.info("No changes detected - skipping file write")
                summary = {
                    "status": "no_changes",
                    "output_file": str(self.output_path),
                    "traits_count": new_manifest["traits"]["count"],
                    "datasets_count": new_manifest["datasets"]["opencompass"]["count"],
                    "last_updated": existing_manifest.get("last_updated"),
                    "version": existing_manifest.get("manifest_version", "1.0.0"),
                    "message": "No changes detected in manifest data",
                }
                return summary

            # Changes detected - increment version and update version history
            if existing_manifest is not None:
                old_version = existing_manifest.get("manifest_version", "1.0.0")
                new_version = self.increment_version(old_version)

                # Update manifest with new version
                new_manifest["manifest_version"] = new_version
                new_manifest["version_info"]["current_version"] = new_version

                # Add old version to previous_versions if not already there
                previous_versions = new_manifest["version_info"]["previous_versions"]
                old_version_entry = {
                    "version": old_version,
                    "deprecated": False,
                    "migration_required": False,
                    "updated_at": existing_manifest.get("last_updated", ""),
                }

                # Check if this version is already in previous_versions
                if not any(v.get("version") == old_version for v in previous_versions):
                    previous_versions.append(old_version_entry)
                    new_manifest["version_info"]["previous_versions"] = previous_versions

                logger.info(f"Version incremented: {old_version} -> {new_version}")

            # Save manifest (either new file or changes detected)
            output_path = await self.save_manifest(new_manifest)

            summary = {
                "status": "success",
                "output_file": str(output_path),
                "traits_count": new_manifest["traits"]["count"],
                "datasets_count": new_manifest["datasets"]["opencompass"]["count"],
                "last_updated": new_manifest["last_updated"],
                "version": new_manifest["manifest_version"],
                "message": "Manifest file created successfully"
                if existing_manifest is None
                else f"Manifest file updated with changes (version {new_manifest['manifest_version']})",
            }

            logger.info(f"Manifest build completed: {summary}")
            return summary

        except Exception as e:
            logger.exception(f"Manifest build failed: {e}")
            return {"status": "failed", "error": str(e), "timestamp": datetime.utcnow().isoformat()}
        finally:
            await self.client.aclose()
            if self.analyzer:
                await self.analyzer.close()
