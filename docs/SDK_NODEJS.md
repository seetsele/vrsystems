# Verity Node.js/TypeScript SDK

Official Node.js SDK for the Verity Systems fact-checking API.

## Installation

```bash
npm install @verity-systems/sdk
# or
yarn add @verity-systems/sdk
# or
pnpm add @verity-systems/sdk
```

## Quick Start

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({ apiKey: 'your-api-key' });

const result = await client.verify('The Earth is approximately 4.5 billion years old');

console.log(`Verdict: ${result.verdict}`);
console.log(`Confidence: ${result.confidence}%`);
console.log(`Summary: ${result.summary}`);
```

## Features

- ✅ Full TypeScript support with comprehensive types
- ✅ Promise-based async API
- ✅ Streaming support with async iterators
- ✅ Batch verification
- ✅ Automatic retries with exponential backoff
- ✅ Works in Node.js, Deno, and Bun

## Usage

### Basic Verification

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.verity.systems', // Optional
  timeout: 30000, // Optional, in milliseconds
  maxRetries: 3 // Optional
});

// Simple verification
const result = await client.verify('The moon landing happened in 1969');
console.log(result.verdict); // TRUE

// With options
const result = await client.verify('Climate change is caused by humans', {
  providers: ['groq', 'wikipedia', 'semantic_scholar'],
  depth: 'deep',
  includeSources: true
});

// Access evidence
for (const evidence of result.evidence) {
  console.log(`[${evidence.provider}] ${evidence.verdict} (${evidence.confidence}%)`);
  for (const source of evidence.sources) {
    console.log(`  - ${source.title}: ${source.url}`);
  }
}
```

### Batch Verification

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({ apiKey: 'your-api-key' });

const claims = [
  'The Great Wall of China is visible from space',
  'Lightning never strikes the same place twice',
  'Humans use only 10% of their brains'
];

const results = await client.verifyBatch(claims);

for (const result of results) {
  console.log(`${result.claim}: ${result.verdict}`);
}
// The Great Wall of China is visible from space: FALSE
// Lightning never strikes the same place twice: FALSE
// Humans use only 10% of their brains: FALSE
```

### Streaming Results

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({ apiKey: 'your-api-key' });

for await (const event of client.verifyStream('COVID-19 vaccines are safe')) {
  switch (event.type) {
    case 'provider_start':
      console.log(`⏳ ${event.provider} processing...`);
      break;
    
    case 'provider_result':
      console.log(`✅ ${event.provider}: ${event.verdict} (${event.confidence}%)`);
      break;
    
    case 'provider_error':
      console.log(`❌ ${event.provider} failed: ${event.error}`);
      break;
    
    case 'complete':
      console.log(`\n📊 Final: ${event.verdict} (${event.confidence}%)`);
      console.log(`📝 ${event.summary}`);
      break;
  }
}
```

### With Callback Pattern

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({ apiKey: 'your-api-key' });

await client.verifyWithCallbacks('Vaccines cause autism', {
  onProviderStart: (provider) => {
    console.log(`${provider} started...`);
  },
  onProviderResult: (result) => {
    console.log(`${result.provider}: ${result.verdict}`);
  },
  onProviderError: (provider, error) => {
    console.error(`${provider} failed:`, error);
  },
  onComplete: (result) => {
    console.log('Final:', result.verdict);
  }
});
```

## TypeScript Types

### VerificationResult

```typescript
interface VerificationResult {
  id: string;
  claim: string;
  verdict: Verdict;
  confidence: number;
  summary: string;
  evidence: Evidence[];
  metadata: Metadata;
}
```

### Verdict

```typescript
type Verdict = 
  | 'TRUE'
  | 'FALSE'
  | 'PARTIALLY_TRUE'
  | 'MISLEADING'
  | 'UNVERIFIABLE'
  | 'OPINION';
```

### Evidence

```typescript
interface Evidence {
  provider: string;
  providerType: 'ai' | 'news' | 'academic' | 'knowledge' | 'government' | 'fact_check';
  verdict: Verdict;
  confidence: number;
  explanation: string;
  sources: Source[];
  latencyMs: number;
}
```

### Source

```typescript
interface Source {
  title: string;
  url?: string;
  credibility: number;
  snippet?: string;
}
```

### VerifyOptions

```typescript
interface VerifyOptions {
  providers?: string[];
  depth?: 'quick' | 'standard' | 'deep';
  includeSources?: boolean;
  language?: string;
  timeout?: number;
}
```

### StreamEvent

```typescript
type StreamEvent =
  | { type: 'start'; claim: string; providers: string[] }
  | { type: 'provider_start'; provider: string }
  | { type: 'provider_result'; provider: string; verdict: Verdict; confidence: number; latencyMs: number }
  | { type: 'provider_error'; provider: string; error: string }
  | { type: 'synthesis'; stage: string; progress: number }
  | { type: 'complete'; verdict: Verdict; confidence: number; summary: string };
