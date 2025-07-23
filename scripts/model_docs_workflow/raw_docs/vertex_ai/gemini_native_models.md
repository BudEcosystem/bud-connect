# Vertex AI Native Gemini Models

## Overview

Vertex AI native Gemini models are Google's flagship AI models, designed specifically for enterprise deployment through Google Cloud infrastructure. These models offer advanced multimodal capabilities, integration with Google Cloud services, and enterprise-grade security features.

## Important 2025 Changes

### Gemini 1.5 Deprecation Notice
**Critical**: Starting April 29, 2025, Gemini 1.5 Pro and Gemini 1.5 Flash models are **not available** in projects that have no prior usage of these models, including new projects. Existing projects with usage history can continue using these models.

### Gemini 1.0 Extended Availability
Gemini 1.0 Pro 001 and Gemini 1.0 Pro Vision 001 availability extended from February 15, 2025 to April 9, 2025.

## Current Model Portfolio (2025)

### Gemini 2.5 Series (Latest - Generally Available)

#### Gemini 2.5 Pro
- **Model ID**: `gemini-2.5-pro`
- **Status**: Generally Available (GA)
- **Capabilities**: Most advanced Gemini model for complex reasoning
- **Key Features**:
  - Advanced multimodal understanding (text, images, video, audio)
  - Long context window support
  - Enhanced reasoning capabilities
  - Code generation and analysis
- **Use Cases**: Complex analysis, research, advanced coding, multimodal understanding
- **Endpoints**: 
  - `gemini-2.5-pro-preview-05-06` (serves GA version released 06-05)
  - `gemini-2.5-pro-preview-03-25` (serves GA version released 06-05)

#### Gemini 2.5 Flash
- **Model ID**: `gemini-2.5-flash`
- **Status**: Generally Available (GA)
- **Capabilities**: Balanced performance and speed
- **Key Features**:
  - Fast inference with high quality
  - Multimodal capabilities
  - Cost-effective for high-volume use
  - Good reasoning performance
- **Use Cases**: Production applications, high-volume processing, real-time applications
- **Endpoints**: `gemini-2.5-flash-preview-04-17` (serves GA version released 05-20)

#### Gemini 2.5 Flash-Lite
- **Model ID**: `gemini-2.5-flash-lite`
- **Status**: Preview
- **Capabilities**: Lightweight, ultra-fast model
- **Key Features**:
  - Optimized for speed and efficiency
  - Lower resource requirements
  - Reduced latency
- **Use Cases**: Real-time chat, lightweight applications, mobile deployment

### Gemini 2.0 Series

#### Gemini 2.0 Flash
- **Model ID**: `gemini-2.0-flash`
- **Status**: Generally Available (GA)
- **Capabilities**: Balanced flagship model
- **Key Features**:
  - Fine-tuning support (GA)
  - Multimodal understanding
  - Good performance-to-cost ratio
  - Image generation capabilities (preview)
- **Special Variants**:
  - `gemini-2.0-flash-preview-image-generation`: Image generation in public preview
- **Use Cases**: General-purpose applications, fine-tuned specialized models

#### Gemini 2.0 Flash-Lite
- **Model ID**: `gemini-2.0-flash-lite`
- **Status**: Generally Available (GA)
- **Capabilities**: Lightweight, efficient model
- **Key Features**:
  - Optimized for speed
  - Lower computational requirements
  - Cost-effective deployment
- **Use Cases**: High-throughput applications, cost-sensitive deployments

### Gemini 1.5 Series (Legacy - Restricted Availability)

> **⚠️ Important**: These models are not available for new projects as of April 29, 2025

#### Gemini 1.5 Pro
- **Model ID**: `gemini-1.5-pro`
- **Status**: Legacy (restricted to existing projects)
- **Capabilities**: Advanced reasoning and long context
- **Key Features**:
  - Up to 2M token context window
  - Multimodal understanding
  - Advanced reasoning capabilities
- **Availability**: Only for projects with prior usage history

#### Gemini 1.5 Flash
- **Model ID**: `gemini-1.5-flash`
- **Status**: Legacy (restricted to existing projects)
- **Capabilities**: Fast inference with good quality
- **Key Features**:
  - Optimized for speed
  - Multimodal capabilities
  - Long context support
- **Availability**: Only for projects with prior usage history

## Pricing Structure (2025)

### Token-Based Billing
- Billing based on input and output tokens
- Different rates for long context (>200K tokens)
- Only charged for successful requests (200 response codes)

### Token Calculation
- **Text**: ~4 characters = 1 token (including whitespace)
- **Images**: 1024x1024 image = 1,290 tokens
- **Video**: 258 tokens per second (at 1 frame/second sample rate)
- **Audio**: 25 tokens per second (Gemini 2.0 Flash Live API)

### Cost Optimization
- Use Flash models for cost-sensitive applications
- Consider Flash-Lite for ultra-high-volume use cases
- Monitor token usage with `countTokens` API

## Vertex AI-Specific Features

