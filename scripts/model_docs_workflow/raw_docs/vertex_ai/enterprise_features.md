# Vertex AI Enterprise Features: VPC-SC, CMEK, and Advanced Security

## Overview

Google Cloud Vertex AI provides comprehensive enterprise-grade security and governance features that distinguish it from consumer AI services. These features enable organizations to deploy AI models while maintaining strict security, compliance, and data governance requirements.

## VPC Service Controls (VPC-SC)

### What is VPC-SC?

VPC Service Controls creates a security perimeter around Google Cloud resources, preventing data exfiltration and controlling API access from specific networks. For Vertex AI, this means AI model interactions can be restricted to approved networks and monitored for compliance.

### VPC-SC with Vertex AI

#### Supported Features
- **Data Boundary Protection**: Prevents AI model responses from leaving your security perimeter
- **Network-Level Access Control**: Restricts API access to specific networks
- **Audit Logging**: Comprehensive logs of all access attempts and data flows
- **Cross-Project Protection**: Secures data flows between different Google Cloud projects

#### Limitations with Vertex AI Agent Engine
- Vertex AI Agent Engine does not support VPC-SC, CMEK, or AXT security controls
- Standard Vertex AI model endpoints fully support all enterprise features

### Setting Up VPC-SC for Vertex AI

#### 1. Create Service Perimeter
```bash
# Create a VPC-SC perimeter
gcloud access-context-manager perimeters create vertex-ai-perimeter \
    --policy=POLICY_ID \
    --title="Vertex AI Security Perimeter" \
    --description="VPC-SC perimeter for Vertex AI workloads" \
    --perimeter-type=regular \
    --restricted-services=aiplatform.googleapis.com,storage.googleapis.com
```

#### 2. Configure Ingress Rules
```yaml
# ingress-rule.yaml
name: projects/PROJECT_NUMBER/locations/global/servicePerimeters/vertex-ai-perimeter
title: "Vertex AI Security Perimeter"
status:
  restrictedServices:
    - "aiplatform.googleapis.com"
    - "storage.googleapis.com"
    - "artifactregistry.googleapis.com"
  ingressPolicies:
    - ingressFrom:
        sources:
          - resource: "projects/PROJECT_NUMBER"
        identities:
          - "serviceAccount:service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
      ingressTo:
        resources:
          - "projects/PROJECT_NUMBER"
        operations:
          - serviceName: "storage.googleapis.com"
          - serviceName: "artifactregistry.googleapis.com"
```

#### 3. Apply Perimeter Configuration
```bash
# Apply the perimeter configuration
gcloud access-context-manager perimeters update vertex-ai-perimeter \
    --policy=POLICY_ID \
    --perimeter-config-file=ingress-rule.yaml
```

### VPC-SC Code Implementation

#### Python Client with VPC-SC
```python
import os
from google import genai
from google.auth import default

def setup_vpc_sc_client():
    """Setup Vertex AI client for VPC-SC environment."""
    
    # Ensure project is within VPC-SC perimeter
    credentials, project = default()
    
    # VPC-SC requires specific project and network configuration
    os.environ['GOOGLE_CLOUD_PROJECT'] = project
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
    os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'
    
    # Client automatically respects VPC-SC boundaries
    client = genai.Client()
    
    return client

def secure_ai_request(prompt, model="gemini-2.5-flash"):
    """Make AI request within VPC-SC perimeter."""
    
    try:
        client = setup_vpc_sc_client()
        
        # This request stays within the security perimeter
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        
        # Response data cannot leave the perimeter
        return response.text
        
    except Exception as e:
        # VPC-SC violations will appear as API errors
        if "VPC Service Controls" in str(e):
            print(f"VPC-SC violation detected: {e}")
            raise
        else:
            print(f"Other error: {e}")
            raise

# Usage within VPC-SC perimeter
try:
    result = secure_ai_request("Analyze this sensitive data...")
    print("✓ Request processed within security perimeter")
except Exception as e:
    print(f"✗ Security perimeter violation: {e}")
```

