#!/usr/bin/env python3
"""Standalone Model Info Extractor.

This script extracts model information from README/content similar to HuggingFaceModelInfo.
It can accept model descriptions as input and generates structured model info and evaluations.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Union


# Try to import json_repair, fallback to json if not available
try:
    from json_repair import repair_json
except ImportError:

    def repair_json(s):
        return s


# Pydantic for data validation
from pydantic import BaseModel


# Model Analysis Prompt - same as in the original codebase
MODEL_ANALYSIS_PROMPT = """
Your goal is to go through the given model description (MODEL DESCRIPTION) carefully and thoroughly to clearly define the description and advantages of the given model. Ensure that your assessment is easy to understand, factual & thorough. Follow the instructions given below carefully to create the final JSON.

description (key - description - String, Max 3-4 Sentences): Read the source document carefully and extract factual details about the model. Identify the model's name, developer, purpose, and key technical specifications (e.g., parameters, architecture, context length). List special features, target tasks, and any explicitly stated limitations. Only include language support, benchmarks, or performance claims if directly mentioned. Keep the description accurate, avoiding assumptions, and summarize the essential information in 2-5 sentences.
advantages (key - advantages [List of strings]): Read the model description and evals carefully to identify explicitly stated strengths and capabilities. Look for phrases like 'excels at,' 'strong in,' or specific improvements (e.g., larger context window). List each advantage as a complete statement with supporting details, using only facts from the source. For evals, note benchmarks, scores, and what they measure (e.g., GSM8K → math reasoning). Translate results into real-world skills, mentioning limitations where stated. Avoid assumptions, comparisons, or unsupported claims — rely strictly on the provided data.
disadvantages (key - disadvantages [List of strings]): Carefully read the model description and evals to identify explicitly stated limitations or weaknesses. Look for words like 'limitation,' 'drawback,' or 'weakness' and categorize them (e.g., technical limits, performance issues, safety concerns). In evals, flag low scores: As an example: GSM8K < 50 means poor math skills, MMLU < 60 suggests weak factual reasoning. List each disadvantage as a clear, standalone point with exact wording or paraphrased text — no assumptions or exaggerations. Only document what's directly provided, and avoid conclusions beyond the source data.
usecases (key: usecases [List of strings]): Read the model description and evals to find suitable use cases. Look for features, architecture details, and benchmark results. For example, a high score on HellaSwag (70) suggests strong natural language understanding for creative writing or content generation. A moderate MMLU score (50) indicates potential for general knowledge tasks, while a GSM8K score of 40 suggests some mathematical reasoning ability. List practical applications directly based on these strengths, without making assumptions beyond the data provided.
evals: (key evals (List of dictionaries)): Find any evals available in the description and extract them with their values. For example: MMLU: 50, GSM8K: 40, HellaSwag: 70, etc. format - {"name": "MMLU", "score": 50}. Ensure that score is a number and also ensure that the value is extracted appropriately for the given model based on the table structure.

Sample JSON Structure for one model is given below:
{
  "description": "Llama 3.2 11B Vision Instruct is a multimodal large language model developed by Meta...",
  "advantages": [
    "Supports multimodal inputs combining text and images...",
    "Optimized for visual reasoning and understanding tasks..."
  ],
  "disadvantages": [
    "Limited to specific image formats...",
    "Requires significant computational resources..."
  ],
  "usecases": [
    "Visual question answering",
    "Image captioning and description"
  ],
  "evals": [
    {"name": "MMLU", "score": 69.8},
    {"name": "GSM8K", "score": 77.2}
  ]
}

