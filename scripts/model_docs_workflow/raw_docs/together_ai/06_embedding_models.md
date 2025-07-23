# Together AI Embedding Models

## Overview

Together AI provides access to high-quality embedding models that transform text into numerical vector representations. These embeddings are essential for building search systems, recommendation engines, and Retrieval Augmented Generation (RAG) applications.

## Available Embedding Models

### BAAI BGE Series

#### BAAI/bge-base-en-v1.5
- **API String**: `BAAI/bge-base-en-v1.5`
- **Model Size**: Base (110M parameters)
- **Language**: English
- **Embedding Dimensions**: 768
- **Max Input Length**: 512 tokens
- **Pricing**: $0.008 per 1M tokens (input only)
- **Use Case**: General-purpose English text embeddings

#### BAAI/bge-large-en-v1.5
- **API String**: `BAAI/bge-large-en-v1.5`
- **Model Size**: Large (335M parameters)
- **Language**: English
- **Embedding Dimensions**: 1024
- **Max Input Length**: 512 tokens
- **Pricing**: $0.015 per 1M tokens (input only)
- **Use Case**: Higher quality embeddings for critical applications

#### BAAI/bge-small-en-v1.5
- **API String**: `BAAI/bge-small-en-v1.5`
- **Model Size**: Small (33M parameters)
- **Language**: English
- **Embedding Dimensions**: 384
- **Max Input Length**: 512 tokens
- **Pricing**: $0.005 per 1M tokens (input only)
- **Use Case**: Cost-effective embeddings for large-scale applications

### Multilingual Models

#### BAAI/bge-m3
- **API String**: `BAAI/bge-m3`
- **Model Size**: ~568M parameters
- **Languages**: 100+ languages
- **Embedding Dimensions**: 1024
- **Max Input Length**: 8192 tokens
- **Pricing**: $0.02 per 1M tokens (input only)
- **Features**:
  - Multi-Functionality: Dense, sparse, and multi-vector retrieval
  - Multi-Linguality: 100+ working languages
  - Multi-Granularity: Short sentences to long documents

#### sentence-transformers/all-MiniLM-L6-v2
- **API String**: `sentence-transformers/all-MiniLM-L6-v2`
- **Model Size**: 22M parameters
- **Language**: English
- **Embedding Dimensions**: 384
- **Max Input Length**: 256 tokens
- **Pricing**: $0.005 per 1M tokens (input only)
- **Use Case**: Lightweight, fast embeddings

### Specialized Models

#### WhereIsAI/UAE-Large-V1
- **API String**: `WhereIsAI/UAE-Large-V1`
- **Model Size**: Large
- **Specialization**: Universal Angle Embeddings
- **Embedding Dimensions**: 1024
- **Pricing**: $0.015 per 1M tokens (input only)
- **Features**: Optimized for semantic similarity tasks

#### togethercomputer/m2-bert-80M-8k-retrieval
- **API String**: `togethercomputer/m2-bert-80M-8k-retrieval`
- **Model Size**: 80M parameters
- **Max Input Length**: 8192 tokens
- **Embedding Dimensions**: 768
- **Pricing**: $0.01 per 1M tokens (input only)
- **Specialization**: Long context retrieval tasks

## Pricing Structure

### Cost Tiers (per 1M input tokens)
- **Small Models (< 50M params)**: $0.005
- **Base Models (50M-150M params)**: $0.008-$0.01
- **Large Models (150M-400M params)**: $0.015
- **Specialized/Multilingual**: $0.02

### Billing Notes
- **Input Only**: Only input tokens are charged for embeddings
- **No Output Costs**: No charges for the embedding vectors themselves
- **Batch Discounts**: 50% discount available for batch processing

## API Usage Examples

### Basic Embedding Generation (Python)
```python
from together import Together

client = Together(api_key="your_api_key")

# Single text embedding
response = client.embeddings.create(
    model="BAAI/bge-base-en-v1.5",
    input="Our solar system orbits the Milky Way galaxy at about 515,000 mph"
)

embedding = response.data[0].embedding
print(f"Embedding dimensions: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
```

