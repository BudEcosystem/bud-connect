# thenlper/gte-base and thenlper/gte-large - General Text Embeddings

## Overview

The GTE (General Text Embeddings) models, developed by Alibaba DAMO Academy, represent a family of high-performance text embedding models built on the BERT framework. These models are trained using multi-stage contrastive learning on large-scale relevance text pairs, achieving exceptional performance across various downstream embedding tasks.

## Model Specifications

### thenlper/gte-base

**Core Specifications:**
- **Embedding Dimensions**: 768
- **Model Size**: 219 MB  
- **Parameters**: ~110M
- **Context Length**: 512 tokens
- **Architecture**: BERT-based transformer
- **License**: Apache 2.0

### thenlper/gte-large

**Core Specifications:**
- **Embedding Dimensions**: 1024
- **Model Size**: 670 MB
- **Parameters**: 335M
- **Context Length**: 512 tokens
- **Architecture**: BERT-based transformer (larger variant)
- **License**: Apache 2.0

### thenlper/gte-small (Reference)

**Core Specifications:**
- **Embedding Dimensions**: 384
- **Model Size**: 67 MB
- **Context Length**: 512 tokens
- **Use Case**: Lightweight applications

## Performance Benchmarks

### MTEB (Massive Text Embedding Benchmark)
- **gte-large**: 63.13% average score on MTEB benchmark
- **gte-base**: Outperforms text-embedding-ada-002 despite being 10x smaller
- **gte-large Ranking**: 25th place on MTEB leaderboard
- **Efficiency**: Excellent performance-to-size ratio

### Comparative Performance
| Model | MTEB Score | Dimensions | Parameters | Size |
|-------|------------|------------|------------|------|
| gte-large | 63.13 | 1024 | 335M | 670 MB |
| gte-base | ~61.5 | 768 | 110M | 219 MB |
| text-embedding-ada-002 | ~61.0 | 1536 | Unknown | API-only |
| E5-large-v2 | ~62.0 | 1024 | 335M | Similar |

### Key Achievements
- **gte-base**: Outperforms OpenAI's text-embedding-ada-002 with 10x fewer parameters
- **gte-large**: Competitive with much larger models while maintaining efficiency
- **BERT-based Excellence**: Demonstrates strong performance of BERT architecture with optimized training

## Training Methodology

### Multi-stage Contrastive Learning
The GTE models employ a sophisticated training approach:

1. **Large-scale Corpus**: Trained on massive datasets covering diverse domains
2. **Relevance Pairs**: Uses text pairs with known relevance relationships
3. **Multi-stage Process**: Progressive training stages for optimal performance
4. **Domain Coverage**: Wide range of scenarios and text types

### Technical Approach
- **Contrastive Objective**: Learns to distinguish relevant vs irrelevant text pairs
- **Average Pooling**: Uses average pooling of BERT's last hidden states
- **Sequence Processing**: Optimized for 512-token sequences
- **Domain Adaptation**: Training across multiple domains for generalization

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

#### Using gte-large
```python
response = client.embeddings.create(
    model="thenlper/gte-large",
    input="Your text to embed here"
)

embedding = response.data[0].embedding
print(f"gte-large embedding dimension: {len(embedding)}")  # Output: 1024
```

#### Using gte-base
```python
response = client.embeddings.create(
    model="thenlper/gte-base", 
    input="Your text to embed here"
)

embedding = response.data[0].embedding
print(f"gte-base embedding dimension: {len(embedding)}")  # Output: 768
```

### Batch Processing
```python
texts = [
    "Information retrieval example",
    "Semantic textual similarity task", 
    "Text reranking application"
]

# Process with gte-large
response_large = client.embeddings.create(
    model="thenlper/gte-large",
    input=texts
)

# Process with gte-base
response_base = client.embeddings.create(
    model="thenlper/gte-base", 
    input=texts
)

large_embeddings = [data.embedding for data in response_large.data]
base_embeddings = [data.embedding for data in response_base.data]
```

### Text Length Handling
```python
def process_text_for_gte(text, max_tokens=400):
    """
    Prepare text for GTE models (512 token limit)
    """
    words = text.split()
    if len(words) > max_tokens:
        # Truncate conservatively
        text = " ".join(words[:max_tokens])
    return text.strip()

# Safe processing
safe_text = process_text_for_gte(long_text)
response = client.embeddings.create(
    model="thenlper/gte-large",
    input=safe_text
)
```

