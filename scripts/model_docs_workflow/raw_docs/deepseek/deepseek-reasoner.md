# DeepSeek Reasoner Model Documentation

## Model Overview and Description

DeepSeek-reasoner is an advanced reasoning model that points to DeepSeek-R1, developed by DeepSeek. It is specifically designed to excel at complex reasoning tasks, mathematical problem-solving, and code generation through Chain-of-Thought (CoT) reasoning. The model generates detailed reasoning steps before delivering final answers, significantly enhancing accuracy and transparency in its responses.

DeepSeek-R1 represents a breakthrough in open-source AI reasoning capabilities, achieving performance comparable to OpenAI's o1 model while being approximately 96% cheaper to use and fully open-source under MIT license.

## Technical Specifications

### Architecture
- **Base Model**: Built on DeepSeek-V3 architecture
- **Model Type**: Mixture-of-Experts (MoE) with reasoning specialization
- **Total Parameters**: 671 billion
- **Activated Parameters**: 37 billion per token
- **Training Method**: Large-scale Reinforcement Learning (RL)
- **Special Features**:
  - Chain-of-Thought (CoT) generation
  - Multi-head Latent Attention (MLA)
  - DeepSeekMoE architecture
  - RL-based reasoning optimization

### Context and Token Specifications
- **Maximum Context Length**: 128,000 tokens (model capability)
- **API Context Length**: 64,000 tokens
- **Maximum Output Tokens**: 8,000 tokens per response
- **Reasoning Content**: Not counted within context limit
- **Tokenizer**: Byte-level BPE with 128K vocabulary

### Model Variants
1. **DeepSeek-R1**: Original release (January 2025)
2. **DeepSeek-R1-0528**: Updated version (May 2025)
   - Supports system prompts
   - JSON output capability
   - Function calling support
   - Enhanced for agentic AI use cases

### Distilled Models
- Available sizes: 1.5B, 7B, 8B, 14B, 32B, and 70B
- Based on Qwen2.5 and Llama3 architectures
- Maintains reasoning capabilities at smaller scales

## Capabilities and Features

### Core Capabilities
1. **Advanced Reasoning**
   - Step-by-step logical thinking
   - Complex problem decomposition
   - Self-correction and refinement
   - Transparent reasoning chains

2. **Mathematical Excellence**
   - Advanced mathematical problem solving
   - Proof generation
   - Statistical analysis
   - Competitive programming mathematics

3. **Code Generation and Analysis**
   - Complex algorithm implementation
   - Code optimization
   - Debugging with explanations
   - Multi-language support

4. **Research and Analysis**
   - Literature analysis
   - Hypothesis generation
   - Data interpretation
   - Scientific reasoning

### API Features (R1-0528)
- **Function Calling**: Supported
- **JSON Output**: Supported
- **Chat Completion**: Supported
- **Chat Prefix Completion**: Beta feature
- **System Prompts**: Supported (R1-0528 only)
- **Reasoning Content Access**: Full CoT visibility

### Unique Features
- **DeepSeek-R1-Zero**: Trained purely through RL without SFT
- **Cold-start Data**: Enhanced reasoning through specialized training
- **Reasoning Transparency**: Access to complete thought process

## Pricing Information

### Current Pricing (per 1 million tokens)
- **Input with cache hit**: $0.14
- **Input with cache miss**: $0.55
- **Output**: $2.19

### Cost Comparison
- **vs OpenAI o1**: ~96% cheaper
  - OpenAI o1: $15/1M input, $60/1M output
  - DeepSeek-R1: $0.55/1M input, $2.19/1M output
  
- **vs DeepSeek-chat**: 
  - 2x more expensive for input
  - 2x more expensive for output
  - Justified by superior reasoning capabilities

### Caching Benefits
- Saves approximately 74.55% on input costs
- Efficient for iterative reasoning tasks
- Automatic cache management

## API Usage Details

### Base Configuration
- **API Endpoint**: `https://api.deepseek.com`
- **Model Names**: 
  - `deepseek-reasoner` (latest)
  - `deepseek-reasoner-r1-0528` (specific version)
- **Authentication**: Bearer token (API key required)

### Basic API Call Example
```bash
curl https://api.deepseek.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_DEEPSEEK_API_KEY>" \
  -d '{
    "model": "deepseek-reasoner",
    "messages": [
      {"role": "user", "content": "Solve this step by step: If x + 2y = 10 and 3x - y = 5, what are x and y?"}
    ],
    "stream": false
  }'
```

### Python SDK Usage
```python
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_DEEPSEEK_API_KEY>",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role": "user", "content": "Explain the proof of the Pythagorean theorem step by step."}
    ],
    temperature=0.6  # Recommended for reasoning tasks
)

# Access reasoning content
reasoning = response.choices[0].message.reasoning_content
final_answer = response.choices[0].message.content
```

