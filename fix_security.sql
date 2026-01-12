-- ============================================
-- FIX SUPABASE SECURITY ADVISOR ISSUES
-- ============================================

-- 1. FIX RLS DISABLED IN PUBLIC (3 tables)
ALTER TABLE IF EXISTS public.api_subscription_tiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.api_pay_per_use_pricing ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.rate_limit_state ENABLE ROW LEVEL SECURITY;

-- Create read policies for pricing tables
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'public_read_subscription_tiers') THEN
        CREATE POLICY public_read_subscription_tiers ON public.api_subscription_tiers FOR SELECT USING (true);
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'public_read_pay_per_use') THEN
        CREATE POLICY public_read_pay_per_use ON public.api_pay_per_use_pricing FOR SELECT USING (true);
    END IF;
END $$;

-- Rate limit policies
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'users_own_rate_limits') THEN
        CREATE POLICY users_own_rate_limits ON public.rate_limit_state FOR ALL USING (true);
    END IF;
END $$;
