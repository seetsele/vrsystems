Console logs and TODO/FIXME report
=================================

Generated: automatic scan

This report lists occurrences of `console.log`, `TODO`, and `FIXME` across the repository to help prioritize cleanup.

- Purpose: create a minimal inventory so we can triage and fix or convert to structured logging.

Summary:

- public/index.html: service worker registration uses console.log(e) (should use logger or swallow error) 
- public/assets/js/verity-fallback.js: converted console logs to (window.verityLogger||console).info/warn ✅
- public/sw.js: still uses internal verityLogger for service worker scope; acceptable (info/warn used) ✅
- public/assets/js/verity-core.js, verity-api-v6.js: converted many logs to verityLogger.info/debug ✅
- public/assets/js/main-v2.js: converted startup logs to verityLogger.info ✅
- public/assets/js/verify.js and verify-plus.js: converted API connection logs to verityLogger.info/warn ✅
- generate-pdf.js: switched to node logger (`scripts/logger-node.js`) and replaced console logs ✅
- browser-extension scripts: still include console.log on some lifecycle events; suggest migrating these to a conditional debug logger in `browser-extension` when packaging for production. 

Next steps: perform a repo sweep to convert remaining production-unsafe console.log occurrences (public assets and extension) and optionally add a build-time step to remove debug logging. (CI can run the linter to flag console.* usage.)
