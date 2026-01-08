# Verity Python SDK

Official Python SDK for the Verity Systems fact-checking API.

## Installation

```bash
pip install verity-sdk
```

## Quick Start

```python
from verity import VerityClient

client = VerityClient(api_key="your-api-key")
result = client.verify("The Earth is approximately 4.5 billion years old")

print(f"Verdict: {result.verdict}")
print(f"Confidence: {result.confidence}%")
print(f"Summary: {result.summary}")
```

## Features

- ✅ Synchronous and asynchronous clients
- ✅ Full type hints with Pydantic models
- ✅ Streaming support for real-time results
- ✅ Batch verification
- ✅ Automatic retries with exponential backoff
- ✅ Comprehensive error handling

## Usage

### Synchronous Client

```python
from verity import VerityClient

client = VerityClient(
    api_key="your-api-key",
    base_url="https://api.verity.systems",  # Optional
    timeout=30.0,  # Optional
    max_retries=3  # Optional
)

# Simple verification
result = client.verify("The moon landing happened in 1969")
print(result.verdict)  # TRUE

# With options
result = client.verify(
    claim="Climate change is caused by humans",
    providers=["groq", "wikipedia", "semantic_scholar"],
    depth="deep",
    include_sources=True
)

# Access evidence
for evidence in result.evidence:
    print(f"[{evidence.provider}] {evidence.verdict} ({evidence.confidence}%)")
    for source in evidence.sources:
        print(f"  - {source.title}: {source.url}")
```

### Async Client

```python
import asyncio
from verity import AsyncVerityClient

async def main():
    async with AsyncVerityClient(api_key="your-api-key") as client:
        # Single verification
        result = await client.verify("Vaccines are effective")
        print(result.verdict)
        
        # Concurrent verifications
        claims = [
            "The Earth is round",
            "Water boils at 100°C",
            "Gravity is 9.8 m/s²"
        ]
        results = await asyncio.gather(*[
            client.verify(claim) for claim in claims
        ])
        for claim, result in zip(claims, results):
            print(f"{claim}: {result.verdict}")

asyncio.run(main())
```

### Batch Verification

```python
from verity import VerityClient

client = VerityClient(api_key="your-api-key")

claims = [
    "The Great Wall of China is visible from space",
    "Lightning never strikes the same place twice",
    "Humans use only 10% of their brains"
]

results = client.verify_batch(claims)

for result in results:
    print(f"{result.claim}: {result.verdict}")
    # The Great Wall of China is visible from space: FALSE
    # Lightning never strikes the same place twice: FALSE
    # Humans use only 10% of their brains: FALSE
```

### Streaming Results

```python
from verity import VerityClient

client = VerityClient(api_key="your-api-key")

for event in client.verify_stream("COVID-19 vaccines are safe"):
    if event.type == "provider_start":
        print(f"⏳ {event.provider} processing...")
    
    elif event.type == "provider_result":
        print(f"✅ {event.provider}: {event.verdict} ({event.confidence}%)")
    
    elif event.type == "provider_error":
        print(f"❌ {event.provider} failed: {event.error}")
    
    elif event.type == "complete":
        print(f"\n📊 Final: {event.verdict} ({event.confidence}%)")
        print(f"📝 {event.summary}")
```

### Async Streaming

```python
import asyncio
from verity import AsyncVerityClient

async def main():
    async with AsyncVerityClient(api_key="your-api-key") as client:
        async for event in client.verify_stream("Climate change is real"):
            print(event)

asyncio.run(main())
```

## Models

### VerificationResult

```python
from verity.models import VerificationResult

result: VerificationResult

result.id            # str: Unique verification ID
result.claim         # str: Original claim
result.verdict       # Verdict: TRUE, FALSE, PARTIALLY_TRUE, etc.
result.confidence    # float: Confidence score (0-100)
result.summary       # str: Human-readable summary
result.evidence      # List[Evidence]: Per-provider results
result.metadata      # Metadata: Request metadata
```

### Verdict Enum

```python
from verity.models import Verdict

Verdict.TRUE           # Claim is true
Verdict.FALSE          # Claim is false
Verdict.PARTIALLY_TRUE # Claim is partially true
Verdict.MISLEADING     # Claim is misleading
Verdict.UNVERIFIABLE   # Cannot be verified
Verdict.OPINION        # Subjective opinion
```

### Evidence

```python
from verity.models import Evidence

evidence: Evidence

evidence.provider       # str: Provider ID
evidence.provider_type  # str: ai, news, academic, etc.
evidence.verdict        # Verdict
evidence.confidence     # float: Provider confidence
evidence.explanation    # str: Detailed explanation
evidence.sources        # List[Source]: Citations
evidence.latency_ms     # int: Response time
```

### Source

```python
from verity.models import Source

source: Source

source.title       # str: Source title
source.url         # Optional[str]: Source URL
source.credibility # float: Credibility score (0-1)
source.snippet     # Optional[str]: Relevant excerpt
```

## Error Handling

```python
from verity import VerityClient
from verity.exceptions import (
    VerityError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ProviderError,
    TimeoutError
)

client = VerityClient(api_key="your-api-key")

try:
    result = client.verify("Some claim")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except ProviderError as e:
    print(f"Provider {e.provider} failed: {e.message}")
except TimeoutError:
    print("Request timed out")
except VerityError as e:
    print(f"API error: {e.code} - {e.message}")
```

## Configuration

### Environment Variables

```bash
export VERITY_API_KEY="your-api-key"
export VERITY_BASE_URL="https://api.verity.systems"
export VERITY_TIMEOUT="30"
```

```python
from verity import VerityClient

# Automatically uses environment variables
client = VerityClient()
```

### Custom Configuration

```python
from verity import VerityClient

client = VerityClient(
    api_key="your-api-key",
    base_url="https://custom.api.endpoint",
    timeout=60.0,
    max_retries=5,
    retry_delay=1.0,
    headers={"X-Custom-Header": "value"}
)
```

## Advanced Usage

### Custom HTTP Client

```python
import httpx
from verity import VerityClient

# Use custom httpx client
http_client = httpx.Client(
    timeout=60.0,
    limits=httpx.Limits(max_connections=100)
)

client = VerityClient(
    api_key="your-api-key",
    http_client=http_client
)
```

### Retry Configuration

```python
from verity import VerityClient

client = VerityClient(
    api_key="your-api-key",
    max_retries=5,
    retry_delay=1.0,
    retry_statuses=[429, 500, 502, 503, 504],
    retry_on_timeout=True
)
```

### Provider Selection

```python
from verity import VerityClient

client = VerityClient(api_key="your-api-key")

# Get available providers
providers = client.get_providers()
for p in providers:
    print(f"{p.id}: {p.name} ({p.type}) - {p.status}")

# Use specific providers
result = client.verify(
    claim="Einstein developed relativity",
    providers=["groq", "wikipedia", "semantic_scholar", "arxiv"]
)
```

## Testing

```python
from verity import VerityClient
from verity.testing import MockVerityClient

# Use mock client for testing
mock_client = MockVerityClient()
mock_client.set_response(
    claim="Test claim",
    verdict="TRUE",
    confidence=95.0
)

result = mock_client.verify("Test claim")
assert result.verdict == "TRUE"
```

## Changelog

### 1.0.0
- Initial release
- Sync and async clients
- Streaming support
- Batch verification

## License

MIT License
