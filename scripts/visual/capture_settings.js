const puppeteer = require('puppeteer');
const fs = require('fs');
(async () => {
  const outDir = 'screenshots';
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);
  const browser = await puppeteer.launch({args: ['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  const fileUrl = 'file://' + require('path').resolve('public/settings.html');
  await page.setViewport({width:1300, height:900});
  await page.goto(fileUrl, {waitUntil:'networkidle0'});
  // wait a moment for any JS to initialize
  await new Promise(r => setTimeout(r, 500));
  const path = `${outDir}/local-settings-1300x900.png`;
  await page.screenshot({path, fullPage:true});
  console.info('Saved', path);
  await browser.close();
})();
