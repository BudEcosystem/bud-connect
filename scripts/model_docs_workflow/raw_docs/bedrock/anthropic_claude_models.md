# Anthropic Claude Models on AWS Bedrock

## Overview

Anthropic's Claude models are available on AWS Bedrock, providing access to advanced AI capabilities with enterprise-grade security and scalability. These models excel in reasoning, analysis, coding, and creative tasks while maintaining strong safety characteristics.

## Available Models

### Claude Opus 4
- **Model ID**: `anthropic.claude-opus-4-20250514-v1:0`
- **Type**: Most powerful model for advanced coding and complex reasoning
- **Context Window**: 200,000 tokens
- **Capabilities**:
  - Advanced coding and software development
  - Complex mathematical reasoning
  - Detailed analysis and research
  - Creative writing and content generation
  - Multi-step problem solving
- **Timeout**: 60 minutes for inference calls
- **Best For**: High-complexity tasks requiring maximum intelligence

### Claude 3.5 Sonnet
- **Model ID**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Type**: Balanced model with excellent performance across tasks
- **Context Window**: 200,000 tokens
- **Capabilities**:
  - Coding and software development
  - Creative writing and content creation
  - Visual data extraction and analysis
  - Agentic tasks and tool use
  - Document analysis and summarization
  - Computer use (beta) - can generate keystrokes and mouse clicks
- **Performance**: 80% cheaper than Opus while delivering superior intelligence and speed
- **Best For**: General-purpose applications requiring high intelligence

### Claude 3.5 Haiku
- **Model ID**: `anthropic.claude-3-5-haiku-20241022-v1:0`
- **Type**: Fast and cost-effective model
- **Context Window**: 200,000 tokens
- **Capabilities**:
  - Rapid response generation
  - Knowledge retrieval
  - Sales automation
  - Customer support
  - Content moderation
  - Data processing
- **Performance**: Optimized for speed and efficiency
- **Fine-tuning**: Available in US West (Oregon) region
- **Best For**: High-volume applications requiring quick responses

### Claude 3 Opus
- **Model ID**: `anthropic.claude-3-opus-20240229-v1:0`
- **Type**: Powerful model for complex tasks
- **Context Window**: 200,000 tokens
- **Capabilities**:
  - Complex reasoning and analysis
  - Advanced mathematical problem solving
  - Detailed research and writing
  - Code generation and debugging
- **Best For**: Tasks requiring deep reasoning and analysis

## AWS Bedrock-Specific Features

### Regional Availability

#### Claude Opus 4
- **US East (Ohio)**
- **US East (N. Virginia)**
- **US West (Oregon)**

#### Claude Sonnet 4
- **North America**: US East (Ohio, N. Virginia), US West (Oregon)
- **Asia Pacific**: Hyderabad, Mumbai, Osaka, Seoul, Singapore, Sydney, Tokyo
- **Europe**: Spain

#### Claude 3.5 Models
- Available in multiple AWS regions with expanding coverage
- Check AWS documentation for current regional availability

### Intelligent Prompt Routing
Amazon Bedrock can automatically route requests between Claude 3.5 Sonnet and Claude 3.5 Haiku based on prompt complexity, optimizing for both performance and cost.

### Latency-Optimized Inference
- Available for Claude 3.5 Haiku
- Delivers faster performance on AWS than any other cloud provider
- Ideal for real-time applications

## Pricing (US West - Oregon Region)

### On-Demand Pricing

#### Claude Opus 4
- **Input**: $15.00 per 1M tokens
- **Output**: $75.00 per 1M tokens

#### Claude 3.5 Sonnet
- **Input**: $3.00 per 1M tokens
- **Output**: $15.00 per 1M tokens

#### Claude 3.5 Haiku
- **Input**: $0.25 per 1M tokens
- **Output**: $1.25 per 1M tokens

#### Claude 3 Opus
- **Input**: $15.00 per 1M tokens
- **Output**: $75.00 per 1M tokens

### Cost Example
A request with 11K input tokens and 4K output tokens to Claude 3.5 Sonnet:
- Input cost: 11K tokens/1000 × $0.003 = $0.033
- Output cost: 4K tokens/1000 × $0.015 = $0.060
- **Total**: $0.093

### Provisioned Throughput
Available for high-volume, predictable workloads with guaranteed throughput and discounted pricing.

## API Usage with boto3

