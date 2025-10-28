#!/usr/bin/env python3
"""Simple test script for the dataset sampler utility.

This script demonstrates the basic usage of get_dataset_sample() function.
"""

import sys
from pathlib import Path

# Add project root to path for direct execution
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from budconnect.eval.dataset_sampler import get_dataset_sample, print_sample_summary


def main():
    """Test the dataset sampler with a simple example."""
    print("Testing OpenCompass Dataset Sampler")
    print("=" * 80)

    # Example 1: Sample from a dataset
    print("\n1. Sampling 100 questions from MMLU dataset...")
    try:
        samples = get_dataset_sample(
            dataset_name='opencompass/mmlu',
            sample_size=100,
            split='test',
            seed=42
        )

        print(f"\n✓ Success! Retrieved {len(samples)} samples")

        # Display summary
        print_sample_summary(samples, max_display=3)

        # Show some statistics
        print("\nDataset Statistics:")
        print(f"  - Total samples retrieved: {len(samples)}")
        print(f"  - Sample structure (keys): {list(samples[0].keys())}")

        # Example of accessing individual fields
        if samples:
            first_sample = samples[0]
            print("\nFirst Sample Details:")
            for key, value in first_sample.items():
                value_str = str(value)[:100]
                print(f"  - {key}: {value_str}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    # Example 2: Sample from a different dataset
    print("\n\n2. Sampling 50 questions from GSM8K dataset...")
    try:
        gsm8k_samples = get_dataset_sample(
            dataset_name='opencompass/gsm8k',
            sample_size=50,
            split='test',
            shuffle=True,
            seed=42
        )

        print(f"\n✓ Success! Retrieved {len(gsm8k_samples)} samples")
        print_sample_summary(gsm8k_samples, max_display=2)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        # This is expected if the dataset is not available
        print("  (This dataset may not be downloaded yet)")

    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
