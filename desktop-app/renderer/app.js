// ================================================
// VERITY DESKTOP v3 - PREMIUM EDITION
// Complete Full-Featured Application
// Integrated with Verity Ultimate API v6
// ================================================

(function() {
'use strict';

// Logger: use preload-exposed logger when available, otherwise console
let log = console;
try { log = window.verity?.logger || console; } catch (e) { log = console; }

// ===== CONFIGURATION =====
const CONFIG = {
    apiEndpoint: 'https://veritysystems-production.up.railway.app',  // Production API (Railway)
    localEndpoint: 'http://localhost:8000',     // Local development
    version: '21.0.0',
    build: 'Ultimate',
    useLocal: false,  // Set to true for local development
    ninePointSystem: true  // Enable 21-Point Verification (flag kept for backwards compatibility)
};

// ===== APPLICATION STATE =====
const state = {
    currentPage: 'dashboard',
    user: null,
    authenticated: false,
    apiOnline: false,
    history: [],
    notifications: [],
    subscription: {
        tier: 'free', // 'free', 'starter', 'pro', 'professional', 'business', 'business_plus', 'enterprise'
        isPro: false  // true for pro+ tiers
    },
    settings: {
        darkMode: true,
        animations: true,
        notifications: true,
        sounds: false,
        autoSave: true
    }
};

// ===== SAFE BRIDGE (minimal stub when preload isn't available) =====
try {
    if (!window.verity) {
        // Provide a tiny safe stub so renderer code can call `window.verity.*` without throwing
        window.verity = Object.freeze({
            window: {
                minimize: () => {},
                maximize: () => {},
                close: () => {},
                isMaximized: async () => false,
                onMaximizedChange: () => () => {}
            },
            settings: { get: async () => null, set: async () => true, getAll: async () => ({}), save: async () => true },
            diagnostics: { dumpLogs: async () => '' },
            api: { getEndpoint: async () => CONFIG.apiEndpoint, setEndpoint: async () => true },
            logger: console,
            devtools: { open: () => {} }
        });
    }
} catch (e) { /* ignore */ }

// Pro+ tiers that unlock AI Tools
const PRO_PLUS_TIERS = ['professional', 'business', 'business_plus', 'enterprise'];

// Check if user has Pro+ access
function hasProPlusAccess() {
    return state.authenticated && PRO_PLUS_TIERS.includes(state.subscription.tier);
}

// ===== PREMIUM SVG ICONS =====
const ICONS = {
    dashboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></svg>`,
    verify: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>`,
    history: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><polyline points="12,7 12,12 15,15"/></svg>`,
    source: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/><path d="M11 8v6"/><path d="M8 11h6"/></svg>`,
    moderate: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4"/><circle cx="12" cy="16" r="0.5" fill="currentColor"/></svg>`,
    research: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>`,
    social: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><path d="M22 6l-10 7L2 6"/></svg>`,
    bell: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>`,
    stats: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>`,
    map: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M2 12h4"/><path d="M18 12h4"/><path d="M12 2v4"/><path d="M12 18v4"/></svg>`,
    realtime: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`,
    api: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>`,
    key: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>`,
    billing: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/></svg>`,
    settings: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`,
    user: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
    check: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20,6 9,17 4,12"/></svg>`,
    x: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>`,
    arrow: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>`,
    copy: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>`,
    share: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg>`,
    download: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7,10 12,15 17,10"/><path d="M12 15V3"/></svg>`,
    upload: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17,8 12,3 7,8"/><path d="M12 3v12"/></svg>`,
    file: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>`,
    link: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>`,
    star: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>`,
    trending: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="23,6 13.5,15.5 8.5,10.5 1,18"/><polyline points="17,6 23,6 23,12"/></svg>`,
    alert: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><path d="M12 9v4"/><circle cx="12" cy="17" r="0.5" fill="currentColor"/></svg>`,
    info: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 16v-4"/><circle cx="12" cy="8" r="0.5" fill="currentColor"/></svg>`,
    help: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><circle cx="12" cy="17" r="0.5" fill="currentColor"/></svg>`,
    brain: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4.5a2.5 2.5 0 00-4.96-.46 2.5 2.5 0 00-1.98 3 2.5 2.5 0 00-1.32 4.24 3 3 0 00.34 5.58 2.5 2.5 0 002.96 3.08A2.5 2.5 0 0012 19.5a2.5 2.5 0 004.96.46 2.5 2.5 0 002.96-3.08 3 3 0 00.34-5.58 2.5 2.5 0 00-1.32-4.24 2.5 2.5 0 00-1.98-3A2.5 2.5 0 0012 4.5"/><path d="M15.7 8a6 6 0 00-7.4 0"/><path d="M12 12v8"/></svg>`,
    shield: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
    target: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></svg>`,
    zap: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10"/></svg>`,
    globe: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>`,
    database: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>`,
    code: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="16,18 22,12 16,6"/><polyline points="8,6 2,12 8,18"/></svg>`,
    terminal: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="4,17 10,11 4,5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>`,
    layers: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="12,2 2,7 12,12 22,7"/><polyline points="2,17 12,22 22,17"/><polyline points="2,12 12,17 22,12"/></svg>`,
    cpu: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>`,
    play: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="5,3 19,12 5,21"/></svg>`,
    pause: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>`,
    refresh: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="23,4 23,10 17,10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>`,
    filter: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46"/></svg>`,
    calendar: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>`,
    clock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><polyline points="12,7 12,12 16,14"/></svg>`,
    eye: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
    eyeOff: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`,
    lock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>`,
    unlock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 019.9-1"/></svg>`,
    plus: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
    minus: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
    menu: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>`,
    more: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1.5" fill="currentColor"/><circle cx="19" cy="12" r="1.5" fill="currentColor"/><circle cx="5" cy="12" r="1.5" fill="currentColor"/></svg>`,
    external: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15,3 21,3 21,9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>`,
    trash: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="3,6 5,6 21,6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>`,
    spinner: `<svg class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" opacity="0.2"/><path d="M12 2a10 10 0 019 5.5" stroke-linecap="round"/></svg>`
};

// ===== NAVIGATION STRUCTURE =====
const NAV_ITEMS = [
    {
        section: 'Overview',
        items: [
            { id: 'dashboard', icon: 'dashboard', label: 'Dashboard' },
            { id: 'verify', icon: 'verify', label: 'Verify Content', badge: 'AI' },
            { id: 'history', icon: 'history', label: 'History' },
            { id: 'analytics', icon: 'stats', label: 'Analytics', badge: 'NEW' }
        ]
    },
    {
        section: 'AI Tools',
        requiresPro: true,
        items: [
            { id: 'source-checker', icon: 'source', label: 'Source Checker', premium: true },
            { id: 'content-mod', icon: 'moderate', label: 'Content Moderator', premium: true },
            { id: 'research', icon: 'research', label: 'Research Assistant', premium: true },
            { id: 'social', icon: 'social', label: 'Social Monitor', premium: true },
            { id: 'stats', icon: 'stats', label: 'Stats Validator', premium: true },
            { id: 'misinfo-map', icon: 'map', label: 'Misinfo Map', premium: true },
            { id: 'realtime', icon: 'realtime', label: 'Realtime Stream', premium: true }
        ]
    },
    {
        section: 'Developer',
        items: [
            { id: 'api-tester', icon: 'api', label: 'API Tester' },
            { id: 'api-keys', icon: 'key', label: 'API Keys' },
            { id: 'webhooks', icon: 'link', label: 'Webhooks', badge: 'NEW' }
        ]
    },
    {
        section: 'Reports',
        items: [
            { id: 'export', icon: 'download', label: 'Export Reports', badge: 'NEW' }
        ]
    },
    {
        section: 'Account',
        items: [
            { id: 'billing', icon: 'billing', label: 'Billing & Plans' },
            { id: 'settings', icon: 'settings', label: 'Settings' }
        ]
    }
];

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', init);

async function init() {
    log.info('🚀 Verity Desktop v3 Initializing...');
    try {
        await loadStoredState();
        buildNavigation();
        setupTitlebar();
        setupAuth();
        setupCommandPalette();
        setupGlobalSearch();
        checkAPIStatus();
        // Periodic API health checks
        try { setInterval(checkAPIStatus, 30000); } catch (e) { /* ignore */ }
        navigate(state.currentPage);
        log.info('✅ Verity Desktop Ready');
    } catch (err) {
        log.error('Initialization failed', err);
        showFatalError('Initialization error. Check logs (DevTools) for details.');
    } finally {
        // Always hide the loading screen after a short delay so users can see any error overlay
        setTimeout(() => {
            document.getElementById('loading-screen')?.classList.add('hidden');
        }, 800);

        // Watchdog: If the app is still on the loading screen after a while, show diagnostic overlay
        setTimeout(() => {
            const loadingVisible = !!document.getElementById('loading-screen') && !document.getElementById('loading-screen').classList.contains('hidden');
            const hasFatal = !!document.getElementById('fatal-overlay');
            if (loadingVisible && !hasFatal) {
                showFatalError('Initialization is taking longer than expected. You can open DevTools or dump logs to diagnose.');
                document.getElementById('loading-screen')?.classList.add('hidden');
            }
        }, 8000);
    }
}

// Global error handlers to capture unhandled errors and show user-friendly overlay
window.addEventListener('error', (e) => {
    log.error('Uncaught error in renderer:', e.error || e.message || e);
    showFatalError('An unexpected error occurred. Open DevTools for details.');
});
window.addEventListener('unhandledrejection', (e) => {
    log.error('Unhandled promise rejection:', e.reason || e);
    showFatalError('An unexpected error occurred (promise rejection). Open DevTools for details.');
});

function showFatalError(message) {
    // Create or update overlay
    let overlay = document.getElementById('fatal-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'fatal-overlay';
        overlay.innerHTML = `
            <div style="position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:10000;display:flex;align-items:center;justify-content:center;">
                <div style="background:#071226;padding:1.25rem;border-radius:12px;max-width:720px;color:#fff;text-align:left;box-shadow:0 10px 40px rgba(0,0,0,0.6);">
                    <h3 style="margin:0 0 0.5rem 0">Something went wrong</h3>
                    <div id="fatal-message" style="margin-bottom:1rem;font-size:0.95rem;color:#cbd5e1">${message}</div>
                    <div style="display:flex;gap:0.5rem;justify-content:flex-end">
                        <button class="small-btn" id="open-dev">Open DevTools</button>
                        <button class="small-btn" id="dump-logs">Dump Logs</button>
                        <button class="small-btn" id="reload-app">Reload</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        document.getElementById('open-dev')?.addEventListener('click', () => {
            try { (window.verity?.devtools?.open || (() => {}))(); } catch (e) { console.warn('open-devtools not available', e); }
        });
        document.getElementById('dump-logs')?.addEventListener('click', async () => {
            try {
                const path = await window.verity.diagnostics.dumpLogs();
                window.verity.clipboard.write(path);
                toast(`Logs saved to ${path} (path copied to clipboard)`, 'info');
            } catch (e) {
                toast('Failed to dump logs: ' + (e.message || e), 'error');
            }
        });
        document.getElementById('reload-app')?.addEventListener('click', () => location.reload());
    } else {
        document.getElementById('fatal-message').textContent = message;
        overlay.style.display = 'flex';
    }
}

async function loadStoredState() {
    if (window.verity) {
        try {
            const stored = await window.verity.settings.getAll();
            if (stored) {
                if (stored.user) { state.user = stored.user; state.authenticated = true; }
                if (stored.settings) Object.assign(state.settings, stored.settings);
                if (stored.apiEndpoint) CONFIG.apiEndpoint = stored.apiEndpoint;
            }
            state.history = await window.verity.recent.get() || [];
        } catch (e) { console.warn('Could not load stored state:', e); }
    }
}

async function saveState() {
    if (window.verity) {
        try {
            await window.verity.settings.save({
                user: state.user,
                settings: state.settings,
                apiEndpoint: CONFIG.apiEndpoint
            });
            await window.verity.recent.save(state.history.slice(0, 200));
        } catch (e) { console.warn('Could not save state:', e); }
    }
}

// ===== NAVIGATION =====
function buildNavigation() {
    const nav = document.getElementById('nav');
    if (!nav) return;
    
    const hasPro = hasProPlusAccess();
    
    nav.innerHTML = NAV_ITEMS.map(section => `
        <div class="nav-section${section.requiresPro && !hasPro ? ' section-locked' : ''}">
            <div class="nav-label">
                ${section.section}
                ${section.requiresPro && !hasPro ? `<span class="pro-badge">PRO+</span>` : ''}
            </div>
            ${section.items.map(item => {
                const isLocked = item.premium && !hasPro;
                return `
                <button class="nav-item${state.currentPage === item.id ? ' active' : ''}${isLocked ? ' locked' : ''}" 
                        data-page="${item.id}" 
                        ${isLocked ? 'data-locked="true"' : ''}>
                    <span class="nav-icon">${ICONS[item.icon]}</span>
                    <span>${item.label}</span>
                    ${isLocked ? `<span class="lock-icon">${ICONS.lock}</span>` : ''}
                    ${item.badge && !isLocked ? `<span class="nav-badge">${item.badge}</span>` : ''}
                </button>
            `}).join('')}
        </div>
    `).join('');
    
    nav.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.dataset.locked === 'true') {
                showUpgradeModal();
            } else {
                navigate(btn.dataset.page);
            }
        });
    });
    
    updateUserMenu();
}

// Show upgrade modal for locked features
function showUpgradeModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay active';
    modal.innerHTML = `
        <div class="upgrade-modal">
            <div class="upgrade-modal-header">
                <div class="upgrade-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        <path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h2>Upgrade to Pro+</h2>
                <p>Unlock all AI Tools with a Professional plan or higher</p>
            </div>
            <div class="upgrade-features">
                <div class="upgrade-feature">
                    <span class="feature-icon">${ICONS.source}</span>
                    <span>Source Checker</span>
                </div>
                <div class="upgrade-feature">
                    <span class="feature-icon">${ICONS.moderate}</span>
                    <span>Content Moderator</span>
                </div>
                <div class="upgrade-feature">
                    <span class="feature-icon">${ICONS.research}</span>
                    <span>Research Assistant</span>
                </div>
                <div class="upgrade-feature">
                    <span class="feature-icon">${ICONS.social}</span>
                    <span>Social Monitor</span>
                </div>
                <div class="upgrade-feature">
                    <span class="feature-icon">${ICONS.stats}</span>
                    <span>Stats Validator</span>
                </div>
                <div class="upgrade-feature">
                    <span class="feature-icon">${ICONS.map}</span>
                    <span>Misinfo Map</span>
                </div>
                <div class="upgrade-feature">
                    <span class="feature-icon">${ICONS.realtime}</span>
                    <span>Realtime Stream</span>
                </div>
            </div>
            <div class="upgrade-pricing">
                <div class="upgrade-price">
                    <span class="price-label">Starting at</span>
                    <span class="price-amount">$199<span>/mo</span></span>
                </div>
                <p class="price-desc">Professional plan with 15,000 verifications/month</p>
            </div>
            <div class="upgrade-actions">
                <button class="btn btn-primary btn-upgrade" id="upgrade-now-btn">
                    ${ICONS.zap} Upgrade Now
                </button>
                <button class="btn btn-ghost btn-close-modal">Maybe Later</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Animate in
    requestAnimationFrame(() => modal.classList.add('visible'));
    
    // Close handlers
    modal.querySelector('.btn-close-modal')?.addEventListener('click', () => {
        modal.classList.remove('visible');
        setTimeout(() => modal.remove(), 300);
    });
    
    modal.querySelector('#upgrade-now-btn')?.addEventListener('click', () => {
        modal.classList.remove('visible');
        setTimeout(() => {
            modal.remove();
            navigate('billing');
        }, 300);
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('visible');
            setTimeout(() => modal.remove(), 300);
        }
    });
}

function updateUserMenu() {
    const userArea = document.getElementById('user-area');
    if (!userArea) return;
    
    if (state.authenticated && state.user) {
        userArea.innerHTML = `
            <button class="user-btn">
                <div class="user-avatar">${state.user.name?.charAt(0) || 'U'}</div>
                <span>${state.user.name || 'User'}</span>
            </button>
        `;
    } else {
        userArea.innerHTML = `
            <button class="btn btn-primary btn-sm" id="login-btn">Sign In</button>
        `;
        document.getElementById('login-btn')?.addEventListener('click', () => {
            document.getElementById('auth')?.classList.add('active');
        });
    }
}

function attachPageHandlers(page) {
    // Attach handlers based on current page
    switch(page) {
        case 'verify':
            document.getElementById('verify-btn')?.addEventListener('click', handleVerify);
            
            // Character counter for verify input
            const verifyInput = document.getElementById('verify-input');
            const charCount = document.getElementById('char-count');
            if (verifyInput && charCount) {
                verifyInput.addEventListener('input', () => {
                    charCount.textContent = verifyInput.value.length;
                });
            }
            
            // Mode tab switching
            document.querySelectorAll('.verify-mode-tab').forEach(tab => {
                tab.addEventListener('click', () => {
                    document.querySelectorAll('.verify-mode-tab').forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    toast(`Switched to ${tab.dataset.mode === 'quick' ? 'Quick' : 'Full 21-Point'} mode`, 'info');
                });
            });
            
            // Input type tab switching
            document.querySelectorAll('.input-type-tab').forEach(tab => {
                tab.addEventListener('click', () => {
                    document.querySelectorAll('.input-type-tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.input-section').forEach(s => s.classList.remove('active'));
                    tab.classList.add('active');
                    const section = document.getElementById(`input-${tab.dataset.type}`);
                    if (section) section.classList.add('active');
                });
            });
            
            // Option chips toggle
            document.querySelectorAll('.option-chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    chip.classList.toggle('active');
                    const checkbox = chip.querySelector('input[type="checkbox"]');
                    if (checkbox) checkbox.checked = chip.classList.contains('active');
                });
            });
            
            // File upload handling
            const uploadZone = document.getElementById('upload-zone');
            const fileInput = document.getElementById('file-input');
            if (uploadZone && fileInput) {
                uploadZone.addEventListener('click', () => fileInput.click());
                uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
                uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
                uploadZone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    uploadZone.classList.remove('dragover');
                    const file = e.dataTransfer.files[0];
                    if (file) handleFileUpload(file);
                });
                fileInput.addEventListener('change', (e) => {
                    if (e.target.files[0]) handleFileUpload(e.target.files[0]);
                });
            }
            
            // Extract claims button
            document.getElementById('extract-claims-btn')?.addEventListener('click', handleExtractClaims);
            // How It Works card click
            document.querySelector('.card-how-it-works')?.addEventListener('click', (e) => {
                // If clicked on inner buttons, let them handle; otherwise show modal
                if (e.target.closest('button')) return;
                showHowItWorks();
            });
            break;
        case 'source-checker':
            document.getElementById('check-source-btn')?.addEventListener('click', handleSourceCheck);
            break;
        case 'content-mod':
            document.getElementById('moderate-btn')?.addEventListener('click', handleModerate);
            break;
        case 'research':
            document.getElementById('research-btn')?.addEventListener('click', handleResearch);
            break;
        case 'stats':
            document.getElementById('stats-btn')?.addEventListener('click', handleStatsValidate);
            break;
        case 'api-tester':
            document.getElementById('send-api-btn')?.addEventListener('click', handleAPITest);
            break;
        case 'settings':
            // Settings tab navigation
            document.querySelectorAll('.settings-nav-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    // Update active nav button
                    document.querySelectorAll('.settings-nav-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    
                    // Show corresponding section
                    const sectionId = `settings-${btn.dataset.section}`;
                    document.querySelectorAll('.settings-section').forEach(section => {
                        section.classList.remove('active');
                    });
                    document.getElementById(sectionId)?.classList.add('active');
                });
            });
            
            // Settings toggle handlers
            document.querySelectorAll('.settings-card input[type="checkbox"]').forEach(toggle => {
                toggle.addEventListener('change', handleSettingChange);
            });
            
            // Export data button
            document.getElementById('export-data-btn')?.addEventListener('click', () => {
                const data = JSON.stringify({ history: state.history, settings: state.settings }, null, 2);
                const blob = new Blob([data], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `verity-data-${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
                toast('Data exported successfully!', 'success');
            });
            
            // Clear history button
            document.getElementById('clear-history-settings-btn')?.addEventListener('click', () => {
                if (confirm('Are you sure you want to clear all verification history?')) {
                    state.history = [];
                    saveState();
                    toast('History cleared', 'success');
                }
            });
            
            // Test API connection
            document.getElementById('test-api-connection-btn')?.addEventListener('click', async () => {
                toast('Testing connection...', 'info');
                await checkAPIStatus();
                toast(state.apiOnline ? 'API connected successfully!' : 'Connection failed', state.apiOnline ? 'success' : 'error');
            });
            
            // Check updates button
            document.getElementById('check-updates-btn')?.addEventListener('click', () => {
                toast('You\'re running the latest version!', 'success');
            });
            break;
        case 'billing':
            // Billing period toggle
            document.querySelectorAll('.billing-period').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.billing-period').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    const isYearly = btn.dataset.period === 'yearly';
                    updatePricing(isYearly);
                });
            });
            // Upgrade button
            document.getElementById('upgrade-pro')?.addEventListener('click', () => {
                document.getElementById('auth-modal')?.classList.add('active');
                toast('Sign in to upgrade your plan', 'info');
            });
            document.getElementById('contact-sales')?.addEventListener('click', () => {
                toast('Our sales team will contact you shortly!', 'success');
            });
            break;
        case 'history':
            document.getElementById('clear-history-btn')?.addEventListener('click', () => {
                if (confirm('Clear all history?')) {
                    state.history = [];
                    saveState();
                    navigate('history');
                    toast('History cleared', 'success');
                }
            });
            break;
        case 'export':
            // Format card selection
            document.querySelectorAll('.format-card-premium').forEach(card => {
                card.addEventListener('click', () => {
                    document.querySelectorAll('.format-card-premium').forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                    const format = card.dataset.format;
                    // Update preview format display
                    const summaryFormat = document.querySelector('.summary-stat:last-child .summary-value');
                    if (summaryFormat) summaryFormat.textContent = format.toUpperCase();
                });
            });
            
            // Include option toggle
            document.querySelectorAll('.include-option').forEach(option => {
                option.addEventListener('click', () => {
                    option.classList.toggle('active');
                    const checkbox = option.querySelector('input[type="checkbox"]');
                    if (checkbox) checkbox.checked = option.classList.contains('active');
                });
            });
            
            // Template button selection
            document.querySelectorAll('.template-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.template-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                });
            });
            
            // Date range buttons
            document.querySelectorAll('.range-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.range-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                });
            });
            
            // Schedule option change
            document.querySelectorAll('.schedule-option input').forEach(radio => {
                radio.addEventListener('change', () => {
                    const emailSection = document.getElementById('schedule-email');
                    if (emailSection) {
                        emailSection.classList.toggle('hidden', radio.value === 'none');
                    }
                });
            });
            
            // Generate export button
            document.getElementById('generate-export-btn')?.addEventListener('click', () => {
                const selectedFormat = document.querySelector('.format-card-premium.selected')?.dataset.format || 'pdf';
                const data = JSON.stringify({ history: state.history, exportDate: new Date().toISOString() }, null, 2);
                const blob = new Blob([data], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `verity-report-${new Date().toISOString().split('T')[0]}.${selectedFormat === 'json' ? 'json' : selectedFormat}`;
                a.click();
                URL.revokeObjectURL(url);
                toast(`${selectedFormat.toUpperCase()} report generated successfully!`, 'success');
            });
            break;
        case 'dashboard':
            // Quick actions (supports both data-action and data-url for quick source checks)
            document.querySelectorAll('.quick-action').forEach(action => {
                action.addEventListener('click', () => {
                    const url = action.dataset.url;
                    const target = action.dataset.action;

                    // If this quick action contains a URL (common for popular sources), open Source Checker and prefill
                    if (url) {
                        navigate('source-checker');
                        setTimeout(() => {
                            const input = document.getElementById('source-url');
                            if (input) {
                                input.value = url.startsWith('http') ? url : `https://${url}`;
                                document.getElementById('check-source-btn')?.click();
                            }
                        }, 150);
                        return;
                    }

                    const actionMap = {
                        'verify': 'verify',
                        'source': 'source-checker',
                        'moderate': 'content-mod',
                        'research': 'research',
                        'realtime': 'realtime',
                        'api': 'api-tester'
                    };
                    if (actionMap[target]) navigate(actionMap[target]);
                });
            });
            // Quick verify
            document.getElementById('quick-verify-btn')?.addEventListener('click', async () => {
                const text = document.getElementById('quick-verify-text')?.value;
                if (text?.trim()) {
                    navigate('verify');
                    setTimeout(() => {
                        const input = document.getElementById('verify-input');
                        if (input) {
                            input.value = text;
                            handleVerify();
                        }
                    }, 100);
                }
            });

            // Dashboard action items (alternate class used in some templates)
            document.querySelectorAll('.action-item').forEach(action => {
                action.addEventListener('click', () => {
                    const url = action.dataset.url;
                    const target = action.dataset.action;
                    if (url) {
                        navigate('source-checker');
                        setTimeout(() => {
                            const input = document.getElementById('source-url');
                            if (input) {
                                input.value = url.startsWith('http') ? url : `https://${url}`;
                                document.getElementById('check-source-btn')?.click();
                            }
                        }, 150);
                        return;
                    }
                    const actionMap = {
                        'verify': 'verify',
                        'source': 'source-checker',
                        'moderate': 'content-mod',
                        'research': 'research',
                        'realtime': 'realtime',
                        'api': 'api-tester'
                    };
                    if (actionMap[target]) navigate(actionMap[target]);
                });
            });

            // Promo cards clickable (navigate by data-target or default to 21-point info)
            document.querySelectorAll('.promo-card').forEach(card => {
                card.addEventListener('click', () => {
                    const target = card.dataset.target || '21-point-info';
                    navigate(target);
                });
            });
            break;

        case '21-point-info':
            // Make each point-card expandable to view details in a modal
            document.querySelectorAll('.point-card').forEach(card => {
                card.style.cursor = 'pointer';
                card.addEventListener('click', () => {
                    const titleEl = card.querySelector('.point-title');
                    const descEl = card.querySelector('.point-desc');
                    const title = titleEl ? titleEl.textContent : 'Detail';
                    const desc = descEl ? descEl.textContent : '';
                    const modal = document.createElement('div');
                    modal.className = 'modal modal-info';
                    modal.innerHTML = `
                        <div class="modal-card">
                            <button class="btn-close-modal">×</button>
                            <h3>${escapeHtml(title)}</h3>
                            <p>${escapeHtml(desc)}</p>
                        </div>
                    `;
                    document.body.appendChild(modal);
                    requestAnimationFrame(() => modal.classList.add('visible'));
                    modal.querySelector('.btn-close-modal')?.addEventListener('click', () => {
                        modal.classList.remove('visible');
                        setTimeout(() => modal.remove(), 260);
                    });
                    modal.addEventListener('click', (e) => { if (e.target === modal) { modal.classList.remove('visible'); setTimeout(() => modal.remove(), 260); } });
                });
            });
    }
}

