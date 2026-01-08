# Verity Systems - Complete Integration Guide v8.0

## 🎯 Overview

Verity Systems is a comprehensive AI-powered fact verification platform that aggregates data from **40+ authoritative sources** to deliver accurate, trustworthy verification results.

---

## 📊 Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           VERITY SYSTEMS v8.0                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   ┌─────────────┐    ┌──────────────────┐    ┌─────────────────────────────┐ │
│   │   CLIENTS   │    │   UNIFIED API    │    │      DATA PROVIDERS         │ │
│   │             │    │                  │    │                             │ │
│   │ • Web App   │───▶│ • Authentication │───▶│ AI Models (11 providers)    │ │
│   │ • Desktop   │    │ • Rate Limiting  │    │ Search (6 providers)        │ │
│   │ • Mobile    │    │ • Verification   │    │ Academic (6 providers)      │ │
│   │ • API       │◀───│ • Consensus      │◀───│ Fact-Check (4 providers)    │ │
│   │             │    │                  │    │ News (3 providers)          │ │
│   └─────────────┘    └──────────────────┘    │ Knowledge (6 providers)     │ │
│                                               │ Government (4+ sources)     │ │
│                                               └─────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 API Configuration

### Quick Start
```bash
# Start the API server
cd python-tools
python api_server_unified.py

# Server runs at http://localhost:9000 (or PORT env var)
```

### Environment Variables
Create a `.env` file in the project root:

```env
# Server Configuration
ENVIRONMENT=development
PORT=9000
HOST=0.0.0.0
DEBUG=true

# Authentication
VERITY_SECRET_KEY=your-secure-secret-key
API_KEYS=demo-key,your-api-key

# AI Providers
GROQ_API_KEY=your-groq-key
GOOGLE_AI_API_KEY=your-google-ai-key
PERPLEXITY_API_KEY=your-perplexity-key
MISTRAL_API_KEY=your-mistral-key
OPENAI_API_KEY=your-openai-key
COHERE_API_KEY=your-cohere-key

# Search Providers
TAVILY_API_KEY=your-tavily-key
BRAVE_API_KEY=your-brave-key
SERPER_API_KEY=your-serper-key
EXA_API_KEY=your-exa-key
YOU_API_KEY=your-you-key

# Academic (some are FREE)
SEMANTIC_SCHOLAR_API_KEY=your-semantic-scholar-key

# Fact-Check
GOOGLE_FACTCHECK_API_KEY=your-factcheck-key
CLAIMBUSTER_API_KEY=your-claimbuster-key

# News
NEWS_API_KEY=your-newsapi-key
MEDIASTACK_API_KEY=your-mediastack-key
```

---

## 🔐 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and provider counts |
| `/health` | GET | Health check |
| `/verify` | POST | Verify a single claim |
| `/batch` | POST | Batch verify multiple claims |
| `/analyze/url` | POST | Analyze a URL |
| `/analyze/text` | POST | Analyze text content |
| `/providers` | GET | List all providers |
| `/stats` | GET | API statistics |
| `/docs` | GET | Interactive API documentation |

### Verify a Claim
```bash
curl -X POST http://localhost:9000/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{"claim": "The Earth orbits the Sun"}'
```

Response:
```json
{
  "claim": "The Earth orbits the Sun",
  "category": "scientific",
  "verdict": "true",
  "confidence": 0.95,
  "consistency": 1.0,
  "passes": {
    "search": { "verdict": "true", "confidence": 0.85 },
    "ai_validation": { "verdict": "true", "confidence": 0.92 },
    "high_trust": { "verdict": "true", "confidence": 0.98 }
  },
  "total_sources": 12,
  "cross_references": 10,
  "processing_time": 2.5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Batch Verification
```bash
curl -X POST http://localhost:9000/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{"claims": ["Claim 1", "Claim 2", "Claim 3"]}'
```

---

## 🔄 3-Pass Verification System

Verity uses a sophisticated 3-pass verification pipeline:

### Pass 1: Search & Discovery (Weight: 0.2)
- **Providers**: Tavily, Brave, Serper, Exa, You
- **Purpose**: Find relevant sources and initial evidence
- **Trust Weight**: 0.7

### Pass 2: AI Cross-Validation (Weight: 0.3)
- **Providers**: Groq, Gemini, Perplexity, Mistral, OpenAI, Cohere
- **Purpose**: Intelligent analysis and reasoning
- **Trust Weight**: 0.65

### Pass 3: High-Trust Sources (Weight: 0.5)
- **Academic**: Semantic Scholar, OpenAlex, CrossRef, PubMed (Trust: 0.85-0.9)
- **Fact-Check**: Google Fact Check, ClaimBuster (Trust: 0.85)
- **Knowledge**: DBpedia, Wikidata, ConceptNet (Trust: 0.8)

### Consensus Calculation
```
Final Score = Σ(pass_weight × verdict_confidence × source_trust_weight)
```

---

## 📦 Provider Registry

### AI Language Models (Trust: 0.65)
| Provider | API Key Env Var | Model |
|----------|-----------------|-------|
| Groq | GROQ_API_KEY | llama-3.1-70b-versatile |
| Google AI | GOOGLE_AI_API_KEY | gemini-pro |
| Perplexity | PERPLEXITY_API_KEY | llama-3.1-sonar-large |
| Mistral | MISTRAL_API_KEY | mistral-large-latest |
| OpenAI | OPENAI_API_KEY | gpt-4-turbo |
| Cohere | COHERE_API_KEY | command-r-plus |

### Search Engines (Trust: 0.7)
| Provider | API Key Env Var | Type |
|----------|-----------------|------|
| Tavily | TAVILY_API_KEY | AI Search |
| Brave | BRAVE_API_KEY | Web Search |
| Serper | SERPER_API_KEY | Google Search |
| Exa | EXA_API_KEY | Neural Search |
| You | YOU_API_KEY | AI Search |

### Academic Sources (Trust: 0.85-0.9)
| Provider | API Key | Notes |
|----------|---------|-------|
| Semantic Scholar | Optional | 200M+ papers |
| OpenAlex | FREE | Open scholarly data |
| CrossRef | FREE | DOI metadata |
| PubMed | FREE | 35M+ biomedical |
| arXiv | FREE | Preprints |

### Government Sources (Trust: 1.0) - FREE
| Source | Domain |
|--------|--------|
| WHO | who.int |
| CDC | cdc.gov |
| FDA | fda.gov |
| EPA | epa.gov |
| NIH | nih.gov |
| World Bank | worldbank.org |

---

## 💻 Frontend Integration

### Using the Unified Client

Include the scripts:
```html
<script src="/assets/js/verity-config.js"></script>
<script src="/assets/js/verity-api-v8.js"></script>
```

Basic usage:
```javascript
// Verify a claim
const result = await VerityAPI.verify("The claim to verify");
console.log(result.verdict, result.confidence);

