import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const SCREENSHOT_DIR = path.resolve(process.cwd(), 'playwright-report', 'screenshots');
if (!fs.existsSync(SCREENSHOT_DIR)) fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status !== 'passed') {
    const safe = testInfo.title.replace(/[^a-z0-9\-]/gi, '_').slice(0, 120);
    const ts = Date.now();
    const filename = `${safe}_${ts}.png`;
    const metaName = `${safe}_${ts}.json`;
    await page.screenshot({ path: `playwright-report/screenshots/${filename}`, fullPage: true });
    const meta = {
      title: testInfo.title,
      status: testInfo.status,
      error: testInfo.error?.message || null,
      url: page.url(),
      timestamp: ts
    };
    fs.writeFileSync(path.join('playwright-report', 'screenshots', metaName), JSON.stringify(meta, null, 2));
  }
});

function fileUrlFor(relativePath: string) {
  const abs = path.resolve(__dirname, '..', '..', relativePath);
  const win = process.platform === 'win32';
  if (win) return 'file:///' + abs.replace(/\\\\/g, '/');
  return 'file://' + abs;
}

test.describe('Visual snapshots', () => {
  test('test-suite main view matches snapshot', async ({ page }) => {
    await page.goto('/test-suite.html');
    await page.waitForSelector('.container, #testList, h1', { timeout: 7000 });
    const main = await page.locator('body');
    expect(await main.screenshot()).toMatchSnapshot('test-suite-main.png');
  });

  test('desktop renderer search dropdown snapshot', async ({ page }) => {
    const url = fileUrlFor('desktop-app/renderer/index.html');
    // stub electron APIs and required modules so the renderer initializes correctly in a browser
    await page.addInitScript(() => {
      // minimal stubs for require(); some libraries expect electron-log
      // eslint-disable-next-line no-global-assign
      window.require = (name) => ({ info: () => {}, warn: () => {}, error: () => {} });
      window.verity = window.verity || {};
      window.verity.settings = window.verity.settings || { getAll: async () => ({}), save: async () => {} };
      window.verity.recent = window.verity.recent || { get: async () => [] };
      // Pause animations and hide dynamic backgrounds for stable screenshots
      const style = document.createElement('style');
      style.innerHTML = `*{animation:none!important;transition:none!important!important} .animated-bg, .orb, .glow-lines, .bg-noise { display:none!important }`;
      document.addEventListener('DOMContentLoaded', () => document.head.appendChild(style));
    });
    await page.goto(url);
    // wait for the renderer to finish its fake "initialization" (loading screen should hide)
    await page.waitForSelector('#loading-screen', { state: 'hidden', timeout: 10000 });
    await page.waitForSelector('.search-bar input', { timeout: 7000 });
    const input = await page.locator('.search-bar input');
    await input.click({ force: true });
    await input.fill('provider');
    // wait for dropdown animation
    await page.waitForTimeout(350);
    const dropdown = await page.locator('.search-results');
    expect(await dropdown.screenshot()).toMatchSnapshot('search-dropdown.png');
  });

  test('desktop renderer index snapshot', async ({ page }) => {
    const url = fileUrlFor('desktop-app/renderer/index.html');
    // stub electron modules so the renderer can initialize when opened as file://
    await page.addInitScript(() => {
      window.require = (name) => ({ info: () => {}, warn: () => {}, error: () => {} });
      window.verity = window.verity || {};
      window.verity.settings = window.verity.settings || { getAll: async () => ({}), save: async () => {} };
      window.verity.recent = window.verity.recent || { get: async () => [] };
      const style = document.createElement('style');
      style.innerHTML = `*{animation:none!important;transition:none!important!important} .animated-bg, .orb, .glow-lines, .bg-noise { display:none!important }`;
      document.addEventListener('DOMContentLoaded', () => document.head.appendChild(style));
    });
    await page.goto(url);
    await page.waitForSelector('#loading-screen', { state: 'hidden', timeout: 10000 });
    await page.waitForSelector('.app-root, .main-window, .container, header', { timeout: 10000 });
    const root = await page.locator('body');
    expect(await root.screenshot()).toMatchSnapshot('desktop-renderer.png');
  });
});