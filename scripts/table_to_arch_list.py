#!/usr/bin/env python3
"""Script to convert table.json to model_architectures format.

Reads table.json with entries containing architecture class names, model info,
and feature support flags, and converts them to the model_architectures.json format
with class_name, architecture_family, parser types, and support flags.

The architecture_family is determined from the vLLM model registry (similar to
arch_support_to_seeder.py), while LoRA and pipeline parallelism support comes
from table.json.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Import the complete _VLLM_MODELS dictionary from arch_support_to_seeder
# This includes all model types: text generation, embedding, cross-encoder, multimodal, etc.
sys.path.insert(0, str(Path(__file__).parent))
from arch_support_to_seeder import _VLLM_MODELS


def convert_entry(entry: Dict[str, Any], architecture_mapping: Dict[str, Tuple[str, str]]) -> List[Dict[str, Any]]:
    """Convert a single table.json entry to one or more architecture entries.

    Handles cases where multiple architectures are listed in a single entry
    (e.g., "ChatGLMModel, ChatGLMForConditionalGeneration").

    Args:
        entry: Dictionary containing architecture, models, examples, lora, and pp fields
        architecture_mapping: Dictionary mapping class_name -> (architecture_family, canonical_class)

    Returns:
        List of architecture dictionaries in the target format
    """
    # Split architecture field by comma to handle multiple class names
    architectures = [arch.strip() for arch in entry["architecture"].split(",")]

    result = []
    for class_name in architectures:
        # Look up architecture family from mapping
        architecture_family = None
        if class_name in architecture_mapping:
            architecture_family = architecture_mapping[class_name][0]

        arch_entry = {
            "class_name": class_name,
            "architecture_family": architecture_family,
            "tool_calling_parser_type": None,
            "reasoning_parser_type": None,
            "supports_lora": entry.get("lora", False),
            "supports_pipeline_parallelism": entry.get("pp", False),
        }
        result.append(arch_entry)

    return result


def convert_table_to_arch_list(input_file: Path, output_file: Optional[Path] = None) -> None:
    """Convert table.json to model_architectures format.

    Args:
        input_file: Path to table.json
        output_file: Optional path to output file. If None, prints to stdout
    """
    # Read input file
    with open(input_file, "r", encoding="utf-8") as f:
        table_data = json.load(f)

    # Convert all entries using the architecture mapping
    architectures = []
    missing_mappings = set()
    for entry in table_data:
        converted = convert_entry(entry, _VLLM_MODELS)
        architectures.extend(converted)

        # Track architectures without mappings
        for arch in converted:
            if arch["architecture_family"] is None:
                missing_mappings.add(arch["class_name"])

    # Create output structure
    output_data = {"architectures": architectures}

    # Write output
    output_json = json.dumps(output_data, indent=2, ensure_ascii=False)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"Converted {len(table_data)} entries to {len(architectures)} architectures", file=sys.stderr)
        if missing_mappings:
            print(f"\nWarning: {len(missing_mappings)} architectures not found in mapping:", file=sys.stderr)
            for arch in sorted(missing_mappings):
                print(f"  - {arch}", file=sys.stderr)
        print(f"Output written to: {output_file}", file=sys.stderr)
    else:
        print(output_json)


def main() -> None:
    """Run the table conversion script."""
    import argparse

    parser = argparse.ArgumentParser(description="Convert table.json to model_architectures.json format")
    parser.add_argument("input", nargs="?", default="table.json", help="Input table.json file (default: table.json)")
    parser.add_argument("-o", "--output", help="Output file path (default: print to stdout)")

    args = parser.parse_args()

    input_file = Path(args.input)
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    output_file = Path(args.output) if args.output else None

    try:
        convert_table_to_arch_list(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
