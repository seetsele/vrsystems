Target screenshot instructions

- Place the target screenshot you want to validate against in this directory:
  `tests/visual/targets/desktop-target.png`

- The Playwright test `tests/visual/compare-to-target.spec.ts` will automatically run and compare the renderer screenshot to the provided target when the file exists.

- Pixel diff tolerance is currently set to 2% (0.02). If the test fails, a diff image will be written to `tests/visual/target-diffs/`.

- For CI: attach your desired target screenshots to the repository (or provide them via an artifact download step before running tests) so the comparison can run on PRs or nightly builds.