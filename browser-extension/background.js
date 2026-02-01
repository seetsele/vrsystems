/**
 * Verity Browser Extension - Background Service Worker
 * =====================================================
 * Handles API calls, context menus, message routing, and WebSocket connections
 * Compatible with Manifest V3
 */

// API Configuration - Try localhost first, fallback to production
const API_CONFIGS = {
  production: {
    apiUrl: 'https://veritysystems-production.up.railway.app',
    wsUrl: 'wss://veritysystems-production.up.railway.app'
  },
  development: {
    apiUrl: 'http://localhost:8000',
    wsUrl: 'ws://localhost:8000'
  }
};

// Default configuration
let config = {
  environment: 'development', // Changed: try localhost first
  apiKey: '',
  autoVerify: false,
  showNotifications: true,
  streamResults: true,
  language: 'en',
  cacheResults: true,
  cacheDuration: 3600000, // 1 hour
  tier: 'free', // User's subscription tier
  platform: 'browser_extension'
};

// Verification cache
const verificationCache = new Map();

// Load config from storage on startup
chrome.storage.sync.get(['verityConfig'], (result) => {
  if (result.verityConfig) {
    config = { ...config, ...result.verityConfig };
  }
});

// ============================================================
// CONTEXT MENUS
// ============================================================

chrome.runtime.onInstalled.addListener(() => {
  // Create context menu items
  chrome.contextMenus.create({
    id: 'verity-verify-selection',
    title: 'Verify with Verity',
    contexts: ['selection']
  });
  
  chrome.contextMenus.create({
    id: 'verity-verify-link',
    title: 'Check Source Credibility',
    contexts: ['link']
  });
  
  chrome.contextMenus.create({
    id: 'verity-verify-page',
    title: 'Analyze This Page',
    contexts: ['page']
  });
  
  console.log('Verity extension installed successfully');
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'verity-verify-selection' && info.selectionText) {
    const result = await verifyClaimAPI(info.selectionText);
    sendResultToTab(tab.id, result, info.selectionText);
  } else if (info.menuItemId === 'verity-verify-link' && info.linkUrl) {
    const result = await analyzeUrlAPI(info.linkUrl);
    sendResultToTab(tab.id, result, info.linkUrl);
  } else if (info.menuItemId === 'verity-verify-page') {
    const result = await analyzeUrlAPI(tab.url);
    sendResultToTab(tab.id, result, tab.url);
  }
});

// ============================================================
// KEYBOARD SHORTCUTS
// ============================================================

chrome.commands.onCommand.addListener(async (command) => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return;
  
  switch (command) {
    case 'verify_selection':
      try {
        const [{ result: selectedText }] = await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: () => window.getSelection()?.toString()
        });
        
        if (selectedText?.trim()) {
          const result = await verifyClaimAPI(selectedText.trim());
          sendResultToTab(tab.id, result, selectedText.trim());
        } else {
          showNotification('No Selection', 'Please select text to verify first.');
        }
      } catch (error) {
        console.error('Error getting selection:', error);
      }
      break;
      
    case 'toggle_overlay':
      chrome.tabs.sendMessage(tab.id, { type: 'TOGGLE_OVERLAY' });
      break;
      
    case 'scan_page':
      chrome.tabs.sendMessage(tab.id, { type: 'SCAN_PAGE' });
      break;
  }
});

// ============================================================
// MESSAGE HANDLING
// ============================================================

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // Log incoming messages for debugging
  console.log('Background received message:', request.type || request.action);
  
  // Handle different message types
  switch (request.type || request.action) {
    case 'VERIFY_CLAIM':
      verifyClaimAPI(request.claim)
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ error: error.message, verdict: 'error' }));
      return true; // Keep channel open for async
      
    case 'GET_PAGE_SCORE':
      analyzeUrlAPI(request.url)
        .then(result => sendResponse({ score: result }))
        .catch(error => sendResponse({ error: error.message }));
      return true;
      
    case 'ANALYZE_URL':
      analyzeUrlAPI(request.url)
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ error: error.message }));
      return true;
      
    case 'GET_CONFIG':
      sendResponse(config);
      return false;
      
    case 'UPDATE_CONFIG':
      config = { ...config, ...request.config };
      chrome.storage.sync.set({ verityConfig: config });
      sendResponse({ success: true });
      return false;
      
    case 'CLEAR_CACHE':
      verificationCache.clear();
      sendResponse({ success: true });
      return false;
      
    case 'GET_STATS':
      chrome.storage.sync.get(['verityStats'], (result) => {
        sendResponse(result.verityStats || { verified: 0, accuracy: 0, streak: 0 });
      });
      return true;
      
    case 'UPDATE_STATS':
      updateStats(request.verdict);
      sendResponse({ success: true });
      return false;
      
    default:
      console.warn('Unknown message type:', request.type || request.action);
      sendResponse({ error: 'Unknown message type' });
      return false;
  }
});