### VPC-SC Monitoring and Alerts
```python
from google.cloud import monitoring_v3
from google.cloud import logging

def setup_vpc_sc_monitoring(project_id):
    """Set up monitoring for VPC-SC violations."""
    
    # Create log-based metric for VPC-SC violations
    logging_client = logging.Client(project=project_id)
    
    metric_filter = '''
    protoPayload.serviceName="aiplatform.googleapis.com"
    AND protoPayload.authenticationInfo.principalEmail!=""
    AND protoPayload.requestMetadata.vpcServiceControlsBlockedByVpcServiceControls=true
    '''
    
    metric = logging_client.metric(
        name="vpc_sc_violations",
        filter_=metric_filter,
        description="VPC Service Controls violations for Vertex AI"
    )
    
    if not metric.exists():
        metric.create()
    
    # Create alerting policy
    monitoring_client = monitoring_v3.AlertPolicyServiceClient()
    project_name = f"projects/{project_id}"
    
    alert_policy = monitoring_v3.AlertPolicy(
        display_name="VPC-SC Violations - Vertex AI",
        conditions=[
            monitoring_v3.AlertPolicy.Condition(
                display_name="VPC-SC Violation Rate",
                condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                    filter=f'resource.type="global" AND metric.type="logging.googleapis.com/user/vpc_sc_violations"',
                    comparison=monitoring_v3.ComparisonType.GREATER_THAN,
                    threshold_value=0,
                    duration={"seconds": 60}
                )
            )
        ],
        enabled=True
    )
    
    created_policy = monitoring_client.create_alert_policy(
        name=project_name,
        alert_policy=alert_policy
    )
    
    print(f"✓ VPC-SC monitoring configured: {created_policy.name}")

# Setup monitoring
setup_vpc_sc_monitoring('your-project-id')
```

## Customer-Managed Encryption Keys (CMEK)

### What is CMEK?

CMEK allows you to control the cryptographic keys used to encrypt your data in Google Cloud services. With Vertex AI, this means you can encrypt model inputs, outputs, and stored data using your own encryption keys managed through Google Cloud KMS.

### CMEK with Vertex AI

#### Supported Components
- **Model Training Data**: Custom training data encrypted with your keys
- **Model Artifacts**: Trained model files encrypted with CMEK
- **Batch Prediction Data**: Input and output data for batch predictions
- **Feature Store Data**: Feature engineering data storage

#### CMEK Coverage Areas
```python
# Areas where CMEK applies in Vertex AI
cmek_coverage = {
    "training_data": "Customer training datasets",
    "model_artifacts": "Stored ML models", 
    "prediction_data": "Batch prediction inputs/outputs",
    "feature_store": "Feature engineering data",
    "custom_training": "Custom training job data",
    "pipeline_data": "ML pipeline intermediate data"
}
```

### Setting Up CMEK for Vertex AI

#### 1. Create KMS Key Ring and Key
```bash
# Create key ring
gcloud kms keyrings create vertex-ai-keyring \
    --location=us-central1

# Create encryption key
gcloud kms keys create vertex-ai-key \
    --location=us-central1 \
    --keyring=vertex-ai-keyring \
    --purpose=encryption
```

#### 2. Grant Vertex AI Access to Key
```bash
# Get Vertex AI service account
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format="value(projectNumber)")
VERTEX_AI_SA="service-${PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com"

# Grant encrypt/decrypt permissions
gcloud kms keys add-iam-policy-binding vertex-ai-key \
    --location=us-central1 \
    --keyring=vertex-ai-keyring \
    --member=serviceAccount:${VERTEX_AI_SA} \
    --role=roles/cloudkms.cryptoKeyEncrypterDecrypter
```

