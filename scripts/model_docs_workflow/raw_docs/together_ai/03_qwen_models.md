# Qwen Models on Together AI

## Overview

Together AI hosts the comprehensive Qwen model family developed by Alibaba Cloud's Qwen team. These powerful decoder-only models are available in multiple variants and sizes, offering excellent performance for various AI tasks at competitive pricing.

## Available Qwen Models

### Qwen 2.5 Series

#### Qwen2.5-72B Instruct Turbo
- **API String**: `Qwen/Qwen2.5-72B-Instruct-Turbo`
- **Parameters**: 72 billion
- **Context Length**: 32,768 tokens
- **Pricing**: $1.20 per 1M tokens
- **Deployment**: Serverless, On-Demand Dedicated, Monthly Reserved
- **Use Case**: High-performance tasks requiring advanced reasoning

#### Qwen2.5-7B Instruct Turbo
- **API String**: `Qwen/Qwen2.5-7B-Instruct-Turbo`
- **Parameters**: 7 billion
- **Context Length**: 32,768 tokens
- **Pricing**: $0.30 per 1M tokens
- **Use Case**: Cost-effective solution for most applications

#### Qwen2.5-14B Instruct
- **API String**: `Qwen/Qwen2.5-14B-Instruct`
- **Parameters**: 14 billion
- **Pricing**: $0.80 per 1M tokens
- **Use Case**: Balanced performance and cost

### Specialized Qwen Models

#### Qwen2.5-Coder-32B Instruct
- **API String**: `Qwen/Qwen2.5-Coder-32B-Instruct`
- **Parameters**: 32 billion
- **Specialization**: Code generation and programming tasks
- **Pricing**: $0.80 per 1M tokens
- **Features**: 
  - Enhanced code understanding
  - Multi-language programming support
  - Code completion and debugging

#### Qwen QwQ-32B Preview
- **API String**: `Qwen/QwQ-32B-Preview`
- **Parameters**: 32 billion
- **Status**: Preview/experimental
- **Pricing**: $1.20 per 1M tokens
- **Features**: Advanced question-answering capabilities

### Next-Generation Models

#### Qwen 3-235B A22B
- **API String**: `Qwen/Qwen3-235B-A22B`
- **Parameters**: 235 billion (22B active)
- **Architecture**: Mixture of Experts (MoE)
- **Pricing**: $0.20 input / $0.60 output per 1M tokens
- **Context Length**: Extended context support
- **Features**: 
  - Latest Qwen architecture
  - Efficient MoE design
  - Differential input/output pricing

### Multimodal Models

#### Qwen2.5-VL-72B Instruct
- **API String**: `Qwen/Qwen2.5-VL-72B-Instruct`
- **Parameters**: 72 billion
- **Modalities**: Text + Vision
- **Pricing**: $1.95 input / $8.00 output per 1M tokens
- **Context Length**: 32,768 tokens
- **Features**:
  - Image understanding and analysis
  - Visual question answering
  - Multi-modal reasoning

## API Usage Examples

### Basic Chat Completion
```python
from together import Together

client = Together(api_key="your_api_key")

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-72B-Instruct-Turbo",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Explain the concept of machine learning."}
    ],
    max_tokens=1000,
    temperature=0.7
)

print(response.choices[0].message.content)
```

### Code Generation with Qwen Coder
```python
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-Coder-32B-Instruct",
    messages=[
        {"role": "user", "content": "Write a Python function to implement binary search."}
    ],
    max_tokens=500,
    temperature=0.1  # Lower temperature for code generation
)

print(response.choices[0].message.content)
```

### Vision-Language Model Usage
```python
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-VL-72B-Instruct",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe what you see in this image and answer any questions about it."},
            {"type": "image_url", "image_url": {"url": "https://example.com/chart.png"}}
        ]
    }],
    max_tokens=1000
)
```

### JavaScript/TypeScript Usage
```javascript
import Together from 'together-ai';

const together = new Together({
    apiKey: process.env.TOGETHER_API_KEY
});

const response = await together.chat.completions.create({
    model: 'Qwen/Qwen2.5-7B-Instruct-Turbo',
    messages: [
        { role: 'user', content: 'Translate this to French: Hello, how are you?' }
    ],
    max_tokens: 100,
    temperature: 0.3
});

console.log(response.choices[0].message.content);
```

### cURL Example
```bash
curl -X POST https://api.together.xyz/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -d '{
    "model": "Qwen/Qwen2.5-72B-Instruct-Turbo",
    "messages": [
      {"role": "user", "content": "What are the benefits of renewable energy?"}
    ],
    "max_tokens": 500,
    "temperature": 0.7
  }'
```

