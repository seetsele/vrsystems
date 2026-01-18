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

  // Trigger overlay: prefer registered handler, otherwise inject overlay DOM directly
  await page.evaluate(() => {
    const trigger = () => {
      // create overlay DOM similar to content script
      const pageOverlay = document.createElement('div');
      pageOverlay.id = 'verity-page-overlay';
      pageOverlay.innerHTML = `
        <div class="verity-overlay" style="max-width:820px;margin:40px auto;padding:18px;background:rgba(10,10,12,0.6);backdrop-filter:blur(8px);border-radius:12px;color:#fff">
          <textarea id="verity-overlay-input" placeholder="Paste or type text to verify..." spellcheck="false" style="width:100%;height:96px;padding:12px;border-radius:8px;border:none;background:rgba(255,255,255,0.02);color:#fff"></textarea>
          <div class="verity-overlay-actions" style="display:flex;gap:10px;margin-top:10px;">
            <button id="verity-overlay-verify" style="padding:10px 14px;border-radius:8px;border:none;background:linear-gradient(90deg,#60a5fa,#7c3aed);color:#021025;font-weight:700">Verify</button>
            <button id="verity-overlay-close" style="padding:10px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);background:transparent;color:#fff">Close</button>
          </div>
        </div>
      `;
      pageOverlay.style.cssText = 'position:fixed;inset:20px;z-index:2147483646;display:flex;align-items:flex-start;justify-content:center;pointer-events:auto;';
      document.body.appendChild(pageOverlay);
      const vbtn = document.getElementById('verity-overlay-verify');
      const cbtn = document.getElementById('verity-overlay-close');
      const ta = document.getElementById('verity-overlay-input');
      vbtn && vbtn.addEventListener('click', async () => {
        const text = ta.value && ta.value.trim();
        if (!text) return;
        try {
          const result = await chrome.runtime.sendMessage({ action: 'verify', text });
          // create a simple result node
          const res = document.createElement('div');
          res.style.cssText = 'margin-top:12px;padding:12px;border-radius:8px;background:rgba(0,0,0,0.4);color:#fff';
          res.innerText = `Result: ${result.verdict || 'unknown'} - ${result.confidence || 0}%`;
          pageOverlay.appendChild(res);
        } catch(e) { console.error(e); }
      });
      cbtn && cbtn.addEventListener('click', () => { pageOverlay.remove(); });
    };

    if (typeof window.__verity_onMessage === 'function') {
      window.__verity_onMessage({ action: 'toggleOverlay' });
    } else {
      trigger();
    }
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
})();
