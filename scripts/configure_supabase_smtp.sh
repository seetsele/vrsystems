#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
This is a template helper for configuring SMTP for a Supabase project.
It does NOT run any privileged change unless you uncomment the example commands
and provide the required environment variables.

Required environment variables (examples in `.env.example`):
- SUPABASE_URL
- SUPABASE_SERVICE_KEY (service_role key)
- SUPABASE_PROJECT_REF
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM

Recommended flow:
1) Prefer using the Supabase dashboard or official CLI when possible.
2) Export the variables (or `source .env`) before running this script.
3) Uncomment the command you want to run and execute this script.

Examples (commented):

# Using the supabase CLI (if installed):
# supabase login
# supabase projects env set SMTP_HOST "$SMTP_HOST" --project "$SUPABASE_PROJECT_REF"
# supabase projects env set SMTP_PORT "$SMTP_PORT" --project "$SUPABASE_PROJECT_REF"
# supabase projects env set SMTP_USER "$SMTP_USER" --project "$SUPABASE_PROJECT_REF"
# supabase projects env set SMTP_PASS "$SMTP_PASS" --project "$SUPABASE_PROJECT_REF"
# supabase projects env set SMTP_FROM "$SMTP_FROM" --project "$SUPABASE_PROJECT_REF"

# Using a management API via curl (highly dependent on your provider and requires
# a service_role key and the correct management endpoint). This is a generic
# template — DO NOT run until you confirm the endpoint and payload with Supabase
# support or your Supabase plan documentation.
#
# curl -X PATCH "https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/settings/email" \
#   -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
#   -H "Content-Type: application/json" \
#   -d '{"smtp_host":"${SMTP_HOST}","smtp_port":'"${SMTP_PORT}"',"smtp_user":"${SMTP_USER}","smtp_pass":"${SMTP_PASS}","smtp_from":"${SMTP_FROM}"}'

EOF

echo "Template created. Edit and uncomment the command you want to use."
