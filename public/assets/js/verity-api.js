/**
 * Verity Systems - Unified API Client
 * ====================================
 * Single, clean interface to the Verity fact-checking API
 * 
 * @version 1.0.0
 * @author Verity Systems
 */

const VerityAPI = (function() {
    'use strict';

    // Configuration
    const CONFIG = {
        baseURL: (typeof window !== 'undefined' && 
            (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'))
            ? 'http://localhost:8000'
            : 'https://veritysystems-production.up.railway.app',
        timeout: 30000,
        retries: 1
    };

    // Cache for health status
    let healthCache = { status: null, timestamp: 0 };
    const HEALTH_CACHE_TTL = 30000; // 30 seconds

    /**
     * Make an API request with timeout and error handling
     */
    async function request(endpoint, options = {}) {
        const url = `${CONFIG.baseURL}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    ...options.headers
                },
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timed out');
            }
            throw error;
        }
    }

    /**
     * Check API health status (cached)
     */
    async function checkHealth() {
        const now = Date.now();
        
        // Return cached result if still valid
        if (healthCache.status !== null && (now - healthCache.timestamp) < HEALTH_CACHE_TTL) {
            return healthCache.status;
        }

        try {
            const data = await request('/health');
            healthCache = { 
                status: { online: true, ...data }, 
                timestamp: now 
            };
            return healthCache.status;
        } catch (error) {
            healthCache = { 
                status: { online: false, error: error.message }, 
                timestamp: now 
            };
            return healthCache.status;
        }
    }

    /**
     * Verify a claim
     * @param {string} claim - The claim to verify
     * @param {object} options - Optional settings
     * @returns {Promise<object>} Verification result
     */
    async function verify(claim, options = {}) {
        if (!claim || typeof claim !== 'string') {
            throw new Error('Claim must be a non-empty string');
        }

        if (claim.trim().length < 5) {
            throw new Error('Claim must be at least 5 characters');
        }

        const response = await request('/verify', {
            method: 'POST',
            body: JSON.stringify({
                claim: claim.trim(),
                detailed: options.detailed !== false
            })
        });

        return formatResponse(response);
    }

    /**
     * Analyze a URL for fact-checking
     * @param {string} url - The URL to analyze
     * @returns {Promise<object>} Analysis result
     */
    async function analyzeURL(url) {
        if (!url || !isValidURL(url)) {
            throw new Error('Invalid URL provided');
        }

        return request('/analyze/url', {
            method: 'POST',
            body: JSON.stringify({ url })
        });
    }

    /**
     * Analyze text content
     * @param {string} text - The text to analyze
     * @returns {Promise<object>} Analysis result
     */
    async function analyzeText(text) {
        if (!text || text.trim().length < 20) {
            throw new Error('Text must be at least 20 characters');
        }

        return request('/analyze/text', {
            method: 'POST',
            body: JSON.stringify({ text: text.trim() })
        });
    }

    /**
     * Get API statistics
     */
    async function getStats() {
        return request('/stats');
    }

    /**
     * Get available providers
     */
    async function getProviders() {
        return request('/providers');
    }

    /**
     * Format API response for UI consumption
     */
    function formatResponse(response) {
        const verdictMap = {
            'true': { emoji: '✅', label: 'Verified True', color: '#22c55e' },
            'mostly_true': { emoji: '✅', label: 'Mostly True', color: '#22c55e' },
            'false': { emoji: '❌', label: 'Verified False', color: '#ef4444' },
            'mostly_false': { emoji: '❌', label: 'Mostly False', color: '#ef4444' },
            'partially_true': { emoji: '⚠️', label: 'Partially True', color: '#f59e0b' },
            'mixed': { emoji: '⚠️', label: 'Mixed', color: '#f59e0b' },
            'unverifiable': { emoji: '❓', label: 'Unverifiable', color: '#6b7280' }
        };

        const verdict = response.verdict?.toLowerCase() || 'unverifiable';
        const verdictInfo = verdictMap[verdict] || verdictMap.unverifiable;

        return {
            id: response.id,
            claim: response.claim,
            verdict: verdict,
            verdictEmoji: verdictInfo.emoji,
            verdictLabel: verdictInfo.label,
            verdictColor: verdictInfo.color,
            confidence: response.confidence,
            confidencePercent: Math.round((response.confidence || 0) * 100),
            explanation: response.explanation || '',
            sources: response.sources || [],
            providersUsed: response.providers_used || [],
            timestamp: response.timestamp,
            cached: response.cached || false,
            raw: response
        };
    }

    /**
     * Validate URL format
     */
    function isValidURL(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch {
            return false;
        }
    }

    // Public API
    return {
        verify,
        analyzeURL,
        analyzeText,
        checkHealth,
        getStats,
        getProviders,
        config: CONFIG
    };
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VerityAPI;
}