```

## Error Handling

```typescript
import { VerityClient } from '@verity-systems/sdk';
import {
  VerityError,
  AuthenticationError,
  RateLimitError,
  ValidationError,
  ProviderError,
  TimeoutError
} from '@verity-systems/sdk';

const client = new VerityClient({ apiKey: 'your-api-key' });

try {
  const result = await client.verify('Some claim');
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error('Invalid API key');
  } else if (error instanceof RateLimitError) {
    console.error(`Rate limited. Retry after ${error.retryAfter} seconds`);
  } else if (error instanceof ValidationError) {
    console.error(`Invalid request: ${error.message}`);
  } else if (error instanceof ProviderError) {
    console.error(`Provider ${error.provider} failed: ${error.message}`);
  } else if (error instanceof TimeoutError) {
    console.error('Request timed out');
  } else if (error instanceof VerityError) {
    console.error(`API error: ${error.code} - ${error.message}`);
  }
}
```

## Configuration

### Environment Variables

```bash
export VERITY_API_KEY="your-api-key"
export VERITY_BASE_URL="https://api.verity.systems"
export VERITY_TIMEOUT="30000"
```

```typescript
import { VerityClient } from '@verity-systems/sdk';

// Automatically uses environment variables
const client = new VerityClient();
```

### Custom Configuration

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://custom.api.endpoint',
  timeout: 60000,
  maxRetries: 5,
  retryDelay: 1000,
  headers: {
    'X-Custom-Header': 'value'
  }
});
```

## Advanced Usage

### Custom Fetch Implementation

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({
  apiKey: 'your-api-key',
  fetch: customFetch // Custom fetch implementation
});
```

### Retry Configuration

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({
  apiKey: 'your-api-key',
  maxRetries: 5,
  retryDelay: 1000,
  retryStatuses: [429, 500, 502, 503, 504],
  retryOnTimeout: true
});
```

### Provider Management

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({ apiKey: 'your-api-key' });

// Get available providers
const providers = await client.getProviders();
for (const p of providers) {
  console.log(`${p.id}: ${p.name} (${p.type}) - ${p.status}`);
}

// Check provider health
const health = await client.getProviderHealth('groq');
console.log(`Uptime: ${health.uptime24h}%`);
console.log(`P95 Latency: ${health.latency.p95Ms}ms`);
```

### Request Interceptors

```typescript
import { VerityClient } from '@verity-systems/sdk';

const client = new VerityClient({
  apiKey: 'your-api-key',
  onRequest: (config) => {
    console.log(`Request: ${config.method} ${config.url}`);
    return config;
  },
  onResponse: (response) => {
    console.log(`Response: ${response.status}`);
    return response;
  },
  onError: (error) => {
    console.error('Error:', error);
    throw error;
  }
});
```

## Framework Integration

### Express.js

```typescript
import express from 'express';
import { VerityClient } from '@verity-systems/sdk';

const app = express();
const verity = new VerityClient({ apiKey: process.env.VERITY_API_KEY });

app.post('/verify', express.json(), async (req, res) => {
  try {
    const result = await verity.verify(req.body.claim);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Next.js API Route

```typescript
// pages/api/verify.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { VerityClient } from '@verity-systems/sdk';

const verity = new VerityClient({ apiKey: process.env.VERITY_API_KEY });

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).end();
  }
  
  const result = await verity.verify(req.body.claim);
  res.json(result);
}
```

### React Hook

```typescript
// useVerity.ts
import { useState, useCallback } from 'react';
import { VerityClient, VerificationResult, StreamEvent } from '@verity-systems/sdk';

const client = new VerityClient({ apiKey: 'your-api-key' });

export function useVerity() {
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [events, setEvents] = useState<StreamEvent[]>([]);

  const verify = useCallback(async (claim: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await client.verify(claim);
      setResult(result);
    } catch (e) {
      setError(e as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  const verifyStream = useCallback(async (claim: string) => {
    setLoading(true);
    setError(null);
    setEvents([]);
    try {
      for await (const event of client.verifyStream(claim)) {
        setEvents(prev => [...prev, event]);
        if (event.type === 'complete') {
          setResult(event as any);
        }
      }
    } catch (e) {
      setError(e as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, error, events, verify, verifyStream };
}
```

## Testing

```typescript
import { VerityClient } from '@verity-systems/sdk';
import { MockVerityClient } from '@verity-systems/sdk/testing';

// Use mock client for testing
const mockClient = new MockVerityClient();

mockClient.setResponse('Test claim', {
  verdict: 'TRUE',
  confidence: 95
});

const result = await mockClient.verify('Test claim');
expect(result.verdict).toBe('TRUE');

// Verify calls
expect(mockClient.getCalls()).toHaveLength(1);
expect(mockClient.getCalls()[0].claim).toBe('Test claim');
```

## Changelog

### 1.0.0
- Initial release
- Full TypeScript support
- Streaming with async iterators
- Batch verification
- React hook example

## License

MIT License
