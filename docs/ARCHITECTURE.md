# Verity Systems Architecture

## Overview

Verity Systems is built on a modular, scalable architecture designed for high-throughput fact-checking with multiple AI providers and data sources.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Web UI    │  Browser Extension  │  Slack Bot  │  Discord Bot  │  SDKs     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Rate Limiting  │  Authentication  │  Request Validation  │  Load Balancing │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI APPLICATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  REST Endpoints  │  WebSocket Handler  │  SSE Streaming  │  Health Checks   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MASTER ORCHESTRATOR                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Provider Selection  │  Parallel Execution  │  Circuit Breakers  │  Retry   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│    REDIS CACHE      │  │   FUSION ENGINE     │  │   PROVIDER LAYER    │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ Semantic Similarity │  │ Claim Analyzer      │  │ AI Providers        │
│ TTL Management      │  │ Source Ranker       │  │ News APIs           │
│ Cache Warming       │  │ Evidence Triangulat │  │ Academic Sources    │
│ Invalidation        │  │ Consensus Synthesiz │  │ Government Data     │
└─────────────────────┘  │ Confidence Calibrat │  │ Fact-Checkers       │
                         └─────────────────────┘  └─────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           OBSERVABILITY                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  Prometheus Metrics  │  Structured Logging  │  Distributed Tracing          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. API Layer (`api_server_ultimate.py`)

The FastAPI-based REST API provides:

- **Endpoints**:
  - `POST /v1/verify` - Single claim verification
  - `POST /v1/verify/batch` - Batch verification (up to 10 claims)
  - `POST /v1/verify/stream` - SSE streaming results
  - `GET /v1/providers` - List available providers
  - `GET /health` - Health check with dependency status
  - `GET /metrics` - Prometheus metrics

- **Features**:
  - JWT authentication with refresh tokens
  - API key management
  - Rate limiting (sliding window algorithm)
  - Request validation with Pydantic
  - CORS configuration
  - Compression middleware

### 2. Master Orchestrator (`verity_master_orchestrator_v2.py`)

Coordinates verification across providers:

```python
class VerityMasterOrchestrator:
    async def verify(self, claim: str, options: VerifyOptions) -> VerificationResult:
        # 1. Check cache
        cached = await self.cache.get(claim)
        if cached:
            return cached
        
        # 2. Select providers
        providers = self.select_providers(claim, options)
        
        # 3. Execute in parallel with circuit breakers
        results = await self.execute_parallel(providers, claim)
        
        # 4. Fuse results
        fused = await self.fusion_engine.fuse(results)
        
        # 5. Cache and return
        await self.cache.set(claim, fused)
        return fused
```

**Key Features**:
- Provider health monitoring
- Circuit breaker pattern for fault tolerance
- Exponential backoff retry
- Parallel execution with timeouts
- Streaming support

### 3. Fusion Engine (`verity_fusion_engine.py`)

Multi-stage evidence synthesis:

