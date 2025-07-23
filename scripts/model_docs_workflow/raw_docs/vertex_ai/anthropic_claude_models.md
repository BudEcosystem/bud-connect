# Anthropic Claude Models on Google Cloud Vertex AI

## Overview

Anthropic Claude models are available on Google Cloud Vertex AI as managed APIs, providing enterprise-grade access to Claude's capabilities without infrastructure management. Over 4,000 customers have started using Claude models on Vertex AI as of 2025.

## Available Models (2025)

### Claude 4 Series (Latest - May 2025)

#### Claude Opus 4
- **Model ID**: `claude-opus-4-20250514`
- **Capabilities**: Anthropic's most intelligent model, state-of-the-art for coding and agent capabilities
- **Key Features**:
  - Hybrid reasoning model with modes for instant responses and extended thinking
  - Excels at coding with sustained performance on complex, long-running tasks
  - Optimized for agentic search and agent workflows
- **Pricing**: $15/$75 per million tokens (input/output)
- **Context Window**: Large context support
- **Use Cases**: Complex coding tasks, agent workflows, sophisticated reasoning

#### Claude Sonnet 4
- **Model ID**: `claude-sonnet-4-20250514`
- **Capabilities**: Mid-size hybrid reasoning model balancing performance and cost
- **Key Features**:
  - Hybrid reasoning with instant and extended thinking modes
  - Optimized for high-volume use cases
  - Balance of intelligence and efficiency
- **Pricing**: $3/$15 per million tokens (input/output)
- **Use Cases**: High-volume applications, balanced reasoning tasks

### Claude 3.7 Series

#### Claude 3.7 Sonnet
- **Model ID**: `claude-3-7-sonnet@20250219`
- **Status**: Preview on Vertex AI
- **Capabilities**: First Claude model with extended thinking
- **Key Features**:
  - Extended thinking capability for complex problem solving
  - Step-by-step reasoning for sophisticated tasks
  - Anthropic's most intelligent model before Claude 4
- **Use Cases**: Complex reasoning, multi-step problem solving

### Claude 3.5 Series

#### Claude 3.5 Haiku
- **Model ID**: `claude-3-5-haiku@20241022`
- **Status**: Generally Available
- **Capabilities**: Fastest and most cost-effective Claude model
- **Key Features**:
  - Optimized for speed and affordability
  - Lightweight for high-throughput applications
  - Maintained quality at reduced cost
- **Use Cases**: High-volume text processing, speed-critical applications

#### Claude 3.5 Sonnet
- **Model ID**: `claude-3-5-sonnet@20241022`
- **Status**: Generally Available
- **Capabilities**: Balanced performance and capability
- **Key Features**:
  - Strong reasoning and analysis capabilities
  - Multimodal support (text and images)
  - Good balance of speed and intelligence
- **Use Cases**: General-purpose AI tasks, analysis, content generation

## Vertex AI-Specific Features

### Managed API Service
- No infrastructure provisioning or management required
- Automatic scaling and availability
- Enterprise-grade reliability and uptime

### Request-Response Logging
- 30-day request-response logging capability
- Track model usage and potential misuse
- Compliance and audit trail support

### Streaming Support
- Real-time response streaming
- Reduced perceived latency for end users
- Better user experience for interactive applications

### Model Versioning
- All Claude models must use versioned identifiers with @ symbol
- Example: `claude-3-7-sonnet@20250219`
- Guaranteed consistent behavior across deployments

## Integration and Setup

### Authentication
Claude models on Vertex AI use Google Cloud authentication:
- Service account credentials
- Google Cloud IAM integration
- Project-level access control

### API Compatibility
The Vertex API for Claude is nearly identical to Anthropic's Messages API with two key differences:
1. Model is specified in the Google Cloud endpoint URL
2. `anthropic_version` is passed in request body with value `vertex-2023-10-16`

### SDK Support
- Supported by Anthropic's official client SDKs
- Google Gen AI SDK compatibility
- Standard HTTP REST API access

