#!/usr/bin/env python3
"""Sync model_architectures.json with vLLM architecture registry.

Adds any missing class names from arch_support_to_seeder._VLLM_MODELS to
budconnect/seeders/data/model_architectures.json, leaving existing entries
untouched. Newly added architectures are initialized with null parser types
and false support flags. The script prints any new class names so they can be
reviewed and filled in.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from arch_support_to_seeder import _VLLM_MODELS


DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "budconnect"
    / "seeders"
    / "data"
    / "model_architectures.json"
)


def load_architectures(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    architectures = data.get("architectures")
    if not isinstance(architectures, list):
        raise ValueError("Expected 'architectures' to be a list in model_architectures.json")
    return architectures


def main() -> None:
    architectures = load_architectures(DATA_FILE)
    existing_by_lower = {}
    for arch in architectures:
        if not isinstance(arch, dict):
            continue
        class_name = arch.get("class_name")
        if not class_name:
            continue
        existing_by_lower.setdefault(class_name.lower(), class_name)

    new_arches = []
    case_mismatches = []
    for class_name, (architecture_family, _) in _VLLM_MODELS.items():
        existing_name = existing_by_lower.get(class_name.lower())
        if existing_name:
            if existing_name != class_name:
                case_mismatches.append((class_name, existing_name))
            continue
        architectures.append(
            {
                "class_name": class_name,
                "architecture_family": architecture_family,
                "tool_calling_parser_type": None,
                "reasoning_parser_type": None,
                "supports_lora": False,
                "supports_pipeline_parallelism": False,
            }
        )
        existing_by_lower[class_name.lower()] = class_name
        new_arches.append(class_name)

    if new_arches:
        output_json = json.dumps({"architectures": architectures}, indent=2, ensure_ascii=False)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write(output_json)
        print("New architectures added:")
        for arch in new_arches:
            print(f"- {arch}")
    else:
        print("No new architectures added.")

    if case_mismatches:
        print("Case-insensitive matches with different casing (not added):")
        for desired, existing in case_mismatches:
            print(f"- {desired} (existing: {existing})")


if __name__ == "__main__":
    main()
