#!/usr/bin/env bash
set -euo pipefail

# Usage:
# 1) Install dependencies: npm i -g @google/webstore-upload-cli (or use similar)
# 2) Set env vars: EXTENSION_ID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN
# 3) Run: ./scripts/publish_extension.sh

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
EXT_DIR="$ROOT_DIR/browser-extension/chrome"
ZIP_PATH="/tmp/verity-extension.zip"

echo "Zipping extension..."
cd "$EXT_DIR"
zip -r "$ZIP_PATH" . -x "*.DS_Store"

# Example using webstore-upload (third-party). Fill environment variables as needed.
if command -v webstore >/dev/null 2>&1; then
  echo "Uploading to Chrome Web Store (requires credentials set in env vars)..."
  webstore upload --source "$ZIP_PATH" --extension-id "$EXTENSION_ID" --client-id "$CLIENT_ID" --client-secret "$CLIENT_SECRET" --refresh-token "$REFRESH_TOKEN"
  echo "Publishing..."
  webstore publish --extension-id "$EXTENSION_ID" --client-id "$CLIENT_ID" --client-secret "$CLIENT_SECRET" --refresh-token "$REFRESH_TOKEN"
else
  echo "webstore CLI not found. Please install @google/webstore-upload-cli or use another upload method."
  echo "ZIP created at: $ZIP_PATH"
fi

echo "Done."