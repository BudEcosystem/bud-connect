# Vertex AI Models Documentation

This directory contains comprehensive documentation for Google Cloud Vertex AI models, focusing on the differences between Vertex AI and direct API access.

## Directory Structure

```
vertex_ai/
├── README.md                          # This file
├── anthropic_claude_models.md         # Claude models on Vertex AI
├── gemini_native_models.md           # Vertex AI native Gemini models
├── vertex_ai_vs_direct_api.md        # Key differences and enterprise features
├── authentication_setup.md           # SDK setup and authentication
├── regional_availability.md          # Regional endpoints and availability
└── enterprise_features.md            # VPC-SC, CMEK, and enterprise controls
```

## Key Documentation Areas

### 1. Anthropic Claude Models on Vertex AI
- Claude 4 series (Opus 4, Sonnet 4)
- Claude 3.7 Sonnet with extended thinking
- Claude 3.5 series (Haiku, Sonnet)
- Vertex AI-specific features and integration

### 2. Vertex AI Native Gemini Models
- Gemini 2.5 series (Pro, Flash)
- Gemini 2.0 series (Flash, Flash-Lite)
- Gemini 1.5 series (legacy models with deprecation notices)
- Model versioning and availability changes for 2025

### 3. Enterprise Features
- VPC Service Controls (VPC-SC)
- Customer-Managed Encryption Keys (CMEK)
- Data residency and compliance
- IAM integration
- MLOps tooling

### 4. Authentication and SDK
- Google Gen AI SDK (recommended as of 2025)
- Service account authentication
- Regional vs global endpoints
- Code examples and best practices

## Important Notes for 2025

- **SDK Migration**: Vertex AI SDK's generative AI modules are deprecated as of June 24, 2025. Use Google Gen AI SDK instead.
- **Gemini 1.5 Restrictions**: Starting April 29, 2025, Gemini 1.5 Pro and Flash are not available in new projects without prior usage.
- **New Models**: Claude Opus 4 and Sonnet 4 are now available with hybrid reasoning capabilities.

## Quick Start

For quick implementation examples, see `authentication_setup.md` for code samples and setup instructions.

## Enterprise vs Developer API

Vertex AI provides enterprise-grade features that are not available in direct APIs:
- Enhanced security controls
- Better quota management
- MLOps integration
- Compliance features
- Regional data residency

See `vertex_ai_vs_direct_api.md` for detailed comparisons.