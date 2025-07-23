# Together AI Embedding Models: 151M-350M Parameters

## Model Overview

Together AI's 151M-350M parameter embedding models represent the mid-tier offering in their embedding model lineup, designed to provide enhanced semantic understanding and representation capabilities while maintaining cost-effectiveness. These models excel at creating high-quality vector representations for text data, making them ideal for sophisticated search, recommendation, and similarity applications that require more nuanced understanding than smaller embedding models can provide.

## Technical Specifications

### Model Architecture
- **Parameter Range**: 151 million to 350 million parameters
- **Model Type**: Dense vector embedding models
- **Vector Dimensions**: Typically 768-1536 dimensions (varies by specific model)
- **Context Window**: Up to 8,192 tokens for longer document embedding
- **Architecture**: Advanced transformer-based encoder models
- **Training Data**: Diverse multilingual text corpus with domain-specific fine-tuning

### Performance Characteristics
- **Embedding Quality**: High-quality semantic representations with nuanced understanding
- **Processing Speed**: Optimized for both single document and batch processing
- **Language Support**: Strong multilingual capabilities across 40+ languages
- **Domain Adaptability**: Effective across various domains including technical, legal, and creative content

## Capabilities and Features

### Core Embedding Capabilities
- **Semantic Understanding**: Captures complex semantic relationships and contextual meaning
- **Domain Specialization**: Performs well across diverse domains and content types
- **Multilingual Support**: Consistent quality across multiple languages
- **Long Document Handling**: Effective processing of documents up to 8K tokens
- **Batch Processing**: Efficient handling of large document collections

### Advanced Features
- **Fine-grained Similarity**: Nuanced similarity scoring for complex content matching
- **Contextual Embeddings**: Context-aware representations that understand document structure
- **Cross-lingual Alignment**: Embeddings that work across language boundaries
- **Domain Transfer**: Embeddings that generalize well across different content domains
- **Clustering Support**: Optimized for document clustering and topic modeling

### API Integration Features
- **RESTful API**: Simple HTTP-based interface for easy integration
- **Batch Processing**: Optimized endpoints for processing multiple documents
- **Streaming Support**: Real-time embedding generation for dynamic applications
- **Custom Normalization**: Configurable output normalization and scaling
- **Metadata Support**: Rich metadata handling for enhanced search applications

## Pricing Information

### Standard Pricing
- **Input Cost**: $0.016 per 1 million tokens
- **Output Cost**: $0 (embeddings are generated, not text)
- **Billing Model**: Pay-per-token input processing
- **No Setup Fees**: Simple pay-as-you-go pricing

### Cost Optimization Options
- **Batch Processing**: 50% introductory discount available
  - Discounted rate: $0.008 per 1M tokens for batch operations
  - Processing window: Most batches complete within 2-4 hours
  - Best-effort completion: 24-hour maximum processing time

### Volume Pricing
- **Enterprise Discounts**: Available for high-volume customers
- **Dedicated Endpoints**: Custom pricing for guaranteed capacity
- **Annual Contracts**: Additional discounts for long-term commitments

### Cost Comparison
- **vs 150M models**: 2x cost but 40-60% better quality for complex content
- **vs 350M+ models**: 20-40% cost savings with competitive quality
- **vs OpenAI Ada-002**: Competitive pricing with specialized features

## API Usage Details

### Basic Implementation
```python
import together
import os
from typing import List, Union

# Configure API access
together.api_key = os.environ.get("TOGETHER_API_KEY")

def create_embeddings(texts: Union[str, List[str]], model="together-ai-embedding-151m-350m"):
    """Create embeddings for text or list of texts"""
    
    # Ensure input is a list
    if isinstance(texts, str):
        texts = [texts]
    
    try:
        response = together.Embeddings.create(
            model=model,
            input=texts
        )
        
        # Extract embeddings
        embeddings = [data.embedding for data in response.data]
        
        return {
            "embeddings": embeddings,
            "usage": response.usage,
            "model": response.model
        }
        
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        return None

# Example usage
text = "Machine learning is transforming how businesses operate and make decisions."
result = create_embeddings(text)

if result:
    embedding = result["embeddings"][0]
    print(f"Embedding dimension: {len(embedding)}")
    print(f"Token usage: {result['usage']['total_tokens']}")
```

