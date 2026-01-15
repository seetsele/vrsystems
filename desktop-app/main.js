// Verity Desktop App v2.0 - Enterprise Main Process
// Comprehensive, Secure, Production-Ready

const { 
    app, 
    BrowserWindow, 
    Menu, 
    Tray, 
    ipcMain, 
    shell, 
    dialog, 
    nativeTheme,
    Notification, 
    globalShortcut, 
    clipboard,
    screen,
    session,
    powerMonitor
} = require('electron');
const path = require('path');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');
const log = require('electron-log');

// ============================================
// Security Configuration
// ============================================
const SECURITY_CONFIG = {
    CSP: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self' http://localhost:* https://*.verity.ai wss://*.verity.ai; img-src 'self' data: https:; frame-ancestors 'none';",
    ALLOWED_DOMAINS: ['localhost', 'verity.ai', 'api.verity.ai'],
    SESSION_TIMEOUT: 30 * 60 * 1000, // 30 minutes
    MAX_FAILED_ATTEMPTS: 5
};

// ============================================
// Logging Configuration
// ============================================
log.transports.file.level = 'info';
log.transports.console.level = 'debug';
autoUpdater.logger = log;

// ============================================
// Secure Store Configuration
// ============================================
const store = new Store({
    name: 'verity-config',
    encryptionKey: 'verity-desktop-secure-2025',
    defaults: {
        windowBounds: { width: 1400, height: 900 },
        windowState: { maximized: false },
        apiEndpoint: 'http://localhost:8081',
        theme: 'dark',
        sidebar: { collapsed: false, width: 280 },
        alwaysOnTop: false,
        startMinimized: false,
        minimizeToTray: true,
        autoStart: false,
        notifications: true,
        soundEffects: true,
        shortcuts: {
            quickVerify: 'CommandOrControl+Shift+V',
            toggleWindow: 'CommandOrControl+Shift+Space',
            newVerification: 'CommandOrControl+N'
        },
        recentVerifications: [],
        favoriteTools: ['verify', 'source-checker', 'research'],
        lastSyncTime: null,
        userPreferences: {
            defaultVerificationMode: 'comprehensive',
            autoSaveHistory: true,
            historyRetentionDays: 90
        },
        security: {
            sessionTimeout: true,
            requirePasswordOnWake: false,
            encryptLocalData: true
        }
    }
});

// ============================================
// Global State
// ============================================
let mainWindow = null;
let tray = null;
let isQuitting = false;
let sessionTimer = null;
let failedAttempts = 0;

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

