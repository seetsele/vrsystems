#!/usr/bin/env bash
# Create a PR using GitHub CLI if available.
if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install GitHub CLI or create PR via web UI: https://github.com/<owner>/<repo>/pull/new/feature/runner-integration"
  exit 1
fi

BRANCH=${1:-feature/runner-integration}
BASE=${2:-main}
TITLE=${3:-"Feature: runner integration and hardening"}
BODY=${4:-"Implements runner integration, Celery worker, webhook signing, Alembic skeleton, Grafana import, and CI improvements."}

gh pr create --base "$BASE" --head "$BRANCH" --title "$TITLE" --body "$BODY"
