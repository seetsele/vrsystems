# Supabase Authentication Setup for Verity Systems

## Current Status

The Supabase client is now properly initialized and working. Authentication functions (sign up, sign in, OAuth) are ready to use, but **OAuth providers need to be configured in your Supabase dashboard**.

## Email/Password Authentication

Email/password authentication is **already working**. Users can:
- Sign up with email and password
- Sign in with email and password  
- Reset password via email

## Setting Up OAuth Providers

### Google OAuth Setup

1. **Go to your Supabase Dashboard**: https://supabase.com/dashboard/project/zxgydzavblgetojqdtir

2. **Navigate to**: Authentication → Providers → Google

3. **Enable Google** and configure:

   **Client ID and Client Secret:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create OAuth 2.0 Client ID (Web application)
   - Add authorized origins:
     ```
     https://www.veritysystems.app
     https://vrsystemss.vercel.app
     ```
   - Add authorized redirect URIs:
     ```
     https://zxgydzavblgetojqdtir.supabase.co/auth/v1/callback
     ```
   - Copy Client ID and Client Secret to Supabase

4. **Save** the configuration

### GitHub OAuth Setup

1. **Go to your Supabase Dashboard**: https://supabase.com/dashboard/project/zxgydzavblgetojqdtir

2. **Navigate to**: Authentication → Providers → GitHub

3. **Enable GitHub** and configure:

   **Client ID and Client Secret:**
   - Go to [GitHub Developer Settings](https://github.com/settings/developers)
   - Click "New OAuth App"
   - Fill in:
     - **Application name**: Verity Systems
     - **Homepage URL**: https://www.veritysystems.app
     - **Authorization callback URL**: `https://zxgydzavblgetojqdtir.supabase.co/auth/v1/callback`
   - After creating, copy Client ID
   - Generate and copy Client Secret
   - Paste both into Supabase

4. **Save** the configuration

## Configuring Redirect URLs

1. **Go to your Supabase Dashboard**

2. **Navigate to**: Authentication → URL Configuration

3. **Site URL**: Set to your primary domain
   ```
   https://www.veritysystems.app
   ```

4. **Redirect URLs** (add all of these):
   ```
   https://www.veritysystems.app/**
   https://vrsystemss.vercel.app/**
   https://veritysystems.app/**
   http://localhost:3000/**
   ```

5. **Save** the configuration

## Testing Authentication

### Test via Auth Debug Page

Visit: https://vrsystemss.vercel.app/auth-test.html

This page shows:
- ✅ Supabase connection status
- OAuth test buttons (Google/GitHub)
- Email sign up/sign in test
- Current session status

### Test via Main Auth Page

Visit: https://vrsystemss.vercel.app/auth.html

- Click "Google" or "GitHub" buttons
- If OAuth is configured correctly, you'll be redirected to the provider
- After authentication, you'll be redirected to the dashboard

## Troubleshooting

### "Provider not enabled" Error
- OAuth provider is not enabled in Supabase dashboard
- Go to Authentication → Providers and enable the provider

### "Invalid redirect_uri" Error
- The callback URL in your OAuth provider settings doesn't match
- Make sure you're using: `https://zxgydzavblgetojqdtir.supabase.co/auth/v1/callback`

### "Auth session missing" Error
- This is normal when not logged in
- After successful login, this error will not appear

### Sign up not working
- Check if email confirmation is required in Supabase
- Go to Authentication → Settings and check "Enable email confirmations"

### Forms don't respond
- Check browser console for JavaScript errors
- Ensure Supabase CDN is loaded (should see "✅ Supabase client initialized successfully")

## Supabase Project Details

- **Project URL**: https://zxgydzavblgetojqdtir.supabase.co
- **Dashboard**: https://supabase.com/dashboard/project/zxgydzavblgetojqdtir
- **Auth Callback**: https://zxgydzavblgetojqdtir.supabase.co/auth/v1/callback

## Waitlist Functionality

The waitlist saves emails to the `newsletter_subscribers` table in Supabase. Make sure:
1. The table exists (run the schema from `database/supabase-schema.sql`)
2. RLS policies allow anonymous inserts
3. The anon key has INSERT permission on the table

---

*Last updated: January 12, 2026*