#### 3. Configure Vertex AI with CMEK
```python
from google.cloud import aiplatform
import os

def setup_cmek_vertex_ai():
    """Configure Vertex AI with Customer-Managed Encryption Keys."""
    
    # Initialize with CMEK configuration
    aiplatform.init(
        project="your-project-id",
        location="us-central1",
        encryption_spec_key_name="projects/your-project-id/locations/us-central1/keyRings/vertex-ai-keyring/cryptoKeys/vertex-ai-key"
    )
    
    return aiplatform

def create_cmek_dataset(display_name, data_source):
    """Create dataset with CMEK encryption."""
    
    kms_key = "projects/your-project-id/locations/us-central1/keyRings/vertex-ai-keyring/cryptoKeys/vertex-ai-key"
    
    dataset = aiplatform.TextDataset.create(
        display_name=display_name,
        gcs_source=data_source,
        encryption_spec_key_name=kms_key
    )
    
    return dataset

def run_cmek_training_job(dataset, model_display_name):
    """Run training job with CMEK encryption."""
    
    kms_key = "projects/your-project-id/locations/us-central1/keyRings/vertex-ai-keyring/cryptoKeys/vertex-ai-key"
    
    job = aiplatform.AutoMLTextTrainingJob(
        display_name=f"{model_display_name}-training",
        prediction_type="classification",
        encryption_spec_key_name=kms_key
    )
    
    model = job.run(
        dataset=dataset,
        model_display_name=model_display_name,
        training_encryption_spec_key_name=kms_key,
        model_encryption_spec_key_name=kms_key
    )
    
    return model

# Usage
setup_cmek_vertex_ai()

# Create encrypted dataset
encrypted_dataset = create_cmek_dataset(
    "secure-training-data",
    "gs://your-bucket/training-data.csv"
)

# Train model with CMEK
encrypted_model = run_cmek_training_job(
    encrypted_dataset, 
    "secure-model"
)
```

### CMEK Key Rotation
```python
from google.cloud import kms
import time

def rotate_cmek_key(project_id, location, keyring, key_name):
    """Rotate CMEK key for enhanced security."""
    
    client = kms.KeyManagementServiceClient()
    
    # Get current key path
    key_path = client.crypto_key_path(project_id, location, keyring, key_name)
    
    # Create new key version (rotation)
    response = client.create_crypto_key_version(
        request={
            "parent": key_path,
            "crypto_key_version": {}
        }
    )
    
    print(f"✓ New key version created: {response.name}")
    
    # Wait for key to be ready
    while response.state != kms.CryptoKeyVersion.CryptoKeyVersionState.ENABLED:
        time.sleep(10)
        response = client.get_crypto_key_version(name=response.name)
        print(f"Key state: {response.state}")
    
    print("✓ Key rotation completed")
    return response

# Rotate key annually
rotate_cmek_key(
    "your-project-id",
    "us-central1", 
    "vertex-ai-keyring",
    "vertex-ai-key"
)
```

### CMEK Compliance Monitoring
```python
from google.cloud import asset_v1
from google.cloud import logging

def audit_cmek_compliance(project_id):
    """Audit CMEK compliance across Vertex AI resources."""
    
    client = asset_v1.AssetServiceClient()
    parent = f"projects/{project_id}"
    
    # Query all Vertex AI resources
    asset_types = [
        "aiplatform.googleapis.com/Dataset",
        "aiplatform.googleapis.com/Model", 
        "aiplatform.googleapis.com/TrainingPipeline"
    ]
    
    compliance_report = {
        "compliant_resources": [],
        "non_compliant_resources": [],
        "total_resources": 0
    }
    
    for asset_type in asset_types:
        # Search for assets of this type
        response = client.search_all_resources(
            request={
                "scope": parent,
                "asset_types": [asset_type]
            }
        )
        
        for resource in response:
            compliance_report["total_resources"] += 1
            
            # Check if resource has CMEK encryption
            has_cmek = False
            if hasattr(resource, 'additional_attributes'):
                encryption_spec = resource.additional_attributes.get('encryptionSpec')
                if encryption_spec and 'kmsKeyName' in encryption_spec:
                    has_cmek = True
                    compliance_report["compliant_resources"].append(resource.name)
            
            if not has_cmek:
                compliance_report["non_compliant_resources"].append(resource.name)
    
    # Log compliance status
    logging_client = logging.Client()
    logger = logging_client.logger("cmek-compliance")
    
    compliance_percentage = (
        len(compliance_report["compliant_resources"]) / 
        compliance_report["total_resources"] * 100
        if compliance_report["total_resources"] > 0 else 0
    )
    
    logger.log_struct({
        "message": "CMEK Compliance Audit",
        "compliance_percentage": compliance_percentage,
        "total_resources": compliance_report["total_resources"],
        "compliant_count": len(compliance_report["compliant_resources"]),
        "non_compliant_count": len(compliance_report["non_compliant_resources"])
    })
    
    return compliance_report

# Run compliance audit
compliance_status = audit_cmek_compliance('your-project-id')
print(f"CMEK Compliance: {len(compliance_status['compliant_resources'])}/{compliance_status['total_resources']} resources")
```