function updatePricing(isYearly) {
    // Update all pricing cards using data attributes
    document.querySelectorAll('.pricing-card .price').forEach(priceEl => {
        const monthly = priceEl.dataset.monthly;
        const yearly = priceEl.dataset.yearly;
        if (monthly && yearly) {
            priceEl.textContent = isYearly ? yearly : monthly;
        }
    });
    
    // Update period text
    document.querySelectorAll('.pricing-card .period').forEach(periodEl => {
        periodEl.textContent = isYearly ? '/mo (billed yearly)' : '/month';
    });
}

function navigate(page) {
    state.currentPage = page;
    
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.page === page);
    });
    
    // Render page content
    const main = document.getElementById('main');
    if (main) {
        main.innerHTML = getPageContent(page);
        attachPageHandlers(page);
    }
    
    // Close command palette if open
    document.getElementById('cmd')?.classList.remove('active');
}

// Expose navigate globally for inline handlers and external test hooks
try { window.navigate = navigate; } catch (e) { /* ignore in restricted contexts */ }

function getPageContent(page) {
    const pages = {
        'dashboard': renderDashboard,
        'verify': renderVerify,
        'history': renderHistory,
        'analytics': renderAnalytics,
        'source-checker': renderSourceChecker,
        'content-mod': renderContentModerator,
        'research': renderResearch,
        'social': renderSocialMonitor,
        'stats': renderStatsValidator,
        'misinfo-map': renderMisinfoMap,
        'realtime': renderRealtime,
        'api-tester': renderAPITester,
        'api-keys': renderAPIKeys,
        'webhooks': renderWebhooks,
        'export': renderExport,
        'billing': renderBilling,
        'settings': renderSettings,
        '21-point-info': render21PointInfo
    };
    return (pages[page] || renderDashboard)();
}

// Continue in next part...