## Performance Characteristics

### Turbo Variants Benefits
1. **Optimized Inference**: Faster response times compared to standard variants
2. **Better Throughput**: Higher tokens per second processing
3. **Cost Efficiency**: Improved price-performance ratio
4. **Reduced Latency**: Optimized for real-time applications

### Model Capabilities by Size

| Model | Parameters | Best Use Cases | Performance Level |
|-------|------------|---------------|------------------|
| Qwen2.5-7B | 7B | General chat, simple tasks | Good |
| Qwen2.5-14B | 14B | Balanced applications | Better |
| Qwen2.5-Coder-32B | 32B | Code generation | Specialized |
| Qwen2.5-72B | 72B | Complex reasoning | Excellent |
| Qwen3-235B | 235B (22B active) | Advanced tasks | Best |

## Pricing Analysis

### Cost Comparison (per 1M tokens)
- **Qwen2.5-7B Turbo**: $0.30 (most cost-effective)
- **Qwen2.5-14B**: $0.80 (balanced option)
- **Qwen2.5-Coder-32B**: $0.80 (specialized coding)
- **Qwen2.5-72B Turbo**: $1.20 (high performance)
- **Qwen3-235B**: $0.20 input / $0.60 output (MoE efficiency)
- **Qwen2.5-VL-72B**: $1.95 input / $8.00 output (multimodal premium)

### Volume Discounts
- **Enterprise Customers**: Volume pricing available
- **Batch Processing**: 50% discount on supported models
- **Dedicated Endpoints**: Per-minute pricing for guaranteed capacity

## Rate Limits and Quotas

### Free Tier
- **New Account Credit**: $1 to get started
- **Rate Limits**: Apply to initial usage
- **Model Access**: Limited to certain models

### Paid Tier Benefits
- **Higher Rate Limits**: Increased requests per minute
- **Priority Queue**: Faster processing
- **Full Model Access**: All Qwen variants available

## Performance Optimizations

### Best Practices
1. **Model Selection**: Choose appropriate size for task complexity
2. **Temperature Tuning**: Lower values (0.1-0.3) for factual tasks, higher (0.7-0.9) for creative tasks
3. **Context Management**: Optimize prompt length for cost efficiency
4. **Batch Processing**: Group similar requests when possible
5. **Caching**: Implement response caching for repeated queries

### Specialized Model Usage
- **Qwen Coder**: Use for programming tasks, code review, debugging
- **Qwen VL**: Leverage for image analysis, visual question answering
- **QwQ Preview**: Experiment with advanced Q&A capabilities

## Comparison with Direct Provider APIs

### Together AI Advantages
- **Simplified Integration**: OpenAI-compatible API
- **Managed Infrastructure**: No deployment complexity
- **Transparent Pricing**: Clear token-based costs
- **Multiple Variants**: Access to entire Qwen family
- **Immediate Access**: No waiting periods or approvals

### Direct Qwen/Alibaba Cloud Considerations
- **Regional Availability**: May be limited in some regions
- **Integration Complexity**: Different API standards
- **Billing Structure**: Different pricing models

## Migration Guide

### From OpenAI to Qwen
```python
# Minimal code changes required
client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key="your_together_api_key"
)

# Simply change the model name
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-72B-Instruct-Turbo",  # Instead of gpt-4
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Performance Migration Tips
1. **Start with Qwen2.5-7B**: Test basic functionality
2. **Scale Up**: Move to larger models as needed
3. **Benchmark**: Compare performance against current solution
4. **Cost Analysis**: Monitor token usage and costs

## Use Case Recommendations

### General Applications
- **Customer Support**: Qwen2.5-7B Turbo
- **Content Generation**: Qwen2.5-14B or 72B
- **Analysis & Research**: Qwen2.5-72B Turbo
- **Enterprise Solutions**: Qwen3-235B

### Specialized Applications
- **Software Development**: Qwen2.5-Coder-32B
- **Visual Analysis**: Qwen2.5-VL-72B
- **Advanced Q&A**: QwQ-32B Preview
- **Multilingual Tasks**: Any Qwen2.5 variant

## Official Resources

- **Model Family Page**: https://www.together.ai/qwen
- **Qwen2.5-72B**: https://www.together.ai/models/qwen-2-5
- **API Documentation**: https://docs.together.ai/docs/serverless-models
- **Pricing**: https://www.together.ai/pricing

## Support and Community

- **GitHub**: Qwen official repositories
- **Documentation**: Comprehensive model cards
- **Community**: Hugging Face discussions
- **Technical Support**: Together AI support channels