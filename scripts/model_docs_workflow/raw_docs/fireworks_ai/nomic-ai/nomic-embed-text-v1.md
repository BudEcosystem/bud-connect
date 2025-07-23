# nomic-ai/nomic-embed-text-v1 - Fireworks AI

## Model Overview and Description

The nomic-ai/nomic-embed-text-v1 is a powerful text embedding model that represents the first generation of Nomic AI's embedding models. It leverages a Transformer architecture and is trained using a self-supervised MLM (Masked Language Modeling) objective, followed by contrastive training on web-scale unsupervised data and fine-tuning on a curated corpus of paired data.

This model is released under an Apache-2 license, ensuring full auditability with access to both model weights and training code. It's designed for various text embedding tasks including retrieval-augmented generation (RAG) and semantic search applications.

## Technical Specifications

- **Architecture**: Transformer-based
- **Training Objective**: Self-supervised MLM followed by contrastive training
- **Context Length**: Extended context support (predecessing v1.5's 8192 tokens)
- **License**: Apache-2 License
- **Training Data**: Web-scale unsupervised data with curated paired data fine-tuning
- **Framework Compatibility**: OpenAI API compatible through Fireworks AI

## Capabilities and Features

### Core Capabilities
- **Text Embeddings**: Converts text into vector representations for similarity tasks
- **Semantic Search**: Optimized for finding semantically related content
- **Retrieval Tasks**: Designed for information retrieval applications
- **Task Versatility**: Supports multiple downstream embedding tasks

### Key Features
- **Contrastive Training**: Enhanced through large-scale contrastive learning
- **Auditability**: Full access to model weights and training code
- **Open Source**: Released under permissive Apache-2 license
- **Production Ready**: Optimized for real-world deployment scenarios

## Fireworks AI Specific Implementation

### API Usage

Fireworks AI provides OpenAI-compatible API access to nomic-embed-text-v1:

```python
import openai

client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<FIREWORKS_API_KEY>",
)

response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1",
    input="Your text here"
)
```

### Task Prefixes (Important)

Nomic models require specific prefixes for optimal performance:
- **For documents**: Use `search_document:` prefix
- **For queries**: Use `search_query:` prefix

```python
# Document embedding
response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1",
    input="search_document: Your document content here"
)

# Query embedding
response = client.embeddings.create(
    model="nomic-ai/nomic-embed-text-v1", 
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
    "model": "nomic-ai/nomic-embed-text-v1"
  }'
```

### LangChain Integration

```python
from langchain_fireworks import FireworksEmbeddings

embeddings = FireworksEmbeddings(
    model="nomic-ai/nomic-embed-text-v1",
)

documents = embeddings.embed_documents([
    "search_document: First document",
    "search_document: Second document"
])
query = embeddings.embed_query("search_query: Your query")
```

## Performance Benchmarks

### MTEB Performance
While specific v1 benchmarks weren't detailed in available sources, the model demonstrates strong performance across various embedding tasks. The subsequent v1.5 model shows significant improvements:
- Outperforms OpenAI's Ada-002 on multiple tasks
- Strong performance on both short and long context tasks
- Competitive results across MTEB benchmark categories

### Task-Specific Performance
- **Information Retrieval**: Optimized for finding relevant documents
- **Semantic Similarity**: Strong performance in text similarity tasks
- **Classification**: Good results in text classification benchmarks
- **Clustering**: Effective for document clustering applications

## Pricing Information

Fireworks AI uses a pay-per-token pricing model:
- **Billing Model**: Pay per token with high rate limits and postpaid billing
- **Free Credits**: $1 in free credits to get started
- **Rate Limits**: 600 requests/min by default for serverless deployment
- **Cost Structure**: Token-based pricing with competitive rates
- **Business Tier**: Available for enterprise customers with custom limits

*Note: For current specific pricing rates, refer to https://fireworks.ai/pricing*

## Use Cases and Applications

### Primary Use Cases
- **Retrieval-Augmented Generation (RAG)**: Powering semantic search for RAG systems
- **Semantic Search**: Finding semantically similar content in large corpora
- **Document Similarity**: Measuring similarity between documents
- **Information Retrieval**: Retrieving relevant information from text databases
- **Content Clustering**: Grouping similar content together

### Industry Applications
- **Search Engines**: Enhancing search capabilities with semantic understanding
- **Question Answering**: Supporting knowledge base question answering systems
- **Content Management**: Organizing large document collections
- **Research**: Academic and scientific text analysis
- **Customer Support**: Finding relevant support documents and FAQs

### Integration Scenarios
- **RAG Pipelines**: Essential component for retrieval-augmented generation
- **Vector Databases**: Storing and querying text embeddings
- **Recommendation Systems**: Content-based recommendations
- **Duplicate Detection**: Finding and removing duplicate content

## Limitations and Considerations

### Model Limitations
- **Task Prefixes Required**: Must use appropriate prefixes for optimal performance
- **Context Length**: Limited compared to newer models (v1.5 extends to 8192 tokens)
- **Language Support**: Primarily optimized for English text
- **Domain Adaptation**: May require fine-tuning for highly specialized domains

### Technical Considerations
- **Prefix Management**: Critical to use correct prefixes for documents vs queries
- **Batch Processing**: Consider batch sizes for optimal performance
- **Vector Storage**: Plan for appropriate vector database solutions
- **Normalization**: Embeddings may require normalization for certain applications

### Deployment Considerations
- **Rate Limiting**: Monitor API rate limits for high-volume applications
- **Caching**: Implement caching for frequently embedded content
- **Cost Management**: Track token usage for cost optimization
- **Error Handling**: Implement robust error handling for API calls

## Original Model Provider Information

### Nomic AI
- **Organization**: Nomic AI research company
- **Mission**: Building interpretable, auditable AI systems
- **Open Source Commitment**: Full model and training code availability
- **Research Focus**: Transparent and explainable AI models

### Model Development
- **Training Approach**: Multi-stage training with MLM and contrastive learning
- **Data Sources**: Web-scale unsupervised data with curated paired datasets
- **Quality Control**: Careful curation of training data for high-quality embeddings
- **Evaluation**: Comprehensive evaluation across multiple benchmark tasks

### Related Models
- **nomic-embed-text-v1.5**: Enhanced version with 8192 context length
- **nomic-embed-vision-v1**: Multimodal variant aligned to same embedding space
- **Future Versions**: Continued development of embedding model family

## Additional Resources

### Documentation and References
- **Nomic AI Blog**: https://www.nomic.ai/blog/posts/nomic-embed-text-v1
- **Fireworks AI Docs**: https://docs.fireworks.ai/guides/querying-embeddings-models
- **Model Hub**: https://ollama.com/library/nomic-embed-text
- **API Reference**: https://docs.fireworks.ai/api-reference/creates-an-embedding-vector-representing-the-input-text

### Technical Resources
- **Training Code**: Available through Nomic AI for full auditability
- **Model Weights**: Publicly available under Apache-2 license
- **Integration Examples**: Available in LangChain and other frameworks
- **Community Support**: Active community around Nomic AI models

## Migration to v1.5

### Advantages of Upgrading
- **Extended Context**: 8192 tokens vs shorter context in v1
- **Better Performance**: Improved benchmarks across multiple tasks
- **Matryoshka Representation**: Variable embedding dimensions in v1.5
- **Multimodal Alignment**: Compatible with vision model in v1.5

### Migration Considerations
- **API Compatibility**: Same API structure and prefix requirements
- **Performance Improvements**: Generally better results with v1.5
- **Context Handling**: Can process longer documents with v1.5
- **Cost Implications**: Consider any pricing differences between versions

For new implementations, consider starting with nomic-embed-text-v1.5 for enhanced capabilities, while v1 remains suitable for existing production systems requiring stability.