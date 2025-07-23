#!/usr/bin/env python3
"""Process search results obtained through Claude's web tools."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# Model documentation collected via Claude's web search
MODEL_DOCS = {
    "gpt-4": """
# GPT-4 Model Documentation

Provider: OpenAI
Model Family: GPT-4

## Overview
GPT-4 is OpenAI's advanced language model, available in multiple variants including standard GPT-4, GPT-4 Turbo, and the latest GPT-4.1 series. The model family offers various context window sizes and capabilities.

## Specifications

### GPT-4 Standard
- Context Window: 8,192 tokens (8K)
- Max Output Tokens: 4,096 tokens
- Pricing: $0.03 per 1K input tokens, $0.06 per 1K output tokens
- Supports: Function calling, System messages, Tool choice, Prompt caching

### GPT-4 32K
- Context Window: 32,768 tokens (32K)
- Pricing: $0.06 per 1K input tokens, $0.12 per 1K output tokens

### GPT-4 Turbo
- Context Window: 128,000 tokens (128K)
- Max Output Tokens: 4,096 tokens
- Pricing: $0.01 per 1K input tokens, $0.03 per 1K output tokens
- Knowledge Cutoff: April 2023
- 3x cheaper input and 2x cheaper output than standard GPT-4

### GPT-4.1 Series (Latest)
- Context Window: Up to 1,000,000 tokens (1M)
- Max Output Tokens: 32,768 tokens
- Pricing: $0.002 per 1K input tokens, $0.008 per 1K output tokens
- Knowledge Cutoff: June 2024
- Supports: Vision, Web search, Parallel function calling, Response schema
- Performance: 87.4% on IFEval, 54.6% on SWE-bench Verified

## Capabilities
- Multimodal inputs (text and images)
- Advanced reasoning and problem-solving
- Code generation and debugging
- Long-context understanding
- Function calling and tool use
- JSON mode and structured outputs

## API Features
- Compatible with OpenAI API format
- Supports streaming responses
- Batch processing available
- Fine-tuning available for some variants

## Use Cases
- Complex reasoning tasks
- Code generation and analysis
- Document processing and summarization
- Conversational AI applications
- Research and analysis
- Creative writing and content generation
""",
    "claude-3-opus-20240229": """
# Claude 3 Opus Model Documentation

Provider: Anthropic
Model Family: Claude 3

## Overview
Claude 3 Opus is the most capable model in the Claude 3 family, designed for complex reasoning tasks. Released in March 2024, it exhibits near-human levels of comprehension and fluency on complex tasks.

## Specifications
- Context Window: 200,000 tokens (200K)
- Extended Context: Up to 1,000,000 tokens available for select customers
- Max Output Tokens: 4,096 tokens
- Pricing: $15 per million input tokens, $75 per million output tokens
- Knowledge Cutoff: August 2023

## Capabilities
- Vision: Process photos, charts, graphs, and technical diagrams
- Multilingual: Strong performance across multiple languages
- Code generation and analysis
- Complex reasoning and problem-solving
- Near-human comprehension on complex tasks
- Reduced hallucinations compared to Claude 2.1
- Fewer unnecessary refusals

## Performance Benchmarks
- MMLU (undergraduate knowledge): Leading performance
- GPQA (graduate reasoning): Top-tier results
- GSM8K (basic mathematics): Strong performance
- Twofold improvement in accuracy over Claude 2.1 on challenging questions

## API Access
- Available through Claude API in 159 countries
- Integrated with Amazon Bedrock
- Available on Google Vertex AI
- Enterprise and developer-friendly

## Key Features
- Sophisticated vision capabilities on par with leading models
- Superior long-context handling
- Enhanced accuracy with reduced hallucinations
- More nuanced understanding of edge cases
- Better at recognizing harmless prompts

## Use Cases
- Complex analysis and research
- Advanced code generation
- Professional writing and editing
- Technical documentation
- Multimodal data analysis
- Enterprise automation
""",
    "gemini-1.5-pro": """
# Gemini 1.5 Pro Model Documentation

Provider: Google (Vertex AI)
Model Family: Gemini 1.5

## Overview
Gemini 1.5 Pro is Google's advanced multimodal AI model with breakthrough long-context understanding capabilities. Released in 2024, it features one of the largest context windows available.

