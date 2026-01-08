/**
 * Verity Browser Extension - Popup Script
 */

// Elements
const claimInput = document.getElementById('claim');
const verifyBtn = document.getElementById('verify-btn');
const resultDiv = document.getElementById('result');
const verdictBadge = document.getElementById('verdict-badge');
const confidenceDiv = document.getElementById('confidence');
const explanationDiv = document.getElementById('explanation');
const sourcesDiv = document.getElementById('sources');
const errorDiv = document.getElementById('error');
const settingsBtn = document.getElementById('settings-btn');

// Verdict mappings
const verdictText = {
  'true': '✓ TRUE',
  'mostly_true': '✓ MOSTLY TRUE',
  'mixed': '⚠ MIXED',
  'mostly_false': '✗ MOSTLY FALSE',
  'false': '✗ FALSE',
  'unverifiable': '? UNVERIFIABLE'
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
 * Show verification result
 */
function showResult(result) {
  const verdict = result.verdict || 'unverifiable';
  const confidence = result.confidence || 0;
  const explanation = result.explanation || 'No explanation available';
  const sources = result.sources || [];
  
  // Update verdict badge
  verdictBadge.textContent = verdictText[verdict] || verdict.toUpperCase();
  verdictBadge.className = `verdict-badge verdict-${verdict}`;
  
  // Update confidence
  confidenceDiv.textContent = `${confidence}% confidence`;
  
  // Update explanation
  explanationDiv.textContent = explanation;
  
  // Update sources
  sourcesDiv.innerHTML = '<div class="sources-title">Sources</div>';
  if (sources.length > 0) {
    sources.slice(0, 5).forEach(source => {
      const link = document.createElement('a');
      link.className = 'source-item';
      link.href = source.url;
      link.target = '_blank';
      link.rel = 'noopener';
      link.textContent = source.name || source.title || source.url;
      sourcesDiv.appendChild(link);
    });
  } else {
    const noSources = document.createElement('span');
    noSources.style.fontSize = '13px';
    noSources.style.color = '#9CA3AF';
    noSources.textContent = 'No external sources available';
    sourcesDiv.appendChild(noSources);
  }
  
  // Show result
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
