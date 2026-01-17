import pytest
import socket


def _is_port_open(port, host='127.0.0.1'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False


def test_core_ports():
    """Check typical local ports for services (http, db)."""
    # http server (public) usually on 3001 or 8000
    assert _is_port_open(3001) or _is_port_open(3002) or _is_port_open(8000) or _is_port_open(3000)
    # postgres default
    # don't require it, but report presence
    _is_port_open(5432)
