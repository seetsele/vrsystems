# Token Rotation Guide

This document explains how to safely rotate the `TOKEN_SECRET` used by staging and production.

Steps:

1. Generate a new strong secret (recommended 32+ random bytes base64).
2. Deploy the new secret to staging behind a feature flag or on a single staging instance.
3. Use a short overlap period where both old and new secrets are accepted by the verification service.
   - To support overlap, update verification code to accept both `TOKEN_SECRET` values for a short period.
4. Issue new tokens signed with the new secret.
5. Revoke or expire old tokens (by shortening TTL or keeping a blacklist of revoked token `jti`).
6. Once all clients have migrated and old tokens expired, remove acceptance of the old secret.

Safe practices:
- Store secrets in a secrets manager (AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault).
- Do not commit secrets to Git.
- Rotate regularly and after any suspected compromise.
