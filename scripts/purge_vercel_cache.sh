#!/usr/bin/env bash
set -euo pipefail

# Options to purge cache / redeploy
# Option A: Use vercel CLI to trigger a production deployment
#   vercel --prod
# Option B: Create an empty commit and push to trigger a new deployment
#   git commit --allow-empty -m "Purge cache" && git push

if command -v vercel >/dev/null 2>&1; then
  echo "Running vercel --prod (ensure you're in the project root and logged in)"
  vercel --prod --confirm
else
  echo "vercel CLI not found. Creating an empty commit instead to force redeploy."
  git commit --allow-empty -m "Force redeploy to purge cache"
  git push
fi

echo "Done."