## Specifications
- Standard Context Window: 128,000 tokens
- Extended Context Window: 2,000,000 tokens (2M) - now generally available
- Research Context: Successfully tested up to 10,000,000 tokens
- Max Output Tokens: 8,192 tokens
- Pricing: $1.25 per million input tokens, $5.00 per million output tokens (up to 128K)
- Above 128K: $2.50 per million input tokens, $10.00 per million output tokens

## Processing Capabilities
- 1 hour of video
- 11 hours of audio
- 30,000+ lines of code
- 700,000+ words of text
- Multimodal: Text, images, video, and audio

## Key Features
- Context caching for cost reduction
- Code execution capabilities
- Comparable quality to Gemini 1.0 Ultra with less compute
- General availability with 2M context window
- API available through Google AI Studio and Vertex AI

## Advanced Capabilities
- Learn rare languages from context (e.g., Kalamang)
- Analyze entire books or codebases
- Process long videos and audio files
- Cross-modal reasoning
- Document analysis and summarization

## Performance
- State-of-the-art on long-context benchmarks
- Strong performance on reasoning tasks
- Excellent multimodal understanding
- Efficient processing of large documents

## API Access
- Google AI Studio (fastest way to build)
- Vertex AI (enterprise features)
- Available in multiple regions
- REST and gRPC APIs

## Important Note
Starting April 29, 2025, Gemini 1.5 Pro not available for new projects without prior usage.

## Use Cases
- Large document analysis
- Video understanding
- Code repository analysis
- Multimodal applications
- Long-form content generation
- Research and analysis
""",
    "mistral/mistral-large-latest": """
# Mistral Large Model Documentation

Provider: Mistral AI
Model Family: Mistral Large

## Overview
Mistral Large is Mistral AI's flagship model for complex reasoning tasks. The latest version (v2) was released on February 26, 2024, with improved reasoning and function calling capabilities.

## Specifications
- Context Window: 128,000 tokens (128K)
- Max Output Tokens: 4,096 tokens
- Pricing: $2.00 per million input tokens, $6.00 per million output tokens
- Version: Mistral Large (24.11) - latest with enhanced capabilities

## Capabilities
- Agent-centric design with built-in function calling
- JSON outputs support
- Native fluency in 5 languages: English, French, Spanish, German, Italian
- Superior programming and mathematical capabilities
- Tool calling and functions support
- Text-only model (no vision support)

## API Features
- Hosted on Mistral's infrastructure in Europe
- OpenAI-compatible API format
- La Plateforme access for all models
- Rate Limits: 5 requests/second, 2M tokens/minute, 10B tokens/month

## Performance
- Top-tier reasoning for high-complexity tasks
- Excels in programming and mathematical tasks
- Strong multilingual capabilities
- Best-in-class agentic capabilities

## API Access
- Available through La Plateforme (console.mistral.ai)
- REST API with comprehensive documentation
- European data hosting
- Enterprise-ready infrastructure

## Key Features
- Function calling for agent applications
- Structured JSON outputs
- Multilingual by design
- Optimized for complex reasoning
- Mathematical and coding excellence

## Use Cases
- Complex reasoning and analysis
- Multilingual applications
- Code generation and debugging
- Mathematical problem solving
- Agent-based systems
- Enterprise automation
""",
    "deepseek/deepseek-chat": """
# DeepSeek Chat Model Documentation

Provider: DeepSeek
Model Family: DeepSeek V3

## Overview
DeepSeek Chat points to DeepSeek-V3-0324, a strong Mixture-of-Experts (MoE) language model with 671B total parameters and 37B activated per token. Released in December 2024.

## Specifications
- Total Parameters: 671 billion
- Active Parameters: 37 billion per token
- Context Window: 128,000 tokens (128K)
- Max Input Tokens: 65,536 tokens
- Max Output Tokens: 8,192 tokens (default: 4,096)
- Pricing: $0.27 per million input tokens, $1.10 per million output tokens
- Cache Hit Pricing: $0.07 per million cached input tokens

## Architecture
- Mixture-of-Experts (MoE) design
- Multi-head Latent Attention (MLA)
- DeepSeekMoE architecture
- Efficient inference design

