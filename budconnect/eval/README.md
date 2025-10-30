# Eval Module

The eval module builds `eval_manifest.json` by fetching data from OpenCompass APIs.

## Features

- **OpenCompass Integration**: Fetches traits and datasets from official APIs
- **Manifest Generation**: Creates standardized eval_manifest.json
- **Simple API**: Direct HTTP endpoint to trigger manifest building

## Architecture

```
budconnect/eval/
├── manifest_builder.py           # Core: Fetches from OpenCompass APIs & builds manifest
├── dataset_analyzer.py            # LLM-based question analysis
├── dataset_sampler.py             # Extracts sample questions from datasets
├── services.py                    # Business logic layer
├── routes.py                      # FastAPI endpoints
├── schemas.py                     # Pydantic validation models
├── models.py                      # Empty (no database models needed)
├── data_collector.py              # Generic data collector (not used currently)
├── build_manifest_standalone.py  # Standalone script (full-featured)
├── quick_build.py                 # Standalone script (minimal)
├── test_dataset_sampler.py        # Test script for dataset sampler
├── anlyticsprompt.txt             # LLM prompt template for analysis
├── data/                          # Output directory for generated manifests
│   ├── analysis/                  # Analysis results (when enabled)
│   └── *.json                     # Generated manifest files
└── example_config.json            # Example configuration
```

## Data Sources

The manifest is built from two OpenCompass API endpoints:

1. **Traits API**: `https://hub.opencompass.org.cn/gw/opencompass-be/api/v1/bench/listTopicDimensionTag`
   - Returns trait/dimension definitions
   - Transformed into the `traits` section of the manifest

2. **Datasets API**: `https://hub.opencompass.org.cn/gw/opencompass-be/api/v1/bench/listIndexCards`
   - Returns benchmark dataset information
   - Transformed into the `datasets.opencompass` section of the manifest

## Manifest Structure

```json
{
  "manifest_version": "3.0.0",
  "last_updated": "2025-10-08T12:00:00Z",
  "schema_version": "1.0",
  "repository": { ... },
  "version_info": { ... },
  "traits": {
    "version": "1.0.0",
    "count": 17,
    "definitions": [...]
  },
  "datasets": {
    "opencompass": {
      "version": "2.0.0",
      "count": 324,
      "datasets": [...]
    }
  }
}
```

## Output Location

All generated manifest files are saved to the directory configured in `EVAL_OUTPUT_DIR` (default: `budconnect/eval/data/`).

The output path is relative to your project root. For example, with the default configuration:
- Manifest files: `budconnect/eval/data/eval_manifest.json`
- Analysis results: `budconnect/eval/data/analysis/<dataset_id>_analysis.json`

You can customize the output directory by setting the `EVAL_OUTPUT_DIR` environment variable in your `.env` file.

## Usage

### Trigger via API

```bash
# Build with default settings
curl -X POST http://localhost:9088/eval/build \
  -H "Content-Type: application/json" \
  -d '{
    "output_filename": "eval_manifest.json"
  }'

# Build with custom sample size (overrides EVAL_SAMPLE_SIZE env var)
curl -X POST http://localhost:9088/eval/build \
  -H "Content-Type: application/json" \
  -d '{
    "output_filename": "eval_manifest.json",
    "sample_size": 100
  }'

# Build with analysis enabled and custom sample size
curl -X POST http://localhost:9088/eval/build \
  -H "Content-Type: application/json" \
  -d '{
    "output_filename": "eval_manifest_analyzed.json",
    "enable_analysis": true,
    "sample_size": 50
  }'
```

### Response

```json
{
  "status": "success",
  "output_file": "budconnect/eval/data/eval_manifest.json",
  "traits_count": 17,
  "datasets_count": 324,
  "last_updated": "2025-10-08T20:10:00Z"
}
```

### Check Status

```bash
curl http://localhost:9088/eval/
```

### Standalone Scripts (Without Running App)

You can build the manifest without starting the full application using the standalone scripts:

#### Option 1: Quick Build (Minimal Script)

```bash
# Edit quick_build.py to configure:
# - ENABLE_ANALYSIS = True/False
# - OUTPUT_FILE = "filename.json"
# - SAMPLE_SIZE = None (use env var) or number (e.g., 100)

python budconnect/eval/quick_build.py
```

#### Option 2: Full-Featured Script

```bash
# Build manifest without analysis (fast)
python budconnect/eval/build_manifest_standalone.py

# Build manifest with LLM analysis (analyzes sample questions per dataset)
python budconnect/eval/build_manifest_standalone.py --enable-analysis

# Custom output filename
python budconnect/eval/build_manifest_standalone.py --output custom_manifest.json

# Custom sample size (overrides EVAL_SAMPLE_SIZE env var)
python budconnect/eval/build_manifest_standalone.py --sample-size 100

# Combination: custom output, analysis, and sample size
python budconnect/eval/build_manifest_standalone.py \
  --output analyzed.json \
  --enable-analysis \
  --sample-size 50

# Enable debug logging
python budconnect/eval/build_manifest_standalone.py --debug

# Show help
python budconnect/eval/build_manifest_standalone.py --help
```

### LLM-Based Question Analysis

When `enable_analysis=True` (via API or standalone script), the system will:

