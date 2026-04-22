import abc
from typing import TYPE_CHECKING, Awaitable, Generic, TypeVar

from eternaltwin.clients.abc.clients import NamespacedClientABC
from eternaltwin.responses import Response
from eternaltwin.tokens import Token

if TYPE_CHECKING:
    from eternaltwin.clients.abc.clients import ClientABC  # noqa: F401

C = TypeVar("C", bound="ClientABC")


class UserClientABC(NamespacedClientABC[C], Generic[C]):
    """Base class for sub-client handling interaction with users."""

    @abc.abstractmethod
    def me(self, token: Token = None) -> Response | Awaitable[Response]:
        """Retrieve currently authenticated user's profile."""

    @abc.abstractmethod
    def get(self, user_id: str, token: Token = None) -> Response | Awaitable[Response]:
        """Retrieve a user using their ID."""

    @abc.abstractmethod
    def search(
        self, query: str = None, limit: int = 20, offset: int = 0, token: Token = None
    ) -> Response | Awaitable[Response]:
        """Search for users matching the query.

        Parameters
        ----------
        query: str, optional
            An optional query to use against the user's username, default to `None`.
        limit: int, optional
            The maximum number of users to return, default to `20`.
        offset: int, optional
            The offset to start returning users from, default to `0`.
        """
