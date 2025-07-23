# Together AI Embedding Models: Up to 150M Parameters

## Model Overview

Together AI's embedding models up to 150M parameters represent the entry-level tier of their embedding offerings, designed for cost-effective semantic understanding and vector representation tasks. These models provide excellent value for applications that require good quality embeddings without the computational overhead of larger models, making them ideal for startups, small businesses, and applications where cost efficiency is a primary concern.

## Technical Specifications

### Model Architecture
- **Parameter Range**: Up to 150 million parameters
- **Model Type**: Lightweight dense vector embedding models
- **Vector Dimensions**: Typically 384-768 dimensions (optimized for efficiency)
- **Context Window**: Up to 4,096 tokens for document embedding
- **Architecture**: Efficient transformer-based encoder architectures
- **Training Approach**: Contrastive learning with diverse text pairs

### Performance Characteristics
- **Processing Speed**: Optimized for high-throughput applications
- **Memory Efficiency**: Low memory footprint for edge deployment
- **Inference Latency**: Ultra-fast embedding generation (<50ms typical)
- **Language Support**: Strong performance in English with good multilingual coverage
- **Scalability**: Excellent for high-volume, cost-sensitive applications

## Capabilities and Features

### Core Embedding Capabilities
- **Semantic Similarity**: Effective capture of semantic relationships in text
- **Document Representation**: Quality vector representations for various content types
- **Fast Processing**: Optimized for real-time and batch processing scenarios
- **Multilingual Support**: Decent performance across major languages
- **Domain Adaptability**: Reasonable performance across different content domains

### Efficiency Features
- **Cost Optimization**: Lowest cost per token in the Together AI embedding lineup
- **High Throughput**: Capable of processing thousands of documents per minute
- **Low Latency**: Suitable for real-time applications requiring fast responses
- **Batch Friendly**: Excellent performance in batch processing scenarios
- **Resource Efficient**: Minimal computational and memory requirements

### API Features
- **Simple Integration**: Straightforward REST API for easy implementation
- **Batch Processing**: Efficient endpoints for processing multiple documents
- **Real-time Processing**: Low-latency endpoints for interactive applications
- **Flexible Input**: Support for various text lengths and formats
- **Normalized Output**: Consistent vector normalization for reliable similarity computation

## Pricing Information

### Highly Competitive Pricing
- **Input Cost**: $0.008 per 1 million tokens
- **Output Cost**: $0 (embeddings are generated, not text)
- **Billing Model**: Simple pay-per-token input processing
- **No Hidden Fees**: Transparent, predictable pricing

### Cost Optimization Benefits
- **Batch Processing**: 50% introductory discount available
  - Discounted rate: $0.004 per 1M tokens for batch operations
  - Processing window: Most batches complete within 1-2 hours
  - Guaranteed processing: 24-hour maximum completion time

### Volume Benefits
- **High-Volume Discounts**: Additional savings for enterprise customers
- **Predictable Costs**: Linear scaling with usage for easy budgeting
- **No Minimum Commitments**: Pay only for what you use

### Cost Comparison Analysis
- **Most Cost-Effective**: Lowest price point in Together AI's embedding lineup
- **vs Larger Models**: 50-75% cost savings compared to 151M-350M models
- **vs Competitors**: Highly competitive with industry-leading embedding providers
- **Total Cost of Ownership**: Excellent value for high-volume applications

## API Usage Details