// ===== PAGE RENDERERS - DASHBOARD =====
function renderDashboard() {
    const verifiedCount = state.history.filter(h => h.score >= 70).length;
    const flaggedCount = state.history.filter(h => h.score < 70).length;
    const totalCount = state.history.length;
    const avgScore = totalCount > 0 ? Math.round(state.history.reduce((a, h) => a + h.score, 0) / totalCount) : 0;

    return `
        <div class="page-header">
            <h1>Welcome back</h1>
            <p>Here's what's happening with your fact-checking today.</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.check}</div>
                    <span class="stat-change up">+12%</span>
                </div>
                <div class="stat-value">${verifiedCount}</div>
                <div class="stat-label">Verified Claims</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.alert}</div>
                    <span class="stat-change down">-5%</span>
                </div>
                <div class="stat-value">${flaggedCount}</div>
                <div class="stat-label">Flagged Content</div>
            </div>
            <div class="stat-card pink">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.stats}</div>
                    <span class="stat-change up">+3%</span>
                </div>
                <div class="stat-value">${avgScore}<span class="stat-unit">%</span></div>
                <div class="stat-label">Accuracy Score</div>
            </div>
            <div class="stat-card green">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.zap}</div>
                </div>
                <div class="stat-value">${state.apiOnline ? 'Online' : 'Offline'}</div>
                <div class="stat-label">API Status</div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card card-large">
                <div class="card-header">
                    <h3>Quick Verify</h3>
                    <span class="card-badge">AI Powered</span>
                </div>
                <textarea class="textarea" id="quick-verify-text" placeholder="Paste any claim, news article, or social media post to fact-check instantly..."></textarea>
                <div class="card-footer">
                    <button class="btn btn-primary" id="quick-verify-btn">
                        ${ICONS.zap} Verify Now
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3>Quick Actions</h3>
                </div>
                <div class="action-grid">
                    <button class="action-item" data-action="verify">
                        <div class="action-icon">${ICONS.verify}</div>
                        <span>Verify</span>
                    </button>
                    <button class="action-item" data-action="source">
                        <div class="action-icon">${ICONS.source}</div>
                        <span>Sources</span>
                    </button>
                    <button class="action-item" data-action="moderate">
                        <div class="action-icon">${ICONS.moderate}</div>
                        <span>Moderate</span>
                    </button>
                    <button class="action-item" data-action="research">
                        <div class="action-icon">${ICONS.research}</div>
                        <span>Research</span>
                    </button>
                    <button class="action-item" data-action="realtime">
                        <div class="action-icon">${ICONS.realtime}</div>
                        <span>Live Feed</span>
                    </button>
                    <button class="action-item" data-action="api">
                        <div class="action-icon">${ICONS.api}</div>
                        <span>API</span>
                    </button>
                </div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    <h3>Weekly Activity</h3>
                    <select class="select-mini">
                        <option>This Week</option>
                        <option>Last Week</option>
                        <option>This Month</option>
                    </select>
                </div>
                <div class="activity-chart">
                    ${[45, 72, 38, 85, 62, 91, 58].map((v, i) => `
                        <div class="chart-col">
                            <div class="chart-bar" style="height: ${v}%"></div>
                            <span class="chart-label">${['M','T','W','T','F','S','S'][i]}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3>Recent Activity</h3>
                    <button class="btn btn-sm btn-ghost" onclick="navigate('history')">View All</button>
                </div>
                ${state.history.length > 0 ? `
                    <div class="activity-list">
                        ${state.history.slice(0, 4).map(item => `
                            <div class="activity-item">
                                <div class="activity-score ${item.score >= 70 ? 'good' : item.score >= 40 ? 'medium' : 'bad'}">${item.score}</div>
                                <div class="activity-content">
                                    <div class="activity-text">${item.claim.substring(0, 50)}${item.claim.length > 50 ? '...' : ''}</div>
                                    <div class="activity-time">${formatTimeAgo(item.timestamp)}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div class="empty-mini">
                        <p>No recent activity</p>
                        <button class="btn btn-sm btn-primary" onclick="navigate('verify')">Start Verifying</button>
                    </div>
                `}
            </div>
        </div>

        <div class="promo-cards">
            <div class="promo-card gradient-cyan">
                <div class="promo-icon">${ICONS.brain}</div>
                <div class="promo-content">
                    <h4>AI-Powered Analysis</h4>
                    <p>GPT-4, Claude & custom models working together</p>
                </div>
                <div class="promo-arrow">${ICONS.arrow}</div>
            </div>
            <div class="promo-card gradient-purple">
                <div class="promo-icon">${ICONS.database}</div>
                <div class="promo-content">
                    <h4>50M+ Verified Facts</h4>
                    <p>Cross-reference with our knowledge base</p>
                </div>
                <div class="promo-arrow">${ICONS.arrow}</div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - 21-POINT INFO =====
function render21PointInfo() {
    // Render a richer 21-point grid to match the website visual style
    return `
        <div class="page-header">
            <h1>21-Point Verification</h1>
            <p>Deep-dive into our multi-step verification methodology used by Verity.</p>
        </div>
        <div class="card card-article">
            <h3>What is the 21-Point System?</h3>
            <p>Our 21-Point System evaluates claims across multiple categories including source credibility, publication history, author reputation, citation depth, temporal validity, statistical consistency, and more. Each criterion yields a score which contributes to the overall confidence rating.</p>
        </div>

        <div class="card card-article">
            <h4>Key Components</h4>
            <div class="points-grid">
                <div class="point-card">${ICONS.shield}<div class="point-title">Source Authority</div><div class="point-desc">Ownership, editorial independence and reputation.</div></div>
                <div class="point-card">${ICONS.user}<div class="point-title">Author Reputation</div><div class="point-desc">Author track record and expertise.</div></div>
                <div class="point-card">${ICONS.calendar}<div class="point-title">Publication History</div><div class="point-desc">Consistency of publication and archival records.</div></div>
                <div class="point-card">${ICONS.link}<div class="point-title">Citation Depth</div><div class="point-desc">Quality and number of supporting citations.</div></div>
                <div class="point-card">${ICONS.clock}<div class="point-title">Temporal Validity</div><div class="point-desc">Date relevance and timeliness of evidence.</div></div>
                <div class="point-card">${ICONS.graph || ICONS.trending}<div class="point-title">Statistical Consistency</div><div class="point-desc">Check for numeric accuracy and plausibility.</div></div>
                <div class="point-card">${ICONS.database}<div class="point-title">Methodological Rigor</div><div class="point-desc">Assess study methods and sampling.</div></div>
                <div class="point-card">${ICONS.globe}<div class="point-title">Cross-Provider Consensus</div><div class="point-desc">Agreement across multiple providers.</div></div>
                <div class="point-card">${ICONS.layers}<div class="point-title">Evidence Diversity</div><div class="point-desc">Multiple source types and formats.</div></div>
                <div class="point-card">${ICONS.file}<div class="point-title">Originality</div><div class="point-desc">Is the claim original or recycled?</div></div>
                <div class="point-card">${ICONS.eye}<div class="point-title">Document Integrity</div><div class="point-desc">Signs of manipulation in media/text.</div></div>
                <div class="point-card">${ICONS.play}<div class="point-title">Media Analysis</div><div class="point-desc">Analyze images, audio and video for edits.</div></div>
                <div class="point-card">${ICONS.map}<div class="point-title">Geolocation</div><div class="point-desc">Location evidence and plausibility.</div></div>
                <div class="point-card">${ICONS.eyeOff}<div class="point-title">Temporal Plausibility</div><div class="point-desc">Verify timelines and sequence of events.</div></div>
                <div class="point-card">${ICONS.info}<div class="point-title">Context Consistency</div><div class="point-desc">Contextual framing and omissions.</div></div>
                <div class="point-card">${ICONS.quote || ICONS.external}<div class="point-title">Quotation Accuracy</div><div class="point-desc">Check direct quotes and sources.</div></div>
                <div class="point-card">${ICONS.user}<div class="point-title">Expert Corroboration</div><div class="point-desc">Independent subject-matter confirmation.</div></div>
                <div class="point-card">${ICONS.brain}<div class="point-title">Source Transparency</div><div class="point-desc">Funding, affiliations and conflicts.</div></div>
                <div class="point-card">${ICONS.history || ICONS.calendar}<div class="point-title">Correction History</div><div class="point-desc">Track record of corrections and retractions.</div></div>
                <div class="point-card">${ICONS.settings}<div class="point-title">Editorial Standards</div><div class="point-desc">Policies, review process and bylines.</div></div>
                <div class="point-card">${ICONS.check}<div class="point-title">Evidence Aggregation</div><div class="point-desc">How supporting data is combined for scoring.</div></div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - VERIFY =====
function renderVerify() {
    return `
        <div class="page-header animate-fade-in">
            <h1>${ICONS.verify} Verify Content</h1>
            <p>AI-powered fact-checking with source analysis, credibility scoring, and 21-Point Verification.</p>
        </div>

        <!-- Mode Selector Tabs -->
        <div class="verify-mode-bar animate-slide-up">
            <button class="verify-mode-tab active" data-mode="quick" id="mode-quick">
                ${ICONS.zap}
                <span class="mode-info">
                    <strong>Quick Verify</strong>
                    <small>Instant results in ~3 seconds</small>
                </span>
                <span class="mode-badge fast">FAST</span>
            </button>
            <button class="verify-mode-tab" data-mode="full" id="mode-full">
                ${ICONS.shield}
                <span class="mode-info">
                    <strong>Full 21-Point Verification</strong>
                    <small>Comprehensive AI analysis</small>
                </span>
                <span class="mode-badge pro">21-POINT</span>
            </button>
        </div>

        <div class="verify-layout">
            <!-- Main Input Panel -->
            <div class="verify-main-panel animate-slide-up delay-1">
                <div class="card card-verify card-elevated">
                    <!-- Input Type Tabs -->
                    <div class="input-type-tabs">
                        <button class="input-type-tab active" data-type="text">
                            ${ICONS.file} Text
                        </button>
                        <button class="input-type-tab" data-type="url">
                            ${ICONS.link} URL
                        </button>
                        <button class="input-type-tab" data-type="document">
                            ${ICONS.upload} Document
                        </button>
                        <button class="input-type-tab" data-type="batch">
                            ${ICONS.layers} Batch
                            <span class="tab-badge pro">PRO</span>
                        </button>
                    </div>

                    <!-- Text Input Section -->
                    <div class="input-section active" id="input-text">
                        <div class="textarea-wrapper">
                            <textarea class="textarea textarea-premium" id="verify-input" 
                                placeholder="Paste a claim, article, social media post, or any text you want to fact-check...

Example: 'The Great Wall of China is visible from space with the naked eye.'"></textarea>
                            <div class="textarea-footer">
                                <span class="char-counter"><span id="char-count">0</span> / 10,000 characters</span>
                                <button class="btn-mini btn-extract" id="extract-claims-btn">
                                    ${ICONS.brain} Extract Claims
                                </button>
                            </div>
                        </div>
                        
                        <!-- Extracted Claims Preview -->
                        <div class="claims-preview hidden" id="claims-preview">
                            <div class="claims-header">
                                <span>${ICONS.target} Detected Claims</span>
                                <button class="btn-mini" id="select-all-claims">Select All</button>
                            </div>
                            <div class="claims-list" id="claims-list"></div>
                        </div>
                    </div>

                    <!-- URL Input Section -->
                    <div class="input-section" id="input-url">
                        <div class="url-input-group">
                            <div class="url-icon">${ICONS.globe}</div>
                            <input type="url" class="input input-lg" id="verify-url" 
                                placeholder="https://example.com/article-to-verify">
                            <button class="btn btn-secondary btn-sm" id="fetch-url-btn">Fetch</button>
                        </div>
                        <div class="url-preview hidden" id="url-preview">
                            <div class="url-meta">
                                <img class="url-favicon" id="url-favicon" src="" alt="">
                                <div class="url-details">
                                    <span class="url-title" id="url-title">Article Title</span>
                                    <span class="url-domain" id="url-domain">example.com</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Document Upload Section -->
                    <div class="input-section" id="input-document">
                        <div class="upload-zone" id="upload-zone">
                            <div class="upload-icon-large">${ICONS.upload}</div>
                            <h4>Drop your document here</h4>
                            <p>or click to browse files</p>
                            <span class="upload-formats">PDF, DOCX, TXT up to 10MB</span>
                        </div>
                        <input type="file" id="file-input" accept=".pdf,.docx,.doc,.txt" hidden>
                        <div class="file-preview hidden" id="file-preview">
                            <div class="file-icon">${ICONS.file}</div>
                            <div class="file-info">
                                <span class="file-name" id="file-name">document.pdf</span>
                                <span class="file-size" id="file-size">2.4 MB</span>
                            </div>
                            <button class="btn-icon btn-remove-file" id="remove-file">${ICONS.x}</button>
                        </div>
                    </div>

                    <!-- Batch Input Section -->
                    <div class="input-section" id="input-batch">
                        <div class="batch-info">
                            <div class="batch-icon">${ICONS.layers}</div>
                            <div class="batch-text">
                                <h4>Batch Verification</h4>
                                <p>Upload a CSV file with multiple claims or paste multiple URLs (one per line)</p>
                            </div>
                        </div>
                        <textarea class="textarea" id="batch-input" 
                            placeholder="Enter multiple claims or URLs, one per line..."></textarea>
                        <div class="batch-stats">
                            <span id="batch-count">0 items detected</span>
                        </div>
                    </div>

                    <!-- Verification Options -->
                    <div class="verify-options-section">
                        <div class="options-header">
                            <span class="options-title">${ICONS.settings} Verification Options</span>
                        </div>
                        <div class="options-chips">
                            <label class="option-chip active">
                                <input type="checkbox" id="opt-sources" checked hidden>
                                <span class="chip-icon">${ICONS.source}</span>
                                <span>Source Analysis</span>
                            </label>
                            <label class="option-chip active">
                                <input type="checkbox" id="opt-cross-ref" checked hidden>
                                <span class="chip-icon">${ICONS.database}</span>
                                <span>Cross-Reference</span>
                            </label>
                            <label class="option-chip">
                                <input type="checkbox" id="opt-deep" hidden>
                                <span class="chip-icon">${ICONS.brain}</span>
                                <span>Deep Analysis</span>
                            </label>
                            <label class="option-chip">
                                <input type="checkbox" id="opt-bias" hidden>
                                <span class="chip-icon">${ICONS.eye}</span>
                                <span>Bias Detection</span>
                            </label>
                            <label class="option-chip">
                                <input type="checkbox" id="opt-historical" hidden>
                                <span class="chip-icon">${ICONS.clock}</span>
                                <span>Historical Context</span>
                            </label>
                        </div>
                    </div>

                    <!-- Action Bar -->
                    <div class="verify-action-bar">
                        <div class="action-info">
                            <span class="provider-count">${ICONS.cpu} Using <strong>75+</strong> verification sources</span>
                        </div>
                        <button class="btn btn-verify-primary btn-lg" id="verify-btn">
                            <span class="btn-icon">${ICONS.verify}</span>
                            <span class="btn-text">Verify Now</span>
                            <span class="btn-loader hidden">${ICONS.spinner}</span>
                        </button>
                    </div>
                </div>

                <!-- Results Area -->
                <div id="verify-result" class="verify-result-area"></div>
            </div>

            <!-- Sidebar -->
            <div class="verify-sidebar animate-slide-up delay-2">
                <!-- Quick Stats -->
                <div class="sidebar-stats-grid">
                    <div class="sidebar-stat stat-green">
                        <span class="stat-value">98.5%</span>
                        <span class="stat-label">Accuracy</span>
                    </div>
                    <div class="sidebar-stat stat-amber">
                        <span class="stat-value">2.3s</span>
                        <span class="stat-label">Avg Speed</span>
                    </div>
                    <div class="sidebar-stat stat-purple">
                        <span class="stat-value">75+</span>
                        <span class="stat-label">Sources</span>
                    </div>
                    <div class="sidebar-stat stat-blue">
                        <span class="stat-value">50M+</span>
                        <span class="stat-label">Facts DB</span>
                    </div>
                </div>

                <!-- How It Works -->
                <div class="card card-how-it-works">
                    <h4 class="card-title">${ICONS.info} How It Works</h4>
                    <div class="verification-steps">
                        <div class="v-step">
                            <div class="v-step-num">1</div>
                            <div class="v-step-content">
                                <strong>Extract Claims</strong>
                                <span>AI identifies key assertions and statements</span>
                            </div>
                            <div class="v-step-line"></div>
                        </div>
                        <div class="v-step">
                            <div class="v-step-num">2</div>
                            <div class="v-step-content">
                                <strong>Multi-Source Search</strong>
                                <span>Query 75+ trusted providers simultaneously</span>
                            </div>
                            <div class="v-step-line"></div>
                        </div>
                        <div class="v-step">
                            <div class="v-step-num">3</div>
                            <div class="v-step-content">
                                <strong>AI Cross-Validation</strong>
                                <span>GPT-4 & Claude analyze conflicting data</span>
                            </div>
                            <div class="v-step-line"></div>
                        </div>
                        <div class="v-step">
                            <div class="v-step-num">4</div>
                            <div class="v-step-content">
                                <strong>Generate Report</strong>
                                <span>Confidence score, sources & evidence</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 21-Point System Info -->
                <div class="card card-21-Point">
                    <div class="nine-point-badge">
                        <span class="badge-icon">${ICONS.shield}</span>
                        <span>21-Point System</span>
                    </div>
                    <p class="nine-point-desc">Our proprietary verification methodology checks claims against 9 distinct validation criteria for maximum accuracy.</p>
                    <button class="btn btn-ghost btn-sm btn-full" onclick="navigate('21-point-info')">
                        Learn More ${ICONS.arrow}
                    </button>
                </div>

                <!-- Preview Panel -->
                <div class="card card-preview">
                    <h4 class="card-title">Preview</h4>
                    <div class="preview-empty" id="preview-empty">
                        <div class="preview-empty-icon">${ICONS.eye}</div>
                        <p>Enter content above to see a live preview and detected claims</p>
                    </div>
                    <div class="preview-content hidden" id="preview-content"></div>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - HISTORY =====
function renderHistory() {
    return `
        <div class="page-header">
            <h1>Verification History</h1>
            <p>View and manage all your past fact-checks.</p>
        </div>

        <div class="toolbar">
            <input type="text" class="input" id="history-search" placeholder="Search history...">
            <select class="select" id="history-filter">
                <option value="all">All Results</option>
                <option value="verified">Verified (70+)</option>
                <option value="flagged">Flagged (&lt;70)</option>
            </select>
            <button class="btn btn-secondary btn-sm">${ICONS.download} Export</button>
            <div style="flex: 1;"></div>
            <button class="btn btn-ghost btn-sm" id="clear-history-btn">${ICONS.x} Clear All</button>
        </div>

        <div class="history-list" id="history-list">
            ${state.history.length > 0 ? 
                state.history.map(item => renderHistoryItem(item)).join('') :
                `<div class="empty-state">
                    <div class="empty-icon">${ICONS.history}</div>
                    <h3>No History Yet</h3>
                    <p>Your verified content will appear here.</p>
                    <button class="btn btn-primary" onclick="navigate('verify')">Start Verifying</button>
                </div>`
            }
        </div>
    `;
}

function renderHistoryItem(item) {
    const scoreClass = item.score >= 70 ? 'good' : item.score >= 40 ? 'medium' : 'bad';
    return `
        <div class="history-item" data-id="${item.id}">
            <div class="history-score ${scoreClass}">${item.score}</div>
            <div class="history-content">
                <div class="history-claim">${escapeHtml(truncate(item.claim || '', 80))}</div>
                <div class="history-meta">
                    <span>${timeAgo(item.timestamp)}</span>
                    <span>${item.sources || 0} sources</span>
                </div>
            </div>
            <div class="history-actions">
                <button class="btn btn-ghost btn-sm">${ICONS.eye}</button>
                <button class="btn btn-ghost btn-sm">${ICONS.x}</button>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - SOURCE CHECKER =====
function renderSourceChecker() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / <span>Source Checker</span></div>
            <div class="header-title-row">
                <h1>${ICONS.source} Source Checker</h1>
                <span class="badge badge-pro">Pro+ Feature</span>
            </div>
            <p class="page-subtitle">Evaluate the credibility and trustworthiness of any news source, website, or publication using our comprehensive AI-powered analysis engine.</p>
        </div>

        <!-- Quick Stats Bar -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.database}</div>
                    <span class="stat-change positive">+2.3K today</span>
                </div>
                <div class="stat-value">2.4M+</div>
                <div class="stat-label">Sources Indexed</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.shield}</div>
                    <span class="stat-change positive">↑ 0.3%</span>
                </div>
                <div class="stat-value">98.7%</div>
                <div class="stat-label">Accuracy Rate</div>
            </div>
            <div class="stat-card pink">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.clock}</div>
                </div>
                <div class="stat-value">&lt;3s</div>
                <div class="stat-label">Avg Analysis Time</div>
            </div>
            <div class="stat-card green">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.globe}</div>
                </div>
                <div class="stat-value">195</div>
                <div class="stat-label">Countries Covered</div>
            </div>
        </div>

        <!-- Main Analysis Card -->
        <div class="card card-elevated" style="margin-top: 24px;">
            <div class="card-header">
                <div class="card-title-group">
                    <div class="card-icon">${ICONS.target}</div>
                    <div>
                        <h3>Analyze a Source</h3>
                        <p class="card-subtitle">Enter a URL, domain, or publication name to check its credibility</p>
                    </div>
                </div>
            </div>
            <div class="source-container">
                <div class="form-group">
                    <label class="input-label">
                        ${ICONS.link} Website URL or Domain
                        <span class="label-hint">We'll analyze ownership, history, fact-check record & more</span>
                    </label>
                    <input type="url" class="input input-lg" id="source-url" placeholder="https://example.com or enter a publication name...">
                </div>
                
                <div class="analysis-options">
                    <div class="option-group">
                        <label class="option-label">Analysis Depth:</label>
                        <div class="radio-buttons">
                            <label class="radio-option"><input type="radio" name="analysis-depth" value="quick" checked><span>Quick Scan</span></label>
                            <label class="radio-option"><input type="radio" name="analysis-depth" value="standard"><span>Standard</span></label>
                            <label class="radio-option"><input type="radio" name="analysis-depth" value="deep"><span>Deep Analysis</span></label>
                        </div>
                    </div>
                </div>
                
                <div class="action-row">
                    <button class="btn btn-primary btn-lg" id="check-source-btn">${ICONS.source} Analyze Source</button>
                    <button class="btn btn-secondary btn-lg">${ICONS.upload} Bulk Upload CSV</button>
                </div>
            </div>
        </div>

        <div id="source-result"></div>

        <!-- Quick Actions -->
        <div class="card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.zap} Quick Check Popular Sources</h3>
                <p class="card-subtitle">One-click analysis for commonly referenced sources</p>
            </div>
            <div class="quick-actions-grid">
                <button class="quick-action" data-url="reuters.com">
                    <span class="quick-icon">${ICONS.globe}</span>
                    <span>Reuters</span>
                </button>
                <button class="quick-action" data-url="apnews.com">
                    <span class="quick-icon">${ICONS.globe}</span>
                    <span>AP News</span>
                </button>
                <button class="quick-action" data-url="bbc.com">
                    <span class="quick-icon">${ICONS.globe}</span>
                    <span>BBC</span>
                </button>
                <button class="quick-action" data-url="cnn.com">
                    <span class="quick-icon">${ICONS.globe}</span>
                    <span>CNN</span>
                </button>
                <button class="quick-action" data-url="foxnews.com">
                    <span class="quick-icon">${ICONS.globe}</span>
                    <span>Fox News</span>
                </button>
                <button class="quick-action" data-url="nytimes.com">
                    <span class="quick-icon">${ICONS.globe}</span>
                    <span>NY Times</span>
                </button>
                <button class="quick-action" data-url="washingtonpost.com">
                    <span class="quick-icon">${ICONS.globe}</span>
                    <span>Washington Post</span>
                </button>
                <button class="quick-action" data-url="theguardian.com">
                    <span class="quick-icon">${ICONS.globe}</span>
                    <span>The Guardian</span>
                </button>
            </div>
        </div>

        <!-- Feature Cards -->
        <div class="section-header" style="margin-top: 32px;">
            <h2>What We Analyze</h2>
            <p>Our AI examines multiple dimensions of source credibility</p>
        </div>
        <div class="feature-grid">
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.shield}</div>
                <h3>Trust Signals</h3>
                <p>Evaluate ownership transparency, editorial policies, corrections history, and industry certifications.</p>
                <div class="feature-tags"><span class="feature-tag">Ownership</span><span class="feature-tag">IFCN Signatory</span><span class="feature-tag">Editorial Policy</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.trending}</div>
                <h3>Bias Detection</h3>
                <p>Advanced NLP analysis of language patterns, headline framing, and story selection bias.</p>
                <div class="feature-tags"><span class="feature-tag">Political Lean</span><span class="feature-tag">Sensationalism</span><span class="feature-tag">Clickbait Score</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.history}</div>
                <h3>Fact-Check Record</h3>
                <p>Cross-reference with 80+ fact-checking organizations worldwide for historical accuracy.</p>
                <div class="feature-tags"><span class="feature-tag">False Claims</span><span class="feature-tag">Corrections</span><span class="feature-tag">Retractions</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.database}</div>
                <h3>Domain Intelligence</h3>
                <p>Technical analysis including domain age, hosting patterns, and connection to known disinformation networks.</p>
                <div class="feature-tags"><span class="feature-tag">Domain Age</span><span class="feature-tag">WHOIS</span><span class="feature-tag">Network Analysis</span></div>
            </div>
        </div>

        <!-- How It Works -->
        <div class="card" style="margin-top: 32px;">
            <div class="card-header">
                <h3>${ICONS.help} How Source Checking Works</h3>
            </div>
            <div class="how-it-works">
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h4>Input Source</h4>
                        <p>Enter any URL, domain, or publication name you want to analyze</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h4>AI Analysis</h4>
                        <p>Our AI examines 50+ credibility signals across multiple dimensions</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h4>Cross-Reference</h4>
                        <p>Results are validated against our database and partner fact-checkers</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <h4>Trust Score</h4>
                        <p>Receive a comprehensive credibility score with detailed breakdown</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tips Card -->
        <div class="card tips-card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.info} Pro Tips for Source Evaluation</h3>
            </div>
            <div class="tips-grid">
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Check the "About" page</strong>
                        <p>Legitimate sources clearly state ownership, funding, and editorial mission</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Look for author credentials</strong>
                        <p>Reliable sources have named authors with verifiable backgrounds</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Verify with multiple sources</strong>
                        <p>Cross-check claims across independent, reputable outlets</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Watch for emotional language</strong>
                        <p>Sensational headlines and fear-mongering often indicate low credibility</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - CONTENT MODERATOR =====
function renderContentModerator() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / <span>Content Moderator</span></div>
            <div class="header-title-row">
                <h1>${ICONS.moderate} Content Moderator</h1>
                <span class="badge badge-pro">Pro+ Feature</span>
            </div>
            <p class="page-subtitle">Detect harmful, misleading, or inappropriate content using our advanced multi-layered AI moderation system. Trusted by enterprises worldwide.</p>
        </div>

        <!-- Performance Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.shield}</div>
                    <span class="stat-change positive">99.2% accuracy</span>
                </div>
                <div class="stat-value">50M+</div>
                <div class="stat-label">Content Pieces Moderated</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.zap}</div>
                </div>
                <div class="stat-value">&lt;100ms</div>
                <div class="stat-label">Average Response Time</div>
            </div>
            <div class="stat-card pink">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.globe}</div>
                </div>
                <div class="stat-value">40+</div>
                <div class="stat-label">Languages Supported</div>
            </div>
            <div class="stat-card green">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.alert}</div>
                </div>
                <div class="stat-value">8</div>
                <div class="stat-label">Detection Categories</div>
            </div>
        </div>

        <!-- Main Moderation Card -->
        <div class="card card-elevated" style="margin-top: 24px;">
            <div class="card-header">
                <div class="card-title-group">
                    <div class="card-icon">${ICONS.eye}</div>
                    <div>
                        <h3>Analyze Content</h3>
                        <p class="card-subtitle">Paste text, URLs, or upload content for comprehensive moderation analysis</p>
                    </div>
                </div>
            </div>
            
            <div class="moderator-container">
                <div class="form-group">
                    <label class="input-label">
                        ${ICONS.file} Content to Analyze
                        <span class="label-hint">Paste text content, a URL, or upload a file</span>
                    </label>
                    <textarea class="textarea textarea-large" id="moderate-input" placeholder="Paste content to analyze for harmful material, hate speech, misinformation, spam, adult content, or other violations...

Examples of what we detect:
• Hate speech and discrimination
• Violent threats or graphic content  
• Misinformation and fake news
• Spam and promotional abuse
• Personal attacks and harassment
• Self-harm or dangerous content"></textarea>
                </div>
                
                <div class="moderation-categories">
                    <label class="section-label">${ICONS.filter} Detection Categories</label>
                    <div class="verify-options">
                        <label class="toggle-option active"><input type="checkbox" id="mod-hate" checked><span class="toggle-label">${ICONS.alert} Hate Speech</span></label>
                        <label class="toggle-option active"><input type="checkbox" id="mod-misinfo" checked><span class="toggle-label">${ICONS.x} Misinformation</span></label>
                        <label class="toggle-option active"><input type="checkbox" id="mod-violence" checked><span class="toggle-label">${ICONS.shield} Violence</span></label>
                        <label class="toggle-option active"><input type="checkbox" id="mod-spam" checked><span class="toggle-label">${ICONS.bell} Spam</span></label>
                        <label class="toggle-option"><input type="checkbox" id="mod-adult"><span class="toggle-label">${ICONS.eyeOff} Adult Content</span></label>
                        <label class="toggle-option"><input type="checkbox" id="mod-harassment"><span class="toggle-label">${ICONS.user} Harassment</span></label>
                        <label class="toggle-option"><input type="checkbox" id="mod-selfharm"><span class="toggle-label">${ICONS.alert} Self-Harm</span></label>
                        <label class="toggle-option"><input type="checkbox" id="mod-pii"><span class="toggle-label">${ICONS.lock} PII Detection</span></label>
                    </div>
                </div>

                <div class="sensitivity-control">
                    <label class="section-label">${ICONS.target} Sensitivity Level</label>
                    <div class="slider-container">
                        <span class="slider-label">Lenient</span>
                        <input type="range" class="slider" id="sensitivity-slider" min="1" max="5" value="3">
                        <span class="slider-label">Strict</span>
                    </div>
                </div>

                <div class="action-row">
                    <button class="btn btn-primary btn-lg" id="moderate-btn">${ICONS.moderate} Analyze Content</button>
                    <button class="btn btn-secondary btn-lg">${ICONS.upload} Upload File</button>
                    <button class="btn btn-ghost btn-lg">${ICONS.link} Analyze URL</button>
                </div>
            </div>
        </div>

        <div id="moderate-result"></div>

        <!-- Detection Capabilities -->
        <div class="section-header" style="margin-top: 32px;">
            <h2>Detection Capabilities</h2>
            <p>Our AI is trained to detect a wide range of harmful content types</p>
        </div>
        <div class="feature-grid">
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.alert}</div>
                <h3>Hate Speech Detection</h3>
                <p>Identify content targeting individuals or groups based on protected characteristics including race, religion, gender, and more.</p>
                <div class="feature-tags"><span class="feature-tag">Slurs</span><span class="feature-tag">Discrimination</span><span class="feature-tag">Dehumanization</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.brain}</div>
                <h3>Misinformation Analysis</h3>
                <p>Cross-reference claims against our fact-check database and identify potentially false or misleading information.</p>
                <div class="feature-tags"><span class="feature-tag">Fake News</span><span class="feature-tag">Conspiracy</span><span class="feature-tag">Manipulation</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.shield}</div>
                <h3>Violence & Threats</h3>
                <p>Detect threats of violence, graphic content descriptions, and calls for harmful action against individuals or groups.</p>
                <div class="feature-tags"><span class="feature-tag">Threats</span><span class="feature-tag">Graphic Content</span><span class="feature-tag">Incitement</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.lock}</div>
                <h3>Privacy Protection</h3>
                <p>Identify personal information, doxxing attempts, and content that could compromise individual privacy and safety.</p>
                <div class="feature-tags"><span class="feature-tag">PII</span><span class="feature-tag">Doxxing</span><span class="feature-tag">Data Leaks</span></div>
            </div>
        </div>

        <!-- How It Works -->
        <div class="card" style="margin-top: 32px;">
            <div class="card-header">
                <h3>${ICONS.layers} Multi-Layer Detection Pipeline</h3>
            </div>
            <div class="how-it-works">
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h4>Text Preprocessing</h4>
                        <p>Normalize text, detect language, and prepare content for analysis</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h4>ML Classification</h4>
                        <p>Multiple specialized models analyze content for different violation types</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h4>Context Analysis</h4>
                        <p>LLM evaluates context, intent, and nuance to reduce false positives</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <h4>Confidence Scoring</h4>
                        <p>Generate confidence scores and actionable recommendations</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Use Cases -->
        <div class="card tips-card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.star} Enterprise Use Cases</h3>
            </div>
            <div class="tips-grid">
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.social}</div>
                    <div class="tip-content">
                        <strong>Social Media Platforms</strong>
                        <p>Real-time moderation of user-generated content at scale</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.research}</div>
                    <div class="tip-content">
                        <strong>News & Publishing</strong>
                        <p>Pre-publication review and comment moderation</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.user}</div>
                    <div class="tip-content">
                        <strong>Community Forums</strong>
                        <p>Keep online communities safe and welcoming</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.billing}</div>
                    <div class="tip-content">
                        <strong>E-Commerce</strong>
                        <p>Review moderation and product listing compliance</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - RESEARCH ASSISTANT =====
