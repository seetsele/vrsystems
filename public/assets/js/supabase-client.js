// ================================================
// VERITY SYSTEMS - SUPABASE CLIENT
// ================================================

// Supabase Configuration - PRODUCTION CREDENTIALS
const SUPABASE_URL = 'https://zxgydzavblgetojqdtir.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4Z3lkemF2YmxnZXRvanFkdGlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3OTk1NTgsImV4cCI6MjA4MjM3NTU1OH0.AVuUK2rFrbjbU5fFqKPKdziaB-jNVaqpdjS2ANPMHYQ';

// Check if Supabase is configured
const isSupabaseConfigured = SUPABASE_URL !== 'YOUR_SUPABASE_URL' && SUPABASE_ANON_KEY !== 'YOUR_SUPABASE_ANON_KEY';

// Initialize Supabase client - use a different variable name to avoid conflict with window.supabase
let supabaseClient = null;

// Try to initialize immediately or wait for library to load
function initSupabase() {
    if (supabaseClient) return true; // Already initialized
    
    // The CDN creates window.supabase with createClient method
    // Check multiple possible locations for the library
    let createClientFn = null;
    
    if (window.supabase && typeof window.supabase.createClient === 'function') {
        createClientFn = window.supabase.createClient;
    } else if (window.Supabase && typeof window.Supabase.createClient === 'function') {
        createClientFn = window.Supabase.createClient;
    }
    
    if (isSupabaseConfigured && createClientFn) {
        try {
            supabaseClient = createClientFn(SUPABASE_URL, SUPABASE_ANON_KEY, {
                auth: {
                    autoRefreshToken: true,
                    persistSession: true,
                    detectSessionInUrl: true,
                    flowType: 'pkce'
                }
            });
            // Also set legacy reference for compatibility
            window.supabaseClient = supabaseClient;
            console.log('✅ Supabase client initialized successfully');
            return true;
        } catch (e) {
            console.error('❌ Supabase initialization error:', e);
            return false;
        }
    }
    return false;
}

// Retry initialization with increasing delays
let initAttempts = 0;
const maxAttempts = 10;

function retryInit() {
    if (initSupabase()) {
        console.log('✅ Supabase ready after', initAttempts, 'attempts');
        // Dispatch custom event to notify waiting code
        window.dispatchEvent(new CustomEvent('supabaseReady'));
        return;
    }
    
    initAttempts++;
    if (initAttempts < maxAttempts) {
        const delay = Math.min(100 * initAttempts, 500);
        setTimeout(retryInit, delay);
    } else {
        console.error('❌ Failed to initialize Supabase after', maxAttempts, 'attempts');
    }
}

// Start initialization
if (!initSupabase()) {
    console.warn('⚠️ Supabase library not yet loaded - retrying...');
    // Wait for DOM and then retry
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', retryInit);
    } else {
        retryInit();
    }
}

// ================================================
// AUTHENTICATION HELPERS
// ================================================

const VerityAuth = {
    // Check if Supabase is available
    isConfigured() {
        // Try to initialize if not already done
        if (!supabaseClient) initSupabase();
        return isSupabaseConfigured && supabaseClient !== null;
    },

    // Ensure client is ready
    ensureClient() {
        if (!supabaseClient) initSupabase();
        if (!supabaseClient) {
            throw new Error('Supabase client not initialized. Please refresh the page.');
        }
        return supabaseClient;
    },

    // Sign up with email and password
    async signUp(email, password, metadata = {}) {
        if (!this.isConfigured()) {
            return { data: null, error: { message: 'Authentication service not available. Please refresh the page.' } };
        }
        try {
            const { data, error } = await supabaseClient.auth.signUp({
                email,
                password,
                options: {
                    data: metadata,
                    emailRedirectTo: `${window.location.origin}/dashboard.html`
                }
            });
            return { data, error };
        } catch (e) {
            console.error('SignUp error:', e);
            return { data: null, error: { message: e.message || 'Sign up failed' } };
        }
    },

    // Sign in with email and password
    async signIn(email, password) {
        if (!this.isConfigured()) {
            return { data: null, error: { message: 'Authentication service not available. Please refresh the page.' } };
        }
        try {
            const { data, error } = await supabaseClient.auth.signInWithPassword({
                email,
                password
            });
            return { data, error };
        } catch (e) {
            console.error('SignIn error:', e);
            return { data: null, error: { message: e.message || 'Sign in failed' } };
        }
    },

    // Sign in with OAuth provider (Google, GitHub, Apple, etc.)
    async signInWithOAuth(provider, options = {}) {
        if (!this.isConfigured()) {
            return { data: null, error: { message: 'Authentication service not available. Please refresh the page.' } };
        }
        
        try {
            const defaultOptions = {
                redirectTo: `${window.location.origin}/dashboard.html`
            };
            
            const { data, error } = await supabaseClient.auth.signInWithOAuth({
                provider,  // 'google', 'github', 'apple', 'discord', etc.
                options: { ...defaultOptions, ...options }
            });
            return { data, error };
        } catch (e) {
            console.error('OAuth error:', e);
            return { data: null, error: { message: e.message || `${provider} sign in failed` } };
        }
    },

    // Sign out
    async signOut() {
        if (!this.isConfigured()) {
            // Clear demo session
            localStorage.removeItem('verity_user');
            localStorage.removeItem('verity_stats');
            return { error: null };
        }
        const { error } = await supabaseClient.auth.signOut();
        // Also clear any local storage
        localStorage.removeItem('verity_user');
        localStorage.removeItem('verity_stats');
        return { error };
    },

    // Get current user
    async getCurrentUser() {
        if (!this.isConfigured()) {
            // Return demo user if exists
            const demoUser = localStorage.getItem('verity_user');
            return { user: demoUser ? JSON.parse(demoUser) : null, error: null };
        }
        const { data: { user }, error } = await supabaseClient.auth.getUser();
        return { user, error };
    },

    // Get current session
    async getSession() {
        if (!this.isConfigured()) {
            const demoUser = localStorage.getItem('verity_user');
            return { session: demoUser ? { user: JSON.parse(demoUser) } : null, error: null };
        }
        const { data: { session }, error } = await supabaseClient.auth.getSession();
        return { session, error };
    },

    // Listen to auth state changes
    onAuthStateChange(callback) {
        if (!this.isConfigured()) {
            // For demo mode, just return a no-op unsubscribe
            return { data: { subscription: { unsubscribe: () => {} } } };
        }
        return supabaseClient.auth.onAuthStateChange((event, session) => {
            callback(event, session);
        });
    },

    // Password reset
    async resetPassword(email) {
        if (!this.isConfigured()) {
            return { data: null, error: { message: 'Supabase not configured - password reset not available' } };
        }
        const { data, error } = await supabaseClient.auth.resetPasswordForEmail(email, {
            redirectTo: `${window.location.origin}/reset-password.html`
        });
        return { data, error };
    }
};

