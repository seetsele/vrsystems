// ================================================
// VERITY SYSTEMS - ONBOARDING FLOW
// Interactive product tour for new users
// ================================================

(function() {
    'use strict';

    const Onboarding = {
        currentStep: 0,
        steps: [],
        overlay: null,
        tooltip: null,
        
        // Check if user is new
        isNewUser() {
            return !localStorage.getItem('verity_onboarding_complete');
        },

        // Check if should show onboarding
        shouldShow() {
            const params = new URLSearchParams(window.location.search);
            return this.isNewUser() && (params.get('welcome') === '1' || params.get('onboarding') === '1');
        },

        // Initialize onboarding
        init() {
            if (!this.shouldShow()) return;
            
            // Wait a moment for page to fully render
            setTimeout(() => this.start(), 1000);
        },

        // Start the onboarding flow
        start() {
            this.createOverlay();
            this.createTooltip();
            this.defineSteps();
            this.showStep(0);
            
            // Track analytics
            if (window.VerityCore?.Analytics) {
                window.VerityCore.Analytics.track('onboarding_started');
            }
        },

        // Define onboarding steps based on current page
        defineSteps() {
            const page = window.location.pathname;
            
            if (page.includes('dashboard')) {
                this.steps = [
                    {
                        title: 'Welcome to Verity! 🎉',
                        content: 'Let\'s take a quick tour of your dashboard and show you how to verify claims in under 2 minutes.',
                        target: null,
                        position: 'center'
                    },
                    {
                        title: 'Quick Verify',
                        content: 'This is your command center. Type any claim here and get instant AI-powered verification.',
                        target: '.verify-card',
                        position: 'bottom'
                    },
                    {
                        title: 'Your Stats',
                        content: 'Track your verification activity, accuracy rate, and misinformation detected at a glance.',
                        target: '.stats-grid',
                        position: 'bottom'
                    },
                    {
                        title: 'Recent Activity',
                        content: 'See your verification history with real-time verdicts and confidence scores.',
                        target: '.recent-card',
                        position: 'right'
                    },
                    {
                        title: 'Quick Actions',
                        content: 'Access advanced tools like batch verification, source checking, and the live misinformation stream.',
                        target: '.actions-card',
                        position: 'left'
                    },
                    {
                        title: 'API Keys',
                        content: 'Generate API keys to integrate Verity into your apps, workflows, and Chrome extension.',
                        target: 'a[href="api-keys.html"]',
                        position: 'right'
                    },
                    {
                        title: 'You\'re All Set! 🚀',
                        content: 'Try verifying your first claim now. Need help? Check our docs or contact support anytime.',
                        target: null,
                        position: 'center'
                    }
                ];
            } else if (page.includes('verify')) {
                this.steps = [
                    {
                        title: 'Full Verification Suite',
                        content: 'This is where the magic happens. Get our 21-point verification with detailed analysis.',
                        target: null,
                        position: 'center'
                    },
                    {
                        title: 'Enter Your Claim',
                        content: 'Paste any claim, statement, or URL. Our AI analyzes it against 40+ trusted sources.',
                        target: '.verify-input, textarea',
                        position: 'bottom'
                    },
                    {
                        title: 'Verification Options',
                        content: 'Choose verification depth: Quick (3 models), Standard (5 models), or Deep (10+ models).',
                        target: '.verification-options, .options',
                        position: 'bottom'
                    }
                ];
            } else {
                // Generic welcome for other pages
                this.steps = [
                    {
                        title: 'Welcome to Verity! 🎉',
                        content: 'Your AI-powered fact-checking companion. Verify claims instantly with 20+ AI models and 40+ trusted sources.',
                        target: null,
                        position: 'center'
                    }
                ];
            }
        },

        // Create overlay backdrop
        createOverlay() {
            this.overlay = document.createElement('div');
            this.overlay.id = 'verity-onboarding-overlay';
            this.overlay.style.cssText = `
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.75);
                z-index: 99998;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            document.body.appendChild(this.overlay);
            
            // Fade in
            requestAnimationFrame(() => {
                this.overlay.style.opacity = '1';
            });
        },

        // Create tooltip element
        createTooltip() {
            this.tooltip = document.createElement('div');
            this.tooltip.id = 'verity-onboarding-tooltip';
            this.tooltip.style.cssText = `
                position: fixed;
                z-index: 99999;
                background: #111113;
                border: 1px solid rgba(245, 158, 11, 0.3);
                border-radius: 16px;
                padding: 1.5rem;
                max-width: 340px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                opacity: 0;
                transform: scale(0.9);
                transition: all 0.3s ease;
            `;
            document.body.appendChild(this.tooltip);
        },

        // Show a specific step
        showStep(index) {
            if (index >= this.steps.length) {
                this.complete();
                return;
            }

            this.currentStep = index;
            const step = this.steps[index];
            
            // Remove previous highlight
            document.querySelectorAll('.verity-highlight').forEach(el => {
                el.classList.remove('verity-highlight');
            });
            
            // Highlight target element
            let targetRect = null;
            if (step.target) {
                const target = document.querySelector(step.target);
                if (target) {
                    target.classList.add('verity-highlight');
                    target.style.position = 'relative';
                    target.style.zIndex = '99999';
                    targetRect = target.getBoundingClientRect();
                    
                    // Scroll into view
                    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }

            // Update tooltip content
            this.tooltip.innerHTML = `
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: #a3a3a3; font-size: 0.8rem;">Step ${index + 1} of ${this.steps.length}</span>
                </div>
                <h3 style="font-size: 1.1rem; font-weight: 600; color: #fafafa; margin-bottom: 0.75rem;">${step.title}</h3>
                <p style="color: #a3a3a3; font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.5rem;">${step.content}</p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <button id="onboarding-skip" style="
                        background: none;
                        border: none;
                        color: #525252;
                        font-size: 0.85rem;
                        cursor: pointer;
                        padding: 0.5rem;
                    ">Skip Tour</button>
                    <div style="display: flex; gap: 0.5rem;">
                        ${index > 0 ? `
                            <button id="onboarding-prev" style="
                                background: #18181b;
                                border: 1px solid rgba(255,255,255,0.1);
                                color: #fafafa;
                                padding: 0.6rem 1rem;
                                border-radius: 8px;
                                font-size: 0.85rem;
                                cursor: pointer;
                            ">← Back</button>
                        ` : ''}
                        <button id="onboarding-next" style="
                            background: linear-gradient(135deg, #f59e0b, #d97706);
                            border: none;
                            color: #000;
                            padding: 0.6rem 1.25rem;
                            border-radius: 8px;
                            font-size: 0.85rem;
                            font-weight: 600;
                            cursor: pointer;
                        ">${index === this.steps.length - 1 ? 'Get Started' : 'Next →'}</button>
                    </div>
                </div>
                <div style="display: flex; justify-content: center; gap: 0.35rem; margin-top: 1rem;">
                    ${this.steps.map((_, i) => `
                        <div style="
                            width: 8px;
                            height: 8px;
                            border-radius: 50%;
                            background: ${i === index ? '#f59e0b' : '#333'};
                            transition: background 0.3s;
                        "></div>
                    `).join('')}
                </div>
            `;

            // Position tooltip
            this.positionTooltip(step.position, targetRect);
            
            // Show tooltip
            requestAnimationFrame(() => {
                this.tooltip.style.opacity = '1';
                this.tooltip.style.transform = 'scale(1)';
            });

            // Wire up buttons
            this.tooltip.querySelector('#onboarding-skip')?.addEventListener('click', () => this.complete());
            this.tooltip.querySelector('#onboarding-prev')?.addEventListener('click', () => this.showStep(index - 1));
            this.tooltip.querySelector('#onboarding-next')?.addEventListener('click', () => this.showStep(index + 1));
        },

        // Position tooltip relative to target
        positionTooltip(position, targetRect) {
            const tooltip = this.tooltip;
            const padding = 20;
            
            if (position === 'center' || !targetRect) {
                tooltip.style.top = '50%';
                tooltip.style.left = '50%';
                tooltip.style.transform = 'translate(-50%, -50%) scale(1)';
                return;
            }

            const tooltipRect = tooltip.getBoundingClientRect();
            let top, left;

            switch (position) {
                case 'bottom':
                    top = targetRect.bottom + padding;
                    left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
                    break;
                case 'top':
                    top = targetRect.top - tooltipRect.height - padding;
                    left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
                    break;
                case 'right':
                    top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
                    left = targetRect.right + padding;
                    break;
                case 'left':
                    top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
                    left = targetRect.left - tooltipRect.width - padding;
                    break;
            }

            // Keep in viewport
            left = Math.max(padding, Math.min(left, window.innerWidth - tooltipRect.width - padding));
            top = Math.max(padding, Math.min(top, window.innerHeight - tooltipRect.height - padding));

            tooltip.style.top = `${top}px`;
            tooltip.style.left = `${left}px`;
            tooltip.style.transform = 'scale(1)';
        },

        // Complete onboarding
        complete() {
            localStorage.setItem('verity_onboarding_complete', 'true');
            
            // Track analytics
            if (window.VerityCore?.Analytics) {
                window.VerityCore.Analytics.track('onboarding_completed', {
                    stepsViewed: this.currentStep + 1,
                    totalSteps: this.steps.length
                });
            }
            
            // Clean up
            document.querySelectorAll('.verity-highlight').forEach(el => {
                el.classList.remove('verity-highlight');
                el.style.position = '';
                el.style.zIndex = '';
            });
            
            // Fade out
            this.overlay.style.opacity = '0';
            this.tooltip.style.opacity = '0';
            this.tooltip.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                this.overlay.remove();
                this.tooltip.remove();
            }, 300);
            
            // Show success toast
            if (window.VerityCore?.Toast) {
                window.VerityCore.Toast.success('You\'re all set! Start verifying claims now.');
            }
        },

        // Restart onboarding
        restart() {
            localStorage.removeItem('verity_onboarding_complete');
            this.currentStep = 0;
            this.start();
        }
    };

    // Add highlight styles
    const styles = document.createElement('style');
    styles.textContent = `
        .verity-highlight {
            box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.5), 0 0 30px rgba(245, 158, 11, 0.3) !important;
            border-radius: 12px !important;
        }
    `;
    document.head.appendChild(styles);

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => Onboarding.init());
    } else {
        Onboarding.init();
    }

    // Export to global scope
    window.VerityOnboarding = Onboarding;

})();
