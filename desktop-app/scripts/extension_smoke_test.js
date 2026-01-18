const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
  const out = (name) => path.join(__dirname, '..', 'test-results', name);
  const scriptPath = path.join(__dirname, '..', '..', 'browser-extension', 'chrome', 'content.js');
  const scriptSrc = fs.readFileSync(scriptPath, 'utf8');

  if (!fs.existsSync(path.join(__dirname, '..', 'test-results'))) fs.mkdirSync(path.join(__dirname, '..', 'test-results'));

  const browser = await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  await page.setViewport({width:1200, height:900});

  // Load a sample article page
  const sampleHTML = `
    <html><head><meta charset="utf-8"><title>Sample Article</title></head>
    <body style="font-family:Inter, system-ui, sans-serif; padding:40px; background:#0b1220; color:#e6eef8">
    <article>
      <h1>Breaking Research Finds New Biomarker</h1>
      <p id="p1">A recent study published in the Journal of Important Things finds that exposure to certain wavelengths may influence gene expression in rare cases. This finding has been replicated across multiple labs and suggests new avenues for therapeutic exploration.</p>
      <p id="p2">Further analysis shows limited applicability to the general population, and more research is needed.</p>
    </article>
    </body></html>`;

  // Inject a chrome stub and a fake runtime responder before any scripts run
  await page.evaluateOnNewDocument(() => {
    window.chrome = {
      storage: {
        sync: {
          get: (keys, cb) => { try { cb({}); } catch(e){} },
          set: (obj) => {}
        }
      },
      runtime: {
        sendMessage: (msg) => {
          // default: return a promise resolved with fake verification
          return new Promise((res) => {
            if (msg && msg.action === 'verify') {
              res({ verdict: 'true', confidence: 92, explanation: 'Well-supported by multiple reputable sources.', sources: [{name:'Journal of Important Things', url:'https://example.com/study'}] });
            } else {
              res({});
            }
          });
        },
        onMessage: {
          addListener: (cb) => { window.__verity_onMessage = cb; }
        }
      }
    };
  });

  await page.setContent(sampleHTML, { waitUntil: 'networkidle2' });

  // Inject content script into the page as a script tag so it runs in the page context
  await page.addScriptTag({ content: scriptSrc });
  // Capture console from the page for debugging
  page.on('console', msg => { try { fs.appendFileSync(out('extension_console.log'), msg.text() + '\n'); } catch(e){} });

  // Give the injected script a short moment to initialize
  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({ path: out('extension_overlay_initial.png'), fullPage: true });

  // Trigger overlay by calling the registered message handler
  await page.evaluate(() => {
    if (typeof window.__verity_onMessage === 'function') window.__verity_onMessage({ action: 'toggleOverlay' });
  });

  await new Promise(r => setTimeout(r, 300));
  await page.screenshot({ path: out('extension_overlay_open.png'), fullPage: true });

  // Fill textarea and click Verify
  await page.evaluate(() => {
    const ta = document.getElementById('verity-overlay-input');
    if (ta) ta.value = document.getElementById('p1').innerText.slice(0, 200);
    const v = document.getElementById('verity-overlay-verify');
    if (v) v.click();
  });

  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({ path: out('extension_overlay_after_verify.png'), fullPage: true });

  await browser.close();
  console.log('Extension overlay smoke completed. Screenshots saved to test-results.');
})();
