# Release notes — 2026-01-22

## Browser Extension: Cluely-style overlay

- Added a floating Cluely-style HUD overlay with glassmorphism, top controls, and a chat-style input.
- Matched typography to site premium fonts (`Plus Jakarta Sans` / `Inter`) for visual parity.
- Added a popup `Overlay` toggle that sends `{ action: 'toggleOverlay' }` to the active tab.
- Added click-outside-to-close behavior, keyboard shortcut `Ctrl/Cmd+Enter` for quick send, and UI polish (backdrop, handle, animations).

Files changed:
- `browser-extension/chrome/content.css`
- `browser-extension/chrome/content.js`
- `browser-extension/chrome/popup.js`

Notes: Run `node browser-extension/scripts/extension_smoke_test.js` to capture screenshots for verification.
