# WhereIsAI/UAE-Large-V1 - Universal AnglE Embedding Model

## Overview

UAE-Large-V1 (Universal AnglE Embedding) is a state-of-the-art text embedding model developed by WhereIsAI that achieves exceptional performance on semantic textual similarity tasks. The model introduces innovative angle optimization techniques to address limitations in traditional cosine similarity measures.

## Model Architecture

**Core Specifications:**
- **Embedding Dimensions**: 1024
- **Maximum Sequence Length**: 512 tokens
- **Model Type**: Universal AnglE Embedding (AnglE)
- **License**: MIT
- **Architecture**: Based on RoBERTa-Large backbone

**Technical Innovation:**
- **AnglE Methodology**: Angle-optimized text embeddings that address cosine similarity saturation issues
- **Complex Space Optimization**: Leverages angle optimization in complex space for improved semantic understanding
- **Angle Difference Calculation**: Uses normalized angle difference to ensure high-similarity pairs have smaller angle differences

## Performance Benchmarks

### MTEB Leaderboard Performance
- **Overall Score**: 64.64 (as of December 4, 2023)
- **Ranking**: SOTA (State-of-the-Art) performance on MTEB
- **Specific Ranking**: 10th place on MTEB benchmark

### Evaluation Datasets
**Standard STS Benchmarks:**
- MRPC (Microsoft Research Paraphrase Corpus)
- QQP (Quora Question Pairs)
- QNLI (Question Natural Language Inference)
- STS-B (Semantic Textual Similarity Benchmark)
- STS 2012-2016 datasets
- SICK-R (Sentences Involving Compositional Knowledge)

**Long-Text Evaluation:**
- GitHub Issues dataset for long-text semantic textual similarity
- Superior performance on longer text sequences

## Technical Approach

### AnglE Optimization
The model addresses fundamental limitations in cosine similarity:

1. **Saturation Problem**: Traditional cosine similarity suffers from saturation zones where gradient information is lost
2. **Complex Space Solution**: Divides text embeddings into real and imaginary parts
3. **Angle Difference Computation**: Calculates angle differences in complex space
4. **Gradient Preservation**: Maintains meaningful gradients throughout training

### Mathematical Foundation
```
Traditional Cosine Similarity: cos(θ) = (A·B)/(|A||B|)
AnglE Approach: Optimizes angle θ directly in complex space
Complex Representation: z = x + iy (where x, y are embedding components)
Angle Difference: θ_diff = angle(z1) - angle(z2)
```

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
response = client.embeddings.create(
    model="WhereIsAI/UAE-Large-V1",
    input="Your text to embed here"
)

# Extract 1024-dimensional embedding
embedding = response.data[0].embedding
print(f"Embedding dimension: {len(embedding)}")  # Output: 1024
```

### Batch Processing
```python
texts = [
    "Semantic textual similarity is important for NLP",
    "Text similarity measurement is crucial in natural language processing",
    "The weather is nice today"
]

response = client.embeddings.create(
    model="WhereIsAI/UAE-Large-V1",
    input=texts
)

embeddings = [data.embedding for data in response.data]
```

### Similarity Calculation
```python
import numpy as np
from scipy.spatial.distance import cosine

# Generate embeddings for two texts
text1 = "Machine learning is fascinating"
text2 = "AI and ML are interesting fields"

response1 = client.embeddings.create(
    model="WhereIsAI/UAE-Large-V1",
    input=text1
)

response2 = client.embeddings.create(
    model="WhereIsAI/UAE-Large-V1",
    input=text2
)

# Calculate cosine similarity
similarity = 1 - cosine(response1.data[0].embedding, response2.data[0].embedding)
print(f"Similarity: {similarity:.4f}")
```

## Pricing with Fireworks AI

**Cost Structure:**
- **Input Pricing**: $0.008 per 1 million tokens
- **Output Pricing**: $0 (no charge for embeddings)
- **Token Calculation**: Based on input text length
- **Billing**: Pay-per-token model

**Cost Example:**
```python
# For 10,000 tokens of input text
cost = (10000 / 1000000) * 0.008  # $0.00008
```

## Use Cases and Applications

### 1. Semantic Search
```python
# Document similarity search
documents = ["Document 1 text", "Document 2 text", ...]
query = "Search query"

# Generate embeddings
doc_embeddings = []
for doc in documents:
    response = client.embeddings.create(
        model="WhereIsAI/UAE-Large-V1",
        input=doc
    )
    doc_embeddings.append(response.data[0].embedding)

# Find most similar document
query_response = client.embeddings.create(
    model="WhereIsAI/UAE-Large-V1",
    input=query
)
query_embedding = query_response.data[0].embedding

similarities = [1 - cosine(query_embedding, doc_emb) for doc_emb in doc_embeddings]
best_match = documents[np.argmax(similarities)]
```

### 2. RAG (Retrieval-Augmented Generation)
```python
# Vector database integration for RAG
import pinecone

# Initialize Pinecone
pinecone.init(api_key="your-pinecone-key", environment="us-west1-gcp")
index = pinecone.Index("your-index-name")

