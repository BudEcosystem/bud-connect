# GPT-4o-Realtime-Preview Model Documentation

## Overview
GPT-4o-realtime-preview powers OpenAI's Realtime API, enabling developers to build low-latency, multimodal voice experiences. It supports natural speech-to-speech conversations through WebSocket connections, eliminating the need for separate transcription, reasoning, and text-to-speech steps.

## Model Variants
- **gpt-4o-realtime-preview**: Initial release
- **gpt-4o-realtime-preview-2024-12-17**: December 2024 version with improved voice quality, more reliable input handling, and 60%+ cheaper audio pricing

## Model Capabilities
- **Real-time Conversations**: Natural, low-latency voice interactions
- **Native Speech Processing**: Direct speech-to-speech without intermediate text
- **Emotion Preservation**: Maintains emotion, emphasis, and accents
- **Function Calling**: Trigger actions based on voice commands
- **Interruption Handling**: Supports natural conversation interruptions
- **WebRTC Support**: Easy integration with web applications
- **Multimodal**: Handles both text and audio inputs/outputs

## Technical Architecture

### Connection Type
- **Protocol**: WebSocket for persistent, bidirectional communication
- **Alternative**: WebRTC for simplified web integration
- **Endpoint**: Dedicated Realtime API endpoint
- **Session-based**: Maintains conversation context

### Input/Output Specifications
- **Audio Input**: Continuous audio streaming
- **Text Input**: Supported alongside audio
- **Audio Output**: Streaming speech synthesis
- **Text Output**: Optional text transcriptions
- **Formats**: Common audio formats supported

## Pricing Information

### Current Pricing (2024-12-17 version)
- **Text Input**: $5 per 1M tokens
- **Text Output**: $20 per 1M tokens
- **Audio Input**: $100 per 1M tokens (~$0.06/minute)
- **Audio Output**: $200 per 1M tokens (~$0.24/minute)
- **Note**: December version offers 60%+ reduction in audio costs

### Billing Details
- Charged per token for both text and audio
- Audio tokens calculated based on duration
- Text tokens standard GPT-4o rates
- Pay-as-you-go pricing model

## API Usage Examples

### WebSocket Connection Setup
```python
import websocket
import json

# Establish WebSocket connection
ws = websocket.WebSocket()
ws.connect("wss://api.openai.com/v1/realtime", 
           header={"Authorization": f"Bearer {api_key}"})

# Initialize session
session_config = {
    "type": "session.update",
    "session": {
        "model": "gpt-4o-realtime-preview",
        "voice": "alloy",
        "temperature": 0.7
    }
}
ws.send(json.dumps(session_config))
```

### Sending Audio Input
```python
# Send audio data
audio_event = {
    "type": "input_audio_buffer.append",
    "audio": base64_encoded_audio_chunk
}
ws.send(json.dumps(audio_event))

# Commit audio buffer
commit_event = {
    "type": "input_audio_buffer.commit"
}
ws.send(json.dumps(commit_event))
```

### Function Calling
```python
# Configure function
function_config = {
    "type": "session.update",
    "session": {
        "tools": [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    }
                }
            }
        }]
    }
}
ws.send(json.dumps(function_config))
```

### WebRTC Integration (Simplified)
```javascript
// JavaScript example for WebRTC
const pc = new RTCPeerConnection();

// Get audio stream
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
stream.getTracks().forEach(track => pc.addTrack(track, stream));

// Connect to OpenAI Realtime API via WebRTC
const response = await fetch('/api/openai/realtime/connect', {
    method: 'POST',
    body: JSON.stringify({ offer: await pc.createOffer() })
});
```

## Best Practices
1. **Connection Management**: Implement reconnection logic for stability
2. **Audio Quality**: Use good microphones and echo cancellation
3. **Interruption Handling**: Design for natural conversation flow
4. **Error Handling**: Gracefully handle connection drops
5. **Voice Selection**: Choose appropriate voice for use case
6. **Latency Optimization**: Use WebRTC for lowest latency
7. **Resource Management**: Close connections when not in use

## Limitations and Use Cases

### Limitations
- Requires persistent connection (WebSocket/WebRTC)
- Higher complexity than request-response APIs
- Limited to preset voices
- Requires real-time audio processing capability
- Beta status may have stability considerations
- Higher cost than text-only interactions

### Use Cases
- **Voice Assistants**: Real-time conversational AI assistants
- **Customer Service**: Live automated support agents
- **Language Learning**: Interactive conversation practice
- **Gaming**: Voice-controlled game characters
- **Accessibility**: Real-time audio interfaces
- **Telehealth**: Voice-based health consultations
- **Smart Home**: Natural voice control systems
- **Education**: Interactive tutoring systems
- **Entertainment**: Live AI performers or hosts
- **Translation**: Real-time voice translation

## Comparison with Audio Preview
| Feature | Realtime API | Audio Preview |
|---------|--------------|---------------|
| Latency | Low (real-time) | Higher (turn-based) |
| Connection | WebSocket/WebRTC | REST API |
| Streaming | Yes | No |
| Use Case | Live conversations | Async processing |
| Complexity | Higher | Lower |
| Interruptions | Natural | Not supported |

## Available Voices
- alloy
- echo  
- fable
- onyx
- nova
- shimmer
- ash (in some versions)
- ballad (in some versions)

## Safety Features
- Multiple layers of protection against abuse
- Automated monitoring of inputs/outputs
- Human review of flagged content
- Same safety infrastructure as ChatGPT Advanced Voice
- Compliance with OpenAI usage policies

## Additional Notes
- Requires paid OpenAI developer account
- Built on same model as ChatGPT Advanced Voice Mode
- Continuously improved with new versions
- WebRTC support added for easier web integration
- Supports same safety evaluations as GPT-4o
- Part of OpenAI's real-time multimodal strategy
- Beta status indicates ongoing development
- Future versions may add more voices and capabilities