// ============================================
// Window Creation
// ============================================
function createMainWindow() {
    const { width, height, x, y } = store.get('windowBounds');
    const { maximized } = store.get('windowState');
    const { workArea } = screen.getPrimaryDisplay();

    // Check if icon exists
    const fs = require('fs');
    const iconPath = path.join(__dirname, 'assets', 'icon.png');
    const hasIcon = fs.existsSync(iconPath);

    mainWindow = new BrowserWindow({
        width: Math.min(width, workArea.width),
        height: Math.min(height, workArea.height),
        x: x !== undefined ? x : undefined,
        y: y !== undefined ? y : undefined,
        minWidth: 1024,
        minHeight: 700,
            title: 'Verity',
        icon: hasIcon ? iconPath : undefined,
        backgroundColor: '#09090b',
        darkTheme: true,
        frame: false,
        titleBarStyle: 'hidden',
        titleBarOverlay: process.platform === 'darwin' ? {
            color: '#09090b',
            symbolColor: '#ffffff',
            height: 40
        } : false,
        trafficLightPosition: { x: 16, y: 12 },
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: true,
            webSecurity: true,
            allowRunningInsecureContent: false,
            enableRemoteModule: false,
            spellcheck: true
        },
        show: false
    });

    // Security: Set CSP headers
    mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
        callback({
            responseHeaders: {
                ...details.responseHeaders,
                'Content-Security-Policy': [SECURITY_CONFIG.CSP]
            }
        });
    });

    // Security: Block navigation to external URLs
    mainWindow.webContents.on('will-navigate', (event, url) => {
        const parsedUrl = new URL(url);
        if (!SECURITY_CONFIG.ALLOWED_DOMAINS.some(d => parsedUrl.hostname.includes(d))) {
            event.preventDefault();
            shell.openExternal(url);
        }
    });

    // Security: Block new window creation
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });

    // Load app
    mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

    // Show when ready
    mainWindow.once('ready-to-show', () => {
        if (maximized) {
            mainWindow.maximize();
        }
        if (!store.get('startMinimized')) {
            mainWindow.show();
            mainWindow.focus();
        }
    });

    // Save window state
    mainWindow.on('resize', saveWindowState);
    mainWindow.on('move', saveWindowState);
    mainWindow.on('maximize', () => store.set('windowState.maximized', true));
    mainWindow.on('unmaximize', () => store.set('windowState.maximized', false));

    // Handle close to tray
    mainWindow.on('close', (event) => {
        if (!isQuitting && store.get('minimizeToTray')) {
            event.preventDefault();
            mainWindow.hide();
            if (process.platform === 'darwin') {
                app.dock.hide();
            }
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Dev tools in development
    if (isDev) {
        mainWindow.webContents.openDevTools({ mode: 'detach' });
    }

    return mainWindow;
}

function saveWindowState() {
    if (mainWindow && !mainWindow.isMaximized()) {
        store.set('windowBounds', mainWindow.getBounds());
    }
}

// ============================================
// System Tray
// ============================================
function createTray() {
    // Skip tray creation on Windows if no .ico file exists
    // Electron's Tray requires .ico on Windows, .png on Linux, .png or .icns on macOS
    const fs = require('fs');
    
    let iconPath;
    let iconFormats;
    
    if (process.platform === 'win32') {
        // Try multiple formats on Windows
        iconFormats = ['icon.ico', 'icon.png'];
    } else if (process.platform === 'darwin') {
        iconFormats = ['icon.icns', 'icon.png'];
    } else {
        iconFormats = ['icon.png'];
    }
    
    // Find first available icon
    for (const format of iconFormats) {
        const testPath = path.join(__dirname, 'assets', format);
        if (fs.existsSync(testPath)) {
            iconPath = testPath;
            break;
        }
    }
    
    if (!iconPath) {
        log.warn('Tray icon not found in assets folder - skipping tray creation');
        return;
    }
    
    try {
        tray = new Tray(iconPath);
        tray.setToolTip('Verity - AI Fact Checker');
        
        updateTrayMenu();
        
        tray.on('click', () => showWindow());
        tray.on('double-click', () => showWindow());
    } catch (error) {
        log.error('Failed to create tray:', error);
    }
}

function updateTrayMenu() {
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Open Verity',
            click: () => showWindow()
        },
        {
            label: 'Quick Verify Clipboard',
            accelerator: store.get('shortcuts.quickVerify'),
            click: () => quickVerifyClipboard()
        },
        { type: 'separator' },
        {
            label: 'Tools',
            submenu: [
                { label: 'Fact Checker', click: () => navigateTo('verify') },
                { label: 'Source Analyzer', click: () => navigateTo('source-checker') },
                { label: 'Research Assistant', click: () => navigateTo('research') },
                { label: 'Content Moderator', click: () => navigateTo('content-moderator') }
            ]
        },
        { type: 'separator' },
        {
            label: 'Dashboard',
            click: () => navigateTo('dashboard')
        },
        {
            label: 'History',
            click: () => navigateTo('history')
        },
        { type: 'separator' },
        {
            label: 'Settings',
            click: () => navigateTo('settings')
        },
        { type: 'separator' },
        {
            label: 'Quit Verity',
            click: () => {
                isQuitting = true;
                app.quit();
            }
        }
    ]);
    
    tray.setContextMenu(contextMenu);
}

function showWindow() {
    if (mainWindow) {
        if (mainWindow.isMinimized()) mainWindow.restore();
        mainWindow.show();
        mainWindow.focus();
        if (process.platform === 'darwin') {
            app.dock.show();
        }
    }
}

function navigateTo(page) {
    showWindow();
    mainWindow?.webContents.send('navigate', page);
}