## Access Transparency (AXT)

### What is Access Transparency?

Access Transparency provides near real-time logs that record actions Google personnel take when accessing your content. For Vertex AI, this means you can see when Google support engineers access your AI model data for troubleshooting or maintenance.

### AXT with Vertex AI

#### Coverage Areas
- **Support Access**: When Google support accesses your AI models or data
- **Maintenance Activities**: Scheduled maintenance affecting your resources
- **Security Investigations**: Access during security incident response
- **Service Operations**: Operational access for service reliability

### Enabling AXT for Vertex AI
```bash
# Enable Access Transparency for your organization
gcloud organizations add-iam-policy-binding ORGANIZATION_ID \
    --member=serviceAccount:your-admin@your-domain.com \
    --role=roles/accesstransparency.admin

# Configure AXT logging
gcloud logging sinks create axt-vertex-ai-sink \
    bigquery.googleapis.com/projects/your-project-id/datasets/axt_logs \
    --log-filter='protoPayload.serviceName="aiplatform.googleapis.com" AND protoPayload."@type"="type.googleapis.com/google.cloud.audit.AuditLog"'
```

### AXT Monitoring Implementation
```python
from google.cloud import bigquery
from google.cloud import monitoring_v3
import json

def monitor_axt_access(project_id):
    """Monitor Access Transparency logs for Vertex AI."""
    
    client = bigquery.Client(project=project_id)
    
    # Query AXT logs for Vertex AI access
    query = """
    SELECT
        timestamp,
        protoPayload.authenticationInfo.principalEmail as accessor,
        protoPayload.serviceName as service,
        protoPayload.methodName as method,
        protoPayload.requestMetadata.reason as access_reason,
        resource.labels.project_id as project
    FROM `{project_id}.axt_logs.cloudaudit_googleapis_com_access_transparency`
    WHERE protoPayload.serviceName = "aiplatform.googleapis.com"
    AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
    ORDER BY timestamp DESC
    """.format(project_id=project_id)
    
    results = client.query(query)
    
    access_events = []
    for row in results:
        event = {
            "timestamp": row.timestamp.isoformat(),
            "accessor": row.accessor,
            "service": row.service,
            "method": row.method,
            "reason": row.access_reason,
            "project": row.project
        }
        access_events.append(event)
    
    # Alert on unexpected access
    if access_events:
        print(f"⚠️  {len(access_events)} Google access events detected in last 24h")
        for event in access_events:
            print(f"  {event['timestamp']}: {event['accessor']} - {event['reason']}")
    else:
        print("✓ No Google access to Vertex AI resources in last 24h")
    
    return access_events

def setup_axt_alerting(project_id):
    """Set up alerting for Access Transparency events."""
    
    monitoring_client = monitoring_v3.AlertPolicyServiceClient()
    project_name = f"projects/{project_id}"
    
    # Create alert policy for AXT events
    alert_policy = monitoring_v3.AlertPolicy(
        display_name="Access Transparency - Vertex AI Access",
        conditions=[
            monitoring_v3.AlertPolicy.Condition(
                display_name="Google Personnel Access",
                condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                    filter='resource.type="global" AND log_name="projects/{}/logs/cloudaudit.googleapis.com%2Faccess_transparency"'.format(project_id),
                    comparison=monitoring_v3.ComparisonType.GREATER_THAN,
                    threshold_value=0,
                    duration={"seconds": 300}
                )
            )
        ],
        notification_channels=[],  # Add your notification channels
        enabled=True
    )
    
    created_policy = monitoring_client.create_alert_policy(
        name=project_name,
        alert_policy=alert_policy
    )
    
    print(f"✓ AXT alerting configured: {created_policy.name}")

# Monitor AXT events
axt_events = monitor_axt_access('your-project-id')
setup_axt_alerting('your-project-id')
```

