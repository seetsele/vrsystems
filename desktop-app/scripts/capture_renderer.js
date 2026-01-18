const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async ()=>{
  const out = (n)=>path.join(__dirname,'..','test-results',n);
  if (!fs.existsSync(path.join(__dirname,'..','test-results'))) fs.mkdirSync(path.join(__dirname,'..','test-results'));
  const filePath = path.join(__dirname,'..','renderer','index.html');
  const url = 'file://' + filePath.replace(/\\/g, '/');
  const browser = await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  await page.setViewport({width:1200,height:800});
  await page.goto(url,{waitUntil:'networkidle2'});
  await new Promise(r=>setTimeout(r,400));
  await page.screenshot({path: out('renderer_capture.png'), fullPage:true});
  await browser.close();
  console.debug('Saved renderer screenshot to', out('renderer_capture.png'));
})();
