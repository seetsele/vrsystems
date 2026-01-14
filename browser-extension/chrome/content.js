/**
 * Verity Browser Extension - Content Script
 * Handles text selection, inline verification UI, and page interactions
 */

// State
let isVerifying = false;
let currentTooltip = null;
let inlineModeEnabled = true;
let darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

// Load preferences
chrome.storage.sync.get(['inlineMode', 'darkMode'], (result) => {
  inlineModeEnabled = result.inlineMode !== false;
  if (result.darkMode !== undefined) {
    darkMode = result.darkMode;
  }
  applyDarkMode();
});

// Apply dark mode to Verity elements
function applyDarkMode() {
  const style = document.getElementById('verity-dark-mode');
  if (darkMode && !style) {
    const darkStyles = document.createElement('style');
    darkStyles.id = 'verity-dark-mode';
    darkStyles.textContent = `
      .verity-tooltip.verity-dark {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border-color: #334155 !important;
      }
      .verity-tooltip.verity-dark .verity-tooltip-header {
        background: #0f172a !important;
        border-color: #334155 !important;
      }
      .verity-tooltip.verity-dark .verity-sources a {
        color: #818cf8 !important;
      }
    `;
    document.head.appendChild(darkStyles);
  } else if (!darkMode && style) {
    style.remove();
  }
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'verificationStarted':
      showLoadingIndicator(request.text);
      break;
    case 'verificationComplete':
      hideLoadingIndicator();
      showVerificationResult(request.result);
      break;
    case 'verificationError':
      hideLoadingIndicator();
      showError(request.error);
      break;
    case 'toggleInlineMode':
      inlineModeEnabled = !inlineModeEnabled;
      chrome.storage.sync.set({ inlineMode: inlineModeEnabled });
      showModeNotification(inlineModeEnabled);
      sendResponse({ inlineMode: inlineModeEnabled });
      break;
    case 'setDarkMode':
      darkMode = request.darkMode;
      applyDarkMode();
      sendResponse({ darkMode });
      break;
  }
});

// Show mode toggle notification
function showModeNotification(enabled) {
  const notification = document.createElement('div');
  notification.className = 'verity-mode-notification';
  notification.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M9 12l2 2 4-4"/>
      <circle cx="12" cy="12" r="10"/>
    </svg>
    <span>Inline verification ${enabled ? 'enabled' : 'disabled'}</span>
  `;
  notification.style.cssText = `
    position: fixed; bottom: 20px; right: 20px; padding: 12px 16px;
    background: ${enabled ? '#22c55e' : '#6b7280'}; color: white;
    border-radius: 8px; display: flex; align-items: center; gap: 8px;
    font-family: system-ui, sans-serif; font-size: 14px; z-index: 999999;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3); animation: verity-fade-in 0.3s ease;
  `;
  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 2000);
}

// Handle text selection
document.addEventListener('mouseup', (event) => {
  if (!inlineModeEnabled) return;
  
  const selection = window.getSelection();
  const selectedText = selection.toString().trim();
  
  // Only show button for meaningful selections
  if (selectedText.length > 20 && selectedText.length < 1000) {
    showVerifyButton(event, selectedText);
  }
});

// Hide tooltip when clicking elsewhere
document.addEventListener('mousedown', (event) => {
  if (!event.target.closest('.verity-tooltip') && !event.target.closest('.verity-verify-btn')) {
    removeAllVerityElements();
  }
});

/**
 * Show floating verify button near selection
 */
function showVerifyButton(event, text) {
  removeAllVerityElements();
  
  const button = document.createElement('button');
  button.className = 'verity-verify-btn';
  button.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M9 12l2 2 4-4"/>
      <circle cx="12" cy="12" r="10"/>
    </svg>
    Verify
  `;
  
  // Position near selection
  const selection = window.getSelection();
  const range = selection.getRangeAt(0);
  const rect = range.getBoundingClientRect();
  
  button.style.position = 'fixed';
  button.style.left = `${rect.left + rect.width / 2 - 40}px`;
  button.style.top = `${rect.bottom + 5}px`;
  button.style.zIndex = '999999';
  
  button.addEventListener('click', (e) => {
    e.stopPropagation();
    verifySelectedText(text);
  });
  
  document.body.appendChild(button);
}

/**
 * Verify selected text
 */
async function verifySelectedText(text) {
  if (isVerifying) return;
  isVerifying = true;
  
  removeAllVerityElements();
  showLoadingIndicator(text);
  
  try {
    const result = await chrome.runtime.sendMessage({
      action: 'verify',
      text: text
    });
    
    if (result.error) {
      showError(result.error);
    } else {
      showVerificationResult(result);
    }
  } catch (error) {
    showError(error.message);
  } finally {
    isVerifying = false;
  }
}

/**
 * Show loading indicator
 */
function showLoadingIndicator(text) {
  const indicator = document.createElement('div');
  indicator.className = 'verity-tooltip verity-loading';
  indicator.id = 'verity-loading';
  indicator.innerHTML = `
    <div class="verity-tooltip-header">
      <div class="verity-logo">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2">
          <path d="M9 12l2 2 4-4"/>
          <circle cx="12" cy="12" r="10"/>
        </svg>
        <span>Verity</span>
      </div>
    </div>
    <div class="verity-tooltip-body">
      <div class="verity-spinner"></div>
      <p>Verifying claim...</p>
      <p class="verity-claim-preview">"${text.substring(0, 100)}${text.length > 100 ? '...' : ''}"</p>
    </div>
  `;
  
  positionTooltip(indicator);
  document.body.appendChild(indicator);
  currentTooltip = indicator;
}

