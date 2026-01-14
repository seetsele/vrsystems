"""Helper functions for creating/deleting confirmed Supabase users for testing.
Requires SUPABASE_SERVICE_KEY in environment or in .env (loaded by tests).
"""
import os
import requests

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://zxgydzavblgetojqdtir.supabase.co')
def _auth_headers():
    svc = os.getenv('SUPABASE_SERVICE_KEY')
    return {
        'Authorization': f'Bearer {svc}' if svc else '',
        'apikey': svc or '',
        'Content-Type': 'application/json'
    }


def create_confirmed_user(email: str, password: str = 'TestPass123!') -> requests.Response:
    """Create a confirmed user via Supabase admin API.
    Returns the Response object; caller should handle status and cleanup.
    """
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    payload = {'email': email, 'password': password, 'email_confirm': True}
    resp = requests.post(url, headers=_auth_headers(), json=payload, timeout=30)
    return resp


def delete_user(user_id: str) -> requests.Response:
    """Delete a user via Supabase admin API by user id."""
    url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
    resp = requests.delete(url, headers=_auth_headers(), timeout=30)
    return resp