## Data Residency Controls

### Regional Data Processing
```python
import os
from google import genai

def enforce_data_residency(region, model, content):
    """Enforce data residency by region."""
    
    # Validate region for compliance
    compliant_regions = {
        'eu': ['europe-west1', 'europe-west3', 'europe-west4'],
        'us': ['us-central1', 'us-east1', 'us-west1'],
        'asia': ['asia-northeast1', 'asia-southeast1', 'asia-south1']
    }
    
    region_type = None
    for region_group, regions in compliant_regions.items():
        if region in regions:
            region_type = region_group
            break
    
    if not region_type:
        raise ValueError(f"Region {region} not supported for data residency")
    
    # Configure client for specific region
    os.environ['GOOGLE_CLOUD_LOCATION'] = region
    client = genai.Client()
    
    # Process data in specified region only
    response = client.models.generate_content(
        model=model,
        contents=content
    )
    
    # Log data processing location for audit
    print(f"✓ Data processed in {region} ({region_type} compliance)")
    
    return response.text, region

# Usage with data residency enforcement
gdpr_response, processed_region = enforce_data_residency(
    'europe-west1',  # GDPR-compliant region
    'gemini-2.5-flash',
    'Process this EU citizen data...'
)

print(f"GDPR-compliant processing completed in {processed_region}")
```

### Data Residency Audit Trail
```python
from google.cloud import logging
import json
from datetime import datetime

class DataResidencyAuditor:
    """Audit data processing locations for compliance."""
    
    def __init__(self, project_id):
        self.project_id = project_id
        self.logging_client = logging.Client(project=project_id)
        self.logger = self.logging_client.logger("data-residency-audit")
    
    def log_processing_event(self, region, data_type, compliance_regime):
        """Log data processing event for audit trail."""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "processing_region": region,
            "data_type": data_type,
            "compliance_regime": compliance_regime,
            "service": "vertex-ai",
            "project": self.project_id
        }
        
        self.logger.log_struct(audit_entry, severity="INFO")
        return audit_entry
    
    def validate_compliance(self, region, required_compliance):
        """Validate region meets compliance requirements."""
        
        compliance_mappings = {
            'gdpr': ['europe-west1', 'europe-west3', 'europe-west4'],
            'us_government': ['us-central1', 'us-east1'],
            'apac_local': ['asia-northeast1', 'asia-southeast1', 'asia-south1']
        }
        
        allowed_regions = compliance_mappings.get(required_compliance, [])
        is_compliant = region in allowed_regions
        
        self.log_processing_event(region, "ai_model_inference", required_compliance)
        
        return is_compliant
    
    def generate_compliance_report(self, start_date, end_date):
        """Generate compliance report for audit period."""
        
        # Query audit logs
        filter_str = f'''
        jsonPayload.service="vertex-ai"
        AND timestamp>="{start_date}"
        AND timestamp<="{end_date}"
        '''
        
        entries = self.logging_client.list_entries(filter_=filter_str)
        
        compliance_summary = {}
        for entry in entries:
            if hasattr(entry, 'json_payload'):
                region = entry.json_payload.get('processing_region')
                compliance = entry.json_payload.get('compliance_regime')
                
                key = f"{compliance}_{region}"
                compliance_summary[key] = compliance_summary.get(key, 0) + 1
        
        return compliance_summary

# Usage
auditor = DataResidencyAuditor('your-project-id')

# Validate compliance before processing
is_compliant = auditor.validate_compliance('europe-west1', 'gdpr')
if is_compliant:
    print("✓ Region compliant with GDPR requirements")
else:
    print("✗ Region not compliant with GDPR requirements")

# Generate monthly compliance report
from datetime import datetime, timedelta
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=30)

report = auditor.generate_compliance_report(
    start_date.isoformat(),
    end_date.isoformat()
)
print(f"Compliance report: {report}")
```

## Integration with Enterprise IAM

