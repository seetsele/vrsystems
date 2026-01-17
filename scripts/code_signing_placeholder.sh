#!/usr/bin/env bash
echo "Code signing / notarization placeholder"
echo "This script is a template for CI. Fill signing identities and credentials in CI secrets."

if [ ! -d "build" ]; then
  echo "No build directory found. Run your build first." >&2
  exit 1
fi

echo "Signing artifacts in build/ (placeholder). Use codesign (macOS) or signtool (Windows)."