## Pricing with Fireworks AI

**Cost Structure:**
- **Input Pricing**: $0.008 per 1 million tokens
- **Output Pricing**: $0 (no charge for embeddings)
- **Token Limit**: 512 tokens per request
- **Model Choice**: Same pricing for both gte-base and gte-large

**Cost Comparison:**
```python
# Cost calculation for different scenarios
def calculate_cost(num_tokens):
    return (num_tokens / 1_000_000) * 0.008

# Example costs
cost_1k_tokens = calculate_cost(1000)      # $0.000008
cost_100k_tokens = calculate_cost(100000)  # $0.0008
cost_1m_tokens = calculate_cost(1000000)   # $0.008
```

## Use Cases and Applications

### 1. Information Retrieval
```python
import numpy as np
from scipy.spatial.distance import cosine

class GTERetriever:
    def __init__(self, documents, model="thenlper/gte-large"):
        self.documents = documents
        self.model = model
        self.doc_embeddings = self._embed_documents()
    
    def _embed_documents(self):
        embeddings = []
        for doc in self.documents:
            processed_doc = process_text_for_gte(doc)
            response = client.embeddings.create(
                model=self.model,
                input=processed_doc
            )
            embeddings.append(response.data[0].embedding)
        return embeddings
    
    def retrieve(self, query, top_k=5):
        # Embed query
        processed_query = process_text_for_gte(query)
        query_response = client.embeddings.create(
            model=self.model,
            input=processed_query
        )
        query_embedding = query_response.data[0].embedding
        
        # Calculate similarities
        similarities = []
        for doc_embedding in self.doc_embeddings:
            similarity = 1 - cosine(query_embedding, doc_embedding)
            similarities.append(similarity)
        
        # Return top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = [
            {
                "document": self.documents[i],
                "score": similarities[i]
            }
            for i in top_indices
        ]
        return results

# Usage example
documents = ["Document 1 text...", "Document 2 text...", ...]
retriever = GTERetriever(documents, model="thenlper/gte-large")
results = retriever.retrieve("search query", top_k=3)
```

### 2. Semantic Textual Similarity
```python
def calculate_similarity(text1, text2, model="thenlper/gte-base"):
    """
    Calculate semantic similarity between two texts
    """
    # Process texts
    processed_text1 = process_text_for_gte(text1)
    processed_text2 = process_text_for_gte(text2)
    
    # Generate embeddings
    response1 = client.embeddings.create(model=model, input=processed_text1)
    response2 = client.embeddings.create(model=model, input=processed_text2)
    
    # Calculate cosine similarity
    similarity = 1 - cosine(
        response1.data[0].embedding,
        response2.data[0].embedding
    )
    
    return similarity

# Example usage
text1 = "Machine learning is a subset of artificial intelligence"
text2 = "AI includes machine learning as one of its components"

similarity_base = calculate_similarity(text1, text2, "thenlper/gte-base")
similarity_large = calculate_similarity(text1, text2, "thenlper/gte-large")

print(f"Similarity (gte-base): {similarity_base:.4f}")
print(f"Similarity (gte-large): {similarity_large:.4f}")
```

### 3. Text Reranking
```python
class GTEReranker:
    def __init__(self, model="thenlper/gte-large"):
        self.model = model
    
    def rerank(self, query, candidates, top_k=None):
        """
        Rerank candidate texts based on relevance to query
        """
        # Embed query
        processed_query = process_text_for_gte(query)
        query_response = client.embeddings.create(
            model=self.model,
            input=processed_query
        )
        query_embedding = query_response.data[0].embedding
        
        # Embed candidates
        candidate_embeddings = []
        for candidate in candidates:
            processed_candidate = process_text_for_gte(candidate)
            response = client.embeddings.create(
                model=self.model,
                input=processed_candidate
            )
            candidate_embeddings.append(response.data[0].embedding)
        
        # Calculate relevance scores
        scores = []
        for candidate_embedding in candidate_embeddings:
            score = 1 - cosine(query_embedding, candidate_embedding)
            scores.append(score)
        
        # Sort by relevance
        ranked_indices = np.argsort(scores)[::-1]
        
        if top_k:
            ranked_indices = ranked_indices[:top_k]
        
        reranked_results = [
            {
                "text": candidates[i],
                "score": scores[i],
                "rank": rank + 1
            }
            for rank, i in enumerate(ranked_indices)
        ]
        
        return reranked_results

# Usage example
reranker = GTEReranker(model="thenlper/gte-large")
query = "How to train machine learning models?"
candidates = [
    "Deep learning training techniques and best practices",
    "Weather forecasting using meteorological data", 
    "Supervised learning algorithms for classification",
    "Recipe for chocolate chip cookies",
    "Neural network optimization and hyperparameter tuning"
]

reranked = reranker.rerank(query, candidates, top_k=3)
for result in reranked:
    print(f"Rank {result['rank']}: {result['score']:.4f} - {result['text']}")
```

