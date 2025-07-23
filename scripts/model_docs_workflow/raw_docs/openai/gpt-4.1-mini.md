# GPT-4.1-mini Documentation

## Model Overview

GPT-4.1-mini is a fast, capable, and efficient small model in the GPT-4.1 family, delivering significant improvements compared to GPT-4o mini in instruction-following, coding, and overall intelligence. It represents a significant leap in small model performance, even beating GPT-4o in many benchmarks.

## Release Information

- **Release Date**: April 2025
- **Model IDs**: 
  - `gpt-4.1-mini`
  - `gpt-4.1-mini-2025-04-14`
- **Availability**: Available via API, with ChatGPT access for Plus, Pro, Team, Enterprise, and Edu users

## Technical Specifications

### Context Window
- **Maximum Context**: 1 million tokens (matching the full GPT-4.1 model)
- **Long Context Performance**: Improved long-context comprehension capabilities

### Knowledge Cutoff
- **Training Data**: Up to June 2024

### Performance Characteristics
- **Latency**: Nearly half the latency of GPT-4o
- **Speed**: Optimized for fast response times while maintaining high quality

## Key Capabilities

### Performance Metrics
- Matches or exceeds GPT-4o in intelligence evaluations
- Even beats GPT-4o in many benchmarks despite being a "mini" model
- Significant improvements in:
  - Instruction-following accuracy
  - Coding capabilities
  - Overall intelligence and reasoning

### Specialized Strengths
- **Instruction Following**: Enhanced ability to follow complex, multi-step instructions
- **Coding**: Strong performance on coding tasks, suitable for most development needs
- **Efficiency**: Optimal balance between performance and resource usage

## Pricing

### Token Costs (as of 2025)
- **Input**: $0.40 per 1M tokens
- **Output**: $1.60 per 1M tokens
- **Cost Reduction**: 83% cost reduction compared to GPT-4o
- **Price Matching**: Same pricing as the o3 model after its 80% price reduction

### Additional Pricing Features
- **Prompt Caching**: 75% discount for repeated context
- **Batch API**: Additional 50% discount available
- **Long Context**: No additional cost for using the full 1M token context
- **Web Search**: Search content tokens included in standard pricing

## API Usage

### Basic Implementation
```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function to sort a list."}
    ]
)
```

### Optimization Tips
- Use for tasks that don't require the full power of GPT-4.1
- Take advantage of the 1M token context for document processing
- Utilize prompt caching for repetitive queries

## Use Cases

### Ideal For:
- High-volume API applications where cost is a concern
- Real-time applications requiring low latency
- General-purpose chatbots and assistants
- Code generation and review tasks
- Document analysis and summarization
- Applications currently using GPT-4o that need cost reduction

### Not Recommended For:
- The most complex reasoning or creative tasks (use GPT-4.1 or o3)
- Ultra-low latency requirements (consider GPT-4.1-nano)
- Tasks requiring specialized domain expertise beyond general knowledge

## Comparison to Other Models

### vs GPT-4o-mini
- Significant improvements in all areas
- Better instruction-following capabilities
- Enhanced coding performance
- Higher overall intelligence

### vs GPT-4o
- Matches or exceeds performance in many benchmarks
- 83% cost reduction
- Nearly half the latency
- Same 1M token context window as GPT-4.1

### vs GPT-4.1 (full model)
- More cost-effective for most use cases
- Slightly lower performance on the most complex tasks
- Same context window and knowledge cutoff
- Better suited for high-volume applications

## Image Processing

- Supports image inputs like other GPT-4.1 models
- Images are converted to tokens and count against token limits
- Efficient processing for multi-modal applications

## Limitations

- While excellent for most tasks, the full GPT-4.1 model may be better for the most demanding applications
- Not suitable for tasks requiring specialized fine-tuning (API-only model)
- May have slightly reduced performance on highly complex reasoning compared to larger models

## Best Practices

1. **Context Management**: Even though 1M tokens are available, use context efficiently for cost optimization
2. **Prompt Engineering**: Clear, specific prompts yield best results with mini models
3. **Batch Processing**: Take advantage of 50% batch API discount for bulk operations
4. **Caching Strategy**: Implement prompt caching for frequently used contexts to save 75% on those tokens

## Migration Guide

### From GPT-4o-mini:
1. Simple model name change from `gpt-4o-mini` to `gpt-4.1-mini`
2. Expect improved performance with no code changes needed
3. Review outputs as response patterns may differ slightly

### From GPT-4o:
1. Change model name and enjoy 83% cost savings
2. Monitor performance on your specific use cases
3. Most applications will see no degradation in quality

## Future Considerations

- Continued optimization for specific use cases
- Potential for further cost reductions as technology improves
- Integration with specialized tools and frameworks
- Enhanced multi-modal capabilities in future iterations