# Vertex AI Authentication and SDK Setup

## Overview

This guide provides comprehensive instructions for setting up authentication and SDKs for Google Cloud Vertex AI, including the latest recommendations for 2025. Google has transitioned to the Google Gen AI SDK as the recommended approach for accessing generative AI models on Vertex AI.

## Important SDK Changes (2025)

### Deprecated: Vertex AI SDK Generative AI Modules
- **Deprecation Date**: June 24, 2025
- **Removal Date**: June 24, 2026
- **Action Required**: Migrate to Google Gen AI SDK

### Recommended: Google Gen AI SDK
- **Current Status**: Generally Available
- **Primary Support**: Unified SDK for Google AI and Vertex AI
- **Migration Path**: Google provides migration tools and documentation

## Google Gen AI SDK Setup

### Installation

```bash
# Install the Google Gen AI SDK
pip install google-genai

# Optional: Install with additional dependencies
pip install google-genai[all]

# For development/testing
pip install google-genai[dev]
```

### Environment Variables Configuration

```bash
# Required environment variables for Vertex AI
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="True"

# Optional: Specify credentials file
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Basic Setup and Usage

```python
import os
from google import genai
from google.genai.types import HttpOptions

# Set environment variables (if not set in shell)
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

# Initialize the client
client = genai.Client(
    http_options=HttpOptions(api_version="v1")
)

# Basic text generation
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain quantum computing in simple terms."
)

print(response.text)
```

## Authentication Methods

### 1. Default Application Credentials (Recommended)

This is the most common method for production environments and local development.

#### Setup for Local Development
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate with your Google account
gcloud auth application-default login

# Set your project
gcloud config set project your-project-id
```

#### Code Implementation
```python
from google.auth import default
from google import genai

# Automatically uses default credentials
credentials, project = default()

client = genai.Client()

# The client will automatically use the default credentials
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello, world!"
)
```

### 2. Service Account Authentication

Recommended for production deployments and CI/CD pipelines.

#### Creating a Service Account
```bash
# Create a service account
gcloud iam service-accounts create vertex-ai-service \
    --display-name="Vertex AI Service Account" \
    --description="Service account for Vertex AI API access"

# Grant necessary permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:vertex-ai-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key file
gcloud iam service-accounts keys create vertex-ai-key.json \
    --iam-account=vertex-ai-service@your-project-id.iam.gserviceaccount.com
```

#### Code Implementation
```python
from google.auth import service_account
from google import genai

# Load service account credentials
credentials = service_account.Credentials.from_service_account_file(
    'path/to/vertex-ai-key.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Create client with specific credentials
client = genai.Client(credentials=credentials)

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Analyze this data for patterns."
)
```

### 3. Workload Identity (GKE/Cloud Run)

For applications running on Google Cloud services.

#### Kubernetes Setup
```yaml
# kubernetes-service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: vertex-ai-ksa
  namespace: default
  annotations:
    iam.gke.io/gcp-service-account: vertex-ai-service@your-project-id.iam.gserviceaccount.com
```

```bash
# Bind Kubernetes service account to Google service account
gcloud iam service-accounts add-iam-policy-binding \
    vertex-ai-service@your-project-id.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:your-project-id.svc.id.goog[default/vertex-ai-ksa]"
```

#### Code Implementation
```python
from google import genai

# Workload Identity automatically provides credentials
client = genai.Client()

# No explicit credential configuration needed
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Process this request."
)
```

## Advanced Configuration

### Custom HTTP Options

```python
from google import genai
from google.genai.types import HttpOptions
import requests

# Configure custom HTTP settings
http_options = HttpOptions(
    api_version="v1",
    timeout=60,  # Request timeout in seconds
    retry_config={
        "max_retries": 3,
        "backoff_factor": 2
    }
)

client = genai.Client(http_options=http_options)
```

### Regional Configuration

```python
import os
from google import genai

# Configure for specific region
os.environ['GOOGLE_CLOUD_LOCATION'] = 'europe-west1'

client = genai.Client()

# Client will use Europe region for processing
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Process in European region."
)
```

### Global Endpoint Configuration

