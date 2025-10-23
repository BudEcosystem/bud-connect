#!/usr/bin/env python3
"""Quick script to build eval manifest - minimal version.

Usage:
    python budconnect/eval/quick_build.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from budconnect.eval.manifest_builder import EvalManifestBuilder


async def main():
    """Build the manifest."""
    # Configuration
    ENABLE_ANALYSIS = False  # Set to True to enable question analysis
    OUTPUT_FILE = "eval_manifest.json"

    print("=" * 80)
    print("Building Eval Manifest")
    print("=" * 80)
    print(f"Output: budconnect/eval/data/{OUTPUT_FILE}")
    print(f"Analysis: {'ENABLED' if ENABLE_ANALYSIS else 'DISABLED'}")
    print("=" * 80)

    # Build path
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / OUTPUT_FILE

    try:
        # Create builder and build manifest
        builder = EvalManifestBuilder(
            output_path=str(output_path),
            enable_analysis=ENABLE_ANALYSIS
        )

        print("\nFetching data from OpenCompass API...")
        result = await builder.build_manifest()

        # Show results
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"Status: {result.get('status')}")
        print(f"File: {result.get('output_file')}")
        print(f"Version: {result.get('version')}")
        print(f"Traits: {result.get('traits_count')}")
        print(f"Datasets: {result.get('datasets_count')}")
        print(f"Updated: {result.get('last_updated')}")

        if result.get('error'):
            print(f"Error: {result['error']}")
            return 1

        print("\n✓ Manifest built successfully!")
        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