// Batch verification
const results = await VerityAPI.batchVerify([
  "Claim 1",
  "Claim 2",
  "Claim 3"
]);

// Get available providers
const providers = await VerityAPI.getProviders();

// Format results for display
const summary = VerityAPI.formatter.getSummary(result);
const badge = VerityAPI.formatter.createBadge(result);
```

### Configuration
```javascript
// Access configuration
const apiBase = VERITY_CONFIG.api.base;
const timeout = VERITY_CONFIG.api.timeout;
const verdictColors = VERITY_CONFIG.ui.verdicts;

// Create custom client
const customClient = VerityAPI.createClient({
  baseURL: 'https://veritysystems-production.up.railway.app',
  timeout: 60000,
  debug: true
});
```

---

## 🚀 Deployment

### Docker
```bash
docker-compose -f docker-compose.production.yml up -d
```

### Railway (API)
```bash
railway login
railway init
railway up
```

### Vercel (Frontend)
```bash
vercel login
vercel --prod
```

### Environment for Production
```env
ENVIRONMENT=production
DEBUG=false
PORT=8081
CORS_ORIGINS=https://verity.systems,https://www.verity.systems
```

---

## 📁 File Structure

```
verity-systems/
├── python-tools/
│   ├── api_server_unified.py      # Main unified API (v8.0)
│   ├── api_server_production.py   # Previous production API
│   └── verity_*.py                # Verification modules
├── public/
│   ├── assets/
│   │   ├── js/
│   │   │   ├── verity-config.js   # Unified configuration
│   │   │   └── verity-api-v8.js   # Unified API client
│   │   └── css/
│   ├── verify.html
│   ├── dashboard.html
│   └── index.html
├── desktop-app/                    # Electron desktop app
├── verity-mobile/                  # React Native mobile app
├── .env                            # Local environment
├── .env.master                     # Master API documentation
├── docker-compose.yml
└── README.md
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find process using port
netstat -ano | findstr :9000

# Kill process
taskkill /PID <process_id> /F
```

### API Connection Failed
1. Check server is running: `curl http://localhost:9000/health`
2. Verify CORS settings in `.env`
3. Check API key is valid

### Missing Providers
- Verify API keys are set in `.env`
- Check `http://localhost:9000/providers` to see active providers
- Some providers (Academic, Government) work without API keys

---

## 📊 Verdict Meanings

| Verdict | Description | Confidence Range |
|---------|-------------|-----------------|
| `true` | Verified as factually accurate | 85%+ |
| `false` | Verified as factually inaccurate | 85%+ |
| `partially_true` | Contains both true and false elements | 65-85% |
| `unverifiable` | Cannot determine with confidence | <65% |

---

## 🔗 API Key Sources

### Recommended (Essential)
- **Groq**: https://console.groq.com (FREE tier available)
- **Google AI**: https://makersuite.google.com (FREE tier)
- **Tavily**: https://tavily.com (FREE tier)
- **Perplexity**: https://perplexity.ai/api

### Additional (Enhance accuracy)
- **Serper**: https://serper.dev
- **Brave**: https://api.search.brave.com
- **NewsAPI**: https://newsapi.org
- **OpenAI**: https://platform.openai.com

---

## 📈 Performance

- Average response time: 2-5 seconds
- Providers queried per request: 10-20
- Consensus agreement threshold: 66%
- Rate limits (default): 100 requests/minute

---

## 🆘 Support

- Documentation: `/docs` endpoint
- Health check: `/health` endpoint
- Provider status: `/providers` endpoint

---

**Version**: 8.0.0  
**Last Updated**: January 2025
