# LocalStack & Comet ML Integration Guide

## Overview

This guide explains how to integrate and use **LocalStack** (AWS services locally) and **Comet ML** (ML experiment tracking) with Verity Systems.

**✅ Status: Fully Implemented and Tested**

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install comet-ml boto3 moto

# 2. Run integration tests
cd python-tools
python test_integrations.py

# 3. (Optional) Set Comet API key for cloud tracking
# Get key at: https://www.comet.com/
set COMET_API_KEY=your-api-key
```

---

## 🏗️ AWS Services (Two Modes)

### Mode 1: Moto Mocks (No Docker Required) ✅ RECOMMENDED

This mode uses Python's `moto` library to mock AWS services in-memory. Perfect for development and testing without Docker.

```bash
# Enable in .env
USE_AWS_MOCKS=true
USE_LOCALSTACK=false
```

**Advantages:**
- No Docker required
- Instant startup
- No external dependencies
- Works everywhere Python runs

### Mode 2: LocalStack (Docker)

Use actual LocalStack containers for more realistic AWS simulation.

```bash
# Enable in .env
USE_AWS_MOCKS=false
USE_LOCALSTACK=true
AWS_ENDPOINT_URL=http://localhost:4566

# Start LocalStack
docker compose up -d localstack redis
```

### Using in Python

```python
from aws_local import VerityAWSService

# Initialize (auto-detects LocalStack vs real AWS)
aws = VerityAWSService()

# Store a verification result
await aws.s3.store_verification_result("claim-123", {
    "verdict": "TRUE",
    "confidence": 95,
    "providers_used": ["anthropic", "groq"]
})

# Cache a verification
await aws.dynamodb.cache_verification("The Earth is round", result)

# Queue for batch processing
message_id = await aws.sqs.queue_verification(
    "Climate change is real",
    priority="high"
)
```

### Environment Variables

```bash
# .env file
USE_LOCALSTACK=true                    # Use LocalStack for development
AWS_ENDPOINT_URL=http://localhost:4566 # LocalStack endpoint
AWS_REGION=us-east-1                   # Default region

# For production, switch to real AWS
USE_LOCALSTACK=false
AWS_ACCESS_KEY_ID=your-real-key
AWS_SECRET_ACCESS_KEY=your-real-secret
```

### LocalStack Pro (GitHub Education)

If you have GitHub Education, you can get LocalStack Pro credits for advanced features:

1. Visit https://localstack.cloud/
2. Sign up with your GitHub Education account
3. Get your auth token
4. Add to `.env`:
   ```bash
   LOCALSTACK_AUTH_TOKEN=your-pro-token
   ```

Pro features include:
- Persistence across restarts
- IAM simulation
- Cognito
- More Lambda runtimes

---

## 🔬 Comet ML Integration

Comet ML tracks your AI model experiments, provider performance, and verification accuracy.

### Setup

1. **Get API Key**
   - Sign up at https://www.comet.com/
   - GitHub Education users get enhanced free tier
   - Copy your API key from Settings → API Keys

2. **Configure Environment**
   ```bash
   # .env file
   COMET_API_KEY=your-api-key
   COMET_PROJECT_NAME=verity-fact-checking
   COMET_WORKSPACE=verity-systems
   ```

3. **Install Package**
   ```bash
   pip install comet-ml
   ```

### Basic Usage

```python
from comet_integration import (
    configure_comet,
    get_metrics_tracker,
    track_verification,
    track_provider_call
)

# Initialize Comet
configure_comet(experiment_name="verification-run-001")

# Get tracker
tracker = get_metrics_tracker()

# Log a verification
tracker.log_verification(
    claim="The Earth is round",
    verdict="TRUE",
    confidence=98.5,
    providers_used=["anthropic", "groq", "wikipedia"],
    response_time_ms=250.5,
    metadata={"source": "api", "user_tier": "premium"}
)

# Log provider performance
tracker.log_provider_performance(
    provider="anthropic",
    response_time_ms=150.0,
    success=True
)

# Finalize when done
tracker.finalize()
```

### Decorator Pattern

Use decorators for automatic tracking:

```python
from comet_integration import track_verification, track_provider_call

@track_verification
async def verify_claim(claim: str) -> dict:
    # Your verification logic
    return {"verdict": "TRUE", "confidence": 95}

@track_provider_call("anthropic")
async def call_anthropic(prompt: str) -> str:
    # Call Anthropic API
    return response
```

### Model Comparison

Compare different AI provider configurations:

```python
from comet_integration import ModelComparison

comparison = ModelComparison("provider-accuracy-test")

# Test different configs
comparison.log_config_result(
    config_name="anthropic-only",
    accuracy=92.5,
    avg_confidence=88.0,
    avg_response_time_ms=180.0,
    total_cost_usd=0.50
)

comparison.log_config_result(
    config_name="multi-provider",
    accuracy=96.8,
    avg_confidence=94.0,
    avg_response_time_ms=350.0,
    total_cost_usd=1.20
)

