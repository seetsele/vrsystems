import pytest


def transient_send(email):
    # simulate transient failure then success based on counter
    counter = getattr(transient_send, 'count', 0)
    transient_send.count = counter + 1
    if counter < 1:
        raise ConnectionError('transient')
    return {'status': 'ok', 'id': 'sg_123'}


def send_with_retry(email, attempts=3):
    for i in range(attempts):
        try:
            return transient_send(email)
        except ConnectionError:
            if i == attempts - 1:
                raise
    return None


@pytest.mark.unit
def test_sendgrid_retry_succeeds_after_transient():
    # first call should raise inside transient_send, overall should succeed
    res = send_with_retry({'to': 'a@example.com'})
    assert res['status'] == 'ok'
