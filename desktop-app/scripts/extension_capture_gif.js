const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const GIFEncoder = require('gifencoder');
const { createCanvas, loadImage } = require('canvas');

(async () => {
  const outDir = path.join(__dirname, '..', 'test-results');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  const outGif = path.join(outDir, 'extension_overlay_capture.gif');

  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 900 });

  const sampleHTML = `
    <html><head><meta charset="utf-8"><title>Sample Article</title></head>
    <body style="font-family:Inter, system-ui, sans-serif; padding:40px; background:#0b1220; color:#e6eef8">
    <article>
      <h1>Breaking Research Finds New Biomarker</h1>
      <p id="p1">A recent study published in the Journal of Important Things finds that exposure to certain wavelengths may influence gene expression in rare cases.</p>
    </article>
    </body></html>`;

  await page.evaluateOnNewDocument(() => {
    window.chrome = {
      storage: { sync: { get: (keys, cb) => { try { cb({}); } catch(e){} }, set: (o) => {} } },
      runtime: { sendMessage: (msg) => new Promise((res)=> res({ verdict: 'true', confidence: 92 })), onMessage: { addListener: (cb) => { window.__verity_onMessage = cb; } } }
    };
  });

  await page.setContent(sampleHTML, { waitUntil: 'networkidle2' });
  // inject content script
  const scriptPath = path.join(__dirname, '..', '..', 'browser-extension', 'chrome', 'content.js');
  const scriptSrc = fs.readFileSync(scriptPath, 'utf8');
  await page.addScriptTag({ content: scriptSrc });

  // small helper to capture screenshots frames
  const frames = [];
  const capture = async () => {
    const buf = await page.screenshot({ fullPage: false });
    frames.push(buf);
  };

  // open overlay
  await page.evaluate(() => {
    if (typeof window.__verity_onMessage === 'function') {
      window.__verity_onMessage({ action: 'toggleOverlay' });
    } else {
      // fallback create overlay
      const evt = new Event('click');
      document.body.dispatchEvent(evt);
    }
  });
  await page.waitForTimeout(400);
  await capture();

  // click Cluely toggle
  await page.evaluate(() => { const t = document.getElementById('verity-overlay-toggle-style'); if (t) t.click(); });
  await page.waitForTimeout(400);
  await capture();

  // fill input and click send
  await page.evaluate(() => {
    const ta = document.getElementById('verity-overlay-input'); if (ta) ta.value = document.getElementById('p1').innerText.slice(0,200);
    const b = document.getElementById('verity-overlay-send'); if (b) b.click();
  });
  await page.waitForTimeout(800);
  await capture();

  // produce GIF from frames
  const encoder = new GIFEncoder(1200, 900);
  const canvas = createCanvas(1200, 900);
  const ctx = canvas.getContext('2d');
  const stream = fs.createWriteStream(outGif);
  encoder.createReadStream().pipe(stream);
  encoder.start();
  encoder.setRepeat(0);
  encoder.setDelay(500);
  encoder.setQuality(10);

  for (const f of frames) {
    const img = await loadImage(f);
    ctx.drawImage(img, 0, 0);
    encoder.addFrame(ctx);
  }
  encoder.finish();

  await browser.close();
  try {
    fs.writeFileSync(path.join(outDir, 'extension_overlay_capture.json'), JSON.stringify({ gif: outGif }));
  } catch (e) { }
})();
