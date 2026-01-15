# Verity Systems

<div align="center">

![Verity Systems](https://img.shields.io/badge/Verity-Systems-6366f1?style=for-the-badge&logo=checkmarx&logoColor=white)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?style=flat-square&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)

[![CI Status](https://github.com/-q/actions/workflows/ci.yml/badge.svg)](https://github.com/seetsele/vrsystems/actions/workflows/ci.yml) <!-- Replace <owner>/<repo> if needed -->

**?? Enterprise AI-Powered Fact-Checking Platform**

*Verify claims with 20+ AI providers, fact-checkers, and data sources in real-time*

[Live Demo](https://verity.systems) � [API Docs](docs/API.md) � [Quick Start](#-quick-start) � [SDKs](#-sdks) � [Deploy](#-deployment)

</div>

---

## ?? Overview

Verity Systems is a comprehensive, production-ready fact-checking platform that aggregates verification results from 20+ providers including AI models, news sources, academic databases, government data, and international fact-checkers. It uses advanced fusion algorithms to synthesize multiple sources into accurate, well-cited verdicts.

## ? Features

### Core Capabilities
- **?? 20+ providers** - Groq, Cloudflare AI, SambaNova, NVIDIA NIM, OpenAI, Anthropic, and more
- **? Real-Time Verification** - Fast verification with parallel processing
- **?? Streaming Results** - Server-Sent Events for real-time progressive updates
- **?? Fusion Algorithm** - Multi-stage evidence synthesis with confidence calibration
- **?? Smart Scoring** - Bayesian confidence with source credibility weighting
- **??? Distributed Caching** - Redis-based semantic similarity caching
- **?? Full Observability** - Prometheus metrics, Grafana dashboards, alerting

### Integration Options
- **?? REST API** - Full-featured JSON API with OpenAPI documentation
- **?? WebSocket** - Real-time bidirectional communication
- **?? SSE Streaming** - Progressive result streaming
- **?? Python SDK** - Async/sync client with full typing
- **?? Node.js SDK** - TypeScript client with streaming support
- **?? Browser Extension** - Chrome/Firefox/Edge extension
- **?? Chat Bots** - Slack and Discord integrations

### Enterprise Features
- **?? Security** - AES-256-GCM encryption, JWT auth, HMAC signing
- **?? Rate Limiting** - Sliding window with burst allowance
- **?? Circuit Breakers** - Automatic failover and recovery
- **?? Multi-tenancy** - Organization and team management
- **?? Audit Logging** - Tamper-evident hash chains

## ?? Quick Start

### Option 1: Local Development

```bash
# Clone repository
git clone https://github.com/verity-systems/verity.git
cd verity-systems

# Setup Python environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (many providers have free tiers!)

# Run API server
python python-tools/api_server_ultimate.py
```

### Option 2: Docker

```bash
# Quick start with Docker Compose
docker-compose up -d

# Or build and run manually
docker build -t verity-systems .
docker run -p 8000:8000 --env-file .env verity-systems
```

### Option 3: Kubernetes

```bash
# Using Helm
helm repo add verity https://charts.verity.systems
helm install verity verity/verity-systems -f values.yaml

# Or kubectl
kubectl apply -f deploy/kubernetes/
```

## ?? Provider Categories

### ?? AI/LLM Providers (Free Tier)
| Provider | Models | Free Limits |
|----------|--------|-------------|
| **Groq** | Llama 3.1 70B/8B, Mixtral | 30 RPM, 6K TPM |
| **Cloudflare AI** | Llama, Mistral, BERT | 10K req/day |
| **SambaNova** | Llama 3.1 405B | 10 RPM |
| **NVIDIA NIM** | Llama 3.1, Mixtral | 1K req/month |
| **Together AI** | Llama 3.1, Mistral | $5 credits |
| **Fireworks** | Llama 3.1, Mixtral | $1 credits |
| **Cohere** | Command-R | 100 req/min |
| **Hugging Face** | NLI Models | Unlimited |

### ?? News & Fact-Check APIs
| Provider | Coverage | Free Limits |
|----------|----------|-------------|
| **Google Fact Check** | Global fact-checks | 10K/day |
| **MediaWiki** | Wikipedia/Wikidata | Unlimited |
| **Semantic Scholar** | 200M+ papers | 100/5min |
| **OpenAlex** | 250M+ works | Unlimited |
| **CrossRef** | DOI metadata | 50/sec |
| **DuckDuckGo** | Web search | Unlimited |
| **Brave Search** | Web search | 2K/month |

### ?? Academic Sources
| Provider | Content | Access |
|----------|---------|--------|
| **arXiv** | 2M+ papers | Free |
| **PubMed** | Medical research | Free |
| **CORE** | 300M+ papers | Free |
| **Internet Archive** | Historical data | Free |
| **Open Library** | Books | Free |

### ??? Government & Official Data
| Provider | Data Type | Access |
|----------|-----------|--------|
| **FRED** | Economic data | Free |
| **World Bank** | Global indicators | Free |
| **data.gov** | US government | Free |
| **EU Open Data** | EU statistics | Free |
| **CDC** | Health data | Free |
| **NASA** | Space/Earth data | Free |

### ?? International Fact-Checkers
| Organization | Region | Language |
|--------------|--------|----------|
| **Africa Check** | Africa | EN/FR |
| **Full Fact** | UK | EN |
| **Snopes** | US | EN |
| **PolitiFact** | US | EN |
| **FactCheck.org** | US | EN |
| **AFP Fact Check** | Global | Multi |

## ?? Security

- **AES-256-GCM** encryption with PBKDF2 key derivation (600K iterations)
- **JWT authentication** with refresh tokens
- **HMAC request signing** for integrity verification
- **PII anonymization** for GDPR compliance
- **Audit logging** with tamper-evident hash chains
- **Rate limiting** with sliding window algorithm

## ? SDKs

### Python SDK
```bash
pip install verity-sdk
```

```python
from verity import VerityClient, AsyncVerityClient

# Synchronous usage
client = VerityClient(api_key="your-api-key")
result = client.verify("The Earth is 4.5 billion years old")
print(f"Verdict: {result.verdict} ({result.confidence}%)")

# Async usage
async with AsyncVerityClient(api_key="your-api-key") as client:
    result = await client.verify("Climate change is real")
    print(result.summary)

# Streaming
for event in client.verify_stream("Vaccines are safe"):
    print(f"[{event.provider}] {event.verdict}")
```

### Node.js/TypeScript SDK
```bash
npm install @verity-systems/sdk
```

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({ apiKey: 'your-api-key' });

// Simple verification
const result = await client.verify('The moon landing was real');
console.log(`Verdict: ${result.verdict} (${result.confidence}%)`);

// Streaming
for await (const event of client.verifyStream('COVID vaccines work')) {
  console.log(`[${event.provider}] ${event.verdict}`);
}
```

## ?? API Usage

### REST API
```bash
# Verify a claim
curl -X POST https://api.verity.systems/v1/verify \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"claim": "The Earth is round", "providers": ["groq", "wikipedia"]}'

# Batch verification
curl -X POST https://api.verity.systems/v1/verify/batch \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"claims": ["Claim 1", "Claim 2", "Claim 3"]}'

# Stream results (SSE)
curl -N https://api.verity.systems/v1/verify/stream \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"claim": "Vaccines are effective"}'
```

### Response Format
```json
{
  "id": "ver_abc123",
  "claim": "The Earth is approximately 4.5 billion years old",
  "verdict": "TRUE",
  "confidence": 95.2,
  "summary": "Scientific consensus strongly supports this claim...",
  "evidence": [
    {
      "provider": "groq",
      "verdict": "TRUE",
      "confidence": 94,
      "explanation": "Radiometric dating confirms...",
      "sources": ["Nature", "Science"]
    }
  ],
  "metadata": {
    "processing_time_ms": 1243,
    "providers_used": 5,
    "cache_hit": false
  }
}
```

## ?? GitHub Education Benefits

This project is optimized for GitHub Education Pack:

| Service | Benefit | Value |
|---------|---------|-------|
| Anthropic | API credits | $25/month |
| Microsoft Azure | Cloud credits | $100 |
| DigitalOcean | Platform credits | $200 |
| MongoDB Atlas | Database | $50 + cert |
| Heroku | Hosting | $312 (2 years) |
| JetBrains | IDEs | Free |

## ? Integrations

### Browser Extension
Available for Chrome, Firefox, and Edge. Highlight text on any webpage and verify claims instantly.

```bash
# Build extension
cd browser-extension
npm install && npm run build
# Load unpacked extension from dist/ folder
```

### Slack Bot
Add to your Slack workspace for team fact-checking:
```
/verify The claim you want to check
```

### Discord Bot
Add to your Discord server:
```
!verify The claim you want to check
```

## ?? Deployment

### Docker Compose (Recommended for Dev)
```bash
docker-compose up -d
# Includes: API, Redis, Prometheus, Grafana
```

### Kubernetes (Production)
```bash
# Using Helm
helm install verity ./helm/verity-systems \
  --set api.replicas=3 \
  --set redis.enabled=true \
  --set monitoring.enabled=true

# Using kubectl
kubectl apply -f deploy/kubernetes/
```

### Cloud Platforms
- **AWS**: EKS deployment with Terraform (see `terraform/aws/`)
- **GCP**: GKE deployment with Cloud Build
- **Azure**: AKS deployment with ARM templates
- **Vercel**: Frontend deployment
- **Railway/Render**: One-click deploy

## ?? Project Structure

```
verity-systems/
+-- python-tools/               # Backend
�   +-- api_server_ultimate.py  # Main FastAPI server
�   +-- verity_master_orchestrator_v2.py  # Core orchestration
�   +-- verity_fusion_engine.py # Fusion algorithms
�   +-- verity_redis_cache.py   # Distributed caching
�   +-- verity_metrics.py       # Prometheus metrics
�   +-- free_providers_*.py     # Provider implementations
�   +-- requirements.txt
+-- public/                     # Frontend
�   +-- index.html             # Landing page
�   +-- verify.html            # Verification UI
�   +-- dashboard.html         # Analytics dashboard
�   +-- assets/
+-- browser-extension/          # Chrome/Firefox extension
+-- slack-bot/                  # Slack integration
+-- discord-bot/                # Discord integration
+-- sdk/
�   +-- python/                # Python SDK
�   +-- nodejs/                # Node.js SDK
+-- tests/                      # Test suite
+-- deploy/
�   +-- kubernetes/            # K8s manifests
�   +-- aws-cloudformation.yaml
+-- helm/                       # Helm charts
+-- terraform/                  # Infrastructure as code
+-- monitoring/                 # Prometheus/Grafana configs
+-- docker-compose.yml
+-- Dockerfile
```

## ?? Monitoring & Observability

- **Prometheus**: Metrics collection at `/metrics`
- **Grafana**: Pre-built dashboards for API, providers, cache

## Grafana & Prometheus (Local setup)

You can run a local monitoring stack that scrapes the Verity metrics and imports the starter dashboard.

1) Start Prometheus + Grafana (from the repository):

   - cd docker/prometheus
   - docker-compose up -d

2) Open Grafana: http://localhost:3000 (default admin/admin)

3) The Prometheus data source is pre-configured (provisioning). The provider dashboard is mounted and will be automatically imported on Grafana startup via the provisioning files.

   - If automatic import doesn't occur, manually import `public/grafana_provider_dashboard.json` from the Grafana UI (Dashboards → Import).

4) What to monitor:

   - verity_provider_failures{provider="<name>"}
   - verity_provider_in_cooldown{provider="<name>"}
   - verity_cache_hits / verity_cache_misses

Notes:
- The provisioning files are located under `docker/prometheus/provisioning` and the dashboard JSON file is at `public/grafana_provider_dashboard.json`.
- For production deployments, secure Grafana and restrict provisioning access.

- **Alertmanager**: Configurable alerts for SLA breaches
- **Structured Logging**: JSON logs with correlation IDs

## ?? Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=python-tools --cov-report=html

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

## ?? Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ?? License

MIT License - see [LICENSE](LICENSE) for details.

## ?? Acknowledgments

- All the amazing free-tier API providers
- The open-source fact-checking community
- Contributors and testers

---

<div align="center">

**Built with ?? for fighting misinformation**

[Website](https://verity.systems) � [Documentation](https://docs.verity.systems) � [API Status](https://status.verity.systems)

</div>
