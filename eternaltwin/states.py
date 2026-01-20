import time
from typing import Any, Self

from eternaltwin.exceptions import InvalidStateError
from eternaltwin.keys import KeyABC


class State:
    """Represents an authorization state."""

    def __init__(self, a: str, as_: str, iat: int, rfp: int, exp: int, key: KeyABC):
        """Create a new state.

        Parameters
        ----------
        a: str
            Action.
        as_: str
            Authorization server URL.
        iat: int
            Issued at timestamp.
        rfp: int
            Request forgery protection as a timestamp.
        exp: int
            Expiration timestamp.
        key: KeyABC
            Key used to encode the state.
        """
        self.a = a
        self.as_ = as_
        self.iat = iat
        self.rfp = rfp
        self.exp = exp
        self.key = key

    def __hash__(self) -> int:
        return hash(self.jwt)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and hash(self) == hash(other)

    @property
    def jwt(self) -> str:
        """Return the state as a JWT."""
        return self.key.encode({"a": self.a, "as": self.as_, "iat": self.iat, "rfp": self.rfp, "exp": self.exp})

    @classmethod
    def new(cls, url: str, key: KeyABC, expiration: int = 600) -> Self:
        """Create e new state using given parameters.

        Parameters
        ----------
        url: str
            URL of the authorization server.
        key: KeyABC
            Key used to encode the state.
        expiration: int
            Expiration time in seconds.
        """
        timestamp = int(time.time())
        return cls("authorize", url, timestamp, timestamp, timestamp + expiration, key)

    @classmethod
    def from_jwt(cls, jwt: str, url: str, key: KeyABC) -> Self:
        """Create a state from a JWT.

        Parameters
        ----------
        jwt: str
            JWT string representing the state.
        url: str
            URL of the authorization server.
        key: KeyABC
            Key used to decode the state.

        Raises
        ------
        InvalidStateError
            If the action or authorization server does not match, or the JWT is
            expired.
        """
        payload = key.decode(jwt)
        state = cls(payload["a"], payload["as"], payload["iat"], payload["rfp"], payload["exp"], key)

        if state.a != "authorize":
            raise InvalidStateError(f"Expected action 'authorize', got '{state.a}", state)
        if state.as_ != url:
            raise InvalidStateError(f"Expected authorization server '{url}', got '{state.as_}", state)
        if state.has_expired():
            raise InvalidStateError("Authorization expired", state)

        return state

    def has_expired(self) -> bool:
        """Check if the state has expired."""
        return self.exp < int(time.time())
