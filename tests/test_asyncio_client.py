import base64
from urllib.parse import urlencode

import pytest

from eternaltwin.clients.asyncio import Eternaltwin
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


async def test_authenticate_no_authorization_code_nor_token(async_client):
    with pytest.raises(ValueError):
        await async_client.authenticate()


async def test_authenticate_both_authorization_code_and_token(async_client, token):
    with pytest.raises(ValueError):
        await async_client.authenticate(authorization_code="code", token=token)


async def test_authenticate_authorization_code(async_client, user1_authorization_code):
    assert not async_client.is_authenticated()
    await async_client.authenticate(authorization_code=user1_authorization_code)
    assert async_client.is_authenticated()


async def test_authenticate_token(async_client, token):
    assert not async_client.is_authenticated()
    await async_client.authenticate(token=token)
    assert async_client.is_authenticated()
    assert async_client.token.access_token == token.access_token
    assert async_client.token.refresh_token == token.refresh_token


async def test_self_unauthenticated(async_client):
    user = await async_client.me()
    assert user.is_guest is True
    assert user == AnonymousUser()


async def test_self_authenticated(async_client, user1_access_token):
    await async_client.authenticate(token=user1_access_token)
    user1 = await async_client.me()
    assert user1.is_guest is False
    assert user1.username == "user1"


async def test_get_user(async_client, user1_access_token):
    await async_client.authenticate(token=user1_access_token)
    me = await async_client.me()
    identifier = me.identifier
    user1 = await async_client.user(identifier)
    assert user1.is_guest is False
    assert user1.username == "user1"
    assert user1 == me
