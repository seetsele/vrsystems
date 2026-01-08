# ============================================================================
# VERITY SYSTEMS - PRODUCTION DEPLOYMENT GUIDE
# ============================================================================
# Complete guide for deploying to production
# Last Updated: January 6, 2026

## STEP 1: Deploy API to Railway (or Render/DigitalOcean)

### Option A: Railway (Recommended - Easiest)

1. Go to https://railway.app and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `verity-systems` repository
4. Set the root directory to `python-tools`
5. Add these environment variables in Railway dashboard:

```
ENVIRONMENT=production
PORT=8000
VERITY_SECRET_KEY=your-secret-key-here
JWT_EXPIRY_HOURS=24
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
CORS_ORIGINS=https://verity.systems,https://www.verity.systems
API_KEYS=your-api-keys-here
LOG_LEVEL=INFO

# AI Provider Keys (get from each provider's dashboard)
GROQ_API_KEY=your-groq-key
GOOGLE_AI_API_KEY=your-google-ai-key
PERPLEXITY_API_KEY=your-perplexity-key
MISTRAL_API_KEY=your-mistral-key
OPENAI_API_KEY=your-openai-key
COHERE_API_KEY=your-cohere-key
OPENROUTER_API_KEY=your-openrouter-key

# Search Provider Keys
TAVILY_API_KEY=your-tavily-key
BRAVE_API_KEY=your-brave-key
SERPER_API_KEY=your-serper-key
```

6. Railway will auto-deploy. Note the generated URL (e.g., `verity-api.up.railway.app`)

### Option B: Render

1. Go to https://render.com and sign in
2. Click "New" → "Web Service"
3. Connect your GitHub repo
4. Set root directory to `python-tools`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn api_server_production:app --host 0.0.0.0 --port $PORT`
7. Add the same environment variables as above

### Option C: DigitalOcean App Platform

1. Go to https://cloud.digitalocean.com/apps
2. Create App → GitHub → Select repo
3. Set source directory to `python-tools`
4. Configure as Python app with same env vars

---

## STEP 2: Point DNS for api.verity.systems

After deploying the API, configure your DNS:

### For Railway:
1. In Railway dashboard, go to Settings → Domains
2. Add custom domain: `api.verity.systems`
3. Railway will show you a CNAME record to add
4. In your domain registrar (e.g., Namecheap, GoDaddy, Cloudflare):
   - Add CNAME record: `api` → `<your-railway-app>.up.railway.app`

### For Render:
1. In Render dashboard → Settings → Custom Domain
2. Add `api.verity.systems`
3. Add the CNAME record Render provides

### DNS Records to Add:
```
Type    Name    Value                           TTL
CNAME   api     <your-deployed-api-url>         3600
```

Wait 5-30 minutes for DNS propagation.

---

## STEP 3: Deploy Frontend to Vercel

1. Go to https://vercel.com and sign in with GitHub
2. Click "Add New" → "Project"
3. Import your `verity-systems` repository
4. Configure:
   - Framework Preset: Other
   - Root Directory: `.` (root)
   - Build Command: (leave empty)
   - Output Directory: `public`
5. Click "Deploy"

### Add Custom Domain:
1. In Vercel dashboard → Settings → Domains
2. Add `verity.systems` and `www.verity.systems`
3. Vercel will show DNS records to add:
   - `verity.systems` → A record to `76.76.21.21`
   - `www.verity.systems` → CNAME to `cname.vercel-dns.com`

---

## STEP 4: SSL Certificates

### Railway/Render/DigitalOcean:
- SSL is automatically provisioned (Let's Encrypt)
- No action needed

### Vercel:
- SSL is automatically provisioned
- No action needed

### Verify SSL:
```bash
curl -I https://api.verity.systems/health
curl -I https://verity.systems
```

Both should return `HTTP/2 200` with valid SSL certificates.

---

## POST-DEPLOYMENT CHECKLIST

- [ ] API health check: https://api.verity.systems/health
- [ ] API docs: https://api.verity.systems/docs
- [ ] Website loads: https://verity.systems
- [ ] Verify page works: https://verity.systems/verify.html
- [ ] SSL certificates valid (green padlock)
- [ ] CORS working (no console errors)
- [ ] Test verification endpoint with API key

### Test API:
```bash
curl -X POST https://api.verity.systems/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: PiLl66YdclgQCwEQFwp7rB5Diw3xDpvJi2cR709TNkA" \
  -d '{"claim": "Water boils at 100 degrees Celsius at sea level"}'
```

---

## ENVIRONMENT SUMMARY

| Service | Local URL | Production URL |
|---------|-----------|----------------|
| API | http://localhost:8081 | https://api.verity.systems |
| Website | http://localhost:3000 | https://verity.systems |
| API Docs | http://localhost:8081/docs | https://api.verity.systems/docs |

## API KEYS (Keep Secret!)
- `PiLl66YdclgQCwEQFwp7rB5Diw3xDpvJi2cR709TNkA`
- `TTIyLVvtam6Wq6WbSXfdMFxaBDQI6jSNLQsu0BzCzoY`
