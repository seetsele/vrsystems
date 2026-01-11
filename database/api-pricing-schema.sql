-- ================================================
-- VERITY SYSTEMS - API PRICING SCHEMA EXTENSION
-- Additional tables for API billing & rate limiting
-- Run this AFTER the main supabase-schema.sql
-- ================================================

-- ================================================
-- API USAGE BILLING TABLE
-- Tracks pay-per-use verification costs
-- ================================================
CREATE TABLE IF NOT EXISTS public.api_usage_billing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES public.api_keys(id) ON DELETE SET NULL,
    
    -- Billing period (monthly)
    billing_period_start DATE NOT NULL,
    billing_period_end DATE NOT NULL,
    
    -- Usage counts by type
    standard_count INTEGER DEFAULT 0,       -- Standard verifications
    premium_count INTEGER DEFAULT 0,        -- Premium (multi-source)
    bulk_count INTEGER DEFAULT 0,           -- Bulk batch processing
    verify_plus_count INTEGER DEFAULT 0,    -- Document verification
    
    -- Costs in cents
    standard_cost_cents INTEGER DEFAULT 0,
    premium_cost_cents INTEGER DEFAULT 0,
    bulk_cost_cents INTEGER DEFAULT 0,
    verify_plus_cost_cents INTEGER DEFAULT 0,
    
    -- Totals
    total_verifications INTEGER DEFAULT 0,
    total_cost_cents INTEGER DEFAULT 0,
    discount_applied DECIMAL(5,4) DEFAULT 0.0, -- e.g., 0.20 for 20%
    final_cost_cents INTEGER DEFAULT 0,
    
    -- Stripe billing
    stripe_invoice_id TEXT,
    invoice_status TEXT DEFAULT 'pending' CHECK (invoice_status IN ('pending', 'invoiced', 'paid', 'failed', 'waived')),
    paid_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint per user per billing period
    UNIQUE(user_id, billing_period_start)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_api_usage_billing_user_id ON public.api_usage_billing(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_billing_period ON public.api_usage_billing(billing_period_start, billing_period_end);
CREATE INDEX IF NOT EXISTS idx_api_usage_billing_status ON public.api_usage_billing(invoice_status);

-- Enable RLS
ALTER TABLE public.api_usage_billing ENABLE ROW LEVEL SECURITY;

-- Policy
CREATE POLICY "Users can view own billing" ON public.api_usage_billing
    FOR SELECT USING (auth.uid() = user_id);

-- ================================================
-- API SUBSCRIPTION TIERS TABLE
-- Defines the subscription plans for API access
-- ================================================
CREATE TABLE IF NOT EXISTS public.api_subscription_tiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    name TEXT UNIQUE NOT NULL,              -- 'starter', 'developer', 'pro', 'business', 'enterprise'
    display_name TEXT NOT NULL,             -- 'API Starter', 'API Developer', etc.
    
    -- Monthly pricing in cents
    monthly_price_cents INTEGER NOT NULL,
    annual_price_cents INTEGER,             -- Annual price (if offered)
    
    -- Included verifications
    included_verifications INTEGER NOT NULL,
    
    -- Rate limits
    rate_limit_per_minute INTEGER NOT NULL,
    daily_limit INTEGER,                    -- NULL = unlimited
    
    -- Features
    features JSONB DEFAULT '{}'::jsonb,
    
    -- Stripe product/price IDs
    stripe_monthly_price_id TEXT,
    stripe_annual_price_id TEXT,
    
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default API tiers
INSERT INTO public.api_subscription_tiers (name, display_name, monthly_price_cents, annual_price_cents, included_verifications, rate_limit_per_minute, daily_limit, features, sort_order)
VALUES 
    ('api_starter', 'API Starter', 4900, 52920, 1500, 60, 100, '{"support": "email", "batch": false, "webhook": false}'::jsonb, 1),
    ('api_developer', 'API Developer', 9900, 106920, 3500, 120, 250, '{"support": "email", "batch": true, "webhook": true, "batch_size": 10}'::jsonb, 2),
    ('api_pro', 'API Pro', 19900, 214920, 8000, 240, NULL, '{"support": "priority", "batch": true, "webhook": true, "batch_size": 50, "sla": "99.9%"}'::jsonb, 3),
    ('api_business', 'API Business', 49900, 538920, 20000, 600, NULL, '{"support": "dedicated", "batch": true, "webhook": true, "batch_size": 100, "sla": "99.95%", "custom_endpoints": true}'::jsonb, 4),
    ('api_enterprise', 'API Enterprise', 99900, NULL, 50000, 10000, NULL, '{"support": "dedicated", "batch": true, "webhook": true, "batch_size": 500, "sla": "99.99%", "custom_endpoints": true, "on_premise": true}'::jsonb, 5)
ON CONFLICT (name) DO UPDATE SET
    monthly_price_cents = EXCLUDED.monthly_price_cents,
    included_verifications = EXCLUDED.included_verifications,
    rate_limit_per_minute = EXCLUDED.rate_limit_per_minute;

-- ================================================
-- PAY-PER-USE PRICING TABLE
-- Defines the pay-per-use pricing tiers
-- ================================================
CREATE TABLE IF NOT EXISTS public.api_pay_per_use_pricing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    name TEXT UNIQUE NOT NULL,              -- 'standard', 'premium', 'bulk', 'verify_plus'
    display_name TEXT NOT NULL,
    description TEXT,
    
    -- Pricing in cents
    price_cents INTEGER NOT NULL,
    
    -- Volume discounts (stored as JSONB for flexibility)
    volume_discounts JSONB DEFAULT '[
        {"min": 0, "max": 999, "discount": 0.00},
        {"min": 1000, "max": 4999, "discount": 0.10},
        {"min": 5000, "max": 24999, "discount": 0.20},
        {"min": 25000, "max": 99999, "discount": 0.30},
        {"min": 100000, "max": null, "discount": 0.40}
    ]'::jsonb,
    
    -- Stripe meter/price IDs
    stripe_meter_id TEXT,
    stripe_price_id TEXT,
    
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default pay-per-use pricing
INSERT INTO public.api_pay_per_use_pricing (name, display_name, description, price_cents, sort_order)
VALUES 
    ('standard', 'Standard Verification', 'Basic fact-check with 5+ AI models', 6, 1),
    ('premium', 'Premium Verification', 'Enhanced multi-source verification with 10+ models', 10, 2),
    ('bulk', 'Bulk Verification', 'Batch processing rate (100+ items)', 5, 3),
    ('verify_plus', 'VerifyPlus Document', 'Full document analysis and verification', 150, 4)