```python
import os
from google import genai

# Use global endpoint for higher availability
os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'

client = genai.Client()

# Requests will be automatically load-balanced globally
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="High availability request."
)
```

## Legacy Vertex AI SDK (Deprecated)

### Migration from Legacy SDK

If you're currently using the deprecated Vertex AI SDK, here's how to migrate:

#### Old Approach (Deprecated)
```python
# DEPRECATED - Do not use in new projects
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="your-project", location="us-central1")
model = GenerativeModel("gemini-pro")
response = model.generate_content("Hello")
```

#### New Approach (Recommended)
```python
# RECOMMENDED - Use Google Gen AI SDK
from google import genai
import os

os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello"
)
```

## Anthropic Claude on Vertex AI

### Setup for Claude Models

```python
import anthropic
from google.auth import default

# Get default Google Cloud credentials
credentials, project = default()

# Initialize Anthropic client for Vertex AI
client = anthropic.AnthropicVertex(
    region="us-central1",
    project_id=project
)

# Use Claude models through Vertex AI
message = client.messages.create(
    model="claude-3-7-sonnet@20250219",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain machine learning concepts."}
    ]
)

print(message.content)
```

### Direct Anthropic SDK with Vertex AI

```python
# Alternative approach using direct Anthropic SDK
import anthropic
import os

# Set Vertex AI configuration
os.environ['ANTHROPIC_VERTEX_REGION'] = 'us-central1'
os.environ['ANTHROPIC_VERTEX_PROJECT_ID'] = 'your-project-id'

# The SDK will automatically use Vertex AI
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-5-sonnet@20241022",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Write a Python function to sort a list."}
    ]
)
```

## Error Handling and Best Practices

### Robust Error Handling

```python
from google import genai
from google.api_core import exceptions
import time
import random

def generate_with_retry(client, model, content, max_retries=3):
    """Generate content with exponential backoff retry logic."""
    
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=content
            )
            return response
            
        except exceptions.ResourceExhausted as e:
            # Handle quota/rate limit errors
            if attempt < max_retries:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise e
                
        except exceptions.GoogleAPIError as e:
            # Handle other API errors
            print(f"API Error: {e}")
            if attempt < max_retries and e.code in [503, 502]:
                # Retry on server errors
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                raise e
                
        except Exception as e:
            # Handle unexpected errors
            print(f"Unexpected error: {e}")
            raise e

# Usage example
client = genai.Client()
response = generate_with_retry(
    client, 
    "gemini-2.5-flash", 
    "Explain neural networks."
)
```

### Authentication Validation

```python
from google import genai
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

def validate_authentication():
    """Validate Google Cloud authentication setup."""
    try:
        credentials, project = default()
        print(f"✓ Authentication successful")
        print(f"✓ Project: {project}")
        
        # Test API access
        client = genai.Client()
        models = client.models.list()
        print(f"✓ API access successful. Available models: {len(list(models))}")
        
        return True
        
    except DefaultCredentialsError:
        print("✗ No valid credentials found")
        print("Please run: gcloud auth application-default login")
        return False
        
    except Exception as e:
        print(f"✗ Authentication error: {e}")
        return False

# Validate before starting
if validate_authentication():
    print("Ready to use Vertex AI!")
else:
    print("Please fix authentication issues before proceeding.")
```

## Environment-Specific Configurations

### Development Environment

```python
# development_config.py
import os
from google import genai

def setup_development():
    """Setup for local development."""
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-dev-project'
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
    os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'
    
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    return genai.Client()

client = setup_development()
```

### Production Environment

```python
# production_config.py
import os
from google import genai
from google.genai.types import HttpOptions

def setup_production():
    """Setup for production deployment."""
    
    # Production configuration
    http_options = HttpOptions(
        api_version="v1",
        timeout=30,  # Shorter timeout for production
        retry_config={
            "max_retries": 5,
            "backoff_factor": 1.5
        }
    )
    
    client = genai.Client(http_options=http_options)
    
    # Validate setup
    try:
        # Test with a simple request
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Test connection"
        )
        print("✓ Production setup validated")
    except Exception as e:
        print(f"✗ Production setup failed: {e}")
        raise
    
    return client
```

### Testing Environment

