# Omni-Moderation Model Documentation

## Overview
Omni-moderation is OpenAI's advanced multimodal content moderation model built on GPT-4o. It can analyze both text and images to detect potentially harmful content across multiple categories, providing developers with a powerful and free tool for content moderation.

## Model Variants
- **omni-moderation-latest**: Always points to the most recent version
- **omni-moderation-2024-09-26**: September 2024 snapshot
- **omni-moderation-latest-intents**: Version with enhanced intent detection

## Model Capabilities
- **Multimodal Analysis**: Evaluates both text and images
- **Multiple Categories**: Detects various types of harmful content
- **Calibrated Scores**: Probability scores that accurately reflect likelihood
- **Enhanced Accuracy**: Improved performance especially for non-English languages
- **Combined Analysis**: Can evaluate text and images together for context
- **Intent Detection**: Advanced version can detect harmful intents

## Content Categories

### Violence
- **violence**: General violent content
- **violence/graphic**: Graphic violence and gore

### Self-Harm
- **self-harm**: Content depicting self-harm
- **self-harm/intent**: Expression of self-harm intentions
- **self-harm/instruction**: Instructions for self-harm

### Sexual Content
- **sexual**: Sexual content detection
- **sexual/minors**: Content involving minors
- Additional sexual content subcategories

### Hate and Harassment
- **hate**: Hate speech and discriminatory content
- **hate/threatening**: Threatening hate speech
- **harassment**: Harassment and bullying
- **harassment/threatening**: Threatening harassment

## Input/Output Specifications

### Input
- **Text**: Any text string for analysis
- **Images**: Image files for visual content analysis
- **Combined**: Text with associated images for context
- **Batch Processing**: Multiple items in single request

### Output
```json
{
  "id": "modr-xyz123",
  "model": "omni-moderation-latest",
  "results": [{
    "flagged": false,
    "categories": {
      "hate": false,
      "hate/threatening": false,
      "self-harm": false,
      "self-harm/intent": false,
      "self-harm/instruction": false,
      "sexual": false,
      "sexual/minors": false,
      "violence": false,
      "violence/graphic": false
    },
    "category_scores": {
      "hate": 0.0023,
      "hate/threatening": 0.0001,
      "self-harm": 0.0012,
      "self-harm/intent": 0.0008,
      "self-harm/instruction": 0.0002,
      "sexual": 0.0156,
      "sexual/minors": 0.0003,
      "violence": 0.0089,
      "violence/graphic": 0.0021
    }
  }]
}
```

## Pricing Information
- **Cost**: FREE for all developers
- **Rate Limits**: Based on usage tier
- **No Hidden Costs**: Completely free tier available
- **Volume Scaling**: Higher rate limits for verified accounts

## API Usage Examples

### Basic Text Moderation
```python
import openai

response = openai.Moderation.create(
  model="omni-moderation-latest",
  input="This is the text I want to check for harmful content."
)

if response.results[0].flagged:
    print("Content flagged as potentially harmful")
    print("Categories:", response.results[0].categories)
```

### Image Moderation
```python
import base64

# Read and encode image
with open("image.jpg", "rb") as image_file:
    image_base64 = base64.b64encode(image_file.read()).decode()

response = openai.Moderation.create(
  model="omni-moderation-latest",
  input={
    "type": "image",
    "image": {
      "data": image_base64,
      "format": "jpeg"
    }
  }
)
```

### Combined Text and Image
```python
response = openai.Moderation.create(
  model="omni-moderation-latest",
  input=[
    {"type": "text", "text": "Check this image caption"},
    {"type": "image", "image": {"data": image_base64}}
  ]
)
```

### Threshold-Based Filtering
```python
# Custom thresholds for different categories
thresholds = {
    "hate": 0.7,
    "violence": 0.8,
    "sexual": 0.5
}

response = openai.Moderation.create(
  model="omni-moderation-latest",
  input=user_content
)

for category, score in response.results[0].category_scores.items():
    if category in thresholds and score > thresholds[category]:
        print(f"Content exceeds threshold for {category}: {score}")
```

### Batch Processing
```python
# Check multiple pieces of content
contents = [
    "First piece of content",
    "Second piece of content",
    {"type": "image", "image": {"data": image_base64}}
]

response = openai.Moderation.create(
  model="omni-moderation-latest",
  input=contents
)

for i, result in enumerate(response.results):
    if result.flagged:
        print(f"Content {i} flagged")
```

## Best Practices
1. **Threshold Tuning**: Adjust thresholds based on your use case
2. **Context Consideration**: Use combined text+image for better accuracy
3. **Non-English Content**: Leverage improved non-English support
4. **Batch Processing**: Group multiple items for efficiency
5. **Category Selection**: Focus on categories relevant to your platform
6. **False Positive Handling**: Implement human review for edge cases
7. **Logging**: Track moderation decisions for improvement

## Limitations and Use Cases

### Limitations
- Cannot detect all types of harmful content
- May have false positives/negatives
- Cultural context may affect accuracy
- Not a replacement for human judgment
- Rate limits apply based on tier
- Some nuanced content may be misclassified

### Use Cases
- **Social Media**: Content moderation for posts and comments
- **Gaming**: Chat and user-generated content filtering
- **Education**: Ensuring safe learning environments
- **E-commerce**: Review and listing moderation
- **Forums**: Community content moderation
- **Productivity Tools**: Document and collaboration safety
- **AI Applications**: Guardrails for generative AI
- **Dating Apps**: Profile and message screening
- **Content Platforms**: Video, image, and text moderation
- **Customer Service**: Filtering inappropriate requests

## Integration Examples

### Grammarly Use Case
Uses the API as part of safety guardrails in AI communications assistance, ensuring generated content is appropriate.

### ElevenLabs Use Case
Scans content generated by audio AI products to prevent harmful audio generation.

## Comparison with Previous Version
- **Accuracy**: Significantly improved, especially for non-English
- **Multimodal**: Adds image support beyond text-only
- **Calibration**: Better probability score accuracy
- **Categories**: More granular category detection
- **Performance**: Faster processing times
- **Context**: Better understanding of combined inputs

## Additional Notes
- Built on GPT-4o architecture for advanced understanding
- Free tier makes it accessible for all developers
- Regular updates through the "latest" endpoint
- Part of OpenAI's commitment to AI safety
- Can be combined with other safety measures
- Supports OpenAI's mission of safe AI deployment
- Actively improved based on user feedback
- Documentation and examples available in OpenAI Cookbook