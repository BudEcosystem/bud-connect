# Model Documentation Workflow

This document describes a scalable two-phase workflow for collecting and processing documentation for proprietary AI models. The workflow separates web searching (using Claude CLI) from information extraction (using API-based LLM processing).

## Overview

With lot of models in the TensorZero configuration(budconnect/seeders/data/tensorzero/tensorzero_v_0_1_0.json), processing all documentation at once would be time-consuming and require significant API credits. This workflow addresses these challenges by:

1. **Phase 1: Documentation Search** - Use Claude CLI to search and save raw documentation
2. **Phase 2: Information Extraction** - Process saved documentation with LLM-based extraction

## Directory Structure

```
scripts/model_docs_workflow/
├── MODEL_DOCS_WORKFLOW.md          # This documentation
├── raw_docs/                       # Raw documentation from web searches
│   ├── openai/                     # OpenAI model docs
│   │   ├── gpt-4.md
│   │   ├── gpt-3.5-turbo.md
│   │   └── ...
│   ├── anthropic/                  # Anthropic model docs
│   │   ├── claude-3-opus.md
│   │   └── ...
│   ├── gemini/                     # Google Gemini docs
│   ├── vertex_ai/                  # Vertex AI docs
│   ├── mistral/                    # Mistral AI docs
│   ├── deepseek/                   # DeepSeek docs
│   ├── xai/                        # xAI docs
│   ├── azure/                      # Azure OpenAI docs
│   └── bedrock/                    # AWS Bedrock docs
│
├── extracted_info/                 # Processed JSON output
│   ├── all_models.json            # Combined results
│   ├── openai/                    # Provider-specific results
│   └── ...
│
├── extract_from_saved_docs.py     # Extraction script
├── extraction_progress.json       # Progress tracking
└── extraction_errors.log          # Error logging
```

## Phase 1: Documentation Search (Using Claude CLI)

### Why Use Claude CLI?

- No API keys required for web searching
- Claude can search multiple sources and compile comprehensive documentation
- Interactive process allows for quality control
- Can save results directly to organized markdown files

### Basic Search Commands

1. **Search for a single model:**
```bash
# Example: Search for GPT-4 documentation
# In Claude, ask:
"Search for comprehensive documentation about OpenAI's GPT-4 model including specifications, capabilities, pricing, API details, and benchmarks. Save the results as markdown."

# Then save the response to:
scripts/model_docs_workflow/raw_docs/openai/gpt-4.md
```

2. **Batch search for multiple models:**
```bash
# In Claude, provide a list of models:
"Search for documentation for these OpenAI models:
- gpt-4
- gpt-3.5-turbo
- text-embedding-ada-002

For each model, find specifications, capabilities, pricing, and API details."
```

### Search Template

Use this template when searching for model documentation:

```
Search for comprehensive documentation about [PROVIDER] [MODEL_NAME] including:
- Model overview and description
- Technical specifications (parameters, context window, etc.)
- Capabilities and features
- Pricing information
- API usage details
- Performance benchmarks
- Use cases and applications
- Limitations and considerations

Format the results as structured markdown with clear sections.
```

### Organizing Raw Documentation

Save each model's documentation as a markdown file following this naming convention:

```
raw_docs/[provider]/[model_name].md
```

Examples:
- `raw_docs/openai/gpt-4.md`
- `raw_docs/anthropic/claude-3-opus-20240229.md`
- `raw_docs/mistral/mistral-large-latest.md`

### Tips for Effective Searching

1. **Group by Provider**: Search for multiple models from the same provider together
2. **Verify Information**: Cross-reference official documentation URLs
3. **Include Dates**: Note when the information was retrieved
4. **Comprehensive Coverage**: Ensure all key aspects are covered

## Phase 2: Information Extraction

### The Extraction Script

The `extract_from_saved_docs.py` script processes the saved markdown files and extracts structured information using the `model_info_extractor.py` tool.

### Features

- **Batch Processing**: Process multiple files efficiently
- **Progress Tracking**: Resume interrupted extractions
- **Provider Filtering**: Process specific providers
- **Error Handling**: Logs failures for retry
- **Multiple Output Formats**: Individual and combined JSON files

### Usage

1. **Extract all saved documentation:**
```bash
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_PERPLEXITY_API_KEY
```

2. **Extract specific provider:**
```bash
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_API_KEY \
  --provider openai
```

3. **Extract specific models:**
```bash
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_API_KEY \
  --models gpt-4 claude-3-opus-20240229
```

4. **Resume interrupted extraction:**
```bash
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_API_KEY \
  --resume
```

5. **Use different LLM provider:**
```bash
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_API_KEY \
  --llm-provider anthropic \
  --llm-model claude-3-sonnet-20240229
```