### Basic Implementation
```python
import together
import os
from typing import List, Union

# Configure API access
together.api_key = os.environ.get("TOGETHER_API_KEY")

def create_embeddings(texts: Union[str, List[str]], model="together-ai-embedding-up-to-150m"):
    """Create cost-effective embeddings for text or list of texts"""
    
    # Ensure input is a list
    if isinstance(texts, str):
        texts = [texts]
    
    try:
        response = together.Embeddings.create(
            model=model,
            input=texts
        )
        
        # Extract embeddings and usage info
        embeddings = [data.embedding for data in response.data]
        
        return {
            "embeddings": embeddings,
            "usage": response.usage,
            "model": response.model,
            "cost": response.usage.total_tokens * 0.008 / 1_000_000  # Calculate cost
        }
        
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        return None

# Example usage
documents = [
    "Customer service is our top priority and we strive for excellence.",
    "Our product offers innovative solutions for modern businesses.",
    "Technical support is available 24/7 for all our customers."
]

result = create_embeddings(documents)

if result:
    print(f"Generated {len(result['embeddings'])} embeddings")
    print(f"Token usage: {result['usage']['total_tokens']}")
    print(f"Estimated cost: ${result['cost']:.6f}")
```

### High-Volume Batch Processing
```python
class CostOptimizedEmbeddingProcessor:
    def __init__(self, model="together-ai-embedding-up-to-150m"):
        self.model = model
        together.api_key = os.environ.get("TOGETHER_API_KEY")
        self.total_cost = 0.0
        self.total_tokens = 0
    
    def process_large_dataset(self, documents: List[str], batch_size: int = 200):
        """Process large document collections with cost optimization"""
        
        all_embeddings = []
        failed_indices = []
        
        print(f"Processing {len(documents)} documents in batches of {batch_size}")
        
        # Process in larger batches for cost efficiency
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            batch_start = i
            
            try:
                response = together.Embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # Extract embeddings and track costs
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
                
                batch_cost = response.usage.total_tokens * 0.008 / 1_000_000
                self.total_cost += batch_cost
                self.total_tokens += response.usage.total_tokens
                
                print(f"Batch {i//batch_size + 1}: Processed {len(batch)} docs, "
                      f"Cost: ${batch_cost:.6f}, Tokens: {response.usage.total_tokens}")
                
            except Exception as e:
                print(f"Error processing batch {i//batch_size + 1}: {e}")
                # Track failed documents
                failed_indices.extend(range(batch_start, batch_start + len(batch)))
                # Add None placeholders
                all_embeddings.extend([None] * len(batch))
        
        return {
            "embeddings": all_embeddings,
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
            "failed_indices": failed_indices,
            "success_rate": (len(documents) - len(failed_indices)) / len(documents)
        }
    
    def create_searchable_index(self, documents: List[dict], content_field: str = "content"):
        """Create cost-effective searchable index from documents"""
        
        # Extract text content
        texts = []
        valid_docs = []
        
        for doc in documents:
            content = doc.get(content_field, "")
            if content.strip():  # Only process non-empty content
                texts.append(content)
                valid_docs.append(doc)
        
        print(f"Creating index for {len(texts)} valid documents")
        
        # Process with batch optimization
        result = self.process_large_dataset(texts)
        
        # Build index structure
        index = []
        for i, (doc, embedding) in enumerate(zip(valid_docs, result["embeddings"])):
            if embedding:  # Only include successful embeddings
                index.append({
                    "id": doc.get("id", f"doc_{i}"),
                    "title": doc.get("title", ""),
                    "content": doc.get(content_field, ""),
                    "embedding": embedding,
                    "metadata": doc.get("metadata", {})
                })
        
        return {
            "index": index,
            "total_cost": result["total_cost"],
            "total_tokens": result["total_tokens"],
            "indexed_documents": len(index),
            "cost_per_document": result["total_cost"] / len(index) if index else 0
        }

# Example: Processing a large document collection
processor = CostOptimizedEmbeddingProcessor()

# Simulate large document collection
large_dataset = [
    f"Document {i}: This is sample content for document number {i} in our large collection."
    for i in range(1000)  # 1000 documents
]

result = processor.process_large_dataset(large_dataset, batch_size=200)

print(f"\nProcessing Summary:")
print(f"Total documents: {len(large_dataset)}")
print(f"Success rate: {result['success_rate']:.2%}")
print(f"Total cost: ${result['total_cost']:.4f}")
print(f"Cost per document: ${result['total_cost']/len(large_dataset):.6f}")
```

