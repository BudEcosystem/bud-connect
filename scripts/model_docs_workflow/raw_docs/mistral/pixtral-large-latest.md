# Pixtral Large Latest

## Model Overview

Pixtral Large is a 124B open-weights multimodal model built on top of Mistral Large 2. It is the second model in Mistral AI's multimodal family and demonstrates frontier-level image understanding. The model combines a powerful 124-billion-parameter language model with a 1-billion-parameter vision encoder, enabling sophisticated understanding of documents, charts, and natural images while maintaining the leading text-only capabilities of Mistral Large 2.

## Technical Specifications

### Architecture
- **Total Parameters**: 124 billion (123B language model + 1B vision encoder)
- **Base Model**: Built on Mistral Large 2
- **Context Window**: 128,000 tokens
- **Image Capacity**: Up to 30 high-resolution images per input
- **Equivalent Reading**: 300-page book or extensive visual content

### Model Components
- **Language Model**: 123B parameters (from Mistral Large 2)
- **Vision Encoder**: 1B parameters
- **Architecture Type**: Multimodal transformer

## Capabilities and Features

### Vision Capabilities
- Document understanding and analysis
- Chart and graph interpretation
- Natural image comprehension
- Visual question answering
- OCR and text extraction from images
- Complex visual reasoning

### Multimodal Features
- Process up to 30 high-resolution images per request
- Seamless integration of text and visual inputs
- Maintains full text capabilities of Mistral Large 2
- Cross-modal reasoning and understanding

### API Limitations
- Maximum 8 images per request via API
- File size limit: 10MB per image
- Supports common image formats (JPEG, PNG, etc.)

## Pricing Information

### Licensing Options
- **Research Use**: Mistral Research License (MRL) - free for research and education
- **Commercial Use**: Mistral Commercial License required
- **API Access**: Standard Mistral API pricing applies

### API Pricing
- Available through Mistral's La Plateforme
- Pricing details on Mistral's official pricing page
- Pay-per-token model for API usage

## API Usage Details

### Model Identifier
- **API Name**: `pixtral-large-latest`
- **Self-deployment**: Available as Mistral Large 24.11 on HuggingFace

### Python Example
```python
from mistralai import Mistral
import os

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

# Single image example
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "What's in this image? Describe in detail."
            },
            {
                "type": "image_url",
                "image_url": "https://example.com/image.jpg"
            }
        ]
    }
]

chat_response = client.chat.complete(
    model="pixtral-large-latest",
    messages=messages
)
```

### Multiple Images Example
```python
# Process multiple images (up to 8 via API)
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Compare these two charts"},
            {"type": "image_url", "image_url": "https://example.com/chart1.png"},
            {"type": "image_url", "image_url": "https://example.com/chart2.png"}
        ]
    }
]

response = client.chat.complete(
    model="pixtral-large-latest",
    messages=messages
)
```

### Base64 Image Support
```python
import base64

# Load local image
with open("document.pdf", "rb") as img_file:
    img_data = base64.b64encode(img_file.read()).decode()

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Extract all text from this document"},
            {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{img_data}"
            }
        ]
    }
]
```

## Performance Benchmarks

### Vision Benchmarks
- **MathVista**: 69.4% (complex mathematical reasoning over visual data)
  - Outperforms all other models on this benchmark
- **MM-MT-Bench**: Outperforms Claude-3.5 Sonnet (new), Gemini-1.5 Pro, and GPT-4o (latest)

### Comparison with Other Models
- Superior mathematical reasoning on visual data
- Competitive with leading multimodal models
- Maintains Mistral Large 2's text performance
- Frontier-level image understanding capabilities

## Deployment Options

### API Access
- Mistral La Plateforme (primary)
- RESTful API with standard authentication
- SDK support for major programming languages

### Self-Deployment
- **Model Name**: Mistral Large 24.11
- **Platform**: HuggingFace
- **License Required**: 
  - MRL for research
  - Commercial license for production

### Hardware Requirements
- Significant GPU memory required (124B parameters)
- Recommended: Multiple high-end GPUs
- Cloud deployment often more practical

## Use Cases and Applications

### Document Processing
- PDF analysis and extraction
- Form understanding
- Contract review
- Report generation from visual data

### Data Analysis
- Chart and graph interpretation
- Dashboard analysis
- Visual data extraction
- Trend identification from visualizations

### Educational Applications
- Mathematical problem solving with diagrams
- Science diagram interpretation
- Educational content analysis
- Visual learning assistance

### Business Applications
- Invoice processing
- Receipt analysis
- Presentation understanding
- Visual quality control

## Limitations and Considerations

### API Constraints
- 8 image maximum per API request
- 10MB file size limit per image
- 30 images possible in self-hosted deployments

### Processing Considerations
- Large model size requires substantial resources
- Inference time increases with image count
- Balance between image resolution and processing speed

### Licensing Requirements
- Research use requires MRL acceptance
- Commercial use requires paid license
- Self-deployment needs license compliance

## Code Examples and Implementation Guides

### Document Analysis
```python
def analyze_document(image_path, question):
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_data}"}
            ]
        }
    ]
    
    response = client.chat.complete(
        model="pixtral-large-latest",
        messages=messages
    )
    return response.choices[0].message.content
```

### Batch Image Processing
```python
def process_image_batch(image_urls, instruction):
    content = [{"type": "text", "text": instruction}]
    
    # Add up to 8 images
    for url in image_urls[:8]:
        content.append({
            "type": "image_url",
            "image_url": url
        })
    
    messages = [{"role": "user", "content": content}]
    
    return client.chat.complete(
        model="pixtral-large-latest",
        messages=messages
    )
```

### Mathematical Reasoning
```python
# Solve visual math problems
math_problem = """
Analyze this geometry problem and provide a step-by-step solution.
Show all work and explain your reasoning.
"""

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": math_problem},
            {"type": "image_url", "image_url": "geometry_problem.png"}
        ]
    }
]

solution = client.chat.complete(
    model="pixtral-large-latest",
    messages=messages
)
```

## Additional Resources

- **Official Announcement**: https://mistral.ai/news/pixtral-large
- **Documentation**: https://docs.mistral.ai/capabilities/vision/
- **Model Page**: Available on HuggingFace as Mistral Large 24.11
- **API Reference**: https://docs.mistral.ai/api/
- **Licensing Information**: Contact Mistral AI for commercial licenses