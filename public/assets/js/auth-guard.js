// ================================================
// VERITY SYSTEMS - AUTH GUARD
// Protects pages that require authentication
// ================================================

const VerityGuard = {
    // Pages that don't require auth
    publicPages: [
        'index.html', 'auth.html', 'pricing.html', 'terms.html', 
        'privacy.html', 'api-docs.html', 'reset-password.html',
        'waitlist.html', '9-point-system.html'
    ],
    
    // Check if user is authenticated
    async isAuthenticated() {
        // Check localStorage first
        const user = localStorage.getItem('verity_user');
        const session = localStorage.getItem('verity_session');
        
        if (!user && !session) {
            return false;
        }
        
        // If Supabase is available, verify session
        if (window.VeritySupabase?.auth?.isConfigured()) {
            try {
                const { session: supaSession } = await window.VeritySupabase.auth.getSession();
                if (supaSession) {
                    return true;
                }
                // Session expired, clear localStorage
                this.clearSession();
                return false;
            } catch (error) {
                console.error('Auth check error:', error);
                return !!user; // Fall back to localStorage
            }
        }
        
        return !!user;
    },
    
    // Get current user
    async getUser() {
        if (window.VeritySupabase?.auth?.isConfigured()) {
            const { user } = await window.VeritySupabase.auth.getCurrentUser();
            if (user) return user;
        }
        
        const stored = localStorage.getItem('verity_user');
        return stored ? JSON.parse(stored) : null;
    },
    
    // Get user's tier
    async getTier() {
        const user = await this.getUser();
        return user?.user_metadata?.tier || localStorage.getItem('verity_tier') || 'free';
    },
    
    // Clear session
    clearSession() {
        localStorage.removeItem('verity_user');
        localStorage.removeItem('verity_session');
        localStorage.removeItem('verity_tier');
    },
    
    // Redirect to login
    redirectToLogin(returnUrl = null) {
        const current = returnUrl || window.location.pathname;
        window.location.href = `auth.html?redirect=${encodeURIComponent(current)}`;
    },
    
    // Check page access and redirect if needed
    async checkAccess() {
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        
        // Allow public pages
        if (this.publicPages.includes(currentPage)) {
            return true;
        }
        
        // Check authentication
        const isAuth = await this.isAuthenticated();
        
        if (!isAuth) {
            this.redirectToLogin();
            return false;
        }
        
        return true;
    },
    
    // Initialize guard on protected pages
    init() {
        // Run on DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.checkAccess());
        } else {
            this.checkAccess();
        }
    },
    
    // Log out user
    async logout() {
        if (window.VeritySupabase?.auth) {
            await window.VeritySupabase.auth.signOut();
        }
        this.clearSession();
        window.location.href = 'index.html';
    }
};

// Auto-init if on a protected page
// Uncomment to enforce auth on all pages:
// VerityGuard.init();

// Export for use in other scripts
window.VerityGuard = VerityGuard;
