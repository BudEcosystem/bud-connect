# Nomic AI Embedding Models - nomic-embed-text-v1 & v1.5

## Overview

Nomic AI's embedding models represent a breakthrough in open-source text embeddings, offering superior performance compared to closed-source alternatives like OpenAI's text-embedding-ada-002. These models are specifically designed for long-context understanding and reproducible embedding generation.

## Model Specifications

### nomic-ai/nomic-embed-text-v1

**Core Specifications:**
- **Embedding Dimensions**: Variable (64-768), typically 768
- **Context Length**: 8192 tokens
- **Model Type**: Contrastive learning-based transformer
- **License**: Apache 2.0 (fully open source)
- **Architecture**: Custom transformer optimized for embedding tasks

### nomic-ai/nomic-embed-text-v1.5

**Core Specifications:**
- **Embedding Dimensions**: Variable (64-768), default 768
- **Context Length**: 8192 tokens  
- **Model Type**: Enhanced contrastive learning transformer
- **License**: Apache 2.0 (fully open source)
- **Improvements**: Enhanced training data and methodology over v1

**Variable Dimension Support:**
Both models support adjustable embedding dimensions from 64 to 768, allowing users to balance performance and computational efficiency based on their specific use case requirements.

## Performance Benchmarks

### MTEB (Massive Text Embedding Benchmark)
- **nomic-embed-text-v1**: Outperforms text-embedding-ada-002 and jina-embeddings-v2-base-en
- **nomic-embed-text-v1.5**: Superior performance at both 512 and 768 dimensions
- **Ranking**: Among top open-source models on MTEB leaderboard

### Long Context Performance (LoCo Benchmark)
- **nomic-embed-text-v1**: Only open-source model to outperform text-embedding-ada-002 and text-embedding-3-small on long context tasks
- **Context Advantage**: 8192 tokens vs 512 for many competitors
- **Use Case**: Ideal for document-level embeddings and long-form content

### Comparative Performance
| Model | MTEB Score | Context Length | Dimensions | Open Source |
|-------|------------|----------------|------------|-------------|
| nomic-embed-text-v1.5 | ~62.0 | 8192 | 768 | ✅ |
| nomic-embed-text-v1 | ~60.5 | 8192 | 768 | ✅ |
| text-embedding-ada-002 | ~61.0 | 8191 | 1536 | ❌ |
| text-embedding-3-small | ~62.3 | 8191 | 1536 | ❌ |

## API Usage with Fireworks AI

### Authentication Setup
```python
import openai

client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<FIREWORKS_API_KEY>",
)
```

### Basic Embedding Generation
```python
# Using nomic-embed-text-v1.5
response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1.5",
    input="Your text to embed here"
)

embedding = response.data[0].embedding
print(f"Embedding dimension: {len(embedding)}")  # Default dimension
```

### Variable Dimension Example
```python
# Request specific dimension size
response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1.5",
    input="Sample text for embedding",
    dimensions=512  # Specify desired dimension
)

embedding = response.data[0].embedding
print(f"Embedding dimension: {len(embedding)}")  # Output: 512
```

### Long Context Processing
```python
# Process long documents (up to 8192 tokens)
long_document = """
[Insert long document text here - up to 8192 tokens]
Multiple paragraphs, articles, or documentation...
"""

response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1.5",
    input=long_document
)

long_doc_embedding = response.data[0].embedding
```

### Batch Processing
```python
texts = [
    "Short text example",
    "Medium length text with more content and details",
    "Very long text that could be several paragraphs with extensive information..."
]

response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1",
    input=texts,
    dimensions=768
)

embeddings = [data.embedding for data in response.data]
```

## Pricing with Fireworks AI

**Cost Structure:**
- **Input Pricing**: $0.008 per 1 million tokens
- **Output Pricing**: $0 (no charge for embeddings)
- **Long Context Advantage**: More content per API call due to 8192 token limit
- **Cost Efficiency**: Reduced API calls needed for long documents

**Cost Comparison Example:**
```python
# Processing a 4000-token document
# Nomic models: 1 API call = $0.008 * (4000/1M) = $0.000032
# Shorter context models: Multiple calls needed = Higher cost
```