### Batch Processing Implementation
```python
class EmbeddingProcessor:
    def __init__(self, model="together-ai-embedding-151m-350m"):
        self.model = model
        together.api_key = os.environ.get("TOGETHER_API_KEY")
    
    def process_documents_batch(self, documents: List[str], batch_size: int = 100):
        """Process large document collections efficiently"""
        
        all_embeddings = []
        total_tokens = 0
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            
            try:
                response = together.Embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # Extract embeddings and track usage
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
                total_tokens += response.usage.total_tokens
                
                print(f"Processed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
                
            except Exception as e:
                print(f"Error processing batch {i//batch_size + 1}: {e}")
                # Add placeholder embeddings for failed batch
                all_embeddings.extend([None] * len(batch))
        
        return {
            "embeddings": all_embeddings,
            "total_tokens": total_tokens,
            "documents_processed": len(documents)
        }
    
    def create_document_index(self, documents: List[dict]):
        """Create searchable document index with embeddings"""
        
        # Extract text content
        texts = [doc.get("content", "") for doc in documents]
        
        # Generate embeddings
        result = self.process_documents_batch(texts)
        
        # Create index structure
        index = []
        for i, (doc, embedding) in enumerate(zip(documents, result["embeddings"])):
            if embedding:  # Skip failed embeddings
                index.append({
                    "id": doc.get("id", i),
                    "title": doc.get("title", f"Document {i}"),
                    "content": doc.get("content", ""),
                    "embedding": embedding,
                    "metadata": doc.get("metadata", {})
                })
        
        return {
            "index": index,
            "total_tokens": result["total_tokens"],
            "indexed_documents": len(index)
        }

# Example usage
processor = EmbeddingProcessor()

documents = [
    {
        "id": "doc1",
        "title": "AI in Healthcare",
        "content": "Artificial intelligence is revolutionizing healthcare delivery...",
        "metadata": {"category": "healthcare", "author": "Dr. Smith"}
    },
    {
        "id": "doc2", 
        "title": "Financial Technology Trends",
        "content": "The fintech industry is experiencing rapid transformation...",
        "metadata": {"category": "finance", "author": "Jane Doe"}
    }
]

index = processor.create_document_index(documents)
print(f"Created index with {index['indexed_documents']} documents")
```

### Semantic Search Implementation
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SemanticSearchEngine:
    def __init__(self, model="together-ai-embedding-151m-350m"):
        self.model = model
        self.processor = EmbeddingProcessor(model)
        self.document_index = []
        
    def build_index(self, documents: List[dict]):
        """Build searchable index from documents"""
        
        index_result = self.processor.create_document_index(documents)
        self.document_index = index_result["index"]
        
        # Create embedding matrix for efficient search
        self.embedding_matrix = np.array([
            doc["embedding"] for doc in self.document_index
        ])
        
        return {
            "indexed_documents": len(self.document_index),
            "embedding_dimension": self.embedding_matrix.shape[1],
            "total_cost": index_result["total_tokens"] * 0.016 / 1_000_000
        }
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.0):
        """Search for similar documents using semantic similarity"""
        
        if not self.document_index:
            return {"error": "Index not built. Call build_index() first."}
        
        # Create query embedding
        query_result = create_embeddings(query, self.model)
        if not query_result:
            return {"error": "Failed to create query embedding"}
        
        query_embedding = np.array(query_result["embeddings"][0]).reshape(1, -1)
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embedding_matrix)[0]
        
        # Get top-k results above threshold
        results = []
        for i, score in enumerate(similarities):
            if score >= threshold:
                results.append({
                    "document": self.document_index[i],
                    "similarity_score": float(score),
                    "rank": len(results) + 1
                })
        
        # Sort by similarity and return top-k
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return {
            "query": query,
            "results": results[:top_k],
            "total_matches": len(results),
            "query_tokens": query_result["usage"]["total_tokens"]
        }
    
    def find_similar_documents(self, document_id: str, top_k: int = 5):
        """Find documents similar to a specific document in the index"""
        
        # Find source document
        source_doc = None
        source_embedding = None
        
        for i, doc in enumerate(self.document_index):
            if doc["id"] == document_id:
                source_doc = doc
                source_embedding = self.embedding_matrix[i].reshape(1, -1)
                break
        
        if source_doc is None:
            return {"error": f"Document {document_id} not found in index"}
        
        # Calculate similarities (excluding self)
        similarities = cosine_similarity(source_embedding, self.embedding_matrix)[0]
        
        results = []
        for i, score in enumerate(similarities):
            if self.document_index[i]["id"] != document_id:  # Exclude self
                results.append({
                    "document": self.document_index[i],
                    "similarity_score": float(score)
                })
        
        # Sort and return top-k
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return {
            "source_document": source_doc,
            "similar_documents": results[:top_k]
        }

# Example usage
search_engine = SemanticSearchEngine()

# Build index
build_result = search_engine.build_index(documents)
print(f"Index built: {build_result}")

# Search
search_results = search_engine.search(
    query="artificial intelligence healthcare applications",
    top_k=3,
    threshold=0.1
)

print("Search Results:")
for result in search_results["results"]:
    print(f"- {result['document']['title']}: {result['similarity_score']:.3f}")
