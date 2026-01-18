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
      const delay = (ms) => new Promise(res => setTimeout(res, ms));

    const url = process.env.VERITY_URL || 'http://127.0.0.1:3001/verify.html';
    console.log('Opening', url);
    let resp = null;
    try {
      resp = await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    } catch (e) {
      console.warn('First goto failed, retrying with domcontentloaded:', e && e.message);
      resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    }
    console.log('Page response status:', resp && resp.status());

    // Save initial snapshot for debugging
    await page.screenshot({ path: out('initial.png'), fullPage: true });
    const html = await page.content();
    fs.writeFileSync(out('initial.html'), html);

    // Try a list of possible input selectors (site variations)
    const inputCandidates = ['#verify-input', '#quickText', '#claimText', '#verify-input-area', '.main-textarea', 'textarea'];
    let inputSel = null;
    for (const s of inputCandidates) {
      if (await page.$(s)) { inputSel = s; break; }
    }
    if (!inputSel) throw new Error('No input selector found on page');
    console.log('Using input selector:', inputSel);

    // Type a sample claim and click extract
    await page.focus(inputSel);
    await page.keyboard.type('The Great Wall of China is visible from space with the naked eye.');
    await delay(250);
    const extractBtnCandidates = ['#extract-claims-btn', '.extract-btn', 'button.extract-btn', 'button[onclick="extractClaims()"]'];
    for (const b of extractBtnCandidates) {
      if (await page.$(b)) {
        await page.evaluate((sel) => { const el = document.querySelector(sel); if (el) el.click(); }, b);
        console.log('Clicked extract button:', b);
        await delay(800);
        await page.screenshot({ path: out('after-extract.png') });
        break;
      }
    }

    // Click verify using multiple possible selectors
    const verifyBtnCandidates = ['#verify-btn', '#verifyBtn', 'button.btn-verify', 'button.btn-primary', 'button[onclick="fullVerify()"]', 'button[onclick^="quickVerify"]'];
    for (const b of verifyBtnCandidates) {
      if (await page.$(b)) {
        await page.evaluate((sel) => { const el = document.querySelector(sel); if (el) el.click(); }, b);
        console.log('Clicked verify button:', b);
        await delay(1500);
        await page.screenshot({ path: out('after-verify.png') });
        break;
      }
    }

    // Open 21-point info
    const learnBtn = "button[onclick=\"navigate('21-point-info')\"]";
    if (await page.$(learnBtn)) {
      await page.evaluate((sel) => { const el = document.querySelector(sel); if (el) el.click(); }, learnBtn);
      await delay(500);
      await page.screenshot({ path: out('21-point-page.png') });
      // Click a point-card if present
      const point = '.point-card';
      if (await page.$(point)) {
        await page.evaluate((sel) => { const el = document.querySelector(sel); if (el) el.click(); }, point);
        await delay(300);
        await page.screenshot({ path: out('point-modal.png') });
      }
    }

    // Click a promo card
    const promo = '.promo-card';
    if (await page.$(promo)) {
      await page.evaluate((sel) => { const el = document.querySelector(sel); if (el) el.click(); }, promo);
      await delay(500);
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
