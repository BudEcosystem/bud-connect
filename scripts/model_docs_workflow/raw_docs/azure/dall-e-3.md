# DALL-E 3 Model Documentation

## Overview
DALL-E 3 is OpenAI's advanced image generation model with improved understanding of nuance and detail. It features better prompt adherence, higher image quality, and enhanced safety measures compared to DALL-E 2.

## Model Capabilities
- **Enhanced Prompt Understanding**: Automatically creates more detailed prompts for better results
- **Higher Resolution Support**: Native support for multiple aspect ratios and larger sizes
- **Quality Settings**: Adjustable quality levels for different use cases
- **Style Control**: New style parameter for controlling artistic output
- **Better Text Rendering**: Improved ability to generate readable text within images

## Input/Output Specifications

### Input
- **Type**: Text prompt (natural language description)
- **Model Parameter**: Must specify `model="dall-e-3"`
- **Style Options**: "vivid" (default) or "natural"
- **Quality Options**: "standard" (default) or "hd"
- **n Parameter**: Only supports n=1 (single image generation)

### Output
- **Format**: Images as URLs (valid for one hour)
- **Supported Sizes**:
  - 1024×1024 (square)
  - 1024×1792 (portrait)
  - 1792×1024 (landscape)
- **Resolution**: Higher resolution options available with "hd" quality setting

## Pricing Information
- **Standard Quality**:
  - Square images (1024×1024): ~$0.04 per image
  - Other sizes scale proportionally
- **HD Quality**:
  - Approximately 2x the cost of standard quality
  - Square images (1024×1024): ~$0.08 per image
- **Prompt Processing**: Billed similarly to GPT text models
- **Billing**: Pay-as-you-go through OpenAI Platform

## API Usage Examples

### Basic Image Generation
```python
import openai

response = openai.Image.create(
  model="dall-e-3",
  prompt="A futuristic cityscape at sunset with flying cars",
  n=1,
  size="1024x1024",
  quality="standard",
  style="vivid"
)

image_url = response['data'][0]['url']
```

### HD Quality Generation
```python
response = openai.Image.create(
  model="dall-e-3",
  prompt="A detailed oil painting of a mountain landscape",
  n=1,
  size="1792x1024",
  quality="hd",
  style="natural"
)
```

### Using Different Aspect Ratios
```python
# Portrait orientation
response = openai.Image.create(
  model="dall-e-3",
  prompt="A tall redwood tree in a misty forest",
  size="1024x1792"
)

# Landscape orientation
response = openai.Image.create(
  model="dall-e-3",
  prompt="A panoramic view of the Grand Canyon",
  size="1792x1024"
)
```

## Best Practices
1. **Prompt Design**: DALL-E 3 automatically enhances prompts, but being specific still helps
2. **Quality Selection**: Use "standard" for quick iterations, "hd" for final outputs
3. **Style Choice**: Experiment with "vivid" vs "natural" for different artistic effects
4. **Aspect Ratio**: Choose size based on intended use (portrait, landscape, or square)
5. **Cost Optimization**: Use standard quality for prototyping to reduce costs

## Limitations and Use Cases

### Limitations
- Only generates one image at a time (n=1)
- No support for edit or variations endpoints (DALL-E 2 only)
- URLs expire after one hour
- Higher latency for HD quality generation
- More expensive than DALL-E 2

### Use Cases
- Professional artwork and illustrations
- Marketing and advertising campaigns
- Concept art and design mockups
- Educational materials requiring high detail
- Social media content creation
- Book and magazine illustrations
- Product visualization
- Architectural renders

## Additional Notes
- DALL-E 3 expects highly detailed prompts and will automatically expand simple prompts
- The model includes improved safety measures and content filtering
- ChatGPT Plus subscribers can access DALL-E 3 through the ChatGPT interface
- For backward compatibility, APIs default to DALL-E 2 unless explicitly specified
- The "vivid" style tends to produce more dramatic and artistic results
- The "natural" style produces more realistic and subdued images