```

## Performance Benchmarks

### Quality Metrics
- **MTEB (Massive Text Embedding Benchmark)**: Strong performance across retrieval tasks
- **Semantic Similarity**: High correlation with human similarity judgments
- **Classification Accuracy**: Excellent performance when used as features
- **Clustering Quality**: Strong performance in document clustering tasks
- **Cross-lingual Performance**: Consistent quality across supported languages

### Speed and Efficiency
- **Single Document**: ~50-100ms processing time
- **Batch Processing**: 100-500 documents per second (depending on document length)
- **Throughput**: Scales linearly with available compute resources
- **Memory Efficiency**: Optimized memory usage for large document collections

### Comparative Performance
- **vs 150M models**: 40-60% better quality on complex semantic tasks
- **vs 350M+ models**: 90% of the quality at 50% lower cost
- **vs Domain-specific models**: Competitive across multiple domains
- **vs OpenAI models**: Similar quality with more transparent pricing

## Use Cases and Applications

### Enterprise Search and Knowledge Management
1. **Document Search Systems**
   - Semantic search in corporate knowledge bases
   - Legal document retrieval and analysis
   - Technical documentation search
   - Research paper and publication search

2. **Content Discovery**
   - Product catalog search and recommendation
   - Content management system enhancement
   - News and media content discovery
   - Educational resource matching

3. **Customer Support**
   - FAQ matching and retrieval
   - Support ticket categorization
   - Knowledge base optimization
   - Automated response suggestion

### E-commerce and Recommendation Systems
1. **Product Recommendations**
   - Similar product discovery
   - Cross-selling and upselling
   - Personalized product matching
   - Inventory optimization

2. **Content Matching**
   - User preference modeling
   - Content-based filtering
   - Hybrid recommendation systems
   - Dynamic content personalization

### Content Analysis and Organization
1. **Document Clustering**
   - Automatic content categorization
   - Topic modeling and analysis
   - Duplicate content detection
   - Content workflow optimization

2. **Sentiment and Intent Analysis**
   - Customer feedback analysis
   - Social media monitoring
   - Brand sentiment tracking
   - Market research analysis

## Industry-Specific Applications

### Financial Services
- **Document Analysis**: Contract similarity, regulatory document matching
- **Risk Assessment**: Similar case analysis, fraud pattern detection
- **Research**: Investment research document matching, market analysis
- **Compliance**: Regulatory document classification, audit trail analysis

### Healthcare and Life Sciences
- **Research**: Medical literature search, clinical trial matching
- **Documentation**: Patient record similarity, treatment protocol matching
- **Drug Discovery**: Compound similarity analysis, research paper matching
- **Education**: Medical education content matching, case study similarity

### Legal and Professional Services
- **Case Law**: Legal precedent search, case similarity analysis
- **Contract Analysis**: Contract clause matching, template similarity
- **Due Diligence**: Document similarity in M&A processes
- **Compliance**: Regulatory requirement matching, policy analysis

### Technology and Software
- **Code Search**: API documentation matching, code example search
- **Technical Support**: Solution matching, troubleshooting guides
- **Product Development**: Feature similarity analysis, competitive analysis
- **Knowledge Management**: Engineering documentation search, best practices

## Best Practices and Optimization

### Input Preparation
1. **Text Preprocessing**
   - Clean and normalize text input
   - Handle special characters and encoding
   - Optimize document chunking for long texts
   - Maintain consistent formatting

2. **Content Strategy**
   - Focus on meaningful content over metadata
   - Balance document length for optimal performance
   - Consider domain-specific terminology
   - Maintain consistent language and style

### Performance Optimization
1. **Batch Processing**
   - Group similar documents together
   - Use appropriate batch sizes (50-100 documents)
   - Implement error handling and retries
   - Monitor processing times and adjust

2. **Caching Strategy**
   - Cache frequently accessed embeddings
   - Implement efficient storage formats
   - Use vector databases for large-scale applications
   - Consider embedding versioning

### Cost Management
1. **Token Optimization**
   - Monitor token usage patterns
   - Optimize document preprocessing
   - Use batch processing for 50% savings
   - Implement efficient caching

2. **Resource Planning**
   - Estimate costs based on document volume
   - Plan for peak usage periods
   - Consider dedicated endpoints for consistent workloads
   - Monitor and alert on usage thresholds

## Integration Patterns

### Vector Database Integration
```python
import pinecone
import weaviate

