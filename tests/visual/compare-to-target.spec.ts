import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import pixelmatch from 'pixelmatch';
import { PNG } from 'pngjs';

// Compare a stable region (header) of the desktop renderer to a provided header target screenshot.
const targetFile = path.resolve(__dirname, 'targets', 'desktop-target-header.png');

// This test only runs if the CI/dev uploads a header target screenshot
// It compares the header element only which is more stable across runs
test('compare desktop renderer header to provided target screenshot', async ({ page }) => {
  test.skip(!fs.existsSync(targetFile), 'No header target screenshot provided - skipping visual header comparison');

  // minimal stubs for electron APIs used by the renderer
  await page.addInitScript(() => {
    // eslint-disable-next-line no-global-assign
    window.require = (name) => ({ info: () => {}, warn: () => {}, error: () => {} });
    window.verity = window.verity || {};
    window.verity.settings = window.verity.settings || { getAll: async () => ({}), save: async () => {} };
    window.verity.recent = window.verity.recent || { get: async () => [] };
  });

  // open the renderer (file:// URL)
  const url = 'file://' + path.resolve(__dirname, '..', '..', 'desktop-app', 'renderer', 'index.html').replace(/\\/g, '/');

  await page.goto(url);

  // wait for loading to finish and header to be visible
  await page.waitForSelector('#loading-screen', { state: 'hidden', timeout: 15000 });
  const header = await page.waitForSelector('header', { timeout: 7000 });

  // capture header region screenshot
  const actualBuf = await header.screenshot();
  const actualImg = PNG.sync.read(actualBuf);

  // Read target
  const targetBuf = fs.readFileSync(targetFile);
  const targetImg = PNG.sync.read(targetBuf);

  // If dimensions differ, fail with guidance (user can update target if intentionally changed)
  expect(actualImg.width).toBe(targetImg.width);
  expect(actualImg.height).toBe(targetImg.height);

  const diff = new PNG({ width: actualImg.width, height: actualImg.height });
  const diffPixels = pixelmatch(targetImg.data, actualImg.data, diff.data, actualImg.width, actualImg.height, { threshold: 0.12 });
  const percent = diffPixels / (actualImg.width * actualImg.height);

  // Tolerance: allow up to 2% pixel difference by default
  expect(percent).toBeLessThan(0.02);

  // Write the diff image to help debugging when it fails
  const outDir = path.resolve(__dirname, '..', '..', 'tests', 'visual', 'target-diffs');
  try { fs.mkdirSync(outDir, { recursive: true }); } catch (e) {}
  fs.writeFileSync(path.join(outDir, `header-diff-${Date.now()}.png`), PNG.sync.write(diff));
});