ON CONFLICT (name) DO UPDATE SET
    price_cents = EXCLUDED.price_cents,
    description = EXCLUDED.description;

-- ================================================
-- API USAGE LOG (Real-time tracking)
-- Each API call is logged here
-- ================================================
CREATE TABLE IF NOT EXISTS public.api_call_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES public.api_keys(id) ON DELETE SET NULL,
    
    -- Request details
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    
    -- Verification details
    verification_type TEXT NOT NULL DEFAULT 'standard',
    claim_hash TEXT,                        -- For caching/deduplication
    
    -- Cost tracking
    base_cost_cents INTEGER NOT NULL DEFAULT 6,
    discount_applied DECIMAL(5,4) DEFAULT 0.0,
    final_cost_cents INTEGER NOT NULL DEFAULT 6,
    
    -- Response details
    status_code INTEGER,
    response_time_ms INTEGER,
    
    -- Metadata
    ip_address INET,
    user_agent TEXT,
    
    -- Billing reference
    billing_period_id UUID REFERENCES public.api_usage_billing(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_call_log_user_id ON public.api_call_log(user_id);
CREATE INDEX IF NOT EXISTS idx_api_call_log_created_at ON public.api_call_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_call_log_claim_hash ON public.api_call_log(claim_hash);
CREATE INDEX IF NOT EXISTS idx_api_call_log_billing ON public.api_call_log(billing_period_id);

-- Partitioning by month (optional - for high volume)
-- CREATE INDEX IF NOT EXISTS idx_api_call_log_month ON public.api_call_log(date_trunc('month', created_at));

-- Enable RLS
ALTER TABLE public.api_call_log ENABLE ROW LEVEL SECURITY;

-- Policy
CREATE POLICY "Users can view own API calls" ON public.api_call_log
    FOR SELECT USING (auth.uid() = user_id);

-- ================================================
-- RATE LIMIT TRACKING TABLE
-- Tracks rate limit state per user/key
-- ================================================
CREATE TABLE IF NOT EXISTS public.rate_limit_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Can be user_id or api_key_id
    identifier_type TEXT NOT NULL CHECK (identifier_type IN ('user', 'api_key', 'ip')),
    identifier TEXT NOT NULL,
    
    -- Rate limit window
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Counts
    request_count INTEGER DEFAULT 0,
    limit_value INTEGER NOT NULL,
    
    -- Last update
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique per identifier per window
    UNIQUE(identifier_type, identifier, window_start)
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_rate_limit_lookup ON public.rate_limit_state(identifier_type, identifier, window_start);

-- Auto-cleanup old rate limit records (older than 1 hour)
CREATE OR REPLACE FUNCTION cleanup_old_rate_limits()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM public.rate_limit_state WHERE window_end < NOW() - INTERVAL '1 hour';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger to clean up periodically (runs on insert)
DROP TRIGGER IF EXISTS cleanup_rate_limits ON public.rate_limit_state;
CREATE TRIGGER cleanup_rate_limits
    AFTER INSERT ON public.rate_limit_state
    EXECUTE FUNCTION cleanup_old_rate_limits();

-- ================================================
-- FUNCTIONS FOR API BILLING
-- ================================================

-- Function to get or create current billing period
CREATE OR REPLACE FUNCTION get_or_create_billing_period(p_user_id UUID)
RETURNS UUID AS $$
DECLARE
    v_period_start DATE;
    v_period_end DATE;
    v_billing_id UUID;
BEGIN
    -- Get start of current month
    v_period_start := DATE_TRUNC('month', CURRENT_DATE)::DATE;
    v_period_end := (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' - INTERVAL '1 day')::DATE;
    
    -- Try to get existing period
    SELECT id INTO v_billing_id 
    FROM public.api_usage_billing 
    WHERE user_id = p_user_id 
      AND billing_period_start = v_period_start;
    
    -- Create if doesn't exist
    IF v_billing_id IS NULL THEN
        INSERT INTO public.api_usage_billing (user_id, billing_period_start, billing_period_end)
        VALUES (p_user_id, v_period_start, v_period_end)
        RETURNING id INTO v_billing_id;
    END IF;
    
    RETURN v_billing_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to record API usage with automatic billing
CREATE OR REPLACE FUNCTION record_api_usage(
    p_user_id UUID,
    p_api_key_id UUID,
    p_verification_type TEXT,
    p_base_cost_cents INTEGER,
    p_endpoint TEXT DEFAULT '/api/verify',
    p_method TEXT DEFAULT 'POST',
    p_status_code INTEGER DEFAULT 200,
    p_response_time_ms INTEGER DEFAULT NULL,
    p_claim_hash TEXT DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS TABLE(
    call_id UUID,
    billing_id UUID,
    final_cost INTEGER,
    monthly_total INTEGER,
    discount DECIMAL
) AS $$
DECLARE
    v_billing_id UUID;
    v_call_id UUID;
    v_monthly_count INTEGER;
    v_discount DECIMAL(5,4);
    v_final_cost INTEGER;
BEGIN
    -- Get or create billing period
    v_billing_id := get_or_create_billing_period(p_user_id);
    
    -- Get current monthly count for discount calculation
    SELECT total_verifications INTO v_monthly_count
    FROM public.api_usage_billing
    WHERE id = v_billing_id;
    
    v_monthly_count := COALESCE(v_monthly_count, 0);
    
    -- Calculate volume discount
    v_discount := CASE
        WHEN v_monthly_count >= 100000 THEN 0.40
        WHEN v_monthly_count >= 25000 THEN 0.30
        WHEN v_monthly_count >= 5000 THEN 0.20
        WHEN v_monthly_count >= 1000 THEN 0.10
        ELSE 0.00
    END;
    
    -- Calculate final cost
    v_final_cost := ROUND(p_base_cost_cents * (1 - v_discount));
    
    -- Insert API call log
    INSERT INTO public.api_call_log (
        user_id, api_key_id, endpoint, method, verification_type,
        claim_hash, base_cost_cents, discount_applied, final_cost_cents,
        status_code, response_time_ms, ip_address, user_agent, billing_period_id
    )
    VALUES (
        p_user_id, p_api_key_id, p_endpoint, p_method, p_verification_type,
        p_claim_hash, p_base_cost_cents, v_discount, v_final_cost,
        p_status_code, p_response_time_ms, p_ip_address, p_user_agent, v_billing_id
    )
    RETURNING id INTO v_call_id;
    
    -- Update billing period totals
    UPDATE public.api_usage_billing
    SET 
        total_verifications = total_verifications + 1,
        total_cost_cents = total_cost_cents + v_final_cost,
        discount_applied = v_discount,
        final_cost_cents = total_cost_cents + v_final_cost,
        updated_at = NOW(),
        -- Update type-specific counts
        standard_count = CASE WHEN p_verification_type = 'standard' THEN standard_count + 1 ELSE standard_count END,
        premium_count = CASE WHEN p_verification_type = 'premium' THEN premium_count + 1 ELSE premium_count END,
        bulk_count = CASE WHEN p_verification_type = 'bulk' THEN bulk_count + 1 ELSE bulk_count END,
        verify_plus_count = CASE WHEN p_verification_type = 'verify_plus' THEN verify_plus_count + 1 ELSE verify_plus_count END,
        -- Update type-specific costs
        standard_cost_cents = CASE WHEN p_verification_type = 'standard' THEN standard_cost_cents + v_final_cost ELSE standard_cost_cents END,
        premium_cost_cents = CASE WHEN p_verification_type = 'premium' THEN premium_cost_cents + v_final_cost ELSE premium_cost_cents END,
        bulk_cost_cents = CASE WHEN p_verification_type = 'bulk' THEN bulk_cost_cents + v_final_cost ELSE bulk_cost_cents END,
        verify_plus_cost_cents = CASE WHEN p_verification_type = 'verify_plus' THEN verify_plus_cost_cents + v_final_cost ELSE verify_plus_cost_cents END
    WHERE id = v_billing_id;
    
    -- Return result
    RETURN QUERY SELECT v_call_id, v_billing_id, v_final_cost, v_monthly_count + 1, v_discount;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- GRANT PERMISSIONS
-- ================================================
GRANT SELECT ON public.api_subscription_tiers TO anon, authenticated;
GRANT SELECT ON public.api_pay_per_use_pricing TO anon, authenticated;
GRANT ALL ON public.api_usage_billing TO authenticated;
GRANT ALL ON public.api_call_log TO authenticated;
GRANT ALL ON public.rate_limit_state TO authenticated;

-- ================================================
-- COMMENTS
-- ================================================
COMMENT ON TABLE public.api_usage_billing IS 'Monthly billing summaries for pay-per-use API users';
COMMENT ON TABLE public.api_subscription_tiers IS 'API subscription plan definitions';
COMMENT ON TABLE public.api_pay_per_use_pricing IS 'Pay-per-use verification pricing tiers';
COMMENT ON TABLE public.api_call_log IS 'Detailed log of every API call for billing and analytics';
COMMENT ON TABLE public.rate_limit_state IS 'Rate limiting state for Redis fallback/sync';
COMMENT ON FUNCTION record_api_usage IS 'Records API usage with automatic volume discount and billing period management';
