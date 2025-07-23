# Together AI Pricing Tiers and Structure

## Overview

Together AI offers a comprehensive tiered pricing structure based on model size and complexity, providing developers and enterprises with flexible options for serverless AI model deployment.

## Serverless Endpoints Pricing (per 1M tokens)

### Model Size-Based Tiers

| Model Size | Price per 1M tokens |
|------------|-------------------|
| Up to 4B | $0.10 |
| 4.1B - 8B | $0.20 |
| 8.1B - 21B | $0.30 |
| 21.1B - 41B | $0.80 |
| 41.1B - 80B | $0.90 |
| 80.1B - 110B | $1.80 |

### Mixture-of-Experts (MoE) Pricing

| Total Parameters | Price per 1M tokens |
|------------------|-------------------|
| Up to 56B | $0.60 |
| 56.1B - 176B | $1.20 |
| 176.1B - 480B | $2.40 |

## Special Model Categories

### Text Models with Variants
- **Llama 3 70B Text Model**:
  - Lite: $0.54 per 1M tokens
  - Turbo: $0.88 per 1M tokens
  - Reference: $0.90 per 1M tokens

### Specific Model Pricing
- **Qwen 2 72B**: $0.90 per 1M tokens
- **DeepSeek-V3**: $1.25 per 1M tokens

### Embedding Models
- **Price Range**: $0.008 to $0.02 per 1M tokens
- **Billing**: Only input tokens are charged (no output token costs)

### Rerank Models
- **Up to 8B parameters**: $0.10 per 1M tokens

### Image Models
- **Pricing**: Varies by model and resolution
- **Billing**: Based on image size and processing steps

## Dedicated Endpoints

### GPU-Based Per-Minute Pricing
- **Price Range**: $0.025 to $0.083 per minute
- **Depends on**: GPU type and configuration
- **Use Case**: Custom deployments with guaranteed capacity

## Fine-Tuning Pricing

### Pricing Factors
- **Model Size**: Larger models cost more
- **Fine-tuning Method**: 
  - LoRA (Low-Rank Adaptation): Lower cost
  - Full Fine-tuning: Higher cost
- **Price Range**: $0.48 to $8.00 per 1M tokens

### Pricing Variables
- **Dataset Size**: Larger datasets increase costs
- **Number of Epochs**: More training iterations increase costs
- **Validation Processes**: Both training and validation tokens are counted

## Rate Limits and Quotas

### Free Tier
- **New Account Credit**: $1 to get started
- **Rate Limits**: Apply to free tier usage

### Volume Discounts
- **Enterprise Customers**: Volume discounts available
- **Batch Inference**: 50% discount on input and output tokens for supported models

## API Authentication and Usage

### Getting Started
1. Register for an account at Together AI
2. Receive $1 in free credits
3. Obtain API key for authentication
4. Start building with 200+ open-source models

### Billing Model
- **Pay-Per-Use**: Only pay for tokens processed
- **No Minimum Fees**: Transparent token-based pricing
- **Automatic Scaling**: Infrastructure scales with demand

## Key Features

### Supported Model Types
- **Chat Models**: Conversational AI
- **Multimodal Models**: Text + image processing
- **Language Models**: Text generation and completion
- **Code Models**: Programming assistance
- **Embedding Models**: Vector representations
- **Image Models**: Image generation and processing
- **Audio Models**: Speech and audio processing

### Infrastructure Benefits
- **State-of-the-art Hardware**: NVIDIA Blackwell and Hopper GPUs
- **High-Performance Networking**: NVLink and InfiniBand connectivity
- **Optimal Performance**: Designed for AI training and inference
- **Serverless Architecture**: No infrastructure management required

## Comparison with Other Providers

### Competitive Advantages
- **Transparent Pricing**: Clear token-based costs
- **No Hidden Fees**: What you see is what you pay
- **Flexible Deployment**: Serverless and dedicated options
- **Wide Model Selection**: 200+ open-source models
- **OpenAI Compatibility**: Easy migration from other providers

### Cost Efficiency
- **70-90% Savings**: Compared to similar closed models
- **Batch Processing Discounts**: Additional cost savings
- **Volume Pricing**: Enterprise discounts available

## Best Practices for Cost Optimization

1. **Choose Appropriate Model Size**: Use the smallest model that meets your requirements
2. **Utilize Batch Processing**: Take advantage of 50% discounts where available
3. **Monitor Token Usage**: Track consumption to optimize costs
4. **Consider Dedicated Endpoints**: For high-volume, predictable workloads
5. **Leverage Free Credits**: Start with the $1 credit to test models

## Official Resources

- **Pricing Page**: https://www.together.ai/pricing
- **Fine-tuning Pricing**: https://docs.together.ai/docs/fine-tuning-pricing
- **API Documentation**: https://docs.together.ai/
- **Model Catalog**: https://www.together.ai/models

## Support and Contact

For enterprise pricing, volume discounts, and custom deployments, contact Together AI's sales team through their official website.