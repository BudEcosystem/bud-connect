# Together AI Documentation Index

This directory contains comprehensive documentation about Together AI's models, pricing, and API usage. The documentation is organized by model categories and includes detailed information about specifications, pricing, API examples, and best practices.

## Documentation Files

### 📋 Platform Overview
- **[00_together_ai_overview.md](./00_together_ai_overview.md)** - Complete platform introduction, infrastructure, and ecosystem overview

### 💰 Pricing and Tiers
- **[01_together_ai_pricing_tiers.md](./01_together_ai_pricing_tiers.md)** - Detailed pricing structure, tiers, and cost optimization strategies

### 🦙 Meta Llama Models
- **[02_meta_llama_models.md](./02_meta_llama_models.md)** - Comprehensive coverage of Llama 3.1, 3.2, 3.3, and Llama 4 variants

### 🚀 Qwen Models
- **[03_qwen_models.md](./03_qwen_models.md)** - Qwen2.5 series including 72B, 7B Turbo, Coder, and Vision models

### 🧠 DeepSeek-V3
- **[04_deepseek_v3.md](./04_deepseek_v3.md)** - DeepSeek-V3 model specifications, pricing, and performance characteristics

### 🎯 Mistral Models
- **[05_mistral_models.md](./05_mistral_models.md)** - Mixtral 8x7B and 8x22B models with MoE architecture details

### 🔍 Embedding Models
- **[06_embedding_models.md](./06_embedding_models.md)** - BAAI BGE models and other embedding solutions for RAG applications

## Quick Reference

### Model Categories by Use Case

| Use Case | Recommended Model | Documentation |
|----------|------------------|---------------|
| General Chat | Llama 3.3-70B Turbo | [Meta Llama Models](./02_meta_llama_models.md) |
| Code Generation | Qwen2.5-Coder-32B | [Qwen Models](./03_qwen_models.md) |
| Cost-Effective | Llama 3.1-8B Turbo | [Meta Llama Models](./02_meta_llama_models.md) |
| Complex Reasoning | DeepSeek-V3 | [DeepSeek-V3](./04_deepseek_v3.md) |
| Multilingual | Mixtral-8x7B | [Mistral Models](./05_mistral_models.md) |
| Vision Tasks | Llama 3.2-11B Vision | [Meta Llama Models](./02_meta_llama_models.md) |
| Embeddings/RAG | BAAI/bge-base-en-v1.5 | [Embedding Models](./06_embedding_models.md) |

### Pricing Quick Reference (per 1M tokens)

| Model Size | Price | Examples |
|------------|-------|----------|
| Up to 4B | $0.10 | Llama 3.2-3B |
| 4.1B - 8B | $0.20 | Llama 3.1-8B, Qwen2.5-7B |
| 8.1B - 21B | $0.30 | - |
| 21.1B - 41B | $0.80 | Qwen2.5-14B |
| 41.1B - 80B | $0.90 | Llama 3.1-70B |
| 80.1B - 110B | $1.80 | Llama 3.1-405B |
| MoE (up to 56B) | $0.60 | Mixtral-8x7B |
| MoE (56.1B-176B) | $1.20 | Mixtral-8x22B |
| DeepSeek-V3 | $1.25 | DeepSeek-V3-0324 |
| Embeddings | $0.005-$0.02 | BGE models |

## API Quick Start

### Python SDK
```python
from together import Together

client = Together(api_key="your_api_key")

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

### OpenAI Compatibility
```python
import openai

openai.api_base = "https://api.together.xyz/v1"
openai.api_key = "your_together_api_key"

response = openai.ChatCompletion.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Key Features Covered

### Platform Capabilities
- ✅ Serverless inference with automatic scaling
- ✅ 200+ open-source models available
- ✅ OpenAI-compatible API for easy migration
- ✅ Transparent token-based pricing
- ✅ Batch processing with 50% discounts
- ✅ Fine-tuning services
- ✅ Dedicated endpoints for enterprise

### Model Types
- ✅ **Chat Models**: Conversational AI and general purpose
- ✅ **Code Models**: Programming assistance and debugging
- ✅ **Vision Models**: Image understanding and multimodal tasks
- ✅ **Embedding Models**: Vector representations for RAG systems
- ✅ **Multilingual Models**: Support for 100+ languages
- ✅ **Mixture-of-Experts**: Efficient large-scale models

### Technical Details
- ✅ **Context Lengths**: Up to 131K tokens for most models
- ✅ **Quantization**: FP8 optimization for speed
- ✅ **Rate Limits**: Detailed quota information
- ✅ **Performance Optimization**: Best practices and tuning
- ✅ **Migration Guides**: From other providers to Together AI
- ✅ **Security**: Authentication and privacy controls

## Documentation Quality

Each documentation file includes:
- 📊 **Comprehensive Model Specifications**: Parameters, context length, pricing
- 💻 **API Usage Examples**: Python, JavaScript, and cURL examples
- ⚡ **Performance Characteristics**: Speed, quality, and optimization tips
- 🔄 **Migration Guides**: Easy transition from other providers
- 🎯 **Use Case Recommendations**: Best model selection for specific tasks
- 📈 **Cost Analysis**: Pricing comparisons and optimization strategies
- 🛠️ **Best Practices**: Implementation tips and troubleshooting

## Official Resources

- **Together AI Website**: https://www.together.ai/
- **API Documentation**: https://docs.together.ai/
- **Model Catalog**: https://www.together.ai/models
- **Pricing**: https://www.together.ai/pricing
- **GitHub**: Official repositories and tools
- **Discord**: Community support and discussions

## Updates and Maintenance

This documentation is based on information gathered in January 2025. For the most current information, please refer to the official Together AI documentation and pricing pages.

Last Updated: January 2025
Sources: Official Together AI documentation, pricing pages, and API references