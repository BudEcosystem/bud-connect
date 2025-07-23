# Mistral Medium Latest - Model Documentation

## Model Overview

Mistral Medium represents Mistral AI's frontier-class model in the medium size category, delivering state-of-the-art performance at 8X lower cost with radically simplified enterprise deployments. The latest version, Mistral Medium 3 (mistral-medium-2505), was released in May 2025. The model is designed to offer a balanced trade-off between performance and resource efficiency, positioned between the lightweight Mistral 7B and the more computationally intensive Mistral Large series.

## Technical Specifications

### Model Versions
- **Latest Version**: Mistral Medium 3 (mistral-medium-2505) - May 2025
- **Previous Versions**: 
  - mistral-medium-2312 (December 2023)
  - Original Mistral Medium with 13 billion parameters
- **Model Category**: Medium-sized frontier model

### Architecture Details
- **Architecture Type**: Transformer-based dense decoder-only autoregressive LLM
- **Context Window**: Up to 128k tokens (Mistral Medium 3)
- **Previous versions**: 32k tokens context window
- **Deployment**: Optimized for enterprise deployment on four GPUs and above
- **Based on**: Proprietary Mistral architecture

## Capabilities and Features

### Core Capabilities
- Frontier-class performance in professional use categories
- Exceptional performance in coding and STEM tasks
- Competitive with very large models while being significantly faster
- Enterprise context adaptation capabilities

### Performance Highlights
- Surpasses leading open models such as Llama 4 Maverick
- Outperforms enterprise models such as Cohere Command A
- Comes close to very large models in coding and STEM tasks
- Maintains high fidelity for domain-specific training

### Enterprise Features
- Continuous pretraining capabilities
- Full fine-tuning support
- Integration with enterprise knowledge bases
- Adaptive workflows support
- Domain-specific training optimization

## Pricing Information

### API Pricing
- **Input Tokens**: $0.4 per million tokens
- **Output Tokens**: $2.0 per million tokens
- **Note**: Same pricing as devstral-medium-2507

For detailed and up-to-date pricing information, please refer to Mistral AI's official pricing page.

## API Usage Details

### API Access Points
- Mistral La Plateforme (Primary)
- Amazon Sagemaker
- IBM WatsonX (coming soon)
- NVIDIA NIM (coming soon)
- Azure AI Foundry (coming soon)
- Google Cloud Vertex (coming soon)

### Model Identifiers
- **API Name**: `mistral-medium-latest`
- **Specific Version**: `mistral-medium-2505` (latest)

### Integration Options
- REST API via La Plateforme
- Cloud provider integrations (AWS, Azure, Google Cloud, IBM, Snowflake, NVIDIA, Outscale)
- Self-hosted deployment options
- OpenAPI specification available for download

## Performance Benchmarks

### Mistral Medium 3 Performance
- Performs at or above 90% of Claude Sonnet 3.7 on benchmarks across the board
- Particularly stands out in coding and STEM tasks
- 8X more cost-effective than comparable models
- Significantly faster than larger competitors

### Legacy Mistral Medium Performance  
- **MMLU Score**: 0.491
- **Intelligence Index**: 23 (across evaluations)
- **Output Speed**: 84.5 tokens per second
- **Latency (TTFT)**: 0.39s to receive the first token
- Positioned as best performance model delivered from Mistral AI at the time

## Use Cases and Applications

### Primary Use Cases
- Enterprise AI integration
- Professional coding assistance
- STEM problem solving
- Document understanding and analysis
- Domain-specific applications

### Enterprise Applications
- Continuous learning systems
- Adaptive workflows
- Knowledge base integration
- Custom fine-tuning for specific domains
- Production-ready deployments

## Limitations and Considerations

### Deployment Requirements
- Minimum of four GPUs for self-hosted deployment
- Enterprise-grade infrastructure for optimal performance
- Proper API authentication and security measures

### Model Considerations
- Designed specifically for enterprise contexts
- May require fine-tuning for specialized domains
- Performance varies based on task complexity

## Version Information and Release Dates

### Release Timeline
- **Mistral Medium 3**: May 2025 (mistral-medium-2505)
- **Previous Version**: December 2023 (mistral-medium-2312)

### Availability
- Immediate availability on La Plateforme
- Rolling deployment across cloud providers
- Self-hosted options for enterprise customers

## Additional Resources

### Documentation Access
- Create account on La Plateforme: https://console.mistral.ai
- Official documentation: https://docs.mistral.ai
- OpenAPI specification available for download

### Cloud Provider Support
- Azure AI Studio
- AWS Bedrock
- Google Cloud Model Garden
- IBM Watsonx
- Snowflake

## Notes

Mistral Medium 3 represents a significant advancement in the medium-sized model category, offering a unique balance between performance and cost. Its ability to adapt to enterprise contexts through continuous pretraining and fine-tuning makes it particularly valuable for organizations seeking to integrate AI deeply into their systems without the overhead of very large models.