/**
 * Verity Systems - Frontend API Client
 * Secure client for interacting with the fact-checking API
 */

class VerityClient {
    constructor(options = {}) {
        const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
        this.baseURL = options.baseURL || (isLocal ? 'http://localhost:8000' : 'https://veritysystems-production.up.railway.app');
        this.apiKey = options.apiKey || null;
        this.accessToken = options.accessToken || null;
        this.onError = options.onError || console.error;
        this.onRateLimitExceeded = options.onRateLimitExceeded || null;
        
        // Rate limit info
        this.rateLimitInfo = {
            limit: null,
            remaining: null,
            reset: null
        };
    }

    /**
     * Set API key for authentication
     */
    setApiKey(apiKey) {
        this.apiKey = apiKey;
    }

    /**
     * Set access token for JWT authentication
     */
    setAccessToken(token) {
        this.accessToken = token;
    }

    /**
     * Get authorization headers
     */
    _getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        } else if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        return headers;
    }

    /**
     * Parse rate limit headers from response
     */
    _parseRateLimitHeaders(response) {
        this.rateLimitInfo = {
            limit: response.headers.get('X-RateLimit-Limit'),
            remaining: response.headers.get('X-RateLimit-Remaining'),
            reset: response.headers.get('X-RateLimit-Reset')
        };
    }

    /**
     * Make API request with error handling
     */
    async _request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...this._getHeaders(),
                    ...options.headers
                }
            });

            // Parse rate limit headers
            this._parseRateLimitHeaders(response);

            // Handle rate limiting
            if (response.status === 429) {
                const retryAfter = response.headers.get('Retry-After');
                if (this.onRateLimitExceeded) {
                    this.onRateLimitExceeded(retryAfter);
                }
                throw new Error(`Rate limit exceeded. Retry after ${retryAfter} seconds.`);
            }

            // Handle other errors
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'API request failed');
            }

            return await response.json();
        } catch (error) {
            this.onError(error);
            throw error;
        }
    }

    // ===========================================
    // VERIFICATION ENDPOINTS
    // ===========================================

    /**
     * Verify a single claim
     * @param {string} claim - The claim to verify
     * @param {object} options - Additional options
     * @returns {Promise<object>} Verification result
     */
    async verifyClaim(claim, options = {}) {
        return this._request('/v1/verify', {
            method: 'POST',
            body: JSON.stringify({
                claim,
                providers: options.providers || null,
                use_cache: options.useCache !== false,
                anonymize_pii: options.anonymizePii !== false
            })
        });
    }

    /**
     * Verify a claim with detailed results
     * @param {string} claim - The claim to verify
     * @param {object} options - Additional options
     * @returns {Promise<object>} Detailed verification result
     */
    async verifyClaimDetailed(claim, options = {}) {
        return this._request('/v1/verify/detailed', {
            method: 'POST',
            body: JSON.stringify({
                claim,
                providers: options.providers || null,
                use_cache: options.useCache !== false,
                anonymize_pii: options.anonymizePii !== false
            })
        });
    }

    /**
     * Verify multiple claims in batch
     * @param {string[]} claims - Array of claims to verify
     * @param {object} options - Additional options
     * @returns {Promise<object>} Batch verification results
     */
    async verifyBatch(claims, options = {}) {
        return this._request('/v1/verify/batch', {
            method: 'POST',
            body: JSON.stringify({
                claims,
                providers: options.providers || null
            })
        });
    }

    // ===========================================
    // INFORMATION ENDPOINTS
    // ===========================================

    /**
     * Get available providers
     * @returns {Promise<object>} List of providers
     */
    async getProviders() {
        return this._request('/v1/providers');
    }

    /**
     * Get API usage statistics
     * @returns {Promise<object>} Usage statistics
     */
    async getUsage() {
        return this._request('/v1/usage');
    }

    /**
     * Health check
     * @returns {Promise<object>} Health status
     */
    async healthCheck() {
        return this._request('/health');
    }

    // ===========================================
    // AUTHENTICATION ENDPOINTS
    // ===========================================

    /**
     * Login and get tokens
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise<object>} Token response
     */
    async login(email, password) {
        const response = await this._request('/v1/auth/token', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (response.access_token) {
            this.setAccessToken(response.access_token);
        }
        
        return response;
    }

    /**
     * Generate new API key
     * @returns {Promise<object>} New API key
     */
    async generateApiKey() {
        return this._request('/v1/auth/api-key', {
            method: 'POST'
        });
    }
}