## Use Cases and Applications

### 1. Long Document Processing
```python
# Research paper or documentation embedding
def embed_research_paper(paper_text):
    # Nomic can handle full papers in single call
    response = client.embeddings.create(
        model="nomic-ai/nomic-embed-text-v1.5",
        input=paper_text[:8192*4]  # Conservative token estimate
    )
    return response.data[0].embedding

# Legal document analysis
def process_legal_document(legal_text):
    response = client.embeddings.create(
        model="nomic-ai/nomic-embed-text-v1.5",
        input=legal_text,
        dimensions=768
    )
    return response.data[0].embedding
```

### 2. Advanced RAG Implementation
```python
import numpy as np
from scipy.spatial.distance import cosine

class NomicRAGRetriever:
    def __init__(self, documents):
        self.documents = documents
        self.embeddings = self._embed_documents()
    
    def _embed_documents(self):
        embeddings = []
        for doc in self.documents:
            response = client.embeddings.create(
                model="nomic-ai/nomic-embed-text-v1.5",
                input=doc,
                dimensions=768
            )
            embeddings.append(response.data[0].embedding)
        return embeddings
    
    def retrieve(self, query, top_k=5):
        # Embed query
        query_response = client.embeddings.create(
            model="nomic-ai/nomic-embed-text-v1.5",
            input=query,
            dimensions=768
        )
        query_embedding = query_response.data[0].embedding
        
        # Calculate similarities
        similarities = []
        for doc_embedding in self.embeddings:
            similarity = 1 - cosine(query_embedding, doc_embedding)
            similarities.append(similarity)
        
        # Get top-k documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]

# Usage
documents = ["Long document 1...", "Long document 2...", ...]
retriever = NomicRAGRetriever(documents)
relevant_docs = retriever.retrieve("What is the main finding?")
```

### 3. Semantic Search with Variable Dimensions
```python
class AdaptiveSemanticSearch:
    def __init__(self, corpus, dimension=768):
        self.corpus = corpus
        self.dimension = dimension
        self.index = self._build_index()
    
    def _build_index(self):
        embeddings = []
        for text in self.corpus:
            response = client.embeddings.create(
                model="nomic-ai/nomic-embed-text-v1.5",
                input=text,
                dimensions=self.dimension
            )
            embeddings.append(response.data[0].embedding)
        return embeddings
    
    def search(self, query, top_k=10):
        query_response = client.embeddings.create(
            model="nomic-ai/nomic-embed-text-v1.5",
            input=query,
            dimensions=self.dimension
        )
        query_embedding = query_response.data[0].embedding
        
        similarities = [
            1 - cosine(query_embedding, doc_emb) 
            for doc_emb in self.index
        ]
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = [
            {"text": self.corpus[i], "score": similarities[i]} 
            for i in top_indices
        ]
        return results

# Flexible dimension usage
# High accuracy: 768 dimensions
search_high = AdaptiveSemanticSearch(corpus, dimension=768)

# Balanced: 512 dimensions  
search_balanced = AdaptiveSemanticSearch(corpus, dimension=512)

# Fast/storage efficient: 256 dimensions
search_fast = AdaptiveSemanticSearch(corpus, dimension=256)
```

### 4. Multilingual and Cross-lingual Applications
```python
def cross_lingual_similarity(text1, text2, lang1="en", lang2="en"):
    """
    Compare texts across languages using Nomic embeddings
    """
    response1 = client.embeddings.create(
        model="nomic-ai/nomic-embed-text-v1.5",
        input=f"[{lang1}] {text1}",  # Language prefix for better performance
        dimensions=768
    )
    
    response2 = client.embeddings.create(
        model="nomic-ai/nomic-embed-text-v1.5",
        input=f"[{lang2}] {text2}",
        dimensions=768
    )
    
    similarity = 1 - cosine(
        response1.data[0].embedding, 
        response2.data[0].embedding
    )
    return similarity

# Example usage
similarity = cross_lingual_similarity(
    "Hello, how are you?", 
    "Hola, ¿cómo estás?", 
    "en", 
    "es"
)
```

