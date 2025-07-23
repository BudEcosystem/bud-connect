# WhereIsAI/UAE-Large-V1 - Fireworks AI

## Model Overview and Description

WhereIsAI/UAE-Large-V1 is a state-of-the-art text embedding model that achieves SOTA performance on the MTEB Leaderboard with an average score of 64.64. The model is part of the AnglE series for training and inferring powerful sentence embeddings and is licensed under MIT, making it freely usable in any scenario.

The UAE (Universal AnglE) embedding model is designed for universal applicability across different NLP tasks while maintaining state-of-the-art performance in sentence embedding generation. It implements the innovative AnglE architecture which addresses the vanishing gradients problem from cosine function's saturation zone through angle optimization in complex space.

## Technical Specifications

- **Architecture**: Based on AnglE (https://arxiv.org/abs/2309.12871) series Embeddings
- **Base Model**: Uses pre-trained BERT model (uncased BERT base model with 110M parameters)
- **Pooling Strategy**: 'cls' pooling strategy for encoding (recommended for optimal performance)
- **Context Window**: 512 tokens (typical for BERT-based models)
- **Embedding Dimensions**: Standard BERT-based dimensions (768 typical)
- **License**: MIT License
- **Model Size**: Compact BERT-based architecture (~110M parameters)

## Capabilities and Features

### Core Capabilities
- **Universal Text Embeddings**: Designed for broad applicability across NLP tasks
- **High Performance**: SOTA performance on MTEB benchmark with 64.64 average score
- **No Prompt Required**: No need to specify any prompts when using this model
- **Angle Optimization**: Uses novel angle-optimized loss function in complex space

### Key Features
- **AnglE Loss Function**: Introduces angle optimization to deal with vanishing gradients problem
- **Complex Space Optimization**: Substantially improves text embedding quality in various scenarios
- **Multi-framework Support**: Can be used through angle_emb package or sentence-transformers framework
- **Versatile Applications**: Suitable for similarity comparisons, search, clustering, and retrieval tasks

## Fireworks AI Specific Implementation

### API Usage

Fireworks AI provides OpenAI-compatible API access to UAE-Large-V1:

```python
import openai

client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<FIREWORKS_API_KEY>",
)

response = client.embeddings.create(
    model="WhereIsAI/UAE-Large-V1",
    input="Your text here"
)
```

### REST API Example

```bash
curl --request POST \
  --url https://api.fireworks.ai/inference/v1/embeddings \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "input": "The quick brown fox jumped over the lazy dog",
    "model": "WhereIsAI/UAE-Large-V1"
  }'
```

### Integration Features
- **OpenAI Compatibility**: Fully compatible with OpenAI embeddings API
- **Fast Inference**: Optimized for blazing fast speed on Fireworks platform
- **Rate Limits**: 600 requests/min by default for serverless models
- **Post-paid Billing**: Pay-per-token with postpaid billing available

## Performance Benchmarks

### MTEB Benchmark Results
- **Overall Average Score**: 64.64 (State-of-the-art performance)
- **Classification**: 75.58 (average across 12 datasets)
- **Clustering**: 46.73 (average across 11 datasets)
- **Pair Classification**: 87.25 (average across 3 datasets)
- **Re-ranking**: 59.88 (average across 4 datasets)
- **Retrieval**: 54.66 (average across 15 datasets)

### Performance Positioning
- **MTEB Ranking**: 10th among top text embedding models
- **Innovation**: Notable for innovative loss function improvements
- **Efficiency**: Smaller model size compared to LLM-based embeddings while maintaining high performance

## Pricing Information

Fireworks AI uses a pay-per-token pricing model with the following features:
- **Billing Model**: Pay per token with high rate limits and postpaid billing
- **Free Credits**: $1 in free credits to get started
- **Cost Structure**: Token-based pricing (specific rates available on Fireworks pricing page)
- **Rate Limits**: 600 requests/min by default for serverless deployment
- **Business Tier**: Available for customers deploying at scale with custom rate limits

*Note: For current specific pricing rates, refer to https://fireworks.ai/pricing*

## Use Cases and Applications

### Primary Use Cases
- **Semantic Search**: Optimized for finding semantically similar content
- **Similarity Comparisons**: Measuring text similarity across documents
- **Information Retrieval**: Retrieving relevant information from large text corpora
- **Clustering**: Grouping texts with similar semantic meanings
- **Duplicate Detection**: Removing semantic duplicates from text collections

### Industry Applications
- **Search Engines**: Powering semantic search capabilities
- **Question Answering**: Supporting retrieval-augmented generation (RAG) systems
- **Content Management**: Organizing and categorizing large document collections
- **Research**: Academic and scientific text analysis and organization

## Limitations and Considerations

### Model Limitations
- **Language Support**: Optimized primarily for English text
- **Context Length**: Limited to 512 tokens (typical BERT constraint)
- **Domain Specificity**: While universal, may require fine-tuning for highly specialized domains
- **Model Size**: Smaller than large language model-based embeddings, which may limit some capabilities

### Technical Considerations
- **Pooling Strategy**: Best performance achieved with 'cls' pooling strategy
- **No Prompting**: Unlike some models, doesn't require specific task prompts
- **Framework Compatibility**: Supports both angle_emb and sentence-transformers frameworks

### Deployment Considerations
- **Rate Limits**: Consider rate limiting for high-volume applications
- **Cost Management**: Monitor token usage for cost optimization
- **Caching**: Implement caching strategies for frequently embedded texts

## Original Model Provider Information

### WhereIsAI
- **Organization**: WhereIsAI research organization
- **Model Family**: UAE (Universal AnglE) series
- **Research Focus**: Advanced embedding models using angle optimization techniques
- **Open Source**: Released under MIT license for broad accessibility

### Related Models
- **WhereIsAI/UAE-Code-Large-V1**: Specialized variant for code or GitHub issue similarity measurement
- **AnglE Series**: Part of broader AnglE research for sentence embeddings

### Research Background
- **Paper**: Based on AnglE research (https://arxiv.org/abs/2309.12871)
- **Innovation**: Introduces angle optimization in complex space for improved embedding quality
- **Methodology**: Multi-stage contrastive learning approach for effective text embeddings

## Additional Resources

- **Hugging Face Model Page**: https://huggingface.co/WhereIsAI/UAE-Large-V1
- **Fireworks AI Documentation**: https://docs.fireworks.ai/guides/querying-embeddings-models
- **AnglE Research Paper**: https://arxiv.org/abs/2309.12871
- **MTEB Leaderboard**: For current benchmark standings and comparisons

## Integration Examples

### LangChain Integration
```python
from langchain_fireworks import FireworksEmbeddings

embeddings = FireworksEmbeddings(
    model="WhereIsAI/UAE-Large-V1",
)

text_embeddings = embeddings.embed_documents(["Your text here"])
query_embedding = embeddings.embed_query("Your query here")
```

### Batch Processing
```python
response = client.embeddings.create(
    model="WhereIsAI/UAE-Large-V1",
    input=[
        "First document text",
        "Second document text",
        "Third document text"
    ]
)
```