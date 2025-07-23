# GPT-4o Mini Realtime Preview

## Model Overview

The GPT-4o-mini-realtime-preview is a specialized variant of OpenAI's GPT-4o mini model designed for real-time, low-latency conversational interactions. It's part of the GPT-4o model family and supports "speech in, speech out" conversational interactions.

## Technical Specifications

- **Context window**: 128K tokens
- **Max output tokens**: Up to 16K tokens per request
- **Knowledge cutoff**: October 2023
- **Modalities**: Text and audio (speech)
- **Model family**: GPT-4o mini
- **API compatibility**: Realtime API via WebSocket/WebRTC

## Key Features

### 1. Real-time Capabilities
- Optimized for real-time, low-latency conversations with minimal delay
- Ideal for chatbots, voice assistants, and conversational AI applications
- Great fit for live interactions between users and models
- Supports customer support agents, voice assistants, and real-time translators

### 2. Multimodal Support
- Supports both "audio" and "text" modalities
- Speech-to-speech conversational capabilities
- Multilingual speech support
- Currently supports text and vision in the API, with expanded audio/video support coming

### 3. Performance Benchmarks
- Scores 82% on MMLU (Massive Multitask Language Understanding)
- Outperforms GPT-4 on chat preferences in LMSYS leaderboard
- Surpasses GPT-3.5 Turbo on academic benchmarks
- Strong performance in function calling for external system integration
- Demonstrates strong multimodal reasoning capabilities

### 4. Enhanced Tokenization
- Improved tokenizer shared with GPT-4o
- More cost-effective handling of non-English text
- Better performance across multilingual tasks

## Capabilities and Features

### Speech and Audio
- Real-time speech input and output
- Low-latency audio processing
- Natural conversation flow
- Multilingual speech capabilities

### Function Calling
- Strong function calling capabilities
- Enables applications to fetch data from external systems
- Supports actions with external APIs and services

### Safety Features
- First model to apply instruction hierarchy method
- Enhanced resistance to jailbreaks and prompt injections
- Improved system prompt extraction protection
- Multiple layers of safety protections
- Automated monitoring and human review of flagged content

## Pricing Information

### Standard GPT-4o Mini Pricing
- **Input tokens**: $0.15 per 1M tokens (15 cents per million)
- **Output tokens**: $0.60 per 1M tokens (60 cents per million)
- **Cost efficiency**: Order of magnitude more affordable than previous frontier models
- **Comparison**: More than 60% cheaper than GPT-3.5 Turbo

### Realtime API Pricing
- **Text input tokens**: $5.00 per 1M tokens
- **Text output tokens**: $20.00 per 1M tokens
- **Audio input tokens**: $100.00 per 1M tokens (~$0.06 per minute)
- **Audio output tokens**: $200.00 per 1M tokens (~$0.24 per minute)

### Cached Pricing (Available)
- **Cached text input**: $2.50 per 1M tokens
- **Cached audio input**: $20.00 per 1M tokens

## API Usage Details

### Supported APIs
- Assistants API
- Chat Completions API
- Batch API
- Realtime API (WebSocket/WebRTC)

### Connection Methods
- WebSocket connections for real-time audio
- WebRTC support for enhanced connectivity
- Standard REST API endpoints

### Voice Support
- Multiple voice options available
- Optimized for natural conversation
- Low-latency audio processing

## Performance Benchmarks

### Academic Performance
- **MMLU Score**: 82%
- **Chat Preferences**: Outperforms GPT-4 on LMSYS leaderboard
- **Multimodal Reasoning**: Strong performance across vision and text tasks
- **Function Calling**: Excellent performance in API integration scenarios

### Efficiency Metrics
- Low latency for real-time applications
- High throughput for batch processing
- Cost-effective token utilization

## Use Cases and Applications

### Customer Support
- Real-time customer service chatbots
- Voice-enabled support systems
- Multilingual customer interactions
- Automated query resolution

### Voice Assistants
- Personal assistant applications
- Smart home integrations
- Hands-free interfaces
- Voice-controlled systems

### Real-time Translation
- Live translation services
- Multilingual conversation facilitation
- Cross-language communication tools

### Development Applications
- Applications requiring multiple model calls
- Large volume context processing (full codebase analysis)
- Conversation history management
- Fast, real-time text responses

### Content Creation
- Interactive content generation
- Voice-based content creation
- Real-time storytelling applications

## Limitations and Considerations

### Current Limitations
- Preview model - not optimized for production traffic
- Limited to text and audio modalities (image support coming)
- Knowledge cutoff at October 2023
- Rate limits suitable primarily for testing and development

### Safety Considerations
- Requires careful monitoring for API abuse
- Subject to content filtering and safety protocols
- Human review processes for flagged content
- Adherence to OpenAI usage policies

### Technical Considerations
- Real-time requirements may impact latency in some scenarios
- Audio quality dependent on input source and network conditions
- WebSocket/WebRTC connection stability requirements

## Availability

### Platform Support
- OpenAI API Platform
- Microsoft Azure OpenAI Service
- Azure AI Foundry portal deployment

### Regional Availability
- Available through OpenAI's global infrastructure
- Azure deployments in specific regions

### Integration Support
- REST API compatibility
- WebSocket/WebRTC for real-time features
- Standard authentication and billing systems

## Safety and Security Features

### Built-in Safety
- Instruction hierarchy method implementation
- Enhanced jailbreak resistance
- Prompt injection protection
- System prompt extraction safeguards

### Monitoring and Review
- Automated content monitoring
- Human review for flagged interactions
- Multi-layer safety protection system
- Compliance with OpenAI safety standards

### Risk Assessment
- Comprehensive safety evaluations
- External red teaming with 70+ experts
- Testing across multiple risk categories
- Ongoing safety monitoring and improvements

The GPT-4o-mini-realtime-preview represents a cost-efficient solution for developers looking to build real-time, conversational AI applications with low latency requirements while maintaining strong performance across various tasks.