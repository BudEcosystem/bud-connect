# Model Documentation Workflow

A streamlined three-phase workflow for collecting, extracting, and converting model documentation into seeder-ready JSON format for BudConnect.

## Quick Start

```bash
# Phase 1: Search and save documentation (using Claude CLI)
# Phase 2: Extract structured information
python scripts/model_docs_workflow/extract_from_saved_docs.py --api-key YOUR_API_KEY

# Phase 3: Convert to seeder format
python scripts/model_docs_workflow/create_model_details_json.py
```

## Overview

This workflow processes hundreds of proprietary AI model documentations by:
1. **Manual Documentation Search** - Using Claude CLI for comprehensive web searching (no API needed)
2. **Automated Information Extraction** - LLM-based extraction of structured data from saved docs
3. **Seeder JSON Creation** - Converting extracted data into BudConnect seeder format

## Directory Structure

```
scripts/
├── model_docs_workflow/
│   ├── README.md                    # This documentation
│   ├── QUICK_START.md              # Quick reference guide
│   ├── MODEL_DOCS_WORKFLOW.md      # Detailed workflow documentation
│   │
│   ├── raw_docs/                   # Phase 1: Raw markdown documentation
│   │   ├── openai/                 # Provider-specific directories
│   │   ├── anthropic/
│   │   ├── gemini/
│   │   └── ...
│   │
│   ├── extracted_info/             # Phase 2: Extracted JSON data
│   │   ├── all_models.json        # Combined results
│   │   ├── extraction_summary.json # Statistics
│   │   └── [provider]/            # Provider-specific results
│   │
│   ├── extract_from_saved_docs.py  # Main extraction script
│   ├── extraction_progress.json    # Progress tracking
│   └── extraction_errors.log       # Error logging
│
│   ├── model_info_extractor.py     # Core extraction logic
│   ├── create_model_details_json.py # Seeder conversion script
│   ├── validate_model_data.py      # Data validation and quality checks
│   └── process_claude_search_results.py # Alternative search processing

budconnect/seeders/data/
└── model_details.json             # Final output for seeders
```

## Phase 1: Documentation Search

### Using Claude CLI

Claude CLI provides comprehensive web search without requiring API keys:

```bash
# Search for a single model
"Search for comprehensive documentation about OpenAI's GPT-4 including specifications, capabilities, pricing, API details, and benchmarks. Save as markdown."

# Batch search for provider
"Search documentation for these OpenAI models: gpt-4, gpt-3.5-turbo, text-embedding-ada-002. Include specifications, pricing, and API details."
```

### Search Template

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

### Saving Documentation

Save files using this naming convention:
```
raw_docs/[provider]/[model_name].md
```

Examples:
- `raw_docs/openai/gpt-4.md`
- `raw_docs/anthropic/claude-3-opus-20240229.md`

## Phase 2: Information Extraction

### Basic Usage

```bash
# Extract all documentation
python scripts/model_docs_workflow/extract_from_saved_docs.py --api-key YOUR_KEY

# Extract specific provider
python scripts/model_docs_workflow/extract_from_saved_docs.py --api-key YOUR_KEY --provider openai

# Resume interrupted extraction
python scripts/model_docs_workflow/extract_from_saved_docs.py --api-key YOUR_KEY --resume
```

### Features

- **Batch Processing**: Efficiently process multiple files
- **Progress Tracking**: Automatic resume capability
- **Multiple LLM Providers**: Support for OpenAI, Anthropic, Perplexity
- **Error Recovery**: Automatic retry with exponential backoff
- **Provider Filtering**: Process specific providers or models
- **Data Validation**: Built-in quality checks and validation
- **Rate Limit Handling**: Intelligent retry on API limits

### Output Format

Each extracted model contains:
```json
{
  "model_info": {
    "description": "Comprehensive model description...",
    "use_cases": ["Visual question answering", "..."],
    "strengths": ["Supports multimodal inputs...", "..."],
    "limitations": ["Limited to specific formats...", "..."]
  },
  "model_evals": [
    {"name": "MMLU", "score": 69.8},
    {"name": "GSM8K", "score": 77.2}
  ]
}
```

