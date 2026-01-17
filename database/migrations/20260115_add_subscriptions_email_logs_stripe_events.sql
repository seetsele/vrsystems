-- Migration: add subscriptions, email_logs, and stripe_events tables
-- Created: 2026-01-15

create table if not exists subscriptions (
    id serial primary key,
    email text,
    stripe_session_id text,
    stripe_customer_id text,
    stripe_subscription_id text,
    metadata jsonb,
    status text,
    created_at timestamptz default now()
);

create table if not exists email_logs (
    id serial primary key,
    idempotency_key text unique,
    to_email text,
    subject text,
    sent_at timestamptz default now(),
    status_code int,
    response_text text
);

create table if not exists stripe_events (
    id serial primary key,
    event_id text unique,
    event_type text,
    payload jsonb,
    received_at timestamptz default now()
);

-- Optional: create indexes for frequent queries
create index if not exists idx_subscriptions_email on subscriptions (email);
create index if not exists idx_email_logs_key on email_logs (idempotency_key);
create index if not exists idx_stripe_events_event_id on stripe_events (event_id);
