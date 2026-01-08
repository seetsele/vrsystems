# Verity Systems API Documentation

## Overview

The Verity Systems API provides programmatic access to our fact-checking platform. Verify claims using 50+ AI models, news sources, academic databases, and fact-checkers.

**Base URL**: `https://api.verity.systems`

**Version**: `v1`

## Authentication

All API requests require authentication using either:

### API Key (Recommended)
```http
Authorization: Bearer YOUR_API_KEY
```

### JWT Token
```http
Authorization: Bearer YOUR_JWT_TOKEN
```

### Obtaining API Keys

1. Sign up at [verity.systems](https://verity.systems)
2. Navigate to Settings → API Keys
3. Generate a new API key
4. Store securely - keys are only shown once

## Rate Limits

| Plan | Requests/min | Requests/day | Concurrent |
|------|--------------|--------------|------------|
| Free | 10 | 100 | 2 |
| Starter | 60 | 1,000 | 5 |
| Pro | 300 | 10,000 | 20 |
| Enterprise | Custom | Custom | Custom |

Rate limit headers:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704672000
```

## Endpoints

### Verify Single Claim

Verify a single claim against selected providers.

```http
POST /v1/verify
```

#### Request Body

```json
{
  "claim": "The Earth is approximately 4.5 billion years old",
  "providers": ["groq", "wikipedia", "semantic_scholar"],
  "options": {
    "depth": "standard",
    "include_sources": true,
    "language": "en"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `claim` | string | Yes | The claim to verify (max 2000 chars) |
| `providers` | string[] | No | Provider IDs to use (default: auto-select) |
| `options.depth` | string | No | `quick`, `standard`, `deep` (default: `standard`) |
| `options.include_sources` | boolean | No | Include source citations (default: true) |
| `options.language` | string | No | ISO 639-1 language code (default: `en`) |

#### Response

```json
{
  "id": "ver_abc123xyz",
  "claim": "The Earth is approximately 4.5 billion years old",
  "verdict": "TRUE",
  "confidence": 95.2,
  "summary": "Scientific consensus strongly supports this claim. Radiometric dating of meteorites and Earth rocks consistently indicates an age of approximately 4.54 billion years.",
  "evidence": [
    {
      "provider": "groq",
      "provider_type": "ai",
      "verdict": "TRUE",
      "confidence": 94,
      "explanation": "Based on radiometric dating methods, including uranium-lead dating of zircon crystals...",
      "sources": [
        {
          "title": "Age of the Earth",
          "url": "https://en.wikipedia.org/wiki/Age_of_Earth",
          "credibility": 0.9
        }
      ],
      "latency_ms": 423
    },
    {
      "provider": "wikipedia",
      "provider_type": "knowledge",
      "verdict": "TRUE",
      "confidence": 98,
      "explanation": "According to Wikipedia, the age of Earth is estimated to be 4.54 ± 0.05 billion years...",
      "sources": [
        {
          "title": "Age of Earth - Wikipedia",
          "url": "https://en.wikipedia.org/wiki/Age_of_Earth",
          "credibility": 0.85
        }
      ],
      "latency_ms": 156
    }
  ],
  "metadata": {
    "request_id": "req_def456",
    "processing_time_ms": 1243,
    "providers_requested": 3,
    "providers_succeeded": 3,
    "cache_hit": false,
    "created_at": "2026-01-08T12:00:00Z"
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique verification ID |
| `verdict` | string | `TRUE`, `FALSE`, `PARTIALLY_TRUE`, `UNVERIFIABLE`, `MISLEADING` |
| `confidence` | number | Confidence score (0-100) |
| `summary` | string | Human-readable summary |
| `evidence` | array | Per-provider results |
| `metadata` | object | Request metadata |

---

### Verify Batch

Verify multiple claims in a single request.

```http
POST /v1/verify/batch
```

#### Request Body

```json
{
  "claims": [
    "The Earth is round",
    "Water boils at 100°C at sea level",
    "The Great Wall of China is visible from space"
  ],
  "providers": ["groq", "wikipedia"],
  "options": {
    "depth": "quick"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `claims` | string[] | Yes | Array of claims (max 10) |
| `providers` | string[] | No | Provider IDs |
| `options` | object | No | Verification options |

#### Response

```json
{
  "batch_id": "batch_abc123",
  "results": [
    {
      "claim": "The Earth is round",
      "verdict": "TRUE",
      "confidence": 99.1,
      "summary": "..."
    },
    {
      "claim": "Water boils at 100°C at sea level",
      "verdict": "TRUE",
      "confidence": 98.5,
      "summary": "..."
    },
    {
      "claim": "The Great Wall of China is visible from space",
      "verdict": "FALSE",
      "confidence": 92.3,
      "summary": "This is a common misconception..."
    }
  ],
  "metadata": {
    "total_claims": 3,
    "processing_time_ms": 2156
  }
}
```

---

### Verify Stream (SSE)

Stream verification results as they arrive from providers.

```http
POST /v1/verify/stream
```

#### Request Body

Same as `/v1/verify`

#### Response

Server-Sent Events stream:

```
event: start
data: {"claim": "The Earth is 4.5 billion years old", "providers": ["groq", "wikipedia"]}

event: provider_start
data: {"provider": "groq", "status": "processing"}

event: provider_result
data: {"provider": "groq", "verdict": "TRUE", "confidence": 94, "latency_ms": 423}

event: provider_start
data: {"provider": "wikipedia", "status": "processing"}

event: provider_result
data: {"provider": "wikipedia", "verdict": "TRUE", "confidence": 98, "latency_ms": 156}

event: synthesis
data: {"stage": "fusion", "progress": 80}

event: complete
data: {"verdict": "TRUE", "confidence": 95.2, "summary": "..."}
```

#### Event Types

| Event | Description |
|-------|-------------|
| `start` | Verification started |
| `provider_start` | Provider started processing |
| `provider_result` | Provider returned result |
| `provider_error` | Provider failed |
| `synthesis` | Fusion progress update |
| `complete` | Final result |
| `error` | Error occurred |

---

### List Providers

Get available verification providers.

```http
GET /v1/providers
```

#### Response

```json
{
  "providers": [
    {
      "id": "groq",
      "name": "Groq",
      "type": "ai",
      "models": ["llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
      "status": "operational",
      "latency_avg_ms": 450,
      "success_rate": 0.99
    },
    {
      "id": "wikipedia",
      "name": "Wikipedia",
      "type": "knowledge",
      "status": "operational",
      "latency_avg_ms": 150,
      "success_rate": 0.999
    }
  ],
  "categories": {
    "ai": ["groq", "cloudflare_ai", "sambanova", "nvidia_nim"],
    "news": ["google_fact_check", "newsapi", "mediastack"],
    "academic": ["semantic_scholar", "openalgex", "arxiv", "pubmed"],
    "knowledge": ["wikipedia", "wikidata", "duckduckgo"],
    "government": ["fred", "world_bank", "cdc", "nasa"],
    "fact_check": ["snopes", "politifact", "full_fact"]
  }
}
```

---

### Provider Health

Get health status of a specific provider.

```http
GET /v1/providers/{provider_id}/health
```

#### Response

```json
{
  "provider_id": "groq",
  "status": "operational",
  "uptime_24h": 99.95,
  "latency": {
    "p50_ms": 420,
    "p95_ms": 850,
    "p99_ms": 1200
  },
  "error_rate_24h": 0.001,
  "last_check": "2026-01-08T12:00:00Z"
}
```

---

### Health Check

Check API health and dependencies.

```http
GET /health
```

#### Response

```json
{
  "status": "healthy",
  "version": "1.5.0",
  "uptime_seconds": 86400,
  "dependencies": {
    "redis": {
      "status": "healthy",
      "latency_ms": 2
    },
    "database": {
      "status": "healthy",
      "latency_ms": 5
    }
  },
  "providers": {
    "total": 50,
    "healthy": 48,
    "degraded": 2
  }
}
```

---

## Webhooks

Receive notifications when verifications complete (async mode).

### Configure Webhook

```http
POST /v1/webhooks
```

```json
{
  "url": "https://your-app.com/webhook",
  "events": ["verification.complete", "verification.failed"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload

```json
{
  "event": "verification.complete",
  "timestamp": "2026-01-08T12:00:00Z",
  "data": {
    "id": "ver_abc123",
    "claim": "...",
    "verdict": "TRUE",
    "confidence": 95.2
  },
  "signature": "sha256=..."
}
```

Verify signature:
```python
import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please retry after 60 seconds.",
    "details": {
      "limit": 60,
      "reset_at": "2026-01-08T12:01:00Z"
    }
  },
  "request_id": "req_abc123"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request body |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `PROVIDER_ERROR` | 502 | Provider returned error |
| `TIMEOUT` | 504 | Request timed out |
| `INTERNAL_ERROR` | 500 | Internal server error |

### Retry Strategy

```python
import time
from typing import Optional

def verify_with_retry(claim: str, max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        response = requests.post(
            "https://api.verity.systems/v1/verify",
            json={"claim": claim},
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            time.sleep(retry_after)
            continue
            
        if response.status_code >= 500:
            time.sleep(2 ** attempt)  # Exponential backoff
            continue
            
        return response.json()
    
    raise Exception("Max retries exceeded")
```

---

## SDKs

### Python SDK

```bash
pip install verity-sdk
```

```python
from verity import VerityClient, AsyncVerityClient

# Synchronous
client = VerityClient(api_key="your-api-key")
result = client.verify("The Earth is round")
print(f"{result.verdict}: {result.confidence}%")

# Async
async with AsyncVerityClient(api_key="your-api-key") as client:
    result = await client.verify("Climate change is real")
    
# Streaming
for event in client.verify_stream("Vaccines are safe"):
    if event.type == "provider_result":
        print(f"[{event.provider}] {event.verdict}")
    elif event.type == "complete":
        print(f"Final: {event.verdict}")
```

### Node.js SDK

```bash
npm install @verity-systems/sdk
```

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({ apiKey: 'your-api-key' });

// Simple
const result = await client.verify('The moon landing was real');
console.log(`${result.verdict}: ${result.confidence}%`);

// Batch
const results = await client.verifyBatch([
  'Earth is round',
  'Water is wet'
]);

// Streaming
for await (const event of client.verifyStream('COVID vaccines work')) {
  console.log(event);
}
```

---

## Best Practices

### 1. Choose Appropriate Depth

- **`quick`**: Fast, uses 2-3 providers. Good for real-time UI.
- **`standard`**: Balanced, uses 5-7 providers. Recommended default.
- **`deep`**: Thorough, uses 10+ providers. Best for important decisions.

### 2. Handle Streaming for Long Claims

Complex claims take longer to verify. Use streaming to show progress:

```javascript
const eventSource = new EventSource('/v1/verify/stream?claim=...');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateUI(data);
};
```

### 3. Cache Results Client-Side

```python
import hashlib

def cache_key(claim: str) -> str:
    return hashlib.sha256(claim.lower().strip().encode()).hexdigest()

# Check local cache before API call
cached = local_cache.get(cache_key(claim))
if cached and not cached.is_expired:
    return cached.result
```

### 4. Implement Exponential Backoff

```python
def backoff_retry(func, max_retries=5):
    for i in range(max_retries):
        try:
            return func()
        except RateLimitError:
            time.sleep(2 ** i + random.random())
    raise MaxRetriesExceeded()
```

### 5. Use Batch API for Multiple Claims

Instead of:
```python
# ❌ Slow - 10 sequential requests
for claim in claims:
    result = client.verify(claim)
```

Do:
```python
# ✅ Fast - 1 request
results = client.verify_batch(claims)
```

---

## Changelog

### v1.5.0 (2026-01-08)
- Added 20 new providers
- Streaming API improvements
- Batch endpoint now supports 10 claims

### v1.4.0 (2025-12-15)
- WebSocket support
- Provider health endpoint
- Rate limit headers

### v1.3.0 (2025-11-01)
- Batch verification
- Webhook support
- Python and Node.js SDKs

---

## Support

- **Documentation**: [docs.verity.systems](https://docs.verity.systems)
- **Status Page**: [status.verity.systems](https://status.verity.systems)
- **Email**: support@verity.systems
- **Discord**: [discord.gg/verity](https://discord.gg/verity)