// ================================================
// DATABASE HELPERS
// ================================================

const VerityDB = {
    // Check if configured
    isConfigured() {
        if (!supabaseClient) initSupabase();
        return isSupabaseConfigured && supabaseClient !== null;
    },

    // Fact check submissions
    async submitFactCheck(claim, userId = null) {
        if (!this.isConfigured()) return { data: null, error: { message: 'Database not available' } };
        const { data, error } = await supabaseClient
            .from('fact_checks')
            .insert({
                claim,
                user_id: userId,
                status: 'pending',
                created_at: new Date().toISOString()
            })
            .select();
        return { data, error };
    },

    // Get user's fact check history
    async getFactCheckHistory(userId) {
        if (!this.isConfigured()) return { data: null, error: { message: 'Database not available' } };
        const { data, error } = await supabaseClient
            .from('fact_checks')
            .select('*')
            .eq('user_id', userId)
            .order('created_at', { ascending: false });
        return { data, error };
    },

    // Get single fact check by ID
    async getFactCheck(id) {
        if (!this.isConfigured()) return { data: null, error: { message: 'Database not available' } };
        const { data, error } = await supabaseClient
            .from('fact_checks')
            .select('*')
            .eq('id', id)
            .single();
        return { data, error };
    },

    // Contact form submissions
    async submitContactForm(formData) {
        if (!this.isConfigured()) return { data: null, error: { message: 'Database not available' } };
        const { data, error } = await supabaseClient
            .from('contact_submissions')
            .insert({
                name: formData.name,
                email: formData.email,
                company: formData.company,
                message: formData.message,
                created_at: new Date().toISOString()
            })
            .select();
        return { data, error };
    },

    // Newsletter signup
    async subscribeNewsletter(email) {
        if (!this.isConfigured()) return { data: null, error: { message: 'Database not available' } };
        const { data, error } = await supabaseClient
            .from('newsletter_subscribers')
            .upsert({
                email,
                subscribed_at: new Date().toISOString()
            }, { onConflict: 'email' })
            .select();
        return { data, error };
    }
};

// ================================================
// REAL-TIME SUBSCRIPTIONS
// ================================================

const VerityRealtime = {
    // Subscribe to fact check updates
    subscribeToFactCheck(factCheckId, callback) {
        if (!supabaseClient) return null;
        return supabaseClient
            .channel(`fact_check:${factCheckId}`)
            .on('postgres_changes', {
                event: 'UPDATE',
                schema: 'public',
                table: 'fact_checks',
                filter: `id=eq.${factCheckId}`
            }, callback)
            .subscribe();
    },

    // Unsubscribe from channel
    unsubscribe(channel) {
        if (supabaseClient && channel) {
            supabaseClient.removeChannel(channel);
        }
    }
};

// ================================================
// STORAGE HELPERS
// ================================================

const VerityStorage = {
    // Upload document for fact-checking
    async uploadDocument(file, userId) {
        if (!supabaseClient) return { data: null, error: { message: 'Storage not available' } };
        const fileName = `${userId}/${Date.now()}_${file.name}`;
        const { data, error } = await supabaseClient.storage
            .from('documents')
            .upload(fileName, file);
        return { data, error };
    },

    // Get document URL
    getDocumentUrl(path) {
        if (!supabaseClient) return null;
        const { data } = supabaseClient.storage
            .from('documents')
            .getPublicUrl(path);
        return data.publicUrl;
    },

    // Delete document
    async deleteDocument(path) {
        if (!supabaseClient) return { error: { message: 'Storage not available' } };
        const { error } = await supabaseClient.storage
            .from('documents')
            .remove([path]);
        return { error };
    }
};

// Export for use in other modules
window.VeritySupabase = {
    get client() { return supabaseClient; },
    auth: VerityAuth,
    db: VerityDB,
    realtime: VerityRealtime,
    storage: VerityStorage
};

// Also expose VerityAuth and VerityDB globally for easier access
window.VerityAuth = VerityAuth;
window.VerityDB = VerityDB;

console.log('Verity Supabase client initialized');
