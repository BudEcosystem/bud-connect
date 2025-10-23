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

"""Dataset analyzer module - analyzes dataset questions using LLM."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx


logger = logging.getLogger(__name__)


class DatasetAnalyzer:
    """Analyzes dataset questions using LLM to extract metadata about difficulty, skills, etc."""

    def __init__(
        self,
        llm_endpoint: str = "http://20.66.97.208/v1/chat/completions",
        model: str = "qwen3-32b",
        output_dir: Optional[str] = None,
    ) -> None:
        """Initialize the dataset analyzer.

        Args:
            llm_endpoint: LLM API endpoint URL
            model: Model name to use
            output_dir: Directory to save analysis results (defaults to budconnect/eval/data/analysis/)
        """
        self.llm_endpoint = llm_endpoint
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0, follow_redirects=True)

        # Set up output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).parent / "data" / "analysis"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load analytics prompt
        self.analytics_prompt = self._load_analytics_prompt()

    def _load_analytics_prompt(self) -> str:
        """Load the analytics prompt from file.

        Returns:
            Analytics prompt template
        """
        prompt_file = Path(__file__).parent / "anlyticsprompt.txt"
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load analytics prompt: {e}")
            raise

    def format_question(self, sample: Dict[str, Any]) -> str:
        """Format a dataset sample into a question string.

        Args:
            sample: Dataset sample dictionary

        Returns:
            Formatted question string
        """
        # Try to extract question from common field names
        question_fields = ["input", "question", "prompt", "text", "query"]

        for field in question_fields:
            if field in sample:
                question = str(sample[field])
                # Add options if available (for multiple choice)
                if "A" in sample and "B" in sample:
                    options = []
                    for opt in ["A", "B", "C", "D"]:
                        if opt in sample:
                            options.append(f"{opt}) {sample[opt]}")
                    if options:
                        question += "\n\nOptions:\n" + "\n".join(options)
                return question

        # Fallback: convert entire sample to string
        return json.dumps(sample, ensure_ascii=False)

    async def analyze_question(self, question: str) -> Dict[str, Any]:
        """Analyze a single question using the LLM.

        Args:
            question: Question text to analyze

        Returns:
            Analysis results as dictionary
        """
        # Format the prompt with the question
        full_prompt = self.analytics_prompt.replace("{$Question}", question)

        # Prepare API request
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": full_prompt,
                        }
                    ],
                }
            ],
            "model": self.model,
        }

        try:
            logger.debug(f"Analyzing question (length: {len(question)})")
            response = await self.client.post(self.llm_endpoint, json=payload)
            response.raise_for_status()

            result = response.json()

            # Extract the response content
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]

                # Try to parse JSON from content
                try:
                    # Remove markdown code blocks if present
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0]
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0]

                    analysis = json.loads(content.strip())
                    return analysis
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON response: {e}")
                    return {
                        "error": "Failed to parse response",
                        "raw_content": content,
                    }
            else:
                logger.warning("Unexpected API response format")
                return {"error": "Unexpected response format", "raw_response": result}

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during analysis: {e}")
            return {"error": f"HTTP error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error analyzing question: {e}")
            return {"error": str(e)}

    async def analyze_dataset(
        self, dataset_id: str, samples: List[Dict[str, Any]], max_questions: int = 100
    ) -> Dict[str, Any]:
        """Analyze a dataset by processing multiple questions.

        Args:
            dataset_id: Dataset identifier
            samples: List of dataset samples
            max_questions: Maximum number of questions to analyze

        Returns:
            Analysis summary with all results
        """
        logger.info(f"Starting analysis of dataset {dataset_id} ({len(samples)} samples)")

        # Limit to max_questions
        samples_to_analyze = samples[:max_questions]

        analyzed_questions = []
        successful = 0
        failed = 0

        for idx, sample in enumerate(samples_to_analyze, 1):
            logger.info(f"Analyzing question {idx}/{len(samples_to_analyze)} for {dataset_id}")

            # Format the question
            question_text = self.format_question(sample)

            # Analyze
            analysis = await self.analyze_question(question_text)

            # Store result
            result = {
                "question_index": idx,
                "original_sample": sample,
                "question_text": question_text,
                "analysis": analysis,
            }

            analyzed_questions.append(result)

            if "error" not in analysis:
                successful += 1
            else:
                failed += 1

            # Log progress every 10 questions
            if idx % 10 == 0:
                logger.info(f"Progress: {idx}/{len(samples_to_analyze)} questions analyzed")

        # Create summary
        summary = {
            "dataset_id": dataset_id,
            "total_samples": len(samples),
            "analyzed_count": len(analyzed_questions),
            "successful": successful,
            "failed": failed,
            "questions": analyzed_questions,
        }

        logger.info(
            f"Analysis complete for {dataset_id}: {successful} successful, {failed} failed"
        )

        return summary

    async def save_analysis(self, dataset_id: str, analysis_data: Dict[str, Any]) -> Path:
        """Save analysis results to a JSON file.

        Args:
            dataset_id: Dataset identifier
            analysis_data: Analysis results to save

        Returns:
            Path to saved file
        """
        # Clean dataset_id for filename
        safe_id = dataset_id.replace("/", "_").replace(" ", "_")
        output_file = self.output_dir / f"{safe_id}_analysis.json"

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Analysis saved to: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
