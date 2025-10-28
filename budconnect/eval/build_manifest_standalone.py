#!/usr/bin/env python3
"""Standalone script to build eval manifest without running the full app.

This script can be run directly to generate the eval_manifest.json file.

Usage:
    # Build manifest without analysis (fast)
    python budconnect/eval/build_manifest_standalone.py

    # Build manifest with analysis (analyzes questions)
    python budconnect/eval/build_manifest_standalone.py --enable-analysis

    # Custom output filename
    python budconnect/eval/build_manifest_standalone.py --output custom_manifest.json

    # Enable analysis with custom output
    python budconnect/eval/build_manifest_standalone.py --output analyzed.json --enable-analysis
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from budconnect.eval.manifest_builder import EvalManifestBuilder


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def build_manifest(output_filename: str = "eval_manifest.json", enable_analysis: bool = False):
    """Build the eval manifest file.

    Args:
        output_filename: Name of the output file
        enable_analysis: Whether to enable LLM-based question analysis
    """
    # Determine output path
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / output_filename

    logger.info("=" * 80)
    logger.info("Eval Manifest Builder - Standalone Mode")
    logger.info("=" * 80)
    logger.info(f"Output file: {output_path}")
    logger.info(f"Analysis enabled: {enable_analysis}")
    logger.info("=" * 80)

    try:
        # Create builder instance
        builder = EvalManifestBuilder(output_path=str(output_path), enable_analysis=enable_analysis)

        # Build the manifest
        logger.info("Building manifest...")
        result = await builder.run()

        # Display results
        logger.info("=" * 80)
        logger.info("Build Complete!")
        logger.info("=" * 80)
        logger.info(f"Status: {result.get('status', 'unknown')}")
        logger.info(f"Output file: {result.get('output_file', 'N/A')}")
        logger.info(f"Version: {result.get('version', 'N/A')}")
        logger.info(f"Traits count: {result.get('traits_count', 0)}")
        logger.info(f"Datasets count: {result.get('datasets_count', 0)}")
        logger.info(f"Last updated: {result.get('last_updated', 'N/A')}")

        if result.get('message'):
            logger.info(f"Message: {result['message']}")

        if result.get('error'):
            logger.error(f"Error: {result['error']}")
            return 1

        # If analysis was enabled, show analysis info
        if enable_analysis and output_path.exists():
            with open(output_path, 'r') as f:
                manifest = json.load(f)

            datasets_with_analysis = [
                d for d in manifest.get('datasets', {}).get('opencompass', {}).get('datasets', [])
                if 'analysis_file' in d
            ]

            if datasets_with_analysis:
                logger.info("=" * 80)
                logger.info(f"Analysis Results: {len(datasets_with_analysis)} datasets analyzed")
                logger.info("=" * 80)

                for dataset in datasets_with_analysis[:5]:  # Show first 5
                    summary = dataset.get('analysis_summary', {})
                    logger.info(f"  {dataset['name']}:")
                    logger.info(f"    - Analyzed: {summary.get('total_analyzed', 0)} questions")
                    logger.info(f"    - Successful: {summary.get('successful', 0)}")
                    logger.info(f"    - Failed: {summary.get('failed', 0)}")
                    logger.info(f"    - File: {dataset.get('analysis_file', 'N/A')}")

                if len(datasets_with_analysis) > 5:
                    logger.info(f"  ... and {len(datasets_with_analysis) - 5} more datasets")

        logger.info("=" * 80)
        return 0

    except KeyboardInterrupt:
        logger.warning("\nBuild interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Build failed: {e}", exc_info=True)
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build eval manifest from OpenCompass API data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build manifest without analysis (fast)
  %(prog)s

  # Build manifest with analysis (analyzes questions)
  %(prog)s --enable-analysis

  # Custom output filename
  %(prog)s --output custom_manifest.json

  # Enable debug logging
  %(prog)s --debug
        """
    )

    parser.add_argument(
        '--output', '-o',
        default='eval_manifest.json',
        help='Output filename (default: eval_manifest.json)'
    )

    parser.add_argument(
        '--enable-analysis', '-a',
        action='store_true',
        help='Enable LLM-based analysis of dataset questions (slow, analyzes sample questions per dataset)'
    )

    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('budconnect').setLevel(logging.DEBUG)

    # Run the async build function
    exit_code = asyncio.run(build_manifest(
        output_filename=args.output,
        enable_analysis=args.enable_analysis
    ))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
