# Vertex AI Regional Availability and Endpoints

## Overview

Google Cloud Vertex AI provides both regional and global endpoints for accessing AI models. Understanding regional availability is crucial for optimizing latency, ensuring data residency compliance, and meeting performance requirements.

## Global vs Regional Endpoints

### Global Endpoint
- **URL Format**: `https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/...`
- **Coverage**: Worldwide with automatic load balancing
- **Benefits**: Higher availability, reduced 429 errors, automatic failover
- **Limitation**: No control over processing region

### Regional Endpoints
- **URL Format**: `https://{location}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{location}/...`
- **Coverage**: Specific geographic region
- **Benefits**: Data residency control, predictable latency, compliance
- **Limitation**: Single region dependency

## Regional Availability by Model Type

### Gemini Models (Native Vertex AI)

#### Generally Available Regions
- **us-central1** (Iowa, USA)
- **us-east1** (South Carolina, USA)
- **us-west1** (Oregon, USA)
- **us-west4** (Las Vegas, USA)
- **europe-west1** (Belgium)
- **europe-west3** (Frankfurt, Germany)
- **europe-west4** (Netherlands)
- **asia-northeast1** (Tokyo, Japan)
- **asia-southeast1** (Singapore)
- **asia-south1** (Mumbai, India)

#### Preview/Limited Availability Regions
- **europe-west2** (London, UK) - Limited models
- **asia-northeast3** (Seoul, South Korea) - Limited models
- **australia-southeast1** (Sydney) - Limited models

### Anthropic Claude Models

#### Supported Regions (2025)
- **us-central1** (Iowa, USA)
- **us-east1** (South Carolina, USA)
- **europe-west1** (Belgium)
- **asia-northeast1** (Tokyo, Japan)

> **Note**: Claude models require regions that specifically support Anthropic models. Not all Vertex AI regions support Claude.

## Model-Specific Regional Availability

### Gemini 2.5 Series
```json
{
  "gemini-2.5-pro": {
    "regions": [
      "us-central1", "us-east1", "us-west1", "us-west4",
      "europe-west1", "europe-west3", "europe-west4",
      "asia-northeast1", "asia-southeast1", "asia-south1"
    ],
    "global_endpoint": true
  },
  "gemini-2.5-flash": {
    "regions": [
      "us-central1", "us-east1", "us-west1", "us-west4",
      "europe-west1", "europe-west3", "europe-west4",
      "asia-northeast1", "asia-southeast1", "asia-south1"
    ],
    "global_endpoint": true
  }
}
```

### Gemini 2.0 Series
```json
{
  "gemini-2.0-flash": {
    "regions": [
      "us-central1", "us-east1", "us-west1",
      "europe-west1", "europe-west3",
      "asia-northeast1", "asia-southeast1"
    ],
    "global_endpoint": true,
    "fine_tuning_regions": ["us-central1", "europe-west1"]
  },
  "gemini-2.0-flash-lite": {
    "regions": [
      "us-central1", "us-east1",
      "europe-west1",
      "asia-northeast1"
    ],
    "global_endpoint": true
  }
}
```

### Claude Models
```json
{
  "claude-opus-4": {
    "regions": ["us-central1", "us-east1", "europe-west1", "asia-northeast1"],
    "global_endpoint": false
  },
  "claude-sonnet-4": {
    "regions": ["us-central1", "us-east1", "europe-west1", "asia-northeast1"],
    "global_endpoint": false
  },
  "claude-3-7-sonnet": {
    "regions": ["us-central1", "us-east1", "europe-west1"],
    "global_endpoint": false
  }
}
```

## Regional Configuration

### Setting Regional Endpoints

#### Environment Variable Approach
```python
import os
from google import genai

# Set specific region
os.environ['GOOGLE_CLOUD_LOCATION'] = 'europe-west1'

client = genai.Client()

# All requests will use Europe West 1
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Process in European region"
)
```

#### Programmatic Approach
```python
from google import genai
from google.genai.types import HttpOptions

# Create client with specific region
client = genai.Client(
    http_options=HttpOptions(
        api_version="v1",
        base_url="https://europe-west1-aiplatform.googleapis.com"
    )
)
```

### Global Endpoint Configuration
```python
import os
from google import genai

# Use global endpoint
os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'

client = genai.Client()

# Requests automatically load-balanced globally
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="High availability request"
)
```

## Latency Optimization

### Regional Latency Considerations

#### North America
- **Lowest Latency**: us-central1 (Iowa) for central US
- **East Coast**: us-east1 (South Carolina)
- **West Coast**: us-west1 (Oregon) or us-west4 (Las Vegas)

