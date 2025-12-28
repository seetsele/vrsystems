# Verity Systems - Setup Checklist

## ✅ What's Working Now

- [x] LocalStack AWS mocks (S3, DynamoDB, SQS) - tested and working
- [x] Comet ML integration module - ready for API key
- [x] Frontend UI with dark theme
- [x] Demo verification on homepage
- [x] Full verify page at `/verify.html`
- [x] Navigation updated with Verify link
- [x] Auth system with email/password

---

## 🔧 What YOU Need to Configure

### Priority 1: Supabase (Authentication & Database)

**Status: ❌ Not Configured**

1. Go to [supabase.com](https://supabase.com) and create a free project
2. Get your credentials from Project Settings → API:
   - `SUPABASE_URL` (looks like `https://abc123.supabase.co`)
   - `SUPABASE_ANON_KEY` (JWT token starting with `eyJ...`)

3. Update `public/assets/js/supabase-client.js`:
   ```javascript
   const SUPABASE_URL = 'https://YOUR-PROJECT.supabase.co';
   const SUPABASE_ANON_KEY = 'eyJ...your-anon-key...';
   ```

4. **Enable OAuth Providers** (optional but recommended):
   - In Supabase Dashboard → Authentication → Providers
   - Enable Google: Add your Google Cloud OAuth credentials
   - Enable GitHub: Add your GitHub OAuth app credentials

---

### Priority 2: Comet ML (ML Tracking)

**Status: ❌ API Key Missing**

1. Go to [comet.com](https://www.comet.com) and sign up (free tier available)
2. Go to Settings → API Keys → Generate new key
3. Add to your `.env` file:
   ```bash
   COMET_API_KEY=your-comet-api-key
   ```

---

### Priority 3: AI Provider Keys

Update your `.env` file with real API keys:

| Provider | Status | Get Key At |
|----------|--------|------------|
| Anthropic Claude | ❌ Empty | [console.anthropic.com](https://console.anthropic.com) |
| Groq | ⚠️ Placeholder | [console.groq.com](https://console.groq.com) |
| OpenAI | ⚠️ Placeholder | [platform.openai.com](https://platform.openai.com) |
| Perplexity | ✅ Has value | - |
| OpenRouter | ✅ Has value | - |
| Google Fact Check | ✅ Has value | - |

**Minimum Required for Demo**: At least ONE of Anthropic, Groq, or OpenAI

---

### Priority 4: Error Tracking (Optional)

Update `public/index.html` line 27:
```javascript
Honeybadger.configure({
    apiKey: 'YOUR_ACTUAL_HONEYBADGER_KEY',  // Get from app.honeybadger.io
    ...
});
```

---

## 🔐 OAuth Setup (For Social Login)

Your auth system supports OAuth via Supabase. To enable:

### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials
3. Set redirect URI: `https://YOUR-PROJECT.supabase.co/auth/v1/callback`
4. Add credentials to Supabase Dashboard → Auth → Providers → Google

### GitHub OAuth
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create new OAuth App
3. Set callback URL: `https://YOUR-PROJECT.supabase.co/auth/v1/callback`
4. Add credentials to Supabase Dashboard → Auth → Providers → GitHub

---

## 📁 Files You Need to Update

| File | What to Update |
|------|----------------|
| `.env` | All API keys (copy from `.env.example`) |
| `public/assets/js/supabase-client.js` | `SUPABASE_URL`, `SUPABASE_ANON_KEY` |
| `public/index.html` | Honeybadger API key (line 27) |

---

## 🧪 Test Your Setup

```bash
# Test AWS mocks + Comet ML
cd python-tools
python test_integrations.py

# Test API server
python api_server.py

# View frontend
# Open public/index.html in browser
```

---

## 📊 Current Features

| Feature | Page | Status |
|---------|------|--------|
| Homepage | `/index.html` | ✅ Working |
| Demo Verification | `/index.html#demo` | ✅ Working (needs API keys) |
| Full Verify Page | `/verify.html` | ✅ Working |
| Verify+ (Bulk) | `/verify-plus.html` | ✅ Working |
| Dashboard | `/dashboard.html` | ✅ Working (needs auth) |
| Sign In/Up | `/auth.html` | ✅ Working (demo mode) |
| Misinformation Map | `/misinformation-map.html` | ✅ Working |
| History | `/history.html` | ✅ Working |
| API Keys | `/api-keys.html` | ✅ Working |
| Billing | `/billing.html` | ✅ Working |

---

## 🚀 Quick Start Commands

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with your API keys
notepad .env  # or code .env

# 3. Install Python dependencies
pip install -r python-tools/requirements.txt

# 4. Test integrations
cd python-tools && python test_integrations.py

# 5. Start API server
python api_server.py
```

---

## ❓ Need Help?

- Supabase Docs: https://supabase.com/docs
- Comet ML Docs: https://www.comet.com/docs
- Anthropic Docs: https://docs.anthropic.com
- GitHub Education (free credits): https://education.github.com/pack
