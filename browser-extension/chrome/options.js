/**
 * Verity Browser Extension - Options Page Script
 */

// Elements
const apiUrlInput = document.getElementById('api-url');
const apiKeyInput = document.getElementById('api-key');
const autoVerifyCheckbox = document.getElementById('auto-verify');
const showNotificationsCheckbox = document.getElementById('show-notifications');
const defaultLanguageSelect = document.getElementById('default-language');
const usageStats = document.getElementById('usage-stats');
const saveBtn = document.getElementById('save-btn');
const resetBtn = document.getElementById('reset-btn');
const statusDiv = document.getElementById('status');

// Default configuration
const DEFAULT_CONFIG = {
  apiUrl: 'https://api.verity-systems.com',
  apiKey: '',
  autoVerify: false,
  showNotifications: true,
  defaultLanguage: 'en'
};

// Load settings on page load
document.addEventListener('DOMContentLoaded', loadSettings);

// Save settings
saveBtn.addEventListener('click', saveSettings);

// Reset to defaults
resetBtn.addEventListener('click', resetSettings);

/**
 * Load settings from storage
 */
async function loadSettings() {
  try {
    const result = await chrome.storage.sync.get(['config', 'stats']);
    const config = result.config || DEFAULT_CONFIG;
    
    apiUrlInput.value = config.apiUrl || '';
    apiKeyInput.value = config.apiKey || '';
    autoVerifyCheckbox.checked = config.autoVerify || false;
    showNotificationsCheckbox.checked = config.showNotifications !== false;
    defaultLanguageSelect.value = config.defaultLanguage || 'en';
    
    // Load usage stats
    const stats = result.stats || { verifications: 0, lastUsed: null };
    updateUsageStats(stats);
    
  } catch (error) {
    showStatus('Error loading settings: ' + error.message, 'error');
  }
}

/**
 * Save settings to storage
 */
async function saveSettings() {
  try {
    const config = {
      apiUrl: apiUrlInput.value.trim() || DEFAULT_CONFIG.apiUrl,
      apiKey: apiKeyInput.value.trim(),
      autoVerify: autoVerifyCheckbox.checked,
      showNotifications: showNotificationsCheckbox.checked,
      defaultLanguage: defaultLanguageSelect.value
    };
    
    await chrome.storage.sync.set({ config });
    
    // Notify background script
    chrome.runtime.sendMessage({ action: 'updateConfig', config });
    
    showStatus('Settings saved successfully!', 'success');
    
  } catch (error) {
    showStatus('Error saving settings: ' + error.message, 'error');
  }
}

/**
 * Reset settings to defaults
 */
async function resetSettings() {
  if (!confirm('Are you sure you want to reset all settings to defaults?')) {
    return;
  }
  
  try {
    await chrome.storage.sync.set({ config: DEFAULT_CONFIG });
    
    // Update UI
    apiUrlInput.value = '';
    apiKeyInput.value = '';
    autoVerifyCheckbox.checked = false;
    showNotificationsCheckbox.checked = true;
    defaultLanguageSelect.value = 'en';
    
    // Notify background script
    chrome.runtime.sendMessage({ action: 'updateConfig', config: DEFAULT_CONFIG });
    
    showStatus('Settings reset to defaults', 'success');
    
  } catch (error) {
    showStatus('Error resetting settings: ' + error.message, 'error');
  }
}

/**
 * Update usage statistics display
 */
function updateUsageStats(stats) {
  const verifications = stats.verifications || 0;
  const lastUsed = stats.lastUsed ? new Date(stats.lastUsed).toLocaleDateString() : 'Never';
  
  usageStats.innerHTML = `
    <strong>Total verifications:</strong> ${verifications}<br>
    <strong>Last used:</strong> ${lastUsed}
  `;
}

/**
 * Show status message
 */
function showStatus(message, type) {
  statusDiv.textContent = message;
  statusDiv.className = 'status ' + type;
  
  // Auto-hide after 3 seconds
  setTimeout(() => {
    statusDiv.className = 'status';
  }, 3000);
}