1. Extract sample questions from each dataset (currently configured via `SAMPLE_SIZE` constant in `manifest_builder.py`)
2. Analyze each question using the LLM at `http://20.66.97.208/v1/chat/completions` (model: `qwen3-32b`)
3. Use the analytics prompt from `anlyticsprompt.txt` to extract metadata about:
   - Age of capability (min/avg/max)
   - Educational level required
   - Domain understanding needed
   - Language/cultural requirements
   - Task type
   - Skills required
   - Difficulty level
4. Save detailed analysis results to `budconnect/eval/data/analysis/<dataset_id>_analysis.json`
5. Add summary to manifest under each dataset's `analysis_file` and `analysis_summary` fields

**Note**: Analysis can take significant time as it processes multiple questions per dataset via LLM API calls.

## Configuration

The eval module can be configured via environment variables in the `.env` file:

### Eval Output Directory

```bash
# Directory path for eval manifest and analysis output files (relative to project root)
# Default: budconnect/eval/data
EVAL_OUTPUT_DIR=budconnect/eval/data

# Number of sample questions to extract from each dataset
# Default: 200
EVAL_SAMPLE_SIZE=200
```

This controls where manifest files and analysis results are saved, and how many sample questions to extract from each dataset.

**Sample Size Precedence:**
The sample size can be configured at multiple levels with the following precedence (highest to lowest):
1. **API/Function Argument** - Passed directly via `sample_size` parameter
2. **Environment Variable** - Set via `EVAL_SAMPLE_SIZE` in `.env`
3. **Default Value** - 200 (if not specified anywhere)

### Eval LLM Configuration (for Dataset Analysis)

```bash
# LLM endpoint for dataset question analysis
EVAL_LLM_ENDPOINT=http://20.66.97.208/v1/chat/completions

# Model name to use for analysis
EVAL_LLM_MODEL=qwen3-32b

# Timeout in seconds for LLM API calls (default: 120)
EVAL_LLM_TIMEOUT=120
```

These settings control the LLM used when `enable_analysis=True` is set during manifest building.

**Configuration in Code:**

The settings are defined in `budconnect/commons/config.py` and can be accessed via:

```python
from budconnect.commons.config import app_settings

# Access eval output directory and sample size
output_dir = app_settings.eval_output_dir  # e.g., "budconnect/eval/data"
sample_size = app_settings.eval_sample_size  # e.g., 200

# Access eval LLM configuration
endpoint = app_settings.eval_llm_endpoint
model = app_settings.eval_llm_model
timeout = app_settings.eval_llm_timeout
```

The `DatasetAnalyzer` class automatically uses these settings by default, but they can be overridden:

```python
from budconnect.eval.dataset_analyzer import DatasetAnalyzer

# Use default config from environment
analyzer = DatasetAnalyzer()

# Override specific settings
analyzer = DatasetAnalyzer(
    llm_endpoint="http://custom-endpoint.com/v1/chat/completions",
    model="custom-model",
    timeout=180
)
```

## Data Transformation

### Traits Transformation

API response from `listTopicDimensionTag`:
```json
[
  {"cn": "知识", "en": "Knowledge"},
  {"cn": "推理", "en": "Reasoning"}
]
```

Transformed to:
```json
{
  "name": "Knowledge",
  "description": "Evaluation trait: Knowledge",
  "icon": "icons/traits/knowledge.png"
}
```

### Datasets Transformation

API response from `listIndexCards` includes:
- `id`, `name`, `introduction`
- `dimensions`, `tags`, `language`
- `githubLink`, `paperLink`, etc.

Transformed to include:
- Standard metadata (format, language, domain)
- Trait mappings from dimensions
- Original API data preserved in `original_data` field
- Static fields where calculation is needed (size_mb, sample_count, etc.)

## Static vs Dynamic Data

### Dynamic (from API):
- Trait names and count
- Dataset names, descriptions
- Languages, domains, tags
- Links (GitHub, papers, official websites)
- Creator information

### Static (placeholders):
- `size_mb`: Set to 1.0 (needs actual file size calculation)
- `sample_count`: Set to 1000 (needs actual count from dataset)
- `checksum`: Placeholder values (needs actual file checksum)
- `estimated_input_tokens`: Set to 1000
- `estimated_output_tokens`: Set to 500
- Difficulty levels, language defaults

## Customization

### Modifying Transformations

Edit `manifest_builder.py` methods:
- `transform_traits()`: Customize trait transformation logic
- `transform_datasets()`: Customize dataset transformation logic

### Adding Calculated Fields

To calculate actual values instead of static placeholders:

```python
# In manifest_builder.py
def transform_datasets(self, api_datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
    for dataset in api_datasets:
        # Add actual calculation
        actual_size = self.calculate_dataset_size(dataset)
        dataset_entry["size_mb"] = actual_size
```

## Error Handling

- API failures don't crash the build - empty data arrays are used as fallback
- Failed API calls are logged with warnings
- All errors are logged to application logs
- Failed builds return error status with details

## Development

### Testing the Manifest Builder

```python
from budconnect.eval.manifest_builder import EvalManifestBuilder

builder = EvalManifestBuilder(output_path="cache/test_manifest.json")
result = await builder.run()
print(result)
```

## Notes

- The manifest builder will create parent directories if they don't exist
- UTF-8 encoding is preserved for multilingual content (Chinese/English)
- OpenCompass APIs may require specific headers or rate limiting considerations
- Build process is synchronous - the API waits for completion before returning