## Advanced Features

### 1. Reproducible Embeddings
```python
def reproducible_embed(text, seed=42):
    """
    Generate reproducible embeddings for the same input
    """
    # Nomic models are designed for reproducibility
    response = client.embeddings.create(
        model="nomic-ai/nomic-embed-text-v1.5",
        input=text,
        dimensions=768
    )
    return response.data[0].embedding

# Same input will always produce same embedding
embedding1 = reproducible_embed("Test text")
embedding2 = reproducible_embed("Test text")
# embedding1 == embedding2 (within floating point precision)
```

### 2. Dimension Optimization
```python
def find_optimal_dimension(texts, dimensions=[128, 256, 512, 768]):
    """
    Test different dimensions to find optimal performance/efficiency balance
    """
    results = {}
    
    for dim in dimensions:
        embeddings = []
        for text in texts[:100]:  # Sample for testing
            response = client.embeddings.create(
                model="nomic-ai/nomic-embed-text-v1.5",
                input=text,
                dimensions=dim
            )
            embeddings.append(response.data[0].embedding)
        
        # Calculate average pairwise similarity spread (quality metric)
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i+1, len(embeddings)):
                sim = 1 - cosine(embeddings[i], embeddings[j])
                similarities.append(sim)
        
        std_dev = np.std(similarities)  # Higher std = better discrimination
        results[dim] = {
            'dimension': dim,
            'std_dev': std_dev,
            'storage_per_embedding': dim * 4,  # bytes (float32)
            'quality_score': std_dev / (dim * 4) * 1000  # Quality per byte
        }
    
    return results
```

### 3. Streaming and Chunking for Very Long Texts
```python
def embed_very_long_text(text, max_tokens=7000):
    """
    Handle texts longer than 8192 tokens by intelligent chunking
    """
    # Simple word-based chunking (improve with sentence boundaries)
    words = text.split()
    chunk_size = max_tokens // 2  # Conservative word estimate
    
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    # Embed each chunk
    chunk_embeddings = []
    for chunk in chunks:
        response = client.embeddings.create(
            model="nomic-ai/nomic-embed-text-v1.5",
            input=chunk,
            dimensions=768
        )
        chunk_embeddings.append(response.data[0].embedding)
    
    # Combine embeddings (average or weighted average)
    combined_embedding = np.mean(chunk_embeddings, axis=0).tolist()
    return combined_embedding
```

## Model Comparison: v1 vs v1.5

### Key Improvements in v1.5
1. **Enhanced Training Data**: Larger and more diverse training corpus
2. **Improved Methodology**: Refined contrastive learning approach
3. **Better Performance**: Superior results on both short and long context benchmarks
4. **Dimension Flexibility**: Better performance across variable dimensions

### Migration from v1 to v1.5
```python
def migrate_embeddings(texts, old_model="nomic-ai/nomic-embed-text-v1", 
                      new_model="nomic-ai/nomic-embed-text-v1.5"):
    """
    Migrate existing embeddings from v1 to v1.5
    """
    new_embeddings = []
    for text in texts:
        response = client.embeddings.create(
            model=new_model,
            input=text,
            dimensions=768
        )
        new_embeddings.append(response.data[0].embedding)
    
    return new_embeddings
```

## Integration Examples

### LangChain Integration
```python
from langchain_fireworks import FireworksEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize with Nomic model
embeddings = FireworksEmbeddings(
    model="nomic-ai/nomic-embed-text-v1.5",
    api_key="your-fireworks-api-key"
)

# Text splitter optimized for long context
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=6000,  # Leverage long context capability
    chunk_overlap=500,
    length_function=len,
)

# Create vector store
texts = text_splitter.split_text(long_document)
vectorstore = FAISS.from_texts(texts, embeddings)

# Search with long context
results = vectorstore.similarity_search(
    "Complex query requiring long context understanding", 
    k=5
)
```