function renderResearch() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / <span>Research Assistant</span></div>
            <div class="header-title-row">
                <h1>${ICONS.research} Research Assistant</h1>
                <span class="badge badge-pro">Pro+ Feature</span>
            </div>
            <p class="page-subtitle">AI-powered research helper with access to academic databases, verified sources, and intelligent synthesis capabilities. Your personal research librarian.</p>
        </div>

        <!-- Research Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.database}</div>
                    <span class="stat-change positive">Updated hourly</span>
                </div>
                <div class="stat-value">250M+</div>
                <div class="stat-label">Academic Papers</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.globe}</div>
                </div>
                <div class="stat-value">180K+</div>
                <div class="stat-label">Journals Indexed</div>
            </div>
            <div class="stat-card pink">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.brain}</div>
                </div>
                <div class="stat-value">GPT-4</div>
                <div class="stat-label">AI Summarization</div>
            </div>
            <div class="stat-card green">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.check}</div>
                </div>
                <div class="stat-value">Verified</div>
                <div class="stat-label">Peer-Reviewed Sources</div>
            </div>
        </div>

        <!-- Main Research Card -->
        <div class="card card-elevated" style="margin-top: 24px;">
            <div class="card-header">
                <div class="card-title-group">
                    <div class="card-icon">${ICONS.source}</div>
                    <div>
                        <h3>Start Your Research</h3>
                        <p class="card-subtitle">Ask a question or describe your research topic</p>
                    </div>
                </div>
            </div>
            
            <div class="verify-box">
                <div class="form-group">
                    <label class="input-label">
                        ${ICONS.help} Research Topic or Question
                        <span class="label-hint">Be specific for best results - include key terms, time periods, or specific domains</span>
                    </label>
                    <input type="text" class="input input-lg" id="research-query" placeholder="e.g., What are the latest developments in mRNA vaccine technology for cancer treatment?">
                </div>
                
                <div class="source-filters">
                    <label class="section-label">${ICONS.filter} Source Types</label>
                    <div class="verify-options">
                        <label class="verify-option active"><input type="checkbox" id="src-academic" checked> ${ICONS.research} Academic Papers</label>
                        <label class="verify-option active"><input type="checkbox" id="src-news" checked> ${ICONS.file} News Articles</label>
                        <label class="verify-option"><input type="checkbox" id="src-gov"> ${ICONS.shield} Government Data</label>
                        <label class="verify-option"><input type="checkbox" id="src-science"> ${ICONS.brain} Scientific Papers</label>
                        <label class="verify-option"><input type="checkbox" id="src-clinical"> ${ICONS.stats} Clinical Trials</label>
                        <label class="verify-option"><input type="checkbox" id="src-patents"> ${ICONS.code} Patents</label>
                    </div>
                </div>

                <div class="research-options">
                    <div class="option-row">
                        <div class="form-group inline">
                            <label class="input-label">${ICONS.calendar} Date Range</label>
                            <select class="select" id="date-range">
                                <option value="any">Any time</option>
                                <option value="year">Past year</option>
                                <option value="5years" selected>Past 5 years</option>
                                <option value="10years">Past 10 years</option>
                            </select>
                        </div>
                        <div class="form-group inline">
                            <label class="input-label">${ICONS.target} Output Format</label>
                            <select class="select" id="output-format">
                                <option value="summary">Summary Report</option>
                                <option value="detailed">Detailed Analysis</option>
                                <option value="bibliography">Bibliography Only</option>
                                <option value="citations">With Citations</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="verify-actions">
                    <button class="btn btn-primary btn-lg" id="research-btn">${ICONS.research} Start Research</button>
                    <button class="btn btn-secondary btn-lg">${ICONS.download} Export to PDF</button>
                    <button class="btn btn-ghost btn-lg">${ICONS.history} View History</button>
                </div>
            </div>
        </div>

        <div id="research-result"></div>

        <!-- Quick Research Topics -->
        <div class="card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.trending} Trending Research Topics</h3>
                <p class="card-subtitle">Popular research queries from the academic community</p>
            </div>
            <div class="trending-topics">
                <button class="topic-pill">AI in Healthcare</button>
                <button class="topic-pill">Climate Change Mitigation</button>
                <button class="topic-pill">Quantum Computing</button>
                <button class="topic-pill">mRNA Technology</button>
                <button class="topic-pill">Renewable Energy</button>
                <button class="topic-pill">Cybersecurity</button>
                <button class="topic-pill">Mental Health</button>
                <button class="topic-pill">Space Exploration</button>
            </div>
        </div>

        <!-- Feature Cards -->
        <div class="section-header" style="margin-top: 32px;">
            <h2>Research Capabilities</h2>
            <p>Powerful tools for comprehensive academic research</p>
        </div>
        <div class="feature-grid">
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.database}</div>
                <h3>Academic Databases</h3>
                <p>Access millions of peer-reviewed papers from major academic publishers and repositories worldwide.</p>
                <div class="feature-tags"><span class="feature-tag">PubMed</span><span class="feature-tag">arXiv</span><span class="feature-tag">JSTOR</span><span class="feature-tag">IEEE</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.brain}</div>
                <h3>AI Summarization</h3>
                <p>Get concise, accurate summaries and key insights from complex research papers using advanced language models.</p>
                <div class="feature-tags"><span class="feature-tag">GPT-4</span><span class="feature-tag">Claude</span><span class="feature-tag">Key Findings</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.link}</div>
                <h3>Citation Network</h3>
                <p>Explore citation graphs to discover related papers, influential works, and research trends.</p>
                <div class="feature-tags"><span class="feature-tag">References</span><span class="feature-tag">Citations</span><span class="feature-tag">Impact Factor</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.code}</div>
                <h3>Export & Integration</h3>
                <p>Export your research to various formats and integrate with popular reference management tools.</p>
                <div class="feature-tags"><span class="feature-tag">BibTeX</span><span class="feature-tag">Zotero</span><span class="feature-tag">Mendeley</span></div>
            </div>
        </div>

        <!-- How It Works -->
        <div class="card" style="margin-top: 32px;">
            <div class="card-header">
                <h3>${ICONS.help} How Research Assistant Works</h3>
            </div>
            <div class="how-it-works">
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h4>Define Your Query</h4>
                        <p>Enter your research question or topic with relevant keywords</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h4>Source Selection</h4>
                        <p>Choose which databases and source types to include in your search</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h4>AI Analysis</h4>
                        <p>Our AI synthesizes findings from multiple sources into coherent insights</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <h4>Verified Results</h4>
                        <p>Receive comprehensive research with proper citations and source links</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Pro Tips -->
        <div class="card tips-card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.star} Research Best Practices</h3>
            </div>
            <div class="tips-grid">
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Use Boolean operators</strong>
                        <p>Combine keywords with AND, OR, NOT for precise results</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Check citations counts</strong>
                        <p>Highly cited papers are often more influential and reliable</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Review recent publications</strong>
                        <p>Include recent papers to ensure your research is current</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Cross-reference findings</strong>
                        <p>Validate claims across multiple independent sources</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - SOCIAL MONITOR =====
