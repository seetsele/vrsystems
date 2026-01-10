/**
 * Verity Browser Extension - Popup Script
 * Updated for v10.0.0 with tabs, tier-based features, and animations
 */

// Elements
const claimInput = document.getElementById('claim');
const verifyBtn = document.getElementById('verify-btn');
const btnText = document.getElementById('btn-text');
const resultDiv = document.getElementById('result');
const verdictBadge = document.getElementById('verdict-badge');
const confidenceDiv = document.getElementById('confidence');
const explanationDiv = document.getElementById('explanation');
const sourcesDiv = document.getElementById('sources');
const sourcesListDiv = document.getElementById('sources-list');
const providerTagsDiv = document.getElementById('provider-tags');
const errorDiv = document.getElementById('error');
const charCountSpan = document.getElementById('char-count');
const tierBadge = document.getElementById('tier-badge');
const tierName = document.getElementById('tier-name');
const usageText = document.getElementById('usage-text');
const usageFill = document.getElementById('usage-fill');

// Tab elements
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');
const historyList = document.getElementById('history-list');
const historyEmpty = document.getElementById('history-empty');

// Settings toggles
const toggles = document.querySelectorAll('.toggle');

// Model selector
const modelChips = document.querySelectorAll('.model-chip');
let selectedModel = 'quick';

// User state
let userTier = 'pro';
let usedVerifications = 1700;
let tierLimits = {
  free: 300, starter: 1200, pro: 2500, professional: 5000,
  business: 15000, business_plus: 25000, enterprise: 75000
};

// Verification history
let verificationHistory = [];

// Verdict mappings with icons
const verdictConfig = {
  'true': { text: 'VERIFIED TRUE', class: 'verdict-true', icon: '✓' },
  'mostly_true': { text: 'MOSTLY TRUE', class: 'verdict-mostly-true', icon: '✓' },
  'mixed': { text: 'MIXED EVIDENCE', class: 'verdict-mixed', icon: '⚠' },
  'mostly_false': { text: 'MOSTLY FALSE', class: 'verdict-mostly-false', icon: '✗' },
  'false': { text: 'VERIFIED FALSE', class: 'verdict-false', icon: '✗' },
  'unverifiable': { text: 'UNVERIFIABLE', class: 'verdict-unverifiable', icon: '?' }
};

// Provider name mappings for display
const providerNames = {
  'openai': 'OpenAI GPT-4',
  'anthropic': 'Claude 3.5',
  'google': 'Google Gemini',
  'mistral': 'Mistral AI',
  'together': 'Together AI',
  'groq': 'Groq',
  'cohere': 'Cohere',
  'perplexity': 'Perplexity',
  'huggingface': 'HuggingFace',
  'deepseek': 'DeepSeek',
  'github': 'GitHub Copilot',
  'azure': 'Azure OpenAI',
  'qwen': 'Qwen',
  'llama': 'Meta Llama',
  'gemma': 'Google Gemma',
  'falcon': 'TII Falcon',
  'yi': 'Yi AI',
  'phi': 'Microsoft Phi'
};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  // Load saved settings and history
  loadSettings();
  loadHistory();
  updateTierDisplay();
  
  // Initialize tab navigation
  initTabs();
  
  // Initialize model selector
  initModelSelector();
  
  // Initialize settings toggles
  initToggles();
  
  // Character counter
  claimInput.addEventListener('input', () => {
    charCountSpan.textContent = claimInput.value.length;
  });
  
  // Try to get selected text from active tab
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
      chrome.tabs.sendMessage(tab.id, { action: 'getSelection' }, (response) => {
        if (response && response.text) {
          claimInput.value = response.text;
          charCountSpan.textContent = response.text.length;
        }
      });
    }
  } catch (e) {
    // Ignore - just don't prefill
  }
});

// Tab navigation
function initTabs() {
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.dataset.tab;
      
      // Update active tab button
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      // Show active panel
      tabPanels.forEach(panel => {
        panel.classList.remove('active');
        if (panel.id === `panel-${tabId}`) {
          panel.classList.add('active');
        }
      });
    });
  });
}

// Model selector
function initModelSelector() {
  modelChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const models = chip.dataset.models;
      
      // Check if locked (deep requires pro+)
      if (models === 'deep' && !['pro', 'professional', 'business', 'business_plus', 'enterprise'].includes(userTier)) {
        window.open('https://vrsystemss.vercel.app/pricing.html', '_blank');
        return;
      }
      
      modelChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      selectedModel = models;
    });
  });
}

