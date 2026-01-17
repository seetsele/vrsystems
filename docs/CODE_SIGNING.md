# Code signing & notarization (Windows + macOS)

Windows (MSI / EXE)
- Obtain an EV Code Signing certificate from a CA (DigiCert, Sectigo, etc.).
- Use `electron-builder` with `win` target and configure `win.sign` with certificate details or use `signtool.exe` to sign produced artifacts.

macOS
- Enrol in Apple Developer Program.
- Use `electron-builder` with `mac` target and provide `APPLE_ID`, `APPLE_ID_PASSWORD`, and a provisioning profile for notarization.
- Run `xcrun altool --notarize-app` or rely on electron-builder notarize step.

CI notes
- Store signing credentials in secure secrets (GitHub Secrets or environment vault).
- Use self-hosted macOS runner for mac notarization or an external notarization service.

Verification
- After signing, verify signatures: `codesign --verify` (mac) and `signtool verify` (windows).
