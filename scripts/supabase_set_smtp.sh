#!/usr/bin/env bash
set -euo pipefail

echo "Supabase SMTP setter (safe). This script will use the `supabase` CLI if available"
echo "and set project environment variables for SMTP. It will NOT run unless required vars exist."

if ! command -v supabase >/dev/null 2>&1; then
  echo "supabase CLI not found. Install it: https://supabase.com/docs/guides/cli"
  exit 1
fi

# Load .env if present
if [ -f .env ]; then
  # shellcheck disable=SC1091
  export $(grep -v '^#' .env | xargs)
fi

: ${SUPABASE_PROJECT_REF:?Please set SUPABASE_PROJECT_REF in .env or environment}
: ${SMTP_HOST:?Please set SMTP_HOST}
: ${SMTP_PORT:?Please set SMTP_PORT}
: ${SMTP_USER:?Please set SMTP_USER}
: ${SMTP_PASS:?Please set SMTP_PASS}
: ${SMTP_FROM:?Please set SMTP_FROM}

echo "About to set SMTP env vars for Supabase project: $SUPABASE_PROJECT_REF"
read -p "Continue? (y/N) " confirm
if [ "${confirm}" != "y" ] && [ "${confirm}" != "Y" ]; then
  echo "Aborting."
  exit 0
fi

echo "Setting SMTP envs via supabase CLI (scoped to project)."
supabase projects env set SMTP_HOST "$SMTP_HOST" --project "$SUPABASE_PROJECT_REF"
supabase projects env set SMTP_PORT "$SMTP_PORT" --project "$SUPABASE_PROJECT_REF"
supabase projects env set SMTP_USER "$SMTP_USER" --project "$SUPABASE_PROJECT_REF"
supabase projects env set SMTP_PASS "$SMTP_PASS" --project "$SUPABASE_PROJECT_REF"
supabase projects env set SMTP_FROM "$SMTP_FROM" --project "$SUPABASE_PROJECT_REF"

echo "Done. Please verify SMTP settings in Supabase dashboard and test signup flow."