/**
 * Hide loading indicator
 */
function hideLoadingIndicator() {
  const indicator = document.getElementById('verity-loading');
  if (indicator) {
    indicator.remove();
  }
}

/**
 * Show verification result
 */
function showVerificationResult(result) {
  removeAllVerityElements();
  
  const verdict = result.verdict || 'unknown';
  const confidence = result.confidence || 0;
  const sources = result.sources || [];
  const explanation = result.explanation || 'No explanation available';
  
  const verdictColors = {
    'true': '#22C55E',
    'mostly_true': '#84CC16',
    'mixed': '#EAB308',
    'mostly_false': '#F97316',
    'false': '#EF4444',
    'unverifiable': '#6B7280'
  };
  
  const verdictText = {
    'true': 'TRUE',
    'mostly_true': 'MOSTLY TRUE',
    'mixed': 'MIXED',
    'mostly_false': 'MOSTLY FALSE',
    'false': 'FALSE',
    'unverifiable': 'UNVERIFIABLE'
  };
  
  const color = verdictColors[verdict] || '#6B7280';
  const displayVerdict = verdictText[verdict] || verdict.toUpperCase();
  
  const tooltip = document.createElement('div');
  tooltip.className = 'verity-tooltip verity-result';
  tooltip.innerHTML = `
    <div class="verity-tooltip-header">
      <div class="verity-logo">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2">
          <path d="M9 12l2 2 4-4"/>
          <circle cx="12" cy="12" r="10"/>
        </svg>
        <span>Verity</span>
      </div>
      <button class="verity-close" aria-label="Close">&times;</button>
    </div>
    
    <div class="verity-verdict" style="background: ${color}20; border-left: 4px solid ${color};">
      <span class="verity-verdict-text" style="color: ${color}">${displayVerdict}</span>
      <span class="verity-confidence">${confidence}% confidence</span>
    </div>
    
    <div class="verity-tooltip-body">
      <p class="verity-explanation">${explanation}</p>
      
      ${sources.length > 0 ? `
        <div class="verity-sources">
          <h4>Sources (${sources.length})</h4>
          <ul>
            ${sources.slice(0, 3).map(source => `
              <li>
                <a href="${source.url}" target="_blank" rel="noopener">
                  ${source.name || source.title || 'Source'}
                </a>
              </li>
            `).join('')}
          </ul>
        </div>
      ` : ''}
    </div>
    
    <div class="verity-tooltip-footer">
      <a href="https://verity-systems.vercel.app/dashboard" target="_blank">View Details</a>
    </div>
  `;
  
  positionTooltip(tooltip);
  
  // Add close handler
  tooltip.querySelector('.verity-close').addEventListener('click', () => {
    tooltip.remove();
    currentTooltip = null;
  });
  
  document.body.appendChild(tooltip);
  currentTooltip = tooltip;
}

/**
 * Show error message
 */
function showError(message) {
  removeAllVerityElements();
  
  const tooltip = document.createElement('div');
  tooltip.className = 'verity-tooltip verity-error';
  tooltip.innerHTML = `
    <div class="verity-tooltip-header">
      <div class="verity-logo">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
        <span>Verity</span>
      </div>
      <button class="verity-close" aria-label="Close">&times;</button>
    </div>
    <div class="verity-tooltip-body">
      <p class="verity-error-message">${message}</p>
      <button class="verity-retry-btn">Retry</button>
    </div>
  `;
  
  positionTooltip(tooltip);
  
  tooltip.querySelector('.verity-close').addEventListener('click', () => {
    tooltip.remove();
    currentTooltip = null;
  });
  
  document.body.appendChild(tooltip);
  currentTooltip = tooltip;
}

/**
 * Position tooltip in viewport
 */
function positionTooltip(tooltip) {
  tooltip.style.position = 'fixed';
  tooltip.style.zIndex = '999999';
  
  // Get selection position
  const selection = window.getSelection();
  if (selection.rangeCount > 0) {
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    
    // Position below selection
    let top = rect.bottom + 10;
    let left = rect.left;
    
    // Ensure it stays in viewport
    const tooltipWidth = 360;
    const tooltipHeight = 300;
    
    if (left + tooltipWidth > window.innerWidth) {
      left = window.innerWidth - tooltipWidth - 20;
    }
    if (left < 10) left = 10;
    
    if (top + tooltipHeight > window.innerHeight) {
      top = rect.top - tooltipHeight - 10;
    }
    
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
  } else {
    // Center in viewport
    tooltip.style.left = '50%';
    tooltip.style.top = '100px';
    tooltip.style.transform = 'translateX(-50%)';
  }
}

/**
 * Remove all Verity elements from page
 */
function removeAllVerityElements() {
  document.querySelectorAll('.verity-tooltip, .verity-verify-btn').forEach(el => el.remove());
  currentTooltip = null;
}

// Log when content script loads
(this.verityLogger || console).info('Verity content script loaded');
