# Observability: Sentry Setup (notes)

To collect crashes and errors in backend and desktop app, configure Sentry:

1. Create a Sentry project for `verity-backend` and `verity-desktop`.
2. Add `SENTRY_DSN` to `.env` and to GitHub Actions secrets.
3. Install SDKs:

- Python backend: `pip install sentry-sdk`
- Electron/Renderer: `npm install @sentry/electron`

Example (Python):

```py
import sentry_sdk
sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'))
```

Example (Electron main):

```js
const Sentry = require('@sentry/electron');
Sentry.init({ dsn: process.env.SENTRY_DSN });
```

Privacy: add a telemetry opt-in toggle in UIs and document in privacy policy.
