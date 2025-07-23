# GPT-4o-Audio-Preview Model Documentation

## Overview
GPT-4o-audio-preview is OpenAI's multimodal model that enables native audio understanding and generation in the Chat Completions API. It allows developers to build applications that can process audio inputs and generate audio outputs alongside text, bringing voice capabilities to traditional chat interfaces.

## Model Variants
- **gpt-4o-audio-preview**: Initial release
- **gpt-4o-audio-preview-2024-10-01**: October 2024 version
- **gpt-4o-audio-preview-2024-12-17**: December 2024 version with improved voice quality

## Model Capabilities
- **Audio Input**: Process and understand spoken audio directly
- **Audio Output**: Generate natural speech responses
- **Text I/O**: Full text input/output capabilities maintained
- **Multimodal**: Can handle combinations of text and audio
- **Voice Preservation**: Maintains context of voice characteristics
- **Language Support**: Multilingual audio understanding and generation

## Input/Output Specifications

### Input
- **Text**: Standard text prompts
- **Audio**: 
  - Formats: Common audio formats supported
  - Duration: Subject to token limits
  - Quality: Best results with clear audio
- **Combined**: Mix of text and audio inputs in same request

### Output
- **Options**: Text only, audio only, or both text and audio
- **Audio Format**: Various formats supported (MP3, WAV, etc.)
- **Voice Selection**: Six preset voices available
- **Response Control**: Developer chooses output modality

## Pricing Information

### Token Costs
- **Text Input**: $5 per 1M tokens
- **Text Output**: $20 per 1M tokens
- **Audio Input**: $100 per 1M tokens (~$0.06/minute)
- **Audio Output**: $200 per 1M tokens (~$0.24/minute)
- **Combined Usage**: Billed separately for each modality

### Cost Optimization
- December 2024 version offers 60%+ cheaper audio pricing
- Text portions charged at standard rates
- Audio portions charged at audio rates

## API Usage Examples

### Basic Audio Input with Text Output
```python
import openai

response = openai.ChatCompletion.create(
  model="gpt-4o-audio-preview",
  messages=[
    {
      "role": "user",
      "content": {
        "type": "audio",
        "audio": {
          "data": audio_base64,
          "format": "mp3"
        }
      }
    }
  ],
  modalities=["text"]
)
```

### Text Input with Audio Output
```python
response = openai.ChatCompletion.create(
  model="gpt-4o-audio-preview",
  messages=[
    {
      "role": "user",
      "content": "Please explain quantum computing in simple terms."
    }
  ],
  modalities=["audio"],
  voice="alloy"
)
```

### Combined Audio I/O
```python
response = openai.ChatCompletion.create(
  model="gpt-4o-audio-preview",
  messages=[
    {
      "role": "user",
      "content": {
        "type": "audio",
        "audio": {
          "data": audio_base64,
          "format": "wav"
        }
      }
    }
  ],
  modalities=["text", "audio"],
  voice="nova"
)

# Access both text and audio responses
text_response = response.choices[0].message.content
audio_response = response.choices[0].message.audio
```

### Function Calling with Audio
```python
response = openai.ChatCompletion.create(
  model="gpt-4o-audio-preview",
  messages=[
    {
      "role": "user",
      "content": {
        "type": "audio",
        "audio": {"data": audio_base64}
      }
    }
  ],
  functions=[
    {
      "name": "set_alarm",
      "description": "Set an alarm for a specific time",
      "parameters": {
        "type": "object",
        "properties": {
          "time": {"type": "string"},
          "label": {"type": "string"}
        }
      }
    }
  ],
  modalities=["text", "audio"]
)
```

## Best Practices
1. **Audio Quality**: Provide clear, high-quality audio for best results
2. **Modality Selection**: Choose output modality based on use case
3. **Cost Management**: Use text output when audio isn't necessary
4. **Voice Consistency**: Stick to one voice per conversation
5. **Error Handling**: Implement fallbacks for audio processing failures
6. **Preprocessing**: Clean audio inputs to remove background noise

## Limitations and Use Cases

### Limitations
- Not real-time (use Realtime API for low-latency needs)
- Limited to preset voices
- Higher latency than text-only responses
- No custom voice cloning
- Audio size limits based on token constraints
- Sequential processing (not streaming)

### Use Cases
- **Voice Assistants**: Build conversational AI with voice
- **Accessibility Tools**: Audio interfaces for visually impaired users
- **Language Learning**: Practice conversations with pronunciation
- **Customer Service**: Automated voice response systems
- **Podcasting**: Generate audio content from text scripts
- **Voice Notes**: Transcribe and respond to voice messages
- **Multimodal Apps**: Applications requiring both text and voice
- **Education**: Interactive audio-based learning tools
- **Healthcare**: Voice-based patient interaction systems
- **Entertainment**: Interactive storytelling with voice

## Comparison with Realtime API
- **Realtime API**: For low-latency, streaming conversations
- **Audio Preview**: For turn-based, non-real-time interactions
- **Realtime API**: WebSocket-based continuous connection
- **Audio Preview**: REST API with request-response pattern
- **Choose Audio Preview**: When latency isn't critical
- **Choose Realtime**: For live conversations and streaming

## Available Voices
Same preset voices as other OpenAI audio models:
- alloy
- echo
- fable
- onyx
- nova
- shimmer

## Additional Notes
- Released as public beta for Chat Completions API
- Represents unified multimodal processing (no stitching required)
- Preserves emotion, emphasis, and accents better than pipeline approaches
- December 2024 version offers significant improvements
- Function calling fully supported with audio inputs
- Part of OpenAI's broader multimodal AI strategy
- Complements but doesn't replace Realtime API