Format Output as a valid JSON. And the keys are - description, advantages, disadvantages, usecases, evals
"""


# Data Models
class PaperInfo(BaseModel):
    title: str
    authors: List[str]
    url: str


class ModelDerivatives(BaseModel):
    base_model: Optional[List[str]] = None
    is_finetune: Optional[bool] = None
    is_adapter: Optional[bool] = None
    is_quantization: Optional[bool] = None
    is_merge: Optional[bool] = None


class LLMConfig(BaseModel):
    num_layers: Optional[int] = None
    hidden_size: Optional[int] = None
    intermediate_size: Optional[int] = None
    context_length: Optional[int] = None
    vocab_size: Optional[int] = None
    torch_dtype: Optional[str] = None
    num_attention_heads: Optional[int] = None
    num_key_value_heads: Optional[int] = None
    rope_scaling: Optional[Dict[str, Any]] = None


class VisionConfig(BaseModel):
    num_layers: Optional[int] = None
    hidden_size: Optional[int] = None
    intermediate_size: Optional[int] = None
    torch_dtype: Optional[str] = None


class EmbeddingConfig(BaseModel):
    embedding_dimension: Optional[int] = None


class ModelArchitecture(BaseModel):
    class Config:
        protected_namespaces = ()

    type: Optional[str] = None
    family: Optional[str] = None
    num_params: Optional[int] = None
    model_weights_size: Optional[int] = None
    kv_cache_size: Optional[int] = None
    text_config: Optional[LLMConfig] = None
    vision_config: Optional[VisionConfig] = None
    embedding_config: Optional[EmbeddingConfig] = None


class LicenseInfo(BaseModel):
    id: Optional[str] = None
    license_id: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    faqs: Optional[List[Dict[str, Union[str, List[str]]]]] = None
    type: Optional[str] = None
    description: Optional[str] = None
    suitability: Optional[str] = None


class ModelInfo(BaseModel):
    class Config:
        protected_namespaces = ()

    author: Optional[str] = None
    description: Optional[str] = None
    uri: Optional[str] = None
    modality: Optional[str] = None
    tags: Optional[List[str]] = None
    tasks: Optional[List[str]] = None
    papers: Optional[List[PaperInfo]] = None
    github_url: Optional[str] = None
    provider_url: Optional[str] = None
    website_url: Optional[str] = None
    license: Optional[LicenseInfo] = None
    logo_url: Optional[str] = None
    use_cases: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    model_tree: Optional[ModelDerivatives] = None
    languages: Optional[List[str]] = None
    architecture: Optional[ModelArchitecture] = None


class ModelAnalysisResult(BaseModel):
    model_info: ModelInfo
    model_evals: List[Dict[str, Any]]


# LLM Inference Functions
def get_model_analysis_openai(content: str, api_key: str, model: str = "gpt-4") -> Dict[str, Any]:
    """Get model analysis using OpenAI API."""
    try:
        import openai

        client = openai.OpenAI(api_key=api_key, base_url="http://20.66.97.208/v1")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": MODEL_ANALYSIS_PROMPT},
                {"role": "user", "content": f"MODEL DESCRIPTION: {content}"},
            ],
            temperature=0.1,
        )

        response_text = response.choices[0].message.content
        return json.loads(repair_json(response_text))
    except Exception as e:
        print(f"Error calling OpenAI API: {e}", file=sys.stderr)
        return {}


def get_model_analysis_anthropic(
    content: str, api_key: str, model: str = "claude-3-sonnet-20240229"
) -> Dict[str, Any]:
    """Get model analysis using Anthropic API."""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0.1,
            system=MODEL_ANALYSIS_PROMPT,
            messages=[{"role": "user", "content": f"MODEL DESCRIPTION: {content}"}],
        )

        response_text = response.content[0].text
        return json.loads(repair_json(response_text))
    except Exception as e:
        print(f"Error calling Anthropic API: {e}", file=sys.stderr)
        return {}


def get_model_analysis_perplexity(
    content: str, api_key: str, model: str = "llama-3.1-sonar-small-128k-online"
) -> Dict[str, Any]:
    """Get model analysis using Perplexity API."""
    try:
        import requests

        url = "https://api.perplexity.ai/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": MODEL_ANALYSIS_PROMPT},
                {"role": "user", "content": f"MODEL DESCRIPTION: {content}"},
            ],
            "max_tokens": 4096,
            "temperature": 0.1,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        response_data = response.json()
        response_text = response_data["choices"][0]["message"]["content"]
        return json.loads(repair_json(response_text))
    except Exception as e:
        print(f"Error calling Perplexity API: {e}", file=sys.stderr)
        return {}


def extract_model_info(
    content: str, provider: str, api_key: str, model_name: Optional[str] = None
) -> ModelAnalysisResult:
    """Extract model information from the given content."""
    # Get model analysis
    if provider == "openai":
        model = model_name or "gpt-4"
        analysis = get_model_analysis_openai(content, api_key, model)
    elif provider == "anthropic":
        model = model_name or "claude-3-sonnet-20240229"
        analysis = get_model_analysis_anthropic(content, api_key, model)
    elif provider == "perplexity":
        model = model_name or "llama-3.1-sonar-small-128k-online"
        analysis = get_model_analysis_perplexity(content, api_key, model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    # Create ModelInfo object
    model_info = ModelInfo(
        description=analysis.get("description", ""),
        use_cases=analysis.get("usecases", []),
        strengths=analysis.get("advantages", []),
        limitations=analysis.get("disadvantages", []),
        # Other fields can be filled as needed
        tags=[],
        tasks=[],
        languages=[],
    )

    # Extract model evals
    model_evals = analysis.get("evals", [])

    return ModelAnalysisResult(model_info=model_info, model_evals=model_evals)


def read_input(input_source: str) -> str:
    """Read input from file or stdin."""
    if input_source == "-":
        # Read from stdin
        return sys.stdin.read()
    elif os.path.isfile(input_source):
        # Read from file
        with open(input_source, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Treat as direct text input
        return input_source


def main():
    parser = argparse.ArgumentParser(
        description="Extract model information from README/content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using OpenAI
  python standalone_model_info_extractor.py -p openai -k YOUR_API_KEY "Model description here"

  # Using Anthropic with file input
  python standalone_model_info_extractor.py -p anthropic -k YOUR_API_KEY model_readme.md

  # Using Perplexity with stdin
  cat model_description.txt | python standalone_model_info_extractor.py -p perplexity -k YOUR_API_KEY -

  # Output to file
  python standalone_model_info_extractor.py -p openai -k YOUR_API_KEY model.md -o model_info.json
        """,
    )

    parser.add_argument("input", help="Input source: file path, '-' for stdin, or direct text")

    parser.add_argument(
        "-p", "--provider", choices=["openai", "anthropic", "perplexity"], required=True, help="LLM provider to use"
    )

    parser.add_argument("-k", "--api-key", required=True, help="API key for the chosen provider")

    parser.add_argument("-m", "--model", help="Model name to use (optional, defaults to provider's default)")

    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")

    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")

    args = parser.parse_args()

    try:
        # Read input content
        content = read_input(args.input)

        if not content.strip():
            print("Error: Empty input content", file=sys.stderr)
            sys.exit(1)

        # Extract model information
        result = extract_model_info(content, args.provider, args.api_key, args.model)

        # Prepare output
        output = {"model_info": result.model_info.dict(exclude_none=True), "model_evals": result.model_evals}

        # Format JSON
        json_output = json.dumps(output, indent=2) if args.pretty else json.dumps(output)

        # Write output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_output)
            print(f"Output written to: {args.output}")
        else:
            print(json_output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