# Get best performing config
best = comparison.get_best_config('accuracy')
print(f"Best config: {best}")

comparison.log_comparison_summary()
```

### FastAPI Integration

```python
from fastapi import FastAPI
from comet_integration import register_comet_with_fastapi

app = FastAPI()
register_comet_with_fastapi(app)
```

### View Results

Visit https://www.comet.com/ to:
- View experiment dashboards
- Compare verification runs
- Analyze provider performance
- Track accuracy over time
- Create custom visualizations

---

## 🔧 Complete Integration Example

Here's how to use both LocalStack and Comet ML together:

```python
import asyncio
from aws_local import VerityAWSService
from comet_integration import (
    configure_comet,
    get_metrics_tracker,
    comet_experiment_context
)

async def run_verification_batch():
    # Initialize services
    aws = VerityAWSService()
    
    # Use Comet experiment context
    with comet_experiment_context("batch-verification-001") as experiment:
        tracker = get_metrics_tracker()
        
        claims = [
            "The Earth is round",
            "Water boils at 100°C at sea level",
            "Humans have 206 bones"
        ]
        
        for claim in claims:
            # Check cache first
            cached = await aws.dynamodb.get_cached_verification(claim)
            
            if cached:
                print(f"Cache hit: {claim[:30]}...")
                continue
            
            # Perform verification (your logic here)
            result = {
                "verdict": "TRUE",
                "confidence": 95.0,
                "providers_used": ["anthropic", "groq"]
            }
            
            # Log to Comet
            tracker.log_verification(
                claim=claim,
                verdict=result["verdict"],
                confidence=result["confidence"],
                providers_used=result["providers_used"],
                response_time_ms=250.0
            )
            
            # Cache result
            await aws.dynamodb.cache_verification(claim, result)
            
            # Store to S3
            claim_id = hashlib.sha256(claim.encode()).hexdigest()[:16]
            await aws.s3.store_verification_result(claim_id, result)
        
        tracker.finalize()

asyncio.run(run_verification_batch())
```

---

## 📁 File Structure

```
verity-systems/
├── docker-compose.yml              # LocalStack + Redis config
├── python-tools/
│   ├── aws_local.py                # LocalStack Python clients
│   ├── comet_integration.py        # Comet ML tracking
│   ├── integrations.py             # All integrations (updated)
│   └── localstack-init/
│       └── init-aws.sh             # LocalStack initialization
└── .env                            # Environment variables
```

---

## 🚀 Quick Start

```bash
# 1. Add environment variables
cp .env.example .env
# Edit .env with your API keys

# 2. Start LocalStack
docker-compose up -d localstack redis

# 3. Verify LocalStack is running
curl http://localhost:4566/_localstack/health

# 4. Install Python dependencies
pip install -r python-tools/requirements.txt

# 5. Test the integrations
python python-tools/aws_local.py
python python-tools/comet_integration.py

# 6. Start the API server
uvicorn python-tools.api_server:app --reload
```

---

## 🔑 API Keys Required

| Service | Environment Variable | Get Key At |
|---------|---------------------|------------|
| Comet ML | `COMET_API_KEY` | https://www.comet.com/ |
| LocalStack Pro | `LOCALSTACK_AUTH_TOKEN` | https://localstack.cloud/ |

---

## 📊 Benefits

### LocalStack
- ✅ No AWS charges during development
- ✅ Fast local testing
- ✅ Persistent data with Docker volumes
- ✅ Same APIs as real AWS
- ✅ GitHub Education Pro credits available

### Comet ML
- ✅ Track verification accuracy over time
- ✅ Compare AI provider performance
- ✅ A/B test different configurations
- ✅ Visualize metrics in dashboards
- ✅ GitHub Education enhanced free tier

---

## 🐛 Troubleshooting

### LocalStack Issues

```bash
# Check if LocalStack is running
docker-compose ps

# View LocalStack logs
docker-compose logs localstack

# Restart LocalStack
docker-compose restart localstack

# Reset all data
docker-compose down -v
docker-compose up -d
```

### Comet ML Issues

```python
# Test Comet connection
import comet_ml
comet_ml.init(api_key="your-key")
exp = comet_ml.Experiment()
exp.log_metric("test", 1.0)
exp.end()
```

### Common Errors

| Error | Solution |
|-------|----------|
| `Connection refused :4566` | Start LocalStack: `docker-compose up -d localstack` |
| `Comet API key not found` | Set `COMET_API_KEY` in `.env` |
| `Bucket not found` | Run init script or wait for healthcheck |
| `Table not found` | Tables are created on first use |

---

## 📚 Resources

- [LocalStack Documentation](https://docs.localstack.cloud/)
- [Comet ML Documentation](https://www.comet.com/docs/v2/)
- [AWS SDK for Python (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [GitHub Education](https://education.github.com/pack)
