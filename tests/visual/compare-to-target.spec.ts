import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import pixelmatch from 'pixelmatch';
import { PNG } from 'pngjs';

const targetFile = path.resolve(__dirname, 'targets', 'desktop-target.png');

// This test only runs if the CI/dev uploads a target screenshot at tests/visual/targets/desktop-target.png
// It compares a fresh screenshot of the desktop renderer to the target using pixelmatch.

test('compare desktop renderer to provided target screenshot', async ({ page }) => {
  test.skip(!fs.existsSync(targetFile), 'No target screenshot provided - skipping visual target comparison');

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

  // If target exists, read its dimensions and set page viewport to match so screenshots align
  const targetBuf = fs.readFileSync(targetFile);
  const targetImg = PNG.sync.read(targetBuf);
  await page.setViewportSize({ width: targetImg.width, height: targetImg.height });

  await page.goto(url);

  // wait for loading to finish
  await page.waitForSelector('#loading-screen', { state: 'hidden', timeout: 15000 });
  await page.waitForSelector('header, .search-bar', { timeout: 7000 });

  // capture viewport-only screenshot so dimensions match target
  const actualBuf = await page.screenshot({ fullPage: false });
  const actualImg = PNG.sync.read(actualBuf);

  // Ensure same dimensions - if not, fail with helpful message
  expect(actualImg.width).toBe(targetImg.width);
  expect(actualImg.height).toBe(targetImg.height);

  const diff = new PNG({ width: actualImg.width, height: actualImg.height });
  const diffPixels = pixelmatch(targetImg.data, actualImg.data, diff.data, actualImg.width, actualImg.height, { threshold: 0.12 });
  const percent = diffPixels / (actualImg.width * actualImg.height);

  // Tolerance: allow up to 2% pixel difference by default
  expect(percent).toBeLessThan(0.02);

  // Optionally write the diff image to help debugging when it fails
  const outDir = path.resolve(__dirname, '..', '..', 'tests', 'visual', 'target-diffs');
  try { fs.mkdirSync(outDir, { recursive: true }); } catch (e) {}
  fs.writeFileSync(path.join(outDir, `diff-${Date.now()}.png`), PNG.sync.write(diff));
});