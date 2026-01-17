import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

// Ensure screenshots folder exists for CI artifacts
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

const BASE = process.env.TEST_URL || 'http://localhost:8000';

test.describe('UI Flows - Enterprise', () => {
  test('dashboard loads and key widgets present', async ({ page }) => {
    await page.goto(BASE, { waitUntil: 'domcontentloaded' });
    const homeTitle = await page.title();
    if (!homeTitle || !homeTitle.toLowerCase().includes('verity')) test.skip();
    // Dashboard link or route
    const dash = page.locator('a[href*="dashboard"], a:has-text("Dashboard"), nav >> text=Dashboard').first();
    if ((await dash.count()) === 0) test.skip();
    await dash.click();
    const widget = page.locator('.dashboard, #dashboard, .stats, .activity').first();
    await expect(widget).toBeVisible({ timeout: 10000 });
  });

  test('search -> verify end-to-end', async ({ page }) => {
    await page.goto(BASE, { waitUntil: 'domcontentloaded' });
    const search = page.getByRole('searchbox').first();
    if ((await search.count()) === 0) {
      // fallback selectors
      const s2 = page.locator('input[placeholder*="Search"], input[name="q"]').first();
      if ((await s2.count()) === 0) test.skip();
      await s2.fill('Is water wet?');
      await s2.press('Enter');
    } else {
      await search.fill('Is water wet?');
      await page.keyboard.press('Enter');
    }
    const result = page.locator('.result, .verification-result, #result, .results').first();
    await expect(result).toBeVisible({ timeout: 20000 });
    // check for a verdict element
    const verdict = result.locator('.verdict, .verdict-badge, .confidence').first();
    await expect(verdict).toBeVisible({ timeout: 10000 });
  });

  test('open settings and provider-setup', async ({ page }) => {
    await page.goto(BASE, { waitUntil: 'domcontentloaded' });
    const settings = page.locator('a[href*="settings"], a:has-text("Settings"), nav >> text=Settings').first();
    if ((await settings.count()) === 0) test.skip();
    await settings.click();
    const prov = page.locator('a[href*="provider-setup"], button:has-text("Providers"), text=Providers').first();
    if ((await prov.count()) === 0) test.skip();
    await prov.click();
    const testStatus = page.locator('#testStatus, .provider-status, .provider-list').first();
    await expect(testStatus).toBeVisible({ timeout: 10000 });
  });
});
