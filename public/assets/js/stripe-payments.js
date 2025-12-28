// ================================================
// VERITY SYSTEMS - STRIPE PAYMENT HANDLER
// Frontend JavaScript for handling Stripe checkout
// ================================================

const VerityPayments = {
    API_BASE: window.location.hostname === 'localhost' 
        ? 'http://localhost:8081' 
        : 'https://api.verity-systems.com',
    
    stripeConfig: null,
    
    /**
     * Initialize Stripe configuration from API
     */
    async init() {
        try {
            const response = await fetch(`${this.API_BASE}/stripe/config`);
            if (response.ok) {
                this.stripeConfig = await response.json();
                console.log('✅ Stripe config loaded');
            }
        } catch (error) {
            console.error('Failed to load Stripe config:', error);
        }
    },
    
    /**
     * Handle pricing button clicks
     * @param {string} tier - The pricing tier: free, starter, professional, business, enterprise
     * @param {string} email - Optional customer email
     */
    async handlePricingClick(tier, email = null) {
        tier = tier.toLowerCase();
        
        // Show loading state
        this.showLoading(tier);
        
        try {
            // Handle free tier - direct signup
            if (tier === 'free') {
                window.location.href = '/auth.html?signup=true&plan=free';
                return;
            }
            
            // Handle enterprise tier - contact sales
            if (tier === 'enterprise') {
                this.showEnterpriseModal();
                return;
            }
            
            // For paid tiers, create checkout session
            const response = await fetch(`${this.API_BASE}/stripe/create-checkout-session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    tier: tier,
                    user_email: email,
                    success_url: `${window.location.origin}/success`,
                    cancel_url: `${window.location.origin}/#pricing`
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'checkout_created' && data.url) {
                // Redirect to Stripe Checkout
                window.location.href = data.url;
            } else if (data.status === 'contact_sales') {
                this.showEnterpriseModal();
            } else if (data.status === 'free_tier') {
                window.location.href = data.redirect_url || '/dashboard?plan=free';
            } else {
                throw new Error(data.detail || 'Failed to create checkout session');
            }
            
        } catch (error) {
            console.error('Payment error:', error);
            this.showError('Unable to process payment. Please try again or contact support.');
        } finally {
            this.hideLoading(tier);
        }
    },
    
    /**
     * Show enterprise contact modal
     */
    showEnterpriseModal() {
        // Check if modal already exists
        let modal = document.getElementById('enterpriseModal');
        if (!modal) {
            modal = this.createEnterpriseModal();
            document.body.appendChild(modal);
        }
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    },
    
    /**
     * Create enterprise contact modal HTML
     */
    createEnterpriseModal() {
        const modal = document.createElement('div');
        modal.id = 'enterpriseModal';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content enterprise-modal">
                <button class="modal-close" onclick="VerityPayments.closeModal()">&times;</button>
                <div class="modal-header">
                    <svg class="modal-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 21h18M5 21V7l7-4 7 4v14M9 21v-6h6v6"/>
                    </svg>
                    <h2>Enterprise Solutions</h2>
                    <p>Custom pricing for platforms at scale</p>
                </div>
                <form id="enterpriseForm" class="enterprise-form" onsubmit="VerityPayments.submitEnterpriseForm(event)">
                    <div class="form-group">
                        <label for="entName">Full Name *</label>
                        <input type="text" id="entName" name="name" required minlength="2" placeholder="John Smith">
                    </div>
                    <div class="form-group">
                        <label for="entEmail">Work Email *</label>
                        <input type="email" id="entEmail" name="email" required placeholder="john@company.com">
                    </div>
                    <div class="form-group">
                        <label for="entCompany">Company *</label>
                        <input type="text" id="entCompany" name="company" required minlength="2" placeholder="Acme Inc.">
                    </div>
                    <div class="form-group">
                        <label for="entVolume">Estimated Monthly Verifications</label>
                        <select id="entVolume" name="estimated_volume">
                            <option value="">Select volume...</option>
                            <option value="300k-500k">300,000 - 500,000</option>
                            <option value="500k-1m">500,000 - 1,000,000</option>
                            <option value="1m-5m">1,000,000 - 5,000,000</option>
                            <option value="5m+">5,000,000+</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="entMessage">Tell us about your use case</label>
                        <textarea id="entMessage" name="message" rows="3" placeholder="We're building a platform that..."></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <span>Contact Sales</span>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M5 12h14M12 5l7 7-7 7"/>
                            </svg>
                        </button>
                    </div>
                    <p class="form-note">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M12 16v-4M12 8h.01"/>
                        </svg>
                        We typically respond within 24 hours
                    </p>
                </form>
            </div>
        `;
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });
        
        return modal;
    },
    
    /**
     * Submit enterprise contact form
     */
    async submitEnterpriseForm(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Show loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <svg class="spinner" width="20" height="20" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" opacity="0.25"/>
                <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round"/>
            </svg>
            <span>Sending...</span>
        `;
        
        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const response = await fetch(`${this.API_BASE}/stripe/contact-sales`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Show success message
                form.innerHTML = `
                    <div class="success-message">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M9 12l2 2 4-4"/>
                        </svg>
                        <h3>Thank You!</h3>
                        <p>${result.message}</p>
                        <p class="reference">Reference: ${result.reference_id}</p>
                        <button type="button" class="btn btn-outline" onclick="VerityPayments.closeModal()">Close</button>
                    </div>
                `;
            } else {
                throw new Error(result.detail || 'Failed to submit form');
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            this.showError('Failed to submit form. Please try again or email enterprise@verity-systems.com');
        }
    },
    
    /**
     * Close modal
     */
    closeModal() {
        const modal = document.getElementById('enterpriseModal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    },
    
    /**
     * Show loading state on button
     */
    showLoading(tier) {
        const btn = document.querySelector(`[data-tier="${tier}"]`);
        if (btn) {
            btn.dataset.originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = `
                <svg class="spinner" width="20" height="20" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" opacity="0.25"/>
                    <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round"/>
                </svg>
            `;
        }
    },
    
    /**
     * Hide loading state on button
     */
    hideLoading(tier) {
        const btn = document.querySelector(`[data-tier="${tier}"]`);
        if (btn && btn.dataset.originalText) {
            btn.disabled = false;
            btn.innerHTML = btn.dataset.originalText;
        }
    },
    
    /**
     * Show error message
     */
    showError(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast toast-error';
        toast.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M15 9l-6 6M9 9l6 6"/>
            </svg>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    VerityPayments.init();
});

// Add modal and toast styles
const paymentStyles = document.createElement('style');
paymentStyles.textContent = `
    .modal-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(4px);
        z-index: 10000;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    .modal-content {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        max-width: 500px;
        width: 100%;
        max-height: 90vh;
        overflow-y: auto;
        position: relative;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    
    .modal-close {
        position: absolute;
        top: 16px;
        right: 16px;
        background: none;
        border: none;
        color: #94a3b8;
        font-size: 28px;
        cursor: pointer;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .modal-close:hover {
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .modal-header {
        text-align: center;
        padding: 32px 32px 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .modal-icon {
        color: #6366f1;
        margin-bottom: 16px;
    }
    
    .modal-header h2 {
        font-size: 24px;
        font-weight: 700;
        margin: 0 0 8px;
        color: white;
    }
    
    .modal-header p {
        color: #94a3b8;
        margin: 0;
    }
    
    .enterprise-form {
        padding: 24px 32px 32px;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    .form-group label {
        display: block;
        font-size: 14px;
        font-weight: 500;
        color: #e2e8f0;
        margin-bottom: 8px;
    }
    
    .form-group input,
    .form-group select,
    .form-group textarea {
        width: 100%;
        padding: 12px 16px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        color: white;
        font-size: 15px;
        transition: all 0.2s;
    }
    
    .form-group input:focus,
    .form-group select:focus,
    .form-group textarea:focus {
        outline: none;
        border-color: #6366f1;
        background: rgba(99, 102, 241, 0.1);
    }
    
    .form-group input::placeholder,
    .form-group textarea::placeholder {
        color: #64748b;
    }
    
    .form-group select {
        cursor: pointer;
    }
    
    .form-group select option {
        background: #1a1a2e;
        color: white;
    }
    
    .form-actions {
        margin-top: 24px;
    }
    
    .form-actions .btn {
        width: 100%;
        justify-content: center;
    }
    
    .form-note {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-top: 16px;
        font-size: 13px;
        color: #64748b;
    }
    
    .success-message {
        text-align: center;
        padding: 20px 0;
    }
    
    .success-message svg {
        margin-bottom: 16px;
    }
    
    .success-message h3 {
        font-size: 24px;
        color: white;
        margin: 0 0 12px;
    }
    
    .success-message p {
        color: #94a3b8;
        margin: 0 0 8px;
    }
    
    .success-message .reference {
        font-family: monospace;
        font-size: 12px;
        color: #64748b;
        margin-bottom: 24px;
    }
    
    .spinner {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .toast {
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: #1e293b;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        color: white;
        font-size: 14px;
        z-index: 10001;
        transform: translateY(100px);
        opacity: 0;
        transition: all 0.3s ease;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }
    
    .toast.show {
        transform: translateY(0);
        opacity: 1;
    }
    
    .toast-error {
        border-color: rgba(239, 68, 68, 0.5);
    }
    
    .toast-error svg {
        color: #ef4444;
    }
`;
document.head.appendChild(paymentStyles);