#### Europe
- **GDPR Compliance**: europe-west1 (Belgium), europe-west3 (Germany)
- **UK Access**: europe-west2 (London) - limited availability
- **General Purpose**: europe-west1 for best model availability

#### Asia Pacific
- **Japan**: asia-northeast1 (Tokyo)
- **Southeast Asia**: asia-southeast1 (Singapore)
- **India**: asia-south1 (Mumbai)

### Latency Testing Example
```python
import time
from google import genai
import os

def test_regional_latency(regions, model, prompt):
    """Test latency across different regions."""
    
    results = {}
    
    for region in regions:
        os.environ['GOOGLE_CLOUD_LOCATION'] = region
        client = genai.Client()
        
        # Warm up
        try:
            client.models.generate_content(model=model, contents="test")
        except:
            continue
        
        # Measure latency
        start_time = time.time()
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            latency = time.time() - start_time
            results[region] = {
                'latency': latency,
                'success': True,
                'response_length': len(response.text)
            }
        except Exception as e:
            results[region] = {
                'latency': None,
                'success': False,
                'error': str(e)
            }
    
    return results

# Test regions
regions = ['us-central1', 'us-east1', 'europe-west1', 'asia-northeast1']
results = test_regional_latency(
    regions, 
    'gemini-2.5-flash', 
    'Explain machine learning in one sentence.'
)

for region, data in results.items():
    if data['success']:
        print(f"{region}: {data['latency']:.2f}s")
    else:
        print(f"{region}: Failed - {data['error']}")
```

## Data Residency and Compliance

### European Data Residency (GDPR)
```python
import os
from google import genai

# Ensure data stays in Europe
os.environ['GOOGLE_CLOUD_LOCATION'] = 'europe-west1'  # Belgium
# or
os.environ['GOOGLE_CLOUD_LOCATION'] = 'europe-west3'  # Germany

client = genai.Client()

# Data processing guaranteed in specified European region
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="GDPR-compliant processing request"
)
```

### US Data Residency
```python
import os
from google import genai

# Keep data in United States
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

client = genai.Client()

# Data stays within US borders
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="US-resident data processing"
)
```

### Asia Pacific Data Residency
```python
import os
from google import genai

# Process data in Asia Pacific
regions = {
    'japan': 'asia-northeast1',
    'singapore': 'asia-southeast1',
    'india': 'asia-south1'
}

os.environ['GOOGLE_CLOUD_LOCATION'] = regions['japan']

client = genai.Client()

# Data processed in specified APAC region
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="APAC regional processing"
)
```

## Fallback and High Availability Strategies

### Multi-Region Fallback
```python
import os
from google import genai
from google.api_core import exceptions

class MultiRegionClient:
    """Client with automatic regional fallback."""
    
    def __init__(self, preferred_regions):
        self.preferred_regions = preferred_regions
        self.clients = {}
        
        # Initialize clients for each region
        for region in preferred_regions:
            os.environ['GOOGLE_CLOUD_LOCATION'] = region
            self.clients[region] = genai.Client()
    
    def generate_content_with_fallback(self, model, contents, **kwargs):
        """Try regions in order until one succeeds."""
        
        last_error = None
        
        for region in self.preferred_regions:
            try:
                client = self.clients[region]
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    **kwargs
                )
                print(f"✓ Success using region: {region}")
                return response, region
                
            except exceptions.ResourceExhausted as e:
                print(f"✗ Quota exhausted in {region}")
                last_error = e
                continue
                
            except exceptions.ServiceUnavailable as e:
                print(f"✗ Service unavailable in {region}")
                last_error = e
                continue
                
            except Exception as e:
                print(f"✗ Error in {region}: {e}")
                last_error = e
                continue
        
        # All regions failed
        raise last_error

# Usage example
client = MultiRegionClient(['us-central1', 'us-east1', 'europe-west1'])

response, used_region = client.generate_content_with_fallback(
    model="gemini-2.5-flash",
    contents="High availability request"
)

print(f"Processed using region: {used_region}")
```

