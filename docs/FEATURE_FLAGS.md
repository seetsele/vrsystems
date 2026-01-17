# Feature Flags & Telemetry Opt-In

Use a feature-flag system (LaunchDarkly, Unleash, or simple DB-driven flags) for beta features.

Suggested minimal implementation
- Add a `feature_flags` table with `key`, `enabled`, `rollout_percent`.
- Add a `telemetry_opt_in` boolean on user settings and a UI toggle.
- Respect `telemetry_opt_in` before sending events to Sentry/analytics.

Example flags
- `beta_model_v2` — route some users to experimental model adapter
- `show_onboarding_modal` — toggle onboarding

Rollout
- Implement gradual rollout by `rollout_percent` and user-id hashing.