```
┌─────────────────────────────────────────────────────────────────┐
│                      FUSION PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Stage 1: CLAIM ANALYSIS                                        │
│  ├── Extract entities (NER)                                     │
│  ├── Classify claim type (factual, opinion, prediction)         │
│  ├── Identify temporal context                                  │
│  └── Detect checkworthiness                                     │
│                                                                  │
│  Stage 2: SOURCE AUTHORITY RANKING                              │
│  ├── Calculate base credibility score                           │
│  ├── Apply domain expertise weighting                           │
│  ├── Factor in recency and freshness                            │
│  └── Compute final authority score                              │
│                                                                  │
│  Stage 3: EVIDENCE TRIANGULATION                                │
│  ├── Cross-reference claims across sources                      │
│  ├── Identify corroborating evidence                            │
│  ├── Detect contradictions                                      │
│  └── Build evidence graph                                       │
│                                                                  │
│  Stage 4: CONSENSUS SYNTHESIS                                   │
│  ├── Weighted voting by authority                               │
│  ├── Agreement/disagreement analysis                            │
│  ├── Minority opinion handling                                  │
│  └── Final verdict determination                                │
│                                                                  │
│  Stage 5: CONFIDENCE CALIBRATION                                │
│  ├── Bayesian confidence estimation                             │
│  ├── Uncertainty quantification                                 │
│  ├── Source diversity factor                                    │
│  └── Final confidence score                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Provider Layer

Modular provider architecture:

```python
class BaseProvider(ABC):
    @abstractmethod
    async def check_claim(self, claim: str) -> ProviderResult:
        """Verify a claim and return structured result."""
        pass
    
    @abstractmethod
    async def search(self, query: str) -> List[SearchResult]:
        """Search for relevant information."""
        pass
    
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the type of provider (AI, NEWS, ACADEMIC, etc.)."""
        pass
```

**Provider Categories**:

| Category | Count | Examples |
|----------|-------|----------|
| AI/LLM | 8 | Groq, Cloudflare AI, SambaNova, NVIDIA NIM |
| News | 12 | Google Fact Check, NewsAPI, MediaStack |
| Academic | 12 | Semantic Scholar, OpenAlex, arXiv, PubMed |
| Search | 9 | DuckDuckGo, Brave, Wikipedia, Wikidata |
| Government | 8 | FRED, World Bank, CDC, NASA |
| Fact-Checkers | 6 | Snopes, PolitiFact, Full Fact, AFP |

### 5. Redis Cache (`verity_redis_cache.py`)

Intelligent caching layer:

```python
class VerityRedisCache:
    async def get(self, claim: str) -> Optional[CachedResult]:
        # 1. Try exact match
        exact = await self._get_exact(claim)
        if exact:
            return exact
        
        # 2. Try semantic similarity
        embedding = await self._get_embedding(claim)
        similar = await self._find_similar(embedding, threshold=0.95)
        if similar:
            return similar
        
        return None
    
    async def set(self, claim: str, result: VerificationResult, ttl: int = 3600):
        # Store with embedding for semantic search
        embedding = await self._get_embedding(claim)
        await self._store_with_embedding(claim, result, embedding, ttl)
```

**Features**:
- Exact match caching
- Semantic similarity matching (cosine similarity)
- TTL-based expiration
- Cache warming for common claims
- Invalidation on source updates

### 6. Metrics & Observability (`verity_metrics.py`)

Prometheus metrics:

```python
# Request metrics
verity_requests_total = Counter('verity_requests_total', 'Total requests', ['endpoint', 'status'])
verity_request_duration = Histogram('verity_request_duration_seconds', 'Request duration')

# Provider metrics
verity_provider_requests = Counter('verity_provider_requests_total', 'Provider requests', ['provider', 'status'])
verity_provider_latency = Histogram('verity_provider_latency_seconds', 'Provider latency', ['provider'])

# Cache metrics
verity_cache_hits = Counter('verity_cache_hits_total', 'Cache hits')
verity_cache_misses = Counter('verity_cache_misses_total', 'Cache misses')

# Business metrics
verity_verifications = Counter('verity_verifications_total', 'Total verifications', ['verdict'])
verity_confidence_distribution = Histogram('verity_confidence', 'Confidence distribution')
```

## Data Flow

### Single Verification Request

```
1. Client sends POST /v1/verify
                │
                ▼
2. API validates request & authenticates
                │
                ▼
3. Orchestrator checks Redis cache
                │
         ┌──────┴──────┐
         │             │
    Cache Hit     Cache Miss
         │             │
         ▼             ▼
4. Return cached   5. Select providers
   result             │
                      ▼
                 6. Execute providers in parallel
                      │
                      ▼
                 7. Fusion engine synthesizes results
                      │
                      ▼
                 8. Cache result in Redis
                      │
                      ▼
                 9. Return to client
```

### Streaming Verification

```
Client                    API                    Orchestrator              Providers
   │                       │                          │                        │
   │  POST /verify/stream  │                          │                        │
   │──────────────────────>│                          │                        │
   │                       │   verify_streaming()     │                        │
   │                       │─────────────────────────>│                        │
   │                       │                          │   check_claim()        │
   │                       │                          │───────────────────────>│
   │                       │                          │                        │
   │   SSE: provider_start │                          │<──────────────────────│
   │<──────────────────────│<─────────────────────────│   ProviderResult      │
   │                       │                          │                        │
   │   SSE: provider_result│                          │                        │
   │<──────────────────────│                          │                        │
   │                       │                          │                        │
   │         ...           │          ...             │          ...           │
   │                       │                          │                        │
   │   SSE: final_result   │                          │                        │
   │<──────────────────────│<─────────────────────────│                        │
   │                       │                          │                        │
```

## Deployment Architecture

### Kubernetes Deployment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           KUBERNETES CLUSTER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │   Ingress   │    │   Service   │    │     HPA     │                     │
│  │  (nginx)    │───>│  (ClusterIP)│───>│  (2-10 pods)│                     │
│  └─────────────┘    └─────────────┘    └─────────────┘                     │
│                                              │                              │
│                           ┌──────────────────┼──────────────────┐          │
│                           ▼                  ▼                  ▼          │
│                    ┌───────────┐      ┌───────────┐      ┌───────────┐    │
│                    │  API Pod  │      │  API Pod  │      │  API Pod  │    │
│                    │  (verity) │      │  (verity) │      │  (verity) │    │
│                    └───────────┘      └───────────┘      └───────────┘    │
│                           │                  │                  │          │
│                           └──────────────────┼──────────────────┘          │
│                                              ▼                              │
│                    ┌─────────────────────────────────────────────┐         │
│                    │              Redis Cluster                   │         │
│                    │  (Master + Replica, Sentinel)               │         │
│                    └─────────────────────────────────────────────┘         │
│                                              │                              │
│                           ┌──────────────────┼──────────────────┐          │
│                           ▼                  ▼                  ▼          │
│                    ┌───────────┐      ┌───────────┐      ┌───────────┐    │
│                    │Prometheus │      │  Grafana  │      │Alertmanager│   │
│                    └───────────┘      └───────────┘      └───────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### AWS Infrastructure (Terraform)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS REGION                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                              VPC                                       │  │
│  │  ┌────────────────────────┐    ┌────────────────────────┐           │  │
│  │  │   Public Subnet (AZ1)   │    │   Public Subnet (AZ2)   │           │  │
│  │  │  ┌─────────────────┐   │    │  ┌─────────────────┐   │           │  │
│  │  │  │   NAT Gateway   │   │    │  │   NAT Gateway   │   │           │  │
│  │  │  └─────────────────┘   │    │  └─────────────────┘   │           │  │
│  │  └────────────────────────┘    └────────────────────────┘           │  │
│  │                                                                       │  │
│  │  ┌────────────────────────┐    ┌────────────────────────┐           │  │
│  │  │  Private Subnet (AZ1)  │    │  Private Subnet (AZ2)  │           │  │
│  │  │  ┌─────────────────┐   │    │  ┌─────────────────┐   │           │  │
│  │  │  │  EKS Node Group │   │    │  │  EKS Node Group │   │           │  │
│  │  │  │  (t3.medium)    │   │    │  │  (t3.medium)    │   │           │  │
│  │  │  └─────────────────┘   │    │  └─────────────────┘   │           │  │
│  │  │                        │    │                        │           │  │
│  │  │  ┌─────────────────┐   │    │  ┌─────────────────┐   │           │  │
│  │  │  │  ElastiCache    │   │    │  │  ElastiCache    │   │           │  │
│  │  │  │  (Redis Node)   │   │    │  │  (Redis Node)   │   │           │  │
│  │  │  └─────────────────┘   │    │  └─────────────────┘   │           │  │
│  │  └────────────────────────┘    └────────────────────────┘           │  │
│  │                                                                       │  │
│  │  ┌──────────────────────────────────────────────────────────────┐   │  │
│  │  │                     EKS Control Plane                         │   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │     ALB     │    │   Route53   │    │     ACM     │                     │
│  │ (Ingress)   │    │   (DNS)     │    │   (TLS)     │                     │
│  └─────────────┘    └─────────────┘    └─────────────┘                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Authentication Flow

```
┌─────────┐         ┌─────────┐         ┌─────────┐
│ Client  │         │   API   │         │  Redis  │
└────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │
     │  POST /auth/login │                   │
     │  {email, password}│                   │
     │──────────────────>│                   │
     │                   │                   │
     │                   │  Validate creds   │
     │                   │──────────────────>│
     │                   │<──────────────────│
     │                   │                   │
     │   JWT + Refresh   │                   │
     │<──────────────────│                   │
     │                   │                   │
     │  POST /v1/verify  │                   │
     │  Authorization:   │                   │
     │  Bearer <JWT>     │                   │
     │──────────────────>│                   │
     │                   │                   │
     │                   │  Verify JWT       │
     │                   │  Check rate limit │
     │                   │──────────────────>│
     │                   │<──────────────────│
     │                   │                   │
     │    Response       │                   │
     │<──────────────────│                   │
     │                   │                   │
```

### API Key Security

- Keys generated with `secrets.token_urlsafe(32)`
- Stored as SHA-256 hash in database
- Rate limits tied to API key
- Scopes for fine-grained permissions
- Automatic rotation support

## Performance Characteristics

### Latency Breakdown

| Component | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| API Gateway | 2ms | 5ms | 10ms |
| Cache Lookup | 1ms | 3ms | 8ms |
| Provider Execution | 500ms | 1500ms | 3000ms |
| Fusion Engine | 50ms | 100ms | 200ms |
| **Total (Cache Hit)** | 10ms | 20ms | 50ms |
| **Total (Cache Miss)** | 600ms | 1800ms | 3500ms |

### Throughput

| Configuration | Requests/sec | Concurrent Users |
|---------------|--------------|------------------|
| Single Node | 100 | 500 |
| 3-Node Cluster | 300 | 1500 |
| 10-Node Cluster | 1000 | 5000 |

### Resource Requirements

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| API Server | 0.5-2 cores | 512MB-2GB | - |
| Redis | 0.5-1 cores | 1-4GB | 10-50GB |
| Prometheus | 0.5 cores | 1-2GB | 50-100GB |
| Grafana | 0.25 cores | 256-512MB | 1GB |

## Extensibility

### Adding a New Provider

1. Create provider class extending `BaseProvider`:

```python
# python-tools/providers/my_provider.py
from base_provider import BaseProvider, ProviderResult, ProviderType

class MyProvider(BaseProvider):
    name = "my_provider"
    provider_type = ProviderType.AI
    
    async def check_claim(self, claim: str) -> ProviderResult:
        # Implementation
        response = await self.client.verify(claim)
        return ProviderResult(
            verdict=response.verdict,
            confidence=response.confidence,
            explanation=response.explanation,
            sources=response.sources
        )
```

2. Register in orchestrator:

```python
# python-tools/verity_master_orchestrator_v2.py
from providers.my_provider import MyProvider

self.providers["my_provider"] = MyProvider(config)
```

3. Add configuration:

```yaml
# config/providers.yaml
my_provider:
  enabled: true
  weight: 0.8
  timeout: 10
  api_key: ${MY_PROVIDER_API_KEY}
```

### Custom Fusion Strategy

```python
from fusion_engine import BaseFusionStrategy

class CustomFusionStrategy(BaseFusionStrategy):
    def fuse(self, results: List[ProviderResult]) -> FusedResult:
        # Custom fusion logic
        pass

# Register
fusion_engine.register_strategy("custom", CustomFusionStrategy())
```

## Monitoring & Alerting

### Key Metrics to Monitor

1. **Availability**: API uptime, error rates
2. **Latency**: P50, P95, P99 response times
3. **Throughput**: Requests per second
4. **Provider Health**: Individual provider success rates
5. **Cache Performance**: Hit rate, latency
6. **Resource Usage**: CPU, memory, connections

### Alert Rules

```yaml
# High error rate
- alert: HighErrorRate
  expr: rate(verity_requests_total{status="error"}[5m]) > 0.1
  for: 5m
  
# Slow responses
- alert: SlowResponses
  expr: histogram_quantile(0.95, verity_request_duration_seconds) > 3
  for: 5m

# Provider down
- alert: ProviderDown
  expr: verity_provider_health == 0
  for: 2m
```

## Disaster Recovery

### Backup Strategy

- **Redis**: RDB snapshots every hour, AOF for durability
- **Configuration**: GitOps with version control
- **Secrets**: AWS Secrets Manager with rotation

### Recovery Procedures

1. **API Failure**: Kubernetes auto-restarts pods
2. **Redis Failure**: Sentinel promotes replica
3. **Region Failure**: DNS failover to secondary region
4. **Data Corruption**: Restore from RDB snapshot

---

*Last updated: January 2026*
