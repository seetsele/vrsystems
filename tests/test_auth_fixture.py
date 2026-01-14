import os
import requests


def test_confirmed_user_fixture(confirmed_user):
    # confirmed_user fixture provides email, password, id
    email = confirmed_user['email']
    user_id = confirmed_user['id']

    # Verify user exists using Supabase admin GET endpoint
    svc = os.getenv('SUPABASE_SERVICE_KEY')
    base = os.getenv('SUPABASE_URL', 'https://zxgydzavblgetojqdtir.supabase.co')
    assert svc, 'SUPABASE_SERVICE_KEY not set in env for tests'
    headers = {'Authorization': f'Bearer {svc}', 'apikey': svc}
    r = requests.get(f"{base}/auth/v1/admin/users/{user_id}", headers=headers, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data.get('email') == email
