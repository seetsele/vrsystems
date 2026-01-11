-- ================================================
-- VERITY SYSTEMS - SUPABASE DATABASE SCHEMA
-- Run this in your Supabase SQL Editor
-- ================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================
-- USERS PROFILE TABLE
-- Extends Supabase auth.users with app-specific data
-- ================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'starter', 'pro', 'professional', 'business', 'business-plus', 'enterprise')),
    verifications_used INTEGER DEFAULT 0,
    verifications_limit INTEGER DEFAULT 300,
    api_calls_used INTEGER DEFAULT 0,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_tier ON public.profiles(tier);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Policies for profiles
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- ================================================
-- FACT CHECKS TABLE
-- Stores all verification requests and results
-- ================================================
CREATE TABLE IF NOT EXISTS public.fact_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    claim TEXT NOT NULL,
    claim_type TEXT DEFAULT 'text' CHECK (claim_type IN ('text', 'url', 'image', 'document')),
    truth_score DECIMAL(5,2),
    verdict TEXT CHECK (verdict IN ('true', 'false', 'partially_true', 'unverifiable', 'pending')),
    confidence DECIMAL(5,2),
    sources JSONB DEFAULT '[]'::jsonb,
    analysis JSONB DEFAULT '{}'::jsonb,
    ai_models_used TEXT[],
    processing_time_ms INTEGER,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fact_checks
CREATE INDEX IF NOT EXISTS idx_fact_checks_user_id ON public.fact_checks(user_id);
CREATE INDEX IF NOT EXISTS idx_fact_checks_created_at ON public.fact_checks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_fact_checks_status ON public.fact_checks(status);
CREATE INDEX IF NOT EXISTS idx_fact_checks_verdict ON public.fact_checks(verdict);

-- Enable RLS
ALTER TABLE public.fact_checks ENABLE ROW LEVEL SECURITY;

-- Policies for fact_checks
CREATE POLICY "Users can view own fact checks" ON public.fact_checks
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own fact checks" ON public.fact_checks
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Anonymous can insert fact checks" ON public.fact_checks
    FOR INSERT WITH CHECK (user_id IS NULL);

-- ================================================
-- API KEYS TABLE
-- User-generated API keys for programmatic access
-- ================================================
CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    key_hash TEXT NOT NULL, -- Hashed API key (never store plain text)
    key_prefix TEXT NOT NULL, -- First 8 chars for identification
    permissions JSONB DEFAULT '{"verify": true, "batch": false, "admin": false}'::jsonb,
    rate_limit INTEGER DEFAULT 100, -- requests per minute
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON public.api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_prefix ON public.api_keys(key_prefix);

-- Enable RLS
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can manage own API keys" ON public.api_keys
    FOR ALL USING (auth.uid() = user_id);

-- ================================================
-- SUBSCRIPTIONS TABLE
-- Stripe subscription tracking
-- ================================================
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    stripe_subscription_id TEXT UNIQUE,
    stripe_price_id TEXT,
    tier TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'canceled', 'past_due', 'trialing', 'paused')),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT false,
    canceled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_id ON public.subscriptions(stripe_subscription_id);

-- Enable RLS
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view own subscriptions" ON public.subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- ================================================
-- USAGE LOGS TABLE
-- Track API usage for billing and analytics
-- ================================================
CREATE TABLE IF NOT EXISTS public.usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    api_key_id UUID REFERENCES public.api_keys(id) ON DELETE SET NULL,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    tokens_used INTEGER DEFAULT 0,
    cost_cents INTEGER DEFAULT 0,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON public.usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON public.usage_logs(created_at DESC);

-- Partition by month for better performance (optional)
-- CREATE INDEX IF NOT EXISTS idx_usage_logs_month ON public.usage_logs(date_trunc('month', created_at));

-- Enable RLS
ALTER TABLE public.usage_logs ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view own usage logs" ON public.usage_logs
    FOR SELECT USING (auth.uid() = user_id);

-- ================================================
-- CONTACT SUBMISSIONS TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS public.contact_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    company TEXT,
    subject TEXT,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'read', 'replied', 'closed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS (admins only via service role)
ALTER TABLE public.contact_submissions ENABLE ROW LEVEL SECURITY;

-- Allow public inserts
CREATE POLICY "Anyone can submit contact form" ON public.contact_submissions
    FOR INSERT WITH CHECK (true);

-- ================================================
-- NEWSLETTER SUBSCRIBERS TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS public.newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    is_subscribed BOOLEAN DEFAULT true,
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    unsubscribed_at TIMESTAMP WITH TIME ZONE
);

-- Enable RLS
ALTER TABLE public.newsletter_subscribers ENABLE ROW LEVEL SECURITY;

-- Allow public inserts
CREATE POLICY "Anyone can subscribe to newsletter" ON public.newsletter_subscribers
    FOR INSERT WITH CHECK (true);

-- ================================================
-- FUNCTIONS & TRIGGERS
-- ================================================

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Update timestamp function
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add update triggers
DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS update_fact_checks_updated_at ON public.fact_checks;
CREATE TRIGGER update_fact_checks_updated_at
    BEFORE UPDATE ON public.fact_checks
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- ================================================
-- TIER LIMITS VIEW
-- Easy access to tier configuration
-- ================================================
CREATE OR REPLACE VIEW public.tier_limits AS
SELECT * FROM (VALUES
    ('free', 300, 5, false, false, false),
    ('starter', 1200, 10, true, false, false),
    ('pro', 2500, 15, true, true, false),
    ('professional', 5000, 20, true, true, true),
    ('business', 15000, 25, true, true, true),
    ('business-plus', 25000, 30, true, true, true),
    ('enterprise', 75000, 32, true, true, true)
) AS t(tier, monthly_verifications, ai_models, api_access, batch_processing, priority_support);

-- ================================================
-- GRANT PERMISSIONS
-- ================================================
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON public.tier_limits TO anon, authenticated;
GRANT ALL ON public.profiles TO authenticated;
GRANT ALL ON public.fact_checks TO authenticated;
GRANT INSERT ON public.fact_checks TO anon;
GRANT ALL ON public.api_keys TO authenticated;
GRANT ALL ON public.subscriptions TO authenticated;
GRANT ALL ON public.usage_logs TO authenticated;
GRANT INSERT ON public.contact_submissions TO anon, authenticated;
GRANT INSERT ON public.newsletter_subscribers TO anon, authenticated;

-- ================================================
-- INITIAL DATA (Optional)
-- ================================================
-- You can add seed data here if needed

COMMENT ON TABLE public.profiles IS 'User profiles extending Supabase auth';
COMMENT ON TABLE public.fact_checks IS 'All verification requests and results';
COMMENT ON TABLE public.api_keys IS 'User API keys for programmatic access';
COMMENT ON TABLE public.subscriptions IS 'Stripe subscription tracking';
COMMENT ON TABLE public.usage_logs IS 'API usage logs for billing and analytics';
