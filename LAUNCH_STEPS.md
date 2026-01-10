# 🚀 Verity AI - Exact Launch Steps

> Last Updated: Session v10.4.0

---

## ✅ Pre-Launch Checklist

### 1. Environment Variables (Railway)

Set these in your Railway dashboard → Settings → Variables:

```env
# Required API Keys (minimum 1 for basic operation)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
GROQ_API_KEY=gsk_...
PERPLEXITY_API_KEY=pplx-...

# OAuth (for Google/GitHub login)
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
GITHUB_CLIENT_ID=Ov...
GITHUB_CLIENT_SECRET=...

# Email Service (Resend)
RESEND_API_KEY=re_...
FROM_EMAIL=verify@yourdomain.com

# Security
JWT_SECRET=your-256-bit-secret

# AWS (optional, for LocalStack in dev)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

---

### 2. Git Commands

```powershell
# From project root
cd c:\Users\lawm\Desktop\verity-systems

# Check status
git status

# Stage all changes
git add .

# Commit with version tag
git commit -m "v10.4.0: Mobile app redesign + chatbot theme unification

- Updated mobile HomeScreen, VerifyScreen, ToolsScreen to match test website
- Created centralized theme (colors.ts) with amber/gold palette
- Updated desktop chatbot colors from cyan to amber
- Updated website chatbot component with test site styling
- All platforms now use consistent #f59e0b / #fbbf24 amber theme
- Matches reference: https://vrsystemss.vercel.app/index-v2-test.html"

# Push to main
git push origin main

# Create release tag
git tag -a v10.4.0 -m "Mobile redesign + unified amber theme"
git push origin v10.4.0
```

---

### 3. Backend Deployment (Railway)

Railway auto-deploys from main branch. After pushing:

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Wait for build to complete (~2-3 min)
3. Verify deployment at: `https://veritysystems-production.up.railway.app/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "10.4.0",
  "providers": ["openai", "anthropic", "google", "groq", "perplexity"]
}
```

---

### 4. Frontend Deployment (Vercel)

Vercel auto-deploys from main branch. After pushing:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Wait for build to complete (~1-2 min)
3. Verify at: `https://vrsystemss.vercel.app/`

---

### 5. Mobile App Build

```powershell
# Navigate to mobile app
cd verity-mobile

# Install dependencies
npm install

# iOS (requires Mac)
npx expo run:ios

# Android
npx expo run:android

# Build for production
npx eas build --platform all
```

---

### 6. Desktop App Build

```powershell
# Navigate to desktop app
cd desktop-app

# Install dependencies
npm install

# Build for all platforms
npm run make

# Output will be in: desktop-app/out/make/
```

---

### 7. Browser Extension

```powershell
# Navigate to extension
cd browser-extension

# Load in Chrome:
# 1. Go to chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select the browser-extension folder

# For production:
# 1. Zip the browser-extension folder
# 2. Upload to Chrome Web Store
```

---

## 🧪 Testing Checklist

### API Endpoints
- [ ] `GET /health` - Returns healthy status
- [ ] `POST /v3/verify` - Returns verification result
- [ ] `POST /v3/deep-verify` - Returns deep analysis
- [ ] `POST /oauth/google` - OAuth flow works
- [ ] `POST /oauth/github` - OAuth flow works

### Website Pages
- [ ] Home page loads with amber theme
- [ ] Verify page accepts claims
- [ ] Tools page shows all tools
- [ ] Chatbot appears bottom-right
- [ ] Mobile responsive works

### Mobile App
- [ ] HomeScreen matches test site
- [ ] VerifyScreen accepts input
- [ ] ToolsScreen shows grid layout
- [ ] Navigation works smoothly

### Desktop App
- [ ] Window opens correctly
- [ ] Chatbot uses amber theme
- [ ] Verification works
- [ ] System tray works

### Browser Extension
- [ ] Popup opens with amber styling
- [ ] Quick verify works
- [ ] Context menu appears

---

## 🎨 Theme Reference

All platforms use these colors:

| Token | Value | Usage |
|-------|-------|-------|
| bg | `#0a0a0b` | Main background |
| bgCard | `#111113` | Card backgrounds |
| bgElevated | `#18181b` | Elevated elements |
| amber | `#f59e0b` | Primary accent |
| amberLight | `#fbbf24` | Gradient end |
| green | `#10b981` | Success/verified |
| red | `#ef4444` | Error/false |
| textPrimary | `#fafafa` | Primary text |
| textSecondary | `#a3a3a3` | Secondary text |
| textMuted | `#525252` | Muted/placeholder |

---

## 📱 Platform Status

| Platform | Status | Notes |
|----------|--------|-------|
| Website | ✅ Ready | Vercel deployment |
| Backend API | ✅ Ready | Railway deployment |
| Mobile App | ✅ Ready | Expo/EAS build |
| Desktop App | ✅ Ready | Electron Forge |
| Browser Extension | ✅ Ready | Chrome Web Store |
| Chatbot (Web) | ✅ Ready | Embedded component |
| Chatbot (Desktop) | ✅ Ready | IPC renderer |

---

## 🚨 Emergency Rollback

If issues occur after launch:

```powershell
# Revert to previous version
git revert HEAD
git push origin main

# Or checkout specific tag
git checkout v10.3.0
git push -f origin main
```

---

## 📞 Support Contacts

- **Railway Issues**: Check logs at railway.app/dashboard
- **Vercel Issues**: Check deployments at vercel.com/dashboard
- **API Keys**: Regenerate at provider dashboards

---

## ✨ Launch Complete!

Once all checks pass:

1. Update `PROJECT_STATUS.md` to reflect v10.4.0
2. Announce on social channels
3. Monitor Railway/Vercel analytics for first 24 hours
4. Collect user feedback

**Congratulations on the launch! 🎉**
