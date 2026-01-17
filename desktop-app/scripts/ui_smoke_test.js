const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const out = (name) => `./test-results/${name}`;
  try {
    if (!fs.existsSync('./test-results')) fs.mkdirSync('./test-results');
    console.log('Launching headless browser...');
    const browser = await puppeteer.launch({args: ['--no-sandbox','--disable-setuid-sandbox']});
    const page = await browser.newPage();
    page.setDefaultTimeout(20000);

    const url = process.env.VERITY_URL || 'http://127.0.0.1:3001/verify.html';
    console.log('Opening', url);
    await page.goto(url, { waitUntil: 'networkidle2' });

    // Ensure verify input exists
    const inputSel = '#verify-input';
    await page.waitForSelector(inputSel);
    console.log('Found verify input');

    // Type a sample claim and click extract
    await page.type(inputSel, 'The Great Wall of China is visible from space with the naked eye.');
    await page.waitForTimeout(250);
    const extractBtn = '#extract-claims-btn';
    if (await page.$(extractBtn)) {
      await page.click(extractBtn);
      console.log('Clicked Extract Claims');
      await page.waitForTimeout(800);
      await page.screenshot({ path: out('after-extract.png') });
    }

    // Click verify
    const verifyBtn = '#verify-btn';
    if (await page.$(verifyBtn)) {
      await page.click(verifyBtn);
      console.log('Clicked Verify Now');
      await page.waitForTimeout(1500);
      await page.screenshot({ path: out('after-verify.png') });
    }

    // Open 21-point info
    const learnBtn = "button[onclick=\"navigate('21-point-info')\"]";
    if (await page.$(learnBtn)) {
      await page.click(learnBtn);
      await page.waitForTimeout(500);
      await page.screenshot({ path: out('21-point-page.png') });
      // Click a point-card if present
      const point = '.point-card';
      if (await page.$(point)) {
        await page.click(point);
        await page.waitForTimeout(300);
        await page.screenshot({ path: out('point-modal.png') });
      }
    }

    // Click a promo card
    const promo = '.promo-card';
    if (await page.$(promo)) {
      await page.click(promo);
      await page.waitForTimeout(500);
      await page.screenshot({ path: out('promo-click.png') });
    }

    await browser.close();
    console.log('Smoke test completed — screenshots saved to ./test-results/');
    process.exit(0);
  } catch (err) {
    console.error('Smoke test failed:', err);
    try { fs.writeFileSync('./test-results/ui_smoke_error.txt', String(err)); } catch(e){}
    process.exit(2);
  }
})();
