const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const PNG = require('pngjs').PNG;
const pixelmatch = require('pixelmatch');

async function capture(url, outPath, viewport) {
  const browser = await puppeteer.launch({ args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport(viewport);
  // Support file:// urls
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 120000 });
  await new Promise((res) => setTimeout(res, 500));
  await page.screenshot({ path: outPath, fullPage: true });
  await browser.close();
}

function diffImages(img1Path, img2Path, outDiffPath) {
  const img1 = PNG.sync.read(fs.readFileSync(img1Path));
  const img2 = PNG.sync.read(fs.readFileSync(img2Path));

  const width = Math.max(img1.width, img2.width);
  const height = Math.max(img1.height, img2.height);

  const img1Resized = new PNG({ width, height });
  const img2Resized = new PNG({ width, height });

  PNG.bitblt(img1, img1Resized, 0, 0, img1.width, img1.height, 0, 0);
  PNG.bitblt(img2, img2Resized, 0, 0, img2.width, img2.height, 0, 0);

  const diff = new PNG({ width, height });
  const mismatch = pixelmatch(img1Resized.data, img2Resized.data, diff.data, width, height, { threshold: 0.12 });
  fs.writeFileSync(outDiffPath, PNG.sync.write(diff));
  const total = width * height;
  return { mismatch, total, percent: (mismatch / total) * 100 };
}

(async ()=>{
  const outDir = path.join(__dirname, '..', 'test-results');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  const sitePath = path.join(process.cwd(), 'public', 'index.html');
  const siteUrl = 'file://' + sitePath.replace(/\\/g, '/');
  const desktopPath = path.join(process.cwd(), 'desktop-app', 'renderer', 'index.html');
  const desktopUrl = 'file://' + desktopPath.replace(/\\/g, '/');
  const popupPath = path.join(process.cwd(), 'browser-extension', 'chrome', 'popup.html');
  const popupUrl = 'file://' + popupPath.replace(/\\/g, '/');

  const siteImg = path.join(outDir, 'site.png');
  const desktopImg = path.join(outDir, 'desktop.png');
  const desktopImgLarge = path.join(outDir, 'desktop_1280.png');
  const popupImg = path.join(outDir, 'popup.png');

  console.debug('Capturing site...');
  await capture(siteUrl, siteImg, { width: 1280, height: 900 });
  console.debug('Capturing desktop renderer...');
  await capture(desktopUrl, desktopImg, { width: 1200, height: 900 });
  // Also capture desktop at the same viewport as the site for a fair comparison
  await capture(desktopUrl, desktopImgLarge, { width: 1280, height: 900 });
  console.debug('Capturing extension popup...');
  await capture(popupUrl, popupImg, { width: 420, height: 700 });
  console.debug('Running diffs...');
  const diffDesktop = diffImages(siteImg, desktopImg, path.join(outDir, 'diff_site_desktop.png'));
  const diffDesktop1280 = diffImages(siteImg, desktopImgLarge, path.join(outDir, 'diff_site_desktop_1280.png'));
  const diffPopup = diffImages(siteImg, popupImg, path.join(outDir, 'diff_site_popup.png'));

  console.debug(`Site vs Desktop diff: ${diffDesktop.mismatch} px different (${diffDesktop.percent.toFixed(3)}%)`);
  console.debug(`Site vs Desktop (1280px) diff: ${diffDesktop1280.mismatch} px different (${diffDesktop1280.percent.toFixed(3)}%)`);
  console.debug(`Site vs Popup diff: ${diffPopup.mismatch} px different (${diffPopup.percent.toFixed(3)}%)`);

  console.debug('Screenshots and diffs saved to test-results/');
})();