// ============================================
// Application Menu
// ============================================
function createMenu() {
    const isMac = process.platform === 'darwin';
    
    const template = [
        ...(isMac ? [{
            label: app.name,
            submenu: [
                { role: 'about' },
                { type: 'separator' },
                { label: 'Preferences...', accelerator: 'Cmd+,', click: () => navigateTo('settings') },
                { type: 'separator' },
                { role: 'services' },
                { type: 'separator' },
                { role: 'hide' },
                { role: 'hideOthers' },
                { role: 'unhide' },
                { type: 'separator' },
                { role: 'quit' }
            ]
        }] : []),
        {
            label: 'File',
            submenu: [
                { label: 'New Verification', accelerator: 'CmdOrCtrl+N', click: () => navigateTo('verify') },
                { label: 'Quick Verify Clipboard', accelerator: 'CmdOrCtrl+Shift+V', click: () => quickVerifyClipboard() },
                { type: 'separator' },
                { label: 'Import History...', click: () => importHistory() },
                { label: 'Export History...', accelerator: 'CmdOrCtrl+E', click: () => exportHistory() },
                { type: 'separator' },
                isMac ? { role: 'close' } : { role: 'quit' }
            ]
        },
        {
            label: 'Edit',
            submenu: [
                { role: 'undo' },
                { role: 'redo' },
                { type: 'separator' },
                { role: 'cut' },
                { role: 'copy' },
                { role: 'paste' },
                { role: 'selectAll' }
            ]
        },
        {
            label: 'View',
            submenu: [
                { label: 'Dashboard', accelerator: 'CmdOrCtrl+1', click: () => navigateTo('dashboard') },
                { label: 'Verify', accelerator: 'CmdOrCtrl+2', click: () => navigateTo('verify') },
                { label: 'History', accelerator: 'CmdOrCtrl+3', click: () => navigateTo('history') },
                { label: 'Tools', accelerator: 'CmdOrCtrl+4', click: () => navigateTo('tools') },
                { type: 'separator' },
                { label: 'Toggle Sidebar', accelerator: 'CmdOrCtrl+B', click: () => mainWindow?.webContents.send('toggle-sidebar') },
                { type: 'separator' },
                { role: 'reload' },
                { role: 'forceReload' },
                { role: 'toggleDevTools' },
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' }
            ]
        },
        {
            label: 'Tools',
            submenu: [
                { label: 'Fact Checker', click: () => navigateTo('verify') },
                { label: 'Source Analyzer', click: () => navigateTo('source-checker') },
                { label: 'Content Moderator', click: () => navigateTo('content-moderator') },
                { label: 'Research Assistant', click: () => navigateTo('research') },
                { type: 'separator' },
                { label: 'Social Monitor', click: () => navigateTo('social-monitor') },
                { label: 'Stats Validator', click: () => navigateTo('stats-validator') },
                { label: 'Misinformation Map', click: () => navigateTo('misinfo-map') },
                { type: 'separator' },
                { label: 'API Tester', click: () => navigateTo('api-tester') }
            ]
        },
        {
            label: 'Window',
            submenu: [
                { role: 'minimize' },
                { role: 'zoom' },
                { label: 'Always on Top', type: 'checkbox', checked: store.get('alwaysOnTop'), click: (item) => {
                    store.set('alwaysOnTop', item.checked);
                    mainWindow?.setAlwaysOnTop(item.checked);
                }},
                { type: 'separator' },
                ...(isMac ? [{ type: 'separator' }, { role: 'front' }] : [{ role: 'close' }])
            ]
        },
        {
            label: 'Help',
            submenu: [
                { label: 'Documentation', click: () => shell.openExternal('https://verity.ai/docs') },
                { label: 'API Reference', click: () => shell.openExternal('https://verity.ai/api-docs') },
                { label: 'Keyboard Shortcuts', click: () => navigateTo('shortcuts') },
                { type: 'separator' },
                { label: 'Report Issue', click: () => shell.openExternal('https://github.com/verity-systems/verity-desktop/issues') },
                { label: 'Check for Updates...', click: () => checkForUpdates(true) },
                { type: 'separator' },
                { label: 'About Verity', click: () => showAboutDialog() }
            ]
        }
    ];
    
    Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

// ============================================
// IPC Handlers
// ============================================
function setupIPC() {
    // App info
    ipcMain.handle('app:getInfo', () => ({
        version: app.getVersion(),
        name: app.getName(),
        platform: process.platform,
        arch: process.arch,
        isDev,
        electron: process.versions.electron,
        chrome: process.versions.chrome,
        node: process.versions.node
    }));
    
    // Window controls
    ipcMain.on('window:minimize', () => mainWindow?.minimize());
    ipcMain.on('window:maximize', () => {
        if (mainWindow?.isMaximized()) {
            mainWindow.unmaximize();
        } else {
            mainWindow?.maximize();
        }
    });
    ipcMain.on('window:close', () => mainWindow?.close());
    ipcMain.handle('window:isMaximized', () => mainWindow?.isMaximized());
    
    // Settings
    ipcMain.handle('settings:get', (_, key) => store.get(key));
    ipcMain.handle('settings:set', (_, key, value) => {
        store.set(key, value);
        return true;
    });
    ipcMain.handle('settings:getAll', () => store.store);
    ipcMain.handle('settings:reset', () => {
        store.clear();
        return true;
    });
    
    // Clipboard
    ipcMain.handle('clipboard:read', () => clipboard.readText());
    ipcMain.handle('clipboard:write', (_, text) => {
        clipboard.writeText(text);
        return true;
    });
    
    // Notifications
    ipcMain.handle('notification:show', (_, { title, body, icon, silent }) => {
        if (store.get('notifications') && Notification.isSupported()) {
            const notification = new Notification({
                title,
                body,
                icon: icon || path.join(__dirname, 'assets', 'icon.png'),
                silent: silent || !store.get('soundEffects')
            });
            notification.show();
            return true;
        }
        return false;
    });
    
    // Dialogs
    ipcMain.handle('dialog:save', async (_, options) => {
        return await dialog.showSaveDialog(mainWindow, options);
    });
    
    ipcMain.handle('dialog:open', async (_, options) => {
        return await dialog.showOpenDialog(mainWindow, options);
    });
    
    ipcMain.handle('dialog:message', async (_, options) => {
        return await dialog.showMessageBox(mainWindow, options);
    });
    
    // Shell
    ipcMain.on('shell:openExternal', (_, url) => {
        // Security: validate URL
        try {
            const parsedUrl = new URL(url);
            if (['http:', 'https:', 'mailto:'].includes(parsedUrl.protocol)) {
                shell.openExternal(url);
            }
        } catch (e) {
            log.warn('Invalid URL:', url);
        }
    });
    
    // Recent verifications
    ipcMain.handle('recent:get', () => store.get('recentVerifications'));
    ipcMain.handle('recent:add', (_, verification) => {
        const recent = store.get('recentVerifications') || [];
        recent.unshift({ ...verification, timestamp: Date.now() });
        store.set('recentVerifications', recent.slice(0, 500));
        return true;
    });
    ipcMain.handle('recent:clear', () => {
        store.set('recentVerifications', []);
        return true;
    });
    ipcMain.handle('recent:delete', (_, id) => {
        const recent = store.get('recentVerifications') || [];
        store.set('recentVerifications', recent.filter(r => r.id !== id));
        return true;
    });

    // Small utility: open DevTools on renderer request
    ipcMain.on('open-devtools', () => {
        try { mainWindow?.webContents.openDevTools({ mode: 'detach' }); } catch (e) { log.warn('open-devtools failed', e); }
    });
    
    // API
    ipcMain.handle('api:getEndpoint', () => store.get('apiEndpoint'));
    ipcMain.handle('api:setEndpoint', (_, endpoint) => {
        store.set('apiEndpoint', endpoint);
        return true;
    });
    
    // Theme
    ipcMain.handle('theme:get', () => store.get('theme'));
    ipcMain.handle('theme:set', (_, theme) => {
        store.set('theme', theme);
        nativeTheme.themeSource = theme;
        return true;
    });
}

// ============================================
// Global Shortcuts
// ============================================
function registerShortcuts() {
    const shortcuts = store.get('shortcuts');
    
    if (shortcuts.quickVerify) {
        globalShortcut.register(shortcuts.quickVerify, quickVerifyClipboard);
    }
    
    if (shortcuts.toggleWindow) {
        globalShortcut.register(shortcuts.toggleWindow, () => {
            if (mainWindow?.isVisible() && mainWindow?.isFocused()) {
                mainWindow.hide();
            } else {
                showWindow();
            }
        });
    }
}

async function quickVerifyClipboard() {
    const text = clipboard.readText().trim();
    if (text) {
        showWindow();
        mainWindow?.webContents.send('quick-verify', text);
        
        if (store.get('notifications')) {
            new Notification({
                title: 'Verifying claim...',
                body: text.substring(0, 80) + (text.length > 80 ? '...' : ''),
                silent: !store.get('soundEffects')
            }).show();
        }
    }
}

// ============================================
// Auto Updates
// ============================================
function setupAutoUpdater() {
    if (isDev) return;
    
    autoUpdater.autoDownload = false;
    autoUpdater.autoInstallOnAppQuit = true;
    
    autoUpdater.on('update-available', (info) => {
        mainWindow?.webContents.send('update-available', info);
        dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Update Available',
            message: `Verity ${info.version} is available`,
            detail: 'Would you like to download it now?',
            buttons: ['Download', 'Later']
        }).then(({ response }) => {
            if (response === 0) autoUpdater.downloadUpdate();
        });
    });
    
    autoUpdater.on('update-downloaded', () => {
        mainWindow?.webContents.send('update-downloaded');
        dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Update Ready',
            message: 'Update downloaded and ready to install',
            buttons: ['Restart Now', 'Later']
        }).then(({ response }) => {
            if (response === 0) {
                isQuitting = true;
                autoUpdater.quitAndInstall();
            }
        });
    });
    
    autoUpdater.on('error', (error) => {
        log.error('Auto-updater error:', error);
    });
}