### 4. Cross-Domain Applications
```python
class MultiDomainEmbedder:
    def __init__(self, model="thenlper/gte-base"):
        self.model = model
    
    def embed_scientific_text(self, text):
        """Embed scientific/academic text"""
        processed = process_text_for_gte(text)
        response = client.embeddings.create(model=self.model, input=processed)
        return response.data[0].embedding
    
    def embed_web_content(self, text):
        """Embed web content/articles"""
        processed = process_text_for_gte(text)
        response = client.embeddings.create(model=self.model, input=processed)
        return response.data[0].embedding
    
    def embed_code_documentation(self, text):
        """Embed code documentation"""
        processed = process_text_for_gte(text)
        response = client.embeddings.create(model=self.model, input=processed)
        return response.data[0].embedding
    
    def find_cross_domain_similarities(self, scientific_texts, web_texts, code_docs):
        """Find similarities across different domains"""
        # Embed all domains
        sci_embeddings = [self.embed_scientific_text(text) for text in scientific_texts]
        web_embeddings = [self.embed_web_content(text) for text in web_texts] 
        code_embeddings = [self.embed_code_documentation(text) for text in code_docs]
        
        # Find cross-domain matches
        similarities = {}
        
        # Science to Web
        for i, sci_emb in enumerate(sci_embeddings):
            for j, web_emb in enumerate(web_embeddings):
                sim = 1 - cosine(sci_emb, web_emb)
                similarities[f"sci_{i}_web_{j}"] = sim
        
        return similarities

# Multi-domain usage
embedder = MultiDomainEmbedder(model="thenlper/gte-large")
cross_similarities = embedder.find_cross_domain_similarities(
    scientific_texts=["Research paper abstract..."],
    web_texts=["Blog post about similar topic..."],
    code_docs=["API documentation..."]
)
```

## Model Selection Guide

### When to Use gte-base
- **Resource Constraints**: Limited memory or storage
- **Real-time Applications**: Faster inference needed
- **Large Scale**: Processing millions of texts
- **Cost Optimization**: Budget-conscious applications
- **Good Performance**: Still outperforms many larger models

### When to Use gte-large  
- **Maximum Accuracy**: Best possible embedding quality needed
- **Complex Tasks**: Nuanced semantic understanding required
- **Research Applications**: Academic or scientific use cases
- **Competitive Benchmarking**: Need top-tier performance
- **Rich Representations**: 1024 dimensions for complex relationships

### Performance vs Efficiency Trade-off
```python
def benchmark_models(test_texts, task_type="similarity"):
    """
    Compare gte-base vs gte-large performance
    """
    models = ["thenlper/gte-base", "thenlper/gte-large"]
    results = {}
    
    for model in models:
        start_time = time.time()
        
        # Process all texts
        embeddings = []
        for text in test_texts:
            processed = process_text_for_gte(text)
            response = client.embeddings.create(model=model, input=processed)
            embeddings.append(response.data[0].embedding)
        
        processing_time = time.time() - start_time
        
        results[model] = {
            'processing_time': processing_time,
            'dimension': len(embeddings[0]),
            'memory_per_embedding': len(embeddings[0]) * 4,  # bytes
            'embeddings': embeddings
        }
    
    return results
```

## Integration Examples

### LangChain Integration
```python
from langchain_fireworks import FireworksEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize with GTE model
embeddings_large = FireworksEmbeddings(
    model="thenlper/gte-large",
    api_key="your-fireworks-api-key"
)

embeddings_base = FireworksEmbeddings(
    model="thenlper/gte-base", 
    api_key="your-fireworks-api-key"
)

# Text splitter for 512 token limit
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,  # Conservative for 512 tokens
    chunk_overlap=50,
    length_function=len,
)

# Create vector stores
texts = text_splitter.split_text(document)

# High-performance vector store
vectorstore_large = Chroma.from_texts(texts, embeddings_large)

# Efficient vector store  
vectorstore_base = Chroma.from_texts(texts, embeddings_base)

# Query both
query = "semantic search query"
results_large = vectorstore_large.similarity_search(query, k=5)
results_base = vectorstore_base.similarity_search(query, k=5)
```

