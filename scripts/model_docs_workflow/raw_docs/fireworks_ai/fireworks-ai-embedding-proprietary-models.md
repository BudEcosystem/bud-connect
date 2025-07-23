# Fireworks AI Proprietary Embedding Models

## Overview

Fireworks AI offers proprietary embedding models designed for high-scale text processing and semantic understanding. These models are specifically optimized for handling large token volumes and are priced competitively for enterprise applications.

## Models

### 1. fireworks-ai-embedding-up-to-150m

**Model Overview:**
- Designed to handle up to 150 million tokens
- Optimized for large-scale text processing and data retrieval
- Built for enterprise-grade applications requiring high throughput

**Architecture:**
- Model Type: Proprietary embedding model
- Token Capacity: Up to 150 million tokens
- Output: Vector embeddings (floating-point numbers)
- API Compatibility: OpenAI-compatible

**Key Features:**
- High-volume token processing capability
- Optimized for similarity comparisons and search
- Suitable for RAG (Retrieval-Augmented Generation) pipelines
- Fast inference with Fireworks AI's optimized infrastructure

### 2. fireworks-ai-embedding-150m-to-350m

**Model Overview:**
- Advanced model designed for handling 150-350 million tokens
- Higher capacity version for enterprise applications
- Enhanced performance for complex embedding tasks

**Architecture:**
- Model Type: Proprietary embedding model
- Token Capacity: 150-350 million tokens
- Output: Vector embeddings
- API Compatibility: OpenAI-compatible

**Key Features:**
- Extended token processing range
- Superior performance for large-scale applications
- Optimized for complex data retrieval scenarios
- Enterprise-grade reliability and performance

## Pricing

**Cost Structure:**
- **Input Pricing**: $0.008 per 1 million tokens
- **Output Pricing**: $0 (no charge for embedding vectors)
- **Billing Model**: Pay-per-token with postpaid billing
- **Rate Limits**: High rate limits suitable for enterprise use

**Cost Benefits:**
- Competitive pricing compared to other providers
- No output charges reduce total cost of ownership
- Transparent pricing with no hidden fees
- Cost-effective for high-volume applications

## Performance Characteristics

**Infrastructure:**
- Processing capacity: 140+ billion tokens daily
- API uptime: 99.99%
- Speed improvement: Up to 12x faster than vLLM, 40x faster than GPT-4
- Global availability with low latency

**Optimization:**
- Serverless deployment for easy scaling
- No cold start delays
- Optimized for batch processing
- Real-time inference capabilities

## API Usage

### Authentication
```python
import openai

client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<FIREWORKS_API_KEY>",
)
```

### Basic Embedding Generation
```python
response = client.embeddings.create(
    model="fireworks-ai-embedding-up-to-150m",
    input="Your text to embed here",
)

embeddings = response.data[0].embedding
```

### Batch Processing
```python
texts = ["Text 1", "Text 2", "Text 3"]
response = client.embeddings.create(
    model="fireworks-ai-embedding-150m-to-350m",
    input=texts,
)

embeddings = [data.embedding for data in response.data]
```

## Use Cases

### 1. Semantic Search
- Large-scale document retrieval
- Content recommendation systems
- Knowledge base search

### 2. Retrieval-Augmented Generation (RAG)
- Context retrieval for LLM responses
- Document similarity matching
- Information extraction pipelines

### 3. Data Analysis
- Clustering large text datasets
- Similarity analysis
- Content categorization

### 4. Enterprise Applications
- Customer support automation
- Content management systems
- Business intelligence applications

## Integration Examples

### LangChain Integration
```python
from langchain_fireworks import FireworksEmbeddings

embeddings = FireworksEmbeddings(
    model="fireworks-ai-embedding-up-to-150m",
    api_key="your-api-key"
)

vectors = embeddings.embed_documents(["document1", "document2"])
```

### Vector Database Integration
```python
# Example with Pinecone
import pinecone
from openai import OpenAI

client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<FIREWORKS_API_KEY>",
)

# Generate embeddings
response = client.embeddings.create(
    model="fireworks-ai-embedding-150m-to-350m",
    input="Document to embed"
)

# Store in vector database
pinecone.upsert(vectors=[(id, response.data[0].embedding, metadata)])
```

## Comparison with Other Providers

**Advantages:**
- Competitive pricing at $0.008 per 1M tokens
- No output charges
- High-volume token processing (150M-350M range)
- Superior infrastructure performance
- OpenAI-compatible API

**Target Scenarios:**
- High-volume enterprise applications
- Cost-sensitive deployments
- Performance-critical applications
- Large-scale RAG implementations

## Best Practices

1. **Batch Processing**: Use batch requests for multiple texts to optimize costs
2. **Token Management**: Monitor token usage for cost optimization
3. **Caching**: Implement caching for frequently accessed embeddings
4. **Error Handling**: Implement robust error handling for production use
5. **Rate Limiting**: Respect API rate limits for optimal performance

## Technical Specifications

**Model Capabilities:**
- Multilingual support (varies by model)
- Context length optimization
- Real-time processing
- Batch processing support

**Infrastructure:**
- Global CDN for low latency
- Auto-scaling capabilities
- High availability architecture
- Enterprise-grade security

## Support and Documentation

**Resources:**
- Official Fireworks AI documentation
- API reference guides
- Integration tutorials
- Community support forums

**Getting Started:**
1. Create a Fireworks AI account
2. Obtain API key
3. Install required SDK/libraries
4. Start with basic embedding examples
5. Scale to production use cases

---

*Last Updated: July 2025*
*For the most current pricing and specifications, visit the official Fireworks AI documentation.*