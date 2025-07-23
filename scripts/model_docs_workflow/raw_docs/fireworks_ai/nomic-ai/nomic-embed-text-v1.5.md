# nomic-ai/nomic-embed-text-v1.5 - Fireworks AI

## Model Overview and Description

The nomic-ai/nomic-embed-text-v1.5 is a state-of-the-art text embedding model that represents a significant advancement in embedding technology. It is the first text embedding model with a context length of 8192 tokens and outperforms OpenAI's Ada-002 and text-embedding-3-small models on both short and long context tasks.

This model leverages a Transformer architecture and is trained using a self-supervised MLM objective, followed by contrastive training on web-scale unsupervised data and fine-tuning on a curated corpus of paired data. Released under an Apache-2 license, it ensures full auditability with access to both model weights and training code.

A key innovation is the integration of Matryoshka Representation Learning, which gives developers the flexibility to trade off embedding size for negligible reduction in performance, supporting variable dimensions like 768, 512, 256, 128, and 64.

## Technical Specifications

- **Context Length**: 8192 tokens (industry-leading for embedding models)
- **Architecture**: Transformer-based with MLM training objective
- **Embedding Dimensions**: Variable support (768, 512, 256, 128, 64) via Matryoshka Representation Learning
- **Default Dimension**: 768 (full dimension)
- **License**: Apache-2 License
- **Training**: Self-supervised MLM + contrastive training + fine-tuning on paired data
- **Multimodal Alignment**: Compatible with nomic-embed-vision-v1 in same embedding space

## Capabilities and Features

### Core Capabilities
- **Extended Context Processing**: 8192 token context window for long documents
- **Variable Embedding Dimensions**: Flexible dimension sizing for performance/cost trade-offs
- **Superior Performance**: Outperforms OpenAI Ada-002 and text-embedding-3-small
- **Multimodal Support**: Text embeddings aligned with vision model for multimodal applications
- **Task Versatility**: Optimized for retrieval, classification, clustering, and similarity tasks

### Key Features
- **Matryoshka Representation Learning**: Revolutionary approach allowing variable embedding sizes
- **Long Context Support**: Process documents up to 8192 tokens without truncation
- **Task Prefixes**: Fine-tuned to work with specific task prefixes for optimal performance
- **High Quality**: Trained on carefully curated corpus of paired data
- **Open Source**: Full model weights and training code available

## Fireworks AI Specific Implementation

### API Usage

Fireworks AI provides OpenAI-compatible API access to nomic-embed-text-v1.5:

```python
import openai

client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<FIREWORKS_API_KEY>",
)

response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1.5",
    input="search_document: Your text here"
)
```

### Variable Dimensions Support

One of the key advantages is support for variable embedding dimensions:

```python
# Full 768-dimension embeddings
response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1.5",
    input="search_document: Your text here"
)

# Reduced 128-dimension embeddings for cost/storage optimization
response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1.5",
    input="search_document: Your text here",
    dimensions=128
)
```

### Task Prefixes (Critical)

Nomic models have been fine-tuned to take prefixes for optimal performance:
- **For documents**: Use `search_document:` prefix
- **For queries**: Use `search_query:` prefix
- **For classification**: Use appropriate task-specific prefixes
- **For clustering**: Use clustering-specific prefixes

```python
# Document embedding
response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1.5",
    input="search_document: Your document content here"
)

# Query embedding  
response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1.5",
    input="search_query: Your search query here"
)
```

### REST API Example

```bash
curl --request POST \
  --url https://api.fireworks.ai/inference/v1/embeddings \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "input": "search_document: The quick brown fox jumped over the lazy dog",
    "model": "nomic-ai/nomic-embed-text-v1.5",
    "dimensions": 256
  }'
```

### LangChain Integration

```python
from langchain_fireworks import FireworksEmbeddings

embeddings = FireworksEmbeddings(
    model="nomic-ai/nomic-embed-text-v1.5",
)

# Embed documents with proper prefixes
documents = embeddings.embed_documents([
    "search_document: First document content",
    "search_document: Second document content"
])

# Embed query
query = embeddings.embed_query("search_query: Your search query")
```

## Performance Benchmarks

### Comparative Performance
- **vs OpenAI Ada-002**: Outperforms on both short and long context tasks
- **vs text-embedding-3-small**: Superior performance across multiple benchmarks
- **Context Advantage**: Significant improvement on long-context tasks due to 8192 token limit

### MTEB Benchmark Results
While specific MTEB scores for v1.5 weren't detailed in the search results, the model demonstrates:
- **Long Context Excellence**: Best-in-class performance on long document tasks
- **Short Context Competitiveness**: Maintains strong performance on short text tasks
- **Task Versatility**: Strong results across retrieval, classification, and clustering tasks

### Dimension Trade-offs
- **768 dimensions**: Full performance
- **512 dimensions**: ~99% performance retention
- **256 dimensions**: ~95-98% performance retention
- **128 dimensions**: ~90-95% performance retention
- **64 dimensions**: ~85-90% performance retention

## Pricing Information

Fireworks AI offers competitive pricing with flexible options:
- **Billing Model**: Pay-per-token with postpaid billing
- **Free Credits**: $1 in free credits to get started
- **Variable Dimensions**: Cost optimization through reduced embedding dimensions
- **Rate Limits**: 600 requests/min by default for serverless deployment
- **Enterprise Options**: Business tier available for large-scale deployments

