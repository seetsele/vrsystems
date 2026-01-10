# OAuth Setup Guide

## Overview

Verity Systems supports OAuth 2.0 authentication with Google and GitHub. This guide walks you through setting up OAuth for your deployment.

---

## Google OAuth Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services > Credentials**

### Step 2: Configure OAuth Consent Screen

1. Click **OAuth consent screen** in the left sidebar
2. Select **External** user type
3. Fill in the required fields:
   - **App name**: Verity Systems
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Add scopes: `email`, `profile`, `openid`
5. Save and continue

### Step 3: Create OAuth Client ID

1. Go to **Credentials** > **Create Credentials** > **OAuth client ID**
2. Application type: **Web application**
3. Name: `Verity Web Client`
4. Add Authorized JavaScript origins:
   ```
   https://your-domain.com
   https://veritysystems-production.up.railway.app
   http://localhost:8000 (for development)
   ```
5. Add Authorized redirect URIs:
   ```
   https://your-domain.com/auth/google/callback
   https://veritysystems-production.up.railway.app/auth/google/callback
   http://localhost:8000/auth/google/callback
   ```
6. Click **Create**
7. Copy the **Client ID** and **Client Secret**

### Step 4: Add to Environment

Add to your `.env` or Railway environment variables:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

---

## GitHub OAuth Setup

### Step 1: Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**

### Step 2: Configure the App

Fill in the details:

| Field | Value |
|-------|-------|
| Application name | Verity Systems |
| Homepage URL | https://vrsystemss.vercel.app |
| Application description | AI-powered fact-checking platform |
| Authorization callback URL | https://veritysystems-production.up.railway.app/auth/github/callback |

### Step 3: Get Credentials

1. After creating, you'll see the **Client ID**
2. Click **Generate a new client secret**
3. Copy both values immediately (secret is only shown once)

### Step 4: Add to Environment

Add to your `.env` or Railway environment variables:

```env
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here
```

---

## Deploying to Railway

### Add Environment Variables in Railway

1. Go to your Railway project dashboard
2. Click on your service
3. Go to **Variables** tab
4. Add the following variables:

```
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
GITHUB_CLIENT_ID=<your_github_client_id>
GITHUB_CLIENT_SECRET=<your_github_client_secret>
REDIRECT_BASE=https://veritysystems-production.up.railway.app
```

5. The service will automatically redeploy

---

## Testing OAuth

### Test Google OAuth

1. Navigate to `/auth/google` on your deployment
2. You should be redirected to Google's login
3. After login, you'll be redirected back with a JWT token

### Test GitHub OAuth

1. Navigate to `/auth/github` on your deployment
2. You should be redirected to GitHub's authorization
3. After authorization, you'll be redirected back with a JWT token

---

## Troubleshooting

### "redirect_uri_mismatch" Error

Make sure the callback URL in your OAuth app settings **exactly matches** the URL your app is using. Common issues:
- HTTP vs HTTPS mismatch
- Trailing slash mismatch
- Port number differences

### "access_denied" Error

- Check that your OAuth consent screen is properly configured
- For Google, ensure the app is in "Testing" mode and your email is added as a test user, OR publish the app

### Token Exchange Fails

- Verify your client secret is correct
- Check that the authorization code hasn't expired (valid for ~10 minutes)

---

## Security Recommendations

1. **Never commit secrets** - Use environment variables
2. **Use HTTPS in production** - OAuth requires secure connections
3. **Rotate secrets periodically** - Regenerate client secrets every 6-12 months
4. **Limit scopes** - Only request the minimum permissions needed
5. **Implement PKCE** - Already implemented in our OAuth handler for added security

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /auth/google` | Initiate Google OAuth flow |
| `GET /auth/google/callback` | Handle Google OAuth callback |
| `GET /auth/github` | Initiate GitHub OAuth flow |
| `GET /auth/github/callback` | Handle GitHub OAuth callback |
| `POST /auth/logout` | Invalidate user session |
| `GET /auth/user` | Get current user info |