### Fine-Grained Access Control
```python
from google.cloud import iam
from google.cloud import resourcemanager

def setup_vertex_ai_iam():
    """Set up fine-grained IAM for Vertex AI resources."""
    
    # Define custom roles for Vertex AI
    custom_roles = {
        "vertex_ai_model_user": {
            "title": "Vertex AI Model User",
            "description": "Can use AI models but not manage them",
            "permissions": [
                "aiplatform.endpoints.predict",
                "aiplatform.models.get",
                "aiplatform.models.list"
            ]
        },
        "vertex_ai_data_scientist": {
            "title": "Vertex AI Data Scientist", 
            "description": "Can create and manage ML experiments",
            "permissions": [
                "aiplatform.datasets.create",
                "aiplatform.datasets.get",
                "aiplatform.datasets.list",
                "aiplatform.trainingPipelines.create",
                "aiplatform.models.upload"
            ]
        },
        "vertex_ai_security_admin": {
            "title": "Vertex AI Security Administrator",
            "description": "Can manage security settings and encryption",
            "permissions": [
                "aiplatform.*.get",
                "aiplatform.*.list", 
                "cloudkms.cryptoKeys.get",
                "cloudkms.cryptoKeys.list"
            ]
        }
    }
    
    return custom_roles

def assign_conditional_access(project_id, user_email, role, condition):
    """Assign conditional IAM access to Vertex AI resources."""
    
    client = resourcemanager.ProjectsClient()
    
    # Get current IAM policy
    policy = client.get_iam_policy(
        request={"resource": f"projects/{project_id}"}
    )
    
    # Add conditional binding
    binding = {
        "role": role,
        "members": [f"user:{user_email}"],
        "condition": {
            "title": condition["title"],
            "description": condition["description"], 
            "expression": condition["expression"]
        }
    }
    
    policy.bindings.append(binding)
    
    # Apply updated policy
    client.set_iam_policy(
        request={
            "resource": f"projects/{project_id}",
            "policy": policy
        }
    )
    
    print(f"✓ Conditional access granted to {user_email}")

# Example: Time-based access
time_condition = {
    "title": "Business Hours Access",
    "description": "Access only during business hours",
    "expression": 'request.time.getHours() >= 9 && request.time.getHours() <= 17'
}

assign_conditional_access(
    "your-project-id",
    "datascientist@company.com",
    "roles/aiplatform.user",
    time_condition
)

# Example: Location-based access
location_condition = {
    "title": "Corporate Network Access",
    "description": "Access only from corporate IP ranges",
    "expression": 'inIpRange(origin.ip, "203.0.113.0/24") || inIpRange(origin.ip, "198.51.100.0/24")'
}

assign_conditional_access(
    "your-project-id", 
    "analyst@company.com",
    "roles/aiplatform.user",
    location_condition
)
```

### Workload Identity Integration
```python
from google.cloud import container_v1

def setup_workload_identity_for_vertex_ai(project_id, cluster_name, zone):
    """Configure Workload Identity for secure Vertex AI access from GKE."""
    
    # Create Kubernetes service account
    k8s_service_account = {
        "apiVersion": "v1",
        "kind": "ServiceAccount", 
        "metadata": {
            "name": "vertex-ai-workload",
            "namespace": "default",
            "annotations": {
                "iam.gke.io/gcp-service-account": f"vertex-ai-workload@{project_id}.iam.gserviceaccount.com"
            }
        }
    }
    
    # Create Google service account
    iam_client = iam.IAMCredentialsServiceClient()
    
    service_account = {
        "account_id": "vertex-ai-workload",
        "service_account": {
            "display_name": "Vertex AI Workload Identity",
            "description": "Service account for Vertex AI access via Workload Identity"
        }
    }
    
    # Bind identities
    workload_identity_binding = {
        "bindings": [
            {
                "role": "roles/iam.workloadIdentityUser",
                "members": [
                    f"serviceAccount:{project_id}.svc.id.goog[default/vertex-ai-workload]"
                ]
            }
        ]
    }
    
    print("✓ Workload Identity configured for secure Vertex AI access")
    
    return {
        "k8s_service_account": k8s_service_account,
        "gcp_service_account": service_account,
        "workload_identity_binding": workload_identity_binding
    }

# Configure Workload Identity
workload_config = setup_workload_identity_for_vertex_ai(
    "your-project-id",
    "your-gke-cluster", 
    "us-central1-a"
)
```

