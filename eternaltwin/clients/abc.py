import abc
import base64
from typing import Any, Awaitable, TypeVar
from urllib.parse import urlencode, urljoin

from eternaltwin.responses import Response
from eternaltwin.states import State
from eternaltwin.tokens import Token
from eternaltwin.users import AnonymousUser, User

C = TypeVar("C", bound="ClientABC")


class ClientABC(abc.ABC):
    """Base class for client handling communication with EternalTwin."""

    def __init__(
        self,
        url: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        timeout: int = 5,
        verify_ssl: bool = True,
        allow_redirects: bool = True,
    ) -> None:
        self.url = url
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.allow_redirects = allow_redirects
        self.token: Token | None = None

    @property
    def authorization_uri(self) -> str:
        """Return the OAuth2 authorization URI."""
        return urljoin(self.url, "/oauth/authorize")

    @property
    def token_uri(self) -> str:
        """Return the OAuth2 token URI."""
        return urljoin(self.url, "/oauth/token")

    @property
    def self_uri(self) -> str:
        """Return the URI to retrieve the current user's profile."""
        return urljoin(self.url, "/api/v1/auth/self")

    @property
    def users_uri(self) -> str:
        """Return the URI to retrieve the list of users."""
        return urljoin(self.url, "/api/v1/users/{user_id}")

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

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated.

        Note that the presence of a token does not guarantee that it is still
        valid.
        """
        return self.token is not None and not self.token.has_expired()

    def authentication_url(self, state: State) -> str:
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
            "state": state.jwt,
            "redirect_uri": self.redirect_uri,
        }
        return f"{self.authorization_uri}?{urlencode(params)}"

    @abc.abstractmethod
    def _get(self, endpoint: str, raise_on_error: bool = True, **kwargs: Any) -> Response | Awaitable[Response]:
        """Helper to make an authenticated GET request to EternalTwin."""
        pass

    @abc.abstractmethod
    def _post(self, endpoint: str, raise_on_error: bool = True, **kwargs: Any) -> Response | Awaitable[Response]:
        """Helper to make an authenticated POST request to EternalTwin."""
        pass

    @abc.abstractmethod
    def authenticate(self, *, authorization_code: str = None, token: Token = None) -> Token | Awaitable[Token]:
        """Authenticate the client using either an authorization code or an existing token."""
        pass

    @abc.abstractmethod
    def me(self) -> User | AnonymousUser | Awaitable[User | AnonymousUser]:
        """Retrieve current user's profile."""
        pass

    @abc.abstractmethod
    def user(self, user_id: str) -> User | Awaitable[User]:
        """Retrieve current user's profile."""
        pass
