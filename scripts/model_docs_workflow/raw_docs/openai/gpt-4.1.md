# GPT-4.1 Documentation

## Model Overview

GPT-4.1 is the flagship model in OpenAI's GPT-4.1 family, introduced in 2025 as a significant upgrade to the GPT-4o series. It represents a major advancement in coding capabilities, instruction following, and long-context understanding.

## Release Information

- **Release Date**: April 2025
- **Model IDs**: 
  - `gpt-4.1`
  - `gpt-4.1-2025-04-14`
- **Availability**: API-only initially, later made available in ChatGPT for Plus, Pro, Team, Enterprise, and Edu users

## Technical Specifications

### Context Window
- **Maximum Context**: 1 million tokens (up from 128,000 in GPT-4o)
- **Reliable Attention**: Trained to reliably attend to information across the full 1 million context length
- **First Token Latency**: Most often returns the first token in less than five seconds for queries with 128,000 input tokens

### Knowledge Cutoff
- **Training Data**: Up to June 2024

### Model Architecture
- Built on improvements from GPT-4o with enhanced pre-training and post-training
- Specialized optimization for coding tasks and precise instruction following

## Key Capabilities

### Coding Excellence
- **Primary Strength**: Excels at coding tasks with significant improvements over GPT-4o
- **Web Development**: Particularly strong at web development tasks
- **Instruction Following**: Enhanced precision in following complex instructions
- **Alternative to Reasoning Models**: Offers an alternative to OpenAI o3 and o4-mini for simpler, everyday coding needs

### Performance Benchmarks
- **SWE-bench Verified**: 21.4% improvement over GPT-4o and 26.6% over GPT-4.5
- **MultiChallenge benchmark**: 38.3%, a 10.5% increase over GPT-4o
- **Video-MME**: 72.0% on the long, no subtitles category, a 6.7% improvement over GPT-4o

### Long Context Understanding
- Major gains in long-context comprehension
- Ability to process and understand information across the full 1 million token context

## Pricing

- **Cost Reduction**: 26% less expensive than GPT-4o for median queries
- **Performance**: Matches or exceeds GPT-4o in intelligence evaluations while reducing latency by nearly half and reducing cost by 83%
- **Prompt Caching**: 75% discount for queries that repeatedly pass the same context (up from 50% previously)
- **Long Context**: No additional cost beyond standard per-token costs for long context requests
- **Batch API**: Additional 50% pricing discount available

## API Usage

### Basic Implementation
```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, GPT-4.1!"}
    ]
)
```

### Model Selection
- Available via the OpenAI API
- In ChatGPT: Available through the "more models" dropdown in the model picker

## Use Cases

### Ideal For:
- Complex coding projects requiring precise instruction following
- Web development and full-stack applications
- Long-document analysis and understanding
- Tasks requiring processing of extensive context (up to 1M tokens)
- Applications where GPT-4o's capabilities are needed but with better performance and lower cost

### Not Recommended For:
- Tasks requiring the absolute highest reasoning capabilities (consider o3 models instead)
- Simple classification tasks (GPT-4.1-nano would be more cost-effective)

## Comparison to Previous Models

### vs GPT-4o
- 21.4% better on SWE-bench Verified
- 10.5% improvement on MultiChallenge benchmark
- Nearly half the latency
- 83% cost reduction
- 8x larger context window (1M vs 128K tokens)

### vs GPT-4.5-preview
- Better performance on most capabilities
- Much lower cost and latency
- GPT-4.5-preview is being deprecated on July 14, 2025, with GPT-4.1 as the recommended replacement

## Limitations

- API-only access (no direct fine-tuning available)
- While excellent at coding, for the most complex reasoning tasks, o3 models may be more suitable
- Image processing capabilities convert images to tokens, which counts against token limits

## Migration Guide

For users migrating from GPT-4.5-preview:
1. Update model parameter from `gpt-4.5-preview` to `gpt-4.1`
2. Take advantage of the larger context window (1M tokens)
3. Expect improved performance at lower cost
4. Review outputs as GPT-4.1 may have different response patterns

## Future Updates

- Continuous improvements planned based on developer feedback
- Integration with Codex CLI for lightweight coding agent support
- Ongoing optimization for specific use cases based on community needs