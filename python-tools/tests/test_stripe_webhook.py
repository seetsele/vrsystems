import pytest

# Simulate a minimal webhook handler with idempotency
class DummyWebhookProcessor:
    def __init__(self):
        self.seen = set()

    def handle(self, payload: dict):
        # payload contains 'id' and 'type'
        eid = payload.get('id')
        if not eid:
            raise ValueError('missing id')
        if eid in self.seen:
            return {'status': 'ignored', 'id': eid}
        # process and mark seen
        self.seen.add(eid)
        return {'status': 'processed', 'id': eid}


@pytest.mark.integration
def test_webhook_idempotency():
    p = DummyWebhookProcessor()
    payload = {'id': 'evt_123', 'type': 'payment.succeeded', 'data': {'object': {}}}
    r1 = p.handle(payload)
    assert r1['status'] == 'processed'
    r2 = p.handle(payload)
    assert r2['status'] == 'ignored'