### Pinecone Integration
```python
import pinecone

# Initialize Pinecone
pinecone.init(api_key="your-pinecone-key", environment="us-west1-gcp")
index = pinecone.Index("nomic-embeddings")

def store_long_documents(documents):
    """Store long documents with Nomic embeddings in Pinecone"""
    for i, doc in enumerate(documents):
        response = client.embeddings.create(
            model="nomic-ai/nomic-embed-text-v1.5",
            input=doc,
            dimensions=768
        )
        
        index.upsert(vectors=[
            (f"doc_{i}", response.data[0].embedding, {"text": doc[:1000]})
        ])

def query_long_context(query, top_k=10):
    """Query with long context understanding"""
    response = client.embeddings.create(
        model="nomic-ai/nomic-embed-text-v1.5",
        input=query,
        dimensions=768
    )
    
    results = index.query(
        vector=response.data[0].embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    return [match.metadata["text"] for match in results.matches]
```

## Best Practices

### 1. Leverage Long Context
```python
# Good: Use full context capability
long_article = read_full_article()  # Up to 8192 tokens
embedding = embed_text(long_article)

# Avoid: Unnecessary chunking
# chunks = split_into_small_pieces(long_article)  # Don't do this
```

### 2. Optimize Dimensions for Use Case
```python
# High-precision applications: Use 768 dimensions
precision_embeddings = embed_with_dimension(texts, 768)

# Real-time applications: Use 256-512 dimensions
realtime_embeddings = embed_with_dimension(texts, 256)

# Storage-constrained: Use 128-256 dimensions
compressed_embeddings = embed_with_dimension(texts, 128)
```

### 3. Batch Processing Optimization
```python
def optimal_batch_processing(texts, batch_size=16):
    """Optimize batch size for Nomic models"""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        
        response = client.embeddings.create(
            model="nomic-ai/nomic-embed-text-v1.5",
            input=batch,
            dimensions=768
        )
        
        batch_embeddings = [data.embedding for data in response.data]
        embeddings.extend(batch_embeddings)
        
        # Rate limiting for large batches
        if len(batch) == batch_size:
            time.sleep(0.1)
    
    return embeddings
```

## Technical Deep Dive

### Model Architecture
- **Base Architecture**: Transformer-based encoder
- **Training Objective**: Contrastive learning with positive/negative pairs
- **Data Sources**: Diverse web text, academic papers, code repositories
- **Optimization**: Custom attention mechanisms for long sequences

### Training Methodology
- **Contrastive Learning**: Learns to distinguish similar vs dissimilar text pairs
- **Long Context Training**: Specific training for extended sequences
- **Reproducibility**: Deterministic training process for consistent outputs
- **Open Source**: Full training code and data pipeline available

### Performance Characteristics
- **Inference Speed**: Optimized for production use
- **Memory Efficiency**: Variable dimension support for resource constraints
- **Scalability**: Designed for large-scale applications
- **Consistency**: Reproducible outputs across runs

## Research and Development

### Academic Contributions
- **Paper**: "Nomic Embed: Training a Reproducible Long Context Text Embedder"
- **ArXiv**: https://arxiv.org/html/2402.01613v2
- **Key Innovation**: First open-source model to outperform closed-source alternatives on long context

### Open Source Impact
- **Full Transparency**: Complete model weights, training code, and data available
- **Community Driven**: Active community contributions and improvements
- **Research Enablement**: Enables academic and commercial research without API dependencies

### Future Roadmap
- Extended context lengths (16K+ tokens)
- Improved multilingual capabilities
- Domain-specific variants
- Enhanced efficiency optimizations

## Support and Resources

**Official Resources:**
- Hugging Face: https://huggingface.co/nomic-ai/nomic-embed-text-v1.5
- Nomic AI Blog: https://www.nomic.ai/blog
- Research Paper: https://arxiv.org/html/2402.01613v2
- GitHub Repository: https://github.com/nomic-ai/contrastors

**Community:**
- Discord server for Nomic AI
- GitHub issues and discussions
- Academic research collaborations

**Documentation:**
- Fireworks AI integration guides
- Model cards and usage examples
- Performance benchmarking results

---

*Last Updated: July 2025*
*Leading open-source embedding models with superior long-context performance and full transparency.*