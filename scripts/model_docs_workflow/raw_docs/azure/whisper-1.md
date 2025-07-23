# Whisper-1 Model Documentation

## Overview
Whisper-1 is OpenAI's general-purpose speech recognition model based on the large-v2 version of the open-source Whisper model. It provides robust and accurate speech-to-text capabilities with support for multiple languages and automatic language detection.

## Model Capabilities
- **Multilingual Support**: Trained on diverse datasets with ~1/3 non-English content
- **Language Identification**: Automatic detection of spoken language
- **Transcription**: Converts speech to text in the original language
- **Translation**: Translates speech from any language to English
- **Robust Performance**: 50% fewer errors than specialized models across diverse datasets
- **Optimized Serving**: Highly optimized stack for faster API performance

## Input/Output Specifications

### Input
- **Supported Formats**: m4a, mp3, mp4, mpeg, mpga, wav, webm
- **Audio Length**: Split into 30-second chunks for processing
- **File Size Limit**: 25 MB maximum file size
- **Language**: Optional language parameter for better accuracy

### Output
- **Transcription**: Text in the original spoken language
- **Translation**: Text translated to English
- **Format**: JSON response with transcribed/translated text
- **Additional Metadata**: Optional timestamps and confidence scores

## Pricing Information
- **Cost**: $0.006 per minute of audio
- **Actual Usage**: Some users report costs closer to $0.010 per minute
- **Billing**: Based on audio duration, not file size
- **Pay-as-you-go**: Charged through OpenAI Platform

## API Usage Examples

### Basic Transcription
```python
import openai

# Transcribe audio in original language
with open("audio.mp3", "rb") as audio_file:
    response = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_file
    )
    
transcript = response["text"]
```

### Translation to English
```python
# Translate any language to English
with open("spanish_audio.mp3", "rb") as audio_file:
    response = openai.Audio.translate(
        model="whisper-1",
        file=audio_file
    )
    
english_translation = response["text"]
```

### With Language Hint
```python
# Provide language hint for better accuracy
response = openai.Audio.transcribe(
    model="whisper-1",
    file=audio_file,
    language="es"  # Spanish
)
```

### Advanced Options
```python
# Request timestamps
response = openai.Audio.transcribe(
    model="whisper-1",
    file=audio_file,
    response_format="verbose_json",
    timestamp_granularities=["word", "segment"]
)
```

## Best Practices
1. **Audio Quality**: Use high-quality audio recordings for best results
2. **File Format**: WAV or FLAC formats typically provide better quality
3. **Language Hints**: Provide language parameter when known for improved accuracy
4. **Chunk Size**: For long audio, split into smaller segments before processing
5. **Preprocessing**: Remove background noise and normalize audio levels
6. **Cost Management**: Monitor usage as actual costs may vary from listed price

## Limitations and Use Cases

### Limitations
- 25 MB file size limit per request
- No real-time streaming support (use Realtime API for that)
- Processing time depends on audio length
- May struggle with heavy accents or background noise
- English translation only (no other target languages)

### Use Cases
- Podcast and video transcription
- Meeting and interview transcription
- Multilingual content accessibility
- Voice note to text conversion
- Customer service call analysis
- Educational content transcription
- Legal and medical transcription
- Media monitoring and analysis
- Language learning applications
- Subtitle generation

## Additional Notes
- Based on the Whisper large-v2 model architecture
- Encoder-decoder Transformer architecture
- Trained on 680,000 hours of multilingual data
- Approaches human-level robustness on English speech
- The API version is optimized for speed compared to open-source version
- Supports automatic punctuation and capitalization
- Can handle multiple speakers but doesn't provide speaker diarization
- For real-time applications, consider the new Realtime API instead