# Contributing

Thanks for contributing — a few notes about repository hygiene and pre-commit hooks.

## Pre-commit hooks
We use Husky and lint-staged to run a staged console linter before commits. This prevents accidental `console.log` usage from being committed to production code.

- To run the same check locally: from the repo root run:

```bash
node scripts/find-console.js
```

- If you are committing intentionally (e.g., updating docs or examples) and need to bypass the pre-commit hook, you can use `--no-verify`:

```bash
git commit -m "message" --no-verify
```

Use bypasses sparingly and add a note in your commit message explaining why.

## Linter behavior
- The console linter scans relevant source paths (public, desktop-app, browser-extension, scripts, verity-mobile) for `console.log` and `console.debug` usage.
- The linter truncates very long matched lines to keep CI logs readable and returns exit code `2` when matches are found.

## Running tests
- Node unit tests for tooling can be run with:

```bash
npm run test:node
```

Thank you!
