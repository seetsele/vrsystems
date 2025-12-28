// ================================================
// VERITY SYSTEMS - SUPABASE CLIENT
// ================================================

// Supabase Configuration - PRODUCTION CREDENTIALS
const SUPABASE_URL = 'https://zxgydzavblgetojqdtir.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4Z3lkemF2YmxnZXRvanFkdGlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3OTk1NTgsImV4cCI6MjA4MjM3NTU1OH0.AVuUK2rFrbjbU5fFqKPKdziaB-jNVaqpdjS2ANPMHYQ';

// Check if Supabase is configured
const isSupabaseConfigured = SUPABASE_URL !== 'YOUR_SUPABASE_URL' && SUPABASE_ANON_KEY !== 'YOUR_SUPABASE_ANON_KEY';

// Initialize Supabase client (or null if not configured)
let supabase = null;
if (isSupabaseConfigured && window.supabase) {
    supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    console.log('✅ Supabase client initialized');
} else {
    console.warn('⚠️ Supabase not configured - using demo mode. Set SUPABASE_URL and SUPABASE_ANON_KEY in supabase-client.js');
}

// ================================================
// AUTHENTICATION HELPERS
// ================================================

const VerityAuth = {
    // Check if Supabase is available
    isConfigured() {
        return isSupabaseConfigured && supabase !== null;
    },

    // Sign up with email and password
    async signUp(email, password, metadata = {}) {
        if (!this.isConfigured()) {
            return { data: null, error: { message: 'Supabase not configured - using demo mode' } };
        }
        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: metadata
            }
        });
        return { data, error };
    },

    // Sign in with email and password
    async signIn(email, password) {
        if (!this.isConfigured()) {
            return { data: null, error: { message: 'Supabase not configured - using demo mode' } };
        }
        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password
        });
        return { data, error };
    },

    // Sign in with OAuth provider (Google, GitHub, Apple, etc.)
    async signInWithOAuth(provider, options = {}) {
        if (!this.isConfigured()) {
            return { data: null, error: { message: 'Supabase not configured - using demo mode' } };
        }
        
        const defaultOptions = {
            redirectTo: `${window.location.origin}/dashboard.html`
        };
        
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider,  // 'google', 'github', 'apple', 'discord', etc.
            options: { ...defaultOptions, ...options }
        });
        return { data, error };
    },

    // Sign out
    async signOut() {
        if (!this.isConfigured()) {
            // Clear demo session
            localStorage.removeItem('verity_user');
            localStorage.removeItem('verity_stats');
            return { error: null };
        }
        const { error } = await supabase.auth.signOut();
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
        const { data: { user }, error } = await supabase.auth.getUser();
        return { user, error };
    },

    // Get current session
    async getSession() {
        if (!this.isConfigured()) {
            const demoUser = localStorage.getItem('verity_user');
            return { session: demoUser ? { user: JSON.parse(demoUser) } : null, error: null };
        }
        const { data: { session }, error } = await supabase.auth.getSession();
        return { session, error };
    },

    // Listen to auth state changes
    onAuthStateChange(callback) {
        if (!this.isConfigured()) {
            // For demo mode, just return a no-op unsubscribe
            return { data: { subscription: { unsubscribe: () => {} } } };
        }
        return supabase.auth.onAuthStateChange((event, session) => {
            callback(event, session);
        });
    },

    // Password reset
    async resetPassword(email) {
        if (!this.isConfigured()) {
            return { data: null, error: { message: 'Supabase not configured - password reset not available' } };
        }
        const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: `${window.location.origin}/reset-password.html`
        });
        return { data, error };
    }
};

// ================================================
// DATABASE HELPERS
// ================================================

const VerityDB = {
    // Fact check submissions
    async submitFactCheck(claim, userId = null) {
        const { data, error } = await supabase
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
        const { data, error } = await supabase
            .from('fact_checks')
            .select('*')
            .eq('user_id', userId)
            .order('created_at', { ascending: false });
        return { data, error };
    },

    // Get single fact check by ID
    async getFactCheck(id) {
        const { data, error } = await supabase
            .from('fact_checks')
            .select('*')
            .eq('id', id)
            .single();
        return { data, error };
    },

    // Contact form submissions
    async submitContactForm(formData) {
        const { data, error } = await supabase
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
        const { data, error } = await supabase
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
        return supabase
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
        supabase.removeChannel(channel);
    }
};

// ================================================
// STORAGE HELPERS
// ================================================

const VerityStorage = {
    // Upload document for fact-checking
    async uploadDocument(file, userId) {
        const fileName = `${userId}/${Date.now()}_${file.name}`;
        const { data, error } = await supabase.storage
            .from('documents')
            .upload(fileName, file);
        return { data, error };
    },

    // Get document URL
    getDocumentUrl(path) {
        const { data } = supabase.storage
            .from('documents')
            .getPublicUrl(path);
        return data.publicUrl;
    },

    // Delete document
    async deleteDocument(path) {
        const { error } = await supabase.storage
            .from('documents')
            .remove([path]);
        return { error };
    }
};

// Export for use in other modules
window.VeritySupabase = {
    client: supabase,
    auth: VerityAuth,
    db: VerityDB,
    realtime: VerityRealtime,
    storage: VerityStorage
};

console.log('Verity Supabase client initialized');
