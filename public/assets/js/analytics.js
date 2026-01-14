/**
 * Verity Analytics - Comprehensive Analytics Integration
 * Tracks user behavior, verification patterns, and system performance
 */

class VerityAnalytics {
  private endpoint = 'https://veritysystems-production.up.railway.app/api/v1/analytics';
  private sessionId = '';
  private userId = '';
  private queue = [];
  private isEnabled = true;
  private flushInterval = null;
  private pageStartTime = 0;
  private interactions = 0;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.pageStartTime = Date.now();
    this.initialize();
  }

  /**
   * Initialize analytics
   */
  initialize() {
    // Load user preference
    const disabled = localStorage.getItem('verity_analytics_disabled');
    this.isEnabled = disabled !== 'true';

    // Get or create user ID
    this.userId = localStorage.getItem('verity_user_id') || this.generateUserId();
    localStorage.setItem('verity_user_id', this.userId);

    // Track page view
    this.trackPageView();

    // Set up flush interval (every 30 seconds)
    this.flushInterval = setInterval(() => this.flush(), 30000);

    // Track page unload
    window.addEventListener('beforeunload', () => {
      this.trackPageLeave();
      this.flush(true);
    });

    // Track visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        this.trackEvent('page_hidden');
      } else {
        this.trackEvent('page_visible');
      }
    });

    // Track clicks for interaction counting
    document.addEventListener('click', () => {
      this.interactions++;
    });

    (window.verityLogger || console).info('Verity Analytics initialized', { sessionId: this.sessionId });
  }

  /**
   * Generate session ID
   */
  generateSessionId() {
    return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate user ID
   */
  generateUserId() {
    return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Identify user (after login)
   */
  identify(userId, traits = {}) {
    this.userId = userId;
    localStorage.setItem('verity_user_id', userId);

    this.trackEvent('user_identified', {
      previousId: this.userId,
      ...traits
    });
  }

  /**
   * Track page view
   */
  trackPageView(page = null) {
    const data = {
      page: page || window.location.pathname,
      title: document.title,
      referrer: document.referrer,
      url: window.location.href,
      search: window.location.search
    };

    this.trackEvent('page_view', data);
  }

  /**
   * Track page leave
   */
  trackPageLeave() {
    const timeOnPage = Date.now() - this.pageStartTime;

    this.trackEvent('page_leave', {
      page: window.location.pathname,
      timeOnPage,
      interactions: this.interactions,
      scrollDepth: this.getScrollDepth()
    });
  }

  /**
   * Get scroll depth percentage
   */
  getScrollDepth() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    return scrollHeight > 0 ? Math.round((scrollTop / scrollHeight) * 100) : 0;
  }

  /**
   * Track generic event
   */
  trackEvent(eventName, properties = {}) {
    if (!this.isEnabled) return;

    const event = {
      event: eventName,
      properties: {
        ...properties,
        sessionId: this.sessionId,
        userId: this.userId,
        timestamp: new Date().toISOString(),
        page: window.location.pathname,
        userAgent: navigator.userAgent,
        screenWidth: window.innerWidth,
        screenHeight: window.innerHeight,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language
      }
    };

    this.queue.push(event);

    // Immediate flush for important events
    if (['verification_complete', 'error', 'purchase'].includes(eventName)) {
      this.flush();
    }
  }

  // ============ Verification Tracking ============

  /**
   * Track verification started
   */
  trackVerificationStarted(claim, options = {}) {
    this.trackEvent('verification_started', {
      claimLength: claim.length,
      claimType: options.type || 'text',
      model: options.model || 'standard',
      source: options.source || 'manual'
    });
  }

  /**
   * Track verification complete
   */
  trackVerificationComplete(result, duration) {
    this.trackEvent('verification_complete', {
      verdict: result.verdict,
      confidence: result.confidence,
      providersUsed: result.providers?.length || 0,
      sourcesFound: result.sources?.length || 0,
      duration,
      cached: result.cached || false
    });
  }

  /**
   * Track verification error
   */
  trackVerificationError(error, claim) {
    this.trackEvent('verification_error', {
      errorType: error.name || 'UnknownError',
      errorMessage: error.message,
      claimLength: claim?.length || 0
    });
  }

  /**
   * Track source click
   */
  trackSourceClick(source, verdict) {
    this.trackEvent('source_click', {
      sourceName: source.name,
      sourceUrl: source.url,
      sourceReliability: source.reliability,
      verdict
    });
  }

  // ============ User Actions ============

  /**
   * Track signup
   */
  trackSignup(method, plan = 'free') {
    this.trackEvent('signup', {
      method, // email, google, github, etc.
      plan
    });
  }

  /**
   * Track login
   */
  trackLogin(method) {
    this.trackEvent('login', { method });
  }

  /**
   * Track logout
   */
  trackLogout() {
    this.trackEvent('logout');
  }

  /**
   * Track plan upgrade
   */
  trackPlanUpgrade(fromPlan, toPlan, revenue) {
    this.trackEvent('plan_upgrade', {
      fromPlan,
      toPlan,
      revenue,
      currency: 'USD'
    });
  }

  /**
   * Track feature usage
   */
  trackFeatureUsage(feature, action = 'used') {
    this.trackEvent('feature_usage', {
      feature,
      action
    });
  }

  /**
   * Track search
   */
  trackSearch(query, resultsCount, filters = {}) {
    this.trackEvent('search', {
      queryLength: query.length,
      resultsCount,
      ...filters
    });
  }

  /**
   * Track export
   */
  trackExport(format, itemCount) {
    this.trackEvent('export', {
      format, // csv, json, pdf
      itemCount
    });
  }

  // ============ UI Interactions ============

  /**
   * Track button click
   */
  trackButtonClick(buttonName, location) {
    this.trackEvent('button_click', {
      buttonName,
      location
    });
  }

  /**
   * Track modal open
   */
  trackModalOpen(modalName) {
    this.trackEvent('modal_open', { modalName });
  }

  /**
   * Track modal close
   */
  trackModalClose(modalName, action) {
    this.trackEvent('modal_close', {
      modalName,
      action // confirmed, cancelled, dismissed
    });
  }

  /**
   * Track form submission
   */
  trackFormSubmission(formName, success, errorField = null) {
    this.trackEvent('form_submission', {
      formName,
      success,
      errorField
    });
  }

  /**
   * Track onboarding step
   */
  trackOnboardingStep(step, completed) {
    this.trackEvent('onboarding_step', {
      step,
      completed
    });
  }

  /**
   * Track onboarding complete
   */
  trackOnboardingComplete(totalSteps, skipped) {
    this.trackEvent('onboarding_complete', {
      totalSteps,
      skipped
    });
  }

  // ============ Performance ============

  /**
   * Track performance metric
   */
  trackPerformance(metric, value, context = {}) {
    this.trackEvent('performance', {
      metric, // LCP, FID, CLS, TTFB, etc.
      value,
      ...context
    });
  }

  /**
   * Track API latency
   */
  trackAPILatency(endpoint, duration, status) {
    this.trackEvent('api_latency', {
      endpoint,
      duration,
      status,
      slow: duration > 2000
    });
  }

  // ============ Errors ============

  /**
   * Track JavaScript error
   */
  trackError(error, context = {}) {
    this.trackEvent('error', {
      errorType: error.name || 'Error',
      errorMessage: error.message,
      errorStack: error.stack?.substring(0, 500),
      ...context
    });
  }

  // ============ A/B Testing ============

  /**
   * Track experiment exposure
   */
  trackExperiment(experimentId, variant) {
    this.trackEvent('experiment_exposure', {
      experimentId,
      variant
    });
  }

  // ============ Utility ============

  /**
   * Flush events to server
   */
  async flush(sync = false) {
    if (this.queue.length === 0) return;

    const events = [...this.queue];
    this.queue = [];

    const payload = {
      events,
      metadata: {
        sessionId: this.sessionId,
        userId: this.userId,
        batchTime: new Date().toISOString()
      }
    };

    try {
      if (sync && navigator.sendBeacon) {
        // Use sendBeacon for unload events
        navigator.sendBeacon(this.endpoint, JSON.stringify(payload));
      } else {
        await fetch(this.endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          keepalive: true
        });
      }
    } catch (error) {
      // Re-queue events on failure
      this.queue = [...events, ...this.queue];
      console.warn('Analytics flush failed:', error);
    }
  }

  /**
   * Enable analytics
   */
  enable() {
    this.isEnabled = true;
    localStorage.removeItem('verity_analytics_disabled');
  }

  /**
   * Disable analytics
   */
  disable() {
    this.isEnabled = false;
    localStorage.setItem('verity_analytics_disabled', 'true');
    this.queue = [];
  }

  /**
   * Check if enabled
   */
  isAnalyticsEnabled() {
    return this.isEnabled;
  }

  /**
   * Reset user (for logout)
   */
  reset() {
    this.flush();
    this.sessionId = this.generateSessionId();
    this.userId = this.generateUserId();
    localStorage.setItem('verity_user_id', this.userId);
  }

  /**
   * Cleanup
   */
  destroy() {
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
    }
    this.flush(true);
  }
}

// Create singleton instance
const analytics = new VerityAnalytics();

// Export for use throughout the app
window.VerityAnalytics = analytics;

// Export convenience functions
window.trackEvent = (name, props) => analytics.trackEvent(name, props);
window.trackVerification = (result, duration) => analytics.trackVerificationComplete(result, duration);
window.trackError = (error, context) => analytics.trackError(error, context);

export default analytics;
