import { test, expect } from '@playwright/test';

test('Image Analysis flow loads from dashboard', async ({ page }) => {
  await page.goto('/dashboard.html');
  // Click the Image Analysis action
  await page.click('a[href*="verify.html?type=image"]');
  await expect(page).toHaveURL(/verify.html\?type=image/);
  // The Image tab is present; on default tiers it's locked (PRO) 
  const imageTab = page.locator('button[data-type="image"]');
  // The image tab exists and should be locked for default test tier
  await expect(imageTab).toHaveClass(/locked/);
  await expect(imageTab.locator('.lock')).toContainText(/PRO|ENT|PROF/i);
});

test('Real-Time Stream page loads and shows stream header', async ({ page }) => {
  await page.goto('/realtime-stream.html');
  // The page uses 'Live Stream' as the heading text
  await expect(page.locator('h1')).toContainText(/Live Stream|Realtime|Real-Time/);
});