### Basic Text Generation Example

```python
import boto3
import json

# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name='us-west-2'
)

# Prepare the request using Messages API
model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"

body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": [
        {
            "role": "user",
            "content": "Explain quantum computing in simple terms."
        }
    ],
    "temperature": 0.7,
    "top_p": 0.9
})

# Invoke the model
response = bedrock_runtime.invoke_model(
    modelId=model_id,
    body=body
)

# Parse the response
response_body = json.loads(response['body'].read())
generated_text = response_body['content'][0]['text']
print(generated_text)
```

### Streaming Response Example

```python
import boto3
import json

bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name='us-west-2'
)

model_id = "anthropic.claude-3-5-haiku-20241022-v1:0"

body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": [
        {
            "role": "user",
            "content": "Write a Python function to calculate the fibonacci sequence."
        }
    ]
})

# Streaming invoke
response = bedrock_runtime.invoke_model_with_response_stream(
    modelId=model_id,
    body=body
)

# Process streaming response
stream = response.get('body')
if stream:
    for event in stream:
        chunk = event.get('chunk')
        if chunk:
            chunk_data = json.loads(chunk.get('bytes').decode())
            if 'delta' in chunk_data and 'text' in chunk_data['delta']:
                print(chunk_data['delta']['text'], end='')
```

### Multi-turn Conversation Example

```python
import boto3
import json

bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name='us-west-2'
)

model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"

# Multi-turn conversation
conversation = [
    {
        "role": "user",
        "content": "What are the main principles of object-oriented programming?"
    },
    {
        "role": "assistant",
        "content": "The main principles of object-oriented programming are: 1) Encapsulation, 2) Inheritance, 3) Polymorphism, and 4) Abstraction."
    },
    {
        "role": "user",
        "content": "Can you explain encapsulation with a Python example?"
    }
]

body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": conversation
})

response = bedrock_runtime.invoke_model(
    modelId=model_id,
    body=body
)

response_body = json.loads(response['body'].read())
print(response_body['content'][0]['text'])
```

### Tool Use Example

```python
import boto3
import json

bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name='us-west-2'
)

model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"

# Define tools
tools = [
    {
        "name": "calculator",
        "description": "A simple calculator that can perform basic arithmetic operations",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"]
                },
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["operation", "a", "b"]
        }
    }
]

body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "tools": tools,
    "messages": [
        {
            "role": "user",
            "content": "What is 15 multiplied by 23?"
        }
    ]
})

response = bedrock_runtime.invoke_model(
    modelId=model_id,
    body=body
)

response_body = json.loads(response['body'].read())
print(json.dumps(response_body, indent=2))
```

## Use Cases on AWS

### Software Development
- **Code Generation**: Create functions, classes, and complete applications
- **Code Review**: Analyze code for bugs, security issues, and optimization opportunities
- **Documentation**: Generate comprehensive code documentation and API references
- **Debugging**: Identify and fix complex programming issues

### Content Creation
- **Writing Assistance**: Blog posts, articles, marketing copy
- **Creative Writing**: Stories, scripts, poetry
- **Technical Documentation**: User manuals, tutorials, guides
- **Translation**: Multi-language content adaptation

### Data Analysis
- **Document Processing**: Extract insights from reports, contracts, and research papers
- **Visual Analysis**: Analyze charts, graphs, and images (Claude 3.5 models)
- **Research**: Comprehensive analysis of complex topics
- **Summarization**: Condense lengthy documents into key points

### Business Automation
- **Customer Support**: Intelligent chatbots and support systems
- **Sales Automation**: Lead qualification and customer engagement
- **Process Automation**: Workflow optimization and task automation
- **Decision Support**: Analysis and recommendations for business decisions

### Agentic Applications
- **Computer Use** (Claude 3.5 Sonnet): Automate computer tasks through UI interaction
- **Tool Integration**: Connect with APIs and external systems
- **Multi-step Workflows**: Complex task orchestration
- **Autonomous Agents**: Self-directed problem solving

## Comparison with Direct Provider APIs

### Advantages of Bedrock Integration
1. **Enterprise Security**: Built-in AWS security, compliance, and governance
2. **Unified Platform**: Single API for multiple AI providers
3. **Scalability**: Automatic scaling without infrastructure management
4. **Cost Management**: Integrated billing and usage tracking
5. **Monitoring**: Native CloudWatch integration and logging
6. **Compliance**: SOC, HIPAA, and other enterprise compliance certifications

