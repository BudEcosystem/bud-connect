# AWS Bedrock Stability AI SD3.5 Large v1.0 Model Documentation

## Model Overview

Stable Diffusion 3.5 Large is the most powerful model in the Stable Diffusion family at 8.1 billion parameters trained on Amazon SageMaker HyperPod. Stable Diffusion 3.5 Large is now generally available in Amazon Bedrock, AWS's fully managed platform for building and scaling generative AI applications with leading foundation models.

## Technical Specifications

- **Model ID**: `stability.sd3-5-large-v1:0`
- **Parameters**: 8.1 billion parameters
- **Architecture**: SOTA open architecture for image generation with 3.5B parameter base model stage and 6.6B parameter ensemble pipeline
- **Output**: High-quality 1-megapixel images
- **Training Platform**: Amazon SageMaker HyperPod

## Key Capabilities

### Image Generation Features
- **Versatile Styles** – Generate images in a wide range of styles and aesthetics, including 3-dimensional, photography, painting, line art, and virtually any visual style
- **Prompt Adherence** – Advanced prompt adherence to closely follow text prompts
- **Text Quality** – Unprecedented text quality with fewer errors in spelling, kerning, letter forming, and spacing
- **Enhanced Features**:
  - Exceptional photorealism with detailed 3D imagery
  - Superior handling of multiple subjects in complex scenes
  - Improved human anatomy rendering

### Use Cases
- **Creative Industries**: Accelerate storyboarding, concept art creation, and rapid prototyping of visual effects
- **Marketing & Advertising**: Quickly generate high-quality 1-megapixel images for campaigns, social media posts, and advertisements
- **Cross-Industry Applications**: Media, gaming, advertising, e-commerce, corporate training, retail, and education industries

## AWS Bedrock API Integration

### Model Invocation

**AWS CLI Example:**
```bash
aws bedrock-runtime invoke-model \
  --model-id stability.sd3-5-large-v1:0 \
  --body "{\"prompt\":\"Your prompt here\",\"mode\":\"text-to-image\",\"aspect_ratio\":\"1:1\",\"output_format\":\"jpeg\",\"seed\":0}" \
  --cli-binary-format raw-in-base64-out \
  --region us-west-2
```

**Python/Boto3 Example:**
```python
import boto3
import json
import base64
import io
from PIL import Image

bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
response = bedrock.invoke_model(
    modelId='stability.sd3-5-large-v1:0',
    body=json.dumps({
        'prompt': 'High-energy street scene with vibrant colors',
        'mode': 'text-to-image',
        'aspect_ratio': '1:1',
        'output_format': 'jpeg',
        'seed': 0
    })
)

output_body = json.loads(response["body"].read().decode("utf-8"))
base64_output_image = output_body["images"][0]
image_data = base64.b64decode(base64_output_image)
image = Image.open(io.BytesIO(image_data))
image.save("generated_image.png")
```

### API Parameters

#### Required Parameters
- **text_prompts** – Array of text prompts for generation. Each element contains a prompt and weight
- **prompt** – String describing what you wish to see in the output image

#### Optional Parameters
- **mode** – Generation mode: "text-to-image" or "image-to-image"
- **aspect_ratio** – Image aspect ratio (e.g., "1:1", "16:9")
- **output_format** – Output format (e.g., "jpeg", "png")
- **seed** – Random seed for reproducible generation
- **image** – Base64 encoded input image (for image-to-image mode)
- **strength** – Control how much output should resemble input (0.0-1.0, for image-to-image)

## Pricing Information

Amazon Bedrock offers flexible pricing options:
- **On-demand pricing** for pay-as-you-go usage with no upfront commitments
- **Batch mode** for cost-efficient processing of large volumes of input
- **Provisioned throughput** for high-volume and predictable workloads with dedicated model capacity and discounted pricing

Previous generation Stability AI image models are priced per image, depending on step count and image resolution. For specific pricing details, refer to the [AWS Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/).

## Performance Benchmarks

- **Quality**: Highest quality in the Stable Diffusion family
- **Resolution**: 1-megapixel output images
- **Speed**: Optimized for production use with AWS infrastructure
- **Accuracy**: Superior prompt adherence compared to previous versions

## Regional Availability

- **Primary Region**: US West (Oregon) AWS region
- **Access Requirements**: Request access for Stable Diffusion 3.5 Large through the Amazon Bedrock console

## Integration with AWS Services

- **Amazon SageMaker**: Model was trained on SageMaker HyperPod
- **AWS CLI**: Full command-line interface support
- **AWS SDK**: Available for all major programming languages
- **Amazon Bedrock**: Fully managed service integration

## Limitations and Considerations

- **Regional Availability**: Currently limited to US West (Oregon)
- **Access Control**: Requires explicit access request through Bedrock console
- **Content Filtering**: Subject to AWS content filtering policies
- **Rate Limits**: Subject to AWS service quotas and rate limiting

## Performance Optimization

- Use specific, descriptive prompts for better results
- Experiment with different aspect ratios for optimal composition
- Utilize seed values for reproducible results
- Consider batch processing for multiple image generation

## Security and Compliance

- **Data Privacy**: Processed through AWS's secure infrastructure
- **Compliance**: Inherits AWS Bedrock compliance certifications
- **Content Safety**: Built-in content filtering and safety measures
- **Access Control**: IAM-based access management

## Related Models

- **Stable Image Ultra**: Updated to include Stable Diffusion 3.5 Large in underlying architecture
- **Stable Diffusion 3 Large**: Previous generation model
- **Stable Image Core**: Optimized for speed and cost-effectiveness