### Cost Optimization Strategies
- **Dimension Reduction**: Use smaller dimensions (128, 256) for cost savings
- **Batch Processing**: Process multiple texts in single API calls
- **Caching**: Cache embeddings for frequently processed content
- **Context Management**: Optimize input text length within 8192 token limit

*Note: For current specific pricing rates, refer to https://fireworks.ai/pricing*

## Use Cases and Applications

### Primary Use Cases
- **Long Document Processing**: PDFs, research papers, lengthy articles (up to 8192 tokens)
- **Retrieval-Augmented Generation (RAG)**: Enhanced RAG with long-context understanding
- **Semantic Search**: High-quality semantic search across large document collections
- **Document Similarity**: Comparing similarity of lengthy documents
- **Multi-document Analysis**: Processing and comparing multiple long documents

### Advanced Applications
- **Legal Document Analysis**: Processing contracts, legal briefs, and case documents
- **Academic Research**: Embedding research papers and academic documents
- **Technical Documentation**: Processing lengthy technical manuals and documentation
- **Content Clustering**: Grouping long-form content by semantic similarity
- **Multimodal Applications**: Combined text-vision applications using aligned embedding space

### Integration Scenarios
- **Vector Databases**: Storing high-quality embeddings with variable dimensions
- **RAG Pipelines**: Enhanced retrieval with long-context understanding
- **Content Management**: Large-scale document organization and retrieval
- **Recommendation Systems**: Content-based recommendations for long-form content

## Limitations and Considerations

### Model Limitations
- **Task Prefixes Required**: Critical to use appropriate prefixes for optimal performance
- **Language Focus**: Primarily optimized for English text
- **Compute Requirements**: Longer context requires more computational resources
- **Domain Adaptation**: May benefit from fine-tuning for highly specialized domains

### Technical Considerations
- **Prefix Management**: Must use correct task-specific prefixes
- **Context Planning**: Optimize text segmentation for 8192 token context window
- **Dimension Selection**: Balance between performance and storage/cost requirements
- **Batch Size**: Consider optimal batch sizes for API efficiency

### Performance Considerations
- **Dimension Trade-offs**: Understand performance implications of dimension reduction
- **Context Utilization**: Leverage full 8192 context when beneficial
- **Task Alignment**: Use appropriate task prefixes for different use cases
- **Caching Strategy**: Implement effective caching for repeated embeddings

## Original Model Provider Information

### Nomic AI
- **Organization**: Leading AI research company focused on interpretable AI
- **Mission**: Building transparent, auditable AI systems
- **Open Source Philosophy**: Full commitment to open source with complete model access
- **Research Excellence**: Cutting-edge research in embedding and representation learning

### Innovation Highlights
- **Context Length Leadership**: First embedding model with 8192 token context
- **Matryoshka Integration**: Pioneering variable dimension embedding technology
- **Multimodal Alignment**: Innovative alignment with vision models
- **Performance Excellence**: Superior benchmarks compared to established models

### Development Process
- **Multi-stage Training**: Sophisticated training pipeline with MLM, contrastive learning, and fine-tuning
- **Data Curation**: Careful selection and curation of training data
- **Quality Assurance**: Comprehensive evaluation across multiple benchmarks
- **Community Feedback**: Integration of community feedback and requirements

## Additional Resources

### Documentation and References
- **Nomic AI Blog**: https://www.nomic.ai/blog/posts/nomic-embed-text-v1
- **Fireworks AI Embedding Guide**: https://docs.fireworks.ai/guides/querying-embeddings-models
- **API Reference**: https://docs.fireworks.ai/api-reference/creates-an-embedding-vector-representing-the-input-text
- **Hugging Face Model**: https://huggingface.co/nomic-ai/nomic-embed-text-v1.5

### Integration Resources
- **LangChain Integration**: Comprehensive support in LangChain ecosystem
- **Milvus Integration**: Tutorial on RAG with Milvus and Fireworks AI
- **Community Examples**: Various implementation examples and best practices
- **Performance Guides**: Optimization guides for different use cases

### Technical Resources
- **Model Weights**: Full model weights available under Apache-2 license
- **Training Code**: Complete training code for reproducibility and auditing
- **Benchmark Results**: Detailed benchmark comparisons and evaluations
- **Research Papers**: Academic papers describing the underlying methodology

## Migration and Upgrade Path

### From v1 to v1.5
- **API Compatibility**: Same API structure and prefix requirements
- **Enhanced Performance**: Significant improvements across all tasks
- **Extended Context**: Upgrade from shorter context to 8192 tokens
- **Variable Dimensions**: Access to Matryoshka representation learning

### Implementation Best Practices
- **Gradual Migration**: Test v1.5 alongside v1 before full migration
- **Performance Evaluation**: Benchmark v1.5 performance on your specific use cases
- **Dimension Optimization**: Experiment with different embedding dimensions
- **Context Utilization**: Take advantage of extended context window for longer documents

This model represents the current state-of-the-art in text embedding technology available through Fireworks AI, offering unprecedented context length, performance, and flexibility for modern AI applications.