// Settings toggles
function initToggles() {
  toggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
      toggle.classList.toggle('active');
      saveSettings();
    });
  });
}

// Load settings from storage
function loadSettings() {
  chrome.storage.local.get(['settings', 'userTier', 'usedVerifications'], (data) => {
    if (data.settings) {
      document.getElementById('toggle-auto').classList.toggle('active', data.settings.autoVerify !== false);
      document.getElementById('toggle-notif').classList.toggle('active', data.settings.notifications !== false);
      document.getElementById('toggle-dark').classList.toggle('active', data.settings.darkMode !== false);
    }
    if (data.userTier) userTier = data.userTier;
    if (data.usedVerifications) usedVerifications = data.usedVerifications;
  });
}

// Save settings
function saveSettings() {
  const settings = {
    autoVerify: document.getElementById('toggle-auto').classList.contains('active'),
    notifications: document.getElementById('toggle-notif').classList.contains('active'),
    darkMode: document.getElementById('toggle-dark').classList.contains('active')
  };
  chrome.storage.local.set({ settings });
}

// Load verification history
function loadHistory() {
  chrome.storage.local.get(['verificationHistory'], (data) => {
    if (data.verificationHistory) {
      verificationHistory = data.verificationHistory;
      renderHistory();
    }
  });
}

// Render history list
function renderHistory() {
  if (verificationHistory.length === 0) {
    historyEmpty.style.display = 'block';
    historyList.style.display = 'none';
    return;
  }
  
  historyEmpty.style.display = 'none';
  historyList.style.display = 'block';
  historyList.innerHTML = '';
  
  verificationHistory.slice(0, 20).forEach((item, index) => {
    const div = document.createElement('div');
    div.className = 'history-item';
    div.innerHTML = `
      <div class="history-claim">${escapeHtml(item.claim)}</div>
      <div class="history-meta">
        <span class="history-verdict verdict-${item.verdict}">${item.verdict.toUpperCase()}</span>
        <span>${formatTimeAgo(item.timestamp)}</span>
      </div>
    `;
    div.addEventListener('click', () => {
      claimInput.value = item.claim;
      charCountSpan.textContent = item.claim.length;
      tabBtns[0].click(); // Switch to verify tab
    });
    historyList.appendChild(div);
  });
}

// Update tier display
function updateTierDisplay() {
  tierName.textContent = userTier.charAt(0).toUpperCase() + userTier.slice(1).replace('_', ' ');
  const limit = tierLimits[userTier] || 300;
  const percentage = Math.min((usedVerifications / limit) * 100, 100);
  
  usageText.textContent = `${usedVerifications.toLocaleString()} / ${limit.toLocaleString()}`;
  usageFill.style.width = `${percentage}%`;
  
  if (percentage >= 90) {
    usageFill.classList.add('danger');
    usageFill.classList.remove('warning');
  } else if (percentage >= 70) {
    usageFill.classList.add('warning');
    usageFill.classList.remove('danger');
  } else {
    usageFill.classList.remove('warning', 'danger');
  }
  
  // Update tier badge class
  tierBadge.className = `tier-badge ${userTier}`;
}

// Verify button click
verifyBtn.addEventListener('click', async () => {
  const claim = claimInput.value.trim();
  
  if (!claim) {
    showError('Please enter a claim to verify');
    return;
  }
  
  if (claim.length < 10) {
    showError('Please enter a longer claim (at least 10 characters)');
    return;
  }
  
  // Check usage limit
  const limit = tierLimits[userTier] || 300;
  if (usedVerifications >= limit) {
    showError('Verification limit reached. Please upgrade your plan.');
    return;
  }
  
  await verifyClaim(claim);
});

// Enter key to verify
claimInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.ctrlKey) {
    verifyBtn.click();
  }
});

/**
 * Verify a claim
 */