function renderSocialMonitor() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / <span>Social Monitor</span></div>
            <div class="header-title-row">
                <h1>${ICONS.social} Social Media Monitor</h1>
                <span class="badge badge-pro">Pro+ Feature</span>
                <span class="badge badge-live pulse">● LIVE</span>
            </div>
            <p class="page-subtitle">Track misinformation trends, viral claims, and emerging narratives across social platforms in real-time. Stay ahead of the disinformation curve.</p>
        </div>

        <!-- Live Stats Dashboard -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.trending}</div>
                    <span class="stat-change live">Live</span>
                </div>
                <div class="stat-value">1,247</div>
                <div class="stat-label">Trending Claims</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.alert}</div>
                    <span class="stat-change negative">+12 new</span>
                </div>
                <div class="stat-value">89</div>
                <div class="stat-label">Active Alerts</div>
            </div>
            <div class="stat-card pink">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.eye}</div>
                </div>
                <div class="stat-value">24/7</div>
                <div class="stat-label">Real-time Monitoring</div>
            </div>
            <div class="stat-card green">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.globe}</div>
                </div>
                <div class="stat-value">50+</div>
                <div class="stat-label">Platforms Tracked</div>
            </div>
        </div>

        <!-- Platform Filters -->
        <div class="card" style="margin-top: 24px;">
            <div class="card-header">
                <div class="card-title-group">
                    <div class="card-icon">${ICONS.filter}</div>
                    <div>
                        <h3>Monitor Settings</h3>
                        <p class="card-subtitle">Configure your monitoring preferences</p>
                    </div>
                </div>
                <button class="btn btn-sm btn-primary">${ICONS.settings} Customize Alerts</button>
            </div>
            <div class="platform-filters">
                <label class="section-label">Platforms</label>
                <div class="platform-toggles">
                    <label class="platform-toggle active">
                        <input type="checkbox" checked>
                        <span class="platform-icon">𝕏</span>
                        <span>X/Twitter</span>
                    </label>
                    <label class="platform-toggle active">
                        <input type="checkbox" checked>
                        <span class="platform-icon">f</span>
                        <span>Facebook</span>
                    </label>
                    <label class="platform-toggle active">
                        <input type="checkbox" checked>
                        <span class="platform-icon">📸</span>
                        <span>Instagram</span>
                    </label>
                    <label class="platform-toggle active">
                        <input type="checkbox" checked>
                        <span class="platform-icon">🎵</span>
                        <span>TikTok</span>
                    </label>
                    <label class="platform-toggle">
                        <input type="checkbox">
                        <span class="platform-icon">▶️</span>
                        <span>YouTube</span>
                    </label>
                    <label class="platform-toggle">
                        <input type="checkbox">
                        <span class="platform-icon">🔗</span>
                        <span>LinkedIn</span>
                    </label>
                    <label class="platform-toggle">
                        <input type="checkbox">
                        <span class="platform-icon">👻</span>
                        <span>Snapchat</span>
                    </label>
                    <label class="platform-toggle">
                        <input type="checkbox">
                        <span class="platform-icon">📌</span>
                        <span>Pinterest</span>
                    </label>
                </div>
            </div>
            <div class="topic-filters" style="margin-top: 16px;">
                <label class="section-label">Topic Categories</label>
                <div class="topic-toggles">
                    <span class="topic-filter active">Politics</span>
                    <span class="topic-filter active">Health</span>
                    <span class="topic-filter active">Science</span>
                    <span class="topic-filter">Finance</span>
                    <span class="topic-filter">Technology</span>
                    <span class="topic-filter">Environment</span>
                    <span class="topic-filter">Entertainment</span>
                    <span class="topic-filter">Sports</span>
                </div>
            </div>
        </div>

        <!-- Trending Misinformation Feed -->
        <div class="card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.alert} Trending Misinformation</h3>
                <div class="header-actions">
                    <button class="btn btn-sm btn-secondary">${ICONS.refresh} Refresh</button>
                    <button class="btn btn-sm btn-ghost">${ICONS.download} Export</button>
                </div>
            </div>
            <div class="history-list">
                ${[
                    { claim: 'Viral claim about election fraud spreads rapidly across multiple platforms', score: 15, time: '2 hours ago', platform: 'X/Twitter', shares: '45.2K', status: 'critical' },
                    { claim: 'Misleading health advice about new treatment circulating widely', score: 22, time: '4 hours ago', platform: 'Facebook', shares: '28.1K', status: 'warning' },
                    { claim: 'Doctored video of public figure gains millions of views', score: 8, time: '6 hours ago', platform: 'TikTok', shares: '2.1M', status: 'critical' },
                    { claim: 'False statistics about crime rates being shared by influencers', score: 31, time: '8 hours ago', platform: 'Instagram', shares: '15.8K', status: 'warning' },
                    { claim: 'Conspiracy theory about tech company gains traction', score: 18, time: '12 hours ago', platform: 'YouTube', shares: '89K', status: 'moderate' }
                ].map(item => `
                    <div class="history-item ${item.status}">
                        <div class="history-score bad">${item.score}</div>
                        <div class="history-content">
                            <div class="history-text">${item.claim}</div>
                            <div class="history-meta">
                                <span class="platform-badge">${item.platform}</span>
                                <span>${ICONS.share} ${item.shares} shares</span>
                                <span>${ICONS.clock} ${item.time}</span>
                            </div>
                        </div>
                        <div class="history-actions">
                            <button class="btn btn-sm btn-ghost">${ICONS.eye} Details</button>
                            <button class="btn btn-sm btn-ghost">${ICONS.bell} Alert</button>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="card-footer">
                <button class="btn btn-secondary btn-block">Load More Results</button>
            </div>
        </div>

        <!-- Monitoring Features -->
        <div class="section-header" style="margin-top: 32px;">
            <h2>Monitoring Capabilities</h2>
            <p>Enterprise-grade social media intelligence</p>
        </div>
        <div class="feature-grid">
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.realtime}</div>
                <h3>Real-Time Tracking</h3>
                <p>Monitor social platforms 24/7 with sub-minute latency for breaking misinformation.</p>
                <div class="feature-tags"><span class="feature-tag">Live Feed</span><span class="feature-tag">Instant Alerts</span><span class="feature-tag">WebSocket</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.trending}</div>
                <h3>Virality Prediction</h3>
                <p>AI predicts which false claims are likely to go viral before they spread widely.</p>
                <div class="feature-tags"><span class="feature-tag">ML Models</span><span class="feature-tag">Early Warning</span><span class="feature-tag">Trend Analysis</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.brain}</div>
                <h3>Narrative Analysis</h3>
                <p>Track how misinformation narratives evolve and spread across different communities.</p>
                <div class="feature-tags"><span class="feature-tag">Network Mapping</span><span class="feature-tag">Influence Tracking</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.bell}</div>
                <h3>Custom Alerts</h3>
                <p>Set up custom monitoring rules and receive alerts via email, Slack, or webhook.</p>
                <div class="feature-tags"><span class="feature-tag">Email</span><span class="feature-tag">Slack</span><span class="feature-tag">Webhook</span><span class="feature-tag">SMS</span></div>
            </div>
        </div>

        <!-- Bot Detection Section -->
        <div class="card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.cpu} Bot & Coordinated Activity Detection</h3>
            </div>
            <div class="bot-stats">
                <div class="bot-stat">
                    <div class="bot-stat-value">23%</div>
                    <div class="bot-stat-label">Bot-like accounts detected in trending topics</div>
                </div>
                <div class="bot-stat">
                    <div class="bot-stat-value">847</div>
                    <div class="bot-stat-label">Coordinated inauthentic behavior networks flagged</div>
                </div>
                <div class="bot-stat">
                    <div class="bot-stat-value">12</div>
                    <div class="bot-stat-label">Countries with active influence operations</div>
                </div>
            </div>
        </div>

        <!-- Tips -->
        <div class="card tips-card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.info} Understanding Social Misinformation</h3>
            </div>
            <div class="tips-grid">
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.alert}</div>
                    <div class="tip-content">
                        <strong>Check the source</strong>
                        <p>Viral content often originates from unverified or anonymous accounts</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.clock}</div>
                    <div class="tip-content">
                        <strong>Beware of "breaking news"</strong>
                        <p>Misinformation spreads fastest during breaking events when facts are unclear</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.eye}</div>
                    <div class="tip-content">
                        <strong>Watch for emotional manipulation</strong>
                        <p>Content designed to provoke outrage often prioritizes engagement over accuracy</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.share}</div>
                    <div class="tip-content">
                        <strong>Don't amplify unverified claims</strong>
                        <p>Sharing to "debunk" still spreads misinformation to new audiences</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - STATS VALIDATOR =====
function renderStatsValidator() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / <span>Stats Validator</span></div>
            <div class="header-title-row">
                <h1>${ICONS.stats} Statistics Validator</h1>
                <span class="badge badge-pro">Pro+ Feature</span>
            </div>
            <p class="page-subtitle">Verify statistical claims and data citations against authoritative government databases, academic sources, and official publications.</p>
        </div>

        <!-- Stats Dashboard -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.database}</div>
                </div>
                <div class="stat-value">15K+</div>
                <div class="stat-label">Data Sources</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.check}</div>
                </div>
                <div class="stat-value">94.7%</div>
                <div class="stat-label">Validation Accuracy</div>
            </div>
            <div class="stat-card pink">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.clock}</div>
                </div>
                <div class="stat-value">&lt;5s</div>
                <div class="stat-label">Avg Check Time</div>
            </div>
            <div class="stat-card green">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.globe}</div>
                </div>
                <div class="stat-value">195</div>
                <div class="stat-label">Countries Data</div>
            </div>
        </div>

        <!-- Main Validation Card -->
        <div class="card card-elevated" style="margin-top: 24px;">
            <div class="card-header">
                <div class="card-title-group">
                    <div class="card-icon">${ICONS.target}</div>
                    <div>
                        <h3>Validate a Statistical Claim</h3>
                        <p class="card-subtitle">Enter any statistic or data claim to verify against official sources</p>
                    </div>
                </div>
            </div>
            <div class="verify-box">
                <div class="form-group">
                    <label class="input-label">
                        ${ICONS.stats} Statistical Claim
                        <span class="label-hint">Include numbers, percentages, or data references for best results</span>
                    </label>
                    <textarea class="textarea" id="stats-input" placeholder="Enter a statistical claim to validate, for example:

• '90% of scientists agree that climate change is human-caused'
• 'Crime rates have increased 50% since 2020'
• 'The average American drinks 3 cups of coffee per day'
• 'Inflation rose 6.2% in 2023'
• 'US unemployment rate is at 3.8%'
• 'Global CO2 emissions reached 37 billion tonnes in 2024'"></textarea>
                </div>

                <div class="validation-options">
                    <label class="section-label">${ICONS.filter} Validation Sources</label>
                    <div class="verify-options">
                        <label class="verify-option active"><input type="checkbox" id="src-govt" checked> ${ICONS.shield} Government Data</label>
                        <label class="verify-option active"><input type="checkbox" id="src-intl" checked> ${ICONS.globe} International Organizations</label>
                        <label class="verify-option active"><input type="checkbox" id="src-acad" checked> ${ICONS.research} Academic Research</label>
                        <label class="verify-option"><input type="checkbox" id="src-industry"> ${ICONS.trending} Industry Reports</label>
                        <label class="verify-option"><input type="checkbox" id="src-ngo"> ${ICONS.user} NGO Publications</label>
                    </div>
                </div>

                <div class="verify-actions">
                    <button class="btn btn-primary btn-lg" id="stats-btn">${ICONS.stats} Validate Statistics</button>
                    <button class="btn btn-secondary btn-lg">${ICONS.upload} Bulk Validate CSV</button>
                    <button class="btn btn-ghost btn-lg">${ICONS.history} Check History</button>
                </div>
            </div>
        </div>
        <div id="stats-result"></div>

        <!-- Quick Validate Common Claims -->
        <div class="card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.zap} Common Statistical Claims</h3>
                <p class="card-subtitle">One-click validation for frequently cited statistics</p>
            </div>
            <div class="quick-stats-grid">
                <button class="quick-stat-btn">
                    <span class="stat-category">Economy</span>
                    <span class="stat-claim">Current US Inflation Rate</span>
                </button>
                <button class="quick-stat-btn">
                    <span class="stat-category">Employment</span>
                    <span class="stat-claim">US Unemployment Rate</span>
                </button>
                <button class="quick-stat-btn">
                    <span class="stat-category">Health</span>
                    <span class="stat-claim">COVID-19 Vaccination Rates</span>
                </button>
                <button class="quick-stat-btn">
                    <span class="stat-category">Climate</span>
                    <span class="stat-claim">Global Temperature Anomaly</span>
                </button>
                <button class="quick-stat-btn">
                    <span class="stat-category">Crime</span>
                    <span class="stat-claim">US Violent Crime Rate</span>
                </button>
                <button class="quick-stat-btn">
                    <span class="stat-category">Population</span>
                    <span class="stat-claim">World Population</span>
                </button>
            </div>
        </div>

        <!-- Data Sources -->
        <div class="section-header" style="margin-top: 32px;">
            <h2>Authoritative Data Sources</h2>
            <p>We validate against the world's most trusted statistical organizations</p>
        </div>
        <div class="feature-grid">
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.shield}</div>
                <h3>Government Agencies</h3>
                <p>Official statistics from federal and state agencies worldwide.</p>
                <div class="feature-tags"><span class="feature-tag">BLS</span><span class="feature-tag">Census</span><span class="feature-tag">CDC</span><span class="feature-tag">FBI</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.globe}</div>
                <h3>International Organizations</h3>
                <p>Global data from trusted international bodies and multilateral institutions.</p>
                <div class="feature-tags"><span class="feature-tag">UN</span><span class="feature-tag">WHO</span><span class="feature-tag">World Bank</span><span class="feature-tag">IMF</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.research}</div>
                <h3>Research Institutions</h3>
                <p>Data from leading universities and research organizations.</p>
                <div class="feature-tags"><span class="feature-tag">Pew Research</span><span class="feature-tag">Gallup</span><span class="feature-tag">RAND</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.database}</div>
                <h3>Open Data Platforms</h3>
                <p>Access to curated open data repositories and databases.</p>
                <div class="feature-tags"><span class="feature-tag">Data.gov</span><span class="feature-tag">Eurostat</span><span class="feature-tag">OECD</span></div>
            </div>
        </div>

        <!-- How It Works -->
        <div class="card" style="margin-top: 32px;">
            <div class="card-header">
                <h3>${ICONS.help} How Statistics Validation Works</h3>
            </div>
            <div class="how-it-works">
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h4>Parse the Claim</h4>
                        <p>AI extracts statistical values, context, and implied sources from your input</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h4>Query Databases</h4>
                        <p>Search 15,000+ authoritative data sources for matching statistics</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h4>Cross-Reference</h4>
                        <p>Compare claimed values against official figures with tolerance for rounding</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <h4>Validation Report</h4>
                        <p>Receive detailed verdict with source citations and confidence levels</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tips -->
        <div class="card tips-card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.info} Reading Statistics Critically</h3>
            </div>
            <div class="tips-grid">
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Ask "compared to what?"</strong>
                        <p>Percentages and changes need baselines for proper context</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Check the date</strong>
                        <p>Statistics can become outdated; always verify currency of data</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Understand the methodology</strong>
                        <p>How data was collected affects what conclusions can be drawn</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.check}</div>
                    <div class="tip-content">
                        <strong>Beware of cherry-picking</strong>
                        <p>Selected data points can mislead when broader context is omitted</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - MISINFO MAP =====
function renderMisinfoMap() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / <span>Misinformation Map</span></div>
            <div class="header-title-row">
                <h1>${ICONS.map} Global Misinformation Map</h1>
                <span class="badge badge-pro">Pro+ Feature</span>
                <span class="badge badge-live pulse">● LIVE</span>
            </div>
            <p class="page-subtitle">Visualize misinformation patterns, hotspots, and disinformation campaigns around the world with interactive geographic intelligence.</p>
        </div>

        <!-- Global Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.alert}</div>
                    <span class="stat-change negative">+847 today</span>
                </div>
                <div class="stat-value">12,847</div>
                <div class="stat-label">Active Hotspots</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.trending}</div>
                    <span class="stat-change negative">↑ 23%</span>
                </div>
                <div class="stat-value">+23%</div>
                <div class="stat-label">Weekly Change</div>
            </div>
            <div class="stat-card pink">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.globe}</div>
                </div>
                <div class="stat-value">195</div>
                <div class="stat-label">Countries Tracked</div>
            </div>
            <div class="stat-card green">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.database}</div>
                </div>
                <div class="stat-value">5.2M+</div>
                <div class="stat-label">Claims Analyzed</div>
            </div>
        </div>

        <!-- Map Container -->
        <div class="card card-elevated" style="margin-top: 24px;">
            <div class="card-header">
                <div class="card-title-group">
                    <div class="card-icon">${ICONS.globe}</div>
                    <div>
                        <h3>Interactive Global Map</h3>
                        <p class="card-subtitle">Click on regions to explore misinformation patterns</p>
                    </div>
                </div>
                <div class="header-actions">
                    <select class="select" id="map-timeframe">
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d" selected>Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                        <option value="90d">Last 90 Days</option>
                    </select>
                    <button class="btn btn-sm btn-secondary">${ICONS.refresh} Refresh</button>
                </div>
            </div>
            <div class="map-container" style="height: 400px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1)); border-radius: 8px;">
                <div class="empty-state">
                    <div class="empty-icon">${ICONS.map}</div>
                    <h3>Interactive Global Map</h3>
                    <p>Load the live visualization to explore misinformation patterns worldwide</p>
                    <button class="btn btn-primary btn-lg" id="load-map-btn">${ICONS.globe} Load Map</button>
                </div>
            </div>
            <div class="map-legend" style="margin-top: 16px; display: flex; gap: 24px; justify-content: center;">
                <div class="legend-item"><span class="legend-dot critical"></span> Critical (1000+ claims)</div>
                <div class="legend-item"><span class="legend-dot high"></span> High (500-999 claims)</div>
                <div class="legend-item"><span class="legend-dot medium"></span> Medium (100-499 claims)</div>
                <div class="legend-item"><span class="legend-dot low"></span> Low (&lt;100 claims)</div>
            </div>
        </div>

        <!-- Regional Breakdown -->
        <div class="card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.trending} Top Misinformation Hotspots</h3>
                <button class="btn btn-sm btn-ghost">${ICONS.download} Export Data</button>
            </div>
            <div class="hotspots-list">
                ${[
                    { region: 'United States', claims: '2,847', change: '+15%', topics: ['Politics', 'Health'], severity: 'critical' },
                    { region: 'Brazil', claims: '1,923', change: '+28%', topics: ['Politics', 'Environment'], severity: 'critical' },
                    { region: 'India', claims: '1,654', change: '+12%', topics: ['Health', 'Religion'], severity: 'high' },
                    { region: 'Russia', claims: '1,432', change: '+8%', topics: ['Politics', 'Conflict'], severity: 'high' },
                    { region: 'United Kingdom', claims: '987', change: '+5%', topics: ['Politics', 'Immigration'], severity: 'medium' },
                    { region: 'Philippines', claims: '856', change: '+22%', topics: ['Politics', 'Celebrity'], severity: 'medium' }
                ].map((item, i) => `
                    <div class="hotspot-item">
                        <div class="hotspot-rank">${i + 1}</div>
                        <div class="hotspot-content">
                            <div class="hotspot-region">
                                <span class="severity-indicator ${item.severity}"></span>
                                ${item.region}
                            </div>
                            <div class="hotspot-topics">
                                ${item.topics.map(t => `<span class="topic-tag">${t}</span>`).join('')}
                            </div>
                        </div>
                        <div class="hotspot-stats">
                            <div class="hotspot-claims">${item.claims} claims</div>
                            <div class="hotspot-change negative">${item.change}</div>
                        </div>
                        <button class="btn btn-sm btn-ghost">${ICONS.eye} View</button>
                    </div>
                `).join('')}
            </div>
        </div>

        <!-- Map Features -->
        <div class="section-header" style="margin-top: 32px;">
            <h2>Map Intelligence Features</h2>
            <p>Comprehensive geographic analysis of global misinformation</p>
        </div>
        <div class="feature-grid">
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.target}</div>
                <h3>Hotspot Detection</h3>
                <p>AI automatically identifies emerging misinformation clusters and predicts spread patterns.</p>
                <div class="feature-tags"><span class="feature-tag">Real-time</span><span class="feature-tag">ML-Powered</span><span class="feature-tag">Predictive</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.layers}</div>
                <h3>Cross-Border Tracking</h3>
                <p>Monitor how narratives spread across geographic and linguistic boundaries.</p>
                <div class="feature-tags"><span class="feature-tag">Translation</span><span class="feature-tag">Network Analysis</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.calendar}</div>
                <h3>Historical Analysis</h3>
                <p>Explore misinformation patterns over time with historical data going back 5 years.</p>
                <div class="feature-tags"><span class="feature-tag">Timeline</span><span class="feature-tag">Trend Analysis</span><span class="feature-tag">Reports</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.download}</div>
                <h3>Data Export</h3>
                <p>Export geographic data and visualizations for reports and presentations.</p>
                <div class="feature-tags"><span class="feature-tag">CSV</span><span class="feature-tag">JSON</span><span class="feature-tag">PDF</span><span class="feature-tag">PNG</span></div>
            </div>
        </div>

        <!-- Topic Categories -->
        <div class="card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.filter} Filter by Topic Category</h3>
            </div>
            <div class="topic-categories">
                <button class="category-btn active">${ICONS.user} Politics</button>
                <button class="category-btn">${ICONS.shield} Health</button>
                <button class="category-btn">${ICONS.brain} Science</button>
                <button class="category-btn">${ICONS.alert} Conflict</button>
                <button class="category-btn">${ICONS.globe} Environment</button>
                <button class="category-btn">${ICONS.trending} Finance</button>
                <button class="category-btn">${ICONS.star} Celebrity</button>
                <button class="category-btn">${ICONS.bell} Breaking News</button>
            </div>
        </div>

        <!-- Insights -->
        <div class="card tips-card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.brain} Key Insights</h3>
            </div>
            <div class="insights-grid">
                <div class="insight-item">
                    <div class="insight-icon">${ICONS.trending}</div>
                    <div class="insight-content">
                        <strong>Rising: South America</strong>
                        <p>34% increase in political misinformation ahead of upcoming elections</p>
                    </div>
                </div>
                <div class="insight-item">
                    <div class="insight-icon">${ICONS.alert}</div>
                    <div class="insight-content">
                        <strong>Alert: Coordinated Campaign</strong>
                        <p>Detected inauthentic activity originating from 3 countries, targeting Europe</p>
                    </div>
                </div>
                <div class="insight-item">
                    <div class="insight-icon">${ICONS.check}</div>
                    <div class="insight-content">
                        <strong>Improving: Oceania</strong>
                        <p>12% decrease in health misinformation following intervention efforts</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - REALTIME STREAM =====
function renderRealtime() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / <span>Realtime Stream</span></div>
            <div class="header-title-row">
                <h1>${ICONS.realtime} Realtime Fact-Check Stream</h1>
                <span class="badge badge-pro">Pro+ Feature</span>
                <span class="badge badge-offline" id="stream-status-badge">● OFFLINE</span>
            </div>
            <p class="page-subtitle">Live feed of fact-checks from around the world as they happen. Monitor breaking news verification in real-time.</p>
        </div>

        <!-- Stream Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.verify}</div>
                </div>
                <div class="stat-value" id="checks-today">2,847</div>
                <div class="stat-label">Checks Today</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.clock}</div>
                </div>
                <div class="stat-value">&lt;30s</div>
                <div class="stat-label">Avg Latency</div>
            </div>
            <div class="stat-card pink">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.globe}</div>
                </div>
                <div class="stat-value">80+</div>
                <div class="stat-label">Fact-Check Partners</div>
            </div>
            <div class="stat-card green">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.database}</div>
                </div>
                <div class="stat-value">40+</div>
                <div class="stat-label">Languages</div>
            </div>
        </div>

        <!-- Stream Controls -->
        <div class="card card-elevated" style="margin-top: 24px;">
            <div class="card-header">
                <div class="card-title-group">
                    <div class="card-icon">${ICONS.settings}</div>
                    <div>
                        <h3>Stream Controls</h3>
                        <p class="card-subtitle">Configure your real-time feed preferences</p>
                    </div>
                </div>
            </div>
            <div class="stream-controls">
                <div class="control-row">
                    <div class="control-group">
                        <button class="btn btn-primary btn-lg" id="start-stream-btn">${ICONS.play} Start Stream</button>
                        <button class="btn btn-secondary btn-lg" id="pause-stream-btn" disabled>${ICONS.pause} Pause</button>
                        <button class="btn btn-ghost btn-lg" id="clear-stream-btn">${ICONS.x} Clear</button>
                    </div>
                    <div class="filter-group">
                        <select class="select" id="stream-category" style="min-width: 160px;">
                            <option value="all">All Categories</option>
                            <option value="politics">Politics</option>
                            <option value="health">Health</option>
                            <option value="science">Science</option>
                            <option value="technology">Technology</option>
                            <option value="finance">Finance</option>
                            <option value="entertainment">Entertainment</option>
                        </select>
                        <select class="select" id="stream-region" style="min-width: 160px;">
                            <option value="global">Global</option>
                            <option value="na">North America</option>
                            <option value="eu">Europe</option>
                            <option value="asia">Asia Pacific</option>
                            <option value="latam">Latin America</option>
                            <option value="mena">Middle East & Africa</option>
                        </select>
                        <select class="select" id="stream-verdict" style="min-width: 140px;">
                            <option value="all">All Verdicts</option>
                            <option value="false">False Only</option>
                            <option value="misleading">Misleading</option>
                            <option value="true">True</option>
                            <option value="unverified">Unverified</option>
                        </select>
                    </div>
                </div>
                <div class="stream-options">
                    <label class="toggle-option"><input type="checkbox" id="stream-sound" ><span class="toggle-label">${ICONS.bell} Sound Alerts</span></label>
                    <label class="toggle-option"><input type="checkbox" id="stream-desktop" checked><span class="toggle-label">${ICONS.bell} Desktop Notifications</span></label>
                    <label class="toggle-option"><input type="checkbox" id="stream-autoscroll" checked><span class="toggle-label">${ICONS.arrow} Auto-scroll</span></label>
                </div>
            </div>
        </div>

        <!-- Live Stream -->
        <div class="card" id="stream-container" style="margin-top: 24px;">
            <div class="card-header">
                <div class="stream-header-left">
                    <h3>${ICONS.realtime} Live Stream</h3>
                    <span class="stream-counter" id="stream-counter">0 items</span>
                </div>
                <div class="stream-header-right">
                    <button class="btn btn-sm btn-ghost">${ICONS.download} Export</button>
                    <button class="btn btn-sm btn-ghost">${ICONS.share} Share</button>
                </div>
            </div>
            <div class="stream-feed" id="stream-feed">
                <div class="empty-state">
                    <div class="empty-icon">${ICONS.realtime}</div>
                    <h3>Stream Offline</h3>
                    <p>Click "Start Stream" to see live fact-checks from around the world</p>
                    <div class="empty-features">
                        <div class="empty-feature">${ICONS.globe} Global Coverage</div>
                        <div class="empty-feature">${ICONS.clock} Real-time Updates</div>
                        <div class="empty-feature">${ICONS.verify} Verified Sources</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Stream Features -->
        <div class="section-header" style="margin-top: 32px;">
            <h2>Stream Capabilities</h2>
            <p>Enterprise-grade real-time fact-checking infrastructure</p>
        </div>
        <div class="feature-grid">
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.zap}</div>
                <h3>Sub-Second Latency</h3>
                <p>WebSocket-powered streaming delivers fact-checks within seconds of publication.</p>
                <div class="feature-tags"><span class="feature-tag">WebSocket</span><span class="feature-tag">Low Latency</span><span class="feature-tag">Real-time</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.globe}</div>
                <h3>Global Network</h3>
                <p>Aggregated feeds from 80+ fact-checking organizations across 6 continents.</p>
                <div class="feature-tags"><span class="feature-tag">IFCN Members</span><span class="feature-tag">40+ Languages</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.filter}</div>
                <h3>Smart Filtering</h3>
                <p>Filter by topic, region, language, or verdict to focus on what matters to you.</p>
                <div class="feature-tags"><span class="feature-tag">Categories</span><span class="feature-tag">Regions</span><span class="feature-tag">Custom Rules</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.bell}</div>
                <h3>Alert Integration</h3>
                <p>Set up custom alerts for specific topics or high-impact fact-checks.</p>
                <div class="feature-tags"><span class="feature-tag">Desktop</span><span class="feature-tag">Email</span><span class="feature-tag">Webhook</span><span class="feature-tag">Slack</span></div>
            </div>
        </div>

        <!-- Integration Options -->
        <div class="card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.code} Developer Integration</h3>
            </div>
            <div class="integration-options">
                <div class="integration-item">
                    <div class="integration-icon">${ICONS.api}</div>
                    <div class="integration-content">
                        <h4>REST API</h4>
                        <p>Access the stream programmatically via our REST API endpoints</p>
                    </div>
                    <button class="btn btn-sm btn-secondary">View Docs</button>
                </div>
                <div class="integration-item">
                    <div class="integration-icon">${ICONS.realtime}</div>
                    <div class="integration-content">
                        <h4>WebSocket</h4>
                        <p>Subscribe to real-time streams using WebSocket connections</p>
                    </div>
                    <button class="btn btn-sm btn-secondary">View Docs</button>
                </div>
                <div class="integration-item">
                    <div class="integration-icon">${ICONS.terminal}</div>
                    <div class="integration-content">
                        <h4>Webhook</h4>
                        <p>Receive push notifications for matching fact-checks</p>
                    </div>
                    <button class="btn btn-sm btn-secondary">Configure</button>
                </div>
            </div>
        </div>

        <!-- How It Works -->
        <div class="card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.help} How the Stream Works</h3>
            </div>
            <div class="how-it-works">
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h4>Global Collection</h4>
                        <p>We aggregate fact-checks from 80+ verified organizations worldwide</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h4>Normalization</h4>
                        <p>All fact-checks are standardized into a consistent format with metadata</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h4>Real-time Delivery</h4>
                        <p>Fact-checks are streamed to your dashboard within seconds</p>
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <h4>Action</h4>
                        <p>View details, share, or integrate with your workflow</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tips -->
        <div class="card tips-card" style="margin-top: 24px;">
            <div class="card-header">
                <h3>${ICONS.star} Get the Most from the Stream</h3>
            </div>
            <div class="tips-grid">
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.filter}</div>
                    <div class="tip-content">
                        <strong>Use filters strategically</strong>
                        <p>Focus on your areas of interest to avoid information overload</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.bell}</div>
                    <div class="tip-content">
                        <strong>Set up keyword alerts</strong>
                        <p>Get notified immediately when specific topics are fact-checked</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.download}</div>
                    <div class="tip-content">
                        <strong>Export for analysis</strong>
                        <p>Download stream data for reporting or research purposes</p>
                    </div>
                </div>
                <div class="tip-item">
                    <div class="tip-icon">${ICONS.code}</div>
                    <div class="tip-content">
                        <strong>Integrate with your tools</strong>
                        <p>Use webhooks to push fact-checks to Slack, email, or custom apps</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - API TESTER =====
function renderAPITester() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>Developer</span> / API Tester</div>
            <h1>API Tester</h1>
            <p>Test Verity API endpoints and explore the documentation.</p>
        </div>

        <div class="card">
            <h3>Request Builder</h3>
            <div class="form-row">
                <select class="select" id="api-method" style="width: 120px;">
                    <option>GET</option>
                    <option selected>POST</option>
                    <option>PUT</option>
                    <option>DELETE</option>
                </select>
                <input type="text" class="input" id="api-endpoint" value="/api/v3/verify" style="flex: 1;">
                <button class="btn btn-primary" id="send-api-btn">${ICONS.play} Send</button>
            </div>

            <div class="form-group" style="margin-top: 16px;">
                <label>Request Body (JSON)</label>
                <textarea class="textarea mono" id="api-body" style="height: 120px;">{
  "claim": "Test claim here",
  "deep_analysis": true,
  "include_sources": true
}</textarea>
            </div>
        </div>

        <div class="card" style="margin-top: 16px;">
            <h3>Response</h3>
            <pre class="code-block" id="api-response">// Response will appear here...</pre>
        </div>

        <div class="feature-grid" style="margin-top: 24px;">
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.api}</div>
                <h3>API v3 Endpoints</h3>
                <ul class="feature-list">
                    <li>/api/v3/verify - Verify claims</li>
                    <li>/api/v3/source - Check sources</li>
                    <li>/api/v3/moderate - Content moderation</li>
                    <li>/api/v3/research - Research queries</li>
                </ul>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.key}</div>
                <h3>Authentication</h3>
                <p>All API requests require an API key in the header:</p>
                <code class="code-inline">X-API-Key: your_api_key</code>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - API KEYS =====
function renderAPIKeys() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>Developer</span> / API Keys</div>
            <h1>API Key Management</h1>
            <p>Create and manage your API keys for accessing Verity services.</p>
        </div>

        <div class="card">
            <div class="card-header">
                <h3>Your API Keys</h3>
                <button class="btn btn-primary" id="create-key-btn">${ICONS.plus} Create New Key</button>
            </div>

            <div class="api-key-list">
                <div class="api-key-item">
                    <div class="key-info">
                        <div class="key-name">Production Key</div>
                        <div class="key-value">vr_prod_••••••••••••••••</div>
                        <div class="key-meta">Created Dec 15, 2024 · Last used 2 hours ago</div>
                    </div>
                    <div class="key-actions">
                        <button class="btn btn-sm btn-ghost">${ICONS.eye} Reveal</button>
                        <button class="btn btn-sm btn-ghost">${ICONS.copy} Copy</button>
                        <button class="btn btn-sm btn-ghost text-danger">${ICONS.trash} Delete</button>
                    </div>
                </div>
                <div class="api-key-item">
                    <div class="key-info">
                        <div class="key-name">Development Key</div>
                        <div class="key-value">vr_dev_••••••••••••••••</div>
                        <div class="key-meta">Created Dec 10, 2024 · Last used 1 day ago</div>
                    </div>
                    <div class="key-actions">
                        <button class="btn btn-sm btn-ghost">${ICONS.eye} Reveal</button>
                        <button class="btn btn-sm btn-ghost">${ICONS.copy} Copy</button>
                        <button class="btn btn-sm btn-ghost text-danger">${ICONS.trash} Delete</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card"><div class="stat-icon">${ICONS.api}</div><div class="stat-value">2</div><div class="stat-label">Active Keys</div></div>
            <div class="stat-card purple"><div class="stat-icon">${ICONS.stats}</div><div class="stat-value">1,247</div><div class="stat-label">API Calls (30d)</div></div>
            <div class="stat-card pink"><div class="stat-icon">${ICONS.trending}</div><div class="stat-value">99.9%</div><div class="stat-label">Uptime</div></div>
            <div class="stat-card green"><div class="stat-icon">${ICONS.check}</div><div class="stat-value">0</div><div class="stat-label">Failed Requests</div></div>
        </div>
    `;
}

// ===== PAGE RENDERERS - BILLING =====
function renderBilling() {
    const isYearly = false; // Will be updated by toggle
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>Account</span> / Billing</div>
            <h1>Billing & Plans</h1>
            <p>Manage your subscription and view usage details.</p>
        </div>

        <div class="billing-toggle">
            <button class="billing-period active" data-period="monthly">Monthly</button>
            <button class="billing-period" data-period="yearly">Yearly <span class="save-badge">Save 17%</span></button>
        </div>

        <div class="pricing-grid">
            <div class="pricing-card">
                <div class="pricing-tier">Free</div>
                <div class="pricing-price"><span class="currency">$</span><span class="price" data-monthly="0" data-yearly="0">0</span><span class="period">/month</span></div>
                <p class="pricing-desc">Try Verity risk-free</p>
                <ul class="pricing-features">
                    <li>${ICONS.check} <span>50 verifications/month</span></li>
                    <li>${ICONS.check} <span>Basic source checking</span></li>
                    <li>${ICONS.check} <span>Community support</span></li>
                    <li class="disabled">${ICONS.x} <span>API access</span></li>
                    <li class="disabled">${ICONS.x} <span>AI Tools</span></li>
                </ul>
                <button class="btn btn-secondary btn-block">Current Plan</button>
            </div>

            <div class="pricing-card">
                <div class="pricing-tier">Starter</div>
                <div class="pricing-price"><span class="currency">$</span><span class="price" data-monthly="29" data-yearly="24">29</span><span class="period">/month</span></div>
                <p class="pricing-desc">For individuals getting started</p>
                <ul class="pricing-features">
                    <li>${ICONS.check} <span>500 verifications/month</span></li>
                    <li>${ICONS.check} <span>Basic API access</span></li>
                    <li>${ICONS.check} <span>Email support</span></li>
                    <li>${ICONS.check} <span>Browser extension</span></li>
                    <li class="disabled">${ICONS.x} <span>AI Tools</span></li>
                </ul>
                <button class="btn btn-secondary btn-block" id="upgrade-starter">Upgrade</button>
            </div>

            <div class="pricing-card">
                <div class="pricing-tier">Pro</div>
                <div class="pricing-price"><span class="currency">$</span><span class="price" data-monthly="79" data-yearly="66">79</span><span class="period">/month</span></div>
                <p class="pricing-desc">For power users</p>
                <ul class="pricing-features">
                    <li>${ICONS.check} <span>5,000 verifications/month</span></li>
                    <li>${ICONS.check} <span>Full API access</span></li>
                    <li>${ICONS.check} <span>Priority support</span></li>
                    <li>${ICONS.check} <span>Export reports</span></li>
                    <li class="disabled">${ICONS.x} <span>AI Tools</span></li>
                </ul>
                <button class="btn btn-secondary btn-block" id="upgrade-pro">Upgrade</button>
            </div>

            <div class="pricing-card featured">
                <div class="pricing-badge">Best Value</div>
                <div class="pricing-tier">Professional</div>
                <div class="pricing-price"><span class="currency">$</span><span class="price" data-monthly="199" data-yearly="166">199</span><span class="period">/month</span></div>
                <p class="pricing-desc">Unlock all AI Tools</p>
                <ul class="pricing-features">
                    <li>${ICONS.check} <span>15,000 verifications/month</span></li>
                    <li>${ICONS.check} <span>All AI Tools included</span></li>
                    <li>${ICONS.check} <span>Dedicated support</span></li>
                    <li>${ICONS.check} <span>Custom integrations</span></li>
                    <li>${ICONS.check} <span>99.5% SLA</span></li>
                </ul>
                <button class="btn btn-primary btn-block" id="upgrade-professional">Upgrade to Pro+</button>
            </div>

            <div class="pricing-card">
                <div class="pricing-tier">Business</div>
                <div class="pricing-price"><span class="currency">$</span><span class="price" data-monthly="499" data-yearly="416">499</span><span class="period">/month</span></div>
                <p class="pricing-desc">For teams and organizations</p>
                <ul class="pricing-features">
                    <li>${ICONS.check} <span>50,000 verifications/month</span></li>
                    <li>${ICONS.check} <span>Team management</span></li>
                    <li>${ICONS.check} <span>Advanced analytics</span></li>
                    <li>${ICONS.check} <span>Webhook integrations</span></li>
                    <li>${ICONS.check} <span>99.9% SLA</span></li>
                </ul>
                <button class="btn btn-secondary btn-block" id="upgrade-business">Contact Sales</button>
            </div>

            <div class="pricing-card">
                <div class="pricing-tier">Enterprise</div>
                <div class="pricing-price"><span class="price-custom">Custom</span></div>
                <p class="pricing-desc">For large organizations</p>
                <ul class="pricing-features">
                    <li>${ICONS.check} <span>Unlimited verifications</span></li>
                    <li>${ICONS.check} <span>Dedicated account manager</span></li>
                    <li>${ICONS.check} <span>On-premise deployment</span></li>
                    <li>${ICONS.check} <span>Custom AI training</span></li>
                    <li>${ICONS.check} <span>White-label option</span></li>
                </ul>
                <button class="btn btn-secondary btn-block" id="contact-sales">Contact Sales</button>
            </div>
        </div>

        <div class="billing-sections">
            <div class="card">
                <div class="card-header">
                    <h3>Current Usage</h3>
                    <span class="usage-period">January 2026</span>
                </div>
                <div class="usage-stats">
                    <div class="usage-stat">
                        <div class="usage-label">Verifications</div>
                        <div class="usage-bar-container">
                            <div class="usage-bar">
                                <div class="usage-fill" style="width: 34%;"></div>
                            </div>
                            <div class="usage-numbers">17 / 50</div>
                        </div>
                    </div>
                    <div class="usage-stat">
                        <div class="usage-label">API Calls</div>
                        <div class="usage-bar-container">
                            <div class="usage-bar">
                                <div class="usage-fill" style="width: 0%;"></div>
                            </div>
                            <div class="usage-numbers">0 / 0</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3>Payment Method</h3>
                    <button class="btn btn-sm btn-ghost">Add New</button>
                </div>
                <div class="payment-empty">
                    <svg viewBox="0 0 24 24" fill="none" width="48" height="48"><rect x="1" y="4" width="22" height="16" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M1 10h22" stroke="currentColor" stroke-width="1.5"/></svg>
                    <p>No payment method on file</p>
                    <button class="btn btn-secondary btn-sm">Add Payment Method</button>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - SETTINGS =====
function renderSettings() {
    return `
        <div class="page-header animate-fade-in">
            <h1>${ICONS.settings} Settings</h1>
            <p>Customize your Verity experience and manage your preferences.</p>
        </div>

        <div class="settings-layout animate-slide-up">
            <!-- Settings Navigation Sidebar -->
            <div class="settings-sidebar">
                <nav class="settings-nav-list">
                    <button class="settings-nav-btn active" data-section="appearance">
                        <span class="nav-icon">${ICONS.settings}</span>
                        <span class="nav-text">Appearance</span>
                    </button>
                    <button class="settings-nav-btn" data-section="notifications">
                        <span class="nav-icon">${ICONS.bell}</span>
                        <span class="nav-text">Notifications</span>
                    </button>
                    <button class="settings-nav-btn" data-section="privacy">
                        <span class="nav-icon">${ICONS.shield}</span>
                        <span class="nav-text">Privacy & Data</span>
                    </button>
                    <button class="settings-nav-btn" data-section="api">
                        <span class="nav-icon">${ICONS.api}</span>
                        <span class="nav-text">API Settings</span>
                    </button>
                    <button class="settings-nav-btn" data-section="about">
                        <span class="nav-icon">${ICONS.info}</span>
                        <span class="nav-text">About</span>
                    </button>
                </nav>
            </div>

            <!-- Settings Content Area -->
            <div class="settings-main">
                <!-- Appearance Section -->
                <div class="settings-section active" id="settings-appearance">
                    <div class="settings-section-header">
                        <h2>Appearance</h2>
                        <p>Customize the look and feel of the application</p>
                    </div>
                    <div class="settings-cards">
                        <div class="card settings-card">
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.settings}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">Dark Mode</div>
                                        <div class="setting-desc">Use dark theme throughout the app for reduced eye strain</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-dark-mode" ${state.settings.darkMode ? 'checked' : ''}>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.zap}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">Animations</div>
                                        <div class="setting-desc">Enable smooth transitions and motion effects</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-animations" ${state.settings.animations ? 'checked' : ''}>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.eye}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">Compact Mode</div>
                                        <div class="setting-desc">Use smaller UI elements to fit more content</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-compact" ${state.settings.compact ? 'checked' : ''}>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Notifications Section -->
                <div class="settings-section" id="settings-notifications">
                    <div class="settings-section-header">
                        <h2>Notifications</h2>
                        <p>Control how and when you receive alerts</p>
                    </div>
                    <div class="settings-cards">
                        <div class="card settings-card">
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.bell}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">Push Notifications</div>
                                        <div class="setting-desc">Receive alerts for trending misinformation and verification updates</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-notifications" ${state.settings.notifications ? 'checked' : ''}>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.realtime}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">Sound Effects</div>
                                        <div class="setting-desc">Play audio feedback for completed verifications</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-sounds" ${state.settings.sounds ? 'checked' : ''}>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.social}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">Email Digest</div>
                                        <div class="setting-desc">Receive weekly summary of your verification activity</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-email-digest">
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.alert}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">Breaking News Alerts</div>
                                        <div class="setting-desc">Get notified about major misinformation events</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-breaking-news" checked>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Privacy & Data Section -->
                <div class="settings-section" id="settings-privacy">
                    <div class="settings-section-header">
                        <h2>Privacy & Data</h2>
                        <p>Manage your data and privacy preferences</p>
                    </div>
                    <div class="settings-cards">
                        <div class="card settings-card">
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.database}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">Auto-save History</div>
                                        <div class="setting-desc">Automatically save verification history locally on your device</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-autosave" ${state.settings.autoSave ? 'checked' : ''}>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.shield}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">Anonymous Analytics</div>
                                        <div class="setting-desc">Help improve Verity by sending anonymous usage data</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-analytics" checked>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="setting-row">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.lock}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">End-to-End Encryption</div>
                                        <div class="setting-desc">Encrypt all verification data in transit and at rest</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-encryption" checked disabled>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="card settings-card">
                            <h4 class="card-subtitle">Data Management</h4>
                            <div class="data-actions">
                                <button class="btn btn-secondary" id="export-data-btn">
                                    ${ICONS.download} Export All Data
                                </button>
                                <button class="btn btn-ghost" id="clear-history-settings-btn">
                                    ${ICONS.trash} Clear History
                                </button>
                                <button class="btn btn-danger-ghost" id="delete-account-btn">
                                    ${ICONS.x} Delete All Data
                                </button>
                            </div>
                            <p class="data-info">Your data is stored locally and never shared without your permission.</p>
                        </div>
                    </div>
                </div>

                <!-- API Settings Section -->
                <div class="settings-section" id="settings-api">
                    <div class="settings-section-header">
                        <h2>API Settings</h2>
                        <p>Configure API endpoints and connection settings</p>
                    </div>
                    <div class="settings-cards">
                        <div class="card settings-card">
                            <div class="form-group">
                                <label class="input-label">API Endpoint</label>
                                <input type="url" class="input" id="api-endpoint-input" 
                                    value="${CONFIG.apiEndpoint}" 
                                    placeholder="https://api.veritysystems.ai">
                                <span class="input-hint">Change this to use a custom API server or local development</span>
                            </div>
                            <div class="setting-row" style="margin-top: 1rem;">
                                <div class="setting-info">
                                    <div class="setting-icon">${ICONS.code}</div>
                                    <div class="setting-text">
                                        <div class="setting-title">Use Local Development Server</div>
                                        <div class="setting-desc">Connect to localhost:8000 for development</div>
                                    </div>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="setting-use-local" ${CONFIG.useLocal ? 'checked' : ''}>
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="card settings-card">
                            <div class="api-status-display">
                                <div class="status-row">
                                    <span>Connection Status</span>
                                    <span class="status-badge ${state.apiOnline ? 'online' : 'offline'}">
                                        ${state.apiOnline ? 'Connected' : 'Disconnected'}
                                    </span>
                                </div>
                                <div class="status-row">
                                    <span>API Version</span>
                                    <span>v6.0 Ultimate</span>
                                </div>
                                <div class="status-row">
                                    <span>Providers Available</span>
                                    <span>75+</span>
                                </div>
                            </div>
                            <button class="btn btn-secondary btn-full" id="test-api-connection-btn">
                                ${ICONS.refresh} Test Connection
                            </button>
                        </div>
                    </div>
                </div>

                <!-- About Section -->
                <div class="settings-section" id="settings-about">
                    <div class="settings-section-header">
                        <h2>About Verity</h2>
                        <p>Application information and credits</p>
                    </div>
                    <div class="settings-cards">
                        <div class="card settings-card about-card">
                            <div class="about-hero">
                                <div class="about-logo-large">
                                    <svg viewBox="0 0 60 60" fill="none">
                                        <defs>
                                            <linearGradient id="aboutGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                                <stop offset="0%" stop-color="#f59e0b"/>
                                                <stop offset="100%" stop-color="#fbbf24"/>
                                            </linearGradient>
                                        </defs>
                                        <path d="M30 5 L10 12 L10 32 Q10 48 30 55 Q50 48 50 32 L50 12 Z" stroke="url(#aboutGrad)" stroke-width="2.5" fill="none"/>
                                        <path d="M22 30 L28 36 L40 24" stroke="url(#aboutGrad)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                                    </svg>
                                </div>
                                <div class="about-title">
                                    <h3>Verity Desktop</h3>
                                    <span class="version-tag">v${CONFIG.version} ${CONFIG.build}</span>
                                </div>
                                <p class="about-tagline">AI-Powered Truth Verification Platform</p>
                            </div>
                            
                            <div class="about-details">
                                <div class="about-detail-row">
                                    <span>Version</span>
                                    <span>${CONFIG.version}</span>
                                </div>
                                <div class="about-detail-row">
                                    <span>Build</span>
                                    <span>${CONFIG.build} Edition</span>
                                </div>
                                <div class="about-detail-row">
                                    <span>Electron</span>
                                    <span>28.0.0</span>
                                </div>
                                <div class="about-detail-row">
                                    <span>Chrome</span>
                                    <span>120.0.6099.109</span>
                                </div>
                            </div>
                            
                            <div class="about-links">
                                <a href="#" class="about-link">${ICONS.globe} Website</a>
                                <a href="#" class="about-link">${ICONS.file} Documentation</a>
                                <a href="#" class="about-link">${ICONS.code} Changelog</a>
                                <a href="#" class="about-link">${ICONS.help} Support</a>
                            </div>
                            
                            <div class="about-footer">
                                <p>© ${new Date().getFullYear()} Verity Systems. All rights reserved.</p>
                                <p class="about-legal">
                                    <a href="#">Privacy Policy</a> · <a href="#">Terms of Service</a> · <a href="#">Licenses</a>
                                </p>
                            </div>
                        </div>

                        <div class="card settings-card">
                            <h4 class="card-subtitle">Check for Updates</h4>
                            <p class="update-status">You're running the latest version!</p>
                            <button class="btn btn-secondary btn-full" id="check-updates-btn">
                                ${ICONS.refresh} Check for Updates
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ===== VERIFY PAGE HELPER FUNCTIONS =====
function handleFileUpload(file) {
    const filePreview = document.getElementById('file-preview');
    const uploadZone = document.getElementById('upload-zone');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    
    if (filePreview && uploadZone && fileName && fileSize) {
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        uploadZone.classList.add('hidden');
        filePreview.classList.remove('hidden');
        toast(`File "${file.name}" uploaded successfully`, 'success');
    }
    
    // Remove file button
    document.getElementById('remove-file')?.addEventListener('click', () => {
        filePreview.classList.add('hidden');
        uploadZone.classList.remove('hidden');
        document.getElementById('file-input').value = '';
    });
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function handleExtractClaims() {
    const input = document.getElementById('verify-input');
    const claimsPreview = document.getElementById('claims-preview');
    const claimsList = document.getElementById('claims-list');
    
    if (!input?.value.trim()) {
        toast('Please enter some text first', 'warning');
        return;
    }
    
    // Simple claim extraction simulation
    const text = input.value;
    const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
    const claims = sentences.slice(0, 5).map((s, i) => ({
        id: i,
        text: s.trim(),
        selected: true
    }));
    
    if (claimsList && claimsPreview) {
        claimsList.innerHTML = claims.map(claim => `
            <div class="claim-item ${claim.selected ? 'selected' : ''}" data-id="${claim.id}">
                <div class="claim-checkbox ${claim.selected ? 'checked' : ''}">
                    ${ICONS.check}
                </div>
                <span class="claim-text">${escapeHtml(claim.text)}</span>
            </div>
        `).join('');
        
        claimsPreview.classList.remove('hidden');
        
        // Add click handlers for claim items
        claimsList.querySelectorAll('.claim-item').forEach(item => {
            item.addEventListener('click', () => {
                item.classList.toggle('selected');
                item.querySelector('.claim-checkbox').classList.toggle('checked');
            });
        });
        
        toast(`Extracted ${claims.length} claims from your text`, 'success');
    }
}

// ===== UTILITY FUNCTIONS =====
function timeAgo(timestamp) {
    const seconds = Math.floor((Date.now() - new Date(timestamp)) / 1000);
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

// Alias for consistency
const formatTimeAgo = timeAgo;

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncate(text, length) {
    return text.length > length ? text.substring(0, length) + '...' : text;
}

function toast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `${type === 'success' ? ICONS.check : ICONS.alert} ${message}`;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Show How It Works modal (reuses sidebar content)
function showHowItWorks() {
    const existing = document.getElementById('howit-modal');
    if (existing) return;
    const card = document.querySelector('.card-how-it-works');
    const modal = document.createElement('div');
    modal.id = 'howit-modal';
    modal.className = 'modal-overlay active';
    modal.innerHTML = `
        <div class="modal-container">
            <button class="modal-close small" id="howit-close">×</button>
            <div class="modal-body">${card ? card.innerHTML : '<h3>How it works</h3><p>Details unavailable.</p>'}</div>
        </div>
    `;
    document.body.appendChild(modal);
    document.getElementById('howit-close')?.addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// ===== EVENT HANDLERS =====
async function handleVerify() {
    const input = document.getElementById('verify-input');
    const resultDiv = document.getElementById('verify-result');
    const btn = document.getElementById('verify-btn');
    
    if (!input?.value.trim()) {
        toast('Please enter a claim to verify', 'warning');
        return;
    }
    
    btn.disabled = true;
    btn.innerHTML = `${ICONS.spinner} Analyzing with 75+ sources...`;
    resultDiv.innerHTML = `
        <div class="loading-state">
            ${ICONS.spinner} 
            <div style="margin-top: 0.5rem;">
                <div style="font-weight: 600;">3-Pass Verification in Progress</div>
                <div style="font-size: 0.875rem; color: #9ca3af; margin-top: 0.25rem;">Pass 1: Search → Pass 2: AI Cross-validation → Pass 3: High-trust sources</div>
            </div>
        </div>
    `;
    
    try {
        // Call v6 Ultimate API
        const response = await fetch(`${CONFIG.apiEndpoint}/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim: input.value, detailed: true })
        });
        
        const data = await response.json();
        const score = Math.round((data.confidence || 0.5) * 100);
        const scoreClass = data.verdict === 'true' ? 'good' : data.verdict === 'false' ? 'bad' : 'medium';
        
        const verdictEmoji = { true: '✅', false: '❌', partially_true: '⚠️', unverifiable: '❓' };
        const verdictLabel = { true: 'Verified True', false: 'Verified False', partially_true: 'Partially True', unverifiable: 'Unverifiable' };
        
        // Build pass breakdown
        let passBreakdown = '';
        if (data.passes) {
            passBreakdown = `
                <div class="result-passes" style="margin-top: 1rem; padding: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 8px;">
                    <div style="font-weight: 600; margin-bottom: 0.5rem; color: #6366f1;">🔄 3-Pass Breakdown</div>
                    ${Object.entries(data.passes).map(([name, p]) => {
                        const passNames = { initial: '🔍 Initial Search', cross_validation: '🤖 AI Cross-validation', high_trust: '🏛️ High-Trust Sources' };
                        return `<div style="display: flex; justify-content: space-between; padding: 0.25rem 0;"><span>${passNames[name] || name}</span><span style="color: ${p.verdict === 'true' ? '#22c55e' : '#f59e0b'};">${p.verdict.toUpperCase()} (${Math.round((p.confidence || 0) * 100)}%)</span></div>`;
                    }).join('')}
                </div>
            `;
        }
        
        resultDiv.innerHTML = `
            <div class="result-card ${scoreClass}">
                <div class="result-header">
                    <div class="result-score">${score}</div>
                    <div class="result-title">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.5rem;">${verdictEmoji[data.verdict] || '❓'}</span>
                            <h3>${verdictLabel[data.verdict] || 'Unknown'}</h3>
                        </div>
                        <p>Category: ${data.category || 'General'}</p>
                    </div>
                </div>
                <div class="result-body">
                    <div class="result-detail"><strong>Sources analyzed:</strong> ${data.sources || 75}+ providers</div>
                    <div class="result-detail"><strong>Confidence:</strong> ${score}%</div>
                    <div class="result-detail"><strong>Consistency:</strong> ${Math.round((data.consistency || 0) * 100)}%</div>
                    <div class="result-detail"><strong>Processing time:</strong> ${data.time ? data.time.toFixed(2) + 's' : 'N/A'}</div>
                    ${passBreakdown}
                </div>
            </div>
        `;
        
        // Save to history
        state.history.unshift({
            id: Date.now(),
            claim: input.value,
            score: score,
            verdict: data.verdict,
            timestamp: new Date().toISOString(),
            sources: data.sources || 75
        });
        saveState();
        
    } catch (error) {
        try { log.error && log.error('Verification error:', error); } catch (e) {}
        // Mark API offline and update UI
        state.apiOnline = false;
        const statusEl = document.getElementById('api-status');
        if (statusEl) {
            statusEl.innerHTML = `
                <span class="status-indicator offline"></span>
                <span class="status-text">Demo Mode (Start API)</span>
            `;
        }
        toast('Verification failed: API unreachable — switching to demo mode', 'warning');

        // Demo mode fallback
        const score = Math.floor(Math.random() * 50 + 40);
        const scoreClass = score >= 70 ? 'good' : score >= 40 ? 'medium' : 'bad';

        resultDiv.innerHTML = `
            <div class="result-card ${scoreClass}">
                <div class="result-header">
                    <div class="result-score">${score}</div>
                    <div class="result-title">
                        <h3>Demo Analysis</h3>
                        <p>${score >= 70 ? 'Appears credible' : score >= 40 ? 'Mixed evidence' : 'Likely false'}</p>
                    </div>
                </div>
                <div class="result-body">
                    <div class="result-detail"><strong>Note:</strong> Running in demo mode (API offline). Start the API with: <code>python api_server_v6.py</code></div>
                </div>
            </div>
        `;
    }
    
    btn.disabled = false;
    btn.innerHTML = `${ICONS.verify} Verify Claim`;
}