## Endpoint Structure

### Regional Endpoints
```
https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/anthropic/models/{model_name}
```

### Global Endpoint
```
https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global/publishers/anthropic/models/{model_name}
```

## Quotas and Limits

### Regional Quotas
- Claude models have regional quotas
- Quotas apply at the GCP project level
- Can potentially be increased upon request

### Global Quotas
- Available for models supporting global endpoints
- Higher availability and reliability
- Covers multiple regions automatically

## Code Example

```python
import anthropic
from google.auth import default

# Get default credentials
credentials, project = default()

# Initialize Anthropic client for Vertex AI
client = anthropic.AnthropicVertex(
    region="us-central1",
    project_id=project
)

# Make a request to Claude
message = client.messages.create(
    model="claude-3-7-sonnet@20250219",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ]
)

print(message.content)
```

## Enterprise Features

### Security Controls
- VPC Service Controls (VPC-SC) support
- Customer-Managed Encryption Keys (CMEK)
- Access Transparency (AXT)
- Data residency controls

### Compliance
- Enterprise-grade compliance features
- Audit logging and monitoring
- Data governance controls

### Integration
- Google Cloud IAM integration
- DevOps tools integration
- Monitoring and logging through Google Cloud

## Pricing Structure

### Token-Based Billing
- Charged per million tokens (input and output separately)
- Only charged for successful requests (200 response codes)
- Long context rates apply for queries over 200K tokens

### Current Pricing (2025)
- **Claude Opus 4**: $15 input / $75 output per million tokens
- **Claude Sonnet 4**: $3 input / $15 output per million tokens
- **Claude 3.7 Sonnet**: Pricing available in Vertex AI console
- **Claude 3.5 Haiku**: Most cost-effective option

## Best Practices

### Model Selection
- Use Claude Opus 4 for complex reasoning and coding tasks
- Use Claude Sonnet 4 for balanced performance and cost
- Use Claude 3.5 Haiku for high-volume, speed-critical applications

### Endpoint Selection
- Use regional endpoints for data residency requirements
- Use global endpoints for higher availability
- Consider latency requirements for endpoint selection

### Error Handling
- Implement proper retry logic for 429 (quota) errors
- Handle regional failures with global endpoint fallback
- Monitor quota usage to avoid service interruptions

## Migration from Direct API

### Key Differences
1. Authentication uses Google Cloud credentials instead of Anthropic API keys
2. Endpoint URLs use Google Cloud format
3. Additional enterprise features available
4. Integration with Google Cloud ecosystem

### Migration Steps
1. Set up Google Cloud project and enable Vertex AI
2. Configure authentication (service account or user credentials)
3. Update endpoint URLs to Vertex AI format
4. Test with existing prompts and workflows
5. Implement enterprise features as needed

## Support and Documentation

### Official Resources
- [Google Cloud Vertex AI Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/claude)
- [Anthropic Vertex AI Documentation](https://docs.anthropic.com/en/api/claude-on-vertex-ai)
- [Model Garden - Claude](https://cloud.google.com/products/model-garden/claude)

### Getting Started
1. Navigate to Claude Opus 4 or Claude Sonnet 4 model card in Vertex AI Model Garden
2. Select "Enable" 
3. Follow the setup instructions
4. Start making API calls

## Limitations

### Vertex AI Agent Engine
- Data residency, CMEK, and AXT security controls not supported in Vertex AI Agent Engine specifically
- Standard Vertex AI Claude models support full enterprise features

### Regional Availability
- Requires regions that support Anthropic Claude models for regional endpoints
- Check current regional availability in Google Cloud Console

## Future Considerations

### Model Updates
- New Claude models typically released first on Anthropic's platform
- Vertex AI availability follows shortly after
- Monitor Anthropic and Google Cloud announcements for new releases

### Enterprise Feature Expansion
- Continued expansion of enterprise features
- Integration with additional Google Cloud services
- Enhanced monitoring and observability tools