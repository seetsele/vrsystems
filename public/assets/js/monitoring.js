// ================================================
// VERITY SYSTEMS - CLIENT-SIDE MONITORING
// Error tracking, performance, and diagnostics
// ================================================

(function() {
    'use strict';

    const VerityMonitoring = {
        initialized: false,
        errors: [],
        metrics: [],
        sessionId: null,
        
        // Configuration
        config: {
            endpoint: null, // Set to your monitoring endpoint
            sampleRate: 1.0,
            maxErrors: 100,
            maxMetrics: 500,
            enableConsole: true
        },

        // Initialize monitoring
        init(options = {}) {
            if (this.initialized) return;
            
            Object.assign(this.config, options);
            this.sessionId = this.generateSessionId();
            
            // Setup global error handlers
            this.setupErrorHandlers();
            
            // Collect performance metrics
            this.collectPerformanceMetrics();
            
            // Setup beforeunload to flush data
            window.addEventListener('beforeunload', () => this.flush());
            
            this.initialized = true;
            this.log('Monitoring initialized');
        },

        // Generate session ID
        generateSessionId() {
            return 'mon_' + Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 9);
        },

        // Log to console if enabled
        log(...args) {
            if (this.config.enableConsole) {
                console.log('[VerityMonitor]', ...args);
            }
        },

        // Setup global error handlers
        setupErrorHandlers() {
            // JavaScript errors
            window.onerror = (message, source, lineno, colno, error) => {
                this.captureError({
                    type: 'javascript',
                    message,
                    source,
                    lineno,
                    colno,
                    stack: error?.stack
                });
                return false;
            };

            // Unhandled promise rejections
            window.addEventListener('unhandledrejection', (event) => {
                this.captureError({
                    type: 'unhandled_rejection',
                    message: event.reason?.message || String(event.reason),
                    stack: event.reason?.stack
                });
            });

            // Resource loading errors
            window.addEventListener('error', (event) => {
                if (event.target !== window) {
                    this.captureError({
                        type: 'resource',
                        tagName: event.target?.tagName,
                        src: event.target?.src || event.target?.href,
                        message: 'Failed to load resource'
                    });
                }
            }, true);

            // Network errors (fetch)
            const originalFetch = window.fetch;
            window.fetch = async (...args) => {
                const start = performance.now();
                try {
                    const response = await originalFetch(...args);
                    const duration = performance.now() - start;
                    
                    this.recordMetric('fetch', {
                        url: args[0]?.url || args[0],
                        method: args[0]?.method || 'GET',
                        status: response.status,
                        duration
                    });
                    
                    if (!response.ok) {
                        this.captureError({
                            type: 'fetch',
                            url: args[0]?.url || args[0],
                            status: response.status,
                            statusText: response.statusText
                        });
                    }
                    
                    return response;
                } catch (error) {
                    this.captureError({
                        type: 'network',
                        url: args[0]?.url || args[0],
                        message: error.message
                    });
                    throw error;
                }
            };
        },

        // Capture an error
        captureError(errorInfo) {
            // Sample rate check
            if (Math.random() > this.config.sampleRate) return;
            
            const error = {
                id: this.generateId(),
                sessionId: this.sessionId,
                timestamp: new Date().toISOString(),
                url: window.location.href,
                userAgent: navigator.userAgent,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                ...errorInfo
            };
            
            this.errors.push(error);
            
            // Limit stored errors
            if (this.errors.length > this.config.maxErrors) {
                this.errors.shift();
            }
            
            // Log error
            this.log('Error captured:', error);
            
            // Store in localStorage
            this.storeErrors();
            
            // Send immediately for critical errors
            if (errorInfo.type === 'javascript' || errorInfo.type === 'unhandled_rejection') {
                this.sendErrors();
            }
            
            return error;
        },

        // Record a performance metric
        recordMetric(name, data = {}) {
            const metric = {
                id: this.generateId(),
                sessionId: this.sessionId,
                timestamp: new Date().toISOString(),
                name,
                page: window.location.pathname,
                ...data
            };
            
            this.metrics.push(metric);
            
            // Limit stored metrics
            if (this.metrics.length > this.config.maxMetrics) {
                this.metrics.shift();
            }
        },

        // Collect Web Vitals and performance metrics
        collectPerformanceMetrics() {
            // Navigation timing
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const timing = performance.timing;
                    
                    this.recordMetric('page_load', {
                        dns: timing.domainLookupEnd - timing.domainLookupStart,
                        tcp: timing.connectEnd - timing.connectStart,
                        ttfb: timing.responseStart - timing.requestStart,
                        download: timing.responseEnd - timing.responseStart,
                        domParse: timing.domInteractive - timing.responseEnd,
                        domComplete: timing.domComplete - timing.domInteractive,
                        total: timing.loadEventEnd - timing.navigationStart
                    });
                }, 0);
            });

            // Largest Contentful Paint
            try {
                new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lcp = entries[entries.length - 1];
                    this.recordMetric('lcp', {
                        value: Math.round(lcp.startTime),
                        element: lcp.element?.tagName
                    });
                }).observe({ type: 'largest-contentful-paint', buffered: true });
            } catch (e) {}

            // First Input Delay
            try {
                new PerformanceObserver((list) => {
                    const entry = list.getEntries()[0];
                    this.recordMetric('fid', {
                        value: Math.round(entry.processingStart - entry.startTime)
                    });
                }).observe({ type: 'first-input', buffered: true });
            } catch (e) {}

            // Cumulative Layout Shift
            try {
                let cls = 0;
                new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) {
                            cls += entry.value;
                        }
                    }
                }).observe({ type: 'layout-shift', buffered: true });
                
                // Report CLS on visibility change
                document.addEventListener('visibilitychange', () => {
                    if (document.visibilityState === 'hidden') {
                        this.recordMetric('cls', { value: Math.round(cls * 1000) / 1000 });
                    }
                });
            } catch (e) {}
        },

        // Store errors in localStorage
        storeErrors() {
            try {
                localStorage.setItem('verity_monitoring_errors', JSON.stringify(this.errors));
            } catch (e) {
                // Storage full or disabled
            }
        },

        // Load errors from localStorage
        loadErrors() {
            try {
                const stored = localStorage.getItem('verity_monitoring_errors');
                if (stored) {
                    this.errors = JSON.parse(stored);
                }
            } catch (e) {}
        },

        // Send errors to endpoint
        async sendErrors() {
            if (!this.config.endpoint || this.errors.length === 0) return;
            
            try {
                const errorsToSend = [...this.errors];
                this.errors = [];
                this.storeErrors();
                
                await fetch(this.config.endpoint + '/errors', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ errors: errorsToSend }),
                    keepalive: true
                });
                
                this.log(`Sent ${errorsToSend.length} errors`);
            } catch (e) {
                // Restore errors if send failed
                this.errors = [...this.errors, ...errorsToSend];
            }
        },

        // Send metrics to endpoint
        async sendMetrics() {
            if (!this.config.endpoint || this.metrics.length === 0) return;
            
            try {
                const metricsToSend = [...this.metrics];
                this.metrics = [];
                
                await fetch(this.config.endpoint + '/metrics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ metrics: metricsToSend }),
                    keepalive: true
                });
                
                this.log(`Sent ${metricsToSend.length} metrics`);
            } catch (e) {
                // Restore metrics if send failed
                this.metrics = [...metricsToSend, ...this.metrics];
            }
        },

        // Flush all data
        async flush() {
            await Promise.all([
                this.sendErrors(),
                this.sendMetrics()
            ]);
        },

        // Generate unique ID
        generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
        },

        // Get diagnostic report
        getDiagnostics() {
            return {
                session: this.sessionId,
                errors: this.errors.length,
                metrics: this.metrics.length,
                recentErrors: this.errors.slice(-5),
                recentMetrics: this.metrics.slice(-10),
                browser: {
                    userAgent: navigator.userAgent,
                    language: navigator.language,
                    online: navigator.onLine,
                    cookiesEnabled: navigator.cookieEnabled
                },
                performance: this.getPerformanceSummary()
            };
        },

        // Get performance summary
        getPerformanceSummary() {
            const timing = performance.timing;
            return {
                pageLoadTime: timing.loadEventEnd - timing.navigationStart,
                domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                firstByte: timing.responseStart - timing.requestStart,
                dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
                connectionTime: timing.connectEnd - timing.connectStart
            };
        },

        // Custom event tracking
        trackEvent(name, properties = {}) {
            this.recordMetric('custom_event', {
                eventName: name,
                ...properties
            });
        },

        // Mark a checkpoint
        mark(name) {
            performance.mark(`verity_${name}`);
        },

        // Measure between checkpoints
        measure(name, startMark, endMark) {
            try {
                performance.measure(`verity_${name}`, `verity_${startMark}`, endMark ? `verity_${endMark}` : undefined);
                const entry = performance.getEntriesByName(`verity_${name}`).pop();
                if (entry) {
                    this.recordMetric('custom_measure', {
                        measureName: name,
                        duration: Math.round(entry.duration)
                    });
                }
            } catch (e) {}
        }
    };

    // ================================================
    // HEALTH CHECK MODULE
    // ================================================
    const HealthCheck = {
        checks: [],
        
        // Add a health check
        addCheck(name, fn) {
            this.checks.push({ name, fn });
        },

        // Run all checks
        async runAll() {
            const results = [];
            
            for (const check of this.checks) {
                const start = performance.now();
                try {
                    await check.fn();
                    results.push({
                        name: check.name,
                        status: 'healthy',
                        latency: Math.round(performance.now() - start)
                    });
                } catch (e) {
                    results.push({
                        name: check.name,
                        status: 'unhealthy',
                        error: e.message,
                        latency: Math.round(performance.now() - start)
                    });
                }
            }
            
            return {
                status: results.every(r => r.status === 'healthy') ? 'healthy' : 'unhealthy',
                timestamp: new Date().toISOString(),
                checks: results
            };
        }
    };

    // Default health checks
    HealthCheck.addCheck('localStorage', () => {
        const key = '_health_check';
        localStorage.setItem(key, 'test');
        if (localStorage.getItem(key) !== 'test') throw new Error('Failed');
        localStorage.removeItem(key);
    });

    HealthCheck.addCheck('online', () => {
        if (!navigator.onLine) throw new Error('Offline');
    });

    HealthCheck.addCheck('supabase', async () => {
        if (window.VerityAuth?.isConfigured()) return;
        throw new Error('Not configured');
    });

    // Initialize
    VerityMonitoring.init();

    // Export
    window.VerityMonitoring = VerityMonitoring;
    window.VerityHealthCheck = HealthCheck;

})();
