import os
import pytest


def test_21_point_system_documented():
    """Check for a 21-point system doc or legacy 9-point doc present."""
    base = os.path.join(os.path.dirname(__file__), '..', '..', 'public')
    candidates = ['21-point-system.html', 'accuracy-score-guide.html']
    found = any(os.path.exists(os.path.join(base, c)) for c in candidates)
    assert found, 'No scoring system documentation found (21/9/accuracy)'
