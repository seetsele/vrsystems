# Verity Systems Email Setup Guide

## Overview

This guide covers setting up email for veritysystems.app:
1. **Sending Emails** (transactional) - Using Resend
2. **Email Forwarding** - Forward all emails to seetsele@veritysystems.app

---

## Part 1: DNS Records for Name.com

Add these records to your veritysystems.app domain at Name.com:

### Resend Email Sending (Required for transactional emails)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| TXT | `resend._domainkey` | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQClaJorTqvRB19E/nwO3bOB+3WhGTdqxXO7hyVZRRttfX8ifcXV2/G0OI//b1h61hm53GlH5tz4viBwsZrzLa4IYAni9jWHh41yCWy7LS61RDkkDlkgadxZFaal+/AbfYUAcxSPAnJ3pq1jgjdA/k6+6vcQxNYGws+rN2i/sjVZGwIDAQAB` | 3600 |
| CNAME | `send` | `feedback-smtp.eu-west-1.amazonses.com` | 3600 |
| TXT | `@` or root | `v=spf1 include:amazonses.com include:_spf.mx.cloudflare.net ~all` | 3600 |

---

## Part 2: Email Forwarding Options

### Option A: Cloudflare Email Routing (RECOMMENDED - Free)

1. **Transfer DNS to Cloudflare** (or keep at Name.com and use Cloudflare for email)
2. Go to Cloudflare Dashboard → Email → Email Routing
3. Add your domain `veritysystems.app`
4. Add routing rule:
   - **Catch-all**: `*@veritysystems.app` → `seetsele@veritysystems.app`
5. Cloudflare will provide MX records to add to your DNS

**Cloudflare MX Records:**
| Type | Name | Value | Priority |
|------|------|-------|----------|
| MX | `@` | `route1.mx.cloudflare.net` | 50 |
| MX | `@` | `route2.mx.cloudflare.net` | 47 |
| MX | `@` | `route3.mx.cloudflare.net` | 3 |

---

### Option B: ImprovMX (Free tier - 25 emails/day)

1. Go to https://improvmx.com
2. Sign up and add `veritysystems.app`
3. Create forward: `*@veritysystems.app` → `seetsele@veritysystems.app`
4. Add the MX records they provide:

**ImprovMX MX Records:**
| Type | Name | Value | Priority |
|------|------|-------|----------|
| MX | `@` | `mx1.improvmx.com` | 10 |
| MX | `@` | `mx2.improvmx.com` | 20 |
| TXT | `@` | `v=spf1 include:spf.improvmx.com ~all` | 3600 |

---

### Option C: ForwardEmail.net (Free & Open Source)

1. Go to https://forwardemail.net
2. Add domain and create forward
3. Add MX records:

| Type | Name | Value | Priority |
|------|------|-------|----------|
| MX | `@` | `mx1.forwardemail.net` | 10 |
| MX | `@` | `mx2.forwardemail.net` | 20 |
| TXT | `@` | `forward-email=seetsele@veritysystems.app` | 3600 |

---

## Part 3: Complete DNS Configuration

For best results, here's the complete DNS setup at Name.com:

```
# Email Forwarding (choose one service from above)
MX   @              route1.mx.cloudflare.net      (priority: 50)
MX   @              route2.mx.cloudflare.net      (priority: 47)  
MX   @              route3.mx.cloudflare.net      (priority: 3)

# Resend for sending emails
TXT  resend._domainkey  p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQClaJorTqvRB19E/nwO3bOB+3WhGTdqxXO7hyVZRRttfX8ifcXV2/G0OI//b1h61hm53GlH5tz4viBwsZrzLa4IYAni9jWHh41yCWy7LS61RDkkDlkgadxZFaal+/AbfYUAcxSPAnJ3pq1jgjdA/k6+6vcQxNYGws+rN2i/sjVZGwIDAQAB
CNAME send            feedback-smtp.eu-west-1.amazonses.com

# SPF Record (combine all services)
TXT  @              v=spf1 include:amazonses.com include:_spf.mx.cloudflare.net ~all

# Optional: DMARC for better deliverability
TXT  _dmarc         v=DMARC1; p=none; rua=mailto:seetsele@veritysystems.app
```

---

## Quick Start Steps

### If using Cloudflare (Recommended):

1. Sign up at cloudflare.com
2. Add veritysystems.app (you can keep DNS at Name.com, just enable Email Routing)
3. Go to Email → Email Routing → Enable
4. Add rule: `Catch-all *` → Forward to `seetsele@veritysystems.app`
5. Verify destination email
6. Add the MX records Cloudflare provides to Name.com
7. Done! All emails to `*@veritysystems.app` forward to seetsele

---

## Verification

After setup, test by sending an email to:
- `test@veritysystems.app`
- `hello@veritysystems.app`
- `support@veritysystems.app`

All should arrive at `seetsele@veritysystems.app`.

---

## Recommended Email Addresses to Create

Once forwarding is set up, you can use any address you want. Suggested:
- `hello@veritysystems.app` - General contact
- `support@veritysystems.app` - Customer support
- `api@veritysystems.app` - API/developer inquiries
- `billing@veritysystems.app` - Payment issues
- `security@veritysystems.app` - Security reports
- `admin@veritysystems.app` - Admin functions

All will forward to `seetsele@veritysystems.app`!

---

## Current API Keys

**Resend API Key:** `re_WYrQ8yQk_PCtzt9fe2XdV1hFJs7xgc7Pa`
**Resend Domain ID:** `ec1c8a9c-7d31-4781-811e-8866fd9c4028`

Once DNS is configured, verify domain in Resend dashboard:
https://resend.com/domains
