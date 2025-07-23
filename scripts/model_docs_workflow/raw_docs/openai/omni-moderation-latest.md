# OpenAI omni-moderation-latest Model Documentation

## Model Overview

The `omni-moderation-latest` is OpenAI's flagship multimodal content moderation model that automatically points to the most recent version of the omni-moderation series. Currently, this points to `omni-moderation-2024-09-26`, but will be automatically updated as newer versions are released.

### Model Identifier
- **Model Name**: `omni-moderation-latest`
- **Current Version**: `omni-moderation-2024-09-26` (as of September 2024)
- **Base Architecture**: GPT-4o
- **Update Policy**: Automatically upgraded to latest version

## Technical Specifications

### Multimodal Capabilities
- **Text Processing**: Advanced natural language understanding across 40+ languages
- **Image Analysis**: Computer vision capabilities for visual content moderation
- **Combined Analysis**: Contextual understanding of text-image combinations
- **Cross-Modal Reasoning**: Ability to understand relationships between text and visual content

### Content Detection Categories

#### Comprehensive Text Moderation (13 Categories)
1. **hate** - Discrimination based on protected characteristics
   - Race, gender, ethnicity, religion, nationality, sexual orientation, disability, caste
2. **hate/threatening** - Hateful content with violence or serious harm
3. **harassment** - Harassing language towards any target
4. **harassment/threatening** - Harassment with threatening elements
5. **self-harm** - Content promoting or depicting self-harm
6. **self-harm/intent** - Expressed intent to engage in self-harm
7. **self-harm/instructions** - Instructions for committing self-harm
8. **sexual** - Content meant to arouse sexual excitement
9. **sexual/minors** - Sexual content involving minors
10. **violence** - Content promoting or glorifying violence
11. **violence/graphic** - Graphic depictions of violence or injury
12. **illicit** - Instructions for committing wrongdoing
13. **illicit/violent** - Instructions for violent wrongdoing

#### Image Moderation (6 Active Categories)
Currently supported multimodal categories:
- **violence** and **violence/graphic** - Visual violence detection
- **self-harm**, **self-harm/intent**, **self-harm/instructions** - Self-harm visual content
- **sexual** - Sexual visual content (excluding minors)

### Performance Characteristics

#### Accuracy Improvements
- **Overall Accuracy**: 42% improvement over legacy models
- **Multilingual Performance**: Superior detection in 40+ languages
- **Non-English Excellence**: Particularly strong in low-resource languages
- **Calibrated Scoring**: More accurate probability representations

#### Benchmark Results
- **Recall**: Enhanced detection of harmful content
- **Precision**: Higher false positive rate due to increased sensitivity
- **Multilingual Dataset**: Significant advantage over legacy models (0.322 vs 0.167)
- **Cross-Language Consistency**: 98% of tested languages show improvement

## API Usage Details

### Request Structure
```json
{
  "model": "omni-moderation-latest",
  "input": [
    {
      "type": "text",
      "text": "Text content to analyze"
    },
    {
      "type": "image_url", 
      "image_url": {
        "url": "https://example.com/image.png"
      }
    }
  ]
}
```

### Advanced Usage Patterns

#### Text-Only Moderation
```json
{
  "model": "omni-moderation-latest",
  "input": "Simple text string to moderate"
}
```

#### Image-Only Moderation
```json
{
  "model": "omni-moderation-latest",
  "input": [
    {
      "type": "image_url",
      "image_url": {
        "url": "https://example.com/suspicious-image.jpg"
      }
    }
  ]
}
```

### Response Analysis
```json
{
  "id": "modr-ABC123DEF456GHI789",
  "model": "omni-moderation-latest",
  "results": [
    {
      "flagged": true,
      "categories": {
        "sexual": false,
        "hate": true,
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
        "hate": 0.85,
        "sexual": 0.02,
        "violence": 0.01,
        "harassment": 0.45
      }
    }
  ]
}
```

## Pricing and Availability

### Cost Structure
- **Usage Fee**: Free for all OpenAI API users
- **Rate Limits**: Based on OpenAI tier (Free, Pay-as-you-go, Enterprise)
- **Billing Impact**: Does not count towards monthly token limits
- **Enterprise Support**: Available for high-volume applications

