import base64
from urllib.parse import urlencode, urljoin

import pytest

from eternaltwin.clients import endpoints
from eternaltwin.clients.sync.clients import Eternaltwin
from eternaltwin.exceptions import InvalidStateError
from tests.conftest import ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, ETWIN_URL


def test_basic_auth_token(hs256_key):
    client = Eternaltwin(ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, hs256_key, url=ETWIN_URL)
    expected = base64.b64encode(f"{ETWIN_CLIENT_ID}:{ETWIN_CLIENT_SECRET}".encode()).decode()
    assert client._basic_auth_token() == expected


def test_authorization_url(hs256_key):
    client = Eternaltwin(ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, hs256_key, url=ETWIN_URL)
    state = client.generate_state()
    params = {
        "response_type": "code",
        "access_type": "offline",
        "client_id": client.client_id,
        "scope": "base",
        "state": state,
        "redirect_uri": client.redirect_uri,
    }
    assert client.authorization_url(state) == f"{urljoin(client.url, endpoints.AUTHORIZATION)}?{urlencode(params)}"


def test_validate_state(client, hs256_key):
    client = Eternaltwin(ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, hs256_key, url=ETWIN_URL)
    with pytest.raises(InvalidStateError):
        client.validate_state(client.generate_state(), client.generate_state())


def test_token(client, user1_authorization_code):
    client.token(authorization_code=user1_authorization_code)