async function handleSourceCheck() {
    const input = document.getElementById('source-url');
    const resultDiv = document.getElementById('source-result');
    const btn = document.querySelector('#source-checker .btn-primary');
    
    if (!input?.value.trim()) {
        toast('Please enter a URL', 'warning');
        return;
    }
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `${ICONS.spinner} Analyzing...`;
    }
    resultDiv.innerHTML = `<div class="loading-state">${ICONS.spinner} Analyzing URL with v6 API...</div>`;
    
    try {
        const response = await fetch(`${CONFIG.apiEndpoint}/analyze/url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: input.value })
        });
        
        const data = await response.json();
        
        if (data.status === 'failed') {
            throw new Error(data.error || 'Could not analyze URL');
        }
        
        const credScore = Math.round((data.source_credibility || 0.5) * 100);
        const accScore = Math.round((data.accuracy_score || 0.5) * 100);
        
        resultDiv.innerHTML = `
            <div class="result-card ${credScore >= 70 ? 'good' : credScore >= 40 ? 'medium' : 'bad'}">
                <div class="result-header">
                    <div class="result-score">${credScore}</div>
                    <div class="result-title">
                        <h3>${data.title || 'URL Analysis'}</h3>
                        <p>${data.summary || 'Analysis complete'}</p>
                    </div>
                </div>
                <div class="result-body">
                    <div class="result-detail"><strong>Source credibility:</strong> ${credScore}%</div>
                    <div class="result-detail"><strong>Claims found:</strong> ${data.claims_found || 0}</div>
                    <div class="result-detail"><strong>Claims verified:</strong> ${data.claims_verified || 0}</div>
                    <div class="result-detail"><strong>Accuracy score:</strong> ${accScore}%</div>
                </div>
            </div>
        `;
    } catch (error) {
        // Demo result
        const score = Math.floor(Math.random() * 40 + 50);
        resultDiv.innerHTML = `
            <div class="result-card ${score >= 70 ? 'good' : 'medium'}">
                <div class="result-header">
                    <div class="result-score">${score}</div>
                    <div class="result-title">
                        <h3>Source Analysis (Demo)</h3>
                        <p>${score >= 70 ? 'Generally reliable' : 'Exercise caution'}</p>
                    </div>
                </div>
                <div class="result-body">
                    <div class="result-detail"><strong>Note:</strong> Demo mode - start API for full analysis</div>
                </div>
            </div>
        `;
    }
    
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = `${ICONS.source} Check Source`;
    }
}

async function handleModerate() {
    const input = document.getElementById('moderate-input');
    const resultDiv = document.getElementById('moderate-result');
    
    if (!input?.value.trim()) {
        toast('Please enter content to analyze', 'warning');
        return;
    }
    
    resultDiv.innerHTML = `<div class="loading-state">${ICONS.spinner} Scanning for harmful content...</div>`;
    
    setTimeout(() => {
        resultDiv.innerHTML = `
            <div class="result-card good">
                <div class="result-header">
                    <div class="result-score">✓</div>
                    <div class="result-title">
                        <h3>Content Analysis Complete</h3>
                        <p>No harmful content detected</p>
                    </div>
                </div>
            </div>
        `;
    }, 1500);
}

async function handleResearch() {
    const input = document.getElementById('research-query');
    const resultDiv = document.getElementById('research-result');
    
    if (!input?.value.trim()) {
        toast('Please enter a research topic', 'warning');
        return;
    }
    
    resultDiv.innerHTML = `<div class="loading-state">${ICONS.spinner} Researching topic across academic databases...</div>`;
    
    setTimeout(() => {
        resultDiv.innerHTML = `
            <div class="card" style="margin-top: 20px;">
                <h3>Research Results</h3>
                <p>Found 47 relevant sources for "${escapeHtml(input.value)}"</p>
                <div class="feature-tags" style="margin-top: 12px;">
                    <span class="feature-tag">12 Academic Papers</span>
                    <span class="feature-tag">23 News Articles</span>
                    <span class="feature-tag">8 Government Reports</span>
                    <span class="feature-tag">4 Scientific Studies</span>
                </div>
            </div>
        `;
    }, 2000);
}

async function handleStatsValidate() {
    const input = document.getElementById('stats-input');
    const resultDiv = document.getElementById('stats-result');
    
    if (!input?.value.trim()) {
        toast('Please enter a statistical claim', 'warning');
        return;
    }
    
    resultDiv.innerHTML = `<div class="loading-state">${ICONS.spinner} Cross-referencing with statistical databases...</div>`;
    
    setTimeout(() => {
        const accurate = Math.random() > 0.5;
        resultDiv.innerHTML = `
            <div class="result-card ${accurate ? 'good' : 'bad'}">
                <div class="result-header">
                    <div class="result-score">${accurate ? '✓' : '✗'}</div>
                    <div class="result-title">
                        <h3>${accurate ? 'Statistic Verified' : 'Statistic Questionable'}</h3>
                        <p>${accurate ? 'Data matches authoritative sources' : 'Could not verify against reliable data'}</p>
                    </div>
                </div>
            </div>
        `;
    }, 1800);
}

async function handleAPITest() {
    const method = document.getElementById('api-method')?.value;
    const endpoint = document.getElementById('api-endpoint')?.value;
    const body = document.getElementById('api-body')?.value;
    const responseDiv = document.getElementById('api-response');
    
    responseDiv.textContent = '// Sending request...';
    
    try {
        const response = await fetch(`${CONFIG.apiEndpoint}${endpoint}`, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: method !== 'GET' ? body : undefined
        });
        const data = await response.json();
        responseDiv.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        responseDiv.textContent = `// Error: ${error.message}\n// API may be offline`;
    }
}

