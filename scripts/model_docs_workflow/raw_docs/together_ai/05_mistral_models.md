# Mistral Models on Together AI

## Overview

Together AI provides access to Mistral AI's family of models, including the powerful Mixtral Mixture-of-Experts models. These models offer excellent performance for various applications while maintaining competitive pricing and fast inference speeds.

## Available Mistral Models

### Mixtral-8x7B Instruct
- **API String**: `mistralai/Mixtral-8x7B-Instruct-v0.1`
- **Architecture**: Mixture of Experts (8 experts, 7B each)
- **Total Parameters**: ~56B (8 × 7B experts)
- **Active Parameters**: ~13B per token
- **Context Length**: 32,768 tokens
- **Pricing**: $0.60 per 1M tokens (unified input/output)
- **Languages**: English, French, Italian, German, Spanish

### Mixtral-8x22B Instruct
- **API String**: `mistralai/Mixtral-8x22B-Instruct-v0.1`
- **Architecture**: Mixture of Experts (8 experts, 22B each)
- **Total Parameters**: ~176B (8 × 22B experts)
- **Active Parameters**: ~39B per token
- **Context Length**: 65,536 tokens
- **Pricing**: $1.20 per 1M tokens
- **Enhanced Capabilities**: Larger expert size for better performance

### DiscoLM-Mixtral-8x7B-v2
- **API String**: `DiscoResearch/DiscoLM-mixtral-8x7b-v2`
- **Architecture**: Fine-tuned Mixtral variant
- **Specialization**: Enhanced conversational abilities
- **Context Length**: 32,768 tokens
- **Pricing**: $0.60 per 1M tokens

## Pricing Analysis

### Cost Comparison (per 1M tokens)
- **Mixtral-8x7B**: $0.60 (both input and output)
- **Mixtral-8x22B**: $1.20 (both input and output)
- **Batch Processing**: 50% discount available for supported models

### Competitive Pricing
Together AI offers competitive rates compared to other providers:
- **Mistral AI Direct**: $0.60 input / $1.80 output
- **Together AI**: $0.60 input / $0.60 output
- **Fireworks AI**: $0.40 input / $1.60 output
- **Together AI Advantage**: Unified pricing for input/output tokens

## Performance Characteristics

### Mixtral-8x7B Features
- **High Throughput**: Up to 100+ tokens per second
- **Code Generation**: Strong programming capabilities
- **Multilingual**: Native support for 5 languages
- **Context Handling**: 32K token context window
- **MT-Bench Score**: 8.3 (instruction-following variant)

### Mixtral-8x22B Enhancements
- **Extended Context**: 65K token support
- **Improved Reasoning**: Larger experts for complex tasks
- **Better Performance**: Enhanced capabilities across all tasks
- **Advanced Applications**: Suitable for enterprise workloads

## API Usage Examples

### Basic Chat Completion (Python)
```python
from together import Together

client = Together(api_key="your_api_key")

response = client.chat.completions.create(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant fluent in multiple languages."},
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    max_tokens=1000,
    temperature=0.7
)

print(response.choices[0].message.content)
```

### Code Generation
```python
response = client.chat.completions.create(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    messages=[
        {"role": "user", "content": "Write a Python function to implement a hash table with collision handling using chaining."}
    ],
    max_tokens=800,
    temperature=0.2  # Lower temperature for more deterministic code
)

print(response.choices[0].message.content)
```

### Multilingual Task
```python
response = client.chat.completions.create(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    messages=[
        {"role": "user", "content": "Translate this English text to French and then provide a summary in Spanish: 'The advancement of artificial intelligence has revolutionized many industries.'"}
    ],
    max_tokens=500,
    temperature=0.5
)
```

### Long Context Processing (Mixtral-8x22B)
```python
response = client.chat.completions.create(
    model="mistralai/Mixtral-8x22B-Instruct-v0.1",
    messages=[
        {"role": "user", "content": f"Analyze this lengthy document and provide key insights:\n\n{long_document}"}
    ],
    max_tokens=1500,
    temperature=0.6
)
```

### Streaming Response
```python
stream = client.chat.completions.create(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    messages=[
        {"role": "user", "content": "Write a comprehensive guide to machine learning algorithms."}
    ],
    stream=True,
    max_tokens=2000
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### JavaScript/TypeScript Usage
```javascript
import Together from 'together-ai';

const together = new Together({
    apiKey: process.env.TOGETHER_API_KEY
});

const response = await together.chat.completions.create({
    model: 'mistralai/Mixtral-8x7B-Instruct-v0.1',
    messages: [
        { role: 'user', content: 'Create a React component for a responsive navigation bar.' }
    ],
    max_tokens: 1000,
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
    "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "messages": [
      {"role": "user", "content": "What are the benefits of using mixture of experts models?"}
    ],
    "max_tokens": 600,
    "temperature": 0.7
  }'
