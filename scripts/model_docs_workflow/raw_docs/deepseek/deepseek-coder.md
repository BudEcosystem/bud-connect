# DeepSeek Coder Documentation

## Model Overview

DeepSeek Coder is a specialized code language model developed by DeepSeek AI, designed to excel at programming-related tasks. Released in November 2023, it represents the company's first open-source model specifically engineered for code generation, completion, and understanding across multiple programming languages.

### Key Highlights
- **Open-source** code language model achieving performance comparable to GPT4-Turbo in code-specific tasks
- Trained from scratch on **2T tokens** with 87% code and 13% natural language
- Available in multiple sizes ranging from **1B to 33B parameters**
- Latest version **DeepSeek-Coder-V2** (July 2024) features **236B parameters** with advanced MoE architecture

## Architecture and Technical Specifications

### Model Architecture

#### Mixture-of-Experts (MoE) Framework
- DeepSeek-Coder-V2 implements an efficient MoE architecture based on the DeepSeekMoE framework
- Total parameters: 16B and 236B variants
- Active parameters: Only 2.4B and 21B respectively (significant efficiency gain)
- Built on transformer architecture with innovations like Multi-head Latent Attention (MLA)

### Training Details

#### Pre-training Data
- **DeepSeek-Coder-V2**: Further pre-trained from DeepSeek-V2 with additional 6 trillion tokens
- Dataset composition:
  - 60% source code
  - 10% math corpus
  - 30% natural language corpus
- Total training: **10.2 trillion tokens**
- Source code dataset: 1,170 billion tokens from GitHub and CommonCrawl

#### Context Window
- **Original DeepSeek Coder**: 16K tokens
- **DeepSeek-Coder-V2**: Extended to 128K tokens
- Maintains performance across all context lengths up to 128K

### Model Variants

| Model | Parameters | Context Window | Key Features |
|-------|------------|----------------|--------------|
| DeepSeek-Coder-Base | 1B-33B | 16K | Base models for code completion |
| DeepSeek-Coder-Instruct | 1B-33B | 16K | Fine-tuned for instruction following |
| DeepSeek-Coder-V2 | 16B/236B | 128K | MoE architecture, 338 languages |
| DeepSeek-Coder-V2-Lite | 16B | 128K | Smaller efficient variant |

## Supported Programming Languages

DeepSeek-Coder-V2 dramatically expands language support from **86 to 338 programming languages**. This comprehensive coverage makes it one of the most versatile code models available.

### Partial List of Supported Languages
- **Popular Languages**: Python, JavaScript, Java, C++, C#, Go, Rust, TypeScript, Ruby, PHP, Swift, Kotlin
- **Web Technologies**: HTML, CSS, JavaScript, TypeScript, React, Angular, Vue
- **Systems Programming**: C, C++, Rust, Go, Assembly, CUDA
- **Functional Languages**: Haskell, Scala, Clojure, F#, Erlang, Elixir, OCaml
- **Scripting Languages**: Python, Ruby, Perl, Bash, PowerShell, Lua
- **Data Science**: R, Julia, MATLAB, SAS
- **Mobile Development**: Swift, Kotlin, Objective-C, Dart
- **Database Languages**: SQL, PL/SQL, T-SQL
- **Configuration**: YAML, JSON, XML, TOML, INI
- **And 300+ more languages**

*Complete list available at: https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/main/supported_langs.txt*

## Pricing Information

DeepSeek Coder offers highly competitive pricing compared to other AI coding models:

### API Pricing (DeepSeek Coder)
- **Input Processing**: $0.14 per million tokens
- **Generation (Output)**: $0.28 per million tokens

### Cost Optimization Features
- **Off-peak pricing**: Discounts available during 16:30-00:30 UTC daily
- **Context caching**: Reduces costs for repeated queries and multi-turn conversations
- **Token efficiency**: 1 English character ≈ 0.3 tokens

