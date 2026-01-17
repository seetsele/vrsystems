import pytest

# Simulate email service that enforces idempotency via keys
class DummyEmailService:
    def __init__(self):
        self.sent_keys = set()

    def send(self, to, subj, body, idempotency_key=None):
        if idempotency_key:
            if idempotency_key in self.sent_keys:
                return {'status': 'duplicate'}
            self.sent_keys.add(idempotency_key)
        # pretend to send
        return {'status': 'sent'}


@pytest.mark.unit
def test_email_idempotency_key():
    svc = DummyEmailService()
    r1 = svc.send('a@example.com', 'Hello', 'Body', idempotency_key='k1')
    assert r1['status'] == 'sent'
    r2 = svc.send('a@example.com', 'Hello', 'Body', idempotency_key='k1')
    assert r2['status'] == 'duplicate'