### Weaviate Integration
```python
import weaviate

# Initialize Weaviate client
client_weaviate = weaviate.Client("http://localhost:8080")

# Define schema for GTE embeddings
schema = {
    "classes": [
        {
            "class": "Document",
            "vectorizer": "none",  # We'll provide vectors
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "source", "dataType": ["string"]},
            ]
        }
    ]
}

def store_with_gte_embeddings(documents, model="thenlper/gte-large"):
    """Store documents with GTE embeddings in Weaviate"""
    
    for i, doc in enumerate(documents):
        # Generate embedding
        processed_doc = process_text_for_gte(doc)
        response = client.embeddings.create(
            model=model,
            input=processed_doc
        )
        embedding = response.data[0].embedding
        
        # Store in Weaviate
        client_weaviate.data_object.create(
            data_object={
                "content": doc,
                "source": f"document_{i}"
            },
            class_name="Document",
            vector=embedding
        )

def search_weaviate(query, model="thenlper/gte-large"):
    """Search Weaviate using GTE embeddings"""
    
    # Generate query embedding
    processed_query = process_text_for_gte(query)
    response = client.embeddings.create(
        model=model,
        input=processed_query
    )
    query_embedding = response.data[0].embedding
    
    # Search Weaviate
    result = client_weaviate.query.get("Document", ["content", "source"]) \
        .with_near_vector({"vector": query_embedding}) \
        .with_limit(5) \
        .do()
    
    return result["data"]["Get"]["Document"]
```

### FAISS Integration  
```python
import faiss
import numpy as np

class GTEFAISSIndex:
    def __init__(self, model="thenlper/gte-base"):
        self.model = model
        self.dimension = 768 if "base" in model else 1024
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product
        self.texts = []
    
    def add_documents(self, documents):
        """Add documents to FAISS index"""
        embeddings = []
        
        for doc in documents:
            processed_doc = process_text_for_gte(doc)
            response = client.embeddings.create(
                model=self.model,
                input=processed_doc
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            
            # Normalize for cosine similarity with inner product
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
            self.texts.append(doc)
        
        # Add to index
        embeddings_matrix = np.vstack(embeddings)
        self.index.add(embeddings_matrix)
    
    def search(self, query, k=5):
        """Search using FAISS index"""
        processed_query = process_text_for_gte(query)
        response = client.embeddings.create(
            model=self.model,
            input=processed_query
        )
        query_embedding = np.array(response.data[0].embedding, dtype=np.float32)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search
        scores, indices = self.index.search(
            query_embedding.reshape(1, -1), k
        )
        
        results = [
            {"text": self.texts[idx], "score": float(score)}
            for score, idx in zip(scores[0], indices[0])
            if idx != -1
        ]
        
        return results

# Usage
faiss_index = GTEFAISSIndex(model="thenlper/gte-large")
faiss_index.add_documents(["Document 1...", "Document 2..."])
results = faiss_index.search("query text", k=3)
```

## Best Practices

### 1. Text Preprocessing
```python
import re

def preprocess_for_gte(text):
    """
    Optimal preprocessing for GTE models
    """
    # Clean text
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    # Handle length (conservative token estimation)
    words = text.split()
    if len(words) > 400:  # Conservative for 512 tokens
        text = " ".join(words[:400])
    
    return text
```

### 2. Batch Processing Optimization
```python
def efficient_batch_processing(texts, model="thenlper/gte-base", batch_size=32):
    """
    Optimized batch processing for GTE models
    """
    embeddings = []
    
    # Preprocess all texts first
    processed_texts = [preprocess_for_gte(text) for text in texts]
    
    # Process in batches
    for i in range(0, len(processed_texts), batch_size):
        batch = processed_texts[i:i+batch_size]
        
        response = client.embeddings.create(
            model=model,
            input=batch
        )
        
        batch_embeddings = [data.embedding for data in response.data]
        embeddings.extend(batch_embeddings)
    
    return embeddings
```

