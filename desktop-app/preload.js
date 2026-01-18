// Verity Desktop App v2.0 - Secure Preload Script
// Context-isolated bridge between main and renderer

const { contextBridge, ipcRenderer } = require('electron');

// ============================================
// Secure API Bridge
// ============================================
contextBridge.exposeInMainWorld('verity', {
    // App information
    app: {
        getInfo: () => ipcRenderer.invoke('app:getInfo'),
        getVersion: () => ipcRenderer.invoke('app:getInfo').then(info => info.version),
        getPlatform: () => process.platform
    },
    
    // Window controls
    window: {
        minimize: () => ipcRenderer.send('window:minimize'),
        maximize: () => ipcRenderer.send('window:maximize'),
        close: () => ipcRenderer.send('window:close'),
        isMaximized: () => ipcRenderer.invoke('window:isMaximized'),
        onMaximizedChange: (callback) => {
            const handler = (_, isMaximized) => callback(isMaximized);
            ipcRenderer.on('window-maximized', handler);
            return () => ipcRenderer.removeListener('window-maximized', handler);
        }
    },
    
    // Settings management
    settings: {
        get: (key) => ipcRenderer.invoke('settings:get', key),
        set: (key, value) => ipcRenderer.invoke('settings:set', key, value),
        getAll: () => ipcRenderer.invoke('settings:getAll'),
        reset: () => ipcRenderer.invoke('settings:reset'),
        save: (obj) => ipcRenderer.invoke('settings:save', obj)
    },
    
    // Clipboard operations
    clipboard: {
        read: () => ipcRenderer.invoke('clipboard:read'),
        write: (text) => ipcRenderer.invoke('clipboard:write', text)
    },
    
    // Notifications
    notification: {
        show: (options) => ipcRenderer.invoke('notification:show', options)
    },
    
    // Dialogs
    dialog: {
        save: (options) => ipcRenderer.invoke('dialog:save', options),
        open: (options) => ipcRenderer.invoke('dialog:open', options),
        message: (options) => ipcRenderer.invoke('dialog:message', options)
    },
    
    // Shell operations
    shell: {
        openExternal: (url) => ipcRenderer.send('shell:openExternal', url)
    },

    // Diagnostics helpers
    diagnostics: {
        dumpLogs: () => ipcRenderer.invoke('dump-logs')
    },

    // Logger proxy: forward logs to main process and console
    logger: {
        info: (...args) => { try { ipcRenderer.send('renderer:log', 'info', ...args); } catch (e) {} ; console.info(...args); },
        warn: (...args) => { try { ipcRenderer.send('renderer:log', 'warn', ...args); } catch (e) {} ; console.warn(...args); },
        error: (...args) => { try { ipcRenderer.send('renderer:log', 'error', ...args); } catch (e) {} ; console.error(...args); },
        debug: (...args) => { try { ipcRenderer.send('renderer:log', 'debug', ...args); } catch (e) {} ; console.debug(...args); }
    },

    // Devtools helper
    devtools: {
        open: () => ipcRenderer.send('open-devtools')
    },
    
    // Recent verifications
    recent: {
        get: () => ipcRenderer.invoke('recent:get'),
        add: (verification) => ipcRenderer.invoke('recent:add', verification),
        clear: () => ipcRenderer.invoke('recent:clear'),
        delete: (id) => ipcRenderer.invoke('recent:delete', id),
        save: (items) => ipcRenderer.invoke('recent:save', items)
    },
    
    // API configuration
    api: {
        getEndpoint: () => ipcRenderer.invoke('api:getEndpoint'),
        setEndpoint: (endpoint) => ipcRenderer.invoke('api:setEndpoint', endpoint)
    },
    
    // Theme
    theme: {
        get: () => ipcRenderer.invoke('theme:get'),
        set: (theme) => ipcRenderer.invoke('theme:set', theme)
    },

    // Overlay helper (for always-on-top quick verify overlay)
    overlay: {
        verify: (text) => ipcRenderer.send('overlay:verify', text),
        toggle: () => ipcRenderer.send('overlay:toggle')
    },
    
    // Event listeners
    on: {
        navigate: (callback) => {
            const handler = (_, page) => callback(page);
            ipcRenderer.on('navigate', handler);
            return () => ipcRenderer.removeListener('navigate', handler);
        },
        quickVerify: (callback) => {
            const handler = (_, text) => callback(text);
            ipcRenderer.on('quick-verify', handler);
            return () => ipcRenderer.removeListener('quick-verify', handler);
        },
        toggleSidebar: (callback) => {
            ipcRenderer.on('toggle-sidebar', callback);
            return () => ipcRenderer.removeListener('toggle-sidebar', callback);
        },
        updateAvailable: (callback) => {
            const handler = (_, info) => callback(info);
            ipcRenderer.on('update-available', handler);
            return () => ipcRenderer.removeListener('update-available', handler);
        },
        updateDownloaded: (callback) => {
            ipcRenderer.on('update-downloaded', callback);
            return () => ipcRenderer.removeListener('update-downloaded', callback);
        },
        exportHistory: (callback) => {
            const handler = (_, data) => callback(data);
            ipcRenderer.on('export-history', handler);
            return () => ipcRenderer.removeListener('export-history', handler);
        },
        importHistory: (callback) => {
            const handler = (_, data) => callback(data);
            ipcRenderer.on('import-history', handler);
            return () => ipcRenderer.removeListener('import-history', handler);
        },
        deepLink: (callback) => {
            const handler = (_, url) => callback(url);
            ipcRenderer.on('deep-link', handler);
            return () => ipcRenderer.removeListener('deep-link', handler);
        },
        systemSuspend: (callback) => {
            ipcRenderer.on('system-suspend', callback);
            return () => ipcRenderer.removeListener('system-suspend', callback);
        },
        systemResume: (callback) => {
            ipcRenderer.on('system-resume', callback);
            return () => ipcRenderer.removeListener('system-resume', callback);
        },
        sessionLock: (callback) => {
            ipcRenderer.on('session-lock', callback);
            return () => ipcRenderer.removeListener('session-lock', callback);
        }
    }
});

// ============================================
// DOM Ready Handler
// ============================================
window.addEventListener('DOMContentLoaded', () => {
    // Platform-specific styling
    document.body.classList.add(`platform-${process.platform}`);
    
    // Prevent default drag & drop behavior
    document.addEventListener('dragover', (e) => e.preventDefault());
    document.addEventListener('drop', (e) => e.preventDefault());
    
    // Context menu prevention for non-editable elements
    document.addEventListener('contextmenu', (e) => {
        const target = e.target;
        if (!target.matches('input, textarea, [contenteditable="true"]')) {
            e.preventDefault();
        }
    });
});

// ============================================
// Security: Disable dangerous features
// ============================================
// Note: These are already disabled via webPreferences, but belt-and-suspenders
delete window.eval;

// Prevent accidental exposure of Node APIs
Object.freeze(window.verity);
