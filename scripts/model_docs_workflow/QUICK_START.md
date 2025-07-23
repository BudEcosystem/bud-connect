# Model Docs Workflow - Quick Start Guide

## Prerequisites

- Claude CLI access (for documentation search)
- API key for extraction (Perplexity, OpenAI, or Anthropic)
- Python 3.8+ with required packages

## Three-Step Process

### Step 1: Search Documentation (Claude CLI)

```bash
# In Claude, search for model documentation:
"Search for documentation about [PROVIDER] [MODEL] including specifications, 
pricing, capabilities, and benchmarks. Format as markdown."

# Save to: scripts/model_docs_workflow/raw_docs/[provider]/[model].md
```

### Step 2: Extract Information (API Required)

```bash
# Extract all saved docs
python scripts/model_docs_workflow/extract_from_saved_docs.py --api-key YOUR_KEY

# Extract specific provider
python scripts/model_docs_workflow/extract_from_saved_docs.py --api-key YOUR_KEY --provider openai

# Resume if interrupted
python scripts/model_docs_workflow/extract_from_saved_docs.py --api-key YOUR_KEY --resume
```

### Step 3: Create Seeder JSON

```bash
# Convert extracted data to seeder format
python scripts/model_docs_workflow/create_model_details_json.py

# Output: budconnect/seeders/data/model_details.json
```

## Common Commands

```bash
# Check progress
cat scripts/model_docs_workflow/extraction_progress.json | jq .

# View errors
tail scripts/model_docs_workflow/extraction_errors.log

# Retry failed extractions
python scripts/model_docs_workflow/extract_from_saved_docs.py --api-key YOUR_KEY --retry-failed

# Extract specific models
python scripts/model_docs_workflow/extract_from_saved_docs.py --api-key YOUR_KEY --models gpt-4 claude-3-opus

# Use different LLM provider
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_KEY \
  --llm-provider anthropic \
  --llm-model claude-3-sonnet-20240229
```

## Directory Structure

```
raw_docs/[provider]/[model].md     → Phase 1 output (manual)
extracted_info/[provider]/[model].json → Phase 2 output (automated)
model_details.json                  → Phase 3 output (final)
```

## Tips

1. **Batch Search**: Search multiple models from same provider together
2. **Save Progress**: Extraction automatically saves progress
3. **Check Output**: Review `extraction_summary.json` after extraction
4. **Validate**: Spot-check final `model_details.json` before use

## Example: Process OpenAI Models

```bash
# 1. In Claude: Search for GPT-4, GPT-3.5-turbo docs
# 2. Save to raw_docs/openai/gpt-4.md, etc.

# 3. Extract information
python scripts/model_docs_workflow/extract_from_saved_docs.py \
  --api-key YOUR_PERPLEXITY_KEY \
  --provider openai

# 4. Validate extracted data
python scripts/model_docs_workflow/validate_model_data.py

# 5. Create seeder JSON
python scripts/model_docs_workflow/create_model_details_json.py

# 6. Verify
cat budconnect/seeders/data/model_details.json | jq '."openai/gpt-4"'
```