### 3. Model Selection Strategy
```python
def select_gte_model(requirements):
    """
    Automatic model selection based on requirements
    """
    if requirements.get("max_accuracy", False):
        return "thenlper/gte-large"
    elif requirements.get("memory_constraint", False):
        return "thenlper/gte-base"
    elif requirements.get("real_time", False):
        return "thenlper/gte-base"
    elif requirements.get("large_scale", False):
        return "thenlper/gte-base"
    else:
        return "thenlper/gte-large"  # Default to higher quality

# Usage
model = select_gte_model({
    "memory_constraint": True,
    "large_scale": True
})  # Returns "thenlper/gte-base"
```

### 4. Caching and Performance
```python
import hashlib
import json
import os

class GTEEmbeddingCache:
    def __init__(self, cache_dir="gte_cache", model="thenlper/gte-base"):
        self.cache_dir = cache_dir
        self.model = model
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, text):
        """Generate cache key for text and model"""
        content = f"{self.model}:{text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_embedding(self, text):
        """Get embedding with caching"""
        cache_key = self._get_cache_key(text)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        # Check cache
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        
        # Generate embedding
        processed_text = preprocess_for_gte(text)
        response = client.embeddings.create(
            model=self.model,
            input=processed_text
        )
        embedding = response.data[0].embedding
        
        # Save to cache
        with open(cache_path, 'w') as f:
            json.dump(embedding, f)
        
        return embedding

# Usage with caching
cache = GTEEmbeddingCache(model="thenlper/gte-large")
embedding = cache.get_embedding("Cached text")  # Fast on second call
```

## Limitations and Considerations

### Text Length Limitations
- **512 Token Limit**: Texts must be truncated to fit context window
- **English Optimization**: Primarily optimized for English texts
- **Truncation Strategy**: Important to preserve key information when truncating

### Model Characteristics
```python
def analyze_gte_limitations():
    """
    Understand GTE model limitations
    """
    limitations = {
        "context_length": 512,
        "primary_language": "English",
        "architecture": "BERT-based (not generative)",
        "training_data_cutoff": "Training data has temporal limits",
        "optimal_use_cases": [
            "Information retrieval",
            "Semantic similarity", 
            "Text reranking",
            "Short to medium text processing"
        ],
        "less_optimal_for": [
            "Very long documents (>512 tokens)",
            "Real-time streaming applications",
            "Highly specialized domains without fine-tuning"
        ]
    }
    return limitations
```

### Performance Considerations
```python
def performance_optimization_tips():
    """
    Tips for optimal GTE performance
    """
    tips = {
        "preprocessing": "Clean and normalize text before embedding",
        "batch_size": "Use moderate batch sizes (16-32) for optimal throughput",
        "caching": "Cache embeddings for frequently accessed texts",
        "model_choice": "Use gte-base for scale, gte-large for accuracy",
        "text_length": "Keep texts under 400 words for best results",
        "normalization": "Normalize embeddings for cosine similarity"
    }
    return tips
```

## Research and Academic Use

### Citation Information
- **Model**: GTE (General Text Embeddings)
- **Organization**: Alibaba DAMO Academy
- **Paper**: "Towards General Text Embeddings with Multi-stage Contrastive Learning"
- **ArXiv**: https://arxiv.org/abs/2308.03281

### Research Applications
- Semantic textual similarity studies
- Information retrieval research
- Cross-domain embedding analysis
- BERT architecture optimization studies

### Academic Integration
```python
def research_embedding_analysis(texts, model="thenlper/gte-large"):
    """
    Generate embeddings for research analysis
    """
    embeddings = []
    metadata = []
    
    for text in texts:
        processed = preprocess_for_gte(text)
        response = client.embeddings.create(model=model, input=processed)
        embedding = response.data[0].embedding
        
        embeddings.append(embedding)
        metadata.append({
            "original_length": len(text),
            "processed_length": len(processed),
            "model": model,
            "dimensions": len(embedding)
        })
    
    return embeddings, metadata
```

## Support and Resources

**Official Resources:**
- Hugging Face Model Hub: 
  - https://huggingface.co/thenlper/gte-large
  - https://huggingface.co/thenlper/gte-base
- Research Paper: https://arxiv.org/abs/2308.03281
- Fireworks AI Documentation: https://docs.fireworks.ai/

**Community:**
- Hugging Face discussions
- GitHub issues and contributions
- Academic research community

**Documentation:**
- Model cards with detailed specifications
- Usage examples and tutorials
- Performance benchmarking results
- Integration guides for popular frameworks

---

*Last Updated: July 2025*
*High-performance BERT-based embedding models with excellent efficiency and broad applicability across text embedding tasks.*