### Output Structure

The extraction produces:

```
extracted_info/
├── all_models.json                 # Combined results for all models
├── extraction_summary.json         # Summary statistics
├── openai/
│   ├── gpt-4.json                 # Individual model results
│   ├── gpt-3.5-turbo.json
│   └── provider_summary.json      # Provider-level summary
├── anthropic/
│   └── ...
└── ...
```

### Extracted Information

Each model's JSON contains:

- **description**: Comprehensive model description
- **use_cases**: List of recommended use cases
- **strengths**: Model advantages and capabilities
- **limitations**: Known limitations and constraints
- **model_evals**: Benchmark scores and evaluations
- **metadata**: Provider, dates, pricing info

## Complete Workflow Example

### Step 1: Identify Models to Process

```bash
# View all proprietary models
cat scripts/proprietary_models_output/summary.json

# Get models for a specific provider
cat scripts/proprietary_models_output/by_provider/openai/models.json | jq -r 'keys[]' | head -10
```

### Step 2: Search and Save Documentation

In Claude CLI:
```
# Search for OpenAI models
"I need to collect documentation for these OpenAI models:
- gpt-4
- gpt-4-turbo
- gpt-3.5-turbo
- text-embedding-ada-002
- whisper-1

Please search for comprehensive documentation for each model including specifications, pricing, capabilities, and API details. Format as structured markdown."

# Save each model's documentation to:
# scripts/model_docs_workflow/raw_docs/openai/[model_name].md
```

### Step 3: Extract Structured Information

```bash
# Extract all OpenAI models
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_API_KEY \
  --provider openai

# Check results
cat scripts/model_docs_workflow/extracted_info/openai/gpt-4.json | jq .
```

### Step 4: Generate Reports

```bash
# View extraction summary
cat scripts/model_docs_workflow/extracted_info/extraction_summary.json | jq .

# Combine with original model data
python scripts/combine_model_data.py \
  --tensorzero scripts/proprietary_models_output/proprietary_models.json \
  --extracted scripts/model_docs_workflow/extracted_info/all_models.json \
  --output scripts/model_docs_workflow/complete_model_catalog.json
```

## Best Practices

### For Search Phase

1. **Batch Similar Models**: Group models by provider or type
2. **Verify Sources**: Ensure documentation comes from official sources
3. **Consistent Formatting**: Use the same markdown structure for all docs
4. **Include Examples**: Save code examples and API usage patterns
5. **Note Versions**: Include model version information and dates

### For Extraction Phase

1. **Test First**: Run extraction on a few models before processing all
2. **Monitor Progress**: Check extraction_progress.json regularly
3. **Review Errors**: Check extraction_errors.log for failed extractions
4. **Validate Output**: Spot-check extracted JSON for quality
5. **Save API Credits**: Use cached results when possible

## Troubleshooting

### Common Issues

1. **Empty Extraction Results**
   - Check if the markdown file has content
   - Verify API key is valid
   - Check API rate limits

2. **Extraction Failures**
   - Review extraction_errors.log
   - Ensure markdown files are properly formatted
   - Check for special characters in model names

3. **Resume Not Working**
   - Ensure extraction_progress.json is not corrupted
   - Delete the file to start fresh if needed

### Error Recovery

```bash
# View error log
tail -50 scripts/model_docs_workflow/extraction_errors.log

# Retry failed extractions
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_API_KEY \
  --retry-failed

# Force re-extraction of specific models
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_API_KEY \
  --models gpt-4 --force
```

## Advanced Usage

### Custom Extraction Prompts

Modify the extraction behavior by editing `model_info_extractor.py` or passing custom parameters:

```bash
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_API_KEY \
  --extraction-focus "security,compliance,enterprise"
```

### Parallel Processing

For faster extraction with multiple API keys:

```bash
# Provider 1
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key KEY1 \
  --provider openai &

# Provider 2
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key KEY2 \
  --provider anthropic &
```

### Integration with Seeders

The extracted data can be integrated into the BudConnect seeders:

```bash
# Generate seeder-compatible format
python scripts/convert_to_seeder_format.py \
  --input scripts/model_docs_workflow/extracted_info/all_models.json \
  --output budconnect/seeders/data/model_descriptions.json
```

## Summary

This workflow enables efficient processing of hundreds of model documentations by:

1. Leveraging Claude's web search capabilities (no API needed)
2. Organizing documentation in a structured manner
3. Processing with LLM extraction only when needed
4. Supporting incremental and resumable operations
5. Producing structured data ready for integration

The separation of search and extraction phases provides flexibility, cost control, and the ability to iterate on either phase independently.