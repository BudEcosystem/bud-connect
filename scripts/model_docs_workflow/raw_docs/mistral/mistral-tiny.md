# Mistral Tiny (Deprecated)

## Model Overview

**IMPORTANT:** The `mistral-tiny` endpoint has been deprecated as of May 2024. Users should migrate to `open-mistral-7b`.

Mistral Tiny was the original endpoint name for what is now known as `open-mistral-7b` (Mistral 7B). This was Mistral AI's first released model and remains one of the most powerful language models for its size.

## Architecture

The underlying model (Mistral 7B) features:
- **Sliding Window Attention (SWA):** Each layer attends to the previous 4,096 hidden states
- **Transformer architecture:** 7B parameters
- **Fast deployment:** Optimized for quick inference
- **Easily customizable:** Designed for fine-tuning

## Technical Specifications

- **Parameters:** 7 billion
- **Context Window:** 8K tokens (with SWA mechanism)
- **License:** Apache 2.0 (open source)
- **Model ID:** `open-mistral-7b` (previously `mistral-tiny-2312`)

## Pricing Information

As an open-source model under Apache 2.0:
- **Self-hosted:** Free (infrastructure costs only)
- **API Access:** Check current pricing at https://mistral.ai/pricing

## API Usage Details

**Migration Required:**
- Old endpoint: `mistral-tiny` (deprecated)
- New endpoint: `open-mistral-7b`

Usage example:
```python
# Old (deprecated)
model="mistral-tiny"

# New
model="open-mistral-7b"
```

## Performance Benchmarks

- Significantly outperforms Llama 2 13B on all metrics
- On par with Llama 34B despite being much smaller
- Optimized for efficiency and speed
- Strong performance across various NLP tasks

## Use Cases and Applications

- Text generation
- Code completion
- Question answering
- Summarization
- General-purpose language understanding
- Edge deployments requiring smaller models

## Deployment Options

1. **Open Source Deployment:**
   - Download weights from Hugging Face
   - Deploy on own infrastructure
   - No usage restrictions under Apache 2.0

2. **API Access:**
   - Via La Plateforme using `open-mistral-7b`
   - Serverless option available

3. **Edge Deployment:**
   - Suitable for deployment on smaller hardware
   - Optimized for resource-constrained environments

## Migration Guide

For users migrating from `mistral-tiny`:
1. Update model endpoint to `open-mistral-7b`
2. No changes needed to input/output format
3. Performance characteristics remain the same
4. Cost structure may differ on API vs self-hosted