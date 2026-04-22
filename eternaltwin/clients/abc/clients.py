import abc
import base64
from typing import Any, Awaitable, Generic, TypeVar
from urllib.parse import urlencode, urljoin

from eternaltwin.clients import endpoints
from eternaltwin.exceptions import InvalidStateError
from eternaltwin.keys import KeyABC
from eternaltwin.states import State
from eternaltwin.tokens import Token

C = TypeVar("C", bound="ClientABC")


class NamespacedClientABC(abc.ABC, Generic[C]):
    """Base class for specific namespaced clients of `ClientABC`."""

    def __init__(self, client: C) -> None:
        self.client = client


class ClientABC(abc.ABC):
    """Base class for client handling communication with EternalTwin.

    Parameters
    ----------
    client_id: str
        The client ID obtained from EternalTwin when registering the app.
    client_secret: str
        The client secret obtained from EternalTwin when registering the app.
    redirect_uri: str
        The redirect URI registered with EternalTwin for the app.
    state_key: KeyABC
        The key used to sign and verify state tokens.
    url: str, optional
        The base URL for the EternalTwin API. If not provided, `scheme`, `host`,
        `port`, and `prefix` should be provided instead.
    scheme: str, optional
        The URL scheme to use (e.g., "http" or "https"). Required if `url` is
        not provided.
    host: str, optional
        The URL host to use (e.g., "eternaltwin.org"). Required if `url` is not
        provided.
    port: str or int, optional
        The URL port to use. Required if `url` is not provided.
    prefix: str, optional
        The URL prefix to use. Default to `/`, only used if `url` is not
        provided.
    timeout: int, optional
        The timeout for API requests in seconds. Default is 5 seconds.
    verify_ssl: bool, optional
        Whether to verify SSL certificates for API requests. Default is True.
    allow_redirects: bool, optional
        Whether to allow redirects for API requests. Default is False.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        state_key: KeyABC,
        *,
        url: str = None,
        scheme: str = "http",
        host: str = None,
        port: str | int = None,
        prefix: str = "/",
        timeout: int = 5,
        verify_ssl: bool = True,
        allow_redirects: bool = False,
    ) -> None:

        match (url, scheme, host, port, prefix):
            case (str(), _, None, _, _):
                url = url
            case (None, str(), str(), _, str()):
                port = f":{port}" if port else ""
                url = f"{scheme}://{host}{port}{prefix}"
            case _:  # pragma: no cover
                raise ValueError("You must provide either `url`, or `scheme`, `host`, `port` and `prefix`.")

        self.url: str = url
        self.client_id = client_id
        self.client_secret = client_secret
        self.state_key = state_key
        self.redirect_uri = redirect_uri
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.allow_redirects = allow_redirects

    def __hash__(self) -> int:
        return hash(
            (
                self.url,
                self.client_id,
                self.client_secret,
                self.redirect_uri,
                self.timeout,
                self.verify_ssl,
                self.allow_redirects,
            )
        )

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and hash(self) == hash(other)

    def _basic_auth_token(self) -> str:
        """Return the basic auth token for the client encoded as base64."""
        return base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

    def authorization_url(self, state: str) -> str:
        """Create an OAuth authorization request URL.

        The result URL contains all the information required for the user to
        grant the requested authorization and then call back the app and resume
        handling with the provided state.
        """
        params = {
            "response_type": "code",
            "access_type": "offline",
            "client_id": self.client_id,
            "scope": "base",
            "state": state,
            "redirect_uri": self.redirect_uri,
        }
        return f"{urljoin(self.url, endpoints.AUTHORIZATION)}?{urlencode(params)}"

    @abc.abstractmethod
    def token(self, authorization_code: str) -> Token | Awaitable[Token]:
        """Retrieve a token using the provided authorization code."""
        pass

    def generate_state(self, expiration: int = 600, nonce: str = None) -> str:
        """Generate a new state using the client's URL and key.

        Parameters
        ----------
        expiration: int, optional
            Expiration time in seconds. Default to 600 seconds.
        nonce: str, optional
            An optional nonce value used to guarantee the state to be unique. If
            not provided, a random one will be generated.

        Return
        -----
        str
            The generated state encoded as a JWT.
        """
        return State.new(self.url, self.state_key, expiration, nonce).jwt

    def validate_state(self, state: str, expected: str = None) -> None:
        """Validate the state received from the authorization server.

        An expected state can be provided to check if the state received from
        the authorization server matches the expected one.

        Raises
        ------
        InvalidStateError
            If action or authorization server does not match, the JWT is
            expired, or the received state does not match the expected one (if
            provided).
        """
        validated = State.from_jwt(state, self.url, self.state_key)
        if expected is not None and state != expected:
            raise InvalidStateError(f"Received state does not match, expected: '{expected}', got '{state}'", validated)
