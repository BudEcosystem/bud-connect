# TTS-1 Model Documentation

## Overview
TTS-1 is OpenAI's standard text-to-speech model that converts written text into natural-sounding spoken audio. It offers a balance between quality and speed, making it suitable for real-time applications and general text-to-speech needs.

## Model Capabilities
- **Natural Voice Generation**: Produces human-like speech from text input
- **Multiple Voice Options**: Several pre-built voice profiles to choose from
- **Language Support**: Supports multiple languages and accents
- **Speed Control**: Adjustable speech rate
- **Streaming Support**: Can stream audio for real-time applications
- **Voice Steering**: Can be instructed to speak in specific tones, styles, or accents

## Input/Output Specifications

### Input
- **Type**: Text string
- **Character Limit**: Based on token limits of the underlying model
- **Voice Selection**: Choose from available voice presets
- **Speed Parameter**: Adjustable playback speed (0.25 to 4.0)
- **Language**: Automatic language detection from input text

### Output
- **Audio Formats**: MP3, OPUS, AAC, FLAC, WAV, PCM
- **Sample Rate**: Varies by format (typically 24kHz)
- **Streaming**: Supports chunk-based streaming for lower latency
- **File Output**: Direct file generation or streaming response

## Pricing Information
- **Cost**: $0.015 per 1,000 characters
- **Billing**: Based on input character count
- **Fractional Billing**: Charged for exact character usage (not rounded to 1,000)
- **Comparison**: Half the cost of TTS-1-HD model

## Available Voices
Current voice options include:
- **alloy**: Neutral and balanced
- **echo**: Warm and conversational  
- **fable**: Expressive and dynamic
- **onyx**: Deep and authoritative
- **nova**: Friendly and upbeat
- **shimmer**: Gentle and pleasant
- **Additional voices**: ash, ballad, coral, sage (availability may vary)

## API Usage Examples

### Basic Text-to-Speech
```python
import openai

response = openai.Audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="Hello, this is a text-to-speech example."
)

# Save to file
response.stream_to_file("output.mp3")
```

### With Speed Control
```python
response = openai.Audio.speech.create(
  model="tts-1",
  voice="nova",
  input="This will be spoken at a faster speed.",
  speed=1.5  # 1.5x speed
)
```

### Streaming Response
```python
response = openai.Audio.speech.create(
  model="tts-1",
  voice="echo",
  input="This audio will be streamed.",
  response_format="mp3"
)

# Stream to file
with open("streamed_audio.mp3", "wb") as file:
    for chunk in response.iter_bytes():
        file.write(chunk)
```

### Different Output Formats
```python
# High-quality WAV format
response = openai.Audio.speech.create(
  model="tts-1",
  voice="fable",
  input="High quality audio output.",
  response_format="wav"
)

# Compressed OPUS format
response = openai.Audio.speech.create(
  model="tts-1",
  voice="onyx",
  input="Compressed for streaming.",
  response_format="opus"
)
```

## Best Practices
1. **Voice Selection**: Test different voices to find the best match for your use case
2. **Text Preparation**: Clean and format text properly (remove special characters if needed)
3. **Chunking**: For long texts, consider splitting into smaller segments
4. **Caching**: Cache generated audio for frequently used phrases
5. **Format Choice**: Use MP3 for general use, OPUS for streaming, WAV for editing
6. **Speed Settings**: Keep between 0.5-2.0 for natural sounding speech

## Limitations and Use Cases

### Limitations
- Lower audio quality compared to TTS-1-HD
- Limited to preset voices (no custom voice cloning)
- No fine-grained prosody control
- May have slight artifacts in complex pronunciations
- Voice consistency can vary with different inputs
- No support for SSML markup

### Use Cases
- Accessibility features for applications
- Podcast and audiobook generation
- Voice assistants and chatbots
- Educational content narration
- Real-time voice responses
- Navigation and announcement systems
- Language learning applications
- Content creation for social media
- Interactive voice response (IVR) systems
- Gaming and entertainment narration

## Additional Notes
- TTS-1 prioritizes speed over quality for real-time applications
- For higher quality output, consider TTS-1-HD (at double the cost)
- Voices are synthetic presets monitored for consistency
- The model supports emotional context through prompt engineering
- New voice options may be added over time
- Audio is generated on-demand (not pre-recorded)
- Suitable for commercial use with proper attribution
- Consider user preferences for voice selection in applications