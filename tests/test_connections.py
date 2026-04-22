import pytest

from eternaltwin.clients.sync.clients import Eternaltwin
from eternaltwin.connections import Connections
from tests.conftest import (
    ETWIN_CLIENT_ID,
    ETWIN_CLIENT_SECRET,
    ETWIN_DUMMY_CLIENT_ID,
    ETWIN_DUMMY_CLIENT_SECRET,
    ETWIN_DUMMY_HOST,
    ETWIN_DUMMY_PORT,
    ETWIN_DUMMY_REDIRECT_URL,
    ETWIN_DUMMY_SCHEME,
    ETWIN_DUMMY_URL,
    ETWIN_HOST,
    ETWIN_PORT,
    ETWIN_REDIRECT_URL,
    ETWIN_SCHEME,
    ETWIN_URL,
)


def test_connections_getter_setter_deleter(client, async_client):
    connections = Connections(Eternaltwin)

    connections["default"] = client
    connections.add_connection("async", async_client)
    assert connections["default"] == client
    assert connections.get_connection() == client
    assert connections.get_connection("async") == async_client

    del connections["default"]
    with pytest.raises(KeyError):
        connections["default"]

    connections.remove_connection("async")
    with pytest.raises(KeyError):
        connections.get_connection("async")


def test_create_connection_url(hs256_key):
    connections = Connections(Eternaltwin)
    created = connections.create_connection(
        "default",
        url=ETWIN_URL,
        client_id=ETWIN_CLIENT_ID,
        client_secret=ETWIN_CLIENT_SECRET,
        redirect_uri=ETWIN_REDIRECT_URL,
        state_key=hs256_key,
    )
    witness = Eternaltwin(ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, hs256_key, url=ETWIN_URL)
    assert created == witness
    assert connections["default"] == witness
    assert connections.get_connection() == witness


def test_create_connection_url_parts(hs256_key):
    connections = Connections(Eternaltwin)
    created = connections.create_connection(
        "default",
        scheme=ETWIN_SCHEME,
        host=ETWIN_HOST,
        port=ETWIN_PORT,
        client_id=ETWIN_CLIENT_ID,
        client_secret=ETWIN_CLIENT_SECRET,
        redirect_uri=ETWIN_REDIRECT_URL,
        state_key=hs256_key,
    )
    witness = Eternaltwin(ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, hs256_key, url=ETWIN_URL)
    assert created == witness
    assert connections["default"] == witness
    assert connections.get_connection() == witness


def test_configure_url(hs256_key):
    connections = Connections(Eternaltwin)
    config = {
        "default": {
            "url": ETWIN_URL,
            "client_id": ETWIN_CLIENT_ID,
            "client_secret": ETWIN_CLIENT_SECRET,
            "redirect_uri": ETWIN_REDIRECT_URL,
            "state_key": hs256_key,
        },
        "another": {
            "url": ETWIN_DUMMY_URL,
            "client_id": ETWIN_DUMMY_CLIENT_ID,
            "client_secret": ETWIN_DUMMY_CLIENT_SECRET,
            "redirect_uri": ETWIN_DUMMY_REDIRECT_URL,
            "state_key": hs256_key,
            "timeout": 1,
            "verify_ssl": False,
            "allow_redirects": True,
        },
    }
    connections.configure(**config)

    witness_default = Eternaltwin(ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, hs256_key, url=ETWIN_URL)
    witness_another = Eternaltwin(
        ETWIN_DUMMY_CLIENT_ID,
        ETWIN_DUMMY_CLIENT_SECRET,
        ETWIN_DUMMY_REDIRECT_URL,
        hs256_key,
        url=ETWIN_DUMMY_URL,
        timeout=1,
        verify_ssl=False,
        allow_redirects=True,
    )

    assert connections["default"] == witness_default
    assert connections["another"] == witness_another


def test_configure_url_parts(hs256_key):
    connections = Connections(Eternaltwin)
    config = {
        "default": {
            "scheme": ETWIN_SCHEME,
            "host": ETWIN_HOST,
            "port": ETWIN_PORT,
            "client_id": ETWIN_CLIENT_ID,
            "client_secret": ETWIN_CLIENT_SECRET,
            "redirect_uri": ETWIN_REDIRECT_URL,
            "state_key": hs256_key,
        },
        "another": {
            "scheme": ETWIN_DUMMY_SCHEME,
            "host": ETWIN_DUMMY_HOST,
            "port": ETWIN_DUMMY_PORT,
            "client_id": ETWIN_DUMMY_CLIENT_ID,
            "client_secret": ETWIN_DUMMY_CLIENT_SECRET,
            "redirect_uri": ETWIN_DUMMY_REDIRECT_URL,
            "state_key": hs256_key,
            "timeout": 1,
            "verify_ssl": False,
            "allow_redirects": True,
        },
    }
    connections.configure(**config)

    witness_default = Eternaltwin(ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, hs256_key, url=ETWIN_URL)
    witness_another = Eternaltwin(
        ETWIN_DUMMY_CLIENT_ID,
        ETWIN_DUMMY_CLIENT_SECRET,
        ETWIN_DUMMY_REDIRECT_URL,
        hs256_key,
        url=ETWIN_DUMMY_URL,
        timeout=1,
        verify_ssl=False,
        allow_redirects=True,
    )
    assert connections["default"] == witness_default
    assert connections["another"] == witness_another