### Global Endpoint with Regional Fallback
```python
import os
from google import genai
from google.api_core import exceptions

def smart_endpoint_selection(model, contents, **kwargs):
    """Try global endpoint first, fallback to regional."""
    
    # Try global endpoint first
    try:
        os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'
        global_client = genai.Client()
        
        response = global_client.models.generate_content(
            model=model,
            contents=contents,
            **kwargs
        )
        return response, 'global'
        
    except exceptions.ResourceExhausted:
        print("Global endpoint quota exhausted, trying regional...")
        
        # Fallback to specific regions
        fallback_regions = ['us-central1', 'europe-west1', 'asia-northeast1']
        
        for region in fallback_regions:
            try:
                os.environ['GOOGLE_CLOUD_LOCATION'] = region
                regional_client = genai.Client()
                
                response = regional_client.models.generate_content(
                    model=model,
                    contents=contents,
                    **kwargs
                )
                return response, region
                
            except exceptions.ResourceExhausted:
                continue
    
    raise exceptions.ResourceExhausted("All endpoints exhausted")

# Usage
response, endpoint = smart_endpoint_selection(
    "gemini-2.5-flash",
    "Process this request with high availability"
)
print(f"Processed using: {endpoint}")
```

## Regional Quota Management

### Understanding Regional Quotas
```python
from google.cloud import monitoring_v3
import os

def check_regional_quotas(project_id, regions):
    """Check quota usage across regions."""
    
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    
    for region in regions:
        print(f"\n=== Quota Status for {region} ===")
        
        # Example quota metrics (actual metrics may vary)
        metrics = [
            'serviceruntime.googleapis.com/quota/rate/net_usage',
            'serviceruntime.googleapis.com/quota/allocation/usage'
        ]
        
        for metric in metrics:
            try:
                # Query quota metrics
                interval = monitoring_v3.TimeInterval({
                    "end_time": {"seconds": int(time.time())},
                    "start_time": {"seconds": int(time.time() - 3600)}
                })
                
                results = client.list_time_series(
                    request={
                        "name": project_name,
                        "filter": f'metric.type="{metric}"',
                        "interval": interval,
                    }
                )
                
                for result in results:
                    print(f"  {metric}: {result.points[-1].value.double_value}")
                    
            except Exception as e:
                print(f"  Error checking {metric}: {e}")

# Usage
check_regional_quotas('your-project-id', ['us-central1', 'europe-west1'])
```

### Quota Optimization Strategies
```python
class QuotaAwareClient:
    """Client that manages quota across regions."""
    
    def __init__(self, regions_with_quotas):
        self.regions = regions_with_quotas
        self.usage_tracking = {region: 0 for region in regions_with_quotas}
    
    def select_optimal_region(self, model):
        """Select region based on quota availability."""
        
        # Check which regions support the model
        supported_regions = self.get_supported_regions(model)
        
        # Find region with lowest usage
        available_regions = [
            r for r in supported_regions 
            if self.usage_tracking[r] < self.regions[r]['quota_limit']
        ]
        
        if not available_regions:
            return None  # All quotas exhausted
        
        # Return region with most remaining quota
        return min(available_regions, 
                  key=lambda r: self.usage_tracking[r])
    
    def get_supported_regions(self, model):
        """Get regions that support the specified model."""
        
        model_regions = {
            'gemini-2.5-pro': ['us-central1', 'us-east1', 'europe-west1', 'asia-northeast1'],
            'gemini-2.5-flash': ['us-central1', 'us-east1', 'europe-west1', 'asia-northeast1'],
            'claude-opus-4': ['us-central1', 'us-east1', 'europe-west1'],
            'claude-sonnet-4': ['us-central1', 'us-east1', 'europe-west1']
        }
        
        return [r for r in model_regions.get(model, []) if r in self.regions]
    
    def generate_content(self, model, contents, **kwargs):
        """Generate content using optimal region selection."""
        
        region = self.select_optimal_region(model)
        if not region:
            raise exceptions.ResourceExhausted("All regional quotas exhausted")
        
        os.environ['GOOGLE_CLOUD_LOCATION'] = region
        client = genai.Client()
        
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                **kwargs
            )
            
            # Track usage
            self.usage_tracking[region] += 1
            return response, region
            
        except exceptions.ResourceExhausted:
            # Mark region as exhausted
            self.usage_tracking[region] = self.regions[region]['quota_limit']
            raise

# Usage example
quota_client = QuotaAwareClient({
    'us-central1': {'quota_limit': 1000},
    'europe-west1': {'quota_limit': 500},
    'asia-northeast1': {'quota_limit': 300}
})

response, used_region = quota_client.generate_content(
    "gemini-2.5-flash",
    "Quota-optimized request"
)
```

## Monitoring Regional Performance