### Considerations
1. **Feature Availability**: Some features may be available later than direct API
2. **Latency**: Additional network hop compared to direct Anthropic API
3. **Model Updates**: Updates follow AWS release schedule
4. **Custom Features**: Limited to AWS-supported capabilities

## Fine-tuning Capabilities

### Claude 3.5 Haiku Fine-tuning
- **Availability**: US West (Oregon) region
- **Unique Feature**: Only fully managed service offering Claude fine-tuning
- **Use Cases**: Domain-specific adaptation, style customization, task specialization
- **Data Requirements**: Custom dataset formatting and preparation

### Fine-tuning Process
1. **Data Preparation**: Format training data according to specifications
2. **Model Training**: Automated training process with hyperparameter optimization
3. **Evaluation**: Built-in model evaluation and performance metrics
4. **Deployment**: Direct deployment to Bedrock endpoints

## Security and Compliance

### Data Handling
- **Data Residency**: Data processed within selected AWS regions
- **Encryption**: In-transit and at-rest encryption
- **Audit Trails**: Complete request/response logging via CloudTrail
- **Access Control**: Fine-grained IAM policies and permissions

### Compliance Certifications
- SOC 1, 2, and 3
- HIPAA compliance
- PCI DSS Level 1
- ISO 27001, 27017, 27018
- FedRAMP Moderate

## Monitoring and Observability

### CloudWatch Metrics
- Request volume and error rates
- Latency percentiles (p50, p95, p99)
- Token usage and billing metrics
- Model performance indicators

### Logging and Debugging
- Request/response logging
- Error tracking and analysis
- Performance monitoring
- Usage analytics and reporting

## Best Practices

### Model Selection
1. **Claude Opus 4**: For most complex coding and reasoning tasks
2. **Claude 3.5 Sonnet**: For balanced performance across general tasks
3. **Claude 3.5 Haiku**: For high-volume, fast-response applications
4. **Claude 3 Opus**: For complex analysis when Opus 4 is not needed

### Performance Optimization
1. **Context Management**: Keep conversations within token limits
2. **Prompt Engineering**: Clear, specific prompts for better results
3. **Streaming**: Use streaming for long responses to improve user experience
4. **Caching**: Implement response caching for repeated queries

### Cost Optimization
1. **Model Tiering**: Use appropriate model for task complexity
2. **Prompt Optimization**: Minimize unnecessary tokens in prompts
3. **Batching**: Group similar requests when possible
4. **Monitoring**: Track usage patterns and optimize accordingly

## Integration Examples

### With Amazon Bedrock Knowledge Bases
```python
# Example of using Claude with Knowledge Base
knowledge_base_id = "your-kb-id"
model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"

# Query knowledge base and use Claude for response generation
response = bedrock_agent_runtime.retrieve_and_generate(
    input={
        'text': 'What are the key findings in the research papers?'
    },
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': knowledge_base_id,
            'modelArn': f'arn:aws:bedrock:us-west-2::foundation-model/{model_id}'
        }
    }
)
```

### With Amazon Bedrock Agents
```python
# Example of using Claude in Bedrock Agents
agent_configuration = {
    'agentName': 'claude-powered-agent',
    'foundationModel': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    'instruction': 'You are a helpful assistant that can access tools and knowledge bases.',
    'agentResourceRoleArn': 'arn:aws:iam::account:role/agent-role'
}

# Create agent with Claude model
response = bedrock_agent.create_agent(**agent_configuration)
```

## Support and Documentation

### Official Resources
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Anthropic Claude Parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html)
- [Claude Messages API](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html)
- [AWS Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/)

### Community Resources
- AWS AI/ML blog posts
- Anthropic model documentation
- Developer community forums
- Sample applications and code repositories

## Migration from Direct Anthropic API

### Key Differences
1. **Authentication**: AWS IAM instead of Anthropic API keys
2. **Endpoints**: AWS Bedrock endpoints instead of Anthropic endpoints
3. **Request Format**: Bedrock-specific request formatting
4. **Response Handling**: AWS SDK response patterns

### Migration Checklist
1. Update authentication mechanism
2. Modify endpoint configurations
3. Adjust request/response handling
4. Update error handling logic
5. Implement AWS-specific monitoring
6. Test thoroughly in non-production environment