### Access Levels
- **Free Tier**: Basic rate limits
- **Pay-as-you-go**: Enhanced rate limits
- **Enterprise**: Custom rate limits and support

## Use Cases and Applications

### High-Volume Applications
1. **Social Media Platforms**: Real-time feed moderation
2. **Content Management Systems**: Automated content screening
3. **Educational Platforms**: Safe learning environment maintenance
4. **Gaming Communities**: Chat and user content moderation
5. **E-commerce Marketplaces**: Product listing review
6. **Corporate Communications**: Internal content compliance

### Specialized Applications
1. **Multilingual Platforms**: Global content moderation
2. **Visual Content Platforms**: Image and video screening
3. **User-Generated Content**: Community-driven platform safety
4. **Compliance Systems**: Regulatory requirement fulfillment
5. **Brand Safety**: Advertisement placement protection

### Industry Solutions
- Media and entertainment
- Social networking
- E-learning and education
- Gaming and virtual worlds
- Corporate communications
- Healthcare and wellness platforms

## Advanced Features

### Contextual Understanding
- **Multi-modal Context**: Understanding relationships between text and images
- **Cultural Sensitivity**: Improved handling of cultural context
- **Intent Recognition**: Better detection of harmful intent vs. educational content
- **Nuanced Analysis**: Sophisticated understanding of context and subtext

### Language Support
- **Primary Languages**: Excellent support for major world languages
- **Low-Resource Languages**: Significant improvements in less common languages
- **Code-Switching**: Handling of multilingual content within single inputs
- **Regional Variations**: Understanding of regional language differences

## Implementation Best Practices

### Threshold Management
1. **Default Thresholds**: Scores above 0.5-0.6 typically indicate violations
2. **Custom Thresholds**: Adjust based on platform requirements and risk tolerance
3. **Category-Specific Tuning**: Different thresholds for different harm categories
4. **A/B Testing**: Empirical threshold optimization

### Integration Patterns
1. **Real-time Moderation**: Immediate content screening
2. **Batch Processing**: Bulk content analysis
3. **Hybrid Approaches**: Combining automated and human review
4. **Appeals Handling**: Managing false positive appeals

### Monitoring and Optimization
1. **Performance Tracking**: Monitor accuracy and false positive rates
2. **Regular Audits**: Periodic review of moderation decisions
3. **Feedback Loops**: Incorporating human reviewer feedback
4. **Model Updates**: Staying current with automatic model upgrades

## Limitations and Considerations

### Current Constraints
1. **Image Category Coverage**: Limited to 6 of 13 categories for visual content
2. **Context Challenges**: Difficulty with highly contextual content (satire, art, education)
3. **Cultural Nuances**: May miss subtle cultural references or contexts
4. **Evolving Threats**: New forms of harmful content may require model updates

### Mitigation Strategies
1. **Human Oversight**: Combine with human moderators for comprehensive coverage
2. **Regular Updates**: Benefit from automatic model improvements
3. **Custom Training**: Consider fine-tuning for specific use cases
4. **Multi-Layer Approach**: Use alongside other safety measures

## Technical Integration

### API Endpoints
- **Primary Endpoint**: `https://api.openai.com/v1/moderations`
- **Authentication**: OpenAI API key required
- **HTTP Methods**: POST requests
- **Content-Type**: `application/json`

### SDKs and Libraries
- Official OpenAI Python library
- OpenAI Node.js library
- Community libraries for other languages
- REST API for custom implementations

### Error Handling
```json
{
  "error": {
    "message": "Invalid image format",
    "type": "invalid_request_error",
    "code": "invalid_image"
  }
}
```

## Model Evolution

### Automatic Updates
- **Version Management**: Automatically points to latest stable version
- **Backward Compatibility**: Maintains API compatibility
- **Performance Improvements**: Regular enhancements without code changes
- **New Features**: Automatic access to new capabilities

### Future Roadmap
- Expansion of image moderation to all categories
- Enhanced contextual understanding
- Improved multilingual capabilities
- Advanced multimodal reasoning