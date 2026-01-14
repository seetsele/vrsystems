import os
import sys
import time
import pytest
from dotenv import load_dotenv

# Ensure python-tools directory is importable
TOOLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python-tools'))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from test_helpers import create_confirmed_user, delete_user

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
print('Loading env from:', env_path)
load_dotenv(env_path, override=True)

@pytest.fixture(scope='function')
def confirmed_user():
    email = f"pytest_user_{os.getpid()}_{int(time.time())}@veritysystems.test"
    password = 'TestPass123!'
    # Debug: ensure SUPABASE_SERVICE_KEY is loaded
    svc = os.getenv('SUPABASE_SERVICE_KEY')
    print('DEBUG SUPABASE_SERVICE_KEY present?', bool(svc))
    resp = create_confirmed_user(email, password)
    if resp is None:
        pytest.skip('Could not create confirmed user; request failed (no response)')
    if resp.status_code not in (200, 201):
        # print debug info
        try:
            print('create_confirmed_user failed:', resp.status_code, resp.text)
        except Exception:
            print('create_confirmed_user failed: no response text')
        pytest.skip('Could not create confirmed user; check SUPABASE_SERVICE_KEY and service availability')
    try:
        data = resp.json()
        user_id = data.get('id') or data.get('user', {}).get('id')
    except Exception:
        user_id = None
    yield {'email': email, 'password': password, 'id': user_id}
    if user_id:
        delete_user(user_id)
