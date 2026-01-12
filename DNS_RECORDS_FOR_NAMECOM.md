# DNS Records for name.com

## Domain: veritysystems.app

Add these 3 records at: https://www.name.com/account/domain/details/veritysystems.app#dns

---

### Record 1: DKIM (TXT)
| Field | Value |
|-------|-------|
| **Type** | TXT |
| **Host** | `resend._domainkey` |
| **Answer/Value** | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQClaJorTqvRB19E/nwO3bOB+3WhGTdqxXO7hyVZRRttfX8ifcXV2/G0OI//b1h61hm53GlH5tz4viBwsZrzLa4IYAni9jWHh41yCWy7LS61RDkkDlkgadxZFaal+/AbfYUAcxSPAnJ3pq1jgjdA/k6+6vcQxNYGws+rN2i/sjVZGwIDAQAB` |
| **TTL** | Auto (or 3600) |

---

### Record 2: MX (for send subdomain)
| Field | Value |
|-------|-------|
| **Type** | MX |
| **Host** | `send` |
| **Answer/Value** | `feedback-smtp.eu-west-1.amazonses.com` |
| **Priority** | `10` |
| **TTL** | 60 (or Auto) |

---

### Record 3: SPF (TXT for send subdomain)
| Field | Value |
|-------|-------|
| **Type** | TXT |
| **Host** | `send` |
| **Answer/Value** | `v=spf1 include:amazonses.com ~all` |
| **TTL** | 60 (or Auto) |

---

## After Adding Records

Wait 5-10 minutes, then verify by running this command in PowerShell:

```powershell
Invoke-RestMethod -Uri "https://api.resend.com/domains/ec1c8a9c-7d31-4781-811e-8866fd9c4028/verify" -Method Post -Headers @{ "Authorization" = "Bearer re_WYrQ8yQk_PCtzt9fe2XdV1hFJs7xgc7Pa" }
```

Or check status:
```powershell
$r = Invoke-RestMethod -Uri "https://api.resend.com/domains/ec1c8a9c-7d31-4781-811e-8866fd9c4028" -Headers @{ "Authorization" = "Bearer re_WYrQ8yQk_PCtzt9fe2XdV1hFJs7xgc7Pa" }
$r.records | Format-Table name, type, status
```
