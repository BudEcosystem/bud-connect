# Grok-3 Beta

## Model Overview

Grok-3 Beta represents xAI's flagship large language model engineered for enterprise use cases requiring deep expertise and robust performance. It is part of xAI's third-generation models that introduce "The Age of Reasoning Agents," trained on the Colossus supercluster with 10x the compute of previous state-of-the-art models.

### Key Improvements over Grok-2
- **10x more compute** used during training compared to Grok-2
- **Reasoning capabilities**: Can think for seconds to minutes before responding
- **Error correction**: Actively corrects mistakes during reasoning
- **Alternative exploration**: Explores multiple solution paths
- **Transparency**: Users can inspect the reasoning process, not just the final answer

## Technical Specifications

### Model Architecture
- **Context Window**: 131,072 tokens (~97,500 words)
- **Knowledge Cutoff**: November 2024
- **Training Infrastructure**: Trained on xAI's Colossus supercluster
- **Model Type**: Reasoning model with chain-of-thought capabilities

### Capabilities
- **Code Interpreter**: Built-in code execution capabilities
- **Internet Access**: Can access and search the web
- **Tool Calling**: Supports function calling
- **Multi-language Support**: Yes
- **Vision Capabilities**: No
- **Fine-tuning**: Not supported

### Reasoning Features
- **Think Mode**: Press the "Think" button to engage reasoning capabilities
- **Big Brain Mode**: Employs additional computing for complex reasoning
- **Reasoning Time**: Can spend seconds to minutes on complex problems
- **Transparent Thinking**: Raw thinking traces are accessible

## Pricing Information

### API Pricing
- **Input Tokens**: $3.00 per million tokens
- **Output Tokens**: $15.00 per million tokens
- **Cached Input Tokens**: $0.75 per million tokens
- **Live Search**: $25 per 1,000 sources ($0.025 per source)

### Token Conversion
- 1 word ≈ 1.33 tokens
- 4 characters ≈ 1 token

## API Usage Details

### Availability
- Released via xAI's API platform
- Available through multiple API providers
- Beta status with ongoing improvements

### API Parameters
- Supports standard LLM parameters
- Reasoning effort can be configured
- When using reasoning mode, presencePenalty, frequencyPenalty, and stop parameters are not supported

### Integration
```python
# Example API usage (conceptual)
response = client.chat.completions.create(
    model="xai/grok-3-beta",
    messages=[{"role": "user", "content": "Your prompt here"}],
    max_tokens=4096,
    temperature=0.7
)
```

## Performance Benchmarks

### Academic Benchmarks
- **AIME 2025**: 93.3% (with highest test-time compute)
- **GPQA (Graduate-level Science)**: 84.6%
- **LiveCodeBench**: 79.4%
- **MMLU-Pro**: State-of-the-art among non-reasoning models

### Chatbot Arena
- **Elo Score**: 1402
- Topped the LMArena Chatbot Arena leaderboard
- Outperformed ChatGPT-4 (1377), Claude 3.5 Sonnet, and GPT-4o

### Comparative Performance
- Outperforms Gemini-2 Pro, DeepSeek-V3, Claude 3.5 Sonnet, and GPT-4o in:
  - Math (AIME)
  - Science (GPQA)
  - Coding (LCB)

## Use Cases and Features

### Primary Use Cases
1. **Enterprise Applications**
   - Data extraction and analysis
   - Complex problem-solving
   - Domain-specific expertise (finance, healthcare, law, science)

2. **Research and Development**
   - Scientific reasoning
   - Mathematical problem-solving
   - Code generation and debugging

3. **Advanced Reasoning Tasks**
   - Multi-step logical problems
   - Error detection and correction
   - Alternative solution exploration

### DeepSearch Agent
- xAI's first agent built to seek truth across human knowledge
- Synthesizes key information
- Reasons about conflicting facts and opinions
- Distills clarity from complexity

## Comparison with Other Grok Models

### vs Grok-3 Mini
- **Grok-3 Beta**: Full reasoning capabilities, broader domain knowledge
- **Grok-3 Mini**: Cost-efficient, faster, great for logic-based tasks without deep domain requirements

### vs Grok-3 Fast
- **Grok-3 Beta**: Standard latency, full reasoning depth
- **Grok-3 Fast**: Premium pricing for significantly faster response times

### Market Position
- Matches Claude 3.7 Sonnet pricing
- More expensive than Google Gemini 2.5 Pro
- Positioned as premium enterprise solution

## Important Notes

1. **Beta Status**: Model is still in training and will evolve rapidly with user feedback
2. **Reasoning Mode**: Not all tasks require reasoning mode - use judiciously
3. **Context Limitations**: API maxes out at 131,072 tokens despite claims of 1M token support
4. **Cost Considerations**: Reasoning mode and internet access add to operational costs

## Future Development

- Continuous improvements based on user feedback
- Planned transition to Grok-4 (fully reasoning model)
- Expanding capabilities and reducing limitations
- Integration with more xAI services and agents