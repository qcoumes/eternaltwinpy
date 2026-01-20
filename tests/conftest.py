import os
import time
from urllib.parse import parse_qs, urljoin, urlparse

import pytest
import requests

from eternaltwin.clients.abc import ClientABC
from eternaltwin.clients.asyncio import Eternaltwin as AsyncEternaltwin
from eternaltwin.clients.sync import Eternaltwin
from eternaltwin.keys import EdDSAKey, ES256Key, HS256Key, PS256Key, RS256Key
from eternaltwin.states import State
from eternaltwin.tokens import Token

# Correspond to the EternalTwin instance in docker/docker-compose.yml
ETWIN_URL = f"http://localhost:{os.getenv('ETWIN_PORT', 50320)}"
ETWIN_CLIENT_ID = "python_client@clients"
ETWIN_CLIENT_SECRET = "dev_secret"
ETWIN_REDIRECT_URL = "http://localhost:8000/oauth/callback"

# Dummy parameters for testing purpose
ETWIN_DUMMY_URL = "http://localhost:50322"
ETWIN_DUMMY_CLIENT_ID = "myclient"
ETWIN_DUMMY_CLIENT_SECRET = "mysecret"
ETWIN_DUMMY_REDIRECT_URL = "http://localhost:8081/oauth/callback"

# Users defined in docker/eternaltwin/eternatwin/eternaltwin.dev.toml
ETWIN_USER1_USERNAME = "user1"
ETWIN_USER1_PASSWORD = "31323334353637383931"  # Works for password "1234567891", probably a hashed by the ET client
ETWIN_USER2_USERNAME = "user2"
ETWIN_USER2_PASSWORD = "31323334353637383932"


def _get_authorization_code(client: ClientABC, username: str, password: str) -> str:
    # Authenticate the user on EternalTwin and retrieve the session_id
    session_id = requests.put(
        urljoin(client.url, "api/v1/auth/self?method=Etwin"),
        json={"login": username, "password": password},
    ).cookies["sid"]

    # Send a request using authentication URL with the session_id cookie. It
    # will immediately try to redirect the the redirect_uri with the
    # authorization code in the query params since the user is already
    # authenticated.
    key = HS256Key("secret")
    state = State.new(client.url, key)
    url = client.authentication_url(state)
    r = requests.get(url, cookies={"sid": session_id}, allow_redirects=False)

    # Parse location header to get "code" query param and check state is the
    # same
    query_params = parse_qs(urlparse(r.headers["Location"]).query)
    assert state == State.from_jwt(query_params["state"][0], client.url, key)
    return query_params["code"][0]


def _get_token(client: ClientABC, username: str, password: str) -> Token:
    authorization_code = _get_authorization_code(client, username, password)
    return client.authenticate(authorization_code=authorization_code)


@pytest.fixture
def client() -> Eternaltwin:
    """Fixture for an Eternaltwin client."""
    return Eternaltwin(ETWIN_URL, ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL)


@pytest.fixture
def async_client() -> AsyncEternaltwin:
    """Fixture for an async Eternaltwin client."""
    return AsyncEternaltwin(ETWIN_URL, ETWIN_CLIENT_ID, ETWIN_CLIENT_SECRET, ETWIN_REDIRECT_URL)


@pytest.fixture
def payload():
    """Fixture for a state payload to be used in tests."""
    timestamp = int(time.time())
    return {"a": "authorize", "as": ETWIN_URL, "iat": timestamp, "rfp": timestamp, "exp": timestamp + 600}


@pytest.fixture
def state(hs256_key):
    """Fixture for a state to be used in tests."""
    return State.new(ETWIN_URL, hs256_key)


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
def user1_access_token(client: ClientABC) -> Token:
    """Fixture to get a token for user1."""
    return _get_token(client, ETWIN_USER1_USERNAME, ETWIN_USER1_PASSWORD)


@pytest.fixture
def user2_access_token(client: ClientABC) -> Token:
    """Fixture to get a token for user2."""
    return _get_token(client, ETWIN_USER2_USERNAME, ETWIN_USER2_PASSWORD)


@pytest.fixture
def hs256_key():
    """Fixture for HS256 symmetric key."""
    return HS256Key("test_secret_key_for_hmac_sha256")