### Multiple Text Embeddings
```python
texts = [
    "Machine learning is a subset of artificial intelligence.",
    "Deep learning uses neural networks with multiple layers.",
    "Natural language processing helps computers understand human language."
]

response = client.embeddings.create(
    model="BAAI/bge-large-en-v1.5",
    input=texts
)

embeddings = [data.embedding for data in response.data]
print(f"Generated {len(embeddings)} embeddings")
```

### Multilingual Embeddings
```python
multilingual_texts = [
    "Hello, how are you?",
    "Bonjour, comment allez-vous?",
    "Hola, ¿cómo estás?",
    "こんにちは、元気ですか？"
]

response = client.embeddings.create(
    model="BAAI/bge-m3",
    input=multilingual_texts
)

embeddings = [data.embedding for data in response.data]
```

### Long Document Embedding
```python
long_document = """
[Your long document content here - up to 8192 tokens for bge-m3]
"""

response = client.embeddings.create(
    model="BAAI/bge-m3",  # Supports up to 8K tokens
    input=long_document
)

document_embedding = response.data[0].embedding
```

### JavaScript/TypeScript Usage
```javascript
import Together from 'together-ai';

const together = new Together({
    apiKey: process.env.TOGETHER_API_KEY
});

const response = await together.embeddings.create({
    model: 'BAAI/bge-base-en-v1.5',
    input: ['Text to embed', 'Another text to embed']
});

const embeddings = response.data.map(item => item.embedding);
console.log(`Generated ${embeddings.length} embeddings`);
```

### cURL Example
```bash
curl -X POST https://api.together.xyz/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -d '{
    "model": "BAAI/bge-base-en-v1.5",
    "input": ["Text to embed", "Another text"]
  }'
```

## Similarity Calculation

### Cosine Similarity (Python)
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Generate embeddings for comparison
texts = ["Artificial intelligence", "Machine learning", "Cooking recipes"]

response = client.embeddings.create(
    model="BAAI/bge-base-en-v1.5",
    input=texts
)

embeddings = np.array([data.embedding for data in response.data])

# Calculate similarity matrix
similarity_matrix = cosine_similarity(embeddings)
print("Similarity between AI and ML:", similarity_matrix[0][1])
print("Similarity between AI and Cooking:", similarity_matrix[0][2])
```

### Vector Database Integration
```python
# Example with Pinecone
import pinecone

# Initialize Pinecone
pinecone.init(api_key="your_pinecone_key", environment="your_env")

# Create or connect to index
index = pinecone.Index("embedding-index")

# Generate embedding and upsert
response = client.embeddings.create(
    model="BAAI/bge-base-en-v1.5",
    input="Document to store"
)

embedding = response.data[0].embedding