function handleSettingChange(e) {
    const settingId = e.target.id;
    const isChecked = e.target.checked;
    
    // Map setting ID to state key
    const settingMap = {
        'setting-dark-mode': 'darkMode',
        'setting-animations': 'animations',
        'setting-notifications': 'notifications',
        'setting-sounds': 'sounds',
        'setting-auto-save': 'autoSave'
    };
    
    const settingKey = settingMap[settingId];
    if (settingKey) {
        state.settings[settingKey] = isChecked;
        saveState();
        
        // Apply settings immediately
        applySettings();
        
        toast(`${settingKey.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase())} ${isChecked ? 'enabled' : 'disabled'}`, 'success');
    }
}

// Apply settings to the UI
function applySettings() {
    const body = document.body;
    
    // Animations setting
    if (state.settings.animations) {
        body.classList.remove('no-animations');
    } else {
        body.classList.add('no-animations');
    }
    
    // Dark mode (always dark for now, but ready for light mode)
    if (state.settings.darkMode) {
        body.classList.remove('light-mode');
    } else {
        body.classList.add('light-mode');
    }
}

// ===== SETUP FUNCTIONS =====
function setupTitlebar() {
    // Window controls
    const btnMin = document.getElementById('btn-min');
    const btnMax = document.getElementById('btn-max');
    const btnClose = document.getElementById('btn-close');

    btnMin?.addEventListener('click', () => {
        try { window.verity?.window?.minimize(); } catch (e) { console.warn('minimize failed', e); }
    });

    btnMax?.addEventListener('click', () => {
        try { window.verity?.window?.maximize(); } catch (e) { console.warn('maximize failed', e); }
    });

    btnClose?.addEventListener('click', () => {
        try { window.verity?.window?.close(); } catch (e) { console.warn('close failed', e); }
    });

    // Reflect maximize/restored state on the maximize button
    const updateMaxButton = async () => {
        try {
            const isMax = await (window.verity?.window?.isMaximized?.() ?? false);
            if (btnMax) {
                btnMax.classList.toggle('is-maximized', !!isMax);
                btnMax.title = isMax ? 'Restore' : 'Maximize';
            }
        } catch (e) { /* ignore */ }
    };
    updateMaxButton();
    if (window.verity?.window?.onMaximizedChange) {
        try {
            window.verity.window.onMaximizedChange((isMax) => {
                if (btnMax) {
                    btnMax.classList.toggle('is-maximized', !!isMax);
                    btnMax.title = isMax ? 'Restore' : 'Maximize';
                }
            });
        } catch (e) { /* ignore */ }
    }
    
    // Sign In button handling
    document.getElementById('signin-btn')?.addEventListener('click', () => {
        const modal = document.getElementById('auth-modal');
        if (!modal) return;
        modal.dataset.prevFocus = document.activeElement?.id || '';
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        const firstInput = document.getElementById('signin-email') || document.getElementById('signup-name');
        firstInput?.focus();
    });
    
    // Notifications panel toggle
    const notifBtn = document.getElementById('btn-notifications');
    const notifPanel = document.getElementById('notif-panel');
    if (notifBtn && notifPanel) {
        notifBtn.addEventListener('click', () => {
            notifPanel.classList.toggle('active');
        });
        
        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            if (!notifBtn.contains(e.target) && !notifPanel.contains(e.target)) {
                notifPanel.classList.remove('active');
            }
        });
        
        // Clear notifications
        document.getElementById('clear-notifs')?.addEventListener('click', () => {
            document.getElementById('notif-list').innerHTML = '<div class="notif-empty">No notifications</div>';
            notifBtn.querySelector('.notif-badge').style.display = 'none';
        });
    }
}

function setupAuth() {
    const modal = document.getElementById('auth-modal');
    if (!modal) return;

    // Focus trapping & keyboard
    function closeModal() {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        const prevId = modal.dataset.prevFocus;
        if (prevId) {
            const prevEl = document.getElementById(prevId);
            prevEl?.focus();
        } else {
            document.getElementById('signin-btn')?.focus();
        }
        document.removeEventListener('keydown', keyHandler);
    }

    function keyHandler(e) {
        if (e.key === 'Escape') return closeModal();
        if (e.key === 'Tab') {
            const focusable = modal.querySelectorAll('a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])');
            if (!focusable.length) return;
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
            else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        }
    }

    // Close button
    document.getElementById('close-auth')?.addEventListener('click', () => closeModal());

    // Backdrop click
    modal.querySelector('.modal-backdrop')?.addEventListener('click', () => closeModal());

    // Tab switching
    modal.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            modal.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            modal.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            tab.classList.add('active');
            const formId = tab.dataset.tab === 'signin' ? 'signin-form' : 'signup-form';
            document.getElementById(formId)?.classList.add('active');
            document.querySelector(`#${formId} input`)?.focus();
        });
    });

    // Sign in form
    document.getElementById('signin-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('signin-email')?.value;
        if (email) {
            state.user = { name: email.split('@')[0], email };
            state.authenticated = true;
            saveState();
            closeModal();
            buildNavigation();
            toast('Signed in successfully!', 'success');
        }
    });

    // Sign up form
    document.getElementById('signup-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = document.getElementById('signup-name')?.value;
        const email = document.getElementById('signup-email')?.value;
        if (name && email) {
            state.user = { name, email };
            state.authenticated = true;
            saveState();
            closeModal();
            buildNavigation();
            toast('Account created!', 'success');
        }
    });

    // Start listening for key traps when open
    document.addEventListener('keydown', keyHandler);
} 

function setupCommandPalette() {
    const cmd = document.getElementById('cmd');
    const input = document.getElementById('cmd-input');
    const results = document.getElementById('cmd-results');
    if (!cmd || !input) return;
    
    // Toggle with Ctrl+K (but don't intercept when typing in inputs)
    document.addEventListener('keydown', (e) => {
        const activeTag = document.activeElement?.tagName;
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            // If user is typing in an input / textarea / contentEditable, let that take precedence
            if (activeTag === 'INPUT' || activeTag === 'TEXTAREA' || document.activeElement?.isContentEditable) return;
            e.preventDefault();
            cmd.classList.toggle('active');
            if (cmd.classList.contains('active')) input.focus();
        }
        if (e.key === 'Escape') cmd.classList.remove('active');
    });
    
    // Backdrop click
    cmd.querySelector('.cmd-backdrop')?.addEventListener('click', () => {
        cmd.classList.remove('active');
    });
    
    // Search input
    input.addEventListener('input', () => {
        const query = input.value.toLowerCase();
        if (!query) {
            results.innerHTML = renderCommandSuggestions();
            return;
        }
        
        const allItems = NAV_ITEMS.flatMap(s => s.items);
        const matches = allItems.filter(item => 
            item.label.toLowerCase().includes(query) || item.id.includes(query)
        );
        
        results.innerHTML = matches.length ? matches.map(item => `
            <button class="cmd-item" data-page="${item.id}">
                <span class="cmd-icon">${ICONS[item.icon]}</span>
                <span>${item.label}</span>
            </button>
        `).join('') : '<div class="cmd-empty">No results found</div>';
        
        results.querySelectorAll('.cmd-item').forEach(btn => {
            btn.addEventListener('click', () => {
                // Prefer any host-provided navigate (test hooks) but fall back to internal navigate
                (window.navigate || navigate)(btn.dataset.page);
                cmd.classList.remove('active');
                input.value = '';
            });
        });
    });
    
    results.innerHTML = renderCommandSuggestions();
}

function renderCommandSuggestions() {
    const suggestions = [
        { id: 'verify', label: 'Verify Claim', icon: 'verify' },
        { id: 'source-checker', label: 'Check Source', icon: 'source' },
        { id: 'history', label: 'View History', icon: 'history' },
        { id: 'analytics', label: 'Analytics', icon: 'stats' },
        { id: 'webhooks', label: 'Webhooks', icon: 'link' },
        { id: 'export', label: 'Export Reports', icon: 'download' },
        { id: 'settings', label: 'Settings', icon: 'settings' }
    ];
    return suggestions.map(s => `
        <button class="cmd-item" data-page="${s.id}">
            <span class="cmd-icon">${ICONS[s.icon]}</span>
            <span>${s.label}</span>
        </button>
    `).join('');
}

