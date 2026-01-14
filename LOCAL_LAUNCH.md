# Launching All Apps Locally

This document explains how to launch the Verity apps locally for testing.

Prerequisites
- Node.js (>=18), npm
- Windows PowerShell (or Git Bash)
- Optional: Xcode / Android Studio for native mobile builds

Quick one-command (PowerShell):

```powershell
cd C:\Users\lawm\Desktop\verity-systems\scripts
.\launch_local.ps1 -OpenChromeExtensions
```

What this does:
- Starts a static server for the PWA at http://localhost:3001/
- Starts the Electron desktop app (Verity)
- Starts the Expo dev server for mobile (verity-mobile)
- Opens the Chrome extensions page so you can "Load unpacked" the folder `browser-extension/chrome` if you want to test the extension locally

Manual steps (detailed):
1. Serve PWA locally:
   ```powershell
   cd public
   npx http-server -p 3001
   # open http://localhost:3001 in your browser
   ```

2. Start Desktop (Electron):
   ```powershell
   cd desktop-app
   npm ci
   npx electron .
   ```

3. Start Mobile (Expo):
   ```powershell
   cd verity-mobile
   npm ci
   npx expo start --tunnel
   ```

4. Load Browser Extension (dev):
   - Open Chrome → `chrome://extensions`
   - Enable "Developer mode"
   - Click "Load unpacked" → Select `browser-extension/chrome/`

Notes & Troubleshooting
- If `npx` fails for `electron` or `expo`, ensure Node and npm are installed and on PATH.
- To stop servers, cancel their terminal windows with CTRL+C.
- Expo will show a QR code for mobile testing in the terminal.
