# Desktop App Icons

Place your app icon files here:
- Windows: app-icon.ico
- Mac: app-icon.icns
- Linux: app-icon.png (512x512)

Reference in Electron main.js:
mainWindow = new BrowserWindow({
  icon: path.join(__dirname, 'assets/icons/app-icon.png'),
  // ...
});

For packaging, set the icon in package.json under the "build" section.