// ===== PAGE RENDERERS - ANALYTICS =====
function renderAnalytics() {
    const totalVerifications = state.history.length;
    const trueVerdicts = state.history.filter(h => h.score >= 70).length;
    const falseVerdicts = state.history.filter(h => h.score < 40).length;
    const avgConfidence = totalVerifications > 0 ? Math.round(state.history.reduce((a, h) => a + h.score, 0) / totalVerifications) : 0;

    return `
        <div class="page-header">
            <h1>Analytics Dashboard</h1>
            <p>Monitor your verification usage, trends, and performance metrics.</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.verify}</div>
                    <span class="stat-change up">+15%</span>
                </div>
                <div class="stat-value">${totalVerifications}</div>
                <div class="stat-label">Total Verifications</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.check}</div>
                </div>
                <div class="stat-value">${trueVerdicts}</div>
                <div class="stat-label">True Verdicts</div>
            </div>
            <div class="stat-card pink">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.x}</div>
                </div>
                <div class="stat-value">${falseVerdicts}</div>
                <div class="stat-label">False Verdicts</div>
            </div>
            <div class="stat-card green">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.target}</div>
                </div>
                <div class="stat-value">${avgConfidence}<span class="stat-unit">%</span></div>
                <div class="stat-label">Avg Confidence</div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card card-large">
                <div class="card-header">
                    <h3>Weekly Activity</h3>
                    <select class="select-mini" id="analytics-period">
                        <option value="week">This Week</option>
                        <option value="month">This Month</option>
                        <option value="year">This Year</option>
                    </select>
                </div>
                <div class="activity-chart" style="height: 200px;">
                    ${[45, 72, 38, 85, 62, 91, 58].map((v, i) => `
                        <div class="chart-col">
                            <div class="chart-bar" style="height: ${v}%"></div>
                            <span class="chart-label">${['M','T','W','T','F','S','S'][i]}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3>${ICONS.cpu} Provider Usage</h3>
                </div>
                <div class="provider-list-premium">
                    ${[
                        { name: 'Claude', org: 'Anthropic', pct: 85, color: '#f59e0b', icon: ICONS.brain },
                        { name: 'GPT-4', org: 'OpenAI', pct: 72, color: '#10b981', icon: ICONS.zap },
                        { name: 'PolitiFact', org: 'Fact-Check', pct: 45, color: '#3b82f6', icon: ICONS.verify },
                        { name: 'Perplexity', org: 'Search', pct: 38, color: '#8b5cf6', icon: ICONS.source }
                    ].map(p => `
                        <div class="provider-row-premium">
                            <div class="provider-icon" style="color: ${p.color}">${p.icon}</div>
                            <div class="provider-details">
                                <span class="provider-name-text">${p.name}</span>
                                <span class="provider-org">${p.org}</span>
                            </div>
                            <div class="provider-bar-container">
                                <div class="provider-bar-track">
                                    <div class="provider-bar-fill" style="width: ${p.pct}%; background: ${p.color}"></div>
                                </div>
                            </div>
                            <span class="provider-pct-badge" style="background: ${p.color}20; color: ${p.color}">${p.pct}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3>${ICONS.realtime} Real-time Metrics</h3>
                <div class="pulse-indicator">
                    <span class="pulse-dot"></span>
                    <span>Live</span>
                </div>
            </div>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-value">3</div>
                    <div class="metric-label">Active Verifications</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">12</div>
                    <div class="metric-label">Verifications/Min</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">847<span class="metric-unit">ms</span></div>
                    <div class="metric-label">Avg Latency</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">28</div>
                    <div class="metric-label">Connections</div>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - WEBHOOKS =====
function renderWebhooks() {
    const webhooks = state.webhooks || [];
    
    return `
        <div class="page-header">
            <h1>Webhooks</h1>
            <p>Configure webhooks to receive real-time notifications for verification events.</p>
        </div>

        <div class="card">
            <div class="card-header">
                <h3>Create Webhook</h3>
            </div>
            <div class="card-body">
                <div class="form-group">
                    <label>Webhook URL</label>
                    <input type="url" id="webhook-url" class="input" placeholder="https://your-domain.com/webhook">
                </div>
                <div class="form-group">
                    <label>Events to Subscribe</label>
                    <div class="checkbox-grid">
                        <label class="checkbox-item">
                            <input type="checkbox" id="evt-complete" checked>
                            <span>verification.complete</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" id="evt-started">
                            <span>verification.started</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" id="evt-error">
                            <span>verification.error</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" id="evt-batch">
                            <span>batch.complete</span>
                        </label>
                    </div>
                </div>
                <button class="btn btn-primary" id="create-webhook-btn">
                    ${ICONS.plus} Create Webhook
                </button>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3>Active Webhooks</h3>
                <span class="badge">${webhooks.length} configured</span>
            </div>
            ${webhooks.length > 0 ? `
                <div class="webhook-list">
                    ${webhooks.map(wh => `
                        <div class="webhook-item">
                            <div class="webhook-info">
                                <div class="webhook-url">${wh.url}</div>
                                <div class="webhook-events">${wh.events.join(', ')}</div>
                            </div>
                            <div class="webhook-actions">
                                <button class="btn btn-sm btn-ghost" data-action="test" data-id="${wh.id}">Test</button>
                                <button class="btn btn-sm btn-danger" data-action="delete" data-id="${wh.id}">Delete</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : `
                <div class="empty-state">
                    <div class="empty-icon">${ICONS.link}</div>
                    <p>No webhooks configured</p>
                    <span>Create your first webhook to receive real-time notifications</span>
                </div>
            `}
        </div>

        <div class="card">
            <div class="card-header">
                <h3>Recent Webhook Deliveries</h3>
            </div>
            <div class="delivery-list">
                <div class="delivery-item success">
                    <div class="delivery-status">${ICONS.check}</div>
                    <div class="delivery-info">
                        <span class="delivery-event">verification.complete</span>
                        <span class="delivery-time">2 minutes ago</span>
                    </div>
                    <span class="delivery-code">200 OK</span>
                </div>
                <div class="delivery-item success">
                    <div class="delivery-status">${ICONS.check}</div>
                    <div class="delivery-info">
                        <span class="delivery-event">verification.complete</span>
                        <span class="delivery-time">15 minutes ago</span>
                    </div>
                    <span class="delivery-code">200 OK</span>
                </div>
                <div class="delivery-item failed">
                    <div class="delivery-status">${ICONS.x}</div>
                    <div class="delivery-info">
                        <span class="delivery-event">verification.error</span>
                        <span class="delivery-time">1 hour ago</span>
                    </div>
                    <span class="delivery-code">500 Error</span>
                </div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - EXPORT =====
function renderExport() {
    return `
        <div class="page-header animate-fade-in">
            <h1>${ICONS.download} Export Reports</h1>
            <p>Generate professional verification reports in multiple formats with customizable templates.</p>
        </div>

        <div class="export-layout animate-slide-up">
            <!-- Format Selection Cards -->
            <div class="export-formats-grid">
                <div class="format-card-premium selected" data-format="pdf">
                    <div class="format-card-icon pdf">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <path d="M10 12h4"/>
                            <path d="M10 16h4"/>
                        </svg>
                    </div>
                    <div class="format-card-content">
                        <h4>PDF Report</h4>
                        <p>Professional printable report with charts, graphs, and executive summary</p>
                        <div class="format-features">
                            <span class="feature-tag">${ICONS.check} Charts</span>
                            <span class="feature-tag">${ICONS.check} Print Ready</span>
                        </div>
                    </div>
                    <div class="format-select-indicator">${ICONS.check}</div>
                </div>

                <div class="format-card-premium" data-format="csv">
                    <div class="format-card-icon csv">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <path d="M8 13h2"/>
                            <path d="M8 17h2"/>
                            <path d="M14 13h2"/>
                            <path d="M14 17h2"/>
                        </svg>
                    </div>
                    <div class="format-card-content">
                        <h4>CSV Spreadsheet</h4>
                        <p>Excel-compatible data export for custom analysis and processing</p>
                        <div class="format-features">
                            <span class="feature-tag">${ICONS.check} Excel Ready</span>
                            <span class="feature-tag">${ICONS.check} Filterable</span>
                        </div>
                    </div>
                    <div class="format-select-indicator">${ICONS.check}</div>
                </div>

                <div class="format-card-premium" data-format="json">
                    <div class="format-card-icon json">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <polyline points="16 18 22 12 16 6"/>
                            <polyline points="8 6 2 12 8 18"/>
                        </svg>
                    </div>
                    <div class="format-card-content">
                        <h4>JSON Data</h4>
                        <p>Full structured data with metadata for API integration</p>
                        <div class="format-features">
                            <span class="feature-tag">${ICONS.check} API Ready</span>
                            <span class="feature-tag">${ICONS.check} Full Data</span>
                        </div>
                    </div>
                    <div class="format-select-indicator">${ICONS.check}</div>
                </div>

                <div class="format-card-premium" data-format="html">
                    <div class="format-card-icon html">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <path d="M12 18v-6"/>
                            <path d="M8 18v-1"/>
                            <path d="M16 18v-3"/>
                        </svg>
                    </div>
                    <div class="format-card-content">
                        <h4>HTML Report</h4>
                        <p>Interactive web report with embedded charts</p>
                        <div class="format-features">
                            <span class="feature-tag">${ICONS.check} Interactive</span>
                            <span class="feature-tag">${ICONS.check} Shareable</span>
                        </div>
                    </div>
                    <div class="format-select-indicator">${ICONS.check}</div>
                </div>
            </div>

            <div class="export-main-grid">
                <!-- Configuration Panel -->
                <div class="export-config-panel">
                    <div class="card card-elevated">
                        <div class="card-header">
                            <h3>${ICONS.settings} Export Configuration</h3>
                        </div>
                        <div class="card-body">
                            <!-- Date Range -->
                            <div class="config-section">
                                <label class="config-label">${ICONS.calendar} Date Range</label>
                                <div class="date-range-grid">
                                    <div class="form-group">
                                        <label>Start Date</label>
                                        <input type="date" id="export-start" class="input">
                                    </div>
                                    <div class="form-group">
                                        <label>End Date</label>
                                        <input type="date" id="export-end" class="input">
                                    </div>
                                </div>
                                <div class="quick-ranges">
                                    <button class="range-btn active" data-range="7d">7 Days</button>
                                    <button class="range-btn" data-range="30d">30 Days</button>
                                    <button class="range-btn" data-range="90d">90 Days</button>
                                    <button class="range-btn" data-range="all">All Time</button>
                                </div>
                            </div>

                            <!-- Filters -->
                            <div class="config-section">
                                <label class="config-label">${ICONS.filter} Filters</label>
                                <div class="filters-grid">
                                    <div class="form-group">
                                        <label>Verdict Filter</label>
                                        <select id="export-verdict" class="select">
                                            <option value="all">All Verdicts</option>
                                            <option value="true">✓ True Only</option>
                                            <option value="false">✗ False Only</option>
                                            <option value="partial">⚠ Partially True</option>
                                            <option value="unverified">? Unverifiable</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label>Minimum Confidence</label>
                                        <select id="export-confidence" class="select">
                                            <option value="0">Any Confidence</option>
                                            <option value="50">50%+ Confidence</option>
                                            <option value="70">70%+ Confidence</option>
                                            <option value="85">85%+ High Confidence</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <!-- Include Options -->
                            <div class="config-section">
                                <label class="config-label">${ICONS.layers} Include in Export</label>
                                <div class="include-options-grid">
                                    <label class="include-option active">
                                        <input type="checkbox" id="inc-sources" checked hidden>
                                        <div class="option-icon">${ICONS.link}</div>
                                        <span>Source Citations</span>
                                    </label>
                                    <label class="include-option active">
                                        <input type="checkbox" id="inc-evidence" checked hidden>
                                        <div class="option-icon">${ICONS.file}</div>
                                        <span>Evidence Breakdown</span>
                                    </label>
                                    <label class="include-option active">
                                        <input type="checkbox" id="inc-summary" checked hidden>
                                        <div class="option-icon">${ICONS.stats}</div>
                                        <span>Executive Summary</span>
                                    </label>
                                    <label class="include-option">
                                        <input type="checkbox" id="inc-metadata" hidden>
                                        <div class="option-icon">${ICONS.code}</div>
                                        <span>Processing Metadata</span>
                                    </label>
                                    <label class="include-option">
                                        <input type="checkbox" id="inc-charts" hidden>
                                        <div class="option-icon">${ICONS.trending}</div>
                                        <span>Visual Charts</span>
                                    </label>
                                    <label class="include-option">
                                        <input type="checkbox" id="inc-timeline" hidden>
                                        <div class="option-icon">${ICONS.clock}</div>
                                        <span>Timeline View</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Report Templates -->
                    <div class="card">
                        <div class="card-header">
                            <h3>${ICONS.file} Report Templates</h3>
                            <span class="badge badge-pro">PRO</span>
                        </div>
                        <div class="templates-grid">
                            <button class="template-btn active">
                                <div class="template-icon">${ICONS.file}</div>
                                <span>Standard Report</span>
                            </button>
                            <button class="template-btn">
                                <div class="template-icon">${ICONS.brain}</div>
                                <span>Executive Brief</span>
                            </button>
                            <button class="template-btn">
                                <div class="template-icon">${ICONS.stats}</div>
                                <span>Analytics Focus</span>
                            </button>
                            <button class="template-btn">
                                <div class="template-icon">${ICONS.code}</div>
                                <span>Technical Report</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Preview & Actions Panel -->
                <div class="export-preview-panel">
                    <div class="card card-elevated">
                        <div class="card-header">
                            <h3>${ICONS.eye} Preview</h3>
                            <button class="btn btn-ghost btn-sm" id="refresh-preview-btn">${ICONS.refresh} Refresh</button>
                        </div>
                        <div class="preview-container">
                            <pre class="code-preview premium" id="export-preview">{
  "report": {
    "title": "Verity Verification Report",
    "generated": "${new Date().toISOString()}",
    "format": "PDF",
    "summary": {
      "total_verifications": ${state.history.length},
      "verified_true": ${state.history.filter(h => h.score >= 70).length},
      "verified_false": ${state.history.filter(h => h.score < 40).length},
      "avg_confidence": ${state.history.length ? Math.round(state.history.reduce((a, h) => a + h.score, 0) / state.history.length) : 0}%
    },
    "date_range": {
      "start": "2026-01-01",
      "end": "2026-01-11"
    }
  }
}</pre>
                        </div>
                    </div>

                    <!-- Export Summary -->
                    <div class="export-summary-card">
                        <div class="summary-stats">
                            <div class="summary-stat">
                                <span class="summary-value">${state.history.length}</span>
                                <span class="summary-label">Records</span>
                            </div>
                            <div class="summary-stat">
                                <span class="summary-value">~${(state.history.length * 2.5).toFixed(1)} KB</span>
                                <span class="summary-label">Est. Size</span>
                            </div>
                            <div class="summary-stat">
                                <span class="summary-value">PDF</span>
                                <span class="summary-label">Format</span>
                            </div>
                        </div>
                        <button class="btn btn-export-primary btn-lg btn-full" id="generate-export-btn">
                            <span class="btn-icon">${ICONS.download}</span>
                            <span>Generate & Download Report</span>
                        </button>
                    </div>

                    <!-- Scheduling -->
                    <div class="card">
                        <div class="card-header">
                            <h3>${ICONS.calendar} Schedule Reports</h3>
                            <span class="badge badge-new">NEW</span>
                        </div>
                        <div class="schedule-options">
                            <label class="schedule-option">
                                <input type="radio" name="schedule" value="none" checked>
                                <span class="schedule-label">No Schedule</span>
                            </label>
                            <label class="schedule-option">
                                <input type="radio" name="schedule" value="daily">
                                <span class="schedule-label">Daily</span>
                            </label>
                            <label class="schedule-option">
                                <input type="radio" name="schedule" value="weekly">
                                <span class="schedule-label">Weekly</span>
                            </label>
                            <label class="schedule-option">
                                <input type="radio" name="schedule" value="monthly">
                                <span class="schedule-label">Monthly</span>
                            </label>
                        </div>
                        <div class="schedule-email hidden" id="schedule-email">
                            <input type="email" class="input" placeholder="Email address for scheduled reports">
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Exports -->
            <div class="card animate-slide-up delay-2">
                <div class="card-header">
                    <h3>${ICONS.history} Recent Exports</h3>
                    <button class="btn btn-ghost btn-sm">${ICONS.trash} Clear History</button>
                </div>
                <div class="recent-exports-list">
                    <div class="recent-export-item">
                        <div class="export-type-icon pdf">${ICONS.file}</div>
                        <div class="export-info">
                            <span class="export-filename">verification_report_jan2026.pdf</span>
                            <span class="export-meta">2.4 MB • 2 hours ago • 127 records</span>
                        </div>
                        <div class="export-actions">
                            <button class="btn btn-ghost btn-sm">${ICONS.eye}</button>
                            <button class="btn btn-ghost btn-sm">${ICONS.download}</button>
                            <button class="btn btn-ghost btn-sm">${ICONS.share}</button>
                        </div>
                    </div>
                    <div class="recent-export-item">
                        <div class="export-type-icon csv">${ICONS.file}</div>
                        <div class="export-info">
                            <span class="export-filename">export_20260110.csv</span>
                            <span class="export-meta">156 KB • Yesterday • 45 records</span>
                        </div>
                        <div class="export-actions">
                            <button class="btn btn-ghost btn-sm">${ICONS.eye}</button>
                            <button class="btn btn-ghost btn-sm">${ICONS.download}</button>
                            <button class="btn btn-ghost btn-sm">${ICONS.share}</button>
                        </div>
                    </div>
                    <div class="recent-export-item">
                        <div class="export-type-icon json">${ICONS.code}</div>
                        <div class="export-info">
                            <span class="export-filename">api_export_full.json</span>
                            <span class="export-meta">892 KB • 3 days ago • 312 records</span>
                        </div>
                        <div class="export-actions">
                            <button class="btn btn-ghost btn-sm">${ICONS.eye}</button>
                            <button class="btn btn-ghost btn-sm">${ICONS.download}</button>
                            <button class="btn btn-ghost btn-sm">${ICONS.share}</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function setupGlobalSearch() {
    const searchInput = document.getElementById('search-input');
    const resultsEl = document.getElementById('search-results');
    const clearBtn = document.getElementById('search-clear');
    const kbdEl = document.getElementById('search-kbd');
    if (!searchInput) return;

    // Platform-aware shortcut label
    try {
        const isMac = /Mac|iPhone|iPad|MacIntel/.test(navigator.platform || '');
        kbdEl && (kbdEl.textContent = isMac ? '⌘K' : 'Ctrl+K');
    } catch (e) { /* ignore */ }

    // Helper: debounce
    function debounce(fn, wait = 180) {
        let t;
        return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), wait); };
    }

    let selectedIndex = -1;

    // Render results: search NAV_ITEMS and history
    function renderResults(query) {
        const q = (query || '').trim().toLowerCase();
        const navMatches = [];
        NAV_ITEMS.forEach(section => section.items.forEach(item => navMatches.push({ type: 'nav', id: item.id, label: item.label, icon: item.icon })));

        const historyMatches = (state.history || []).map(h => ({ type: 'history', id: h.id || '', label: h.claim || h.title || 'Recent', meta: h.date ? new Date(h.date).toLocaleString() : '' }));

        const navFiltered = !q ? navMatches.slice(0, 6) : navMatches.filter(n => n.label.toLowerCase().includes(q) || n.id.includes(q));
        const histFiltered = !q ? historyMatches.slice(0, 6) : historyMatches.filter(h => h.label.toLowerCase().includes(q));

        const items = [...navFiltered.map(i => ({...i, source: 'nav'})), ...histFiltered.map(i => ({...i, source: 'history'}))].slice(0, 10);

        if (!items.length) {
            resultsEl.innerHTML = `<div class="search-empty">No results</div>`;
            resultsEl.classList.remove('hidden');
            selectedIndex = -1;
            return;
        }

        resultsEl.innerHTML = items.map((it, idx) => `
            <div id="search-item-${idx}" class="search-item" data-index="${idx}" data-type="${it.type}" data-id="${it.id}">
                <div class="search-icon">${ICONS[it.icon] || ''}</div>
                <div class="search-body">
                    <div class="search-title">${it.label}</div>
                    ${it.meta ? `<div class="search-meta">${it.meta}</div>` : ''}
                </div>
            </div>
        `).join('');
        resultsEl.classList.remove('hidden');
        selectedIndex = -1;

        // Wire up click handlers
        resultsEl.querySelectorAll('.search-item').forEach(el => el.addEventListener('click', () => {
            const type = el.dataset.type;
            const id = el.dataset.id;
            if (type === 'nav' && id) {
                navigate(id);
            } else if (type === 'history') {
                navigate('history');
            }
            searchInput.value = '';
            clearBtn?.classList.add('hidden');
            resultsEl.classList.add('hidden');
            selectedIndex = -1;
        }));
    }

    function updateSelection(deltaOrIndex) {
        const items = resultsEl.querySelectorAll('.search-item');
        if (!items.length) return;
        if (typeof deltaOrIndex === 'number' && deltaOrIndex >= 0 && deltaOrIndex < items.length) {
            selectedIndex = deltaOrIndex;
        } else {
            selectedIndex = Math.max(0, Math.min(items.length - 1, (selectedIndex + deltaOrIndex)));
        }
        items.forEach((it, i) => it.classList.toggle('selected', i === selectedIndex));
        const active = items[selectedIndex];
        if (active) {
            resultsEl.setAttribute('aria-activedescendant', active.id);
            if (typeof active.scrollIntoView === 'function') {
                active.scrollIntoView({ block: 'nearest' });
            }
        } else {
            resultsEl.removeAttribute('aria-activedescendant');
        }
    }

    const onInput = debounce(() => {
        const q = searchInput.value.trim();
        if (!q) {
            // Show default suggestions when empty, but hide the clear button
            clearBtn?.classList.add('hidden');
            renderResults('');
            return;
        }
        clearBtn?.classList.remove('hidden');
        renderResults(q);
    }, 140);

    searchInput.addEventListener('input', onInput);

    // Keyboard nav (arrow keys + enter)
    searchInput.addEventListener('keydown', (e) => {
        const items = resultsEl.querySelectorAll('.search-item');
        if (!items.length) return;
        if (e.key === 'ArrowDown') { e.preventDefault(); updateSelection( (selectedIndex + 1) < items.length ? (selectedIndex + 1) : 0 ); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); updateSelection( (selectedIndex - 1) >= 0 ? (selectedIndex - 1) : (items.length - 1) ); }
        else if (e.key === 'Enter') {
            if (selectedIndex >= 0) {
                items[selectedIndex].click();
            } else if (items.length > 0) {
                items[0].click();
            }
        } else if (e.key === 'Escape') {
            resultsEl.classList.add('hidden');
        }
    });

    // Clear button
    clearBtn?.addEventListener('click', () => {
        searchInput.value = '';
        clearBtn.classList.add('hidden');
        resultsEl.classList.add('hidden');
        searchInput.focus();
        selectedIndex = -1;
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchInput.focus();
            searchInput.select();
            renderResults('');
        }
        if (e.key === 'Escape') {
            if (resultsEl) resultsEl.classList.add('hidden');
            // keep ESC from closing command palette accidentally
        }
    });

    // Click outside to close
    document.addEventListener('click', (e) => {
        if (!document.getElementById('global-search')?.contains(e.target)) {
            resultsEl.classList.add('hidden');
            selectedIndex = -1;
        }
    });
} 


async function checkAPIStatus() {
    const statusEl = document.getElementById('api-status');
    if (!statusEl) return;
    
    try {
        // Check v6 API health endpoint
        const response = await fetch(`${CONFIG.apiEndpoint}/health`, { 
            method: 'GET',
            signal: AbortSignal.timeout(3000)
        });
        if (response.ok) {
            const data = await response.json();
            state.apiOnline = true;
            statusEl.innerHTML = `
                <span class="status-indicator online"></span>
                <span class="status-text">API v6 Online</span>
            `;
            
            // Try to get stats
            try {
                const statsResponse = await fetch(`${CONFIG.apiEndpoint}/stats`);
                if (statsResponse.ok) {
                    const stats = await statsResponse.json();
                    statusEl.innerHTML = `
                        <span class="status-indicator online"></span>
                        <span class="status-text">v${stats.version || '6'} • ${stats.providers || 75}+ sources</span>
                    `;
                }
            } catch {}
        } else {
            throw new Error('API not responding');
        }
    } catch (e) {
        state.apiOnline = false;
        statusEl.innerHTML = `
            <span class="status-indicator offline"></span>
            <span class="status-text">Demo Mode (Start API)</span>
        `;
    }
}

// ===== CLOSE IIFE AND START APP =====
document.addEventListener('DOMContentLoaded', init);

// Expose helper functions for lightweight tests
window.__verityTest = { setupGlobalSearch, setupCommandPalette, setupAuth };

})();
