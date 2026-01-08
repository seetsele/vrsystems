/**
 * Verity Browser Extension - Background Service Worker
 * Handles context menus, API calls, and message routing
 * Updated for API v3 with WebSocket support
 */

const API_BASE_URL = 'https://api.verity-systems.com';
const DEV_API_URL = 'http://localhost:8000';
const WS_BASE_URL = 'wss://api.verity-systems.com';
const DEV_WS_URL = 'ws://localhost:8000';

// Configuration
let config = {
  apiUrl: API_BASE_URL,
  wsUrl: WS_BASE_URL,
  apiKey: '',
  apiVersion: 'v3',  // Use latest API version
  autoVerify: false,
  showNotifications: true,
  streamResults: true,  // Use WebSocket streaming
  language: 'en'
};

// WebSocket connection
let ws = null;
let wsReconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// Load config from storage
chrome.storage.sync.get(['config'], (result) => {
  if (result.config) {
    config = { ...config, ...result.config };
  }
});

// Create context menu on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'verity-check',
    title: 'Verify with Verity',
    contexts: ['selection']
  });
  
  chrome.contextMenus.create({
    id: 'verity-check-link',
    title: 'Verify Link with Verity',
    contexts: ['link']
  });
  
  console.log('Verity extension installed');
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'verity-check' && info.selectionText) {
    await verifyText(info.selectionText, tab.id);
  } else if (info.menuItemId === 'verity-check-link' && info.linkUrl) {
    await verifyUrl(info.linkUrl, tab.id);
  }
});

// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'verify') {
    verifyText(request.text, sender.tab?.id)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Keep channel open for async response
  }
  
  if (request.action === 'verifyUrl') {
    verifyUrl(request.url, sender.tab?.id)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ error: error.message }));
    return true;
  }
  
  if (request.action === 'getConfig') {
    sendResponse(config);
    return false;
  }
  
  if (request.action === 'updateConfig') {
    config = { ...config, ...request.config };
    chrome.storage.sync.set({ config });
    sendResponse({ success: true });
    return false;
  }
});

/**
 * Verify text claim via API
 */
async function verifyText(text, tabId) {
  try {
    // Notify content script that verification started
    if (tabId) {
      chrome.tabs.sendMessage(tabId, {
        action: 'verificationStarted',
        text: text
      });
    }
    
    const response = await fetch(`${config.apiUrl}/api/v1/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey && { 'Authorization': `ApiKey ${config.apiKey}` })
      },
      body: JSON.stringify({
        claim: text,
        options: {
          include_sources: true,
          include_evidence: true,
          regional_factchecks: true,  // v3 feature
          language: config.language
        }
      })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Transform if using older API format
    const normalizedResult = normalizeResult(result);
    
    // Send result to content script
    if (tabId) {
      chrome.tabs.sendMessage(tabId, {
        action: 'verificationComplete',
        result: normalizedResult
      });
    }
    
    // Show notification if enabled
    if (config.showNotifications) {
      showNotification(normalizedResult);
    }
    
    // Track analytics
    trackVerification(normalizedResult);
    
    return normalizedResult;
    
  } catch (error) {
    console.error('Verification error:', error);
    
    if (tabId) {
      chrome.tabs.sendMessage(tabId, {
        action: 'verificationError',
        error: error.message
      });
    }
    
    throw error;
  }
}

/**
 * Verify URL content
 */
async function verifyUrl(url, tabId) {
  try {
    const response = await fetch(`${config.apiUrl}/api/v1/verify/url`, {
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
    
    const result = await response.json();
    
    if (tabId) {
      chrome.tabs.sendMessage(tabId, {
        action: 'verificationComplete',
        result: result
      });
    }
    
    return result;
    
  } catch (error) {
    console.error('URL verification error:', error);
    throw error;
  }
}

/**
 * Show browser notification
 */
function showNotification(result) {
  const verdict = result.verdict || 'unknown';
  const confidence = result.confidence || 0;
  
  let icon = 'icons/icon48.png';
  let title = 'Verity Fact Check';
  
  const verdictText = {
    'true': '✓ TRUE',
    'mostly_true': '✓ MOSTLY TRUE',
    'mixed': '⚠ MIXED',
    'mostly_false': '✗ MOSTLY FALSE',
    'false': '✗ FALSE',
    'unverifiable': '? UNVERIFIABLE'
  };
  
  chrome.notifications.create({
    type: 'basic',
    iconUrl: icon,
    title: title,
    message: `${verdictText[verdict] || verdict.toUpperCase()} (${confidence}% confidence)`
  });
}

/**
 * Normalize result across API versions
 */
function normalizeResult(result) {
  // Handle v1 accuracy -> confidence conversion
  if (result.accuracy !== undefined && result.confidence === undefined) {
    result.confidence = result.accuracy;
    delete result.accuracy;
  }
  
  // Handle v2 sources -> evidence conversion
  if (result.sources && !result.evidence) {
    result.evidence = result.sources;
  }
  
  return result;
}

/**
 * Track verification analytics
 */
async function trackVerification(result) {
  try {
    const stats = await chrome.storage.local.get(['verificationStats']);
    const current = stats.verificationStats || {
      total: 0,
      byVerdict: {},
      avgConfidence: 0
    };
    
    current.total += 1;
    current.byVerdict[result.verdict] = (current.byVerdict[result.verdict] || 0) + 1;
    current.avgConfidence = ((current.avgConfidence * (current.total - 1)) + result.confidence) / current.total;
    current.lastVerification = new Date().toISOString();
    
    await chrome.storage.local.set({ verificationStats: current });
  } catch (e) {
    console.error('Failed to track stats:', e);
  }
}

/**
 * Connect to WebSocket for real-time updates
 */
function connectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) return;
  
  try {
    const wsUrl = config.apiUrl.includes('localhost') ? DEV_WS_URL : WS_BASE_URL;
    ws = new WebSocket(`${wsUrl}/ws`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      wsReconnectAttempts = 0;
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      } catch (e) {
        console.error('WS message parse error:', e);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      if (wsReconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        wsReconnectAttempts++;
        setTimeout(connectWebSocket, 1000 * wsReconnectAttempts);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  } catch (e) {
    console.error('Failed to connect WebSocket:', e);
  }
}

/**
 * Handle WebSocket messages
 */
function handleWebSocketMessage(data) {
  switch (data.type) {
    case 'verification_progress':
      // Broadcast to all tabs
      chrome.tabs.query({}, (tabs) => {
        tabs.forEach(tab => {
          chrome.tabs.sendMessage(tab.id, {
            action: 'verificationProgress',
            progress: data.progress,
            stage: data.stage
          }).catch(() => {});
        });
      });
      break;
      
    case 'trending_misinformation':
      if (config.showNotifications) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon48.png',
          title: '⚠️ Trending Misinformation Alert',
          message: data.claim.substring(0, 100)
        });
      }
      break;
  }
}

// Initialize WebSocket on startup if streaming enabled
if (config.streamResults) {
  connectWebSocket();
}