function checkForUpdates(manual = false) {
    if (isDev && manual) {
        dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Development Mode',
            message: 'Auto-updates disabled in development'
        });
        return;
    }
    
    autoUpdater.checkForUpdates().catch(err => {
        if (manual) {
            dialog.showMessageBox(mainWindow, {
                type: 'info',
                title: 'Up to Date',
                message: 'You have the latest version of Verity'
            });
        }
    });
}

// ============================================
// Utilities
// ============================================
async function exportHistory() {
    const { filePath } = await dialog.showSaveDialog(mainWindow, {
        title: 'Export Verification History',
        defaultPath: `verity-history-${new Date().toISOString().split('T')[0]}.json`,
        filters: [
            { name: 'JSON', extensions: ['json'] },
            { name: 'CSV', extensions: ['csv'] }
        ]
    });
    
    if (filePath) {
        mainWindow?.webContents.send('export-history', { filePath });
    }
}

async function importHistory() {
    const { filePaths } = await dialog.showOpenDialog(mainWindow, {
        title: 'Import Verification History',
        filters: [{ name: 'JSON', extensions: ['json'] }],
        properties: ['openFile']
    });
    
    if (filePaths?.[0]) {
        mainWindow?.webContents.send('import-history', { filePath: filePaths[0] });
    }
}