### Real-Time Search Implementation
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import time

class FastSemanticSearch:
    def __init__(self, model="together-ai-embedding-up-to-150m"):
        self.model = model
        self.processor = CostOptimizedEmbeddingProcessor(model)
        self.document_index = []
        self.embedding_matrix = None
        
    def build_index(self, documents: List[dict]):
        """Build fast search index optimized for cost and speed"""
        
        start_time = time.time()
        
        # Create embeddings index
        index_result = self.processor.create_searchable_index(documents)
        self.document_index = index_result["index"]
        
        # Create optimized embedding matrix
        embeddings = [doc["embedding"] for doc in self.document_index]
        self.embedding_matrix = np.array(embeddings, dtype=np.float32)  # Use float32 for memory efficiency
        
        build_time = time.time() - start_time
        
        return {
            "indexed_documents": len(self.document_index),
            "embedding_dimension": self.embedding_matrix.shape[1] if len(embeddings) > 0 else 0,
            "build_time_seconds": build_time,
            "index_cost": index_result["total_cost"],
            "cost_per_document": index_result["cost_per_document"]
        }
    
    def search(self, query: str, top_k: int = 10, threshold: float = 0.1):
        """Fast semantic search with cost tracking"""
        
        if not self.document_index:
            return {"error": "Index not built. Call build_index() first."}
        
        search_start = time.time()
        
        # Create query embedding
        query_result = create_embeddings(query, self.model)
        if not query_result:
            return {"error": "Failed to create query embedding"}
        
        query_embedding = np.array(query_result["embeddings"][0], dtype=np.float32).reshape(1, -1)
        
        # Fast similarity computation
        similarities = cosine_similarity(query_embedding, self.embedding_matrix)[0]
        
        # Get results above threshold
        valid_indices = np.where(similarities >= threshold)[0]
        valid_scores = similarities[valid_indices]
        
        # Sort by similarity
        sorted_indices = valid_indices[np.argsort(valid_scores)[::-1]]
        
        # Build results
        results = []
        for idx in sorted_indices[:top_k]:
            results.append({
                "document": self.document_index[idx],
                "similarity_score": float(similarities[idx]),
                "rank": len(results) + 1
            })
        
        search_time = time.time() - search_start
        
        return {
            "query": query,
            "results": results,
            "total_matches": len(valid_indices),
            "search_time_ms": search_time * 1000,
            "query_cost": query_result["cost"],
            "query_tokens": query_result["usage"]["total_tokens"]
        }
    
    def batch_search(self, queries: List[str], top_k: int = 5):
        """Process multiple search queries efficiently"""
        
        if not self.document_index:
            return {"error": "Index not built. Call build_index() first."}
        
        # Create embeddings for all queries in one batch
        query_result = create_embeddings(queries, self.model)
        if not query_result:
            return {"error": "Failed to create query embeddings"}
        
        query_embeddings = np.array(query_result["embeddings"], dtype=np.float32)
        
        # Batch similarity computation
        all_similarities = cosine_similarity(query_embeddings, self.embedding_matrix)
        
        # Process results for each query
        batch_results = []
        for i, (query, similarities) in enumerate(zip(queries, all_similarities)):
            # Get top-k for this query
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            query_results = []
            for idx in top_indices:
                query_results.append({
                    "document": self.document_index[idx],
                    "similarity_score": float(similarities[idx])
                })
            
            batch_results.append({
                "query": query,
                "results": query_results
            })
        
        return {
            "batch_results": batch_results,
            "total_queries": len(queries),
            "batch_cost": query_result["cost"],
            "cost_per_query": query_result["cost"] / len(queries)
        }

# Example usage with cost tracking
search_engine = FastSemanticSearch()

