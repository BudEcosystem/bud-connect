# Mistral Small

## Model Overview

Mistral Small is a versatile model designed for various tasks such as programming, mathematical reasoning, document understanding, and dialogue. The latest versions (Mistral Small 3.1 and 3.2) feature multimodal capabilities and significantly expanded context windows. With 24 billion parameters, this model achieves top-tier capabilities in both text and vision tasks.

## Technical Specifications

### Model Parameters
- **Parameters**: 24 billion (24B)
- **Architecture**: Transformer-based dense decoder-only autoregressive LLM
- **License**: Apache 2.0 (open source)

### Context Window
- **Original Mistral Small**: 32,000 tokens
- **Mistral Small 3.1 (25.03)**: Up to 128,000 tokens
- **Mistral Small 3.2**: 128,000 tokens

### Model Versions
- **Mistral Small 3.2** (Latest - June 2025): `mistralai/Mistral-Small-3.2-24B-Instruct-2506`
- **Mistral Small 3.1** (March 2025): `mistralai/Mistral-Small-3.1-24B-Instruct-2503`
- **Mistral Small 3** (2025): Initial multimodal release

## Capabilities and Features

### Multimodal Capabilities
- Vision understanding capabilities added in Mistral Small 3.1
- Can analyze images and provide insights based on visual content
- Processes both text and images in a single context
- Maintains strong text performance while adding vision features

### Core Capabilities
- Programming and code generation
- Mathematical reasoning
- Document understanding and analysis
- Dialogue and conversational AI
- Image processing and visual inspection
- Object detection and recognition

## Pricing Information

### API Pricing
- **Input**: $0.0002 per 1,000 tokens
- **Output**: $0.0006 per 1,000 tokens
- **Maximum Output**: Up to 4,096 tokens per generation

## API Usage Details

### Model Identifiers
- **API Name**: `mistral-small` or `mistral-small-latest`
- **Specific Versions**: 
  - `mistral-small-3.2` (latest)
  - `mistral-small-3.1`

### API Example
```python
import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

# Text-only example
response = client.chat.complete(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)

# Multimodal example (3.1+)
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": "https://example.com/image.jpg"}
        ]
    }
]

response = client.chat.complete(
    model="mistral-small-latest",
    messages=messages
)
```

## Performance Benchmarks

### Mistral Small 3.2 (Latest)
- **MMLU**: 81% 
- **HumanEval Plus**: 92.90% (up from 88.99% in 3.1)
- **MBPP Pass@5**: 78.33% (up from 74.63% in 3.1)
- **SimpleQA**: Significant improvements
- **Internal Accuracy**: 84.78% (up from 82.75% in 3.1)
- **Infinite Generation Rate**: 1.29% (down from 2.11% in 3.1)
- **Output Speed**: 150 tokens/second

### Performance Comparisons
- Outperforms Gemma 3 and GPT-4o Mini
- Competitive with much larger models while being more efficient
- Nearly 2× reduction in infinite generation errors from 3.1 to 3.2

## Deployment Options

### Cloud Platforms
- Mistral La Plateforme (official API)
- Google Cloud Vertex AI
- NVIDIA NIM
- Microsoft Azure AI Foundry
- Hugging Face

### Local Deployment
- Can run on a single RTX 4090 when quantized
- Fits in 32GB RAM MacBook when quantized
- Requires ~55 GB GPU RAM in bf16/fp16 for full precision
- Exceptionally "knowledge-dense" for its size

### Installation
```bash
# For local deployment
pip install transformers torch

# For API usage
pip install mistralai
```

## Use Cases and Applications

### Enterprise Applications
- Document verification and analysis
- Visual inspection for quality control
- Image-based customer support
- Multimodal content generation
- On-device image processing

### Developer Applications
- Code generation and review
- API documentation creation
- Test case generation
- Bug detection and analysis
- Code translation between languages

### General Applications
- Educational assistance
- Content creation
- Data analysis
- Research support
- General-purpose AI assistance

## Limitations and Considerations

### Technical Requirements
- Significant GPU memory for full precision deployment
- Quantization recommended for consumer hardware
- API rate limits apply for cloud usage

### Model Improvements (3.1 to 3.2)
- Better instruction following
- Improved output stability
- Enhanced function calling robustness
- Reduced tendency for infinite generations

## Code Examples and Implementation Guides

### Basic Text Generation
```python
prompt = "Write a Python function to calculate factorial"
response = client.chat.complete(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": prompt}]
)
```

### Vision Analysis (3.1+)
```python
# Analyze a local image
import base64

with open("image.jpg", "rb") as img_file:
    img_data = base64.b64encode(img_file.read()).decode()

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image in detail"},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_data}"}
        ]
    }
]

response = client.chat.complete(
    model="mistral-small-latest",
    messages=messages
)
```

### Function Calling
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.complete(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools
)
```

## Additional Resources

- **Official Documentation**: https://docs.mistral.ai/
- **Model Cards on Hugging Face**: 
  - https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506
  - https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503
- **API Reference**: https://docs.mistral.ai/api/
- **Mistral La Plateforme**: https://console.mistral.ai/