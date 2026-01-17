import pytest


class AdvancedWebhookProcessor:
    def __init__(self):
        self.seen = {}

    def verify_signature(self, payload: dict, sig_header: str) -> bool:
        # simple deterministic pseudo-check for tests
        return sig_header == f"sig-{payload.get('id','')[:8]}"

    def handle(self, payload: dict, sig_header: str = ''):
        if not self.verify_signature(payload, sig_header):
            return {'status': 'invalid_signature'}
        eid = payload.get('id')
        if eid in self.seen:
            return {'status': 'ignored', 'id': eid}
        # simulate processing different event types
        et = payload.get('type')
        result = {'status': 'processed', 'id': eid, 'type': et}
        if et == 'payment_intent.succeeded':
            result['action'] = 'grant_access'
        elif et == 'charge.refunded':
            result['action'] = 'revoke_access'
        self.seen[eid] = result
        return result


@pytest.mark.integration
def test_stripe_various_events_and_idempotency():
    p = AdvancedWebhookProcessor()
    payload1 = {'id': 'evt_abcdef01', 'type': 'payment_intent.succeeded'}
    sig = 'sig-evt_abc'
    assert p.handle(payload1, sig)['status'] == 'invalid_signature'
    sig = f"sig-{payload1['id'][:8]}"
    r = p.handle(payload1, sig)
    assert r['status'] == 'processed' and r['action'] == 'grant_access'
    # repeated same event should be ignored
    r2 = p.handle(payload1, sig)
    assert r2['status'] == 'ignored'

    payload2 = {'id': 'evt_0002', 'type': 'charge.refunded'}
    sig2 = 'sig-evt_0002'
    r3 = p.handle(payload2, sig2)
    assert r3['action'] == 'revoke_access'
