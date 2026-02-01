// ================================================
// VERITY TIERED API SERVICE
// Desktop & Platform Integration
// ================================================

/**
 * Tiered Verification API Service
 * Connects to Verity's LangChain-powered tiered verification system
 */
class VerityAPIService {
    constructor(config = {}) {
        this.baseUrl = config.apiEndpoint || 'http://localhost:8081';
        this.tier = config.tier || 'free';
        this.platform = config.platform || 'desktop';
        this.apiKey = config.apiKey || '';
        this.timeout = config.timeout || 30000;
    }

    // Update configuration
    setConfig(config) {
        if (config.apiEndpoint) this.baseUrl = config.apiEndpoint;
        if (config.tier) this.tier = config.tier;
        if (config.platform) this.platform = config.platform;
        if (config.apiKey) this.apiKey = config.apiKey;
    }

    // Get headers based on tier
    _getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'X-Platform': this.platform,
            'X-Tier': this.tier
        };
        if (this.apiKey) {
            headers['Authorization'] = `Bearer ${this.apiKey}`;
            headers['X-API-Key'] = this.apiKey;
        }
        return headers;
    }

    // Generic API request
    async _request(endpoint, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers: { ...this._getHeaders(), ...options.headers },
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    // ===========================================
    // TIERED VERIFICATION ENDPOINTS
    // ===========================================

    /**
     * Tiered verification - main verification endpoint
     * Uses LangChain orchestration with tier-based model access
     */
    async verifyTiered(claim, options = {}) {
        return this._request('/tiered-verify', {
            method: 'POST',
            body: JSON.stringify({
                claim,
                tier: options.tier || this.tier,
                platform: options.platform || this.platform,
                context: options.context || '',
                include_free_providers: options.includeFreeProviders ?? true
            })
        });
    }

    /**
     * Platform-specific verification
     */
    async verifyPlatform(claim, options = {}) {
        const endpoint = `/platform/${this.platform}/verify`;
        return this._request(endpoint, {
            method: 'POST',
            body: JSON.stringify({
                claim,
                tier: options.tier || this.tier,
                api_key: this.apiKey
            })
        });
    }

    /**
     * Batch verification (Professional+ only)
     */
    async batchVerify(claims, options = {}) {
        return this._request('/platform/api/batch-verify', {
            method: 'POST',
            body: JSON.stringify({
                claims,
                tier: options.tier || this.tier,
                api_key: this.apiKey
            })
        });
    }

    // ===========================================
    // TIER INFORMATION
    // ===========================================

    /**
     * Get all available tiers
     */
    async getTiers() {
        return this._request('/tiers', { method: 'GET' });
    }

    /**
     * Get specific tier details
     */
    async getTierDetails(tierName) {
        return this._request(`/tiers/${tierName}`, { method: 'GET' });
    }

    /**
     * Get models available for current tier
     */
    async getAvailableModels() {
        const tierInfo = await this.getTierDetails(this.tier);
        return {
            commercial: tierInfo.commercial_models || [],
            specialized: tierInfo.specialized_models || [],
            free: tierInfo.free_providers || [],
            maxModels: tierInfo.max_models || 1
        };
    }

    // ===========================================
    // SPECIALIZED MODELS
    // ===========================================

    /**
     * List specialized domain models
     */
    async listSpecializedModels() {
        return this._request('/specialized-models', { method: 'GET' });
    }

    /**
     * Verify with specialized model
     */
    async verifySpecialized(claim, options = {}) {
        return this._request('/specialized-models/verify', {
            method: 'POST',
            body: JSON.stringify({
                claim,
                domain: options.domain || null,
                auto_select: options.autoSelect ?? true
            })
        });
    }

    // ===========================================
    // AI MODELS
    // ===========================================

    /**
     * List all AI models
     */
    async listAllModels() {
        return this._request('/all-ai-models', { method: 'GET' });
    }

    /**
     * Unified verification with all models
     */
    async verifyUnified(claim, options = {}) {
        return this._request('/unified-verify', {
            method: 'POST',
            body: JSON.stringify({
                claim,
                mode: options.mode || 'standard',
                use_specialized: options.useSpecialized ?? true,
                use_free_providers: options.useFreeProviders ?? true,
                use_commercial: options.useCommercial ?? true
            })
        });
    }

    // ===========================================
    // FREE PROVIDERS
    // ===========================================

    /**
     * List free providers
     */
    async listFreeProviders() {
        return this._request('/free-providers', { method: 'GET' });
    }

    /**
     * Verify with free providers only
     */
    async verifyFreeOnly(claim) {
        return this._request('/free-providers/verify', {
            method: 'POST',
            body: JSON.stringify({ claim })
        });
    }

    // ===========================================
    // HEALTH & STATUS
    // ===========================================

    /**
     * Check API health
     */
    async health() {
        return this._request('/health', { method: 'GET' });
    }

    /**
     * Get API status
     */
    async status() {
        return this._request('/status', { method: 'GET' });
    }

    // ===========================================
    // LEGACY ENDPOINTS (backward compatibility)
    // ===========================================

    /**
     * Legacy verify endpoint
     */
    async verify(claim, options = {}) {
        return this._request('/verify', {
            method: 'POST',
            body: JSON.stringify({
                claim,
                detailed: options.detailed ?? true
            })
        });
    }
}

// ===========================================
// TIER-AWARE VERIFICATION MANAGER
// ===========================================

class VerityVerificationManager {
    constructor(apiService) {
        this.api = apiService;
        this.tierCache = null;
        this.modelCache = null;
    }

    /**
     * Smart verification - chooses best endpoint based on tier and options
     */
    async verify(claim, options = {}) {
        const tier = options.tier || this.api.tier;
        
        // Free tier: use basic verify
        if (tier === 'free') {
            return this.api.verifyFreeOnly(claim);
        }
        
        // Starter-Pro: use tiered verify
        if (['starter', 'pro'].includes(tier)) {
            return this.api.verifyTiered(claim, options);
        }
        
        // Professional+: use full unified verify
        return this.api.verifyUnified(claim, {
            useSpecialized: true,
            useFreeProviders: true,
            useCommercial: true,
            ...options
        });
    }

    /**
     * Domain-aware verification - auto-selects specialized models
     */
    async verifyWithDomain(claim, domain = null, options = {}) {
        if (domain) {
            return this.api.verifySpecialized(claim, { domain, ...options });
        }
        return this.api.verifySpecialized(claim, { autoSelect: true, ...options });
    }

    /**
     * Get tier limits and check usage
     */
    async getTierLimits() {
        if (!this.tierCache) {
            this.tierCache = await this.api.getTiers();
        }
        return this.tierCache.tiers[this.api.tier] || this.tierCache.tiers.free;
    }

    /**
     * Check if feature is available for current tier
     */
    async hasFeature(featureName) {
        const limits = await this.getTierLimits();
        return limits.features?.[featureName] ?? false;
    }
}

// Export for use in desktop app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VerityAPIService, VerityVerificationManager };
}

// Also attach to window for browser context
if (typeof window !== 'undefined') {
    window.VerityAPIService = VerityAPIService;
    window.VerityVerificationManager = VerityVerificationManager;
}
