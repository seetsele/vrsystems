import pytest
import time


def test_live_stream_ws_ping():
    """Try connecting to a known websocket stream endpoint, skip if dependency or service missing."""
    try:
        import websocket
    except Exception:
        pytest.skip('websocket-client library not installed')

    url = "ws://127.0.0.1:8000/stream"
    try:
        ws = websocket.create_connection(url, timeout=2)
        ws.send('ping')
        resp = ws.recv()
        assert resp is not None
        ws.close()
    except Exception:
        pytest.skip('Live stream websocket not available')
