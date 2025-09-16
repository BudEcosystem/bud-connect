# Admin Frontend Deployment Guide

## Overview
The admin frontend is deployed as a separate service alongside the main BudConnect API. It's accessible at `https://budconnect.bud.studio/admin/`.

## Architecture
- **Frontend**: React app served by Nginx at `/admin` path
- **Backend**: BudConnect API at `/` path
- **Routing**: Traefik ingress handles path-based routing

## Building the Docker Image

### Local Build
```bash
cd admin
./build-and-push.sh
```

### Production Build
```bash
cd admin
# Build with specific tag
./build-and-push.sh v1.0.0

# Or manually
docker build -t budstudio/budconnect-admin:latest .
docker push budstudio/budconnect-admin:latest
```

## Deployment with Helm

### 1. Update values file (if needed)
Edit `deploy/helm/values.yaml`:
```yaml
admin:
  enabled: true
  image: "budstudio/budconnect-admin:latest"
  replicas: 1
```

### 2. Deploy with Helm
```bash
# From project root
cd deploy/helm

# Upgrade or install
helm upgrade --install budconnect . \
  --namespace bud-connect \
  --values values.yaml
```

### 3. Verify Deployment
```bash
# Check pods
kubectl get pods -n bud-connect

# Check services
kubectl get svc -n bud-connect

# Check ingress
kubectl get ingress -n bud-connect
```

## Local Development

### Running Admin Frontend Locally
```bash
cd admin
npm install
npm run dev
```

The app will be available at `http://localhost:3000`

### Environment Variables
Create `.env` file in admin directory:
```env
VITE_API_BASE_URL=http://localhost:9088  # For local backend
# Or
VITE_API_BASE_URL=https://budconnect.bud.studio  # For production backend
```

### Building for Production Locally
```bash
cd admin
VITE_BASE_PATH=/admin npm run build
```

## Troubleshooting

### Check Admin Pod Logs
```bash
kubectl logs -n bud-connect deployment/bud-connect-admin
```

### Access Admin Pod
```bash
kubectl exec -it -n bud-connect deployment/bud-connect-admin -- sh
```

### Test Nginx Configuration
```bash
# Inside the pod
nginx -t
```

### Common Issues

1. **404 on refresh**: This is handled by nginx config which serves index.html for all routes
2. **API calls failing**: Check that the backend service name in nginx.conf matches the actual service
3. **Assets not loading**: Ensure VITE_BASE_PATH is set correctly during build

## URLs

- **Production Admin**: https://budconnect.bud.studio/admin/
- **Production API**: https://budconnect.bud.studio/
- **Health Check**: https://budconnect.bud.studio/admin/health