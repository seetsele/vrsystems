const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

async function capture() {
  const win = new BrowserWindow({
    width: 900,
    height: 220,
    show: false,
    transparent: true,
    frame: false,
    webPreferences: {
      offscreen: true,
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  const filePath = path.join(__dirname, '..', 'overlay', 'index.html');
  const url = 'file://' + filePath.replace(/\\/g, '/');
  await win.loadURL(url);

  // allow render to settle
  setTimeout(async () => {
    try {
      const image = await win.webContents.capturePage();
      const outDir = path.join(__dirname, '..', 'test-results');
      if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
      const outPath = path.join(outDir, 'overlay_electron_capture.png');
      fs.writeFileSync(outPath, image.toPNG());
      console.log('Saved overlay capture to', outPath);
    } catch (err) {
      console.error('Capture failed', err);
    } finally {
      app.quit();
    }
  }, 600);
}

app.whenReady().then(capture);
app.on('window-all-closed', () => {});
