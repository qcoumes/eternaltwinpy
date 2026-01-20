import pytest

from eternaltwin.exceptions import InvalidStateError
from eternaltwin.states import State
from tests.conftest import ETWIN_URL


def test_encoding_decoding_state(rs256_key):
    state = State.new(ETWIN_URL, rs256_key)
    assert state == state.from_jwt(state.jwt, ETWIN_URL, rs256_key)


def test_invalid_state_action(rs256_key, payload):
    payload["a"] = "invalid"
    jwt = rs256_key.encode(payload)
    with pytest.raises(InvalidStateError, match="Expected action"):
        State.from_jwt(jwt, ETWIN_URL, rs256_key)


def test_invalid_state_authorization_server(rs256_key, payload):
    payload["as"] = "invalid"
    jwt = rs256_key.encode(payload)
    with pytest.raises(InvalidStateError, match="Expected authorization server"):
        State.from_jwt(jwt, ETWIN_URL, rs256_key)


def test_invalid_state_expiration(rs256_key, payload):
    payload["exp"] = 0
    jwt = rs256_key.encode(payload)
    with pytest.raises(InvalidStateError, match="Authorization expired"):
        State.from_jwt(jwt, ETWIN_URL, rs256_key)