## Phase 3: Seeder JSON Creation

### Convert to Seeder Format

```bash
python scripts/model_docs_workflow/create_model_details_json.py
```

This creates `budconnect/seeders/data/model_details.json` with format:
```json
{
  "openai/gpt-4": {
    "description": "...",
    "advantages": ["..."],
    "disadvantages": ["..."],
    "use_cases": ["..."],
    "evaluations": [{"name": "MMLU", "score": 86.4}]
  }
}
```

## Complete Example Workflow

### 1. Identify Models to Process

```bash
# View TensorZero configuration
cat budconnect/seeders/data/tensorzero/tensorzero_v_0_1_0.json | jq -r '.models | keys' | head -20
```

### 2. Search and Save Documentation

In Claude CLI:
```
"I need documentation for these OpenAI models:
- gpt-4
- gpt-4-turbo
- gpt-3.5-turbo

Search for specifications, pricing, capabilities, and API details. Format as markdown."
```

Save each model's output to `scripts/model_docs_workflow/raw_docs/openai/[model].md`

### 3. Extract Structured Information

```bash
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_API_KEY \
  --provider openai
```

### 4. Create Seeder JSON

```bash
python scripts/model_docs_workflow/create_model_details_json.py
```

### 5. Validate and Verify Results

```bash
# Validate extracted data
python scripts/model_docs_workflow/validate_model_data.py

# Save validation report
python scripts/model_docs_workflow/validate_model_data.py --output validation_report.json

# Check extraction summary
cat scripts/model_docs_workflow/extracted_info/extraction_summary.json | jq .

# Verify seeder file
cat budconnect/seeders/data/model_details.json | jq 'keys' | head -20
```

## Advanced Usage

### Parallel Processing

Process multiple providers simultaneously:
```bash
# Terminal 1
python extract_from_saved_docs.py --api-key KEY1 --provider openai &

# Terminal 2  
python extract_from_saved_docs.py --api-key KEY2 --provider anthropic &
```

### Custom LLM Models

Use specific models for extraction:
```bash
python extract_from_saved_docs.py \
  --api-key YOUR_KEY \
  --llm-provider anthropic \
  --llm-model claude-3-sonnet-20240229
```

### Error Recovery

```bash
# View errors
tail -50 scripts/model_docs_workflow/extraction_errors.log

# Retry failed extractions
python extract_from_saved_docs.py --api-key YOUR_KEY --retry-failed
```

## Best Practices

### Documentation Search
1. **Batch by Provider**: Group similar models together
2. **Verify Sources**: Ensure official documentation
3. **Include Dates**: Note when information was retrieved
4. **Save Examples**: Include code samples when available

### Extraction
1. **Test First**: Run on a few models before full batch
2. **Monitor Progress**: Check `extraction_progress.json`
3. **Validate Output**: Spot-check JSON quality
4. **Save API Credits**: Use resume feature

### Integration
1. **Regular Updates**: Re-run workflow for model updates
2. **Version Control**: Track changes in model_details.json
3. **Validation**: Ensure compatibility with seeders

## Troubleshooting

### Common Issues

**Empty Extraction Results**
- Verify markdown file has content
- Check API key validity
- Review rate limits

**Extraction Failures**
- Check `extraction_errors.log`
- Ensure proper markdown formatting
- Verify model name formatting

**Seeder Creation Issues**
- Ensure extraction completed successfully
- Check file paths are correct
- Verify JSON structure matches expected format

## Maintenance

### Adding New Providers

1. Create provider directory: `raw_docs/[new_provider]/`
2. Search and save model documentation
3. Run extraction for the provider
4. Verify in `model_details.json`

### Updating Existing Models

1. Re-search updated documentation
2. Run extraction with `--force` flag
3. Recreate seeder JSON
4. Review changes before committing

## See Also

- [MODEL_DOCS_WORKFLOW.md](MODEL_DOCS_WORKFLOW.md) - Detailed workflow documentation
- [QUICK_START.md](QUICK_START.md) - Quick reference guide
- [CLAUDE.md](/datadisk/ditto/bud-connect/CLAUDE.md) - Project documentation