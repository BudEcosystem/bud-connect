# DALL-E 2 Model Documentation

## Overview
DALL-E 2 is OpenAI's first image generation model that can create realistic images and art from a text description. It can combine concepts, attributes, and styles to generate original visual content.

## Model Capabilities
- **Text-to-Image Generation**: Creates images from natural language descriptions
- **Image Editing**: Supports edit and variations features through the API
- **Concept Combination**: Can combine multiple concepts, attributes, and artistic styles
- **Multiple Sizes**: Supports generation of images in various sizes

## Input/Output Specifications

### Input
- **Type**: Text prompt (natural language description)
- **Format**: String input through the API

### Output
- **Format**: Images as URLs (valid for one hour)
- **Supported Sizes**: 
  - 1024×1024 (default)
  - 512×512
  - 256×256
- **Format Conversion**: URLs need to be converted to desired image format by the user

## Pricing Information
- **Square Images**:
  - Low quality: ~$0.01 per image
  - Medium quality: ~$0.04 per image  
  - High quality: ~$0.17 per image
- **Billing**: Pay-as-you-go through OpenAI Platform
- **Volume Discounts**: Available for usage >$5k/month (contact sales)

## API Usage Examples

### Basic Image Generation
```python
import openai

response = openai.Image.create(
  model="dall-e-2",
  prompt="A white siamese cat",
  n=1,
  size="1024x1024"
)

image_url = response['data'][0]['url']
```

### Image Variations
```python
response = openai.Image.create_variation(
  model="dall-e-2",
  image=open("image.png", "rb"),
  n=1,
  size="1024x1024"
)
```

### Image Editing
```python
response = openai.Image.create_edit(
  model="dall-e-2",
  image=open("image.png", "rb"),
  mask=open("mask.png", "rb"),
  prompt="A sunlit indoor lounge area with a pool containing a flamingo",
  n=1,
  size="1024x1024"
)
```

## Best Practices
1. **Prompt Engineering**: Be specific and descriptive in your prompts for better results
2. **Image Sizes**: Choose appropriate size based on your use case to optimize costs
3. **URL Handling**: Download images promptly as URLs expire after one hour
4. **API Rate Limits**: Be aware of org-level rate limits on images per minute
5. **Backward Compatibility**: DALL-E 2 remains the default model for backward compatibility

## Limitations and Use Cases

### Limitations
- URLs are temporary (1-hour validity)
- Rate limits shared with other OpenAI API services
- Org-level caps on images per minute
- Less advanced than newer models (DALL-E 3, GPT Image API)

### Use Cases
- Art and creative content generation
- Concept visualization
- Product design mockups
- Educational illustrations
- Marketing and advertising visuals
- Game asset creation

## Additional Notes
- Edit and variations features are only available with DALL-E 2 (not DALL-E 3)
- The API defaults to DALL-E 2 for backward compatibility
- For enhanced capabilities, consider upgrading to DALL-E 3 or the new GPT Image API
- Access requires an OpenAI API account