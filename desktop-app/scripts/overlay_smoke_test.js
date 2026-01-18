const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
  const out = (name) => `./test-results/${name}`;
  try {
    if (!fs.existsSync('./test-results')) fs.mkdirSync('./test-results');
    const filePath = path.join(__dirname, '..', 'overlay', 'index.html');
    const url = 'file://' + filePath.replace(/\\/g, '/');
    console.log('Opening overlay file at', url);

    const browser = await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});
    const page = await browser.newPage();
    page.on('console', msg => {
      try { fs.appendFileSync(out('overlay_console.log'), msg.text() + '\n'); } catch(e){}
    });

    await page.goto(url, { waitUntil: 'networkidle2' });
    await page.screenshot({ path: out('overlay_initial.png') });

    await page.waitForSelector('#overlay-input');
    await page.focus('#overlay-input');
    await page.keyboard.type('Vaccines contain microchips.');
    await page.screenshot({ path: out('overlay_filled.png') });

    // Intercept postMessages from the page
    await page.exposeFunction('onOverlayMessage', msg => {
      try { fs.appendFileSync(out('overlay_messages.log'), JSON.stringify(msg) + '\n'); } catch(e){}
    });

    await page.evaluate(() => {
      window.addEventListener('message', (ev) => {
        try { window.onOverlayMessage(ev.data); } catch(e){}
      });
    });

    await page.click('#verify-btn');
    await new Promise(res => setTimeout(res, 800));
    await page.screenshot({ path: out('overlay_after_click.png') });

    await browser.close();
    console.log('Overlay smoke test completed.');
    process.exit(0);
  } catch (err) {
    console.error('Overlay smoke test failed:', err);
    try { fs.writeFileSync('./test-results/overlay_error.txt', String(err)); } catch(e){}
    process.exit(2);
  }
})();
