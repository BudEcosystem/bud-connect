"""
Dataset Sampler Utility

This module provides functionality to download datasets (if needed) and retrieve
samples from them for evaluation purposes.
"""

import random
from typing import Dict, List, Optional, Union

from datasets import Dataset, DatasetDict

from opencompass.utils import get_data_path, get_logger
from opencompass.utils.datasets_info import DATASETS_MAPPING

logger = get_logger()


def get_dataset_sample(
    dataset_name: str,
    sample_size: int = 100,
    split: str = 'test',
    seed: Optional[int] = 42,
    shuffle: bool = True
) -> List[Dict]:
    """
    Download dataset if needed and retrieve a sample of questions.

    This function integrates with OpenCompass's dataset infrastructure to:
    1. Download the dataset if not already cached
    2. Load the dataset from raw files (CSV, JSON, JSONL)
    3. Return a sample of questions

    Args:
        dataset_name (str): Name of the dataset to load. This should match a key
            in DATASETS_MAPPING or be a path to a local dataset.
        sample_size (int): Number of questions to sample. Defaults to 100.
        split (str): Which split to sample from ('train', 'test', 'dev', etc.).
            Defaults to 'test'.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
            Set to None for no seeding.
        shuffle (bool): Whether to shuffle before sampling. If False, takes the
            first sample_size items. Defaults to True.

    Returns:
        List[Dict]: A list of dictionaries, each representing a question/sample
            from the dataset.

    Raises:
        ValueError: If the dataset_name is not found or split doesn't exist.
        AssertionError: If the dataset cannot be loaded.

    Examples:
        >>> # Sample 100 questions from MMLU
        >>> samples = get_dataset_sample('opencompass/mmlu', sample_size=100)
        >>> print(f"Retrieved {len(samples)} samples")
        >>> print(f"First sample: {samples[0]}")

        >>> # Sample 50 questions from ARC-Challenge without shuffling
        >>> samples = get_dataset_sample(
        ...     'opencompass/ai2_arc',
        ...     sample_size=50,
        ...     shuffle=False
        ... )

        >>> # Sample from training set
        >>> samples = get_dataset_sample(
        ...     'opencompass/mmlu',
        ...     sample_size=20,
        ...     split='dev'
        ... )
    """
    import csv
    import json
    import os
    import glob

    logger.info(f"Loading dataset: {dataset_name}")

    # Check if dataset exists in mapping
    if dataset_name in DATASETS_MAPPING:
        logger.info(f"Found {dataset_name} in DATASETS_MAPPING")
        # Use get_data_path to handle download and caching
        dataset_path = get_data_path(dataset_name, local_mode=False)
        logger.info(f"Dataset path resolved to: {dataset_path}")
    else:
        logger.warning(
            f"{dataset_name} not found in DATASETS_MAPPING. "
            "Attempting to use as direct path..."
        )
        dataset_path = dataset_name

    # Load dataset from raw files
    dataset_items = []

    try:
        # Check if it's a directory with splits
        if os.path.isdir(dataset_path):
            split_dir = os.path.join(dataset_path, split)

            # Try to find CSV files (like MMLU)
            csv_files = glob.glob(os.path.join(split_dir, "*.csv"))
            if csv_files:
                logger.info(f"Found {len(csv_files)} CSV files in {split_dir}")
                for csv_file in csv_files:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if len(row) == 6:  # MMLU format
                                dataset_items.append({
                                    'input': row[0],
                                    'A': row[1],
                                    'B': row[2],
                                    'C': row[3],
                                    'D': row[4],
                                    'target': row[5],
                                    'source_file': os.path.basename(csv_file)
                                })
                            else:
                                # Generic CSV format
                                dataset_items.append(dict(enumerate(row)))

            # Try to find JSONL files (like ARC)
            jsonl_files = glob.glob(os.path.join(split_dir, "*.jsonl"))
            if jsonl_files:
                logger.info(f"Found {len(jsonl_files)} JSONL files in {split_dir}")
                for jsonl_file in jsonl_files:
                    with open(jsonl_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                dataset_items.append(json.loads(line))

            # Try to find JSON files
            json_files = glob.glob(os.path.join(split_dir, "*.json"))
            if json_files:
                logger.info(f"Found {len(json_files)} JSON files in {split_dir}")
                for json_file in json_files:
                    # Skip contamination annotation files
                    if 'contamination' in json_file.lower():
                        continue
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            dataset_items.extend(data)
                        elif isinstance(data, dict):
                            dataset_items.append(data)

            # If split_dir doesn't exist, try the main directory
            if not dataset_items:
                logger.info(f"Split directory {split_dir} not found or empty, trying main directory")

                # Try JSONL in main directory
                jsonl_file = os.path.join(dataset_path, f"{split}.jsonl")
                if os.path.exists(jsonl_file):
                    logger.info(f"Loading from {jsonl_file}")
                    with open(jsonl_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                dataset_items.append(json.loads(line))

                # Try JSON in main directory
                json_file = os.path.join(dataset_path, f"{split}.json")
                if os.path.exists(json_file):
                    logger.info(f"Loading from {json_file}")
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            dataset_items.extend(data)
                        elif isinstance(data, dict):
                            dataset_items.append(data)

        # If it's a single file
        elif os.path.isfile(dataset_path):
            logger.info(f"Loading from file: {dataset_path}")
            if dataset_path.endswith('.jsonl'):
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            dataset_items.append(json.loads(line))
            elif dataset_path.endswith('.json'):
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        dataset_items.extend(data)
                    elif isinstance(data, dict):
                        dataset_items.append(data)
            elif dataset_path.endswith('.csv'):
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    dataset_items.extend(list(reader))
        else:
            raise ValueError(f"Path {dataset_path} is neither a directory nor a file")

        if not dataset_items:
            raise ValueError(
                f"No data found in {dataset_path} for split '{split}'. "
                f"Please check if the split exists and contains data files."
            )

    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise ValueError(
            f"Could not load dataset '{dataset_name}'. "
            f"Error: {e}\n"
            "Please ensure the dataset name is correct and the dataset exists."
        )

    # Now we have dataset_items as a list
    total_samples = len(dataset_items)
    logger.info(f"Total samples loaded: {total_samples}")

    # Adjust sample size if dataset is smaller
    actual_sample_size = min(sample_size, total_samples)
    if actual_sample_size < sample_size:
        logger.warning(
            f"Requested {sample_size} samples, but dataset only has "
            f"{total_samples}. Returning all {actual_sample_size} samples."
        )

    # Set random seed for reproducibility
    if seed is not None:
        random.seed(seed)

    # Sample the dataset
    if shuffle:
        # Shuffle and take first N
        sampled_items = dataset_items.copy()
        random.shuffle(sampled_items)
        samples = sampled_items[:actual_sample_size]
    else:
        # Take first N samples without shuffling
        samples = dataset_items[:actual_sample_size]

    logger.info(f"Successfully sampled {len(samples)} items from dataset")

    return samples


def print_sample_summary(samples: List[Dict], max_display: int = 5):
    """
    Print a summary of the sampled data.

    Args:
        samples (List[Dict]): List of samples from get_dataset_sample()
        max_display (int): Maximum number of samples to display in detail.
            Defaults to 5.

    Examples:
        >>> samples = get_dataset_sample('opencompass/mmlu', sample_size=100)
        >>> print_sample_summary(samples, max_display=3)
    """
    if not samples:
        print("No samples to display.")
        return

    print(f"\n{'='*80}")
    print(f"DATASET SAMPLE SUMMARY")
    print(f"{'='*80}")
    print(f"Total samples: {len(samples)}")
    print(f"Sample keys: {list(samples[0].keys())}")
    print(f"\n{'='*80}")
    print(f"SAMPLE PREVIEW (showing first {min(max_display, len(samples))} items)")
    print(f"{'='*80}\n")

    for idx, sample in enumerate(samples[:max_display]):
        print(f"--- Sample {idx + 1} ---")
        for key, value in sample.items():
            # Truncate long values
            value_str = str(value)
            if len(value_str) > 200:
                value_str = value_str[:200] + "..."
            print(f"  {key}: {value_str}")
        print()


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        dataset_name = sys.argv[1]
        sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        split = sys.argv[3] if len(sys.argv) > 3 else 'test'
    else:
        # Default example
        print("Usage: python dataset_sampler.py <dataset_name> [sample_size] [split]")
        print("\nExample: python dataset_sampler.py opencompass/mmlu 100 test")
        print("\nRunning with default example (opencompass/mmlu)...")
        dataset_name = 'opencompass/mmlu'
        sample_size = 10
        split = 'test'

    try:
        samples = get_dataset_sample(
            dataset_name=dataset_name,
            sample_size=sample_size,
            split=split
        )
        print_sample_summary(samples, max_display=5)
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