### Global vs Regional Endpoints

#### Global Endpoint
- **URL Format**: `https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/...`
- **Benefits**: 
  - Higher availability and reliability
  - Automatic load balancing across regions
  - Reduced resource exhausted (429) errors
- **Considerations**: Cannot control which region processes requests

#### Regional Endpoints
- **URL Format**: `https://{location}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{location}/...`
- **Benefits**:
  - Data residency control
  - Predictable processing location
  - Lower latency for specific regions
- **Use Cases**: Data sovereignty requirements, specific compliance needs

### Enterprise Integration

#### Authentication
- Google Cloud IAM integration
- Service account authentication
- Fine-grained access controls

#### Monitoring and Logging
- Request-response logging (30-day retention)
- Google Cloud Monitoring integration
- Audit trails and compliance logging

#### Security Features
- VPC Service Controls (VPC-SC)
- Customer-Managed Encryption Keys (CMEK)
- Data residency controls
- Access Transparency (AXT)

## Code Examples

### Basic Usage with Google Gen AI SDK

```python
from google import genai
from google.genai.types import HttpOptions
import os

# Set environment variables
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

# Initialize client
client = genai.Client(http_options=HttpOptions(api_version="v1"))

# Generate content with Gemini 2.5 Flash
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain the differences between machine learning and deep learning.",
)
print(response.text)
```

### Multimodal Example

```python
from google import genai
import base64

# Initialize client
client = genai.Client()

# Read and encode image
with open('image.jpg', 'rb') as image_file:
    image_data = base64.b64encode(image_file.read()).decode()

# Multimodal request
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=[
        {
            "role": "user",
            "parts": [
                {"text": "What do you see in this image?"},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                }
            ]
        }
    ]
)
print(response.text)
```

### Token Counting

```python
from google import genai

client = genai.Client()

# Count tokens before sending request
token_count = client.models.count_tokens(
    model="gemini-2.5-flash",
    contents="This is a sample prompt to count tokens."
)
print(f"Input tokens: {token_count.total_tokens}")
```

## Regional Availability

### Supported Regions (2025)
- **North America**: us-central1, us-east1, us-west1
- **Europe**: europe-west1, europe-west3, europe-west4
- **Asia Pacific**: asia-northeast1, asia-southeast1, asia-south1

### Region-Specific Considerations
- Some models may have different availability across regions
- Check current regional support in Google Cloud Console
- Consider data residency requirements for region selection

## Performance Optimization

### Model Selection Guidelines
- **Gemini 2.5 Pro**: Complex reasoning, research, advanced analysis
- **Gemini 2.5 Flash**: Production applications, balanced performance
- **Gemini 2.5 Flash-Lite**: Real-time applications, high-volume processing
- **Gemini 2.0 Flash**: Fine-tuning, specialized use cases

### Latency Optimization
- Use regional endpoints for lower latency
- Consider Flash-Lite for speed-critical applications
- Implement response streaming for better user experience

### Cost Optimization
- Monitor token usage patterns
- Use appropriate model size for use case
- Implement request batching where possible

## Fine-Tuning (Gemini 2.0 Flash)

### Capabilities
- Custom model training on your data
- Domain-specific optimization
- Performance improvement for specific tasks

### Process
1. Prepare training data in required format
2. Create fine-tuning job through Vertex AI
3. Monitor training progress
4. Deploy fine-tuned model
5. Evaluate performance improvements

### Use Cases
- Domain-specific language understanding
- Custom instruction following
- Specialized reasoning tasks

## Migration and Compatibility

### From Gemini 1.5 to 2.5
- Update model identifiers in API calls
- Test functionality with new models
- Validate performance and quality
- Update monitoring and alerting

### API Compatibility
- Maintain backward compatibility for most use cases
- New features available in latest models
- Consider gradual migration approach

## Troubleshooting Common Issues

### Model Availability Errors
- Check project eligibility for Gemini 1.5 models
- Verify regional availability
- Ensure proper model naming with versions

### Authentication Issues
- Verify Google Cloud credentials
- Check IAM permissions
- Ensure Vertex AI API is enabled

### Quota Limits
- Monitor quota usage in Google Cloud Console
- Request quota increases if needed
- Implement proper retry logic for 429 errors

## Future Roadmap

### Expected Developments
- New model versions and capabilities
- Enhanced multimodal features
- Improved fine-tuning options
- Additional enterprise features

### Recommendations
- Stay updated with Google Cloud announcements
- Plan for model migrations as new versions release
- Consider beta/preview features for early adoption
- Monitor deprecation timelines for legacy models

## Support Resources

### Documentation
- [Vertex AI Gemini Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/models)
- [Google Gen AI SDK Documentation](https://googleapis.github.io/python-genai/)
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing)

### Community
- Google Cloud Community forums
- Stack Overflow with `google-vertex-ai` tag
- Google Cloud Support channels

### Professional Support
- Google Cloud Support plans
- Technical Account Manager assistance
- Architecture guidance and best practices