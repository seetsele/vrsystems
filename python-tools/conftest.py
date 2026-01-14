import os
import sys
import time
import pytest
from dotenv import load_dotenv

# Ensure python-tools is on path when tests are run from repo root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

TOOLS_DIR = os.path.abspath(os.path.dirname(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from test_helpers import create_confirmed_user, delete_user

load_dotenv('../.env')

@pytest.fixture(scope='function')
def confirmed_user():
    """Create and yield a confirmed Supabase user, then delete at teardown."""
    email = f"pytest_user_{os.getpid()}_{int(time.time())}@veritysystems.test"
    password = 'TestPass123!'
    resp = create_confirmed_user(email, password)
    if resp is None or resp.status_code not in (200, 201):
        pytest.skip('Could not create confirmed user; check SUPABASE_SERVICE_KEY and service availability')
    try:
        data = resp.json()
        user_id = data.get('id') or data.get('user', {}).get('id')
    except Exception:
        user_id = None
    yield {'email': email, 'password': password, 'id': user_id}
    # Teardown: delete user if created
    if user_id:
        delete_user(user_id)