```python
# test_config.py
import os
from google import genai
from unittest.mock import Mock

def setup_testing():
    """Setup for testing with mocked responses."""
    
    # Use test project
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-test-project'
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
    os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'
    
    # For unit tests, you might want to mock the client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.text = "Mocked response"
    mock_client.models.generate_content.return_value = mock_response
    
    return mock_client

# For integration tests
def setup_integration_testing():
    """Setup for integration testing with real API."""
    return genai.Client()
```

## Monitoring and Observability

### Basic Usage Monitoring

```python
import time
from google import genai
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoredVertexAIClient:
    """Wrapper class for monitoring Vertex AI usage."""
    
    def __init__(self):
        self.client = genai.Client()
        self.request_count = 0
        self.total_latency = 0
    
    def generate_content(self, model, contents, **kwargs):
        """Generate content with monitoring."""
        start_time = time.time()
        
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                **kwargs
            )
            
            # Track metrics
            latency = time.time() - start_time
            self.request_count += 1
            self.total_latency += latency
            
            logger.info(f"Request completed - Model: {model}, Latency: {latency:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Request failed - Model: {model}, Error: {e}")
            raise
    
    def get_stats(self):
        """Get usage statistics."""
        avg_latency = self.total_latency / max(self.request_count, 1)
        return {
            "request_count": self.request_count,
            "average_latency": avg_latency,
            "total_latency": self.total_latency
        }

# Usage
monitored_client = MonitoredVertexAIClient()
response = monitored_client.generate_content(
    "gemini-2.5-flash",
    "Explain photosynthesis."
)

print(monitored_client.get_stats())
```

## Troubleshooting Common Issues

### Authentication Issues

```python
def diagnose_auth_issues():
    """Diagnose common authentication problems."""
    
    import os
    from google.auth import default
    
    print("=== Authentication Diagnosis ===")
    
    # Check environment variables
    required_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'GOOGLE_CLOUD_LOCATION', 
        'GOOGLE_GENAI_USE_VERTEXAI'
    ]
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: Not set")
    
    # Check credentials
    try:
        credentials, project = default()
        print(f"✓ Default credentials found for project: {project}")
    except Exception as e:
        print(f"✗ Credential error: {e}")
    
    # Check API access
    try:
        from google import genai
        client = genai.Client()
        # Attempt a simple operation
        models = list(client.models.list())
        print(f"✓ API access successful. {len(models)} models available.")
    except Exception as e:
        print(f"✗ API access failed: {e}")

# Run diagnosis
diagnose_auth_issues()
```

### Quota and Rate Limiting

```python
from google import genai
from google.api_core import exceptions
import time

def handle_rate_limits():
    """Example of handling rate limits and quotas."""
    
    client = genai.Client()
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Your request here"
        )
        return response
        
    except exceptions.ResourceExhausted as e:
        print(f"Quota exceeded: {e}")
        print("Solutions:")
        print("1. Wait and retry later")
        print("2. Request quota increase in Google Cloud Console")
        print("3. Use a different region")
        print("4. Optimize request frequency")
        
    except exceptions.TooManyRequests as e:
        print(f"Rate limit exceeded: {e}")
        print("Implementing exponential backoff...")
        time.sleep(2)  # Wait before retry
```

## Security Best Practices

### Credential Security

```python
import os
from google import genai

# ✓ Good: Use environment variables
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv('PROJECT_ID')

# ✗ Bad: Hard-code credentials
# PROJECT_ID = "my-project-123"  # Never do this

# ✓ Good: Use service account files in secure locations
# credentials_path = "/secure/path/service-account.json"

# ✗ Bad: Store credentials in code repository
# credentials_path = "./my-key.json"  # Don't commit keys to git
```

### Network Security

```python
# For production environments with VPC-SC
import os
from google import genai

def setup_secure_client():
    """Setup client for VPC-SC environment."""
    
    # Configure for VPC Service Controls
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-vpc-sc-project'
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
    
    # Client will automatically use VPC-SC if configured
    client = genai.Client()
    
    return client
```

This authentication and setup guide provides comprehensive coverage of all authentication methods, SDK setup, and best practices for using Vertex AI in 2025. The focus on the Google Gen AI SDK ensures you're using the most current and supported approach.