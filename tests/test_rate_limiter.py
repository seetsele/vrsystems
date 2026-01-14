import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'python-tools'))
import api_server_v9 as server
rate_limiter = server.rate_limiter


def test_rate_limiter_threshold():
    identifier = 'unit-test-rl'
    # Temporarily lower limit
    old_max = rate_limiter.max_requests
    rate_limiter.max_requests = 3
    # Clear state
    rate_limiter.requests[identifier] = []

    # 3 allowed
    for i in range(3):
        allowed, info = rate_limiter.is_allowed(identifier)
        assert allowed

    # 4th should be blocked
    allowed, info = rate_limiter.is_allowed(identifier)
    assert not allowed
    assert info['limit'] == 3

    # Restore
    rate_limiter.max_requests = old_max
    rate_limiter.requests.pop(identifier, None)