### Comparison
- **27x cheaper** than OpenAI o1 (only 3.6% of OpenAI o1's cost)
- Among the most cost-effective code generation solutions available

## API Usage and Integration

### Getting Started

#### 1. API Key Setup
```bash
# Create an API key at: https://platform.deepseek.com/api_keys
```

#### 2. Installation
```bash
# DeepSeek API is OpenAI-compatible
pip install openai
```

#### 3. Basic Usage Example
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-coder",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function to calculate fibonacci numbers"}
    ],
    temperature=0.3
)
```

### API Features
- **OpenAI-compatible format**: Use existing OpenAI SDK and tools
- **Multiple endpoints**: Support for chat completions, code completion, and more
- **Flexible parameters**: Control temperature, max tokens, and response format
- **Token limits**: Up to 64,000 tokens per conversation

### Integration Options
1. **Direct API calls**: RESTful API endpoints
2. **OpenAI SDK**: Drop-in replacement with base URL modification
3. **Hugging Face Transformers**: Direct model inference
4. **Platform integration**: Available at platform.deepseek.com

## Performance and Benchmarks

### Benchmark Results

DeepSeek-Coder-Base-33B significantly outperforms existing open-source code LLMs:

| Benchmark | DeepSeek-Coder-33B | CodeLlama-34B | Improvement |
|-----------|-------------------|---------------|-------------|
| HumanEval Python | Leading | Baseline | +7.9% |
| HumanEval Multilingual | Leading | Baseline | +9.3% |
| MBPP | Leading | Baseline | +10.8% |
| DS-1000 | Leading | Baseline | +5.9% |

### Key Performance Metrics
- **DeepSeek-Coder-Base-7B** reaches the performance of CodeLlama-34B
- **DeepSeek-Coder-Instruct-33B** outperforms GPT-3.5-Turbo on HumanEval
- Achieves state-of-the-art performance among open-source code models
- Superior performance on multiple programming languages

### Intelligence Index
- DeepSeek-Coder-V2 has an Intelligence Index of 29 across evaluations
- Trade-off between cost and performance compared to proprietary models

## Use Cases and Applications

### Primary Use Cases
1. **Code Generation**: Generate complete functions, classes, and modules
2. **Code Completion**: Context-aware code suggestions and auto-completion
3. **Code Review**: Analyze code for bugs, style issues, and improvements
4. **Documentation**: Generate code documentation and comments
5. **Debugging**: Identify and fix bugs in existing code
6. **Code Translation**: Convert code between programming languages
7. **Test Generation**: Create unit tests and test cases
8. **Refactoring**: Suggest code improvements and optimizations

### Project-Level Features
- 16K-128K context window enables understanding of entire codebases
- Fill-in-the-blank capabilities for code infilling
- Project-level code completion with context awareness

## Comparison with Other DeepSeek Models

### DeepSeek Coder vs DeepSeek Chat vs DeepSeek Reasoner

| Feature | DeepSeek Coder | DeepSeek Chat (V3) | DeepSeek Reasoner (R1) |
|---------|----------------|-------------------|------------------------|
| **Release Date** | Nov 2023 | May 2024 | Jan 2025 |
| **Purpose** | Specialized for coding | General-purpose + coding | Complex reasoning |
| **Strengths** | Fast code generation, 338 languages | Versatile, natural conversations | Deep analytical thinking |
| **Context Window** | 128K (V2) | 128K | 128K |
| **Parameters** | Up to 236B | Varies | 671B |
| **Response Time** | Fast | Fast | Slower (thinking process) |
| **API Name** | deepseek-coder | deepseek-chat | deepseek-reasoner |
| **Best For** | Direct coding tasks | General + moderate coding | Complex problem-solving |

### When to Use Each Model
- **DeepSeek Coder**: Best for dedicated programming tasks, code generation, debugging
- **DeepSeek Chat**: Ideal for documentation, explanations, and general coding assistance
- **DeepSeek Reasoner**: Complex algorithms, research problems, intricate coding challenges

### Evolution Note
DeepSeek V2.5 (September 2024) merged DeepSeek V2 Chat and DeepSeek Coder V2 into a unified model with superior performance across both domains.

## Hardware Requirements

### Inference Requirements
- **BF16 format**: 80GB × 8 GPUs required for full model
- **Efficient inference**: Only active parameters loaded due to MoE architecture
- **Smaller variants**: DeepSeek-Coder-V2-Lite requires less hardware

### Deployment Options
1. **Cloud API**: No hardware requirements, pay-per-use
2. **Self-hosted**: Requires significant GPU resources
3. **Quantized versions**: Reduced precision for smaller hardware

## Commercial Usage

### Licensing
- **DeepSeek-Coder-V2 series** (Base and Instruct) supports commercial use
- Open-source under permissive license
- No restrictions on commercial applications

### Considerations
- Data sent to DeepSeek API servers may be used for training
- Self-hosting available for data privacy requirements
- Regular model updates and improvements

## Additional Resources

### Official Documentation
- **API Documentation**: https://api-docs.deepseek.com/
- **GitHub Repository**: https://github.com/deepseek-ai/DeepSeek-Coder
- **Model Cards**: https://huggingface.co/deepseek-ai
- **Platform**: https://platform.deepseek.com/

### Research Papers
- Original DeepSeek Coder: "When the Large Language Model Meets Programming"
- DeepSeek-Coder-V2: "Breaking the Barrier of Closed-Source Models in Code Intelligence"

### Community Resources
- GitHub discussions and issues
- Hugging Face model hub
- Developer forums and communities

## Summary

DeepSeek Coder represents a significant advancement in open-source code language models, offering:
- **Exceptional performance** comparable to proprietary models
- **Cost-effective** pricing at a fraction of competitor costs
- **Extensive language support** with 338 programming languages
- **Flexible deployment** options from cloud API to self-hosting
- **Commercial-friendly** licensing for business applications

Whether you're building developer tools, automating code generation, or enhancing your development workflow, DeepSeek Coder provides a powerful and affordable solution for code intelligence tasks.