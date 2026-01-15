const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const url = 'file://' + path.resolve(__dirname, '..', '..', 'desktop-app', 'renderer', 'index.html').replace(/\\/g, '/');
  await page.addInitScript(() => {
    // minimal stubs to allow renderer to initialize outside Electron
    // eslint-disable-next-line no-global-assign
    window.require = (name) => ({ info: () => {}, warn: () => {}, error: () => {} });
    window.verity = window.verity || {};
    window.verity.settings = window.verity.settings || { getAll: async () => ({}), save: async () => {} };
    window.verity.recent = window.verity.recent || { get: async () => [] };
  });

  await page.goto(url);
  await page.waitForSelector('#loading-screen', { state: 'hidden', timeout: 15000 });
  const header = await page.$('header');
  if (!header) {
    console.error('Header element not found');
    await browser.close();
    process.exit(2);
  }
  await header.screenshot({ path: path.resolve(__dirname, '..', '..', 'tests', 'visual', 'targets', 'desktop-target-header.png') });
  await browser.close();
})();