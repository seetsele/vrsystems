const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async ()=>{
  const out = (n)=>path.join(__dirname,'..','test-results',n);
  if (!fs.existsSync(path.join(__dirname,'..','test-results'))) fs.mkdirSync(path.join(__dirname,'..','test-results'));
  const filePath = path.join(__dirname,'..','mobile_overlay','index.html');
  const url = 'file://' + filePath.replace(/\\/g, '/');
  const browser = await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  await page.setViewport({width:390,height:844});
  await page.goto(url,{waitUntil:'networkidle2'});
  await new Promise(r=>setTimeout(r,300));
  await page.screenshot({path: out('mobile_overlay_initial.png'), fullPage:true});
  await page.click('#verify-fab');
  await new Promise(r=>setTimeout(r,220));
  await page.screenshot({path: out('mobile_overlay_open.png'), fullPage:true});
  await page.click('#overlay-verify');
  await new Promise(r=>setTimeout(r,380));
  await page.screenshot({path: out('mobile_overlay_after_verify.png'), fullPage:true});
  await browser.close();
})();
