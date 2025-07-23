## GPT-4-32k Model Documentation

### Model Overview
GPT-4-32k is an extended context version of OpenAI's GPT-4 model, featuring quadrupled context length compared to the standard GPT-4. It processes up to approximately 50 pages of text in one pass, making it ideal for longer content analysis without requiring external databases.

### Technical Specifications

**Context Length**: 32,768 tokens (32k)
- Approximately 4x larger than standard GPT-4 (8,192 tokens)
- Equivalent to about 50 pages of text processing capability

**Model Architecture**: Large multimodal model (same architecture as GPT-4)
- Accepts both text and image inputs
- Produces text outputs (natural language, code, etc.)

### Release Information

**Initial Release**: March 14, 2023
- Model version: `gpt-4-32k-0314`
- Initially available only to select users

**Updated Version**: June 13, 2023
- Model version: `gpt-4-32k-0613`
- Added function calling capabilities
- Became more widely available

### Pricing Structure

**Input Tokens**: $60.00 per 1 million tokens ($0.06 per 1K tokens)
**Output Tokens**: $120.00 per 1 million tokens ($0.12 per 1K tokens)

*Note: This is exactly double the pricing of standard GPT-4:*
- GPT-4 standard: $0.03/1K input, $0.06/1K output
- GPT-4-32k: $0.06/1K input, $0.12/1K output

### Function Calling Support

**Available**: Yes (since June 13, 2023 with gpt-4-32k-0613)
- Same function calling capabilities as standard GPT-4
- Enhanced by extended context window for better comprehension
- Supports complex multi-turn conversations with function calls

### Vision Capabilities

**Architecture Support**: Yes - multimodal capabilities
- Can accept prompts with both text and images
- Processes visual information including documents, photographs, diagrams, screenshots
- Exhibits similar capabilities on multimodal inputs as text-only inputs

**Current Availability**: Limited/Research Preview
- Image inputs may not be publicly available through standard API
- Vision capabilities remain in research preview status

### API Access

**Model Names**:
- `gpt-4-32k` (stable reference)
- `gpt-4-32k-0314` (specific version - deprecated)
- `gpt-4-32k-0613` (specific version - deprecated)

**Availability**: Available through OpenAI API and Azure OpenAI
- No longer requires waitlist application
- Available to all qualified customers

### Deprecation Notice

**Status**: DEPRECATED AND RETIRING
- **Deprecation Date**: October 1, 2024 (for 0314 version)
- **Retirement Date**: June 6, 2025
- **Migration Recommended**: Users should migrate to newer models

### Recommended Successors

**GPT-4 Turbo**: 128,000 token context (4x larger than GPT-4-32k)
**GPT-4.1 Models**: Up to 1 million token context
**GPT-4o**: Current flagship multimodal model

### Use Cases

**Optimal For**:
- Long document analysis and processing
- Extended conversations requiring context retention
- Large codebase analysis
- Academic paper processing
- Legal document review
- Multi-page content summarization

**Limitations**:
- Higher cost per token compared to newer models
- Being phased out in favor of models with larger context windows
- Vision capabilities may have limited availability

### Migration Recommendations

Given the deprecation timeline, users should plan migration to:
1. **GPT-4 Turbo** for similar use cases with 4x larger context
2. **GPT-4.1** models for maximum context length requirements
3. **GPT-4o** for multimodal capabilities

**Timeline**: Complete migration before June 6, 2025 retirement date.

This model variant served as an important bridge between the original GPT-4 and the current generation of large-context models, but has been superseded by more capable and cost-effective alternatives.