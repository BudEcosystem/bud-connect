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

All generated manifest files are saved to: `budconnect/eval/data/`

The full path will be: `/home/accubits/PycharmProjects/bud-connect/budconnect/eval/data/eval_manifest.json`

## Usage

### Trigger via API

```bash
# Build with default filename (eval_manifest.json)
curl -X POST http://localhost:9088/eval/build \
  -H "Content-Type: application/json" \
  -d '{
    "output_filename": "eval_manifest.json"
  }'

# Or build with custom filename
curl -X POST http://localhost:9088/eval/build \
  -H "Content-Type: application/json" \
  -d '{
    "output_filename": "eval_manifest_v2.json"
  }'
```

### Response

```json
{
  "status": "success",
  "output_file": "/home/accubits/PycharmProjects/bud-connect/budconnect/eval/data/eval_manifest.json",
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

# With analysis and custom filename
python budconnect/eval/build_manifest_standalone.py --output analyzed.json --enable-analysis

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
