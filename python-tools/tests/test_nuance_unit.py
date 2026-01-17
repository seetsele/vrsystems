import sys
from pathlib import Path
import pytest

# make python-tools importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api_server_v10 import NuanceDetector


@pytest.mark.unit
def test_nuance_analyze_returns_dict():
    r = NuanceDetector.analyze_claim('This will always cure everything')
    assert isinstance(r, dict)
    assert 'nuance_score' in r or 'is_nuanced' in r
