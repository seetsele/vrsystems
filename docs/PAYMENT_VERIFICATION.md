# Payment / Stripe verification for staging

Steps to verify end-to-end payment flow in staging

1. Create a Stripe test account and get `STRIPE_PUBLISHABLE_KEY` and `STRIPE_SECRET_KEY`.
2. Add keys to CI as `STRIPE_SECRET_KEY` and to frontend env as `STRIPE_PUBLISHABLE_KEY`.
3. Use Stripe test cards (e.g., `4242 4242 4242 4242`) and webhook forwarding (Stripe CLI) to confirm backend handling.

Commands

```bash
# Start backend with STRIPE_SECRET_KEY in env
export STRIPE_SECRET_KEY=sk_test_...
python -m python-tools.api_server_v10

# Use Stripe CLI to forward webhooks
stripe listen --forward-to localhost:8000/webhook
```

Validation
- Verify successful charge objects are created in Stripe dashboard and the app records payment status.
- Add test to `python-tools` that fakes a webhook and checks DB insertion.
