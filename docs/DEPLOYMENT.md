# Verity Systems Deployment Guide

This guide covers deploying Verity Systems across various environments from local development to production Kubernetes clusters.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Cloud Platform Guides](#cloud-platform-guides)
6. [Environment Configuration](#environment-configuration)
7. [SSL/TLS Setup](#ssltls-setup)
8. [Monitoring Setup](#monitoring-setup)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | API server |
| Node.js | 18+ | Frontend build |
| Docker | 24+ | Containerization |
| kubectl | 1.28+ | Kubernetes CLI |
| Helm | 3.12+ | Kubernetes packages |
| Terraform | 1.5+ | Infrastructure as code |

### API Keys

Obtain free API keys from these providers:

| Provider | Sign Up URL | Free Tier |
|----------|-------------|-----------|
| Groq | https://console.groq.com | 30 RPM |
| Cloudflare AI | https://dash.cloudflare.com | 10K req/day |
| SambaNova | https://cloud.sambanova.ai | 10 RPM |
| NVIDIA NIM | https://build.nvidia.com | 1K req/month |
| Hugging Face | https://huggingface.co | Unlimited |

---

## Local Development

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/verity-systems/verity.git
cd verity-systems

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

**.env file:**
```bash
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=debug

# Redis (optional for local dev)
REDIS_URL=redis://localhost:6379/0

# AI Providers
GROQ_API_KEY=gsk_...
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_API_TOKEN=...
SAMBANOVA_API_KEY=...
NVIDIA_API_KEY=nvapi-...
HUGGINGFACE_TOKEN=hf_...

# Additional providers
TOGETHER_API_KEY=...
FIREWORKS_API_KEY=...
COHERE_API_KEY=...
```

### 3. Start Services

```bash
# Start Redis (optional, for caching)
docker run -d -p 6379:6379 redis:7-alpine

# Start API server
python python-tools/api_server_ultimate.py

# Or with hot reload
uvicorn python-tools.api_server_ultimate:app --reload --port 8000
```

### 4. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Test verification
curl -X POST http://localhost:8000/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "The Earth is round"}'
```

---

## Docker Deployment

### Single Container

```bash
# Build image
docker build -t verity-systems:latest .

# Run container
docker run -d \
  --name verity-api \
  -p 8000:8000 \
  --env-file .env \
  verity-systems:latest
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  redis-data:
  prometheus-data:
  grafana-data:
```

### Production Docker Compose

```bash
# Use production config
docker-compose -f docker-compose.production.yml up -d
```

---

## Kubernetes Deployment

### Prerequisites

```bash
# Ensure kubectl is configured
kubectl cluster-info

# Ensure Helm is installed
helm version
```

### Using Helm (Recommended)

```bash
# Add Verity Helm repository
helm repo add verity https://charts.verity.systems
helm repo update

# Install with default values
helm install verity verity/verity-systems

# Install with custom values
helm install verity verity/verity-systems \
  --namespace verity \
  --create-namespace \
  -f my-values.yaml

# Upgrade existing installation
helm upgrade verity verity/verity-systems -f my-values.yaml
```

**Custom values.yaml:**
```yaml
replicaCount: 3

image:
  repository: verity-systems/api
  tag: "1.5.0"

resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilization: 70

redis:
  enabled: true
  architecture: replication
  auth:
    enabled: true
    password: "your-redis-password"

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: api.verity.systems
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: verity-tls
      hosts:
        - api.verity.systems

secrets:
  groqApiKey: "gsk_..."
  cloudflareAccountId: "..."
  cloudflareApiToken: "..."
```

### Using kubectl

```bash
# Create namespace
kubectl create namespace verity

# Create secrets
kubectl create secret generic verity-api-keys \
  --namespace verity \
  --from-literal=GROQ_API_KEY=gsk_... \
  --from-literal=CLOUDFLARE_API_TOKEN=...

# Apply manifests
kubectl apply -f deploy/kubernetes/ -n verity

# Check status
kubectl get pods -n verity
kubectl get svc -n verity
kubectl get ingress -n verity
```

### Verify Deployment

```bash
# Port forward to test locally
kubectl port-forward svc/verity-api 8000:80 -n verity

# Test endpoint
curl http://localhost:8000/health

# View logs
kubectl logs -f deployment/verity-api -n verity

# Scale deployment
kubectl scale deployment verity-api --replicas=5 -n verity
```

---

## Cloud Platform Guides

### AWS (EKS)

#### 1. Create Infrastructure with Terraform

```bash
cd terraform/aws

# Initialize Terraform
terraform init

# Plan changes
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan
```

#### 2. Configure kubectl

```bash
aws eks update-kubeconfig --name verity-eks --region us-west-2
```

#### 3. Deploy Application

```bash
helm install verity ./helm/verity-systems \
  --namespace verity \
  --create-namespace \
  -f helm/values-aws.yaml
```

**values-aws.yaml:**
```yaml
redis:
  enabled: false  # Use ElastiCache

externalRedis:
  host: verity-redis.xxxxx.usw2.cache.amazonaws.com
  port: 6379
  tls: true

serviceAccount:
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/verity-api

ingress:
  className: alb
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:...
```

### Google Cloud (GKE)

#### 1. Create Cluster

```bash
gcloud container clusters create verity-gke \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10
```

#### 2. Deploy

```bash
helm install verity ./helm/verity-systems \
  --namespace verity \
  -f helm/values-gcp.yaml
```

### Azure (AKS)

#### 1. Create Cluster

```bash
az aks create \
  --resource-group verity-rg \
  --name verity-aks \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

az aks get-credentials --resource-group verity-rg --name verity-aks
```

#### 2. Deploy

```bash
helm install verity ./helm/verity-systems \
  --namespace verity \
  -f helm/values-azure.yaml
```

### DigitalOcean (DOKS)

```bash
# Create cluster via doctl or UI
doctl kubernetes cluster create verity-doks \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 3

# Deploy
helm install verity ./helm/verity-systems -f helm/values-do.yaml
```

### Railway (One-Click)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/verity)

### Render

1. Connect GitHub repository
2. Create new Web Service
3. Set environment variables
4. Deploy

### Vercel (Frontend Only)

```bash
# Deploy frontend
vercel --prod

# Or via configuration
# vercel.json is pre-configured
```

---

## Environment Configuration

### Required Variables

```bash
# Server
HOST=0.0.0.0
PORT=8000
ENV=production  # development, staging, production
LOG_LEVEL=info  # debug, info, warning, error

# Security
SECRET_KEY=your-256-bit-secret-key
JWT_SECRET=your-jwt-secret
ALLOWED_ORIGINS=https://verity.systems,https://app.verity.systems

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=optional-password
REDIS_TLS=false
```

### Provider API Keys

```bash
# AI Providers (at least one required)
GROQ_API_KEY=gsk_...
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_API_TOKEN=...
SAMBANOVA_API_KEY=...
NVIDIA_API_KEY=nvapi-...
HUGGINGFACE_TOKEN=hf_...
TOGETHER_API_KEY=...
FIREWORKS_API_KEY=...
COHERE_API_KEY=...

# Optional - Enhanced Capabilities
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...
```

### Feature Flags

```bash
# Features
ENABLE_CACHING=true
ENABLE_STREAMING=true
ENABLE_METRICS=true
ENABLE_RATE_LIMITING=true

# Limits
MAX_CLAIM_LENGTH=2000
MAX_BATCH_SIZE=10
DEFAULT_TIMEOUT=30
```

---

## SSL/TLS Setup

### Using cert-manager (Kubernetes)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@verity.systems
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF
```

### Using Cloudflare (Recommended)

1. Add domain to Cloudflare
2. Enable "Full (strict)" SSL mode
3. Create Origin Certificate
4. Apply to Kubernetes:

```bash
kubectl create secret tls verity-tls \
  --cert=origin.pem \
  --key=origin-key.pem \
  -n verity
```

---

## Monitoring Setup

### Prometheus

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'verity-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: /metrics
```

### Grafana Dashboards

Import pre-built dashboards:

1. Access Grafana at `http://localhost:3000`
2. Login (admin/admin)
3. Import dashboards from `monitoring/dashboards/`

### Alertmanager

```yaml
# monitoring/alertmanager.yml
global:
  slack_api_url: 'https://hooks.slack.com/services/...'

route:
  receiver: 'slack'

receivers:
  - name: 'slack'
    slack_configs:
      - channel: '#alerts'
        send_resolved: true
```

---

## Troubleshooting

### Common Issues

#### API Not Starting

```bash
# Check logs
docker logs verity-api
# or
kubectl logs deployment/verity-api -n verity

# Common causes:
# - Missing environment variables
# - Redis connection failed
# - Port already in use
```

#### Redis Connection Failed

```bash
# Test Redis connectivity
redis-cli -h localhost -p 6379 ping

# Check Redis logs
docker logs verity-redis
```

#### Provider Errors

```bash
# Check provider health
curl http://localhost:8000/v1/providers

# Verify API keys
curl -H "Authorization: Bearer $GROQ_API_KEY" \
  https://api.groq.com/openai/v1/models
```

#### High Latency

1. Check provider response times in Grafana
2. Verify Redis cache is working
3. Check network connectivity
4. Consider increasing replica count

#### Memory Issues

```bash
# Check memory usage
kubectl top pods -n verity

# Increase limits in values.yaml
resources:
  limits:
    memory: 4Gi
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug
export DEBUG=true

# Run with verbose output
python python-tools/api_server_ultimate.py --debug
```

### Getting Help

- **Documentation**: [docs.verity.systems](https://docs.verity.systems)
- **GitHub Issues**: [github.com/verity-systems/verity/issues](https://github.com/verity-systems/verity/issues)
- **Discord**: [discord.gg/verity](https://discord.gg/verity)
- **Email**: support@verity.systems

---

## Quick Reference

### Docker Commands

```bash
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose logs -f api    # View API logs
docker-compose restart api    # Restart API
docker-compose pull           # Update images
```

### Kubernetes Commands

```bash
kubectl get pods -n verity              # List pods
kubectl logs -f deploy/verity-api       # View logs
kubectl describe pod <pod-name>         # Debug pod
kubectl exec -it <pod-name> -- /bin/sh  # Shell access
kubectl rollout restart deploy/verity-api  # Restart
kubectl scale deploy/verity-api --replicas=5  # Scale
```

### Helm Commands

```bash
helm install verity ./helm/verity-systems  # Install
helm upgrade verity ./helm/verity-systems  # Upgrade
helm rollback verity 1                     # Rollback
helm uninstall verity                      # Uninstall
helm list                                  # List releases
```

---

*Last updated: January 2026*
