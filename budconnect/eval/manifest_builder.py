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
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import httpx
from openai.helpers.local_audio_player import SAMPLE_RATE

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not available - token estimation will use default values")

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

        # Load eval type mapping
        self.eval_type_mapping = self._load_eval_type_mapping()

        # Initialize analyzer if enabled
        if self.enable_analysis:
            self.analyzer = DatasetAnalyzer()
            logger.info("Dataset analysis enabled")
        else:
            self.analyzer = None
            logger.info("Dataset analysis disabled")

    def _load_eval_type_mapping(self) -> Dict[str, Any]:
        """Load eval type mapping from JSON file.

        Returns:
            Dictionary mapping dataset abbreviations to eval types
        """
        mapping_file = Path(__file__).parent / "data" / "eval_type_mapping.json"
        try:
            if mapping_file.exists():
                with open(mapping_file, 'r') as f:
                    mapping = json.load(f)
                logger.info(f"Loaded eval type mapping for {len(mapping)} datasets")
                return mapping
            else:
                logger.warning(f"Eval type mapping file not found: {mapping_file}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load eval type mapping: {e}")
            return {}

    def _get_eval_type(self, dataset_name: str) -> Dict[str, str]:
        """Get eval type for a dataset based on its name.

        Args:
            dataset_name: Name of the dataset

        Returns:
            Dictionary with eval types (e.g., {"gen": "gsm8k_gen"})
            Returns empty dict if no mapping found
        """
        # Try exact match first
        if dataset_name in self.eval_type_mapping:
            eval_info = self.eval_type_mapping[dataset_name]

            # If it's a string, it means there's only one eval type
            if isinstance(eval_info, str):
                return {eval_info: f"{dataset_name}_{eval_info}"}
            # If it's a dict, return it directly
            elif isinstance(eval_info, dict):
                return eval_info

        # Try case-insensitive match
        dataset_lower = dataset_name.lower()
        for key, value in self.eval_type_mapping.items():
            if key.lower() == dataset_lower:
                if isinstance(value, str):
                    return {value: f"{dataset_name}_{value}"}
                elif isinstance(value, dict):
                    return value

        # No mapping found
        logger.debug(f"No eval type mapping found for dataset: {dataset_name}")
        return {}

    def estimate_tokens_from_samples(self, samples: List[Dict[str, Any]]) -> Dict[str, int]:
        """Estimate input and output tokens from dataset samples.

        Args:
            samples: List of dataset samples

        Returns:
            Dictionary with estimated_input_tokens and estimated_output_tokens
        """
        # If tiktoken is not available, return defaults
        if not TIKTOKEN_AVAILABLE:
            return {
                "estimated_input_tokens": 100,
                "estimated_output_tokens": 50
            }

        try:
            # Use cl100k_base encoding (GPT-4, GPT-3.5-turbo)
            encoding = tiktoken.get_encoding("cl100k_base")

            input_tokens = []
            output_tokens = []

            # Common field names for inputs and outputs
            input_fields = ['input', 'question', 'prompt', 'text', 'query', 'context']
            output_fields = ['output', 'answer', 'target', 'label', 'completion']

            for sample in samples:
                # Extract input text
                input_text = ""
                for field in input_fields:
                    if field in sample and sample[field]:
                        input_text += str(sample[field]) + " "

                # For multiple choice, include options in input
                if 'A' in sample and 'B' in sample:
                    for opt in ['A', 'B', 'C', 'D', 'E']:
                        if opt in sample and sample[opt]:
                            input_text += str(sample[opt]) + " "

                # Extract output text
                output_text = ""
                for field in output_fields:
                    if field in sample and sample[field]:
                        output_text += str(sample[field]) + " "

                # Count tokens
                if input_text.strip():
                    input_tokens.append(len(encoding.encode(input_text.strip())))
                if output_text.strip():
                    output_tokens.append(len(encoding.encode(output_text.strip())))

            # Calculate averages (rounded up)
            avg_input = int(sum(input_tokens) / len(input_tokens)) if input_tokens else 100
            avg_output = int(sum(output_tokens) / len(output_tokens)) if output_tokens else 50

            logger.debug(
                f"Token estimation from {len(samples)} samples: "
                f"input={avg_input} (from {len(input_tokens)} samples), "
                f"output={avg_output} (from {len(output_tokens)} samples)"
            )

            return {
                "estimated_input_tokens": avg_input,
                "estimated_output_tokens": avg_output
            }

        except Exception as e:
            logger.warning(f"Failed to estimate tokens: {e}")
            # Return default values on error
            return {
                "estimated_input_tokens": 100,
                "estimated_output_tokens": 50
            }

    async def fetch_traits_data(self) -> List[Dict[str, Any]]:
        """Fetch traits data from OpenCompass API.

        Returns:
            List of trait definitions (topics from API)
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
                # Use topics instead of dimensions for richer descriptions
                topics = data.get("data", {}).get("topics", [])
                logger.info(f"Successfully fetched {len(topics)} traits (topics)")
                return cast(List[Dict[str, Any]], topics)
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

    def aggregate_analysis(self, analysis_data: Dict[str, Any], total_questions: Optional[int] = None) -> Dict[str, Any]:
        """Aggregate analysis data to extract useful metadata.

        Args:
            analysis_data: Analysis results from DatasetAnalyzer
            total_questions: Total number of questions in the dataset (optional, defaults to total_samples from analysis)

        Returns:
            Dictionary with aggregated sample_questions_answers and advantages_disadvantages
        """
        questions = analysis_data.get("questions", [])

        # Use provided total_questions or fall back to total_samples from analysis
        dataset_total = total_questions if total_questions is not None else analysis_data.get("total_samples", 0)

        if not questions:
            return {
                "sample_questions_answers": {
                    "examples": [],
                    "total_questions": dataset_total,
                    "question_format": "Unknown",
                    "difficulty_levels": []
                },
                "advantages_disadvantages": {
                    "advantages": [],
                    "disadvantages": []
                }
            }

        # Extract examples (first 3 successful analyses)
        examples = []
        difficulty_set = set()
        task_types = set()
        domains_all = set()
        skills_all = set()
        concepts_all = set()

        for q in questions:
            analysis = q.get("analysis", {})

            # Skip if there's an error
            if "error" in analysis:
                continue

            # Collect examples
            if len(examples) < 3:
                example = {
                    "question": q.get("question_text", "")[:200],  # Truncate long questions
                    "difficulty": analysis.get("difficulty", "unknown"),
                    "task_type": ", ".join(analysis.get("task_type", [])) if isinstance(analysis.get("task_type"), list) else analysis.get("task_type", "unknown")
                }
                examples.append(example)

            # Collect difficulty levels
            if "difficulty" in analysis:
                difficulty_set.add(analysis["difficulty"])

            # Collect task types
            task_type = analysis.get("task_type", [])
            if isinstance(task_type, list):
                task_types.update(task_type)
            elif task_type:
                task_types.add(task_type)

            # Collect domains
            domains = analysis.get("domains", [])
            if isinstance(domains, list):
                domains_all.update(domains)

            # Collect skills
            skills = analysis.get("skill", [])
            if isinstance(skills, list):
                skills_all.update(skills)

            # Collect concepts
            concepts = analysis.get("concepts", [])
            if isinstance(concepts, list):
                concepts_all.update(concepts)

        # Format question format from task types
        question_format = ", ".join(sorted(task_types)) if task_types else "Various formats"

        # Map difficulty levels to standard categories
        difficulty_mapping = {
            "easy": "Beginner",
            "moderate": "Intermediate",
            "difficult": "Advanced",
            "extremely_difficult": "Expert",
            "impossible": "Expert"
        }
        difficulty_levels = sorted(set(difficulty_mapping.get(d, "Intermediate") for d in difficulty_set))

        # Generate advantages based on analysis
        advantages = []
        if domains_all:
            advantages.append(f"Tests domain-specific knowledge in {', '.join(list(domains_all)[:3])}")
        if skills_all:
            advantages.append(f"Evaluates {', '.join(list(skills_all)[:3])} skills")
        if len(difficulty_levels) > 1:
            advantages.append(f"Covers multiple difficulty levels: {', '.join(difficulty_levels)}")
        if task_types:
            advantages.append(f"Diverse task types: {', '.join(list(task_types)[:3])}")

        # Generate disadvantages based on analysis
        disadvantages = []
        if "extremely_difficult" in difficulty_set or "impossible" in difficulty_set:
            disadvantages.append("Contains very challenging questions that may require expert knowledge")
        if len(domains_all) > 3:
            disadvantages.append("Requires knowledge across multiple specialized domains")
        if analysis_data.get("failed", 0) > 0:
            disadvantages.append(f"Analysis failed for {analysis_data.get('failed', 0)} questions")

        return {
            "sample_questions_answers": {
                "examples": examples,
                "total_questions": dataset_total,
                "question_format": question_format,
                "difficulty_levels": difficulty_levels if difficulty_levels else ["Intermediate"]
            },
            "advantages_disadvantages": {
                "advantages": advantages,
                "disadvantages": disadvantages
            }
        }

    def transform_traits(self, api_traits: List[Any]) -> Dict[str, Any]:
        """Transform API traits data (topics) to manifest format.

        Args:
            api_traits: Raw traits data from API (topics with rich descriptions)

        Returns:
            Transformed traits section
        """
        definitions = []

        for trait in api_traits:
            if not isinstance(trait, dict):
                logger.warning(f"Unexpected trait format (not dict): {trait}")
                continue

            # Extract name
            name_obj = trait.get("name", {})
            if isinstance(name_obj, dict):
                # Extract English name (prefer 'en' field, fallback to 'cn')
                name = name_obj.get("en") or name_obj.get("cn", "Unknown")
            elif isinstance(name_obj, str):
                name = name_obj
            else:
                logger.warning(f"Unexpected trait name format: {trait}")
                continue

            # Extract description from indexTopicDesc or desc
            # indexTopicDesc is shorter and more focused on evaluation
            description = ""
            desc_obj = trait.get("indexTopicDesc", trait.get("desc", {}))
            if isinstance(desc_obj, dict):
                description = desc_obj.get("en") or desc_obj.get("cn", "")
            elif isinstance(desc_obj, str):
                description = desc_obj

            # Fallback to generic description if nothing found
            if not description:
                description = f"Evaluation trait: {name}"

            # Extract slogan if available
            slogan = ""
            slogan_obj = trait.get("slogan", {})
            if isinstance(slogan_obj, dict):
                slogan = slogan_obj.get("en") or slogan_obj.get("cn", "")

            # Get background image URL if available
            icon_url = trait.get("backgroundImgUrl", "")

            definitions.append(
                {
                    "name": name,
                    "description": description,
                    "slogan": slogan,
                    "icon": icon_url or f"icons/traits/{name.lower().replace(' ', '_').replace('-', '_')}.png",
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

    async def transform_datasets(self, api_datasets: List[Dict[str, Any]], existing_manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Transform API datasets data to manifest format.

        Optionally analyzes datasets using LLM if enable_analysis is True.

        Args:
            api_datasets: Raw datasets data from API
            existing_manifest: Previous manifest for reusing unchanged data

        Returns:
            Transformed datasets section
        """
        # Build lookup for existing datasets by ID for quick access
        existing_datasets_map = {}
        if existing_manifest and "datasets" in existing_manifest:
            opencompass_data = existing_manifest.get("datasets", {}).get("opencompass", {})
            existing_datasets = opencompass_data.get("datasets", [])
            for ds in existing_datasets:
                ds_id = ds.get("id")
                if ds_id:
                    existing_datasets_map[ds_id] = ds

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

            # Determine eval type from mapping
            eval_type = self._get_eval_type(name)

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
                "eval_type": eval_type,
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

            # Check if dataset exists in previous manifest and hasn't been updated
            existing_entry = existing_datasets_map.get(f"opencompass_{dataset_id}")
            dataset_updated = True  # Assume updated by default

            if existing_entry:
                # Compare updateDate to check if dataset has changed
                old_update_date = existing_entry.get("original_data", {}).get("updateDate")
                new_update_date = dataset.get("updateDate")

                if old_update_date == new_update_date:
                    # Dataset hasn't been updated - reuse previous data
                    dataset_updated = False
                    dataset_entry["sample_count"] = existing_entry.get("sample_count", 1000)
                    dataset_entry["metadata"]["estimated_input_tokens"] = existing_entry.get("metadata", {}).get("estimated_input_tokens", 100)
                    dataset_entry["metadata"]["estimated_output_tokens"] = existing_entry.get("metadata", {}).get("estimated_output_tokens", 50)

                    # Also reuse analysis data if it exists
                    has_analysis = "analysis_file" in existing_entry
                    if has_analysis:
                        dataset_entry["analysis_file"] = existing_entry.get("analysis_file")
                    if "analysis_summary" in existing_entry:
                        dataset_entry["analysis_summary"] = existing_entry.get("analysis_summary")

                    # Reuse sample_questions_answers and advantages_disadvantages
                    if "sample_questions_answers" in existing_entry.get("original_data", {}):
                        dataset_entry["original_data"]["sample_questions_answers"] = existing_entry["original_data"]["sample_questions_answers"]
                    if "advantages_disadvantages" in existing_entry.get("original_data", {}):
                        dataset_entry["original_data"]["advantages_disadvantages"] = existing_entry["original_data"]["advantages_disadvantages"]

                    # Enhanced logging
                    cache_type = "with analysis" if has_analysis else "without analysis"
                    logger.info(
                        f"✓ CACHE HIT [{cache_type}]: {name} (updateDate: {old_update_date}) - "
                        f"Reusing sample_count={dataset_entry['sample_count']}, tokens, and metadata"
                    )
                else:
                    # Dataset has been updated
                    logger.info(
                        f"⟳ DATASET UPDATED: {name} - updateDate changed from {old_update_date} to {new_update_date}"
                    )
            else:
                # New dataset (no cache)
                logger.info(f"✦ NEW DATASET: {name} - No cached data available")

            # Only sample if dataset is new or has been updated
            if dataset_updated:
                # Optionally analyze dataset questions
                if self.enable_analysis and self.analyzer:
                    try:
                        reason = "new dataset" if not existing_entry else "dataset updated"
                        logger.info(f"🔬 RUNNING ANALYSIS: {name} ({reason}) - Sampling and analyzing questions")

                        # Try to sample questions from the dataset
                        dataset_name = f"opencompass/{name.lower().replace(' ', '_').replace('-', '_')}"

                        try:
                            # Get sample questions and total count
                            samples, total_count = get_dataset_sample(
                                dataset_name=dataset_name, sample_size=SAMPLE_SIZE, split="test", seed=42, return_total_count=True
                            )

                            logger.info(f"Successfully sampled {len(samples)} questions for {name} (total: {total_count})")

                            # Update dataset entry with actual sample count
                            dataset_entry["sample_count"] = total_count

                            # Estimate tokens from samples
                            token_estimates = self.estimate_tokens_from_samples(samples)
                            dataset_entry["metadata"]["estimated_input_tokens"] = token_estimates["estimated_input_tokens"]
                            dataset_entry["metadata"]["estimated_output_tokens"] = token_estimates["estimated_output_tokens"]

                            # Analyze the samples
                            analysis_data = await self.analyzer.analyze_dataset(
                                dataset_id=f"opencompass_{dataset_id}", samples=samples, max_questions=SAMPLE_SIZE
                            )

                            # Save analysis to file
                            analysis_file = await self.analyzer.save_analysis(
                                dataset_id=f"opencompass_{dataset_id}", analysis_data=analysis_data
                            )

                            # Aggregate analysis data for sample_questions_answers and advantages_disadvantages
                            aggregated_data = self.aggregate_analysis(analysis_data, total_questions=total_count)

                            # Update dataset entry with aggregated data
                            dataset_entry["original_data"]["sample_questions_answers"] = aggregated_data["sample_questions_answers"]
                            dataset_entry["original_data"]["advantages_disadvantages"] = aggregated_data["advantages_disadvantages"]

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
                else:
                    # When analysis is disabled, still try to sample for token estimation
                    reason = "new dataset" if not existing_entry else "dataset updated"
                    logger.info(f"📊 SAMPLING ONLY: {name} ({reason}) - Getting tokens (analysis disabled)")

                    dataset_name = f"opencompass/{name.lower().replace(' ', '_').replace('-', '_')}"

                    try:
                        # Sample just a few rows for token estimation
                        samples, total_count = get_dataset_sample(
                            dataset_name=dataset_name, sample_size=5, split="test", seed=42, return_total_count=True
                        )

                        # Update dataset entry with actual sample count
                        dataset_entry["sample_count"] = total_count

                        # Estimate tokens from samples
                        token_estimates = self.estimate_tokens_from_samples(samples)
                        dataset_entry["metadata"]["estimated_input_tokens"] = token_estimates["estimated_input_tokens"]
                        dataset_entry["metadata"]["estimated_output_tokens"] = token_estimates["estimated_output_tokens"]

                        logger.info(
                            f"  └─ {name}: sample_count={total_count}, "
                            f"input_tokens={token_estimates['estimated_input_tokens']}, "
                            f"output_tokens={token_estimates['estimated_output_tokens']}"
                        )

                    except Exception as sample_error:
                        logger.debug(f"Could not sample dataset {name} for token estimation: {sample_error}")
                        # Keep default values

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
        datasets_section = await self.transform_datasets(datasets_data, existing_manifest)

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
        """Save manifest to versioned JSON file and create symlink.

        Saves the manifest as eval-manifest-<version>.json and creates/updates
        a symlink eval-manifest.json pointing to the latest version.

        Args:
            manifest: Manifest dictionary to save

        Returns:
            Path to saved versioned file
        """
        try:
            # Get version from manifest
            version = manifest.get("manifest_version", "1.0.0")

            # Create versioned filename
            base_name = self.output_path.stem  # e.g., "eval_manifest"
            versioned_name = f"{base_name}-{version}.json"
            versioned_path = self.output_path.parent / versioned_name

            # Save the versioned file
            with open(versioned_path, "w") as f:
                json.dump(manifest, f, indent=4, ensure_ascii=False)
            logger.info(f"Manifest saved to versioned file: {versioned_path}")

            # Create/update symlink to point to latest version
            symlink_path = self.output_path

            # Remove existing symlink or file if it exists
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()

            # Create symlink (relative path for portability)
            os.symlink(versioned_name, symlink_path)
            logger.info(f"Symlink created: {symlink_path} -> {versioned_name}")

            return versioned_path
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
