# Data & Privacy Policy (Developer Notes)

This document summarises how Verity handles client data used for testing, telemetry, and model improvement.

Principles
- Consent-first: collect user data only with explicit consent or contractual allowance.
- Minimize: store only what is necessary for service operation and improvement.
- Anonymize: PII is removed or hashed before being used for model training or analytics.
- No sale: raw client data will not be sold to third parties.

Storage & Access
- Production data is stored in the configured database (see `DATABASE_URL`) and object storage as configured in deployment.
- Local test artifacts and generated pages are stored under `public/tests/` and `python-tools/logs/` for developer convenience.
- Access to production data is restricted via RBAC; logs and access are audited.

Feedback Loop for Model Improvement
- Labeled feedback (user corrections, moderation labels) is exported to a secure dataset for retraining.
- Dataset versions are tracked and stored separately from raw logs; training uses anonymized data.
- Retraining is done in private environments; no client-identifiable data is included without consent.

Retention & Deletion
- Data retention policies should be defined per environment; implement deletion endpoints for client data on request.

Security
- Encrypt data in transit (TLS) and at rest.
- Rotate keys, use secrets management (e.g., environment variables, secret stores), and limit access.

Audit & Compliance
- Keep an immutable audit trail for data accesses and changes.

If you need a customer-facing privacy policy, derive a simplified version from these notes and run it by legal.
