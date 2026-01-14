import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'python-tools'))
from fastapi.testclient import TestClient
import api_server_v9 as server

client = TestClient(server.app)


def test_score_known_domains():
    assert server.score_source_credibility('https://www.nature.com/article') >= 0.95
    assert server.score_source_credibility('https://cnn.com/article') >= 0.7
    assert server.score_source_credibility('https://infowars.com/story') <= 0.2


def test_tools_source_credibility_endpoint():
    # The endpoint expects a text content payload (ToolRequest.content)
    content = 'https://www.nature.com/article https://infowars.com/story'
    # Clear any rate-limiter state to avoid test interference
    server.rate_limiter.requests.clear()
    resp = client.post('/tools/source-credibility', json={'content': content})
    assert resp.status_code == 200
    data = resp.json()
    assert 'verdict' in data
    assert 'score' in data
    assert data['sources'] is not None
