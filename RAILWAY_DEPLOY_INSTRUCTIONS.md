# 🚀 Railway Deployment Instructions

## Current Status

| Component | Local | Railway |
|-----------|-------|---------|
| Version | **v9.0.0** ✅ | v2.0.0 ⚠️ |
| AI Providers | **10** ✅ | 3 ⚠️ |
| Tool Endpoints | **6** ✅ | Unknown |

## Why Railway Isn't Updating

Railway auto-deploy webhook may be:
1. Disabled in settings
2. Misconfigured webhook
3. Branch mismatch
4. Build failing silently

## Manual Deploy Steps

### Option 1: Railway Dashboard
1. Go to https://railway.app/dashboard
2. Find the **Verity Systems** project
3. Click the **service** (API)
4. Click **Deployments** tab
5. Click **"Redeploy"** or **"Deploy Now"**

### Option 2: Railway CLI
```bash
# Install Railway CLI if not installed
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Force deploy
railway up
```

### Option 3: Trigger via Settings
1. Go to Railway Dashboard → Project → Settings
2. Check "Enable automatic deployments from GitHub"
3. Verify correct branch is selected (main)
4. Click "Trigger deployment"

## Verify Deployment Success

After deploying, check:
```bash
curl https://veritysystems-production.up.railway.app/health
```

Expected response:
```json
{
  "version": "9.0.0",
  "providers_available": 10,
  "providers": ["groq", "perplexity", "google", "openai", "mistral", "cohere", "cerebras", "sambanova", "fireworks", "openrouter"]
}
```

## Environment Variables Required

Make sure these are set in Railway:
- `GROQ_API_KEY`
- `PERPLEXITY_API_KEY`
- `GOOGLE_API_KEY`
- `OPENAI_API_KEY`
- `MISTRAL_API_KEY`
- `COHERE_API_KEY`
- `CEREBRAS_API_KEY`
- `SAMBANOVA_API_KEY`
- `FIREWORKS_API_KEY`
- `OPENROUTER_API_KEY`
- `STRIPE_SECRET_KEY` (optional, for billing)

## Files Updated for v9.0.0

- `python-tools/api_server_v9.py` - Main server with 10 providers
- `python-tools/Procfile` - Points to v9
- `python-tools/railway.json` - Deploy config → v9
- `railway.toml` - Root config → main.py → v9
- `main.py` - Root entry point

## What's New in v9.0.0

✅ **10 AI Providers** (up from 3):
- Groq (llama-3.3-70b-versatile)
- Perplexity (sonar-pro)
- Google (gemini-2.0-flash-exp)
- OpenAI (gpt-4o)
- Mistral (mistral-large-latest)
- Cohere (command-r-plus)
- Cerebras (llama-3.3-70b)
- SambaNova (Meta-Llama-3.3-70B-Instruct)
- Fireworks (llama-v3p3-70b-instruct)
- OpenRouter (meta-llama/llama-3.3-70b-instruct)

✅ **All 6 Tool Endpoints**:
- `/tools/sources` - Source verification
- `/tools/stats` - Statistics validation
- `/tools/content` - Content moderation
- `/tools/research` - Research assistant
- `/tools/realtime` - Real-time streams
- `/tools/map` - Misinformation mapping

✅ **Rate Limiting** - 100 requests/minute per IP

✅ **API Key Authentication** - Set `REQUIRE_API_KEY=true` to enable

✅ **Stripe Integration** - `/stripe/create-checkout` & `/stripe/config`

---

**Generated:** January 9, 2026
