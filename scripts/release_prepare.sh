#!/usr/bin/env bash
set -euo pipefail

echo "Release prepare script — builds desktop, extension, and mobile artifacts (templates)."

# Desktop (Electron) build (requires electron-builder & config in desktop-app/package.json)
echo "Building desktop app (Windows/Mac) — uncomment below to run"
# (cd desktop-app && npm ci && npm run build && npx electron-builder --win --mac)

# Browser extension: package manifest into ZIP
echo "Packaging browser extension into releases/verity-extension.zip"
mkdir -p releases
cd browser-extension/chrome || exit 0
zip -r ../../releases/verity-extension.zip . || true
cd - >/dev/null || true

# Mobile (Expo) build (commented; requires Expo credentials)
echo "Mobile build: uncomment expo build commands when ready"
# cd verity-mobile && npm ci && npx expo prebuild && npx eas build --platform all

echo "Release artifacts prepared (some steps are templates; fill credentials to run)."