function showAboutDialog() {
    dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: 'About Verity',
        message: 'Verity - AI-Powered Fact-Checking Platform',
        detail: `Version: ${app.getVersion()}\nElectron: ${process.versions.electron}\nChrome: ${process.versions.chrome}\nNode: ${process.versions.node}\n\n© 2025 Verity Systems Inc.\nAll rights reserved.`,
        buttons: ['OK']
    });
}

// ============================================
// Power & Session Management
// ============================================
function setupPowerMonitor() {
    powerMonitor.on('suspend', () => {
        log.info('System suspended');
        mainWindow?.webContents.send('system-suspend');
    });
    
    powerMonitor.on('resume', () => {
        log.info('System resumed');
        mainWindow?.webContents.send('system-resume');
    });
    
    powerMonitor.on('lock-screen', () => {
        log.info('Screen locked');
        if (store.get('security.requirePasswordOnWake')) {
            mainWindow?.webContents.send('session-lock');
        }
    });
}

// ============================================
// App Lifecycle
// ============================================
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', (event, argv) => {
        if (mainWindow) {
            showWindow();
            // Handle deep links
            const url = argv.find(arg => arg.startsWith('verity://'));
            if (url) {
                mainWindow.webContents.send('deep-link', url);
            }
        }
    });
    
    app.whenReady().then(() => {
        // Set app user model id for Windows
        if (process.platform === 'win32') {
            app.setAppUserModelId('com.veritysystems.desktop');
        }
        
        // Protocol handler for deep links
        app.setAsDefaultProtocolClient('verity');
        
        // Setup IPC BEFORE creating window
        setupIPC();
        
        // Create components
        createMainWindow();
        createTray();
        createMenu();
        registerShortcuts();
        setupAutoUpdater();
        setupPowerMonitor();
        
        // Check for updates after delay
        setTimeout(() => checkForUpdates(), 10000);
        
        // macOS: recreate window on dock click
        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) {
                createMainWindow();
            } else {
                showWindow();
            }
        });
    });
    
    app.on('before-quit', () => {
        isQuitting = true;
        globalShortcut.unregisterAll();
    });
    
    app.on('window-all-closed', () => {
        if (process.platform !== 'darwin') {
            app.quit();
        }
    });
}

// Error handling
process.on('uncaughtException', (error) => {
    log.error('Uncaught Exception:', error);
    dialog.showErrorBox('Unexpected Error', error.message);
});

process.on('unhandledRejection', (reason) => {
    log.error('Unhandled Rejection:', reason);
});
