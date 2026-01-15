import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'python-tools'))
from fastapi.testclient import TestClient
import api_server_v9 as server

client = TestClient(server.app)


def test_image_forensics_with_image_url():
    resp = client.post('/tools/image-forensics', json={'content': 'https://example.com/photo.jpg'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['tool'] == 'Image Forensics'
    assert any(f['type'] == 'analysis' for f in data['findings'])
    assert 'No obvious manipulation' in data['summary'] or data['verdict'] == 'likely_authentic'


def test_image_forensics_deepfake_mention():
    resp = client.post('/tools/image-forensics', json={'content': 'This looks like a deepfake of the politician'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['tool'] == 'Image Forensics'
    assert any(f['type'] == 'deepfake_mention' for f in data['findings'])
    assert data['verdict'] in ('needs_review', 'likely_manipulated')


def test_realtime_stream_high_viral():
    resp = client.post('/tools/realtime-stream', json={'content': 'Breaking: new viral video trending now'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['tool'] == 'Real-Time Stream'
    assert data['spread_velocity'] == 'high'
    assert 'high_spread' in data['verdict']


def test_realtime_stream_medium():
    resp = client.post('/tools/realtime-stream', json={'content': 'News update: regional report posted'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['tool'] == 'Real-Time Stream'
    assert data['spread_velocity'] == 'medium'
    assert 'medium_spread' in data['verdict']