class VectorIndexManager:
    def __init__(self, embedding_model="together-ai-embedding-151m-350m"):
        self.embedding_processor = EmbeddingProcessor(embedding_model)
        
    def setup_pinecone_index(self, index_name: str, dimension: int = 768):
        """Setup Pinecone vector database integration"""
        
        pinecone.init(
            api_key=os.environ.get("PINECONE_API_KEY"),
            environment=os.environ.get("PINECONE_ENV")
        )
        
        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                index_name,
                dimension=dimension,
                metric="cosine"
            )
        
        return pinecone.Index(index_name)
    
    def index_documents_to_pinecone(self, documents: List[dict], index_name: str):
        """Index documents in Pinecone with Together AI embeddings"""
        
        # Get Pinecone index
        index = self.setup_pinecone_index(index_name)
        
        # Generate embeddings
        texts = [doc["content"] for doc in documents]
        embedding_result = self.embedding_processor.process_documents_batch(texts)
        
        # Prepare vectors for Pinecone
        vectors = []
        for i, (doc, embedding) in enumerate(zip(documents, embedding_result["embeddings"])):
            if embedding:
                vectors.append({
                    "id": doc.get("id", f"doc_{i}"),
                    "values": embedding,
                    "metadata": {
                        "title": doc.get("title", ""),
                        "content": doc.get("content", "")[:1000],  # Truncate for metadata
                        **doc.get("metadata", {})
                    }
                })
        
        # Upsert to Pinecone
        index.upsert(vectors)
        
        return {
            "indexed_count": len(vectors),
            "total_tokens": embedding_result["total_tokens"]
        }
```

### Search API Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Embedding Search API")

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    threshold: float = 0.0
    filters: Optional[dict] = None

class EmbeddingSearchAPI:
    def __init__(self):
        self.search_engine = SemanticSearchEngine()
        
    async def initialize(self, documents: List[dict]):
        """Initialize the search engine with documents"""
        result = self.search_engine.build_index(documents)
        return result

@app.post("/search")
async def search_documents(request: SearchRequest):
    """Search documents using semantic similarity"""
    
    try:
        results = search_api.search_engine.search(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        # Apply additional filters if provided
        if request.filters:
            filtered_results = []
            for result in results["results"]:
                metadata = result["document"].get("metadata", {})
                if all(metadata.get(k) == v for k, v in request.filters.items()):
                    filtered_results.append(result)
            results["results"] = filtered_results
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize API
search_api = EmbeddingSearchAPI()
```

## Monitoring and Analytics

### Usage Tracking
```python
class EmbeddingAnalytics:
    def __init__(self):
        self.usage_log = []
        
    def track_usage(self, operation: str, tokens: int, cost: float, metadata: dict = None):
        """Track embedding API usage for analytics"""
        
        log_entry = {
            "timestamp": datetime.utcnow(),
            "operation": operation,
            "tokens": tokens,
            "cost": cost,
            "metadata": metadata or {}
        }
        
        self.usage_log.append(log_entry)
        
        # Aggregate metrics
        self._update_metrics(log_entry)
    
    def get_usage_report(self, days: int = 30):
        """Generate usage report for specified period"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_usage = [
            log for log in self.usage_log 
            if log["timestamp"] >= cutoff_date
        ]
        
        total_tokens = sum(log["tokens"] for log in recent_usage)
        total_cost = sum(log["cost"] for log in recent_usage)
        operation_counts = {}
        
        for log in recent_usage:
            op = log["operation"]
            operation_counts[op] = operation_counts.get(op, 0) + 1
        
        return {
            "period_days": days,
            "total_requests": len(recent_usage),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "average_cost_per_request": total_cost / len(recent_usage) if recent_usage else 0,
            "operations": operation_counts
        }
```

## Getting Started Guide

### Quick Setup
```bash
# Install dependencies
pip install together numpy scikit-learn

# Set environment variable
export TOGETHER_API_KEY="your-api-key-here"

# Test installation
python -c "import together; print('Together AI SDK ready')"
```

### Initial Implementation
```python
# Quick start example
import together
import os

together.api_key = os.environ.get("TOGETHER_API_KEY")

# Test embedding creation
text = "This is a test document for embedding generation."
response = together.Embeddings.create(
    model="together-ai-embedding-151m-350m",
    input=[text]
)

embedding = response.data[0].embedding
print(f"Generated embedding with {len(embedding)} dimensions")
print(f"Used {response.usage.total_tokens} tokens")
```

### Production Checklist
- [ ] API key securely stored in environment variables
- [ ] Error handling implemented for API failures
- [ ] Batch processing configured for cost optimization
- [ ] Caching strategy implemented for frequently accessed embeddings
- [ ] Monitoring and alerting set up for usage and costs
- [ ] Vector database integration configured (if needed)
- [ ] Performance testing completed for expected load
- [ ] Backup and recovery procedures established

Together AI's 151M-350M parameter embedding models provide an excellent balance of quality, performance, and cost-effectiveness for sophisticated text embedding applications across diverse industries and use cases.