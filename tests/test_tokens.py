import time


def test_has_expired(token):
    assert not token.has_expired()
    token.expiration = int(time.time()) - 120
    assert token.has_expired()
