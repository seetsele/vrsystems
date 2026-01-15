import { test, expect } from '@playwright/test';
import path from 'path';

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
    });
    await page.goto(url);
    await page.waitForSelector('#loading-screen', { state: 'hidden', timeout: 10000 });
    await page.waitForSelector('.app-root, .main-window, .container, header', { timeout: 10000 });
    const root = await page.locator('body');
    expect(await root.screenshot()).toMatchSnapshot('desktop-renderer.png');
  });
});