async function verifyClaim(claim) {
  // Show loading state
  verifyBtn.disabled = true;
  btnText.textContent = 'Verifying...';
  verifyBtn.querySelector('svg').style.display = 'none';
  const spinner = document.createElement('div');
  spinner.className = 'spinner';
  verifyBtn.insertBefore(spinner, btnText);
  
  hideError();
  hideResult();
  
  const startTime = Date.now();
  
  try {
    const result = await chrome.runtime.sendMessage({
      action: 'verify',
      text: claim,
      mode: selectedModel
    });
    
    if (result.error) {
      showError(result.error);
    } else {
      const timeTaken = ((Date.now() - startTime) / 1000).toFixed(1);
      result.timeTaken = timeTaken;
      showResult(result);
      
      // Update usage
      usedVerifications++;
      chrome.storage.local.set({ usedVerifications });
      updateTierDisplay();
      
      // Add to history
      addToHistory(claim, result);
    }
  } catch (error) {
    showError(error.message || 'Failed to verify claim');
  } finally {
    verifyBtn.disabled = false;
    spinner.remove();
    verifyBtn.querySelector('svg').style.display = '';
    btnText.textContent = 'Verify Now';
  }
}

// Add to verification history
function addToHistory(claim, result) {
  const historyItem = {
    claim: claim,
    verdict: result.verdict || 'unverifiable',
    confidence: result.confidence || 0,
    timestamp: Date.now()
  };
  
  verificationHistory.unshift(historyItem);
  verificationHistory = verificationHistory.slice(0, 50); // Keep last 50
  
  chrome.storage.local.set({ verificationHistory });
  renderHistory();
}

/**
 * Show verification result with providers used
 */
function showResult(result) {
  const verdict = result.verdict || 'unverifiable';
  const confidence = result.confidence || 0;
  const explanation = result.explanation || 'No explanation available';
  const sources = result.sources || [];
  const providers = result.providers_used || result.providersUsed || [];
  const timeTaken = result.timeTaken || '1.2';
  
  // Get verdict config
  const config = verdictConfig[verdict] || verdictConfig['unverifiable'];
  
  // Update verdict badge
  verdictBadge.textContent = `${config.icon} ${config.text}`;
  verdictBadge.className = `verdict-badge ${config.class}`;
  
  // Update confidence
  confidenceDiv.innerHTML = `Confidence: <strong>${confidence}%</strong>`;
  
  // Update explanation
  explanationDiv.textContent = explanation;
  
  // Update meta info
  document.getElementById('time-taken').textContent = `${timeTaken}s`;
  document.getElementById('models-used').textContent = `${providers.length || 12} AI models`;
  document.getElementById('sources-count').textContent = `${sources.length} sources`;
  
  // Update providers used
  if (providerTagsDiv && providers.length > 0) {
    providerTagsDiv.innerHTML = '';
    
    providers.slice(0, 8).forEach(provider => {
      const tag = document.createElement('span');
      tag.className = 'provider-tag';
      tag.textContent = providerNames[provider] || provider;
      providerTagsDiv.appendChild(tag);
    });
    
    if (providers.length > 8) {
      const moreTag = document.createElement('span');
      moreTag.className = 'provider-tag';
      moreTag.textContent = `+${providers.length - 8} more`;
      providerTagsDiv.appendChild(moreTag);
    }
  }
  
  // Update sources
  if (sourcesListDiv) {
    sourcesListDiv.innerHTML = '';
    if (sources.length > 0) {
      sources.slice(0, 5).forEach(source => {
        const link = document.createElement('a');
        link.className = 'source-item';
        link.href = source.url;
        link.target = '_blank';
        link.rel = 'noopener';
        link.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
            <polyline points="15 3 21 3 21 9"/>
            <line x1="10" y1="14" x2="21" y2="3"/>
          </svg>
          ${escapeHtml(source.name || source.title || new URL(source.url).hostname)}
        `;
        sourcesListDiv.appendChild(link);
      });
    } else {
      sourcesListDiv.innerHTML = '<span style="color: var(--text-muted); font-size: 12px;">No external sources</span>';
    }
  }
  
  // Show result with animation
  resultDiv.classList.add('visible');
}

/**
 * Hide result
 */
function hideResult() {
  resultDiv.classList.remove('visible');
}

/**
 * Show error message
 */
function showError(message) {
  errorDiv.textContent = message;
  errorDiv.classList.add('visible');
}

/**
 * Hide error message
 */
function hideError() {
  errorDiv.classList.remove('visible');
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Format timestamp to relative time
 */
function formatTimeAgo(timestamp) {
  const seconds = Math.floor((Date.now() - timestamp) / 1000);
  
  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  
  return new Date(timestamp).toLocaleDateString();
}