### Performance Tracking
```python
import time
from collections import defaultdict
from google import genai
import os

class RegionalPerformanceMonitor:
    """Monitor performance across regions."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def benchmark_regions(self, regions, model, test_prompts):
        """Benchmark performance across regions."""
        
        for region in regions:
            print(f"\nTesting region: {region}")
            os.environ['GOOGLE_CLOUD_LOCATION'] = region
            
            try:
                client = genai.Client()
                region_metrics = {
                    'latencies': [],
                    'success_rate': 0,
                    'total_requests': 0,
                    'successful_requests': 0
                }
                
                for prompt in test_prompts:
                    start_time = time.time()
                    region_metrics['total_requests'] += 1
                    
                    try:
                        response = client.models.generate_content(
                            model=model,
                            contents=prompt
                        )
                        
                        latency = time.time() - start_time
                        region_metrics['latencies'].append(latency)
                        region_metrics['successful_requests'] += 1
                        
                        print(f"  ✓ Prompt {len(region_metrics['latencies'])}: {latency:.2f}s")
                        
                    except Exception as e:
                        print(f"  ✗ Prompt failed: {e}")
                
                # Calculate metrics
                if region_metrics['latencies']:
                    region_metrics['avg_latency'] = sum(region_metrics['latencies']) / len(region_metrics['latencies'])
                    region_metrics['min_latency'] = min(region_metrics['latencies'])
                    region_metrics['max_latency'] = max(region_metrics['latencies'])
                
                region_metrics['success_rate'] = (
                    region_metrics['successful_requests'] / region_metrics['total_requests']
                ) * 100
                
                self.metrics[region] = region_metrics
                
                print(f"  Results: {region_metrics['successful_requests']}/{region_metrics['total_requests']} successful")
                if region_metrics['latencies']:
                    print(f"  Avg latency: {region_metrics['avg_latency']:.2f}s")
                
            except Exception as e:
                print(f"  Region setup failed: {e}")
                self.metrics[region] = {'error': str(e)}
    
    def get_best_region(self, priority='latency'):
        """Get best performing region based on criteria."""
        
        valid_regions = {
            k: v for k, v in self.metrics.items() 
            if 'error' not in v and v.get('success_rate', 0) > 0
        }
        
        if not valid_regions:
            return None
        
        if priority == 'latency':
            return min(valid_regions.items(), 
                      key=lambda x: x[1].get('avg_latency', float('inf')))[0]
        elif priority == 'success_rate':
            return max(valid_regions.items(), 
                      key=lambda x: x[1].get('success_rate', 0))[0]
        elif priority == 'stability':
            # Prefer regions with low latency variance
            return min(valid_regions.items(), 
                      key=lambda x: max(x[1].get('latencies', [0])) - min(x[1].get('latencies', [0])))[0]
    
    def print_summary(self):
        """Print performance summary."""
        
        print("\n=== Regional Performance Summary ===")
        for region, metrics in self.metrics.items():
            if 'error' in metrics:
                print(f"{region}: ERROR - {metrics['error']}")
            else:
                print(f"{region}:")
                print(f"  Success Rate: {metrics.get('success_rate', 0):.1f}%")
                if metrics.get('avg_latency'):
                    print(f"  Avg Latency: {metrics['avg_latency']:.2f}s")
                    print(f"  Range: {metrics['min_latency']:.2f}s - {metrics['max_latency']:.2f}s")

# Usage example
monitor = RegionalPerformanceMonitor()

test_prompts = [
    "Explain photosynthesis in one sentence.",
    "What is the capital of France?",
    "Calculate 15 * 23.",
    "Write a haiku about technology."
]

regions_to_test = ['us-central1', 'us-east1', 'europe-west1', 'asia-northeast1']

monitor.benchmark_regions(regions_to_test, 'gemini-2.5-flash', test_prompts)
monitor.print_summary()

best_latency_region = monitor.get_best_region('latency')
print(f"\nBest region for latency: {best_latency_region}")
```

## Best Practices for Regional Deployment

### 1. Region Selection Criteria
- **Latency Requirements**: Choose closest geographic region
- **Data Residency**: Comply with local data protection laws
- **Model Availability**: Ensure target models are supported
- **Quota Limits**: Consider regional quota allocations

### 2. Fallback Strategies
- Implement multi-region failover
- Use global endpoints for non-sensitive data
- Monitor regional health and switch proactively

### 3. Performance Optimization
- Benchmark regions for your specific use cases
- Consider time zones for batch processing
- Use regional caching strategies

### 4. Compliance Considerations
- Map compliance requirements to appropriate regions
- Document data processing locations
- Implement proper audit logging

This comprehensive guide to regional availability provides all the information needed to make informed decisions about Vertex AI deployment across different geographic regions.