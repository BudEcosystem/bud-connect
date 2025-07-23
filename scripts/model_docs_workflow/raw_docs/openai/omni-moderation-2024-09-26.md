# OpenAI omni-moderation-2024-09-26 Model Documentation

## Model Overview

The `omni-moderation-2024-09-26` is OpenAI's multimodal content moderation model released on September 26, 2024. Built on GPT-4o, this model represents a significant advancement in AI-powered content moderation, supporting both text and image inputs with enhanced accuracy across multiple languages.

### Model Identifier
- **Model Name**: `omni-moderation-2024-09-26`
- **Alternative Name**: `omni-moderation-latest` (automatically points to this version)
- **Release Date**: September 26, 2024
- **Base Architecture**: GPT-4o

## Technical Specifications

### Input Capabilities
- **Text Input**: Supports text content in 40+ languages
- **Image Input**: Supports image moderation for specific categories
- **Multimodal**: Can process text and images together or separately

### Content Categories

#### Text Moderation (13 Categories)
1. **hate** - Content that expresses, incites, or promotes hate based on protected characteristics
2. **hate/threatening** - Hateful content that includes violence or serious harm towards targeted groups
3. **harassment** - Content that expresses, incites, or promotes harassing language
4. **harassment/threatening** - Harassment content with threats
5. **self-harm** - Content that promotes or depicts acts of self-harm
6. **self-harm/intent** - Content showing intent to commit self-harm
7. **self-harm/instructions** - Instructions on how to commit self-harm
8. **sexual** - Content meant to arouse sexual excitement
9. **sexual/minors** - Sexual content involving individuals under 18
10. **violence** - Content promoting or glorifying violence
11. **violence/graphic** - Graphic violence content
12. **illicit** - Instructions or advice on how to commit wrongdoing (NEW)
13. **illicit/violent** - Instructions for wrongdoing that includes violence (NEW)

#### Image Moderation (6 Categories)
Currently supported for:
- **violence** and **violence/graphic**
- **self-harm**, **self-harm/intent**, and **self-harm/instructions**
- **sexual** (excluding **sexual/minors**)

### Performance Metrics
- **Multilingual Improvement**: 42% accuracy improvement across 40 languages
- **Language Coverage**: 98% of tested languages show improvement over previous models
- **Recall Enhancement**: Significant improvement in detecting potentially harmful content
- **Calibrated Scoring**: More accurate probability scores (0-1 range)

## API Usage

### Request Format
```json
{
  "model": "omni-moderation-2024-09-26",
  "input": [
    {
      "type": "text",
      "text": "Content to moderate"
    },
    {
      "type": "image_url",
      "image_url": {
        "url": "https://example.com/image.jpg"
      }
    }
  ]
}
```

### Response Format
```json
{
  "id": "modr-XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "model": "omni-moderation-2024-09-26",
  "results": [
    {
      "flagged": false,
      "categories": {
        "sexual": false,
        "hate": false,
        "harassment": false,
        "self-harm": false,
        "sexual/minors": false,
        "hate/threatening": false,
        "harassment/threatening": false,
        "self-harm/intent": false,
        "self-harm/instructions": false,
        "violence": false,
        "violence/graphic": false,
        "illicit": false,
        "illicit/violent": false
      },
      "category_scores": {
        "sexual": 0.00001668,
        "hate": 0.00000250,
        "harassment": 0.00000150,
        "self-harm": 0.00000000,
        "sexual/minors": 0.00000001,
        "hate/threatening": 0.00000000,
        "harassment/threatening": 0.00000000,
        "self-harm/intent": 0.00000000,
        "self-harm/instructions": 0.00000000,
        "violence": 0.00000002,
        "violence/graphic": 0.00000001,
        "illicit": 0.00000000,
        "illicit/violent": 0.00000000
      }
    }
  ]
}
```

## Pricing Information

- **Cost**: Free for all OpenAI API users
- **Rate Limits**: Varies by usage tier
- **Billing**: Does not count towards monthly usage limits

## Use Cases and Applications

### Primary Use Cases
1. **Social Media Platforms**: Automated content moderation for posts and images
2. **Educational Platforms**: Ensuring safe learning environments
3. **Gaming Communities**: Moderating chat and user-generated content
4. **E-commerce**: Product description and image review
5. **Corporate Communications**: Internal content compliance
6. **Creative Platforms**: User-generated content screening

### Industries
- Social media and networking
- Education technology
- Gaming and entertainment
- E-commerce and marketplaces
- Corporate communication platforms
- Content management systems

## Limitations and Considerations

### Current Limitations
1. **Image Categories**: Only 6 out of 13 categories support image moderation
2. **False Positives**: Higher sensitivity may result in increased false positive rates
3. **Context Dependency**: May struggle with context-dependent content like satire or educational material
4. **Cultural Nuances**: Despite multilingual improvements, some cultural context may be missed

### Implementation Considerations
1. **Human Review**: Recommended for edge cases and appeals processes
2. **Threshold Tuning**: Category scores above 0.5-0.6 typically indicate violations
3. **Regular Updates**: Model performance may change with future updates
4. **Compliance**: Ensure alignment with local regulations and platform policies

### Best Practices
1. Combine with human moderators for comprehensive coverage
2. Regularly review and adjust moderation thresholds
3. Implement appeals processes for false positives
4. Consider context and cultural sensitivity in moderation decisions
5. Monitor performance across different content types and languages

## Technical Integration

### Rate Limits
- Varies by OpenAI tier (Free, Pay-as-you-go, etc.)
- Generally allows for high-volume moderation needs
- No additional costs beyond standard API limits

### Response Time
- Low latency for real-time moderation applications
- Suitable for both batch and real-time processing

### Backwards Compatibility
- Fully backwards compatible with existing moderation API implementations
- Existing code using `text-moderation-latest` can be easily updated

## Version History

- **September 26, 2024**: Initial release of omni-moderation-2024-09-26
- Based on GPT-4o architecture with multimodal capabilities
- Introduced two new harm categories: illicit and illicit/violent
- Enhanced multilingual performance across 40+ languages