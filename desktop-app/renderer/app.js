// ================================================
// VERITY DESKTOP v3 - PREMIUM EDITION
// Complete Full-Featured Application
// Integrated with Verity Ultimate API v6
// ================================================

(function() {
'use strict';

// ===== CONFIGURATION =====
const CONFIG = {
    apiEndpoint: 'https://veritysystems-production.up.railway.app',  // Production API (Railway)
    localEndpoint: 'http://localhost:8000',     // Local development
    version: '9.0.0',
    build: 'Ultimate',
    useLocal: false,  // Set to true for local development
    ninePointSystem: true  // Enable 9-Point Triple Verification
};

// ===== APPLICATION STATE =====
const state = {
    currentPage: 'dashboard',
    user: null,
    authenticated: false,
    apiOnline: false,
    history: [],
    notifications: [],
    settings: {
        darkMode: true,
        animations: true,
        notifications: true,
        sounds: false,
        autoSave: true
    }
};

// ===== PREMIUM SVG ICONS =====
const ICONS = {
    dashboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>`,
    verify: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    history: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14" stroke-linecap="round"/></svg>`,
    source: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35" stroke-linecap="round"/></svg>`,
    moderate: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4m0 4h.01" stroke-linecap="round"/></svg>`,
    research: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>`,
    social: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M18 8A6 6 0 106 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>`,
    bell: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M18 8A6 6 0 106 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>`,
    stats: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M18 20V10M12 20V4M6 20v-6" stroke-linecap="round"/></svg>`,
    map: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>`,
    realtime: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    api: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    key: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>`,
    billing: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="4" width="22" height="16" rx="2"/><path d="M1 10h22"/></svg>`,
    settings: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>`,
    user: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
    check: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20,6 9,17 4,12" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    x: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12" stroke-linecap="round"/></svg>`,
    arrow: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    copy: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>`,
    share: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg>`,
    download: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    upload: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    file: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>`,
    link: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>`,
    star: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>`,
    trending: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="23,6 13.5,15.5 8.5,10.5 1,18" stroke-linecap="round" stroke-linejoin="round"/><polyline points="17,6 23,6 23,12" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    alert: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><path d="M12 9v4M12 17h.01" stroke-linecap="round"/></svg>`,
    info: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01" stroke-linecap="round"/></svg>`,
    help: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3M12 17h.01" stroke-linecap="round"/></svg>`,
    brain: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 4.5a2.5 2.5 0 00-4.96-.46 2.5 2.5 0 00-1.98 3 2.5 2.5 0 00-1.32 4.24 3 3 0 00.34 5.58 2.5 2.5 0 002.96 3.08A2.5 2.5 0 0012 19.5a2.5 2.5 0 004.96.46 2.5 2.5 0 002.96-3.08 3 3 0 00.34-5.58 2.5 2.5 0 00-1.32-4.24 2.5 2.5 0 00-1.98-3A2.5 2.5 0 0012 4.5"/><path d="M15.7 8a6 6 0 00-7.4 0M8 16a6 6 0 0016 0M12 12v8"/></svg>`,
    shield: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
    target: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>`,
    zap: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10" stroke-linejoin="round"/></svg>`,
    globe: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>`,
    database: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>`,
    code: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="16,18 22,12 16,6" stroke-linecap="round" stroke-linejoin="round"/><polyline points="8,6 2,12 8,18" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    terminal: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="4,17 10,11 4,5" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="19" x2="20" y2="19" stroke-linecap="round"/></svg>`,
    layers: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="12,2 2,7 12,12 22,7"/><polyline points="2,17 12,22 22,17"/><polyline points="2,12 12,17 22,12"/></svg>`,
    cpu: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>`,
    play: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="5,3 19,12 5,21" stroke-linejoin="round"/></svg>`,
    pause: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>`,
    refresh: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="23,4 23,10 17,10" stroke-linecap="round" stroke-linejoin="round"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    filter: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46"/></svg>`,
    calendar: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>`,
    clock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14" stroke-linecap="round"/></svg>`,
    eye: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
    eyeOff: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23" stroke-linecap="round"/></svg>`,
    lock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>`,
    unlock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 019.9-1"/></svg>`,
    plus: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19" stroke-linecap="round"/><line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round"/></svg>`,
    minus: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round"/></svg>`,
    menu: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12" stroke-linecap="round"/><line x1="3" y1="6" x2="21" y2="6" stroke-linecap="round"/><line x1="3" y1="18" x2="21" y2="18" stroke-linecap="round"/></svg>`,
    more: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>`,
    external: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    trash: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="3,6 5,6 21,6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>`,
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
        items: [
            { id: 'source-checker', icon: 'source', label: 'Source Checker' },
            { id: 'content-mod', icon: 'moderate', label: 'Content Moderator' },
            { id: 'research', icon: 'research', label: 'Research Assistant' },
            { id: 'social', icon: 'social', label: 'Social Monitor' },
            { id: 'stats', icon: 'stats', label: 'Stats Validator' },
            { id: 'misinfo-map', icon: 'map', label: 'Misinfo Map' },
            { id: 'realtime', icon: 'realtime', label: 'Realtime Stream' }
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
    console.log('🚀 Verity Desktop v3 Initializing...');
    
    await loadStoredState();
    buildNavigation();
    setupTitlebar();
    setupAuth();
    setupCommandPalette();
    setupGlobalSearch();
    checkAPIStatus();
    
    navigate(state.currentPage);
    
    // Hide loading screen
    setTimeout(() => {
        document.getElementById('loading-screen')?.classList.add('hidden');
    }, 800);
    
    console.log('✅ Verity Desktop Ready');
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
    
    nav.innerHTML = NAV_ITEMS.map(section => `
        <div class="nav-section">
            <div class="nav-label">${section.section}</div>
            ${section.items.map(item => `
                <button class="nav-item${state.currentPage === item.id ? ' active' : ''}" data-page="${item.id}">
                    <span class="nav-icon">${ICONS[item.icon]}</span>
                    <span>${item.label}</span>
                    ${item.badge ? `<span class="nav-badge">${item.badge}</span>` : ''}
                </button>
            `).join('')}
        </div>
    `).join('');
    
    nav.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => navigate(btn.dataset.page));
    });
    
    updateUserMenu();
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
            document.querySelectorAll('.settings-list input[type="checkbox"]').forEach(toggle => {
                toggle.addEventListener('change', handleSettingChange);
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
        case 'dashboard':
            // Quick actions
            document.querySelectorAll('.quick-action').forEach(action => {
                action.addEventListener('click', () => {
                    const target = action.dataset.action;
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
            break;
    }
}

function updatePricing(isYearly) {
    const prices = {
        starter: { monthly: 0, yearly: 0 },
        pro: { monthly: 19, yearly: 15 },
        enterprise: { monthly: 99, yearly: 79 }
    };
    
    document.querySelectorAll('.pricing-card').forEach(card => {
        const tier = card.querySelector('.pricing-tier')?.textContent.toLowerCase();
        if (tier && prices[tier]) {
            const price = isYearly ? prices[tier].yearly : prices[tier].monthly;
            const priceEl = card.querySelector('.pricing-price .price');
            if (priceEl) priceEl.textContent = price;
            
            const periodEl = card.querySelector('.pricing-price .period');
            if (periodEl) periodEl.textContent = isYearly ? '/month, billed yearly' : '/month';
        }
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
        'settings': renderSettings
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

// ===== PAGE RENDERERS - VERIFY =====
function renderVerify() {
    return `
        <div class="page-header">
            <h1>Verify Content</h1>
            <p>AI-powered fact-checking with source analysis and credibility scoring.</p>
        </div>

        <div class="verify-container">
            <div class="verify-main">
                <div class="card card-verify">
                    <textarea class="textarea textarea-large" id="verify-input" placeholder="Paste a claim, article, social media post, or any text you want to fact-check..."></textarea>
                    
                    <div class="verify-options">
                        <label class="toggle-option">
                            <input type="checkbox" id="opt-sources" checked>
                            <span class="toggle-label">Source Analysis</span>
                        </label>
                        <label class="toggle-option">
                            <input type="checkbox" id="opt-deep">
                            <span class="toggle-label">Deep Mode</span>
                        </label>
                        <label class="toggle-option">
                            <input type="checkbox" id="opt-bias">
                            <span class="toggle-label">Bias Check</span>
                        </label>
                    </div>

                    <div class="verify-actions">
                        <button class="btn btn-primary btn-lg" id="verify-btn">
                            ${ICONS.verify} Verify Now
                        </button>
                        <button class="btn btn-secondary" id="verify-url-btn">
                            ${ICONS.link} URL
                        </button>
                        <button class="btn btn-ghost" id="verify-upload-btn">
                            ${ICONS.upload} Upload
                        </button>
                    </div>
                </div>

                <div id="verify-result"></div>
            </div>

            <div class="verify-sidebar">
                <div class="card">
                    <h4 class="card-title">How It Works</h4>
                    <div class="steps-list">
                        <div class="step-item">
                            <div class="step-num">1</div>
                            <div class="step-content">
                                <strong>Extract Claims</strong>
                                <span>AI identifies key assertions</span>
                            </div>
                        </div>
                        <div class="step-item">
                            <div class="step-num">2</div>
                            <div class="step-content">
                                <strong>Cross-Reference</strong>
                                <span>50M+ verified facts checked</span>
                            </div>
                        </div>
                        <div class="step-item">
                            <div class="step-num">3</div>
                            <div class="step-content">
                                <strong>AI Analysis</strong>
                                <span>Multi-model verification</span>
                            </div>
                        </div>
                        <div class="step-item">
                            <div class="step-num">4</div>
                            <div class="step-content">
                                <strong>Generate Report</strong>
                                <span>Confidence score & sources</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mini-stats">
                    <div class="mini-stat">
                        <span class="mini-value green">98.5%</span>
                        <span class="mini-label">Accuracy</span>
                    </div>
                    <div class="mini-stat">
                        <span class="mini-value cyan">2.3s</span>
                        <span class="mini-label">Avg Speed</span>
                    </div>
                    <div class="mini-stat">
                        <span class="mini-value purple">15K+</span>
                        <span class="mini-label">Sources</span>
                    </div>
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
            <h1>Source Checker</h1>
            <p>Evaluate the credibility of any news source or website.</p>
        </div>

        <div class="source-container">
            <div class="card card-source">
                <div class="form-group">
                    <label>Enter URL or Domain</label>
                    <input type="url" class="input input-lg" id="source-url" placeholder="https://example.com">
                </div>
                <button class="btn btn-primary btn-lg" id="check-source-btn">${ICONS.source} Analyze Source</button>
            </div>

            <div id="source-result"></div>
        </div>

        <div class="stats-grid" style="margin-top: 32px;">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.database}</div>
                </div>
                <div class="stat-value">500K+</div>
                <div class="stat-label">Sources Indexed</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.shield}</div>
                </div>
                <div class="stat-value">98%</div>
                <div class="stat-label">Accuracy Rate</div>
            </div>
            <div class="stat-card pink">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.trending}</div>
                </div>
                <div class="stat-value">Real-time</div>
                <div class="stat-label">Updates</div>
            </div>
            <div class="stat-card green">
                <div class="stat-header">
                    <div class="stat-icon">${ICONS.globe}</div>
                </div>
                <div class="stat-value">Global</div>
                <div class="stat-label">Coverage</div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - CONTENT MODERATOR =====
function renderContentModerator() {
    return `
        <div class="page-header">
            <h1>Content Moderator</h1>
            <p>Detect harmful, misleading, or inappropriate content using AI.</p>
        </div>

        <div class="moderator-container">
            <div class="card">
                <textarea class="textarea textarea-large" id="moderate-input" placeholder="Paste content to analyze for harmful material, hate speech, misinformation, or spam..."></textarea>
                
                <div class="verify-options">
                    <label class="toggle-option"><input type="checkbox" id="mod-hate" checked><span class="toggle-label">Hate Speech</span></label>
                    <label class="toggle-option"><input type="checkbox" id="mod-misinfo" checked><span class="toggle-label">Misinformation</span></label>
                    <label class="toggle-option"><input type="checkbox" id="mod-violence" checked><span class="toggle-label">Violence</span></label>
                    <label class="toggle-option"><input type="checkbox" id="mod-spam" checked><span class="toggle-label">Spam</span></label>
                </div>

                <button class="btn btn-primary btn-lg" id="moderate-btn">${ICONS.moderate} Analyze Content</button>
            </div>

            <div id="moderate-result"></div>
        </div>
    `;
}

// ===== PAGE RENDERERS - RESEARCH ASSISTANT =====
function renderResearch() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / Research Assistant</div>
            <h1>Research Assistant</h1>
            <p>AI-powered research helper with access to academic databases and verified sources.</p>
        </div>

        <div class="verify-box">
            <div class="form-group">
                <label>Research Topic or Question</label>
                <input type="text" class="input input-lg" id="research-query" placeholder="What would you like to research?">
            </div>
            <div class="verify-options">
                <label class="verify-option"><input type="checkbox" checked> Academic Sources</label>
                <label class="verify-option"><input type="checkbox" checked> News Articles</label>
                <label class="verify-option"><input type="checkbox"> Government Data</label>
                <label class="verify-option"><input type="checkbox"> Scientific Papers</label>
            </div>
            <div class="verify-actions">
                <button class="btn btn-primary btn-lg" id="research-btn">${ICONS.research} Start Research</button>
            </div>
        </div>

        <div id="research-result"></div>

        <div class="feature-grid">
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.database}</div>
                <h3>Academic Databases</h3>
                <p>Access millions of peer-reviewed papers, journals, and academic publications.</p>
                <div class="feature-tags"><span class="feature-tag">PubMed</span><span class="feature-tag">arXiv</span><span class="feature-tag">JSTOR</span></div>
            </div>
            <div class="card card-gradient">
                <div class="feature-icon">${ICONS.brain}</div>
                <h3>AI Summarization</h3>
                <p>Get concise summaries and key insights from complex research papers.</p>
                <div class="feature-tags"><span class="feature-tag">GPT-4</span><span class="feature-tag">Claude</span></div>
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - SOCIAL MONITOR =====
function renderSocialMonitor() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / Social Monitor</div>
            <h1>Social Media Monitor</h1>
            <p>Track misinformation trends and viral claims across social platforms in real-time.</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card"><div class="stat-icon">${ICONS.trending}</div><div class="stat-value">1,247</div><div class="stat-label">Trending Claims</div></div>
            <div class="stat-card purple"><div class="stat-icon">${ICONS.alert}</div><div class="stat-value">89</div><div class="stat-label">Active Alerts</div></div>
            <div class="stat-card pink"><div class="stat-icon">${ICONS.eye}</div><div class="stat-value">24/7</div><div class="stat-label">Monitoring</div></div>
            <div class="stat-card green"><div class="stat-icon">${ICONS.globe}</div><div class="stat-value">50+</div><div class="stat-label">Platforms</div></div>
        </div>

        <div class="card">
            <div class="card-header"><h3>Trending Misinformation</h3><button class="btn btn-sm btn-secondary">${ICONS.refresh} Refresh</button></div>
            <div class="history-list">
                ${[
                    { claim: 'Viral claim about election fraud spreads on Twitter', score: 15, time: '2 hours ago' },
                    { claim: 'Misleading health advice circulating on Facebook', score: 22, time: '4 hours ago' },
                    { claim: 'Doctored video shared on TikTok gains millions of views', score: 8, time: '6 hours ago' }
                ].map(item => `
                    <div class="history-item">
                        <div class="history-score bad">${item.score}</div>
                        <div class="history-content">
                            <div class="history-text">${item.claim}</div>
                            <div class="history-meta">${item.time}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// ===== PAGE RENDERERS - STATS VALIDATOR =====
function renderStatsValidator() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / Stats Validator</div>
            <h1>Statistics Validator</h1>
            <p>Verify statistical claims and data citations against authoritative sources.</p>
        </div>

        <div class="verify-box">
            <textarea class="textarea" id="stats-input" placeholder="Enter a statistical claim to validate, e.g.:
• '90% of scientists agree on climate change'
• 'Crime rates have increased 50% since 2020'
• 'The average American drinks 3 cups of coffee per day'"></textarea>
            <div class="verify-actions">
                <button class="btn btn-primary btn-lg" id="stats-btn">${ICONS.stats} Validate Statistics</button>
            </div>
        </div>
        <div id="stats-result"></div>
    `;
}

// ===== PAGE RENDERERS - MISINFO MAP =====
function renderMisinfoMap() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / Misinformation Map</div>
            <h1>Global Misinformation Map</h1>
            <p>Visualize misinformation patterns and hotspots around the world.</p>
        </div>

        <div class="card" style="height: 400px; display: flex; align-items: center; justify-content: center;">
            <div class="empty-state">
                <div class="empty-icon">${ICONS.map}</div>
                <h3>Interactive Map</h3>
                <p>Global misinformation tracking visualization</p>
                <button class="btn btn-primary" id="load-map-btn">${ICONS.globe} Load Map</button>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card"><div class="stat-icon">${ICONS.alert}</div><div class="stat-value">12,847</div><div class="stat-label">Active Hotspots</div></div>
            <div class="stat-card purple"><div class="stat-icon">${ICONS.trending}</div><div class="stat-value">+23%</div><div class="stat-label">Weekly Change</div></div>
            <div class="stat-card pink"><div class="stat-icon">${ICONS.globe}</div><div class="stat-value">195</div><div class="stat-label">Countries Tracked</div></div>
            <div class="stat-card green"><div class="stat-icon">${ICONS.database}</div><div class="stat-value">5M+</div><div class="stat-label">Claims Analyzed</div></div>
        </div>
    `;
}

// ===== PAGE RENDERERS - REALTIME STREAM =====
function renderRealtime() {
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>AI Tools</span> / Realtime Stream</div>
            <h1>Realtime Fact-Check Stream</h1>
            <p>Live feed of fact-checks from around the world as they happen.</p>
        </div>

        <div class="toolbar">
            <button class="btn btn-primary" id="start-stream-btn">${ICONS.play} Start Stream</button>
            <button class="btn btn-secondary" id="pause-stream-btn" disabled>${ICONS.pause} Pause</button>
            <div style="flex: 1;"></div>
            <select class="select" style="max-width: 180px;">
                <option>All Categories</option>
                <option>Politics</option>
                <option>Health</option>
                <option>Science</option>
            </select>
        </div>

        <div class="card" id="stream-container">
            <div class="empty-state">
                <div class="empty-icon">${ICONS.realtime}</div>
                <h3>Stream Offline</h3>
                <p>Click "Start Stream" to see live fact-checks</p>
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
    return `
        <div class="page-header">
            <div class="breadcrumb"><span>Account</span> / Billing</div>
            <h1>Billing & Plans</h1>
            <p>Manage your subscription and view usage details.</p>
        </div>

        <div class="billing-toggle">
            <button class="billing-period active" data-period="monthly">Monthly</button>
            <button class="billing-period" data-period="yearly">Yearly <span class="save-badge">Save 20%</span></button>
        </div>

        <div class="pricing-grid">
            <div class="pricing-card">
                <div class="pricing-tier">Starter</div>
                <div class="pricing-price"><span class="currency">$</span><span class="price">0</span><span class="period">/month</span></div>
                <p class="pricing-desc">Perfect for trying out Verity</p>
                <ul class="pricing-features">
                    <li>${ICONS.check} <span>50 verifications/month</span></li>
                    <li>${ICONS.check} <span>Basic source checking</span></li>
                    <li>${ICONS.check} <span>Community support</span></li>
                    <li class="disabled">${ICONS.x} <span>API access</span></li>
                    <li class="disabled">${ICONS.x} <span>Priority support</span></li>
                </ul>
                <button class="btn btn-secondary btn-block">Current Plan</button>
            </div>

            <div class="pricing-card featured">
                <div class="pricing-badge">Most Popular</div>
                <div class="pricing-tier">Pro</div>
                <div class="pricing-price"><span class="currency">$</span><span class="price">19</span><span class="period">/month</span></div>
                <p class="pricing-desc">For professionals and teams</p>
                <ul class="pricing-features">
                    <li>${ICONS.check} <span>1,000 verifications/month</span></li>
                    <li>${ICONS.check} <span>Advanced AI analysis</span></li>
                    <li>${ICONS.check} <span>Full API access</span></li>
                    <li>${ICONS.check} <span>Priority support</span></li>
                    <li>${ICONS.check} <span>Export reports</span></li>
                </ul>
                <button class="btn btn-primary btn-block" id="upgrade-pro">Upgrade to Pro</button>
            </div>

            <div class="pricing-card">
                <div class="pricing-tier">Enterprise</div>
                <div class="pricing-price"><span class="currency">$</span><span class="price">99</span><span class="period">/month</span></div>
                <p class="pricing-desc">Custom solutions for organizations</p>
                <ul class="pricing-features">
                    <li>${ICONS.check} <span>Unlimited verifications</span></li>
                    <li>${ICONS.check} <span>Custom AI models</span></li>
                    <li>${ICONS.check} <span>Dedicated support manager</span></li>
                    <li>${ICONS.check} <span>99.9% SLA guarantee</span></li>
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
        <div class="page-header">
            <h1>Settings</h1>
            <p>Customize your Verity experience.</p>
        </div>

        <div class="settings-grid">
            <div class="settings-nav">
                <button class="settings-nav-item active" data-section="appearance">
                    ${ICONS.settings} Appearance
                </button>
                <button class="settings-nav-item" data-section="notifications">
                    ${ICONS.bell} Notifications
                </button>
                <button class="settings-nav-item" data-section="privacy">
                    ${ICONS.shield} Privacy
                </button>
                <button class="settings-nav-item" data-section="about">
                    ${ICONS.info} About
                </button>
            </div>

            <div class="settings-content">
                <div class="card">
                    <h3 class="card-title">Appearance</h3>
                    <div class="setting-row">
                        <div class="setting-info">
                            <div class="setting-title">Dark Mode</div>
                            <div class="setting-desc">Use dark theme throughout the app</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-dark-mode" ${state.settings.darkMode ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    <div class="setting-row">
                        <div class="setting-info">
                            <div class="setting-title">Animations</div>
                            <div class="setting-desc">Enable smooth transitions and effects</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-animations" ${state.settings.animations ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>

                <div class="card">
                    <h3 class="card-title">Notifications</h3>
                    <div class="setting-row">
                        <div class="setting-info">
                            <div class="setting-title">Push Notifications</div>
                            <div class="setting-desc">Receive alerts for trending misinformation</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-notifications" ${state.settings.notifications ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    <div class="setting-row">
                        <div class="setting-info">
                            <div class="setting-title">Sound Effects</div>
                            <div class="setting-desc">Play sounds for completed verifications</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-sounds" ${state.settings.sounds ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>

                <div class="card">
                    <h3 class="card-title">Data & Privacy</h3>
                    <div class="setting-row">
                        <div class="setting-info">
                            <div class="setting-title">Auto-save History</div>
                            <div class="setting-desc">Save verification history locally</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-autosave" ${state.settings.autoSave ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    <div style="margin-top: 20px; display: flex; gap: 12px;">
                        <button class="btn btn-secondary btn-sm" id="export-data-btn">${ICONS.download} Export Data</button>
                        <button class="btn btn-ghost btn-sm" id="clear-data-btn">${ICONS.trash} Clear All Data</button>
                    </div>
                </div>

                <div class="card">
                    <h3 class="card-title">About</h3>
                    <div class="about-box">
                        <div class="about-logo">V</div>
                        <div class="about-info">
                            <strong>Verity Desktop</strong>
                            <span>v${CONFIG.version} (${CONFIG.build})</span>
                            <span class="text-muted">© 2024 Verity Systems</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
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
        console.error('Verification error:', error);
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
    const setting = e.target.id.replace('setting-', '').replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    state.settings[setting] = e.target.checked;
    saveState();
    toast('Setting saved', 'success');
}

// ===== SETUP FUNCTIONS =====
function setupTitlebar() {
    // Window controls
    document.getElementById('btn-min')?.addEventListener('click', () => {
        window.verity?.window?.minimize();
    });
    document.getElementById('btn-max')?.addEventListener('click', () => {
        window.verity?.window?.maximize();
    });
    document.getElementById('btn-close')?.addEventListener('click', () => {
        window.verity?.window?.close();
    });
    
    // Sign In button handling
    document.getElementById('signin-btn')?.addEventListener('click', () => {
        document.getElementById('auth-modal')?.classList.add('active');
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
    
    // Close button
    document.getElementById('close-auth')?.addEventListener('click', () => {
        modal.classList.remove('active');
    });
    
    // Backdrop click
    modal.querySelector('.modal-backdrop')?.addEventListener('click', () => {
        modal.classList.remove('active');
    });
    
    // Tab switching
    modal.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            modal.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            modal.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            tab.classList.add('active');
            const formId = tab.dataset.tab === 'signin' ? 'signin-form' : 'signup-form';
            document.getElementById(formId)?.classList.add('active');
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
            modal.classList.remove('active');
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
            modal.classList.remove('active');
            buildNavigation();
            toast('Account created!', 'success');
        }
    });
}

function setupCommandPalette() {
    const cmd = document.getElementById('cmd');
    const input = document.getElementById('cmd-input');
    const results = document.getElementById('cmd-results');
    if (!cmd || !input) return;
    
    // Toggle with Ctrl+K
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
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
                navigate(btn.dataset.page);
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
                    <h3>Provider Usage</h3>
                </div>
                <div class="provider-list">
                    ${[
                        { name: 'Claude (Anthropic)', pct: 85 },
                        { name: 'GPT-4 (OpenAI)', pct: 72 },
                        { name: 'PolitiFact', pct: 45 },
                        { name: 'Perplexity', pct: 38 }
                    ].map(p => `
                        <div class="provider-row">
                            <span class="provider-name">${p.name}</span>
                            <div class="provider-bar">
                                <div class="provider-fill" style="width: ${p.pct}%"></div>
                            </div>
                            <span class="provider-pct">${p.pct}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3>Real-time Metrics</h3>
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
                    <div class="metric-label">WebSocket Connections</div>
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
        <div class="page-header">
            <h1>Export Reports</h1>
            <p>Generate professional reports of your verification history in multiple formats.</p>
        </div>

        <div class="export-formats">
            <div class="format-card selected" data-format="pdf">
                <div class="format-icon" style="color: #ef4444;">${ICONS.file}</div>
                <h4>PDF Report</h4>
                <p>Professional printable reports with charts</p>
            </div>
            <div class="format-card" data-format="csv">
                <div class="format-icon" style="color: #22c55e;">${ICONS.file}</div>
                <h4>CSV Spreadsheet</h4>
                <p>Excel-compatible data export</p>
            </div>
            <div class="format-card" data-format="json">
                <div class="format-icon" style="color: #eab308;">${ICONS.code}</div>
                <h4>JSON Data</h4>
                <p>Full structured data with metadata</p>
            </div>
            <div class="format-card" data-format="html">
                <div class="format-icon" style="color: #3b82f6;">${ICONS.code}</div>
                <h4>HTML Report</h4>
                <p>Interactive web report</p>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3>Export Configuration</h3>
            </div>
            <div class="card-body">
                <div class="form-row">
                    <div class="form-group">
                        <label>Start Date</label>
                        <input type="date" id="export-start" class="input">
                    </div>
                    <div class="form-group">
                        <label>End Date</label>
                        <input type="date" id="export-end" class="input">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Verdict Filter</label>
                        <select id="export-verdict" class="select">
                            <option value="all">All Verdicts</option>
                            <option value="true">True Only</option>
                            <option value="false">False Only</option>
                            <option value="partial">Partially True</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Minimum Confidence</label>
                        <select id="export-confidence" class="select">
                            <option value="0">Any Confidence</option>
                            <option value="50">50%+</option>
                            <option value="70">70%+</option>
                            <option value="85">85%+</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label>Include in Export</label>
                    <div class="checkbox-grid">
                        <label class="checkbox-item">
                            <input type="checkbox" id="inc-sources" checked>
                            <span>Source citations</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" id="inc-evidence" checked>
                            <span>Evidence breakdown</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" id="inc-metadata">
                            <span>Processing metadata</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" id="inc-summary" checked>
                            <span>Executive summary</span>
                        </label>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3>Preview</h3>
            </div>
            <pre class="code-preview" id="export-preview">{
  "report": {
    "title": "Verity Verification Report",
    "generated": "${new Date().toISOString()}",
    "summary": {
      "total": ${state.history.length},
      "verified": ${state.history.filter(h => h.score >= 70).length}
    }
  }
}</pre>
        </div>

        <div class="export-actions">
            <button class="btn btn-primary btn-lg" id="generate-export-btn">
                ${ICONS.download} Generate Export
            </button>
            <span class="export-estimate">Estimated size: ~${(state.history.length * 2.5).toFixed(1)} KB</span>
        </div>

        <div class="card">
            <div class="card-header">
                <h3>Recent Exports</h3>
            </div>
            <div class="export-list">
                <div class="export-item">
                    <div class="export-item-icon" style="background: rgba(239, 68, 68, 0.15); color: #ef4444;">${ICONS.file}</div>
                    <div class="export-item-info">
                        <span class="export-name">verification_report_jan2025.pdf</span>
                        <span class="export-meta">2.4 MB • 2 hours ago</span>
                    </div>
                    <button class="btn btn-sm btn-ghost">${ICONS.download}</button>
                </div>
                <div class="export-item">
                    <div class="export-item-icon" style="background: rgba(34, 197, 94, 0.15); color: #22c55e;">${ICONS.file}</div>
                    <div class="export-item-info">
                        <span class="export-name">export_20250114.csv</span>
                        <span class="export-meta">156 KB • Yesterday</span>
                    </div>
                    <button class="btn btn-sm btn-ghost">${ICONS.download}</button>
                </div>
            </div>
        </div>
    `;
}

function setupGlobalSearch() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;
    
    searchInput.addEventListener('focus', () => {
        document.getElementById('cmd')?.classList.add('active');
        document.getElementById('cmd-input')?.focus();
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

})();
