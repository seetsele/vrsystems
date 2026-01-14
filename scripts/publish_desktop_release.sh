#!/usr/bin/env bash
set -euo pipefail

# Usage:
# 1) Install GitHub CLI and authenticate (gh auth login)
# 2) Put your built artifacts into ./releases/<version>/
# 3) Run: ./scripts/publish_desktop_release.sh v1.0.0 "Release title" "Release notes"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <tag> [title] [notes]"
  exit 1
fi
TAG="$1"
TITLE="${2:-$TAG}"
NOTES="${3:-Release $TAG}"
ASSETS_DIR="$(pwd)/releases/$TAG"

if [ ! -d "$ASSETS_DIR" ]; then
  echo "No assets found for $TAG in $ASSETS_DIR"
  exit 1
fi

echo "Creating GitHub release $TAG..."
gh release create "$TAG" "$ASSETS_DIR"/* -t "$TITLE" -n "$NOTES"

echo "Release created and assets uploaded."