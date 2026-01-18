-- 001_create_waitlist_and_stats.sql
-- Migration: create waitlist and stats tables for Verity local DB

BEGIN;

CREATE TABLE IF NOT EXISTS waitlist (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stats (
    key TEXT PRIMARY KEY,
    value JSONB
);

COMMIT;
