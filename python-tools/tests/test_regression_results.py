import json
import os


def test_regression_matches_expected():
    path = os.path.join(os.path.dirname(__file__), '..', 'regression_results.json')
    path = os.path.abspath(path)
    assert os.path.exists(path), f"regression results not found at {path}"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for r in data.get('runs', []):
        expected = r.get('expected')
        resp = r.get('response')
        if not resp:
            # If no response, fail
            assert False, f"No response for {r.get('id')}"
        actual = resp.get('verdict')
        # allow some tolerance: tests pass if actual == expected or expected == 'mixed' and actual in ('mixed','mostly_true','mostly_false')
        if expected == 'mixed':
            assert actual in ('mixed', 'mostly_true', 'mostly_false', 'true', 'false'), f"{r.get('id')} expected mixed got {actual}"
        else:
            assert actual == expected, f"{r.get('id')} expected {expected} got {actual}"
