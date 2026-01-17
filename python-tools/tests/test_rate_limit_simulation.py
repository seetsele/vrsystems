import pytest


class SimpleRateLimiter:
    def __init__(self, max_calls):
        self.max_calls = max_calls
        self.count = 0

    def allow(self):
        if self.count >= self.max_calls:
            return False
        self.count += 1
        return True


@pytest.mark.unit
def test_rate_limiter_blocks_after_limit():
    r = SimpleRateLimiter(3)
    assert r.allow()
    assert r.allow()
    assert r.allow()
    assert not r.allow()
