const puppeteer = require('puppeteer');
const path = require('path');
(async () => {
  const browser = await puppeteer.launch({args: ['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  const filePath = path.join(process.cwd(), 'public', 'settings.html');
  const url = 'file://' + filePath.replace(/\\/g, '/');
  await page.goto(url, {waitUntil: 'networkidle2'});
  await page.setViewport({ width: 1300, height: 900 });
  // wait briefly for JS initialization
  await new Promise(res => setTimeout(res, 700));
  await page.screenshot({path: path.join('screenshots', 'settings-page.png'), fullPage: true});
    console.info('screenshot saved to screenshots/settings-page.png');
  await browser.close();
})();
