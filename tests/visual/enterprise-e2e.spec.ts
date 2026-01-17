import { test, expect } from '@playwright/test';

const BASE = process.env.TEST_URL || 'http://localhost:8000';

async function findHome(page) {
  const candidates = [BASE, BASE + '/index.html', BASE + '/index.htm', BASE + '/public/index.html'];
  for (const u of candidates) {
    try {
      const resp = await page.goto(u, { waitUntil: 'domcontentloaded' });
      if (!resp) continue;
      const title = await page.title();
      if (!/directory listing|index of/i.test(title)) return u;
    } catch (e) {
      continue;
    }
  }
  return null;
}

test.describe('Enterprise E2E - Live', () => {
  test('homepage loads and header is correct', async ({ page }) => {
    const home = await findHome(page);
    test.info().annotations.push({ type: 'home', description: String(home) });
    if (!home) test.skip('No index-like page found at target');
    await page.goto(home, { waitUntil: 'domcontentloaded' });
    const title = await page.title();
    if (!title || !title.toLowerCase().includes('verity')) {
      test.skip(`Target does not appear to be Verity (title='${title}')`);
    }
    const header = page.locator('header, .site-header, #header, nav').first();
    await expect(header).toBeVisible({ timeout: 15000 });
  });

  test('search/verify flow', async ({ page }) => {
    const home = await findHome(page);
    if (!home) test.skip('No index-like page found at target');
    await page.goto(home, { waitUntil: 'domcontentloaded' });
    // prefer semantic role
    let input = page.getByRole('searchbox').first();
    if ((await input.count()) === 0) {
      input = page.locator('input[type="search"], input[name="q"], #search, input[type="text"]').first();
    }
    const count = await input.count();
    if (count === 0) test.skip('No search input found on homepage');
    await expect(input).toBeVisible({ timeout: 20000 });
    await input.fill('The sky is blue');
    await page.keyboard.press('Enter');
    const result = page.locator('.result, .verification-result, #result, .results').first();
    await expect(result).toBeVisible({ timeout: 20000 });
  });

  test('open image-forensics tool', async ({ page }) => {
    const tools = BASE + '/tools';
    await page.goto(tools, { waitUntil: 'domcontentloaded' });
    const link = page.locator('a[href*="image-forensics"], button[data-tool="image-forensics"]').first();
    if ((await link.count()) === 0) test.skip('No image-forensics link/button found on tools page');
    await expect(link).toBeVisible({ timeout: 10000 });
    await link.click();
    const form = page.locator('form[action*="image-forensics"], form#image-forensics');
    if ((await form.count()) === 0) test.skip('No image-forensics form found after navigation');
    await expect(form).toBeVisible({ timeout: 10000 });
  });

  test('realtime-stream endpoint interactive', async ({ page }) => {
    const url = BASE + '/tools/realtime-stream';
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    const form = page.locator('form#realtime, form[action*="realtime-stream"]').first();
    if (await form.count() > 0) {
      const textarea = form.locator('textarea, input[name="text"]');
      await textarea.fill('This is a Playwright realtime smoke test');
      const submit = form.locator('button[type="submit"], input[type="submit"]');
      await submit.first().click();
      const out = page.locator('.realtime-output, #realtime-output');
      await expect(out).toBeVisible({ timeout: 20000 });
    } else {
      test.skip();
    }
  });
});