## Training
- Pre-trained on 14.8 trillion diverse tokens
- Supervised Fine-Tuning
- Reinforcement Learning stages
- Reasoning capabilities distilled from DeepSeek-R1

## API Features
- OpenAI-compatible API format
- Base URL: https://api.deepseek.com
- Supports: Function calling, JSON output, Chat completion
- Chat Prefix Completion (Beta)

## Performance
- Outperforms other open-source models
- Comparable to leading closed-source models
- Strong performance across all context lengths up to 128K
- Excellent reasoning capabilities

## Additional Models
- DeepSeek-Reasoner (R1): 64K context, specialized for reasoning
- DeepSeek-Coder-V2: 236B parameters, 128K context for coding

## Key Features
- Cost-effective training and inference
- Strong long-context performance
- OpenAI API compatibility
- Competitive with closed-source models

## Use Cases
- General conversation and chat
- Code generation and analysis
- Long-document processing
- Complex reasoning tasks
- Cost-effective AI applications
""",
}


def extract_model_info(model_name: str, content: str, api_key: str) -> dict:
    """Extract structured information from model documentation."""
    script_dir = Path(__file__).parent
    extractor_script = script_dir / "model_info_extractor.py"

    # Save content to temporary file
    temp_file = script_dir / f"temp_{model_name.replace('/', '_')}.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        # Run the extractor script
        cmd = [
            sys.executable,
            str(extractor_script),
            str(temp_file),
            "-p",
            "openai",
            "-k",
            api_key,
            "-m",
            "qwen3-32b",
            "--pretty",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error extracting {model_name}: {result.stderr}")
            return None

    finally:
        # Clean up temp file
        temp_file.unlink(missing_ok=True)


def main():
    # Check for API key
    if len(sys.argv) < 2:
        print("Usage: python process_claude_search_results.py <API_KEY>")
        sys.exit(1)

    api_key = sys.argv[1]

    # Output directory
    output_dir = Path(__file__).parent / "claude_tools_output"
    output_dir.mkdir(exist_ok=True)

    # Process each model
    results = {}

    print("Processing 5 proprietary models with documentation from Claude's web search...\n")

    for model_name, doc_content in MODEL_DOCS.items():
        print(f"Processing {model_name}...")

        # Extract structured information
        model_info = extract_model_info(model_name, doc_content, api_key)

        if model_info:
            # Get provider from our data
            provider_map = {
                "gpt-4": "openai",
                "claude-3-opus-20240229": "anthropic",
                "gemini-1.5-pro": "vertex_ai-gemini-models",
                "mistral/mistral-large-latest": "mistral",
                "deepseek/deepseek-chat": "deepseek",
            }

            results[model_name] = {
                "provider": provider_map.get(model_name, "unknown"),
                "search_date": datetime.now().isoformat(),
                **model_info,
            }
            print("  ✓ Successfully extracted information")
        else:
            print("  ✗ Failed to extract information")

    # Save results
    output_file = output_dir / "claude_fetched_models.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Save individual files
    models_dir = output_dir / "models"
    models_dir.mkdir(exist_ok=True)

    for model_name, info in results.items():
        safe_name = model_name.replace("/", "_")
        model_file = models_dir / f"{safe_name}.json"
        with open(model_file, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)

    # Create report
    report_file = output_dir / "claude_fetch_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("Claude Web Search Model Documentation Report\n")
        f.write("==========================================\n\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Models Processed: {len(results)}\n\n")

        for model_name, info in results.items():
            f.write(f"\n{model_name}\n")
            f.write("-" * len(model_name) + "\n")
            if info.get("model_info"):
                f.write(f"✓ Description: {info['model_info'].get('description', 'N/A')[:100]}...\n")
                f.write(f"✓ Advantages: {len(info['model_info'].get('strengths', []))} found\n")
                f.write(f"✓ Use Cases: {len(info['model_info'].get('use_cases', []))} found\n")
            if info.get("model_evals"):
                f.write(f"✓ Evaluations: {len(info['model_evals'])} benchmarks\n")

    print(f"\n✓ Results saved to: {output_file}")
    print(f"✓ Report saved to: {report_file}")
    print(f"✓ Individual models in: {models_dir}")


if __name__ == "__main__":
    main()