# Store in vector database
index.upsert([
    ("doc_1", embedding, {"text": "Document to store"})
])
```

## Model Selection Guide

### By Use Case

| Use Case | Recommended Model | Reasoning |
|----------|------------------|-----------|
| General RAG | BAAI/bge-base-en-v1.5 | Good balance of quality and cost |
| High-Quality Search | BAAI/bge-large-en-v1.5 | Best quality for English |
| Large-Scale/Cost-Sensitive | BAAI/bge-small-en-v1.5 | Lowest cost |
| Multilingual | BAAI/bge-m3 | 100+ languages support |
| Long Documents | BAAI/bge-m3 | 8K token context |
| Quick Prototyping | sentence-transformers/all-MiniLM-L6-v2 | Fast and lightweight |
| Semantic Similarity | WhereIsAI/UAE-Large-V1 | Optimized for similarity |

### By Performance Requirements

| Requirement | Model Choice | Trade-offs |
|-------------|--------------|------------|
| Highest Quality | bge-large-en-v1.5 | Higher cost |
| Best Value | bge-base-en-v1.5 | Balanced |
| Lowest Cost | bge-small-en-v1.5 or all-MiniLM-L6-v2 | Lower quality |
| Speed | all-MiniLM-L6-v2 | Fastest processing |
| Multilingual | bge-m3 | Higher cost but versatile |

## Performance Characteristics

### BGE Model Family Strengths
1. **High Quality**: State-of-the-art performance on retrieval benchmarks
2. **Versatility**: Good performance across different domains
3. **Efficiency**: Optimized for production use
4. **Open Source**: Transparent and reproducible

### BGE-M3 Special Features
1. **Multi-Functionality**: 
   - Dense retrieval (traditional semantic search)
   - Sparse retrieval (keyword-based)
   - Multi-vector retrieval (fine-grained matching)
2. **Multi-Linguality**: Native support for 100+ languages
3. **Multi-Granularity**: From sentences to 8K token documents

## Rate Limits and Quotas

### Free Tier
- **Starting Credit**: $1 for new accounts
- **Rate Limits**: Standard API limits
- **Model Access**: All embedding models available

### Production Usage
- **Higher Limits**: Increased requests per minute
- **Batch Processing**: 50% discount for batch jobs
- **Priority Queue**: Faster processing for paid accounts

## Best Practices

### Optimization Strategies
1. **Model Selection**: Choose appropriate model for your quality/cost requirements
2. **Batch Processing**: Process multiple texts together for efficiency
3. **Caching**: Store embeddings to avoid recomputation
4. **Preprocessing**: Clean and normalize text before embedding
5. **Dimension Reduction**: Consider PCA if storage is a concern

### Text Preprocessing
```python
import re

def preprocess_text(text):
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove special characters if needed
    text = re.sub(r'[^\w\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    return text

# Use with embeddings
clean_text = preprocess_text("Your text here!!!")
response = client.embeddings.create(
    model="BAAI/bge-base-en-v1.5",
    input=clean_text
)
```

### RAG Implementation Example
```python
class RAGSystem:
    def __init__(self, embedding_model="BAAI/bge-base-en-v1.5"):
        self.client = Together(api_key="your_api_key")
        self.model = embedding_model
        self.document_store = []
        self.embeddings = []
    
    def add_documents(self, documents):
        # Generate embeddings for documents
        response = self.client.embeddings.create(
            model=self.model,
            input=documents
        )
        
        new_embeddings = [data.embedding for data in response.data]
        self.embeddings.extend(new_embeddings)
        self.document_store.extend(documents)
    
    def search(self, query, top_k=5):
        # Generate query embedding
        query_response = self.client.embeddings.create(
            model=self.model,
            input=query
        )
        query_embedding = query_response.data[0].embedding
        
        # Calculate similarities
        similarities = cosine_similarity(
            [query_embedding], 
            self.embeddings
        )[0]
        
        # Get top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = [(self.document_store[i], similarities[i]) for i in top_indices]
        
        return results
```

## Comparison with Other Providers

### Together AI Advantages
- **Competitive Pricing**: Often lower cost than alternatives
- **No Output Charges**: Only pay for input tokens
- **Batch Discounts**: Additional cost savings
- **Multiple Models**: Wide selection of embedding models
- **OpenAI Compatibility**: Easy integration

### Quality Benchmarks
- **BGE Models**: Top performers on MTEB benchmark
- **Multilingual Support**: bge-m3 excels in cross-lingual tasks
- **Long Context**: Extended token support for documents

## Official Resources

- **Embedding Documentation**: https://docs.together.ai/docs/embeddings-overview
- **Model List**: https://docs.together.ai/docs/serverless-models
- **Pricing**: https://www.together.ai/pricing
- **BGE Official**: https://bge-model.com/
- **Hugging Face**: Model cards and examples

## Support and Community

- **Together AI Support**: Technical assistance
- **BGE Community**: Model-specific discussions
- **GitHub**: Open-source implementations
- **Documentation**: Comprehensive guides and examples