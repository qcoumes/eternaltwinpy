from urllib.parse import parse_qs, urljoin, urlparse

import requests

from eternaltwin.connections import async_connections, configure, connections
from eternaltwin.users import User
from tests.conftest import ETWIN_USER1_PASSWORD, ETWIN_USER1_USERNAME


def test_synchronous_authorization_process(configuration):
    configure(**configuration)
    client = connections.get_connection()
    state, url = User.start_authorization()

    # Authenticate the user on EternalTwin and retrieve the session_id
    session_id = requests.put(
        urljoin(client.url, "api/v1/auth/self?method=Etwin"),
        json={"login": ETWIN_USER1_USERNAME, "password": ETWIN_USER1_PASSWORD},
    ).cookies["sid"]

    # Send a request using authorization URL with the session_id cookie. It
    # will immediately try to redirect the the redirect_uri with the
    # authorization code in the query params since the user is already
    # authenticated.
    response = requests.get(url, cookies={"sid": session_id}, allow_redirects=False)
    query_params = parse_qs(urlparse(response.headers["Location"]).query)
    state, code = query_params["state"][0], query_params["code"][0]
    user = User.from_authorization_code(code, state)
    assert user.is_authenticated
    assert user.username == ETWIN_USER1_USERNAME


async def test_asynchronous_authorization_process(configuration):
    configure(**configuration)
    client = async_connections.get_connection()
    state, url = User.start_authorization()

    # Authenticate the user on EternalTwin and retrieve the session_id
    session_id = requests.put(
        urljoin(client.url, "api/v1/auth/self?method=Etwin"),
        json={"login": ETWIN_USER1_USERNAME, "password": ETWIN_USER1_PASSWORD},
    ).cookies["sid"]

    # Send a request using authorization URL with the session_id cookie. It
    # will immediately try to redirect the the redirect_uri with the
    # authorization code in the query params since the user is already
    # authenticated.
    response = requests.get(url, cookies={"sid": session_id}, allow_redirects=False)
    query_params = parse_qs(urlparse(response.headers["Location"]).query)
    state, code = query_params["state"][0], query_params["code"][0]
    user = await User.afrom_authorization_code(code, state)
    assert user.is_authenticated
    assert user.username == ETWIN_USER1_USERNAME


def test_get(configuration):
    configure(**configuration)
    client = connections.get_connection()
    data = client.users.search(query=ETWIN_USER1_USERNAME, limit=1).json()
    user_id = data["items"][0]["id"]
    user = User.get(user_id)
    assert not user.is_authenticated
    assert user.identifier == user_id
    assert user.username == ETWIN_USER1_USERNAME


async def test_aget(configuration):
    configure(**configuration)
    async_client = async_connections.get_connection()
    data = (await async_client.users.search(query=ETWIN_USER1_USERNAME, limit=1)).json()
    user_id = data["items"][0]["id"]
    user = await User.aget(user_id)
    assert not user.is_authenticated
    assert user.identifier == user_id
    assert user.username == ETWIN_USER1_USERNAME


def test_search(configuration):
    configure(**configuration)
    users = User.search("user1")
    assert len(users) == 1
    assert users[0].username == "user1"

    users = User.search("user")
    assert len(users) == 2

    users = User.search("user", limit=1)
    assert len(users) == 1
    assert users[0].username == "user1"

    users = User.search("user", limit=1, offset=1)
    assert len(users) == 1
    assert users[0].username == "user2"


async def test_asearch(configuration):
    configure(**configuration)
    users = await User.asearch("user1")
    assert len(users) == 1
    assert users[0].username == "user1"

    users = await User.asearch("user")
    assert len(users) == 2

    users = await User.asearch("user", limit=1)
    assert len(users) == 1
    assert users[0].username == "user1"

    users = await User.asearch("user", limit=1, offset=1)
    assert len(users) == 1
    assert users[0].username == "user2"


def test_count(configuration):
    configure(**configuration)
    assert User.count() == 8
    assert User.count(query="user") == 2
    assert User.count(query="user1") == 1


async def test_acount(configuration):
    configure(**configuration)
    assert await User.acount() == 8
    assert await User.acount(query="user") == 2
    assert await User.acount(query="user1") == 1


def test_logout(configuration, user1_token):
    configure(**configuration)
    user = User.search("user1", limit=1)[0]
    user.token = user1_token
    assert user.is_authenticated
    user.logout()
    assert not user.is_authenticated
    user.logout()
    assert not user.is_authenticated
