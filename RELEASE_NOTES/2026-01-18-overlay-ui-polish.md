# Release notes — 2026-01-18

## feat/overlay-ui-polish

Summary:
- Added transparent, glassmorphism overlay prototypes for Desktop (Electron), Mobile (Expo/HTML prototype), and Browser Extension.
- Imported website typography and premium icons into overlay UIs to match site design language (JetBrains Mono for monospace, Inter/Newsreader for body/display).
- Implemented compact popout, clipboard quick-verify, and "open full report" actions for overlays.
- Polished renderer theme variables and button styles for closer pixel parity with the website.
- Added headless smoke tests (Puppeteer) for: verify page, desktop overlay, extension overlay injection, and mobile overlay flow. Screenshots saved under `desktop-app/test-results/`.

Notes:
- Pre-commit hooks block console.log in staged files; smoke scripts are now cleaned of `console.log` where necessary.
- Branch: `feat/overlay-ui-polish` — PR prepared.

Files of note:
- `desktop-app/overlay/*`
- `desktop-app/renderer/styles.css` (theme refinements)
- `desktop-app/scripts/*_smoke_test.js`
- `desktop-app/mobile_overlay/*`

Testing:
- Run `node ./desktop-app/scripts/ui_smoke_test.js` and check `desktop-app/test-results/` for artifacts.

Signed-off-by: Automated UI agent