```

## Rate Limits and Quotas

### Free Tier
- **Starting Credit**: $1 for new accounts
- **Rate Limits**: Standard limitations apply
- **Model Access**: Available for testing and evaluation

### Production Tier
- **Higher Limits**: Increased requests per minute
- **Priority Processing**: Faster inference
- **Batch Support**: Access to discounted batch processing

## Advanced Features

### Mixture of Experts Benefits
1. **Efficiency**: Only a subset of parameters active per token
2. **Scalability**: Large model capacity with reasonable compute cost
3. **Specialization**: Different experts can specialize in different domains
4. **Performance**: Better performance per compute than dense models

### Language Support
- **Native Languages**: English, French, Italian, German, Spanish
- **Code Languages**: Python, JavaScript, Java, C++, and more
- **Translation**: Between supported languages
- **Cultural Context**: Understanding of regional variations

## Use Case Recommendations

### Ideal Applications for Mixtral-8x7B
- **General Chat**: Customer support, virtual assistants
- **Code Generation**: Programming assistance, debugging
- **Content Creation**: Writing, editing, summarization
- **Translation**: Multilingual content processing
- **Education**: Tutoring, explanation generation

### Ideal Applications for Mixtral-8x22B
- **Complex Analysis**: Research, data interpretation
- **Long Documents**: Legal, technical document processing
- **Advanced Reasoning**: Scientific, mathematical problems
- **Enterprise Solutions**: Business intelligence, reporting
- **Creative Projects**: Long-form content generation

### Model Selection Guide

| Use Case | Recommended Model | Reasoning |
|----------|------------------|-----------|
| Simple Chat | Mixtral-8x7B | Cost-effective, fast |
| Code Tasks | Mixtral-8x7B | Strong programming support |
| Long Documents | Mixtral-8x22B | Extended context length |
| Multilingual | Either | Both support 5 languages |
| Cost-Sensitive | Mixtral-8x7B | Lower cost per token |
| Complex Reasoning | Mixtral-8x22B | Larger expert capacity |

## Performance Optimization

### Best Practices
1. **Temperature Tuning**:
   - Code: 0.1-0.3
   - Analysis: 0.4-0.6
   - Creative: 0.7-0.9
2. **Context Management**: Utilize full context length efficiently
3. **Batch Processing**: Group requests for cost savings
4. **Caching**: Implement response caching for repeated queries

### Prompt Engineering
1. **Clear Instructions**: Specify desired output format
2. **Language Specification**: Clearly state target language for multilingual tasks
3. **Context Provision**: Include relevant background information
4. **Examples**: Provide examples for complex tasks

## Comparison with Other Providers

### Together AI Advantages
- **Unified Pricing**: Same rate for input and output tokens
- **High Throughput**: Up to 100+ tokens per second
- **OpenAI Compatibility**: Easy migration from other APIs
- **No Waitlists**: Immediate access to latest models
- **Transparent Costs**: Clear token-based pricing

### Direct Mistral AI Comparison
- **Pricing**: Together AI often more cost-effective for output tokens
- **Integration**: Simpler API integration
- **Infrastructure**: Fully managed service
- **Support**: Comprehensive documentation and support

## Migration Guide

### From OpenAI to Mixtral
```python
# Minimal changes required
import openai

# Update configuration
openai.api_base = "https://api.together.xyz/v1"
openai.api_key = "your_together_api_key"

# Change model name
response = openai.ChatCompletion.create(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",  # Instead of gpt-3.5-turbo
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Performance Testing
1. **Baseline Establishment**: Test current model performance
2. **Mixtral Evaluation**: Run same tests with Mixtral
3. **Cost Analysis**: Compare token usage and costs
4. **Quality Assessment**: Evaluate output quality differences

## Troubleshooting and Tips

### Common Issues
1. **Rate Limiting**: Implement exponential backoff
2. **Context Length**: Monitor token usage to stay within limits
3. **Language Detection**: Specify target language explicitly
4. **Cost Management**: Monitor usage with Together AI dashboard

### Performance Tips
1. **Model Selection**: Choose appropriate model for task complexity
2. **Batch Requests**: Use batch API for multiple queries
3. **Caching**: Cache responses for repeated queries
4. **Monitoring**: Track performance metrics and costs

## Official Resources

- **Mixtral Blog Post**: https://www.together.ai/blog/mixtral
- **Model Page**: https://www.together.ai/models/mistral-beb7b
- **API Documentation**: https://docs.together.ai/docs/serverless-models
- **Pricing**: https://www.together.ai/pricing
- **Mistral AI Official**: https://mistral.ai/

## Support and Community

- **Together AI Support**: Technical support for API issues
- **Mistral AI Community**: Model-specific discussions
- **GitHub**: Open-source tools and implementations
- **Discord**: Real-time community support
- **Documentation**: Comprehensive guides and tutorials