## Compliance and Audit Framework

### Comprehensive Audit Implementation
```python
from google.cloud import audit
from google.cloud import storage
import csv
from datetime import datetime, timedelta

class VertexAIComplianceAuditor:
    """Comprehensive compliance auditing for Vertex AI."""
    
    def __init__(self, project_id, audit_bucket):
        self.project_id = project_id
        self.audit_bucket = audit_bucket
        self.storage_client = storage.Client()
        self.logging_client = logging.Client()
    
    def generate_security_audit_report(self, days_back=30):
        """Generate comprehensive security audit report."""
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)
        
        audit_data = {
            "vpc_sc_events": self._audit_vpc_sc_events(start_time, end_time),
            "cmek_compliance": self._audit_cmek_compliance(),
            "access_patterns": self._audit_access_patterns(start_time, end_time),
            "data_residency": self._audit_data_residency(start_time, end_time),
            "iam_changes": self._audit_iam_changes(start_time, end_time)
        }
        
        # Generate report
        report = self._format_audit_report(audit_data, start_time, end_time)
        
        # Store in audit bucket
        self._store_audit_report(report, end_time)
        
        return report
    
    def _audit_vpc_sc_events(self, start_time, end_time):
        """Audit VPC Service Controls events."""
        
        filter_str = f'''
        protoPayload.serviceName="aiplatform.googleapis.com"
        AND protoPayload.requestMetadata.vpcServiceControlsBlockedByVpcServiceControls=true
        AND timestamp>="{start_time.isoformat()}"
        AND timestamp<="{end_time.isoformat()}"
        '''
        
        entries = list(self.logging_client.list_entries(filter_=filter_str))
        
        return {
            "violation_count": len(entries),
            "violations": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "resource": entry.resource.labels.get("resource_name", "unknown"),
                    "principal": entry.proto_payload.authentication_info.principal_email
                }
                for entry in entries
            ]
        }
    
    def _audit_cmek_compliance(self):
        """Audit CMEK compliance across resources."""
        
        # Implementation would check all Vertex AI resources for CMEK encryption
        # This is a simplified version
        
        return {
            "total_resources": 100,  # Example numbers
            "cmek_encrypted": 95,
            "compliance_percentage": 95.0,
            "non_compliant_resources": [
                "projects/project/locations/us-central1/datasets/dataset1"
            ]
        }
    
    def _audit_access_patterns(self, start_time, end_time):
        """Audit access patterns for anomaly detection."""
        
        filter_str = f'''
        protoPayload.serviceName="aiplatform.googleapis.com"
        AND timestamp>="{start_time.isoformat()}"
        AND timestamp<="{end_time.isoformat()}"
        '''
        
        entries = list(self.logging_client.list_entries(filter_=filter_str))
        
        access_by_user = {}
        for entry in entries:
            user = entry.proto_payload.authentication_info.principal_email
            access_by_user[user] = access_by_user.get(user, 0) + 1
        
        # Detect anomalies (users with unusually high access)
        avg_access = sum(access_by_user.values()) / len(access_by_user) if access_by_user else 0
        anomalous_users = {
            user: count for user, count in access_by_user.items()
            if count > avg_access * 3  # 3x average is anomalous
        }
        
        return {
            "total_access_events": len(entries),
            "unique_users": len(access_by_user),
            "average_access_per_user": avg_access,
            "anomalous_users": anomalous_users
        }
    
    def _audit_data_residency(self, start_time, end_time):
        """Audit data residency compliance."""
        
        # Query custom data residency logs
        filter_str = f'''
        jsonPayload.service="vertex-ai"
        AND jsonPayload.compliance_regime!=null
        AND timestamp>="{start_time.isoformat()}"
        AND timestamp<="{end_time.isoformat()}"
        '''
        
        entries = list(self.logging_client.list_entries(filter_=filter_str))
        
        compliance_by_region = {}
        for entry in entries:
            if hasattr(entry, 'json_payload'):
                region = entry.json_payload.get('processing_region')
                compliance = entry.json_payload.get('compliance_regime')
                key = f"{compliance}_{region}"
                compliance_by_region[key] = compliance_by_region.get(key, 0) + 1
        
        return {
            "total_processing_events": len(entries),
            "compliance_breakdown": compliance_by_region
        }
    
    def _audit_iam_changes(self, start_time, end_time):
        """Audit IAM policy changes."""
        
        filter_str = f'''
        protoPayload.serviceName="cloudresourcemanager.googleapis.com"
        AND protoPayload.methodName="SetIamPolicy"
        AND timestamp>="{start_time.isoformat()}"
        AND timestamp<="{end_time.isoformat()}"
        '''
        
        entries = list(self.logging_client.list_entries(filter_=filter_str))
        
        return {
            "iam_changes": len(entries),
            "changes": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "principal": entry.proto_payload.authentication_info.principal_email,
                    "resource": entry.resource.labels.get("project_id", "unknown")
                }
                for entry in entries
            ]
        }
    
    def _format_audit_report(self, audit_data, start_time, end_time):
        """Format audit data into comprehensive report."""
        
        report = f"""
# Vertex AI Security Audit Report
**Period**: {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}
**Generated**: {datetime.utcnow().isoformat()}

## Executive Summary
- VPC-SC Violations: {audit_data['vpc_sc_events']['violation_count']}
- CMEK Compliance: {audit_data['cmek_compliance']['compliance_percentage']:.1f}%
- Total Access Events: {audit_data['access_patterns']['total_access_events']}
- Anomalous Users: {len(audit_data['access_patterns']['anomalous_users'])}

## VPC Service Controls
- Violations Detected: {audit_data['vpc_sc_events']['violation_count']}
- Action Required: {"Yes" if audit_data['vpc_sc_events']['violation_count'] > 0 else "No"}

## CMEK Compliance
- Total Resources: {audit_data['cmek_compliance']['total_resources']}
- CMEK Encrypted: {audit_data['cmek_compliance']['cmek_encrypted']}
- Compliance Rate: {audit_data['cmek_compliance']['compliance_percentage']:.1f}%

## Access Patterns
- Unique Users: {audit_data['access_patterns']['unique_users']}
- Average Access per User: {audit_data['access_patterns']['average_access_per_user']:.1f}
- Anomalous Activity: {len(audit_data['access_patterns']['anomalous_users'])} users flagged

## Data Residency
- Processing Events: {audit_data['data_residency']['total_processing_events']}
- Compliance Breakdown: {audit_data['data_residency']['compliance_breakdown']}

## IAM Changes
- Policy Changes: {audit_data['iam_changes']['iam_changes']}

## Recommendations
{"- Investigate VPC-SC violations immediately" if audit_data['vpc_sc_events']['violation_count'] > 0 else "- VPC-SC operating normally"}
{"- Address CMEK non-compliance for " + str(len(audit_data['cmek_compliance']['non_compliant_resources'])) + " resources" if audit_data['cmek_compliance']['compliance_percentage'] < 100 else "- CMEK compliance excellent"}
{"- Review anomalous user access patterns" if audit_data['access_patterns']['anomalous_users'] else "- Access patterns normal"}
"""
        
        return report
    
    def _store_audit_report(self, report, timestamp):
        """Store audit report in secure bucket."""
        
        bucket = self.storage_client.bucket(self.audit_bucket)
        filename = f"vertex-ai-audit-{timestamp.strftime('%Y%m%d-%H%M%S')}.md"
        blob = bucket.blob(f"audit-reports/{filename}")
        
        blob.upload_from_string(report)
        print(f"✓ Audit report stored: gs://{self.audit_bucket}/audit-reports/{filename}")

# Usage
auditor = VertexAIComplianceAuditor(
    project_id="your-project-id",
    audit_bucket="your-audit-bucket"
)

# Generate monthly audit report
report = auditor.generate_security_audit_report(days_back=30)
print("✓ Security audit completed")
```

This comprehensive enterprise features guide covers all the major security and compliance capabilities available in Vertex AI, providing practical implementation examples and best practices for enterprise deployments.