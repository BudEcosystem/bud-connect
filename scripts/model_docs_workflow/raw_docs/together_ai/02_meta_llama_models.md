# Meta Llama Models on Together AI

## Overview

Together AI provides comprehensive support for Meta's Llama model family, including the latest Llama 3.1, 3.2, 3.3, and emerging Llama 4 variants. These models offer state-of-the-art performance for various applications including chat, code generation, and multimodal tasks.

## Llama 3.1 Models

### Llama 3.1 405B Instruct Turbo
- **API String**: `meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo`
- **Parameters**: 405 billion
- **Context Length**: 130,815 tokens
- **Quantization**: FP8
- **Use Case**: Largest and most capable model for complex reasoning tasks
- **Pricing Tier**: 80.1B - 110B ($1.80 per 1M tokens)

### Llama 3.1 70B Instruct Turbo
- **API String**: `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo`
- **Parameters**: 70 billion
- **Context Length**: 131,072 tokens
- **Quantization**: FP8
- **Pricing**: $0.88 per 1M tokens (Turbo variant)
- **Use Case**: Balanced performance and cost for most applications

### Llama 3.1 8B Instruct Turbo
- **API String**: `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`
- **Parameters**: 8 billion
- **Context Length**: 131,072 tokens
- **Quantization**: FP8
- **Pricing Tier**: 4.1B - 8B ($0.20 per 1M tokens)
- **Use Case**: Cost-effective option for simpler tasks

## Llama 3.2 Models

### Llama 3.2 90B Vision Instruct Turbo
- **API String**: `meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo`
- **Parameters**: 90 billion
- **Context Length**: 131,072 tokens
- **Multimodal**: Yes (text + vision)
- **Pricing Tier**: 80.1B - 110B ($1.80 per 1M tokens)
- **Use Case**: Advanced vision and text understanding

### Llama 3.2 11B Vision Instruct Turbo
- **API String**: `meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo`
- **Parameters**: 11 billion
- **Context Length**: 131,072 tokens
- **Multimodal**: Yes (text + vision)
- **Pricing Tier**: 8.1B - 21B ($0.30 per 1M tokens)
- **Use Case**: Cost-effective vision-language tasks

### Llama 3.2 3B Instruct Turbo
- **API String**: `meta-llama/Llama-3.2-3B-Instruct-Turbo`
- **Parameters**: 3 billion
- **Context Length**: 131,072 tokens
- **Quantization**: FP16
- **Pricing Tier**: Up to 4B ($0.10 per 1M tokens)
- **Use Case**: Lightweight applications and edge deployment

### Llama Vision Free
- **API String**: Various free tier models
- **Multimodal**: Yes
- **Pricing**: Free tier with rate limits
- **Use Case**: Testing and development

## Llama 3.3 Models

### Llama 3.3 70B Instruct Turbo
- **API String**: `meta-llama/Llama-3.3-70B-Instruct-Turbo`
- **Parameters**: 70 billion
- **Context Length**: 131,072 tokens
- **Quantization**: FP8
- **Status**: Recommended "to get started"
- **Pricing**: $0.88 per 1M tokens (Turbo variant)
- **Use Case**: Latest optimizations and improvements

## Llama 4 Models (Preview/Beta)

### Llama 4 Maverick (17Bx128E)
- **API String**: `meta-llama/Llama-4-Maverick-17Bx128E`
- **Architecture**: Mixture of Experts
- **Total Parameters**: ~2.2T (17B x 128 experts)
- **Context Length**: TBD
- **Status**: Preview/experimental
- **Pricing**: MoE tier (176.1B - 480B at $2.40 per 1M tokens)

## API Usage Examples

### Basic Chat Completion (Python)
```python
from together import Together

client = Together(api_key="your_api_key")

response = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    max_tokens=1000,
    temperature=0.7
)

print(response.choices[0].message.content)
```

### Vision Model Usage (Llama 3.2 Vision)
```python
response = client.chat.completions.create(
    model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
    }]
)
```

### Streaming Response
```python
stream = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Write a story about AI"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### cURL Example
```bash
curl -X POST https://api.together.xyz/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -d '{
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "max_tokens": 100
  }'
```

## Performance Characteristics

### Turbo Variants Benefits
1. **Optimized Inference**: Faster response times
2. **Better Throughput**: Higher tokens per second
3. **Cost Efficiency**: Better price-performance ratio
4. **Quantization**: FP8 quantization for most models
5. **Context Length**: Extended context windows (128K+ tokens)

### Model Recommendations by Use Case

| Use Case | Recommended Model | Reasoning |
|----------|------------------|-----------|
| Simple Chat | Llama 3.1 8B Instruct Turbo | Cost-effective, fast |
| Complex Reasoning | Llama 3.1 405B Instruct Turbo | Maximum capabilities |
| Vision Tasks | Llama 3.2 11B Vision Instruct Turbo | Multimodal, cost-effective |
| Production Apps | Llama 3.3 70B Instruct Turbo | Latest optimizations |
| Experimental | Llama 4 Maverick | Cutting-edge architecture |

## Rate Limits and Quotas

### Free Tier Limits
- **Rate Limits**: Apply to free models
- **Token Limits**: Daily and monthly caps
- **Concurrent Requests**: Limited for free tier

### Paid Tier Benefits
- **Higher Rate Limits**: Increased requests per minute
- **Priority Processing**: Faster queue processing
- **Extended Context**: Full context length access

## Performance Optimizations

### Best Practices
1. **Model Selection**: Choose appropriate model size for task complexity
2. **Context Management**: Optimize prompt length for cost efficiency
3. **Batch Processing**: Group requests when possible
4. **Caching**: Implement response caching for repeated queries
5. **Streaming**: Use streaming for real-time applications

### Quantization Benefits
- **FP8 Quantization**: Faster inference with minimal quality loss
- **Memory Efficiency**: Reduced memory requirements
- **Cost Savings**: Lower computational costs

## Comparison with Direct Meta APIs

### Together AI Advantages
- **No Waitlists**: Immediate access to latest models
- **Simplified Billing**: Token-based pricing
- **Infrastructure Management**: Fully managed service
- **OpenAI Compatibility**: Easy integration
- **Multiple Models**: Access to entire Llama family

### Direct Provider Considerations
- **Official Support**: Direct from Meta
- **Latest Features**: First access to new capabilities
- **Custom Deployments**: More deployment options

## Migration from Other Providers

### From OpenAI
```python
# Change base URL and model name
client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key="your_together_api_key"
)

# Use Llama model instead of GPT
response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Official Resources

- **Model Pages**: https://www.together.ai/models
- **API Documentation**: https://docs.together.ai/docs/serverless-models
- **Quickstart Guide**: https://docs.together.ai/docs/quickstart
- **Llama Family Overview**: https://www.together.ai/blog/llama-3-2-vision-stack

## Support and Community

- **GitHub**: Official Together AI repositories
- **Discord**: Community support
- **Documentation**: Comprehensive API docs
- **Blog**: Latest updates and tutorials