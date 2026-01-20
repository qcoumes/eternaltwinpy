import base64
from urllib.parse import urlencode

import pytest

from eternaltwin.clients.sync import Eternaltwin
from eternaltwin.users import AnonymousUser
from tests.conftest import ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, ETWIN_URL


def test_basic_auth_token():
    client = Eternaltwin(ETWIN_URL, ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL)
    expected = base64.b64encode(f"{ETWIN_CLIENT_ID}:{ETWIN_CLIENT_SECRET}".encode()).decode()
    assert client._basic_auth_token() == expected


def test_authentication_url(state):
    client = Eternaltwin(ETWIN_URL, ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL)
    params = {
        "response_type": "code",
        "access_type": "offline",
        "client_id": client.client_id,
        "scope": "base",
        "state": state.jwt,
        "redirect_uri": client.redirect_uri,
    }
    assert client.authentication_url(state) == f"{client.authorization_uri}?{urlencode(params)}"


def test_authenticate_no_authorization_code_nor_token(client):
    with pytest.raises(ValueError):
        client.authenticate()


def test_authenticate_both_authorization_code_and_token(client, token):
    with pytest.raises(ValueError):
        client.authenticate(authorization_code="code", token=token)


def test_authenticate_authorization_code(client, user1_authorization_code):
    assert not client.is_authenticated()
    client.authenticate(authorization_code=user1_authorization_code)
    assert client.is_authenticated()


def test_authenticate_token(client, token):
    assert not client.is_authenticated()
    client.authenticate(token=token)
    assert client.is_authenticated()


def test_self_unauthenticated(client):
    user = client.me()
    assert user.is_guest is True
    assert user == AnonymousUser()


def test_self_authenticated(client, user1_access_token):
    client.authenticate(token=user1_access_token)
    user1 = client.me()
    assert user1.is_guest is False
    assert user1.username == "user1"


def test_get_user(client, user1_access_token):
    client.authenticate(token=user1_access_token)
    me = client.me()
    user1 = client.user(me.identifier)
    assert user1.is_guest is False
    assert user1.username == "user1"
    assert user1 == me
