import { test, expect } from '@playwright/test';

test('Image Analysis flow loads from dashboard', async ({ page }) => {
  await page.goto('/dashboard.html');
  // Click the Image Analysis action
  await page.click('a[href*="verify.html?type=image"]');
  await expect(page).toHaveURL(/verify.html\?type=image/);
  // Expect upload area or image-specific UI to be visible
  await expect(page.locator('.upload-zone')).toBeVisible();
});

test('Real-Time Stream page loads and shows stream header', async ({ page }) => {
  await page.goto('/realtime-stream.html');
  // The page uses 'Live Stream' as the heading text
  await expect(page.locator('h1')).toContainText(/Live Stream|Realtime|Real-Time/);
  await expect(page.locator('text=Live Stream')).toBeVisible();
});
