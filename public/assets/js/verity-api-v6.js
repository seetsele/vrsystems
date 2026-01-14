/**
 * Verity API Client v6 - Ultimate Verification System Integration
 * ================================================================
 * Connects to the 3-pass verification system with 75+ data sources
 * 
 * Features:
 * - Claim verification with consensus voting
 * - URL/article analysis
 * - Text content analysis
 * - Batch processing
 * - Provider statistics
 */

class VerityAPIv6 {
    constructor(options = {}) {
        const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
        this.baseURL = options.baseURL || (isLocal ? 'http://localhost:8000' : 'https://veritysystems-production.up.railway.app');
        this.timeout = options.timeout || 60000;
        this.retries = options.retries || 2;
        this.debug = options.debug || false;
    }

    // =========================================================================
    // CORE API METHODS
    // =========================================================================

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...options.headers
            },
            signal: controller.signal
        };

        try {
            if (this.debug) (window.verityLogger || console).debug(`[Verity API] ${options.method || 'GET'} ${url}`);
            
            const response = await fetch(url, config);
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

    // =========================================================================
    // HEALTH & STATUS
    // =========================================================================

    async checkHealth() {
        try {
            const data = await this.request('/health');
            return { online: true, ...data };
        } catch (error) {
            return { online: false, error: error.message };
        }
    }

    async getStats() {
        return this.request('/stats');
    }

    async getProviders() {
        return this.request('/providers');
    }

    // =========================================================================
    // CLAIM VERIFICATION (3-Pass System)
    // =========================================================================

    async verifyClaim(claim, options = {}) {
        const response = await this.request('/verify', {
            method: 'POST',
            body: JSON.stringify({
                claim: claim,
                detailed: options.detailed !== false
            })
        });

        return this.formatVerifyResponse(response);
    }

    formatVerifyResponse(response) {
        // Convert API response to UI-friendly format
        const verdictEmoji = {
            'true': '✅',
            'false': '❌',
            'partially_true': '⚠️',
            'unverifiable': '❓'
        };

        const verdictLabel = {
            'true': 'Verified True',
            'false': 'Verified False',
            'partially_true': 'Partially True',
            'unverifiable': 'Unverifiable'
        };

        const verdictColor = {
            'true': '#22c55e',
            'false': '#ef4444',
            'partially_true': '#f59e0b',
            'unverifiable': '#6b7280'
        };

        return {
            claim: response.claim,
            verdict: response.verdict,
            verdictEmoji: verdictEmoji[response.verdict] || '❓',
            verdictLabel: verdictLabel[response.verdict] || 'Unknown',
            verdictColor: verdictColor[response.verdict] || '#6b7280',
            confidence: response.confidence,
            confidencePercent: Math.round(response.confidence * 100),
            category: response.category,
            consistency: response.consistency,
            consistencyPercent: Math.round((response.consistency || 0) * 100),
            sourcesUsed: response.sources || 0,
            processingTime: response.time ? response.time.toFixed(2) : '0',
            passes: response.passes || null,
            raw: response
        };
    }

    // =========================================================================
    // URL ANALYSIS
    // =========================================================================

    async analyzeURL(url) {
        const response = await this.request('/analyze/url', {
            method: 'POST',
            body: JSON.stringify({ url })
        });

        return this.formatURLResponse(response);
    }

    formatURLResponse(response) {
        if (response.status === 'failed') {
            return {
                success: false,
                url: response.url,
                error: response.error || 'Could not analyze URL'
            };
        }

        const credibilityLabel = response.source_credibility >= 0.8 ? 'High' :
                                 response.source_credibility >= 0.6 ? 'Medium' : 'Low';

        return {
            success: true,
            url: response.url,
            title: response.title,
            credibility: response.source_credibility,
            credibilityPercent: Math.round(response.source_credibility * 100),
            credibilityLabel: credibilityLabel,
            claimsFound: response.claims_found,
            claimsVerified: response.claims_verified,
            claimResults: response.claim_results || [],
            accuracyScore: response.accuracy_score,
            accuracyPercent: Math.round((response.accuracy_score || 0) * 100),
            summary: response.summary,
            raw: response
        };
    }

    // =========================================================================
    // TEXT ANALYSIS
    // =========================================================================

    async analyzeText(text) {
        const response = await this.request('/analyze/text', {
            method: 'POST',
            body: JSON.stringify({ text })
        });

        return this.formatTextResponse(response);
    }

    formatTextResponse(response) {
        const results = response.results || [];
        const trueCount = results.filter(r => r.verdict === 'true').length;
        const falseCount = results.filter(r => r.verdict === 'false').length;
        const partialCount = results.filter(r => r.verdict === 'partially_true').length;
        
        let overallVerdict = 'unverifiable';
        if (results.length > 0) {
            if (trueCount > falseCount && trueCount > partialCount) overallVerdict = 'mostly_true';
            else if (falseCount > trueCount) overallVerdict = 'mostly_false';
            else if (partialCount > 0) overallVerdict = 'mixed';
        }

        return {
            claimsFound: response.claims_found,
            claimsAnalyzed: results.length,
            results: results.map(r => ({
                claim: r.claim,
                verdict: r.verdict,
                confidence: r.confidence,
                confidencePercent: Math.round((r.confidence || 0) * 100)
            })),
            summary: {
                true: trueCount,
                false: falseCount,
                partial: partialCount,
                overall: overallVerdict
            },
            raw: response
        };
    }

    // =========================================================================
    // BATCH PROCESSING
    // =========================================================================

    async batchProcess(items, options = {}) {
        const response = await this.request('/batch', {
            method: 'POST',
            body: JSON.stringify({
                items: items,
                max_concurrent: options.maxConcurrent || 5
            })
        });

        return {
            total: response.total,
            processed: response.processed,
            failed: response.failed,
            processingTime: response.time ? response.time.toFixed(2) : '0',
            results: response.results,
            successRate: response.total > 0 ? Math.round((response.processed / response.total) * 100) : 0
        };
    }

    // =========================================================================
    // CONVENIENCE METHODS
    // =========================================================================

    async quickVerify(claim) {
        // Simplified verification for quick results
        try {
            const result = await this.verifyClaim(claim, { detailed: false });
            return {
                verdict: result.verdictLabel,
                confidence: result.confidencePercent,
                emoji: result.verdictEmoji
            };
        } catch (error) {
            return {
                verdict: 'Error',
                confidence: 0,
                emoji: '⚠️',
                error: error.message
            };
        }
    }

    async getSystemInfo() {
        const [health, stats, providers] = await Promise.all([
            this.checkHealth(),
            this.getStats().catch(() => null),
            this.getProviders().catch(() => null)
        ]);

        return {
            health,
            stats,
            providers,
            version: stats?.version || 'Unknown'
        };
    }
}

// =========================================================================
// GLOBAL INSTANCE
// =========================================================================

const _isLocalV6 = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
window.VerityAPI = new VerityAPIv6({
    baseURL: _isLocalV6 ? 'http://localhost:8000' : 'https://veritysystems-production.up.railway.app',
    debug: _isLocalV6
});

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VerityAPIv6;
}

(window.verityLogger || console).info('✅ Verity API v6 Client loaded');
