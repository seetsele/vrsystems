# Verity Systems - Complete Fix Guide

## 🚨 Current Status

| Feature | vrsystemss.vercel.app | veritysystems.app | Action Needed |
|---------|----------------------|-------------------|---------------|
| Google OAuth | ✅ Working | ⚠️ Cached | Purge Vercel cache |
| GitHub OAuth | ✅ Working | ⚠️ Cached | Purge Vercel cache |
| Email Sign-up | ⚠️ SMTP needed | ⚠️ SMTP needed | Configure in Supabase |
| Waitlist | ✅ Working | ⚠️ Cached | Purge Vercel cache |
| Stripe | ✅ Configured | ✅ Configured | None |

---

## 1. 📧 FIX EMAIL SIGN-UP/SIGN-IN

The error "Error sending confirmation email" means Supabase needs email settings configured.

### Option A: Quick Fix (Disable Email Confirmation)
1. Go to https://supabase.com/dashboard
2. Select project: `zxgydzavblgetojqdtir`
3. Navigate to **Authentication** → **Providers** → **Email**
4. **DISABLE "Confirm email"** toggle
5. Click **Save**

Users will now sign up immediately without email verification.

### Option B: Production Fix (Configure SMTP)
1. Go to Supabase Dashboard → **Project Settings** → **Auth**
2. Scroll to **SMTP Settings** → Click **Enable Custom SMTP**
3. Enter your SMTP provider details:

**Recommended Providers:**
- **Resend.com** (Free tier: 3,000 emails/month)
- **SendGrid** (Free tier: 100 emails/day)
- **Mailgun** (Free tier: 5,000 emails/month)

Example Resend configuration:
```
Host: smtp.resend.com
Port: 465
Username: resend
Password: re_YOUR_API_KEY
Sender email: noreply@veritysystems.app
```

---

## 2. 🔄 PURGE CACHE FOR CUSTOM DOMAIN

### ❌ Name.com Has NO Cache
Name.com is a **DNS registrar only**. It routes traffic but doesn't cache anything.

### ✅ Where the Cache Lives: Vercel
Your files are cached on Vercel's global edge network.

### How to Purge Vercel Cache:
1. Go to https://vercel.com/dashboard
2. Click your project (verity-systems or similar)
3. Go to **Settings** → **Data Cache** (or **Deployments**)
4. Click **"Purge Cache"** or trigger a redeploy

### Force Redeploy Method:
```powershell
cd c:\Users\lawm\Desktop\verity-systems
git commit --allow-empty -m "Force redeploy"
git push
```

---

## 3. 🌐 WHAT IS A CDN?

**CDN = Content Delivery Network**

### Simple Explanation:
Imagine your website is a pizza restaurant:
- **Without CDN**: Every customer drives to one central location (slow for far customers)
- **With CDN**: You have kitchens worldwide, pizzas are pre-made nearby (fast delivery!)

### Your CDN Setup:
```
User in Tokyo     → Vercel Edge Server (Tokyo)     → Fast load! 🚀
User in London    → Vercel Edge Server (London)    → Fast load! 🚀
User in New York  → Vercel Edge Server (New York)  → Fast load! 🚀
```

### Your Infrastructure:
| Service | Role |
|---------|------|
| **Vercel** | CDN + Hosting (caches & serves your files globally) |
| **Name.com** | DNS only (tells browsers where to find veritysystems.app) |
| **Supabase** | Database + Auth (stores data, handles logins) |
| **Railway** | API Server (runs Python backend) |

---

## 4. 💳 STRIPE INTEGRATION

### Current Status: ✅ CONFIGURED

Your Stripe test key is already set in [checkout.html](public/checkout.html):
```javascript
const STRIPE_PUBLISHABLE_KEY = 'pk_test_51Sj7QP9HThAyZpOK...';
```

### To Test Stripe:
1. Go to `/checkout.html`
2. Use test card: `4242 4242 4242 4242`
3. Any future expiry date, any CVC

### For Production:
1. Go to Stripe Dashboard → Developers → API Keys
2. Copy your **Publishable key** (starts with `pk_live_`)
3. Replace the test key in checkout.html
4. Also update the secret key in Railway environment variables

---

## 5. 📝 WAITLIST FIX

### How Waitlist Works:
1. User enters email
2. Email saved to `newsletter_subscribers` table in Supabase
3. Count displayed is 2847 (base) + actual signups

### Required Database Setup:
Run this SQL in Supabase SQL Editor if table doesn't exist:

```sql
-- Create newsletter table
CREATE TABLE IF NOT EXISTS public.newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.newsletter_subscribers ENABLE ROW LEVEL SECURITY;

-- Allow anyone to insert (for waitlist signup)
CREATE POLICY "Anyone can subscribe" ON public.newsletter_subscribers
    FOR INSERT WITH CHECK (true);

-- Grant permissions
GRANT INSERT ON public.newsletter_subscribers TO anon, authenticated;
```

---

## 6. 🧪 TEST EVERYTHING

Visit these URLs to test all features:

| Page | URL | What to Test |
|------|-----|--------------|
| System Test | `/system-test.html` | All services diagnostic |
| Auth Test | `/auth-test.html` | Login methods |
| Waitlist | `/waitlist.html` | Email signup |
| Checkout | `/checkout.html` | Stripe payments |
| API Test | `/api-test.html` | API endpoints |

### Recommended Test Order:
1. **https://vrsystemss.vercel.app/system-test.html** (working version)
2. Verify all green checkmarks
3. Purge Vercel cache for custom domain
4. Test **https://www.veritysystems.app/system-test.html**

---

## 7. ⚡ QUICK ACTIONS CHECKLIST

- [ ] **Fix email auth**: Disable confirmation in Supabase OR configure SMTP
- [ ] **Purge Vercel cache**: Vercel Dashboard → Settings → Purge Cache (or run `./scripts/purge_vercel_cache.sh`)
- [ ] **Test Stripe**: Visit /checkout.html with a test card
- [ ] **Run diagnostics**: Visit /system-test.html
- [ ] **Verify waitlist**: Try signing up on /waitlist.html
- [ ] **Create a public download page**: `/download.html` (Added)
- [ ] **Publish browser extension**: Use `scripts/publish_extension.sh` and Chrome Web Store
- [ ] **Publish desktop installers**: Upload installers to `releases/<version>/` and run `scripts/publish_desktop_release.sh`
- [ ] **Publish mobile apps**: Use App Store Connect and Play Console with listings in `/store_listings/`
---

## 8. 📞 SUPPORT CONTACTS

| Issue | Solution |
|-------|----------|
| Supabase Auth | https://supabase.com/docs/guides/auth |
| Vercel Caching | https://vercel.com/docs/edge-network/caching |
| Stripe Testing | https://stripe.com/docs/testing |

---

*Last Updated: Auto-generated guide*