# Generate and store embeddings
def store_document(doc_id, text):
    response = client.embeddings.create(
        model="WhereIsAI/UAE-Large-V1",
        input=text
    )
    embedding = response.data[0].embedding
    
    index.upsert(vectors=[(doc_id, embedding, {"text": text})])

# Retrieve relevant documents
def retrieve_documents(query, top_k=5):
    response = client.embeddings.create(
        model="WhereIsAI/UAE-Large-V1",
        input=query
    )
    query_embedding = response.data[0].embedding
    
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return [match.metadata["text"] for match in results.matches]
```

### 3. Text Classification
```python
# Few-shot text classification using embeddings
def classify_text(text, categories):
    # Generate embedding for input text
    text_response = client.embeddings.create(
        model="WhereIsAI/UAE-Large-V1",
        input=text
    )
    text_embedding = text_response.data[0].embedding
    
    # Generate embeddings for category descriptions
    category_embeddings = []
    for category in categories:
        cat_response = client.embeddings.create(
            model="WhereIsAI/UAE-Large-V1",
            input=category
        )
        category_embeddings.append(cat_response.data[0].embedding)
    
    # Find most similar category
    similarities = [1 - cosine(text_embedding, cat_emb) for cat_emb in category_embeddings]
    return categories[np.argmax(similarities)]

# Example usage
categories = ["Technology", "Sports", "Politics", "Entertainment"]
text = "The new AI model shows impressive performance"
predicted_category = classify_text(text, categories)
```

## Performance Comparison

### vs. Other Embedding Models
| Model | MTEB Score | Dimensions | Context Length |
|-------|------------|------------|----------------|
| UAE-Large-V1 | 64.64 | 1024 | 512 |
| text-embedding-ada-002 | ~61.0 | 1536 | 8191 |
| gte-large | 63.13 | 1024 | 512 |
| nomic-embed-text-v1.5 | ~62.0 | 768 | 8192 |

### Advantages
- **Superior Angle Optimization**: Addresses cosine similarity limitations
- **SOTA Performance**: Highest MTEB score among comparable models
- **Balanced Architecture**: 1024 dimensions provide good performance/efficiency trade-off
- **Robust Training**: Evaluated on diverse STS datasets

### Considerations
- **Context Length**: Limited to 512 tokens (shorter than some alternatives)
- **Language Support**: Primarily optimized for English text
- **Computational Requirements**: 1024 dimensions require more storage than smaller models

## Integration Examples

### LangChain Integration
```python
from langchain_fireworks import FireworksEmbeddings
from langchain.vectorstores import Chroma

# Initialize embedding model
embeddings = FireworksEmbeddings(
    model="WhereIsAI/UAE-Large-V1",
    api_key="your-fireworks-api-key"
)

# Create vector store
texts = ["Document 1", "Document 2", "Document 3"]
vectorstore = Chroma.from_texts(texts, embeddings)

# Similarity search
results = vectorstore.similarity_search("Query text", k=2)
```

### Hugging Face Integration
```python
# Load model locally for comparison or fine-tuning
from transformers import AutoModel, AutoTokenizer
import torch

model_name = "WhereIsAI/UAE-Large-V1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def local_embed(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        # Use average pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.numpy()
```

## Best Practices

### 1. Text Preprocessing
```python
def preprocess_text(text):
    # Handle text length
    if len(text.split()) > 400:  # Conservative limit for 512 tokens
        text = " ".join(text.split()[:400])
    
    # Clean text
    text = text.strip()
    return text
```

### 2. Batch Processing for Efficiency
```python
def batch_embed(texts, batch_size=32):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        response = client.embeddings.create(
            model="WhereIsAI/UAE-Large-V1",
            input=batch
        )
        batch_embeddings = [data.embedding for data in response.data]
        embeddings.extend(batch_embeddings)
    return embeddings
```

### 3. Caching for Production
```python
import hashlib
import pickle
import os

def cached_embed(text, cache_dir="embeddings_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    
    # Create cache key
    cache_key = hashlib.md5(text.encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{cache_key}.pkl")
    
    # Check cache
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)
    
    # Generate embedding
    response = client.embeddings.create(
        model="WhereIsAI/UAE-Large-V1",
        input=text
    )
    embedding = response.data[0].embedding
    
    # Save to cache
    with open(cache_path, "wb") as f:
        pickle.dump(embedding, f)
    
    return embedding
```

## Research and Development

### Academic Paper
- **Title**: AnglE-optimized Text Embeddings
- **ArXiv**: https://arxiv.org/abs/2309.12871
- **Key Contribution**: Introduces angle optimization in complex space to address cosine similarity limitations

### Future Developments
- Extended context length versions
- Multilingual variants
- Domain-specific fine-tuned models
- Integration with newer transformer architectures

## Support and Resources

**Official Resources:**
- Hugging Face Model Hub: https://huggingface.co/WhereIsAI/UAE-Large-V1
- Fireworks AI Documentation: https://docs.fireworks.ai/
- Model Paper: https://arxiv.org/abs/2309.12871

**Community:**
- GitHub Discussions
- Hugging Face Community
- Research community feedback

---

*Last Updated: July 2025*
*Model achieves SOTA performance on MTEB benchmark with innovative angle optimization approach.*