// ===========================================
// VERITY UI INTEGRATION
// ===========================================

class VerityUI {
    constructor(client) {
        this.client = client;
        this.isLoading = false;
    }

    /**
     * Initialize UI components
     */
    init() {
        this._setupFormHandlers();
        this._setupResultsDisplay();
    }

    /**
     * Setup form submission handlers
     */
    _setupFormHandlers() {
        const form = document.querySelector('#verify-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const claimInput = form.querySelector('#claim-input');
                if (claimInput) {
                    await this.verifyClaim(claimInput.value);
                }
            });
        }
    }

    /**
     * Setup results display area
     */
    _setupResultsDisplay() {
        // Create results container if it doesn't exist
        if (!document.querySelector('#verification-results')) {
            const container = document.createElement('div');
            container.id = 'verification-results';
            container.className = 'verification-results';
            document.body.appendChild(container);
        }
    }

    /**
     * Show loading state
     */
    _showLoading() {
        this.isLoading = true;
        const results = document.querySelector('#verification-results');
        if (results) {
            results.innerHTML = `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>Analyzing claim across multiple sources...</p>
                </div>
            `;
        }
    }

    /**
     * Verify a claim and display results
     */
    async verifyClaim(claim) {
        if (!claim || claim.trim().length < 10) {
            this._showError('Please enter a claim with at least 10 characters.');
            return;
        }

        this._showLoading();

        try {
            const result = await this.client.verifyClaimDetailed(claim);
            this._displayResult(result);
        } catch (error) {
            this._showError(error.message);
        }
    }

    /**
     * Display verification result
     */
    _displayResult(result) {
        this.isLoading = false;
        const container = document.querySelector('#verification-results');
        if (!container) return;

        const statusColors = {
            verified_true: '#22c55e',
            verified_false: '#ef4444',
            partially_true: '#f59e0b',
            unverifiable: '#6b7280',
            needs_context: '#3b82f6',
            disputed: '#8b5cf6'
        };

        const statusIcons = {
            verified_true: '✓',
            verified_false: '✗',
            partially_true: '~',
            unverifiable: '?',
            needs_context: 'ℹ',
            disputed: '⚠'
        };

        const color = statusColors[result.status] || '#6b7280';
        const icon = statusIcons[result.status] || '?';

        container.innerHTML = `
            <div class="result-card">
                <div class="result-header">
                    <div class="status-badge" style="background-color: ${color}">
                        <span class="status-icon">${icon}</span>
                        <span class="status-text">${result.status.replace(/_/g, ' ').toUpperCase()}</span>
                    </div>
                    <div class="confidence-score">
                        <span class="score-value">${Math.round(result.confidence_score * 100)}%</span>
                        <span class="score-label">Confidence</span>
                    </div>
                </div>

                <div class="result-claim">
                    <h4>Claim Analyzed:</h4>
                    <p>"${this._escapeHtml(result.claim)}"</p>
                </div>

                <div class="result-summary">
                    <h4>Summary:</h4>
                    <p>${this._escapeHtml(result.summary)}</p>
                </div>

                ${result.warnings && result.warnings.length > 0 ? `
                    <div class="result-warnings">
                        <h4>⚠ Warnings:</h4>
                        <ul>
                            ${result.warnings.map(w => `<li>${this._escapeHtml(w)}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}

                <div class="result-sources">
                    <h4>Sources (${result.sources_count}):</h4>
                    <div class="sources-list">
                        ${result.sources && result.sources.slice(0, 5).map(s => `
                            <div class="source-item">
                                <span class="source-name">${this._escapeHtml(s.name)}</span>
                                <span class="source-credibility ${s.credibility}">${s.credibility}</span>
                                ${s.url ? `<a href="${s.url}" target="_blank" rel="noopener">View →</a>` : ''}
                            </div>
                        `).join('') || '<p>No sources available</p>'}
                    </div>
                </div>

                ${result.fact_checks && result.fact_checks.length > 0 ? `
                    <div class="result-factchecks">
                        <h4>Professional Fact-Checks (${result.fact_checks_count}):</h4>
                        <div class="factchecks-list">
                            ${result.fact_checks.slice(0, 3).map(fc => `
                                <div class="factcheck-item">
                                    <span class="factcheck-publisher">${this._escapeHtml(fc.publisher || 'Unknown')}</span>
                                    <span class="factcheck-rating">${this._escapeHtml(fc.rating || 'N/A')}</span>
                                    ${fc.url ? `<a href="${fc.url}" target="_blank" rel="noopener">Read →</a>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <div class="result-meta">
                    <span>Request ID: ${result.request_id}</span>
                    <span>Processing time: ${result.processing_time_ms.toFixed(0)}ms</span>
                </div>
            </div>
        `;
    }

    /**
     * Show error message
     */
    _showError(message) {
        this.isLoading = false;
        const container = document.querySelector('#verification-results');
        if (container) {
            container.innerHTML = `
                <div class="error-state">
                    <span class="error-icon">✗</span>
                    <p>${this._escapeHtml(message)}</p>
                </div>
            `;
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    _escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// ===========================================
// CSS STYLES FOR RESULTS
// ===========================================

const verityStyles = `
.verification-results {
    max-width: 800px;
    margin: 2rem auto;
    padding: 1rem;
}

.result-card {
    background: var(--card-bg, #ffffff);
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.status-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 9999px;
    color: white;
    font-weight: 600;
}

.status-icon {
    font-size: 1.25rem;
}

.confidence-score {
    text-align: right;
}

.score-value {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary, #3b82f6);
}

.score-label {
    font-size: 0.875rem;
    color: var(--text-secondary, #6b7280);
}

.result-claim, .result-summary, .result-warnings, .result-sources, .result-factchecks {
    margin-bottom: 1.5rem;
}

.result-claim h4, .result-summary h4, .result-warnings h4, .result-sources h4, .result-factchecks h4 {
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary, #6b7280);
    margin-bottom: 0.5rem;
}

.result-warnings {
    background: #fef3c7;
    border-radius: 8px;
    padding: 1rem;
}

.result-warnings ul {
    margin: 0;
    padding-left: 1.5rem;
}

.sources-list, .factchecks-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.source-item, .factcheck-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bg-secondary, #f9fafb);
    border-radius: 8px;
}

.source-credibility {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
}

.source-credibility.high { background: #dcfce7; color: #166534; }
.source-credibility.medium { background: #fef3c7; color: #92400e; }
.source-credibility.low { background: #fee2e2; color: #991b1b; }
.source-credibility.unknown { background: #e5e7eb; color: #374151; }

.source-item a, .factcheck-item a {
    margin-left: auto;
    color: var(--primary, #3b82f6);
    text-decoration: none;
}

.result-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: var(--text-secondary, #6b7280);
    padding-top: 1rem;
    border-top: 1px solid var(--border-color, #e5e7eb);
}

.loading-state, .error-state {
    text-align: center;
    padding: 3rem;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-color, #e5e7eb);
    border-top-color: var(--primary, #3b82f6);
    border-radius: 50%;
    margin: 0 auto 1rem;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.error-state {
    color: #ef4444;
}

.error-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 1rem;
}
`;

// Inject styles
if (typeof document !== 'undefined') {
    const styleSheet = document.createElement('style');
    styleSheet.textContent = verityStyles;
    document.head.appendChild(styleSheet);
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VerityClient, VerityUI };
}

// Make available globally
if (typeof window !== 'undefined') {
    window.VerityClient = VerityClient;
    window.VerityUI = VerityUI;
}
