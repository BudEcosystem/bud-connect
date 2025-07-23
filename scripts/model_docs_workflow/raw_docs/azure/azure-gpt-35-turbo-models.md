# Azure OpenAI GPT-3.5 Turbo Models

## Model Overview

Azure OpenAI's GPT-3.5 Turbo models are cost-effective, fast language models optimized for chat and traditional completion tasks. These models provide a balance between performance and cost, making them suitable for a wide range of applications.

## Available Models

### azure/gpt-35-turbo
- **Model Name**: gpt-35-turbo (Note: Azure uses hyphens instead of dots)
- **Context Window**: 4,096 tokens
- **Description**: The most capable and cost-effective model in the GPT-3.5 family
- **Optimization**: Optimized for chat and works well for traditional completions tasks

### azure/gpt-35-turbo-16k
- **Model Name**: gpt-35-turbo-16k
- **Context Window**: 16,384 tokens
- **Description**: Extended context version of GPT-3.5 Turbo for longer conversations and documents
- **Use Cases**: Ideal for applications requiring longer context understanding

## Azure-Specific Deployment Process

### 1. Resource Creation
```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
  --name "your-openai-resource" \
  --resource-group "your-resource-group" \
  --kind "OpenAI" \
  --sku "S0" \
  --location "eastus"
```

### 2. Model Deployment
- Navigate to Azure AI Foundry portal
- Select your Azure OpenAI resource
- Go to "Deployments" section
- Click "Create new deployment"
- Choose "gpt-35-turbo" from the model dropdown
- Select appropriate version (latest stable recommended)
- Assign deployment name (used in API calls)
- Configure TPM (Tokens Per Minute) allocation

### 3. Deployment Naming Conventions
- **Deployment Name**: Custom name you assign (e.g., "gpt35-chat-deployment")
- **Model Name**: Always "gpt-35-turbo" or "gpt-35-turbo-16k"
- **API Reference**: Use deployment name in API endpoints, not model name

## Regional Availability

### Current Regions (2025)
- **Primary Regions**: East US, West Europe, South Central US
- **Extended Regions**: Canada East, Japan East, Australia East
- **New Additions**: Sweden Central, Switzerland North, West US 3
- **Data Zones**: US and EU data zones available for compliance requirements

### Regional Deployment Benefits
- Data residency compliance
- Lower latency for regional users
- Isolated processing within geographic boundaries
- 28 regions available for standard deployments

## Pricing Structure

### Pay-as-You-Go (Standard Deployment)
- **Input Tokens**: $0.0015 per 1K tokens
- **Output Tokens**: $0.002 per 1K tokens
- **Billing**: Per-token usage, no minimum commitment

### Provisioned Throughput Units (PTU)
- **Hourly Rate**: $X per PTU per hour (check Azure Pricing Calculator)
- **Minimum Allocation**: Varies by model and region
- **Increments**: 1 PTU increments available
- **Reservations**: Monthly and annual reservations available with significant discounts

### Global Batch Processing
- **Discount**: Up to 50% less than Global Standard pricing
- **Processing Time**: Responses within 24 hours
- **Use Case**: Large-scale, non-urgent processing tasks

## API Differences and Authentication

### Endpoint Structure
```
POST https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME/chat/completions?api-version=2024-06-01
```

### Key Differences from OpenAI
1. **Model Name**: Use "gpt-35-turbo" instead of "gpt-3.5-turbo"
2. **Endpoint**: Azure-specific endpoint format
3. **API Version**: Required query parameter
4. **Deployment Name**: Use custom deployment name, not model name

### Authentication Methods

#### 1. API Key Authentication
```python
import openai

openai.api_type = "azure"
openai.api_base = "https://YOUR_RESOURCE_NAME.openai.azure.com/"
openai.api_version = "2024-06-01"
openai.api_key = "YOUR_API_KEY"

response = openai.ChatCompletion.create(
    engine="YOUR_DEPLOYMENT_NAME",  # Not model name
    messages=[{"role": "user", "content": "Hello!"}]
)
```