# Sample documents
sample_documents = [
    {
        "id": "prod1",
        "title": "Wireless Headphones",
        "content": "High-quality wireless headphones with noise cancellation and long battery life.",
        "metadata": {"category": "electronics", "price": 199.99}
    },
    {
        "id": "prod2", 
        "title": "Smartphone Case",
        "content": "Durable protective case for smartphones with wireless charging compatibility.",
        "metadata": {"category": "accessories", "price": 29.99}
    },
    {
        "id": "prod3",
        "title": "Laptop Stand",
        "content": "Ergonomic laptop stand for improved posture and workspace organization.",
        "metadata": {"category": "office", "price": 49.99}
    }
]

# Build index and track costs
build_result = search_engine.build_index(sample_documents)
print(f"Index built: {build_result['indexed_documents']} documents")
print(f"Index cost: ${build_result['index_cost']:.6f}")
print(f"Cost per document: ${build_result['cost_per_document']:.6f}")

# Perform searches
search_result = search_engine.search("wireless audio device", top_k=2)
print(f"\nSearch results for 'wireless audio device':")
print(f"Query cost: ${search_result['query_cost']:.6f}")
for result in search_result["results"]:
    print(f"- {result['document']['title']}: {result['similarity_score']:.3f}")
```

## Performance Benchmarks

### Speed and Efficiency Metrics
- **Single Document Latency**: 20-50ms typical processing time
- **Batch Throughput**: 1,000-5,000 documents per minute (varies by document length)
- **Memory Usage**: ~50-100MB for 10K document index
- **CPU Efficiency**: Optimized for standard CPU processing
- **Concurrent Requests**: Excellent scalability for high-volume applications

### Quality Benchmarks
- **Semantic Similarity Tasks**: Good performance on standard benchmarks
- **Information Retrieval**: Effective for most search and recommendation use cases
- **Classification Support**: Decent performance when used as feature vectors
- **Cross-lingual Performance**: Reasonable quality across major languages
- **Domain Adaptability**: Good generalization across different content types

### Cost-Performance Analysis
- **vs 151M-350M models**: 50% cost savings with 15-25% quality reduction
- **vs Premium embeddings**: 70-80% cost savings with acceptable quality trade-offs
- **Total Cost of Ownership**: Excellent for high-volume, cost-sensitive applications
- **ROI Optimization**: Best choice when cost is the primary constraint

## Use Cases and Applications

### High-Volume Applications
1. **E-commerce Product Search**
   - Large catalog semantic search
   - Product recommendation systems
   - Customer review analysis
   - Inventory categorization

2. **Content Management Systems**
   - Blog post similarity matching
   - Content categorization and tagging
   - Duplicate content detection
   - SEO content optimization

3. **Customer Support**
   - FAQ matching and retrieval
   - Support ticket categorization
   - Automated response suggestions
   - Knowledge base optimization

### Cost-Sensitive Deployments
1. **Startup Applications**
   - MVP development with AI features
   - Proof-of-concept implementations
   - Bootstrap applications with limited budgets
   - Early-stage product experimentation

2. **Educational Projects**
   - Student research projects
   - Academic experiments
   - Educational tool development
   - Learning and training applications

3. **Non-Profit Organizations**
   - Community resource matching
   - Volunteer opportunity matching
   - Donation and aid distribution
   - Public service applications

### Real-Time Applications
1. **Live Search Systems**
   - Real-time content discovery
   - Dynamic recommendation engines
   - Interactive search interfaces
   - Instant similarity matching

2. **Chat and Messaging**
   - Message similarity detection
   - Content moderation assistance
   - Automated response suggestion
   - Conversation analysis

## Industry-Specific Applications

### Small and Medium Businesses (SMBs)
- **Retail**: Product categorization, customer review analysis
- **Services**: Service matching, customer inquiry routing
- **Marketing**: Content optimization, campaign analysis
- **Operations**: Document organization, workflow optimization

### Media and Publishing
- **Content Discovery**: Article recommendation, related content matching
- **Editorial**: Content categorization, duplicate detection
- **Archives**: Historical content search and organization
- **SEO**: Content optimization, keyword analysis

### Education and Training
- **Course Materials**: Content similarity and organization
- **Student Support**: Question matching, resource recommendation
- **Research**: Literature organization, reference matching
- **Assessment**: Answer similarity analysis, plagiarism detection

## Optimization Strategies

### Cost Optimization Techniques
1. **Batch Processing Strategy**
   ```python
   # Optimize batch sizes for best cost/performance ratio
   def optimize_batch_processing(documents, target_cost_per_doc=0.00001):
       """Find optimal batch size for cost constraints"""
       
       optimal_batch_size = 200  # Start with recommended size
       base_cost_per_million = 0.008
       
       # Calculate tokens per document (estimate)
       sample_docs = documents[:10]
       avg_tokens = sum(len(doc.split()) * 1.3 for doc in sample_docs) / len(sample_docs)  # ~1.3 tokens per word
       
       # Calculate cost per document
       cost_per_doc = (avg_tokens * base_cost_per_million) / 1_000_000
       
       if cost_per_doc <= target_cost_per_doc:
           return optimal_batch_size
       else:
           # Suggest batch processing discount
           return optimal_batch_size, "Consider batch processing for 50% discount"
   ```

2. **Content Preprocessing**
   ```python
   def optimize_content_for_cost(documents, max_tokens_per_doc=512):
       """Optimize document content to reduce token usage"""
       
       optimized_docs = []
       for doc in documents:
           # Remove excessive whitespace
           content = " ".join(doc.split())
           
           # Truncate if too long (rough token estimation)
           words = content.split()
           if len(words) > max_tokens_per_doc:
               content = " ".join(words[:max_tokens_per_doc])
           
           optimized_docs.append(content)
       
       return optimized_docs
   ```

### Performance Optimization
1. **Memory-Efficient Processing**
   ```python
   class MemoryEfficientProcessor:
       def __init__(self):
           self.batch_size = 100  # Smaller batches for memory efficiency
           
       def process_streaming(self, document_generator):
           """Process documents as a stream to minimize memory usage"""
           
           batch = []
           for doc in document_generator:
               batch.append(doc)
               
               if len(batch) >= self.batch_size:
                   yield self.process_batch(batch)
                   batch = []
           
           # Process remaining documents
           if batch:
               yield self.process_batch(batch)
   ```

2. **Caching Strategy**
   ```python
   import hashlib
   import json
   from typing import Dict, Any
   
   class EmbeddingCache:
       def __init__(self, max_cache_size=10000):
           self.cache: Dict[str, Any] = {}
           self.max_size = max_cache_size
           
       def get_cache_key(self, text: str) -> str:
           """Generate cache key for text"""
           return hashlib.md5(text.encode()).hexdigest()
       
       def get_embedding(self, text: str):
           """Get embedding from cache or create new one"""
           cache_key = self.get_cache_key(text)
           
           if cache_key in self.cache:
               return self.cache[cache_key]
           
           # Create new embedding
           result = create_embeddings(text)
           
           if result and len(self.cache) < self.max_size:
               self.cache[cache_key] = result
           
           return result
   ```

## Integration Best Practices

### Production Deployment
```python
import logging
from functools import wraps
import time