### Response Structure
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Final answer after reasoning",
      "reasoning_content": "Step-by-step reasoning process..."
    }
  }]
}
```

### Parameter Restrictions
**Not Supported** (no effect if set):
- `temperature` (internally optimized)
- `top_p`
- `presence_penalty`
- `frequency_penalty`
- `logprobs`
- `top_logprobs`

## Performance Benchmarks

### Key Benchmark Results
- **AIME 2024 (Mathematics)**: 79.8% (vs GPT-4: ~40%)
- **Codeforces (Competitive Programming)**: 96.3% (vs GPT-4: ~45%)
- **MATH-500 (Mathematical Reasoning)**: 97.3%
- **Intelligence Index**: 68 (R1-0528), tied with world's leading labs

### Performance Comparisons
- **vs OpenAI o1**:
  - Comparable performance across math and coding
  - Similar reasoning capabilities
  - 96% lower cost
  
- **vs GPT-4**:
  - Superior on mathematical reasoning
  - Better on complex coding tasks
  - More transparent reasoning process
  
- **vs Claude 3.5**:
  - Competitive on reasoning benchmarks
  - Better cost-performance ratio
  - Open-source advantage

### Reasoning Quality
- Generates 30K-50K tokens of reasoning for complex problems
- Self-correction capabilities
- Iterative refinement of solutions
- Transparent thought process

## Use Cases and Applications

### Primary Use Cases
1. **Mathematical Problem Solving**
   - Competition mathematics (AMC, AIME, IMO level)
   - Proof generation and verification
   - Statistical analysis
   - Numerical computation

2. **Advanced Coding Tasks**
   - Algorithm design and optimization
   - Complex debugging
   - Code review with detailed explanations
   - Competitive programming solutions

3. **Research and Analysis**
   - Scientific hypothesis generation
   - Data analysis and interpretation
   - Literature review and synthesis
   - Experimental design

4. **Educational Applications**
   - Step-by-step problem explanations
   - Concept teaching through reasoning
   - Homework assistance with understanding
   - Test preparation

5. **Engineering and Technical Tasks**
   - System design and architecture
   - Technical documentation
   - Problem diagnosis and troubleshooting
   - Optimization problems

### Industry Applications
- **Finance**: Quantitative analysis, risk modeling
- **Healthcare**: Medical research analysis, diagnostic reasoning
- **Engineering**: Design optimization, failure analysis
- **Education**: Personalized tutoring, curriculum development
- **Legal**: Case analysis, logical argumentation

### When to Use DeepSeek-Reasoner
Choose reasoner over chat when:
- Problem requires multi-step reasoning
- Mathematical accuracy is critical
- Need transparent thought process
- Complex coding or algorithm tasks
- Research-level analysis needed

## Limitations and Considerations

### Technical Limitations
1. **Response Time**: Slower due to reasoning generation
2. **Token Usage**: Higher token consumption for CoT
3. **Parameter Restrictions**: Limited control over generation
4. **No System Prompts**: Original R1 (use R1-0528 for this feature)

### Content Restrictions
1. **Political Sensitivities**: 
   - Same restrictions as DeepSeek-chat
   - Chinese political topics avoided
   - Implements state-mandated filters

2. **Safety Vulnerabilities**:
   - 100% attack success rate in HarmBench tests
   - More prone to jailbreaking than Western models
   - 11x more likely to produce harmful outputs
   - 4x more likely to create insecure code

### Reasoning Limitations
1. **Reward Hacking**: May optimize for reward signals without true understanding
2. **Ambiguity Handling**: Inconsistent evaluation of harmfulness
3. **Context Dependencies**: Reasoning quality varies with context
4. **Hallucination Risk**: 45-50% reduction but not eliminated

### Best Practices
1. **Temperature Settings**: Use 0.5-0.7 (0.6 recommended)
2. **Prompt Structure**: 
   - Avoid system prompts in original R1
   - Include all instructions in user prompt
   - Be explicit about reasoning requirements
3. **Output Handling**: 
   - Parse both reasoning_content and content
   - Validate mathematical results
   - Check code for security issues
4. **Cost Management**: 
   - Use caching for iterative tasks
   - Consider DeepSeek-chat for simpler queries
   - Monitor token usage

### Security and Privacy Considerations
1. **Data Sensitivity**: Avoid sending confidential data to API
2. **Self-Hosting Option**: Use open-source weights for sensitive applications
3. **Output Validation**: Extra scrutiny for generated code
4. **Compliance**: Ensure usage meets regulatory requirements

## Additional Resources
- **Official API Documentation**: https://api-docs.deepseek.com/guides/reasoning_model
- **GitHub Repository**: https://github.com/deepseek-ai/DeepSeek-R1
- **Model Weights**: Available on Hugging Face (MIT license)
- **Technical Paper**: https://arxiv.org/pdf/2501.12948
- **Distilled Models**: Multiple sizes available for different use cases

## Version History
- **DeepSeek-R1**: Initial release (January 2025)
- **DeepSeek-R1-0528**: Enhanced version (May 2025)
  - Added system prompt support
  - JSON output capability
  - Function calling
  - Improved for agentic AI
- **DeepSeek-R1-Zero**: Pure RL training experiment
- **Distilled Versions**: 1.5B to 70B parameter variants