#### 2. Microsoft Entra ID (Recommended)
```python
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

credential = DefaultAzureCredential()
client = AzureOpenAI(
    azure_endpoint="https://YOUR_RESOURCE_NAME.openai.azure.com/",
    azure_ad_token_provider=credential.get_token,
    api_version="2024-06-01"
)
```

## Quotas and Rate Limits

### Token Limits
- **TPM (Tokens Per Minute)**: Configurable per deployment
- **RPM (Requests Per Minute)**: Defined per region and subscription
- **Quota Assignment**: Assigned during deployment creation
- **Modification**: TPM can be modified in increments of 1,000

### Regional Quotas
- **Subscription Level**: Maximum 30 Azure OpenAI resources per region
- **Model Deployments**: No limit on number of deployments per model
- **Cross-Region**: Higher total quota possible across multiple regions

### Enterprise Quotas
- **Separate Batch Quota**: Global batch has independent token quota
- **No Tenant Limits**: Quotas enforced at subscription level
- **Dynamic Allocation**: PTU-based quota is model-independent

## Enterprise Features

### Security and Compliance
- **Private Networking**: VNet integration and private endpoints
- **Data Residency**: Regional and data zone deployments
- **Content Filtering**: Responsible AI content filtering built-in
- **Encryption**: Data encrypted at rest and in transit

### Integration Capabilities
- **Azure Integration**: Native integration with Azure services
- **SDK Support**: Official SDKs for Python, C#, JavaScript, Java, Go
- **Power Platform**: Integration with Power Virtual Agents
- **REST API**: Full REST API support

### Monitoring and Management
- **Azure Monitor**: Built-in monitoring and alerting
- **Cost Management**: Detailed usage and cost tracking
- **Quota Management**: Real-time quota monitoring and adjustment
- **SLA**: 99% latency SLA for token generation

## Best Practices

### Deployment Strategy
1. **Start Regional**: Begin with regional deployment for data residency
2. **Scale Globally**: Move to global deployment for higher availability
3. **Use PTU for Predictable Workloads**: Switch to PTU for consistent usage
4. **Monitor Quotas**: Regular quota usage monitoring

### Cost Optimization
1. **Choose Right Model**: Use gpt-35-turbo for cost-sensitive applications
2. **Batch Processing**: Use global batch for large-scale processing
3. **Reservations**: Purchase PTU reservations for long-term usage
4. **Regional Selection**: Consider regional pricing differences

### Security Best Practices
1. **Use Entra ID**: Prefer Microsoft Entra ID over API keys
2. **Store Keys Securely**: Use Azure Key Vault for API keys
3. **Network Security**: Implement private endpoints for sensitive workloads
4. **Monitor Access**: Enable audit logging and monitoring

## Migration from OpenAI

### Key Changes Required
1. **Endpoint Update**: Change to Azure OpenAI endpoint
2. **Model Name**: Update to "gpt-35-turbo" format
3. **Authentication**: Implement Azure authentication
4. **API Version**: Add required API version parameter
5. **Deployment Reference**: Use deployment name instead of model name

### Code Migration Example
```python
# Before (OpenAI)
import openai
openai.api_key = "sk-..."
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

# After (Azure OpenAI)
from openai import AzureOpenAI
client = AzureOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-azure-key",
    api_version="2024-06-01"
)
response = client.chat.completions.create(
    model="your-deployment-name",  # Your deployment name
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Troubleshooting

### Common Issues
1. **Deployment Name vs Model Name**: Always use deployment name in API calls
2. **API Version**: Ensure you're using a supported API version
3. **Regional Availability**: Check model availability in your target region
4. **Quota Limits**: Verify sufficient TPM quota before scaling

### Error Codes
- **429**: Rate limit exceeded - increase TPM or implement backoff
- **401**: Authentication failed - verify API key or Entra ID setup
- **404**: Deployment not found - check deployment name and region
- **400**: Invalid request - verify API version and request format