// ============================================================
// API FUNCTIONS
// ============================================================

async function verifyClaimAPI(claim) {
  // Check cache first
  const cacheKey = `claim:${claim.substring(0, 100)}`;
  if (config.cacheResults && verificationCache.has(cacheKey)) {
    const cached = verificationCache.get(cacheKey);
    if (Date.now() - cached.timestamp < config.cacheDuration) {
      console.log('Returning cached verification result');
      return cached.result;
    }
    verificationCache.delete(cacheKey);
  }
  
  const apiUrl = API_CONFIGS[config.environment]?.apiUrl || API_CONFIGS.production.apiUrl;
  
  try {
    // Use tiered verification endpoint for tier-aware verification
    const response = await fetch(`${apiUrl}/tiered-verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Platform': config.platform,
        'X-Tier': config.tier,
        ...(config.apiKey && { 'Authorization': `Bearer ${config.apiKey}` })
      },
      body: JSON.stringify({
        claim: claim,
        tier: config.tier,
        platform: config.platform,
        context: '',
        include_free_providers: true
      })
    });
    
    if (!response.ok) {
      // Fallback to legacy endpoint if tiered endpoint fails
      console.log('Tiered endpoint failed, falling back to legacy');
      return await verifyClaimLegacy(claim);
    }
    
    const data = await response.json();
    const result = normalizeVerificationResult(data);
    
    // Cache the result
    if (config.cacheResults) {
      verificationCache.set(cacheKey, { result, timestamp: Date.now() });
    }
    
    // Update stats
    updateStats(result.verdict);
    
    return result;
  } catch (error) {
    console.error('Tiered verification API error:', error);
    
    // Try legacy endpoint
    try {
      return await verifyClaimLegacy(claim);
    } catch (legacyError) {
      console.error('Legacy verification also failed:', legacyError);
      return generateDemoResult(claim);
    }
  }
}

// Legacy verification fallback
async function verifyClaimLegacy(claim) {
  const apiUrl = API_CONFIGS[config.environment]?.apiUrl || API_CONFIGS.production.apiUrl;
  
  const response = await fetch(`${apiUrl}/api/v1/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(config.apiKey && { 'Authorization': `ApiKey ${config.apiKey}` })
    },
    body: JSON.stringify({
      claim: claim,
      options: {
        include_sources: true,
        include_evidence: true,
        language: config.language
      }
    })
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  const data = await response.json();
  return normalizeVerificationResult(data);
}

async function analyzeUrlAPI(url) {
  const apiUrl = API_CONFIGS[config.environment]?.apiUrl || API_CONFIGS.production.apiUrl;
  
  try {
    const response = await fetch(`${apiUrl}/api/v1/analyze/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey && { 'Authorization': `ApiKey ${config.apiKey}` })
      },
      body: JSON.stringify({ url })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    return normalizeSourceResult(data);
  } catch (error) {
    console.error('URL analysis API error:', error);
    return generateDemoSourceResult(url);
  }
}

// ============================================================
// RESULT NORMALIZATION
// ============================================================

function normalizeVerificationResult(data) {
  // Handle different API response formats
  return {
    verdict: data.verdict || data.overall_verdict?.toLowerCase() || 'unverified',
    confidence: data.confidence ?? data.overall_confidence ?? 0.5,
    explanation: data.explanation || data.summary || 'Verification complete.',
    claim: data.claim || data.original_claim || '',
    sources: (data.sources || data.evidence || []).map(s => ({
      name: s.name || s.source || 'Unknown Source',
      url: s.url || s.link || '#',
      verdict: s.verdict || 'neutral',
      credibility: s.credibility || s.trust_score || 0.5
    })),
    category: data.category || 'general',
    timestamp: new Date().toISOString()
  };
}

function normalizeSourceResult(data) {
  return {
    score: Math.round((data.credibility_score || data.trust_score || 0.5) * 100),
    grade: calculateGrade(data.credibility_score || data.trust_score || 0.5),
    domain: data.domain || 'unknown',
    bias: data.bias || 'unknown',
    factCheckHistory: data.fact_check_history || [],
    ownership: data.ownership || 'Unknown',
    timestamp: new Date().toISOString()
  };
}

function calculateGrade(score) {
  if (score >= 0.9) return 'A';
  if (score >= 0.75) return 'B';
  if (score >= 0.6) return 'C';
  if (score >= 0.4) return 'D';
  return 'F';
}

// ============================================================
// DEMO MODE (when API unavailable)
// ============================================================

function generateDemoResult(claim) {
  // Generate a plausible demo result
  const verdicts = ['true', 'false', 'misleading', 'unverified'];
  const randomVerdict = verdicts[Math.floor(Math.random() * verdicts.length)];
  const confidence = 0.5 + Math.random() * 0.4;
  
  return {
    verdict: randomVerdict,
    confidence: confidence,
    explanation: `Demo mode: This claim would be verified against 75+ sources. Start the API server for full verification.`,
    claim: claim,
    sources: [
      { name: 'Demo Source 1', url: '#', verdict: 'neutral', credibility: 0.7 },
      { name: 'Demo Source 2', url: '#', verdict: 'neutral', credibility: 0.8 }
    ],
    category: 'general',
    timestamp: new Date().toISOString(),
    isDemo: true
  };
}

function generateDemoSourceResult(url) {
  const score = 0.5 + Math.random() * 0.4;
  return {
    score: Math.round(score * 100),
    grade: calculateGrade(score),
    domain: new URL(url).hostname,
    bias: 'unknown',
    factCheckHistory: [],
    ownership: 'Unknown',
    timestamp: new Date().toISOString(),
    isDemo: true
  };
}

// ============================================================
// UTILITIES
// ============================================================

function sendResultToTab(tabId, result, originalText) {
  chrome.tabs.sendMessage(tabId, {
    type: 'VERIFICATION_RESULT',
    result: result,
    originalText: originalText
  });
  
  // Show notification if enabled
  if (config.showNotifications) {
    const verdictLabels = {
      true: '✅ TRUE',
      false: '❌ FALSE',
      misleading: '⚠️ MISLEADING',
      unverified: '❓ UNVERIFIED'
    };
    
    showNotification(
      `Verity: ${verdictLabels[result.verdict] || 'Analyzed'}`,
      `${Math.round(result.confidence * 100)}% confidence - ${result.explanation?.substring(0, 100) || 'Analysis complete'}`
    );
  }
}

function showNotification(title, message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'chrome/icons/icon128.png',
    title: title,
    message: message
  });
}

async function updateStats(verdict) {
  const result = await chrome.storage.sync.get(['verityStats']);
  const stats = result.verityStats || { verified: 0, accuracy: 0, streak: 0, trueCount: 0 };
  
  stats.verified++;
  if (verdict === 'true') {
    stats.trueCount++;
    stats.streak++;
  } else if (verdict === 'false') {
    stats.streak = 0;
  }
  stats.accuracy = Math.round((stats.trueCount / stats.verified) * 100);
  
  await chrome.storage.sync.set({ verityStats: stats });
}

// ============================================================
// SERVICE WORKER KEEP-ALIVE (for long-running operations)
// ============================================================

// Ping every 25 seconds to keep service worker alive during operations
let keepAliveInterval = null;

function startKeepAlive() {
  if (!keepAliveInterval) {
    keepAliveInterval = setInterval(() => {
      console.log('Verity background: keeping alive');
    }, 25000);
  }
}

function stopKeepAlive() {
  if (keepAliveInterval) {
    clearInterval(keepAliveInterval);
    keepAliveInterval = null;
  }
}

// Clean up on extension suspend
chrome.runtime.onSuspend?.addListener(() => {
  stopKeepAlive();
  verificationCache.clear();
  console.log('Verity extension suspended');
});

console.log('Verity background service worker initialized');
