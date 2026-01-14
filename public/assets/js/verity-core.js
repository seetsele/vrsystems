// ================================================
// VERITY SYSTEMS - CORE UTILITIES
// Implements: Error Handling, Analytics, Monitoring
// ================================================

(function() {
    'use strict';

    // ================================================
    // 1. GLOBAL ERROR HANDLING & USER-FRIENDLY MESSAGES
    // ================================================
    const ErrorHandler = {
        // Map technical errors to user-friendly messages
        errorMap: {
            // Network errors
            'Failed to fetch': 'Connection lost. Please check your internet and try again.',
            'NetworkError': 'Network error. Please check your connection.',
            'AbortError': 'Request timed out. Please try again.',
            
            // Auth errors
            'Invalid login credentials': 'Invalid email or password. Please try again.',
            'Email not confirmed': 'Please verify your email before signing in.',
            'User already registered': 'An account with this email already exists.',
            'Password should be at least': 'Password must be at least 8 characters.',
            'JWT expired': 'Your session has expired. Please sign in again.',
            'Token expired': 'Your session has expired. Please sign in again.',
            'PGRST301': 'Your session has expired. Please sign in again.',
            'Too many requests': 'Too many attempts. Please wait a moment before trying again.',
            
            // API errors
            'Rate limit exceeded': 'You\'ve made too many requests. Please wait a moment.',
            'Unauthorized': 'Please sign in to continue.',
            'Forbidden': 'You don\'t have permission to perform this action.',
            'Not found': 'The requested resource was not found.',
            'Server error': 'Something went wrong on our end. We\'re working on it.',
            '500': 'Our servers are having issues. Please try again later.',
            '502': 'Our servers are temporarily unavailable. Please try again.',
            '503': 'Service temporarily unavailable. Please try again shortly.',
            
            // Verification errors
            'No claim provided': 'Please enter a claim to verify.',
            'Invalid claim format': 'Please enter a valid text claim.',
            'Provider unavailable': 'AI provider temporarily unavailable. Using backup.',
        },

        // Get user-friendly message
        getUserMessage(error) {
            const errorString = typeof error === 'string' ? error : error?.message || String(error);
            
            for (const [key, message] of Object.entries(this.errorMap)) {
                if (errorString.includes(key)) {
                    return message;
                }
            }
            
            // Default messages based on error type
            if (errorString.includes('network') || errorString.includes('fetch')) {
                return 'Connection error. Please check your internet.';
            }
            if (errorString.includes('auth') || errorString.includes('login')) {
                return 'Authentication error. Please try again.';
            }
            
            return 'Something went wrong. Please try again.';
        },

        // Log error to monitoring service
        logError(error, context = {}) {
            const errorInfo = {
                message: error?.message || String(error),
                stack: error?.stack,
                context,
                timestamp: new Date().toISOString(),
                url: window.location.href,
                userAgent: navigator.userAgent
            };
            
            console.error('[Verity Error]', errorInfo);
            
            // Send to monitoring service (Sentry-style)
            if (window.VerityMonitoring?.captureError) {
                window.VerityMonitoring.captureError(errorInfo);
            }
            
            // Store locally for debugging
            this.storeLocalError(errorInfo);
        },

        // Store errors locally (last 50)
        storeLocalError(errorInfo) {
            try {
                const errors = JSON.parse(localStorage.getItem('verity_errors') || '[]');
                errors.unshift(errorInfo);
                if (errors.length > 50) errors.pop();
                localStorage.setItem('verity_errors', JSON.stringify(errors));
            } catch (e) {
                // Ignore storage errors
            }
        },

        // Get stored errors
        getStoredErrors() {
            try {
                return JSON.parse(localStorage.getItem('verity_errors') || '[]');
            } catch (e) {
                return [];
            }
        }
    };

    // Global error handler
    window.onerror = function(message, source, lineno, colno, error) {
        ErrorHandler.logError(error || message, { source, lineno, colno });
        return false;
    };

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', function(event) {
        ErrorHandler.logError(event.reason, { type: 'unhandledrejection' });
    });

    // ================================================
    // 2. TOAST NOTIFICATION SYSTEM
    // ================================================
    const Toast = {
        container: null,

        init() {
            if (this.container) return;
            
            this.container = document.createElement('div');
            this.container.id = 'verity-toast-container';
            this.container.style.cssText = `
                position: fixed;
                bottom: 2rem;
                right: 2rem;
                z-index: 100000;
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                pointer-events: none;
            `;
            document.body.appendChild(this.container);
        },

        show(message, type = 'info', duration = 5000) {
            this.init();
            
            const colors = {
                success: { bg: '#10b981', text: '#fff' },
                error: { bg: '#ef4444', text: '#fff' },
                warning: { bg: '#f59e0b', text: '#000' },
                info: { bg: '#3b82f6', text: '#fff' }
            };
            
            const icons = {
                success: '✓',
                error: '✕',
                warning: '⚠',
                info: 'ℹ'
            };
            
            const color = colors[type] || colors.info;
            
            const toast = document.createElement('div');
            toast.style.cssText = `
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 1rem 1.5rem;
                background: ${color.bg};
                color: ${color.text};
                border-radius: 12px;
                font-weight: 500;
                font-size: 0.9rem;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                pointer-events: auto;
                animation: toastSlideIn 0.3s ease;
                max-width: 400px;
            `;
            
            toast.innerHTML = `
                <span style="font-size: 1.2rem;">${icons[type]}</span>
                <span>${message}</span>
                <button onclick="this.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: ${color.text};
                    font-size: 1.2rem;
                    cursor: pointer;
                    padding: 0 0.25rem;
                    opacity: 0.7;
                ">×</button>
            `;
            
            this.container.appendChild(toast);
            
            // Auto remove
            setTimeout(() => {
                toast.style.animation = 'toastSlideOut 0.3s ease forwards';
                setTimeout(() => toast.remove(), 300);
            }, duration);
            
            return toast;
        },

        success(message, duration) { return this.show(message, 'success', duration); },
        error(message, duration) { return this.show(message, 'error', duration); },
        warning(message, duration) { return this.show(message, 'warning', duration); },
        info(message, duration) { return this.show(message, 'info', duration); }
    };

    // Add toast animations
    const toastStyles = document.createElement('style');
    toastStyles.textContent = `
        @keyframes toastSlideIn {
            from { transform: translateX(100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes toastSlideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100px); opacity: 0; }
        }
    `;
    document.head.appendChild(toastStyles);

    // ================================================
    // 3. RETRY LOGIC WITH EXPONENTIAL BACKOFF
    // ================================================
    const RetryHandler = {
        async retry(fn, options = {}) {
            const {
                maxRetries = 3,
                baseDelay = 1000,
                maxDelay = 10000,
                shouldRetry = (error) => true
            } = options;
            
            let lastError;
            
            for (let attempt = 0; attempt <= maxRetries; attempt++) {
                try {
                    return await fn();
                } catch (error) {
                    lastError = error;
                    
                    if (attempt === maxRetries || !shouldRetry(error)) {
                        throw error;
                    }
                    
                    // Exponential backoff with jitter
                    const delay = Math.min(
                        baseDelay * Math.pow(2, attempt) + Math.random() * 1000,
                        maxDelay
                    );
                    
                    (window.verityLogger || console).info(`Retry attempt ${attempt + 1}/${maxRetries} in ${delay}ms`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
            
            throw lastError;
        },

        // Check if error is retryable
        isRetryable(error) {
            const nonRetryableErrors = [
                'Invalid login credentials',
                'User already registered',
                'Unauthorized',
                'Forbidden'
            ];
            
            const errorString = String(error?.message || error);
            return !nonRetryableErrors.some(e => errorString.includes(e));
        }
    };

    // ================================================
    // 4. ANALYTICS TRACKING
    // ================================================
    const Analytics = {
        enabled: true,
        queue: [],
        sessionId: null,

        init() {
            this.sessionId = this.getOrCreateSessionId();
            this.trackPageView();
            this.setupEventListeners();
            this.flushQueue();
        },

        getOrCreateSessionId() {
            let sessionId = sessionStorage.getItem('verity_session_id');
            if (!sessionId) {
                sessionId = 'vs_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                sessionStorage.setItem('verity_session_id', sessionId);
            }
            return sessionId;
        },

        track(eventName, properties = {}) {
            if (!this.enabled) return;
            
            const event = {
                event: eventName,
                properties: {
                    ...properties,
                    sessionId: this.sessionId,
                    timestamp: new Date().toISOString(),
                    page: window.location.pathname,
                    referrer: document.referrer,
                    screenWidth: window.innerWidth,
                    screenHeight: window.innerHeight
                }
            };
            
            // Store locally
            this.queue.push(event);
            this.storeEvent(event);
            
            // Log in development
            if (window.location.hostname === 'localhost') {
                (window.verityLogger || console).info('[Analytics]', eventName, properties);
            }
        },

        trackPageView() {
            this.track('page_view', {
                title: document.title,
                url: window.location.href
            });
        },

        setupEventListeners() {
            // Track verification attempts
            document.addEventListener('verification:start', (e) => {
                this.track('verification_started', e.detail);
            });
            
            document.addEventListener('verification:complete', (e) => {
                this.track('verification_completed', e.detail);
            });
            
            // Track auth events
            document.addEventListener('auth:signin', (e) => {
                this.track('user_signin', { method: e.detail?.method });
            });
            
            document.addEventListener('auth:signup', (e) => {
                this.track('user_signup', { method: e.detail?.method });
            });
            
            // Track feature usage
            document.addEventListener('feature:used', (e) => {
                this.track('feature_used', e.detail);
            });
        },

        storeEvent(event) {
            try {
                const events = JSON.parse(localStorage.getItem('verity_analytics') || '[]');
                events.push(event);
                // Keep last 200 events
                if (events.length > 200) events.shift();
                localStorage.setItem('verity_analytics', JSON.stringify(events));
            } catch (e) {
                // Ignore storage errors
            }
        },

        getStoredEvents() {
            try {
                return JSON.parse(localStorage.getItem('verity_analytics') || '[]');
            } catch (e) {
                return [];
            }
        },

        async flushQueue() {
            // In production, send to analytics endpoint
            if (this.queue.length > 0 && window.VERITY_ANALYTICS_ENDPOINT) {
                try {
                    await fetch(window.VERITY_ANALYTICS_ENDPOINT, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ events: this.queue })
                    });
                    this.queue = [];
                } catch (e) {
                    // Will retry on next flush
                }
            }
        }
    };

    // ================================================
    // 5. PERFORMANCE MONITORING
    // ================================================
    const Performance = {
        marks: {},

        mark(name) {
            this.marks[name] = performance.now();
        },

        measure(name, startMark) {
            const start = this.marks[startMark];
            if (!start) return null;
            
            const duration = performance.now() - start;
            Analytics.track('performance_measure', { name, duration });
            return duration;
        },

        getWebVitals() {
            return {
                navigationStart: performance.timing?.navigationStart,
                domContentLoaded: performance.timing?.domContentLoadedEventEnd - performance.timing?.navigationStart,
                loadComplete: performance.timing?.loadEventEnd - performance.timing?.navigationStart
            };
        },

        trackWebVitals() {
            if (typeof PerformanceObserver === 'undefined') return;
            
            // Track Largest Contentful Paint
            try {
                new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lcp = entries[entries.length - 1];
                    Analytics.track('web_vital', { metric: 'LCP', value: lcp.startTime });
                }).observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {}
            
            // Track First Input Delay
            try {
                new PerformanceObserver((list) => {
                    const entry = list.getEntries()[0];
                    Analytics.track('web_vital', { metric: 'FID', value: entry.processingStart - entry.startTime });
                }).observe({ entryTypes: ['first-input'] });
            } catch (e) {}
            
            // Track Cumulative Layout Shift
            try {
                let cls = 0;
                new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) {
                            cls += entry.value;
                        }
                    }
                    Analytics.track('web_vital', { metric: 'CLS', value: cls });
                }).observe({ entryTypes: ['layout-shift'] });
            } catch (e) {}
        }
    };

    // ================================================
    // 6. OFFLINE SUPPORT
    // ================================================
    const OfflineQueue = {
        queue: [],
        isOnline: navigator.onLine,

        init() {
            // Load saved queue
            this.queue = JSON.parse(localStorage.getItem('verity_offline_queue') || '[]');
            
            // Listen for online/offline events
            window.addEventListener('online', () => {
                this.isOnline = true;
                Toast.success('You\'re back online!');
                this.processQueue();
            });
            
            window.addEventListener('offline', () => {
                this.isOnline = false;
                Toast.warning('You\'re offline. Actions will be saved.');
            });
        },

        add(action) {
            if (this.isOnline) {
                return false; // Don't queue, execute normally
            }
            
            this.queue.push({
                ...action,
                timestamp: Date.now()
            });
            
            this.save();
            Toast.info('Action saved for when you\'re back online.');
            return true;
        },

        save() {
            localStorage.setItem('verity_offline_queue', JSON.stringify(this.queue));
        },

        async processQueue() {
            while (this.queue.length > 0) {
                const action = this.queue.shift();
                
                try {
                    // Process based on action type
                    switch (action.type) {
                        case 'verification':
                            await window.VerityAPI?.verify(action.data);
                            break;
                        case 'save_favorite':
                            await window.VerityAPI?.saveFavorite(action.data);
                            break;
                    }
                    
                    this.save();
                } catch (e) {
                    // Re-add to queue if failed
                    this.queue.unshift(action);
                    this.save();
                    break;
                }
            }
        }
    };

    // ================================================
    // 7. LOADING STATES
    // ================================================
    const LoadingState = {
        show(element, message = 'Loading...') {
            if (!element) return;
            
            element.dataset.originalContent = element.innerHTML;
            element.dataset.originalDisabled = element.disabled;
            element.disabled = true;
            element.style.opacity = '0.7';
            element.innerHTML = `
                <svg class="verity-spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" stroke-dasharray="60" stroke-dashoffset="20"/>
                </svg>
                <span>${message}</span>
            `;
        },

        hide(element) {
            if (!element || !element.dataset.originalContent) return;
            
            element.innerHTML = element.dataset.originalContent;
            element.disabled = element.dataset.originalDisabled === 'true';
            element.style.opacity = '1';
            delete element.dataset.originalContent;
            delete element.dataset.originalDisabled;
        }
    };

    // Add spinner animation
    const spinnerStyles = document.createElement('style');
    spinnerStyles.textContent = `
        .verity-spinner {
            animation: veritySpin 1s linear infinite;
        }
        @keyframes veritySpin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(spinnerStyles);

    // ================================================
    // 8. LOCAL STORAGE UTILITIES
    // ================================================
    const Storage = {
        set(key, value, expiresInMinutes = null) {
            const item = {
                value,
                timestamp: Date.now(),
                expires: expiresInMinutes ? Date.now() + expiresInMinutes * 60 * 1000 : null
            };
            localStorage.setItem(`verity_${key}`, JSON.stringify(item));
        },

        get(key) {
            try {
                const item = JSON.parse(localStorage.getItem(`verity_${key}`));
                if (!item) return null;
                
                if (item.expires && Date.now() > item.expires) {
                    localStorage.removeItem(`verity_${key}`);
                    return null;
                }
                
                return item.value;
            } catch (e) {
                return null;
            }
        },

        remove(key) {
            localStorage.removeItem(`verity_${key}`);
        },

        clear() {
            Object.keys(localStorage)
                .filter(k => k.startsWith('verity_'))
                .forEach(k => localStorage.removeItem(k));
        }
    };

    // ================================================
    // INITIALIZE ON DOM READY
    // ================================================
    function init() {
        Analytics.init();
        OfflineQueue.init();
        Performance.trackWebVitals();
        
        (window.verityLogger || console).info('✅ Verity Core initialized');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ================================================
    // EXPORT TO GLOBAL SCOPE
    // ================================================
    window.VerityCore = {
        ErrorHandler,
        Toast,
        RetryHandler,
        Analytics,
        Performance,
        OfflineQueue,
        LoadingState,
        Storage
    };

})();
