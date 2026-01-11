# API Uptime Strategy & Best Practices

This document outlines how to ensure the Verity Systems API stays running reliably in production.

---

## 🏗️ Current Infrastructure

| Component | Platform | Purpose |
|-----------|----------|---------|
| **Frontend** | Vercel | Static site hosting (veritysystems.app) |
| **API Server** | Railway | Python API server (veritysystems-production.up.railway.app) |
| **Database** | Supabase | PostgreSQL + Auth + Realtime |
| **Rate Limiting** | Upstash Redis | Distributed rate limiting cache |

---

## 🚀 Railway API Server Setup

### Why Railway?
- **Auto-scaling**: Automatically scales based on load
- **Zero-downtime deploys**: Rolling deployments with health checks
- **Built-in monitoring**: CPU, memory, and request metrics
- **SSL included**: Automatic HTTPS for all domains
- **Global CDN**: Edge caching for faster responses

### Deployment Configuration

1. **Connect your repository** to Railway:
   ```
   railway login
   railway link
   railway up
   ```

2. **Set environment variables** in Railway dashboard:
   ```
   SUPABASE_URL=https://zxgydzavblgetojqdtir.supabase.co
   SUPABASE_SERVICE_KEY=your-service-key
   UPSTASH_REDIS_URL=your-redis-url
   UPSTASH_REDIS_TOKEN=your-redis-token
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   ```

3. **Configure health checks** in `railway.toml`:
   ```toml
   [deploy]
   startCommand = "python api_server_v4.py"
   healthcheckPath = "/health"
   healthcheckTimeout = 30
   restartPolicyType = "on_failure"
   restartPolicyMaxRetries = 3
   ```

---

## ⚡ Ensuring High Availability

### 1. Health Check Endpoint

The API includes a `/health` endpoint that Railway uses to verify the server is running:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "4.0.0"
    }
```

Railway will:
- Check this endpoint every 10 seconds
- Restart the container if it fails 3 times
- Route traffic away from unhealthy instances

### 2. Railway Auto-Restart

Railway automatically restarts crashed services:
- **On crash**: Immediate restart with exponential backoff
- **On deploy**: Zero-downtime rolling deployment
- **On memory limit**: Restart before OOM

### 3. Multiple Replicas (Recommended for Production)

For high availability, run multiple replicas:

1. In Railway dashboard → Settings → Replicas
2. Set replicas to 2+ for redundancy
3. Railway load balances automatically

### 4. Graceful Shutdown

The API handles shutdown signals gracefully:

```python
import signal
import sys

def shutdown_handler(signum, frame):
    logger.info("Shutting down gracefully...")
    # Close database connections
    # Finish pending requests
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
```

---

## 📊 Monitoring & Alerts

### Railway Built-in Monitoring
- **Metrics**: CPU, memory, requests, response times
- **Logs**: Real-time log streaming
- **Alerts**: Set up alerts for errors and high latency

### Recommended External Monitoring

1. **Uptime Monitoring** (pick one):
   - [Better Uptime](https://betterstack.com/uptime) - Free tier, 5 monitors
   - [Uptime Robot](https://uptimerobot.com) - Free tier, 50 monitors
   - [Pingdom](https://www.pingdom.com) - Professional grade

2. **Error Tracking**:
   - [Sentry](https://sentry.io) - Free tier, error tracking
   
   Add to `requirements.txt`:
   ```
   sentry-sdk[fastapi]==1.35.0
   ```
   
   Initialize in your API:
   ```python
   import sentry_sdk
   sentry_sdk.init(dsn="your-sentry-dsn", traces_sample_rate=0.1)
   ```

3. **Performance Monitoring**:
   - Railway provides built-in APM
   - Or use New Relic / Datadog for advanced needs

---

## 🔄 Automatic Deployments

### GitHub Integration

Railway auto-deploys on push to `main`:

1. **Connect GitHub** in Railway dashboard
2. **Set branch**: `main` for production
3. **Auto-deploy**: Enabled by default

Every `git push origin main` triggers:
1. Build new container
2. Health check new instance
3. Route traffic to new instance
4. Terminate old instance

### Manual Deploy

```bash
# From your local machine
railway up

# Or via GitHub
git push origin main
```

---

## 🛡️ Rate Limiting with Upstash Redis

Distributed rate limiting ensures fair usage across all API replicas:

```python
# Already implemented in api_server_v4.py
from upstash_ratelimit import Ratelimit
from upstash_redis import Redis

redis = Redis(url=UPSTASH_REDIS_URL, token=UPSTASH_REDIS_TOKEN)
ratelimit = Ratelimit(
    redis=redis,
    limiter=Ratelimit.sliding_window(60, "60 s"),  # 60 requests per minute
    prefix="verity_api"
)
```

---

## 🔧 Troubleshooting Common Issues

### API Not Responding

1. **Check Railway status**: https://railway.app/status
2. **View logs**: `railway logs` or Railway dashboard
3. **Check health endpoint**: `curl https://your-api.railway.app/health`
4. **Restart service**: Railway dashboard → Deployments → Redeploy

### High Latency

1. **Check AI provider status**: OpenAI, Anthropic status pages
2. **Review Supabase metrics**: Slow queries?
3. **Check Redis connection**: Upstash console for latency
4. **Scale up**: Add more replicas in Railway

### Rate Limit Errors (429)

1. **Check usage**: Dashboard → API Usage
2. **Upgrade plan**: Higher rate limits
3. **Implement backoff**: Retry with exponential backoff

---

## 📋 Production Checklist

### Before Going Live

- [ ] Set all environment variables in Railway
- [ ] Configure custom domain with SSL
- [ ] Set up health check endpoint
- [ ] Enable 2+ replicas for redundancy
- [ ] Configure uptime monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Test rate limiting works correctly
- [ ] Verify database connections are pooled
- [ ] Set up Supabase database backups

### Ongoing Maintenance

- [ ] Review logs weekly for errors
- [ ] Check performance metrics
- [ ] Update dependencies monthly
- [ ] Test backup restoration quarterly
- [ ] Review and rotate API keys

---

## 🌍 Optional: Multi-Region Deployment

For global users, deploy to multiple regions:

### Railway Regions
- `us-west1` (Oregon, USA)
- `us-east1` (Virginia, USA)
- `eu-west1` (Amsterdam, Netherlands)
- `asia-east1` (Tokyo, Japan)

### DNS-Based Load Balancing

Use Cloudflare or AWS Route 53 for geo-based routing:

```
api.veritysystems.app → Cloudflare
  → us-west.railway.app (Americas)
  → eu-west.railway.app (Europe)
  → asia-east.railway.app (Asia)
```

---

## 📞 Support Escalation

| Issue | Contact |
|-------|---------|
| Railway outage | status.railway.app, Railway Discord |
| Supabase issues | status.supabase.com, support@supabase.io |
| Upstash Redis | Upstash support portal |
| API bugs | github.com/verity-systems/issues |

---

## Quick Commands Reference

```bash
# Check API health
curl https://veritysystems-production.up.railway.app/health

# View Railway logs
railway logs --tail

# Deploy manually
railway up

# Check environment
railway variables

# Connect to Railway shell
railway shell
```

---

*Last updated: January 2025*
