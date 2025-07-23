#!/usr/bin/env python3
"""Extract structured information from saved model documentation.

This script processes markdown files saved in the raw_docs directory
and extracts structured information using the model_info_extractor.py tool.
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("extraction_errors.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class DocumentationExtractor:
    def __init__(
        self,
        api_key: str,
        llm_provider: str = "perplexity",
        llm_model: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        self.api_key = api_key
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.script_dir = Path(__file__).parent
        self.raw_docs_dir = self.script_dir / "raw_docs"
        self.output_dir = self.script_dir / "extracted_info"
        self.progress_file = self.script_dir / "extraction_progress.json"
        self.extractor_script = self.script_dir / "model_info_extractor.py"

        # Load proprietary models data
        self.models_data_file = self.script_dir.parent / "proprietary_models_output" / "proprietary_models.json"
        self.models_data = self._load_models_data()

        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True)

        # Verify extractor script exists
        if not self.extractor_script.exists():
            raise FileNotFoundError(f"Model info extractor not found: {self.extractor_script}")

    def _load_models_data(self) -> Dict:
        """Load proprietary models data for provider mapping."""
        if self.models_data_file.exists():
            with open(self.models_data_file, "r") as f:
                return json.load(f)
        return {}

    def _load_progress(self) -> Dict:
        """Load extraction progress for resume capability."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading progress file: {e}")
        return {"completed": [], "failed": [], "last_update": None}

    def _save_progress(self, progress: Dict):
        """Save extraction progress."""
        progress["last_update"] = datetime.now().isoformat()
        with open(self.progress_file, "w") as f:
            json.dump(progress, f, indent=2)

    def _find_markdown_files(
        self, provider: Optional[str] = None, models: Optional[List[str]] = None
    ) -> List[Tuple[Path, str, str]]:
        """Find markdown files to process.

        Returns list of (file_path, model_name, provider) tuples.
        """
        files_to_process = []

        if provider:
            # Process specific provider
            provider_dir = self.raw_docs_dir / provider
            if provider_dir.exists():
                # Use rglob to find all .md files recursively
                for md_file in provider_dir.rglob("*.md"):
                    # Skip README and overview files
                    stem_lower = md_file.stem.lower()
                    if (
                        stem_lower in ["readme"]
                        or stem_lower.endswith("_overview")
                        or stem_lower.endswith("_models")
                        or stem_lower.endswith("_setup")
                        or stem_lower.endswith("_availability")
                        or stem_lower.endswith("_features")
                        or stem_lower.endswith("_pricing_tiers")
                        or md_file.stem.startswith("0")
                    ):
                        continue

                    # Get relative path from provider directory
                    relative_path = md_file.relative_to(provider_dir)

                    # Model name includes subdirectory structure
                    if relative_path.parent != Path("."):
                        # Has subdirectory (e.g., meta-llama/Llama-3.2-3B-Instruct-Turbo.md)
                        model_name = str(relative_path.with_suffix(""))
                    else:
                        # Direct file in provider directory
                        model_name = md_file.stem

                    files_to_process.append((md_file, model_name, provider))
        else:
            # Process all providers
            for provider_dir in self.raw_docs_dir.iterdir():
                if provider_dir.is_dir():
                    provider = provider_dir.name
                    # Use rglob to find all .md files recursively
                    for md_file in provider_dir.rglob("*.md"):
                        # Skip README and overview files
                        if md_file.stem.lower() in ["readme", "00_together_ai_overview"] or md_file.stem.startswith(
                            "0"
                        ):
                            continue

                        # Get relative path from provider directory
                        relative_path = md_file.relative_to(provider_dir)

                        # Model name includes subdirectory structure
                        if relative_path.parent != Path("."):
                            # Has subdirectory (e.g., meta-llama/Llama-3.2-3B-Instruct-Turbo.md)
                            model_name = str(relative_path.with_suffix(""))
                        else:
                            # Direct file in provider directory
                            model_name = md_file.stem

                        files_to_process.append((md_file, model_name, provider))

        # Filter by specific models if requested
        if models:
            files_to_process = [(f, m, p) for f, m, p in files_to_process if m in models or f"{p}/{m}" in models]

        return sorted(files_to_process)

    def _extract_from_file(self, md_file: Path, model_name: str, retry_count: int = 0) -> Optional[Dict]:
        """Extract structured information from a markdown file with retry logic."""
        try:
            # Read markdown content
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                logger.warning(f"Empty file: {md_file}")
                return None

            # Save to temporary file for extraction
            temp_file = self.script_dir / f"temp_{model_name.replace('/', '_')}.md"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)

            # Run extractor
            cmd = [
                sys.executable,
                str(self.extractor_script),
                str(temp_file),
                "-p",
                self.llm_provider,
                "-k",
                self.api_key,
            ]

            if self.llm_model:
                cmd.extend(["-m", self.llm_model])

            logger.info(f"Extracting from {md_file.name}...")
            logger.debug(f"Command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,  # Increased timeout for large models
            )

            # Clean up temp file
            temp_file.unlink(missing_ok=True)

            if result.returncode == 0:
                try:
                    extracted_data = json.loads(result.stdout)
                    # Validate basic structure
                    if not isinstance(extracted_data, dict) or "model_info" not in extracted_data:
                        logger.error(f"Invalid extraction result structure for {model_name}")
                        return None
                    return extracted_data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON output for {model_name}: {e}")
                    logger.error(f"Output was: {result.stdout[:500]}...")
                    # Retry if JSON parsing failed and retries available
                    if retry_count < self.max_retries:
                        logger.info(
                            f"Retrying extraction for {model_name} (attempt {retry_count + 1}/{self.max_retries})"
                        )
                        time.sleep(self.retry_delay)
                        return self._extract_from_file(md_file, model_name, retry_count + 1)
                    return None
            else:
                logger.error(f"Extraction failed for {model_name}: {result.stderr}")
                if result.stdout:
                    logger.error(f"Stdout: {result.stdout[:500]}...")

                # Check for rate limit or API errors
                if "rate limit" in result.stderr.lower() or "429" in result.stderr:
                    logger.warning(f"Rate limit hit for {model_name}, waiting {self.retry_delay * 2} seconds...")
                    time.sleep(self.retry_delay * 2)
                    if retry_count < self.max_retries:
                        return self._extract_from_file(md_file, model_name, retry_count + 1)

                # Retry on other errors if retries available
                elif retry_count < self.max_retries:
                    logger.info(f"Retrying extraction for {model_name} (attempt {retry_count + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    return self._extract_from_file(md_file, model_name, retry_count + 1)

                return None

        except subprocess.TimeoutExpired:
            logger.error(f"Extraction timeout for {model_name} after 180 seconds")
            if retry_count < self.max_retries:
                logger.info(f"Retrying extraction for {model_name} (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
                return self._extract_from_file(md_file, model_name, retry_count + 1)
            return None
        except Exception as e:
            logger.error(f"Error extracting from {md_file}: {e}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying extraction for {model_name} (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
                return self._extract_from_file(md_file, model_name, retry_count + 1)
            return None

    def _save_extracted_info(self, model_name: str, provider: str, info: Dict):
        """Save extracted information to JSON files."""
        # Create provider directory
        provider_dir = self.output_dir / provider
        provider_dir.mkdir(exist_ok=True)

        # Handle subdirectories in model name (e.g., meta-llama/Llama-3.2-3B-Instruct-Turbo)
        if "/" in model_name:
            # Create subdirectory structure
            model_path = Path(model_name)
            output_dir = provider_dir / model_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)
            output_filename = model_path.name
        else:
            output_dir = provider_dir
            output_filename = model_name

        # Add metadata
        info["model_name"] = model_name
        info["provider"] = provider
        info["extraction_date"] = datetime.now().isoformat()

        # Get additional model data if available
        # Check both with and without provider prefix
        model_key = f"{provider}/{model_name}"
        if model_key in self.models_data:
            info["model_metadata"] = self.models_data[model_key]
        elif model_name in self.models_data:
            info["model_metadata"] = self.models_data[model_name]

        # Save individual file
        output_file = output_dir / f"{output_filename}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)

        logger.info(f"Saved: {output_file}")

    def extract_all(
        self,
        provider: Optional[str] = None,
        models: Optional[List[str]] = None,
        resume: bool = True,
        force: bool = False,
    ):
        """Extract information from all matching markdown files."""
        # Load progress
        progress = self._load_progress() if resume and not force else {"completed": [], "failed": []}

        # Find files to process
        files_to_process = self._find_markdown_files(provider, models)

        if not files_to_process:
            logger.warning("No markdown files found to process")
            return

        # Filter out already completed files if resuming
        if resume and not force:
            completed_set = set(progress["completed"])
            files_to_process = [(f, m, p) for f, m, p in files_to_process if f"{p}/{m}" not in completed_set]

        logger.info(f"Found {len(files_to_process)} files to process")

        # Process statistics
        successful = 0
        failed = 0
        all_results = {}

        # Process each file
        for i, (md_file, model_name, provider_name) in enumerate(files_to_process, 1):
            logger.info(f"\n[{i}/{len(files_to_process)}] Processing {provider_name}/{model_name}")

            # Extract information
            extracted_info = self._extract_from_file(md_file, model_name)

            if extracted_info:
                # Save extracted information
                self._save_extracted_info(model_name, provider_name, extracted_info)

                # Track success
                successful += 1
                progress["completed"].append(f"{provider_name}/{model_name}")
                all_results[f"{provider_name}/{model_name}"] = extracted_info
            else:
                # Track failure
                failed += 1
                progress["failed"].append(
                    {
                        "model": f"{provider_name}/{model_name}",
                        "file": str(md_file),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            # Save progress after each extraction
            self._save_progress(progress)

        # Save combined results
        if all_results:
            all_models_file = self.output_dir / "all_models.json"
            with open(all_models_file, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2)

        # Generate summary
        self._generate_summary(successful, failed, len(files_to_process))

    def _generate_summary(self, successful: int, failed: int, total: int):
        """Generate extraction summary."""
        summary = {
            "extraction_date": datetime.now().isoformat(),
            "total_files": total,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%",
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model or "default",
        }

        # Count by provider
        provider_stats = {}
        for provider_dir in self.output_dir.iterdir():
            if provider_dir.is_dir() and provider_dir.name != "all_models.json":
                count = len(list(provider_dir.glob("*.json")))
                if count > 0:
                    provider_stats[provider_dir.name] = count

        summary["by_provider"] = provider_stats

        # Save summary
        summary_file = self.output_dir / "extraction_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("EXTRACTION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total files processed: {total}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {summary['success_rate']}")
        logger.info("\nBy Provider:")
        for provider, count in provider_stats.items():
            logger.info(f"  {provider}: {count} models")

    def retry_failed(self):
        """Retry extraction for previously failed files."""
        progress = self._load_progress()
        failed_items = progress.get("failed", [])

        if not failed_items:
            logger.info("No failed extractions to retry")
            return

        logger.info(f"Retrying {len(failed_items)} failed extractions...")

        # Clear failed list
        progress["failed"] = []
        self._save_progress(progress)

        # Retry each failed item
        for item in failed_items:
            model_path = item["model"]
            if "/" in model_path:
                provider, model = model_path.split("/", 1)
                self.extract_all(provider=provider, models=[model], resume=False)


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured information from saved model documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all saved documentation
  python extract_from_saved_docs.py --api-key YOUR_KEY

  # Extract specific provider
  python extract_from_saved_docs.py --api-key YOUR_KEY --provider openai

  # Extract specific models
  python extract_from_saved_docs.py --api-key YOUR_KEY --models gpt-4 claude-3-opus

  # Resume interrupted extraction
  python extract_from_saved_docs.py --api-key YOUR_KEY --resume

  # Retry failed extractions
  python extract_from_saved_docs.py --api-key YOUR_KEY --retry-failed
        """,
    )

    parser.add_argument("--api-key", "-k", required=True, help="API key for the LLM provider")

    parser.add_argument(
        "--llm-provider",
        "-p",
        choices=["openai", "anthropic", "perplexity"],
        default="perplexity",
        help="LLM provider to use for extraction (default: perplexity)",
    )

    parser.add_argument("--llm-model", "-m", help="Specific LLM model to use")

    parser.add_argument("--provider", help="Process only models from this provider")

    parser.add_argument("--models", nargs="+", help="Specific model names to process")

    parser.add_argument(
        "--resume", action="store_true", default=True, help="Resume from previous extraction (default: True)"
    )

    parser.add_argument(
        "--no-resume", action="store_false", dest="resume", help="Start fresh, ignore previous progress"
    )

    parser.add_argument("--force", action="store_true", help="Force re-extraction of all files")

    parser.add_argument("--retry-failed", action="store_true", help="Retry previously failed extractions")

    args = parser.parse_args()

    # Create extractor
    extractor = DocumentationExtractor(api_key=args.api_key, llm_provider=args.llm_provider, llm_model=args.llm_model)

    # Execute requested action
    if args.retry_failed:
        extractor.retry_failed()
    else:
        extractor.extract_all(provider=args.provider, models=args.models, resume=args.resume, force=args.force)


if __name__ == "__main__":
    main()
