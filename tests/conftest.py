import os
import secrets
import time
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse

import pytest
import requests

from eternaltwin.clients.abc.clients import ClientABC
from eternaltwin.clients.asyncio.clients import Eternaltwin as AsyncEternaltwin
from eternaltwin.clients.sync.clients import Eternaltwin
from eternaltwin.keys import EdDSAKey, ES256Key, HS256Key, PS256Key, RS256Key
from eternaltwin.states import _generate_nonce
from eternaltwin.tokens import Token

# Correspond to the EternalTwin instance in docker/docker-compose.yml
ETWIN_SCHEME = "http"
ETWIN_HOST = "localhost"
ETWIN_PORT = os.getenv("ETWIN_PORT", 50320)
ETWIN_URL = f"{ETWIN_SCHEME}://{ETWIN_HOST}:{ETWIN_PORT}/"
ETWIN_CLIENT_ID = "python_client@clients"
ETWIN_CLIENT_SECRET = "dev_secret"
ETWIN_REDIRECT_URL = "http://localhost:8000/oauth/callback"

# Dummy parameters for testing purpose
ETWIN_DUMMY_SCHEME = "http"
ETWIN_DUMMY_HOST = "localhost"
ETWIN_DUMMY_PORT = 50322
ETWIN_DUMMY_URL = f"{ETWIN_DUMMY_SCHEME}://{ETWIN_DUMMY_HOST}:{ETWIN_DUMMY_PORT}/"
ETWIN_DUMMY_CLIENT_ID = "myclient"
ETWIN_DUMMY_CLIENT_SECRET = "mysecret"
ETWIN_DUMMY_REDIRECT_URL = "http://localhost:8081/oauth/callback"

# Users defined in docker/eternaltwin/eternatwin/eternaltwin.dev.toml
ETWIN_USER1_USERNAME = "user1"
ETWIN_USER1_PASSWORD = "31323334353637383931"  # Works for password "1234567891", probably hashed by the ET client
ETWIN_USER2_USERNAME = "user2"
ETWIN_USER2_PASSWORD = "31323334353637383932"


def _get_authorization_code(client: ClientABC, username: str, password: str) -> str:
    # Authenticate the user on EternalTwin and retrieve the session_id
    session_id = requests.put(
        urljoin(client.url, "api/v1/auth/self?method=Etwin"),
        json={"login": username, "password": password},
    ).cookies["sid"]

    # Send a request using authorization URL with the session_id cookie. It
    # will immediately try to redirect the the redirect_uri with the
    # authorization code in the query params since the user is already
    # authenticated.
    state = client.generate_state()
    url = client.authorization_url(state)
    r = requests.get(url, cookies={"sid": session_id}, allow_redirects=False)

    # Parse location header to get "code" query param and check state is the
    # same
    query_params = parse_qs(urlparse(r.headers["Location"]).query)
    client.validate_state(query_params["state"][0], state)
    return query_params["code"][0]


def _get_token(client: Eternaltwin, username: str, password: str) -> Token:
    authorization_code = _get_authorization_code(client, username, password)
    return client.token(authorization_code)


@pytest.fixture(scope="session")
def configuration(hs256_key):
    """Fixture a valid dictionary that can be passed to `configure()`."""
    return {
        "default": {
            "url": ETWIN_URL,
            "client_id": ETWIN_CLIENT_ID,
            "client_secret": ETWIN_CLIENT_SECRET,
            "redirect_uri": ETWIN_REDIRECT_URL,
            "state_key": hs256_key,
        }
    }


@pytest.fixture(scope="session")
def client(hs256_key) -> Eternaltwin:
    """Fixture for an Eternaltwin client."""
    return Eternaltwin(ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, hs256_key, url=ETWIN_URL)


@pytest.fixture(scope="session")
def async_client(hs256_key) -> AsyncEternaltwin:
    """Fixture for an async Eternaltwin client."""
    return AsyncEternaltwin(ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL, hs256_key, url=ETWIN_URL)


@pytest.fixture
def payload():
    """Fixture for a state payload to be used in tests."""
    timestamp = int(time.time())
    return {
        "a": "authorize",
        "as": ETWIN_URL,
        "iat": timestamp,
        "rfp": timestamp,
        "exp": timestamp + 600,
        "nonce": _generate_nonce(128),
    }


@pytest.fixture
def token():
    """Fixture for a token to be used in tests."""
    return Token(
        access_token="access", refresh_token="refresh", expires_in=int(time.time()) + 3600, token_type="Bearer"
    )


@pytest.fixture
def user1_authorization_code(client: ClientABC) -> str:
    """Fixture to get an authorization code for user1."""
    return _get_authorization_code(client, ETWIN_USER1_USERNAME, ETWIN_USER1_PASSWORD)


@pytest.fixture
def user2_authorization_code(client: ClientABC) -> str:
    """Fixture to get an authorization code for user2."""
    return _get_authorization_code(client, ETWIN_USER2_USERNAME, ETWIN_USER2_PASSWORD)


@pytest.fixture
def user1_token(client: Eternaltwin) -> Token:
    """Fixture to get a token for user1."""
    return _get_token(client, ETWIN_USER1_USERNAME, ETWIN_USER1_PASSWORD)


@pytest.fixture
def user2_token(client: Eternaltwin) -> Token:
    """Fixture to get a token for user2."""
    return _get_token(client, ETWIN_USER2_USERNAME, ETWIN_USER2_PASSWORD)


@pytest.fixture(scope="session")
def hs256_key(scope="session"):
    """Fixture for HS256 symmetric key."""
    return HS256Key(secrets.token_hex(32))


@pytest.fixture(scope="session")
def rs256_key():
    """Fixture for RS256 asymmetric key."""
    private_key = (Path(__file__).parent / "keys" / "test_private.pem").read_text()
    public_key = (Path(__file__).parent / "keys" / "test_public.pub").read_text()
    return RS256Key(public_key, private_key)


@pytest.fixture(scope="session")
def es256_key():
    """Fixture for ES256 asymmetric key."""
    private_key = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIJzsjjhZuo7IU0xvWFDJEuNra1cwQ4PTfFYZSEKo8lMkoAoGCCqGSM49
AwEHoUQDQgAENPSoreSW9bZC9XJimHF42SoPCSt//cZwD+dXm/tetuCaaa16++6n
HACPWypSLCISqAEUGIu6CKnk0XvjOwQ3eA==
-----END EC PRIVATE KEY-----"""
    public_key = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAENPSoreSW9bZC9XJimHF42SoPCSt/
/cZwD+dXm/tetuCaaa16++6nHACPWypSLCISqAEUGIu6CKnk0XvjOwQ3eA==
-----END PUBLIC KEY-----"""
    return ES256Key(public_key, private_key)


@pytest.fixture(scope="session")
def ps256_key():
    """Fixture for PS256 asymmetric key (uses same RSA keys as RS256)."""

    private_key = (Path(__file__).parent / "keys" / "test_private.pem").read_text()
    public_key = (Path(__file__).parent / "keys" / "test_public.pem").read_text()
    return PS256Key(public_key, private_key)


@pytest.fixture(scope="session")
def eddsa_key():
    """Fixture for EdDSA asymmetric key."""
    private_key = """-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIJ+DYvh6SEqVTm50DFtMDoQikTmiCqirVv9mWG9qfSnF
-----END PRIVATE KEY-----"""
    public_key = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAJrQLj5P/89iXES9+vFgrIy29clF9CC/oPPsw3c5D0bs=
-----END PUBLIC KEY-----"""
    return EdDSAKey(public_key, private_key)
