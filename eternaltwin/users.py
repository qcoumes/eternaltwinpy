from datetime import datetime
from typing import Any, Self

from eternaltwin.connections import async_connections, connections
from eternaltwin.tokens import Token


class User:
    """Represents a user."""

    def __init__(
        self,
        identifier: str,
        username: str,
        is_administrator: bool | None,
        created_at: datetime | None,
        deleted_at: datetime | None,
        token: Token | None = None,
    ) -> None:
        self.identifier = identifier
        self.username = username
        self.is_administrator = is_administrator
        self.created_at = created_at
        self.deleted_at = deleted_at
        self.token = token

    def __str__(self) -> str:
        return f"<User {self.username}>"

    def __repr__(self) -> str:
        return (
            f"User("
            f"    identifier={self.identifier!r},"
            f"    username={self.username!r},"
            f"    is_administrator={self.is_administrator!r},"
            f"    created_at={self.created_at!r},"
            f"    deleted_at={self.deleted_at!r},"
            f"    token={self.token!r}"
            f")"
        )

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, User) and self.identifier == other.identifier

    @classmethod
    def _from_response(cls, using: str | None, data: dict[str, Any]) -> Self:
        """Create an instance from the typical API response data."""
        return cls(
            identifier=data["id"],
            username=data["display_name"]["current"]["value"],
            is_administrator=data.get("is_administrator", None),
            created_at=data.get("created_at") and datetime.fromisoformat(data["created_at"]),
            deleted_at=data.get("deleted_at") and datetime.fromisoformat(data["deleted_at"]),
        )

    @classmethod
    def start_authorization(cls, expiration: int = 600, nonce: str = None, using: str = None) -> tuple[str, str]:
        """Start the authorization process, returning a state and an authorization URL.

        Parameters
        ----------
        expiration: int, optional
            Expiration time in seconds. Default to 600 seconds.
        nonce: str, optional
            An optional nonce value used to guarantee the state to be unique. If
            not provided, a random one will be generated.
        using: str, optional
            The name of the connection to use, default to `None` for the default
            connection.

        Return
        ------
        tuple[str, str]
            The generated state and the authorization URL.
        """
        client = connections.get_connection(using)
        state = client.generate_state(expiration, nonce)
        url = client.authorization_url(state=state)
        return state, url

    @classmethod
    def from_token(cls, token: Token, using: str | None = None) -> Self:
        """Retrieve the user associated with the provided token."""
        data = connections.get_connection(using).users.me(token=token).json()
        user = cls._from_response(using, data["user"])
        user.token = token
        return user

    @classmethod
    async def afrom_token(cls, token: Token, using: str | None = None) -> Self:
        """Retrieve the user associated with the provided token."""
        data = (await async_connections.get_connection(using).users.me(token=token)).json()
        user = cls._from_response(using, data["user"])
        user.token = token
        return user

    @classmethod
    def from_authorization_code(
        cls, authorization_code: str, callback_state: str, expected_state: str | None = None, using: str | None = None
    ) -> Self:
        """Retrieve the user associated with the provided authorization code.

        Validate the state received from the authorization server.

        An expected state can be provided to check if the state received from the
        authorization server matches the expected one.

        Raises
        ------
        InvalidStateError
            If action or authorization server does not match, the JWT is
            expired, or the received state does not match the expected one (if
            provided).
        """
        client = connections.get_connection(using)
        client.validate_state(callback_state, expected_state)
        token = connections.get_connection(using).token(authorization_code)
        return cls.from_token(token, using)

    @classmethod
    async def afrom_authorization_code(
        cls, authorization_code: str, callback_state: str, expected_state: str | None = None, using: str | None = None
    ) -> Self:
        """Retrieve the user associated with the provided authorization code.

        Validate the state received from the authorization server.

        An expected state can be provided to check if the state received from the
        authorization server matches the expected one.

        Raises
        ------
        InvalidStateError
            If action or authorization server does not match, the JWT is
            expired, or the received state does not match the expected one (if
            provided).
        """
        client = async_connections.get_connection(using)
        client.validate_state(callback_state, expected_state)
        token = await async_connections.get_connection(using).token(authorization_code)
        return await cls.afrom_token(token, using)

    @classmethod
    def get(cls, user_id: str, using: str | None = None) -> Self:
        """Retrieve a specific user."""
        data = connections.get_connection(using).users.get(user_id=user_id).json()
        return cls._from_response(using, data)

    @classmethod
    async def aget(cls, user_id: str, using: str | None = None) -> Self:
        """Retrieve a specific user."""
        data = (await async_connections.get_connection(using).users.get(user_id=user_id)).json()
        return cls._from_response(using, data)

    @classmethod
    def search(cls, query: str | None = None, limit: int = 20, offset: int = 0, using: str | None = None) -> list[Self]:
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
        response = connections.get_connection(using).users.search(query=query, limit=limit, offset=offset)
        return [cls._from_response(using, user) for user in response.json()["items"]]

    @classmethod
    async def asearch(
        cls, query: str | None = None, limit: int = 20, offset: int = 0, using: str | None = None
    ) -> list[Self]:
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
        response = await async_connections.get_connection(using).users.search(query=query, limit=limit, offset=offset)
        return [cls._from_response(using, user) for user in response.json()["items"]]

    @classmethod
    def count(cls, query: str | None = None, using: str | None = None) -> int:
        """Search the number of users matching the query.

        If query is not provided, return the total number of users.
        """
        return connections.get_connection(using).users.search(query=query, limit=0).json()["count"]

    @classmethod
    async def acount(cls, query: str | None = None, using: str | None = None) -> int:
        """Search the number of users matching the query.

        If query is not provided, return the total number of users.
        """
        return (await async_connections.get_connection(using).users.search(query=query, limit=0)).json()["count"]

    @property
    def is_authenticated(self) -> bool:
        """Whether the user is authenticated."""
        return self.token is not None

    def logout(self) -> None:
        """Logout the user by deleting their token."""
        if self.token is not None:
            self.token = None
