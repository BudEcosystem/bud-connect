#!/usr/bin/env python3
"""
Scan OpenCompass config files to build eval_type mapping.

This script scans all dataset config files in OpenCompass and extracts:
- Dataset abbreviation (abbr)
- Inferencer type (GenInferencer, PPLInferencer, etc.)
- Config file name
"""

import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path


def extract_inferencer_type(file_path):
    """Extract inferencer type from a config file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for inferencer=dict(type=<InferencerType>)
        inferencer_match = re.search(r'inferencer\s*=\s*dict\(\s*type\s*=\s*(\w+Inferencer)', content)
        if inferencer_match:
            return inferencer_match.group(1)

        return None
    except Exception as e:
        return None


def extract_dataset_info(file_path):
    """Extract dataset info (abbr, name, etc.) from config file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for abbr=
        abbr_match = re.search(r"abbr\s*=\s*['\"]([^'\"]+)['\"]", content)
        abbr = abbr_match.group(1) if abbr_match else None

        # Look for variable name (e.g., gsm8k_datasets = [ ... ])
        var_match = re.search(r'^(\w+)_datasets\s*=', content, re.MULTILINE)
        var_name = var_match.group(1) if var_match else None

        return abbr, var_name
    except Exception:
        return None, None


def main():
    """Scan configs and build mapping."""
    # Find OpenCompass configs directory
    base_dir = Path("venv/lib/python3.11/site-packages/opencompass/configs/datasets")

    if not base_dir.exists():
        print(f"❌ Config directory not found: {base_dir}")
        return

    print("🔍 Scanning OpenCompass config files...")
    print(f"   Directory: {base_dir}")
    print()

    # Collect mappings
    dataset_configs = defaultdict(list)
    inferencer_counts = defaultdict(int)

    # Scan all Python config files
    for config_file in base_dir.rglob("*.py"):
        # Skip __pycache__ and __init__.py
        if "__pycache__" in str(config_file) or config_file.name == "__init__.py":
            continue

        inferencer_type = extract_inferencer_type(config_file)
        abbr, var_name = extract_dataset_info(config_file)

        if inferencer_type:
            inferencer_counts[inferencer_type] += 1

            if abbr:
                # Map inferencer type to eval type
                eval_type = None
                if "GenInferencer" in inferencer_type:
                    eval_type = "gen"
                elif "PPLInferencer" in inferencer_type:
                    eval_type = "ppl"
                elif "CLPInferencer" in inferencer_type:
                    eval_type = "clp"
                elif "AgentInferencer" in inferencer_type:
                    eval_type = "agent"
                elif "LLInferencer" in inferencer_type:
                    eval_type = "ll"
                elif "ChatInferencer" in inferencer_type or "ChatMLInferencer" in inferencer_type:
                    eval_type = "chat"

                if eval_type:
                    dataset_configs[abbr].append({
                        "eval_type": eval_type,
                        "inferencer": inferencer_type,
                        "config_file": config_file.name,
                        "relative_path": str(config_file.relative_to(base_dir))
                    })

    # Print statistics
    print("=" * 80)
    print("📊 INFERENCER TYPE STATISTICS")
    print("=" * 80)
    for inferencer, count in sorted(inferencer_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {inferencer:30s}: {count:4d} configs")

    print()
    print("=" * 80)
    print(f"📚 FOUND {len(dataset_configs)} UNIQUE DATASETS")
    print("=" * 80)

    # Show sample mappings
    print("\n🔍 Sample Dataset Mappings:")
    sample_count = 0
    for abbr, configs in sorted(dataset_configs.items()):
        if sample_count >= 10:
            break
        print(f"\n  Dataset: {abbr}")
        for config in configs[:3]:  # Show up to 3 configs per dataset
            print(f"    - {config['eval_type']:6s} | {config['config_file']}")
        sample_count += 1

    # Build simple mapping: dataset abbr -> list of eval types
    simple_mapping = {}
    for abbr, configs in dataset_configs.items():
        eval_types = list(set(c['eval_type'] for c in configs))
        if len(eval_types) == 1:
            simple_mapping[abbr] = eval_types[0]
        else:
            # If multiple eval types, use dict
            simple_mapping[abbr] = {et: f"{abbr}_{et}" for et in eval_types}

    # Save to JSON
    output_file = Path("budconnect/eval/data/eval_type_mapping.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(simple_mapping, f, indent=2)

    print()
    print("=" * 80)
    print(f"✅ Mapping saved to: {output_file}")
    print(f"   Total datasets: {len(simple_mapping)}")
    print("=" * 80)

    # Show specific examples
    print("\n🎯 Specific Examples:")
    test_datasets = ["gsm8k", "ARC-c", "mmlu", "hellaswag", "ceval"]
    for ds in test_datasets:
        if ds in simple_mapping:
            print(f"  {ds:15s}: {simple_mapping[ds]}")


if __name__ == "__main__":
    main()
