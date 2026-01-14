import time
import os, sys
# Ensure python-tools is importable during tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'python-tools'))
import api_server_v9 as server
provider_health = server.provider_health


def test_provider_cooldown_trigger():
    name = "unit_test_provider"
    # Ensure clean state
    if name in provider_health.cooldown_until:
        del provider_health.cooldown_until[name]
    provider_health.failures[name] = 0

    # Trigger failures
    provider_health.record_failure(name, status_code=500)
    provider_health.record_failure(name, status_code=500)
    provider_health.record_failure(name, status_code=500)

    status = provider_health.get_status()
    assert name in status["in_cooldown"] or name in provider_health.cooldown_until

    # cleanup
    if name in provider_health.cooldown_until:
        del provider_health.cooldown_until[name]
    provider_health.failures[name] = 0