def monitor_embedding_performance(func):
    """Decorator to monitor embedding API performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log successful operations
            logging.info(f"Embedding operation completed in {duration:.2f}s")
            
            if result and 'usage' in result:
                tokens = result['usage']['total_tokens']
                cost = result.get('cost', 0)
                logging.info(f"Usage: {tokens} tokens, Cost: ${cost:.6f}")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"Embedding operation failed after {duration:.2f}s: {e}")
            raise
    
    return wrapper

@monitor_embedding_performance
def create_monitored_embeddings(texts):
    """Create embeddings with performance monitoring"""
    return create_embeddings(texts)
```

### Error Handling and Resilience
```python
import time
import random
from typing import Optional

class ResilientEmbeddingClient:
    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        
    def create_embeddings_with_retry(self, texts, model="together-ai-embedding-up-to-150m"):
        """Create embeddings with exponential backoff retry logic"""
        
        for attempt in range(self.max_retries + 1):
            try:
                return together.Embeddings.create(
                    model=model,
                    input=texts
                )
                
            except Exception as e:
                if attempt == self.max_retries:
                    logging.error(f"Failed to create embeddings after {self.max_retries} attempts: {e}")
                    raise
                
                # Exponential backoff with jitter
                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s")
                time.sleep(delay)
        
        return None
```

## Monitoring and Cost Management

### Usage Analytics
```python
class CostMonitor:
    def __init__(self):
        self.daily_usage = {}
        self.cost_alerts = []
        
    def track_usage(self, tokens: int, cost: float, timestamp=None):
        """Track daily usage and costs"""
        if timestamp is None:
            timestamp = datetime.now()
        
        date_key = timestamp.strftime("%Y-%m-%d")
        
        if date_key not in self.daily_usage:
            self.daily_usage[date_key] = {"tokens": 0, "cost": 0.0, "requests": 0}
        
        self.daily_usage[date_key]["tokens"] += tokens
        self.daily_usage[date_key]["cost"] += cost
        self.daily_usage[date_key]["requests"] += 1
        
        # Check for cost alerts
        self.check_cost_alerts(date_key)
    
    def check_cost_alerts(self, date_key: str, daily_limit: float = 10.0):
        """Check if daily costs exceed limits"""
        daily_cost = self.daily_usage[date_key]["cost"]
        
        if daily_cost > daily_limit:
            alert = {
                "date": date_key,
                "cost": daily_cost,
                "limit": daily_limit,
                "timestamp": datetime.now()
            }
            self.cost_alerts.append(alert)
            logging.warning(f"Daily cost limit exceeded: ${daily_cost:.2f} > ${daily_limit:.2f}")
    
    def get_usage_summary(self, days: int = 7):
        """Get usage summary for recent days"""
        recent_dates = []
        total_cost = 0.0
        total_tokens = 0
        total_requests = 0
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.daily_usage:
                usage = self.daily_usage[date]
                total_cost += usage["cost"]
                total_tokens += usage["tokens"]
                total_requests += usage["requests"]
                recent_dates.append({
                    "date": date,
                    "cost": usage["cost"],
                    "tokens": usage["tokens"],
                    "requests": usage["requests"]
                })
        
        return {
            "period_days": days,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "total_requests": total_requests,
            "average_daily_cost": total_cost / days,
            "cost_per_request": total_cost / total_requests if total_requests > 0 else 0,
            "daily_breakdown": recent_dates
        }
```

## Getting Started - Quick Implementation

### Minimal Setup
```bash
# Install required packages
pip install together numpy

# Set API key
export TOGETHER_API_KEY="your-api-key-here"

# Test setup
python -c "import together; print('Setup complete')"
```

### 5-Minute Implementation
```python
import together
import os

# Quick setup
together.api_key = os.environ.get("TOGETHER_API_KEY")

# Test with sample data
sample_texts = [
    "Customer satisfaction is our priority",
    "Technical support available 24/7",
    "Product quality guaranteed"
]

# Create embeddings
response = together.Embeddings.create(
    model="together-ai-embedding-up-to-150m",
    input=sample_texts
)

# Display results
print(f"Created {len(response.data)} embeddings")
print(f"Embedding dimension: {len(response.data[0].embedding)}")
print(f"Total tokens: {response.usage.total_tokens}")
print(f"Estimated cost: ${response.usage.total_tokens * 0.008 / 1_000_000:.6f}")

# Simple similarity check
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

embeddings = np.array([data.embedding for data in response.data])
similarity_matrix = cosine_similarity(embeddings)

print("\nSimilarity matrix:")
for i, row in enumerate(similarity_matrix):
    print(f"Text {i+1}: {[f'{sim:.3f}' for sim in row]}")
```

Together AI's embedding models up to 150M parameters provide the most cost-effective solution for applications requiring semantic understanding without premium model costs, making them ideal for high-volume, budget-conscious implementations.