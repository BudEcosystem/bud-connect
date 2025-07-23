# GPT-4-Vision-Preview Model Documentation

## Overview
GPT-4-Vision-Preview was OpenAI's first multimodal model combining GPT-4's language capabilities with vision understanding. **Note: This model has been deprecated as of March 2025**, with users directed to use newer models like GPT-4o for vision capabilities.

## Model Capabilities
- **Image Understanding**: Analyzes and interprets visual content
- **Multimodal Reasoning**: Combines text and image inputs for comprehensive analysis
- **Detailed Image Analysis**: Can describe, analyze, and answer questions about images
- **Document Reading**: Capable of reading text and figures in documents
- **Real-World Scene Understanding**: Interprets photographs and real-world imagery

## Input/Output Specifications

### Input
- **Text**: Standard text prompts via Chat Completions API
- **Images**: 
  - Supported formats: PNG, JPEG, WEBP, GIF (non-animated)
  - Maximum size: 20MB per image
  - Resolution modes: "low" or "high" detail
  - Multiple images supported in single request

### Output
- **Type**: Text responses describing or analyzing the visual content
- **Format**: Standard Chat Completions API response format
- **Token Usage**: Combined text and image tokens

## Pricing Information

### Token Calculation
- **Base tokens**: 85 tokens per image
- **Per tile**: 170 tokens (high detail mode)
- **Formula**: Total tokens = 85 + 170 × n (where n = number of tiles)
- **Low detail mode**: Fixed 512×512 processing = ~$0.00085 per image
- **High detail example**: 1080×1080 image = ~$0.00765

### Pricing Structure
- Text tokens charged at standard GPT-4 rates
- Image tokens charged at same rate as text tokens
- Actual costs depend on image size and detail level

## API Usage Examples

### Basic Image Analysis
```python
import openai

response = openai.ChatCompletion.create(
  model="gpt-4-vision-preview",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What's in this image?"},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://example.com/image.jpg",
            "detail": "high"
          }
        }
      ]
    }
  ],
  max_tokens=300
)
```

### Multiple Images
```python
response = openai.ChatCompletion.create(
  model="gpt-4-vision-preview",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Compare these two images"},
        {
          "type": "image_url",
          "image_url": {"url": "image1_url", "detail": "low"}
        },
        {
          "type": "image_url", 
          "image_url": {"url": "image2_url", "detail": "low"}
        }
      ]
    }
  ]
)
```

### Document Analysis
```python
response = openai.ChatCompletion.create(
  model="gpt-4-vision-preview",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Extract the key information from this document"},
        {
          "type": "image_url",
          "image_url": {
            "url": "document_image_url",
            "detail": "high"  # High detail for text reading
          }
        }
      ]
    }
  ]
)
```

## Best Practices
1. **Detail Level Selection**: Use "low" for general understanding, "high" for text or detailed analysis
2. **Image Optimization**: Resize images appropriately to control costs
3. **Prompt Design**: Be specific about what you want analyzed in the image
4. **Cost Management**: Calculate token usage before processing large images
5. **Multiple Images**: Process related images together for better context

## Limitations and Use Cases

### Limitations
- **Deprecated Model**: No longer available for new implementations
- No support for video or animated GIFs
- Cannot generate, edit, or manipulate images
- Limited to 20MB per image
- Processing time increases with image complexity
- May struggle with very small text or complex diagrams

### Original Use Cases
- **Accessibility**: Helping visually impaired users (e.g., BeMyEyes)
- **Document Processing**: Extracting information from scanned documents
- **Product Identification**: Analyzing product images for e-commerce
- **Educational Tools**: Explaining complex diagrams and charts
- **Content Moderation**: Identifying inappropriate visual content
- **Medical Imaging**: Basic analysis of medical images (with appropriate disclaimers)
- **Real Estate**: Describing property images
- **Quality Control**: Identifying defects in manufacturing
- **Social Media Analysis**: Understanding image content for insights

## Migration Notes
Since GPT-4-Vision-Preview is deprecated:
1. **Use GPT-4o**: The recommended replacement for vision tasks
2. **Update Model Name**: Change `gpt-4-vision-preview` to `gpt-4o`
3. **API Compatibility**: Most code should work with minimal changes
4. **Enhanced Features**: Newer models offer better performance and additional capabilities
5. **Cost Considerations**: Check updated pricing for newer models

## Additional Notes
- This model pioneered OpenAI's multimodal capabilities
- It was available to all developers with GPT-4 access
- The technology has been superseded by more advanced models
- Legacy applications should be migrated to current models
- Documentation preserved for historical reference and migration purposes