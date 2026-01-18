const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const PNG = require('pngjs').PNG;
const pixelmatch = require('pixelmatch');

const viewports = [
  { width: 1300, height: 900 },
  { width: 1024, height: 768 },
  { width: 390, height: 844 }
];

async function capture(page, url, outPath, viewport) {
  await page.setViewport(viewport);
  await page.goto(url, { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 700));
  await page.screenshot({ path: outPath, fullPage: true });
}

(async () => {
  const browser = await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();

  const localFile = 'file://' + path.join(process.cwd(), 'public', 'settings.html').replace(/\\/g, '/');
  const liveUrls = [
    'https://veritysystems.app/settings',
    'https://veritysystems.app/settings.html',
    'https://veritysystems.app/'
  ];

  if (!fs.existsSync(path.join(process.cwd(), 'screenshots'))) fs.mkdirSync(path.join(process.cwd(), 'screenshots'));

  for (const vp of viewports) {
    const name = `${vp.width}x${vp.height}`;
    const localOut = path.join('screenshots', `local-settings-${name}.png`);
    console.info('Capturing local', name);
    await capture(page, localFile, localOut, vp);

    let liveOut = null;
    for (const u of liveUrls) {
      try {
        liveOut = path.join('screenshots', `live-settings-${name}.png`);
        console.info('Attempting live capture:', u);
        await capture(page, u, liveOut, vp);
        // if we succeeded capturing, break
        break;
      } catch (e) {
        console.warn('Live capture failed for', u, e.message);
        liveOut = null;
      }
    }

    if (!liveOut || !fs.existsSync(liveOut)) {
      console.warn('Could not capture live page for comparison for viewport', name);
      continue;
    }

    // diff
    const img1 = PNG.sync.read(fs.readFileSync(localOut));
    const img2 = PNG.sync.read(fs.readFileSync(liveOut));
    const width = Math.min(img1.width, img2.width);
    const height = Math.min(img1.height, img2.height);
    // crop to common size
    function cropTo(srcImg, w, h) {
      const cropped = new PNG({ width: w, height: h });
      for (let y = 0; y < h; y++) {
        const srcStart = (y * srcImg.width) * 4;
        const srcRow = srcImg.data.slice(srcStart, srcStart + w * 4);
        const dstStart = (y * w) * 4;
        cropped.data.set(srcRow, dstStart);
      }
      return cropped;
    }
    const c1 = cropTo(img1, width, height);
    const c2 = cropTo(img2, width, height);
    const diff = new PNG({ width, height });
    const mismatched = pixelmatch(c1.data, c2.data, diff.data, width, height, { threshold: 0.15 });
    const diffPath = path.join('screenshots', `diff-settings-${name}.png`);
    fs.writeFileSync(diffPath, PNG.sync.write(diff));
    console.info(`Viewport ${name} -> mismatched pixels: ${mismatched}. Diff saved to ${diffPath}`);
  }

  await browser.close();
  console.info('Visual comparison complete.');
})();