@pytest.fixture
def rs256_key():
    """Fixture for RS256 asymmetric key."""
    private_key = """-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQDDbr5Fwr3mYkrZDrnhtWWEcBLENkcDiS0vTlPPk0lBIGPjBi4H
kvPeCYYwHXVW5RRtrC6p7kuvT+IL3/cFFnrXAXHlpmqk9whDuf/j6dBg4lTFrdRA
wEc2Cn7NAFF0mOiafJnvwWIeeVwCWHshNCbGJxFOVtaNVMFZGR6sJ8OydwIDAQAB
AoGAYEiPNY9cP8TtW0MGEU1tVnJgzIpxMizDNitA32ORE6UBkTfaNaEQxLOsiMf6
p3T1O5M46j+cyiJxG6ib6sXIfocqsDDdeDwf3HZCCDqWHfFFOcKQkHml3iHEXo5Y
7Rj5Pczty3+Men198GmeloQnz6xkaJQnJj8plhfmNeYTyQECQQD7mVvlo6nF+bcx
xzGkX9ql9M0Nva+4sLDQIA5tqU5F1D4jGtM0D8Yu6wQxQsLiVgl5a/oytlVCdfZs
afFV4+01AkEAxtngDUqWhFapybE5RnewCl4bk5L9ihMpEYB8dUsSZIkkvJuWe+D7
GQbUOuQiKsGcS85DtWF39T7I6R6sg6cSewJAIl7z/+4YzlPr49/7dyIlI5DKxnrI
W6m/rd8DOZXsfHufNXp/qdgR0e0HOJePOg5Y4v6OQolIInks/eiHMJ2flQJAATXs
XkhY+D9K01aH4bzyzm1aP6DCeGe7dUbR+yjU2NXY6mkMFn79KF7ZRe6Dor0BBZkg
4mbQgya5tGmiZT7MJwJANynVEMsgGd04wyKJZE9oT921dbPGjcbnW8yZQjH7Rw35
WiU3bltbteU3snWlYZ7KMdI4hFL1n5TQfnYU8ZuNXQ==
-----END RSA PRIVATE KEY-----"""
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQDDbr5Fwr3mYkrZDrnhtWWEcBLENkcDiS0vTlPPk0lBIGPjBi4HkvPeCYYwHXVW5RRtrC6p7kuvT+IL3/cFFnrXAXHlpmqk9whDuf/j6dBg4lTFrdRAwEc2Cn7NAFF0mOiafJnvwWIeeVwCWHshNCbGJxFOVtaNVMFZGR6sJ8Oydw=="
    return RS256Key(public_key, private_key)


@pytest.fixture
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


@pytest.fixture
def ps256_key():
    """Fixture for PS256 asymmetric key (uses same RSA keys as RS256)."""
    private_key = """-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAL5BtN58BsApeRZL
gkK4g95Vf3afsKsKJ05W0gWcvYTUN1yFo0tcd/Brl0WLd1vjslosjudM4UhizoAn
7pJaSHcliWv2miS/M74bFE30WM7vStndtd2+NEDFDfS9dywz4AfYP2wQALNUwKVH
p2jAWoZg4C/Rg9pKg+wvMoE8WbBTAgMBAAECgYB9zyNUT/2Cyqn4lTvw9OS2fCEK
hzSjFdbCFeVRssEb+d0WAITny6DASdVBNqVaDSqeOILS7uK2JChbVIyNGMh7ZUud
gIsQdPtKMNVG6IHqZBpj8Q46eVwFNebh/PpbARcX4ovOwKbSRi6wHWWYTO8jyIrL
TaHbqPFFQc6/qeoUQQJBAOKaJ2Yo3Pi2BPhtr0M6trkV86ZQ9ATmedhgmUIyoscf
guQ1on95zSsn+Fox3mwtLLm3osR7QJUbPPTPI9OsaiECQQDW8HTUue7Umtm8hkkT
BLxQPa1W3F13RTJJx6aiNjlKhnIlm3gB1FS7uQuPb6KLkPiEWAoxOFi2hRdLbKj2
wJPzAkEAwAsRVP1QuN/aOokKvhlmflniUpPNGtIRdZX4jSfI2KUWEz55Zzvc67RG
QHp/HIL0orjFE2u5giTBdmCO5nf6wQJASdx9uXBfky3XbwKSb/erosNfIr89WzQr
MNFsAMgzbdm/tg6z8aT+rTfMsjDBocZisE/0yK89RRN9Ssz/TzQkYwJAE9eLzRaF
KR7iN341M7hISnG5Jh9Y/XKjYFj/gsRrZnWrIpOOIWseORRkp4y3RXSu2MCO+kz8
j4us1Ig4DACwXw==
-----END PRIVATE KEY-----
"""
    public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+QbTefAbAKXkWS4JCuIPeVX92
n7CrCidOVtIFnL2E1DdchaNLXHfwa5dFi3db47JaLI7nTOFIYs6AJ+6SWkh3JYlr
9pokvzO+GxRN9FjO70rZ3bXdvjRAxQ30vXcsM+AH2D9sEACzVMClR6dowFqGYOAv
0YPaSoPsLzKBPFmwUwIDAQAB
-----END PUBLIC KEY-----"""
    return PS256Key(public_key, private_key)


@pytest.fixture
def eddsa_key():
    """Fixture for EdDSA asymmetric key."""
    private_key = """-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIJ+DYvh6SEqVTm50DFtMDoQikTmiCqirVv9mWG9qfSnF
-----END PRIVATE KEY-----"""
    public_key = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAJrQLj5P/89iXES9+vFgrIy29clF9CC/oPPsw3c5D0bs=
-----END PUBLIC KEY-----"""
    return EdDSAKey(public_key, private_key)
