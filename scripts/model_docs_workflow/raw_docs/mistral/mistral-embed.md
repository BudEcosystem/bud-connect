# Mistral Embed

## Model Overview

Mistral Embed is Mistral AI's state-of-the-art semantic model for extracting representations of text extracts. It converts text into high-dimensional vectors that capture semantic meaning, making it essential for retrieval-augmented generation (RAG) systems, semantic search, and various NLP applications.

## Architecture

### Embedding Model Design
- **Type:** Semantic text encoder
- **Purpose:** Convert text to dense vector representations
- **Output:** High-dimensional embeddings
- **Optimization:** Trained for semantic similarity and retrieval tasks

### Key Features
- State-of-the-art semantic understanding
- Optimized for retrieval tasks
- Efficient vector representations
- Multilingual capabilities

## Technical Specifications

- **Model Type:** Text embedding model
- **Output:** Dense vector embeddings
- **Use Case:** RAG, semantic search, text similarity
- **API Endpoint:** Various versions available
- **Related Model:** Codestral Embed (specialized for code)

### Codestral Embed Specifications
- **API Name:** `codestral-embed-2505`
- **Variable Dimensions:** Supports different output dimensions
- **Precision Options:** Including int8 for storage efficiency
- **Context Size:** Up to 8,192 tokens
- **Specialized:** Optimized for code retrieval

## Pricing Information

### Mistral Embed
- Check https://mistral.ai/pricing for current rates
- Priced per million tokens processed

### Codestral Embed
- **Price:** $0.15 per million tokens
- Cost-effective for code-specific applications

## API Usage Details

### Basic Usage
```python
from mistralai.client import MistralClient

client = MistralClient(api_key="your-api-key")

# Generate embeddings
response = client.embeddings(
    model="mistral-embed",
    input=["Text to embed", "Another text to embed"]
)

embeddings = [e.embedding for e in response.data]
```

### Codestral Embed Usage
```python
# For code-specific embeddings
response = client.embeddings(
    model="codestral-embed-2505",
    input=["def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"]
)
```

## Performance Benchmarks

### Mistral Embed Performance
- State-of-the-art retrieval accuracy
- Excellent semantic understanding
- Strong multilingual performance
- Optimized for various text lengths

### Codestral Embed Performance
- **Dimension 256 with int8:** Better than competitors
- Excellent trade-off between quality and storage
- Specialized for code understanding
- Superior performance on code retrieval tasks

## Use Cases and Applications

### Primary Applications

1. **Retrieval-Augmented Generation (RAG)**
   - Document retrieval
   - Knowledge base search
   - Context injection for LLMs
   - Question answering systems

2. **Semantic Search**
   - Enterprise search
   - Content discovery
   - Similar document finding
   - FAQ matching

3. **Text Similarity**
   - Duplicate detection
   - Content clustering
   - Recommendation systems
   - Paraphrase identification

4. **Code Search (Codestral Embed)**
   - Code snippet retrieval
   - Similar function finding
   - Documentation matching
   - Bug pattern detection

5. **Classification and Clustering**
   - Document categorization
   - Topic modeling
   - Content organization
   - Anomaly detection

## Deployment Options

### 1. API Integration
- Direct API access
- No infrastructure needed
- Automatic scaling
- Pay-per-use model

### 2. Batch Processing
- Efficient for large datasets
- Bulk embedding generation
- Optimized pricing for volume

### 3. Real-time Applications
- Low-latency access
- Suitable for search applications
- Interactive systems
- Live content matching

## Best Practices

### 1. Text Preprocessing
```python
def preprocess_text(text):
    # Clean and normalize text
    text = text.strip()
    text = " ".join(text.split())  # Normalize whitespace
    return text

# Preprocess before embedding
texts = [preprocess_text(t) for t in raw_texts]
embeddings = client.embeddings(model="mistral-embed", input=texts)
```

### 2. Chunking Strategies
```python
def chunk_text(text, max_tokens=8192):
    # Split long texts into chunks
    # Implementation depends on tokenizer
    chunks = []
    # ... chunking logic ...
    return chunks

# For long documents
chunks = chunk_text(long_document)
chunk_embeddings = client.embeddings(model="mistral-embed", input=chunks)
```

### 3. Storage Optimization (Codestral Embed)
```python
# Use reduced dimensions for storage efficiency
response = client.embeddings(
    model="codestral-embed-2505",
    input=texts,
    encoding_format="int8",  # If supported
    dimensions=256  # Reduced dimensions
)
```

## Integration Examples

### RAG System Implementation
```python
import numpy as np
from typing import List

class RAGSystem:
    def __init__(self, client):
        self.client = client
        self.documents = []
        self.embeddings = []
    
    def add_documents(self, docs: List[str]):
        # Generate embeddings for documents
        response = self.client.embeddings(
            model="mistral-embed",
            input=docs
        )
        
        self.documents.extend(docs)
        self.embeddings.extend([e.embedding for e in response.data])
    
    def search(self, query: str, top_k: int = 5):
        # Get query embedding
        query_response = self.client.embeddings(
            model="mistral-embed",
            input=[query]
        )
        query_embedding = query_response.data[0].embedding
        
        # Calculate similarities
        similarities = [
            np.dot(query_embedding, emb) / 
            (np.linalg.norm(query_embedding) * np.linalg.norm(emb))
            for emb in self.embeddings
        ]
        
        # Get top results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [(self.documents[i], similarities[i]) for i in top_indices]
```

### Semantic Search Engine
```python
from fastapi import FastAPI
import faiss

app = FastAPI()

# Initialize FAISS index
dimension = 1024  # Adjust based on model
index = faiss.IndexFlatL2(dimension)

@app.post("/index")
async def index_documents(documents: List[str]):
    # Generate embeddings
    response = client.embeddings(
        model="mistral-embed",
        input=documents
    )
    
    # Add to FAISS index
    embeddings = np.array([e.embedding for e in response.data])
    index.add(embeddings)
    
    return {"indexed": len(documents)}

@app.get("/search")
async def search(query: str, k: int = 10):
    # Get query embedding
    response = client.embeddings(
        model="mistral-embed",
        input=[query]
    )
    query_embedding = np.array([response.data[0].embedding])
    
    # Search in index
    distances, indices = index.search(query_embedding, k)
    
    return {"results": indices[0].tolist(), "distances": distances[0].tolist()}
```

## Optimization Tips

1. **Batch Processing**
   - Process multiple texts in single API call
   - Reduces overhead and costs
   - Improves throughput

2. **Caching**
   - Cache frequently used embeddings
   - Implement similarity threshold for cache hits
   - Reduce API calls

3. **Dimension Reduction**
   - Use PCA or other techniques post-processing
   - Balance quality vs storage
   - Consider application requirements

4. **Efficient Storage**
   - Use appropriate data types
   - Compress embeddings when possible
   - Index for fast retrieval