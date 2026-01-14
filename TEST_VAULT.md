Test Vault
==========

This repository records test results into `test-vault/` for historical tracking.

- Desktop Jest tests: `desktop-app/scripts/record-results.js` writes JSON files into `test-vault/` (e.g., `jest-2026-01-14T...json`).
- CI uploads `test-vault` as an artifact on each push/PR touching `desktop-app/` using the `Desktop Tests` workflow.

How to run locally and record results:

1. From `desktop-app`:
   - npm run test:ci
   - This runs Jest (json output) and records into the repository `test-vault/` directory with a timestamped file.

2. For Python tests (suggested): run pytest with `--junitxml=path` and add a small script to convert or move the file into `test-vault/`.

Notes:
- The vault files are JSON and include a `meta` field (timestamp, node version, cwd) and the raw test runner JSON.
- Artifacts are uploaded by CI for review.
