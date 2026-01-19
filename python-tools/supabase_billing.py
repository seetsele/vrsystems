"""
Supabase billing helper utilities.
Best-effort RPC calls to `record_api_usage` and lookups for API keys.
Requires environment variables: SUPABASE_URL and SUPABASE_SERVICE_KEY (preferred) or SUPABASE_ANON_KEY.
"""

import os
import json
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("supabase_billing")

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')

if SUPABASE_URL and not SUPABASE_URL.endswith('/'): 
    SUPABASE_URL = SUPABASE_URL.rstrip('/')

HEADERS = {
    'Content-Type': 'application/json'
}
if SUPABASE_SERVICE_KEY:
    HEADERS['apikey'] = SUPABASE_SERVICE_KEY
    HEADERS['Authorization'] = f'Bearer {SUPABASE_SERVICE_KEY}'


async def get_user_id_from_api_key(api_key_value: str) -> Optional[str]:
    """Try to resolve a user_id (UUID) from the `api_keys` table using the provided api key value.
    Returns the user_id string or None if not found or not configured.
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return None
    try:
        url = f"{SUPABASE_URL}/rest/v1/api_keys?select=user_id&api_key=eq.{api_key_value}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, headers=HEADERS)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and data:
                    return data[0].get('user_id')
    except Exception as e:
        logger.debug('get_user_id_from_api_key error: %s', e)
    return None


async def record_api_usage_via_rpc(
    p_user_id: str,
    p_api_key_id: Optional[str],
    p_verification_type: str,
    p_base_cost_cents: int = 6,
    p_endpoint: str = '/verify',
    p_method: str = 'POST',
    p_status_code: int = 200,
    p_response_time_ms: Optional[int] = None,
    p_claim_hash: Optional[str] = None,
    p_ip_address: Optional[str] = None,
    p_user_agent: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Call Supabase PostgREST RPC `record_api_usage`.
    Returns the RPC result or None on failure.
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.debug('Supabase not configured; skipping record_api_usage_via_rpc')
        return None

    url = f"{SUPABASE_URL}/rest/v1/rpc/record_api_usage"
    payload = {
        'p_user_id': p_user_id,
        'p_api_key_id': p_api_key_id,
        'p_verification_type': p_verification_type,
        'p_base_cost_cents': p_base_cost_cents,
        'p_endpoint': p_endpoint,
        'p_method': p_method,
        'p_status_code': p_status_code,
        'p_response_time_ms': p_response_time_ms,
        'p_claim_hash': p_claim_hash,
        'p_ip_address': p_ip_address,
        'p_user_agent': p_user_agent
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(url, headers=HEADERS, json=payload)
            if r.status_code in (200, 201):
                return r.json()
            else:
                logger.debug('record_api_usage_via_rpc failed: %s %s', r.status_code, r.text)
    except Exception as e:
        logger.debug('record_api_usage_via_rpc exception: %s', e)
    return None


if __name__ == '__main__':
    print('Supabase billing helper loaded. Ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set.')
