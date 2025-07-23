#!/usr/bin/env python3
"""Validate extracted model data for completeness and quality.

This script checks:
- Required fields are present
- Data types are correct
- Evaluation scores are valid
- No duplicate models
- Model URIs match expected format
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ModelDataValidator:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.extracted_dir = self.script_dir / "extracted_info"
        self.errors = []
        self.warnings = []

        # Required fields for each model
        self.required_fields = ["description", "advantages", "disadvantages", "use_cases"]

        # Valid evaluation benchmark names
        self.valid_benchmarks = {
            "MMLU",
            "GSM8K",
            "HellaSwag",
            "HumanEval",
            "MATH",
            "GLUE",
            "SuperGLUE",
            "BBH",
            "DROP",
            "RACE",
            "SQuAD",
            "TruthfulQA",
            "WinoGrande",
            "ARC",
            "PIQA",
            "CommonsenseQA",
            "NaturalQuestions",
            "TriviaQA",
        }

    def validate_model_uri(self, uri: str) -> bool:
        """Validate model URI format (provider/model-name)."""
        pattern = r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9._-]+$"
        return bool(re.match(pattern, uri))

    def validate_evaluation(self, eval_data: Dict) -> List[str]:
        """Validate a single evaluation entry."""
        issues = []

        if not isinstance(eval_data, dict):
            issues.append("Evaluation must be a dictionary")
            return issues

        # Check required fields
        if "name" not in eval_data:
            issues.append("Missing 'name' field in evaluation")
        elif eval_data["name"] not in self.valid_benchmarks:
            issues.append(f"Unknown benchmark: {eval_data['name']} (not in known benchmarks)")

        if "score" not in eval_data:
            issues.append("Missing 'score' field in evaluation")
        elif not isinstance(eval_data["score"], (int, float)):
            issues.append(f"Score must be numeric, got: {type(eval_data['score'])}")
        elif not 0 <= eval_data["score"] <= 100:
            issues.append(f"Score out of range [0-100]: {eval_data['score']}")

        return issues

    def validate_model_data(self, model_uri: str, data: Dict) -> Tuple[List[str], List[str]]:
        """Validate a single model's data."""
        errors = []
        warnings = []

        # Check URI format
        if not self.validate_model_uri(model_uri):
            errors.append(f"Invalid model URI format: {model_uri}")

        # Check required fields
        for field in self.required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing or empty required field: {field}")

        # Validate description
        if "description" in data:
            desc = data["description"]
            if isinstance(desc, str):
                if len(desc) < 20:
                    warnings.append("Description too short (< 20 chars)")
                elif len(desc) > 1000:
                    warnings.append("Description too long (> 1000 chars)")
            else:
                errors.append(f"Description must be string, got: {type(desc)}")

        # Validate lists
        for field in ["advantages", "disadvantages", "use_cases"]:
            if field in data:
                if not isinstance(data[field], list):
                    errors.append(f"{field} must be a list")
                elif len(data[field]) == 0:
                    warnings.append(f"Empty {field} list")
                elif len(data[field]) > 10:
                    warnings.append(f"Too many {field} items (> 10)")

        # Validate evaluations
        if "evaluations" in data:
            if not isinstance(data["evaluations"], list):
                errors.append("Evaluations must be a list")
            else:
                for i, eval_data in enumerate(data["evaluations"]):
                    eval_issues = self.validate_evaluation(eval_data)
                    for issue in eval_issues:
                        errors.append(f"Evaluation[{i}]: {issue}")

        return errors, warnings

    def check_duplicates(self, all_models: Dict[str, Any]) -> List[str]:
        """Check for duplicate model entries."""
        duplicates = []
        seen_names = {}

        for uri in all_models:
            model_name = uri.split("/")[1] if "/" in uri else uri
            if model_name in seen_names:
                duplicates.append(f"Duplicate model name: {model_name} in {uri} and {seen_names[model_name]}")
            seen_names[model_name] = uri

        return duplicates

    def validate_all(self) -> Dict[str, Any]:
        """Validate all extracted model data."""
        results = {
            "total_models": 0,
            "valid_models": 0,
            "models_with_errors": 0,
            "models_with_warnings": 0,
            "errors_by_model": {},
            "warnings_by_model": {},
            "duplicate_models": [],
            "missing_evaluations": [],
            "summary": {},
        }

        # Load all model data
        all_models = {}

        if not self.extracted_dir.exists():
            logger.error(f"Extracted directory not found: {self.extracted_dir}")
            return results

        # Read from provider directories
        for provider_dir in self.extracted_dir.iterdir():
            if provider_dir.is_dir() and provider_dir.name not in ["all_models.json", "extraction_summary.json"]:
                for model_file in provider_dir.glob("*.json"):
                    try:
                        with open(model_file, "r") as f:
                            data = json.load(f)

                        model_info = data.get("model_info", {})
                        model_uri = f"{provider_dir.name}/{model_file.stem}"

                        # Convert to expected format
                        model_data = {
                            "description": model_info.get("description"),
                            "advantages": model_info.get("strengths", []),
                            "disadvantages": model_info.get("limitations", []),
                            "use_cases": model_info.get("use_cases", []),
                            "evaluations": data.get("model_evals", []),
                        }

                        all_models[model_uri] = model_data
                    except Exception as e:
                        logger.error(f"Error loading {model_file}: {e}")

        results["total_models"] = len(all_models)

        # Check for duplicates
        results["duplicate_models"] = self.check_duplicates(all_models)

        # Validate each model
        for model_uri, data in all_models.items():
            errors, warnings = self.validate_model_data(model_uri, data)

            if errors:
                results["models_with_errors"] += 1
                results["errors_by_model"][model_uri] = errors
            else:
                results["valid_models"] += 1

            if warnings:
                results["models_with_warnings"] += 1
                results["warnings_by_model"][model_uri] = warnings

            # Check for missing evaluations
            if not data.get("evaluations"):
                results["missing_evaluations"].append(model_uri)

        # Generate summary
        results["summary"] = {
            "error_rate": f"{(results['models_with_errors']/results['total_models']*100):.1f}%"
            if results["total_models"] > 0
            else "0%",
            "warning_rate": f"{(results['models_with_warnings']/results['total_models']*100):.1f}%"
            if results["total_models"] > 0
            else "0%",
            "models_without_evals": len(results["missing_evaluations"]),
            "duplicate_count": len(results["duplicate_models"]),
        }

        return results

    def generate_report(self, output_file: Path = None):
        """Generate validation report."""
        results = self.validate_all()

        if output_file:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)

        # Print summary
        print("\n" + "=" * 60)
        print("MODEL DATA VALIDATION REPORT")
        print("=" * 60)
        print(f"Total models: {results['total_models']}")
        print(f"Valid models: {results['valid_models']}")
        print(f"Models with errors: {results['models_with_errors']} ({results['summary']['error_rate']})")
        print(f"Models with warnings: {results['models_with_warnings']} ({results['summary']['warning_rate']})")
        print(f"Duplicate models: {results['summary']['duplicate_count']}")
        print(f"Models without evaluations: {results['summary']['models_without_evals']}")

        # Show top errors
        if results["errors_by_model"]:
            print("\n" + "-" * 40)
            print("TOP ERRORS (first 5):")
            for _i, (model, errors) in enumerate(list(results["errors_by_model"].items())[:5]):
                print(f"\n{model}:")
                for error in errors[:3]:  # Show first 3 errors per model
                    print(f"  - {error}")

        # Show duplicates
        if results["duplicate_models"]:
            print("\n" + "-" * 40)
            print("DUPLICATE MODELS:")
            for dup in results["duplicate_models"][:5]:
                print(f"  - {dup}")

        print("\n" + "=" * 60)

        if output_file:
            print(f"\nDetailed report saved to: {output_file}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate extracted model data for completeness and quality")

    parser.add_argument("--output", "-o", help="Output file for detailed validation report (JSON)")

    args = parser.parse_args()

    validator = ModelDataValidator()

    output_file = Path(args.output) if args.output else None
    validator.generate_report(output_file)


if __name__ == "__main__":
    main()
