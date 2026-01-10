/**
 * Verity Browser Extension - Popup Script
 * Updated for v10.0.0 dark amber theme
 */

// Elements
const claimInput = document.getElementById('claim');
const verifyBtn = document.getElementById('verify-btn');
const resultDiv = document.getElementById('result');
const verdictBadge = document.getElementById('verdict-badge');
const confidenceDiv = document.getElementById('confidence');
const explanationDiv = document.getElementById('explanation');
const sourcesDiv = document.getElementById('sources');
const providersUsedDiv = document.getElementById('providers-used');
const errorDiv = document.getElementById('error');
const settingsBtn = document.getElementById('settings-btn');

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
  // Try to get selected text from active tab
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
      chrome.tabs.sendMessage(tab.id, { action: 'getSelection' }, (response) => {
        if (response && response.text) {
          claimInput.value = response.text;
        }
      });
    }
  } catch (e) {
    // Ignore - just don't prefill
  }
});

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
  
  await verifyClaim(claim);
});

// Settings button
settingsBtn.addEventListener('click', () => {
  chrome.runtime.openOptionsPage();
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
  verifyBtn.innerHTML = '<div class="spinner"></div> Verifying...';
  hideError();
  hideResult();
  
  try {
    const result = await chrome.runtime.sendMessage({
      action: 'verify',
      text: claim
    });
    
    if (result.error) {
      showError(result.error);
    } else {
      showResult(result);
    }
  } catch (error) {
    showError(error.message || 'Failed to verify claim');
  } finally {
    verifyBtn.disabled = false;
    verifyBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M9 12l2 2 4-4"/>
        <circle cx="12" cy="12" r="10"/>
      </svg>
      Verify Claim
    `;
  }
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
  
  // Get verdict config
  const config = verdictConfig[verdict] || verdictConfig['unverifiable'];
  
  // Update verdict badge
  verdictBadge.textContent = config.text;
  verdictBadge.className = `verdict-badge ${config.class}`;
  
  // Update confidence with visual bar
  const confidenceBar = `
    <div class="confidence-label">${confidence}% Confidence</div>
    <div class="confidence-bar">
      <div class="confidence-fill" style="width: ${confidence}%"></div>
    </div>
  `;
  confidenceDiv.innerHTML = confidenceBar;
  
  // Update explanation
  explanationDiv.textContent = explanation;
  
  // Update providers used
  if (providersUsedDiv && providers.length > 0) {
    providersUsedDiv.innerHTML = '<div class="providers-title">AI Models Used</div>';
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'provider-tags';
    
    providers.slice(0, 8).forEach(provider => {
      const tag = document.createElement('span');
      tag.className = 'provider-tag';
      tag.textContent = providerNames[provider] || provider;
      tagsContainer.appendChild(tag);
    });
    
    if (providers.length > 8) {
      const moreTag = document.createElement('span');
      moreTag.className = 'provider-tag provider-more';
      moreTag.textContent = `+${providers.length - 8} more`;
      tagsContainer.appendChild(moreTag);
    }
    
    providersUsedDiv.appendChild(tagsContainer);
    providersUsedDiv.style.display = 'block';
  }
  
  // Update sources
  sourcesDiv.innerHTML = '<div class="sources-title">Sources</div>';
  if (sources.length > 0) {
    sources.slice(0, 5).forEach(source => {
      const link = document.createElement('a');
      link.className = 'source-item';
      link.href = source.url;
      link.target = '_blank';
      link.rel = 'noopener';
      link.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
          <polyline points="15 3 21 3 21 9"/>
          <line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
        ${source.name || source.title || new URL(source.url).hostname}
      `;
      sourcesDiv.appendChild(link);
    });
  } else {
    const noSources = document.createElement('span');
    noSources.className = 'no-sources';
    noSources.textContent = 'No external sources available';
    sourcesDiv.appendChild(noSources);
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
