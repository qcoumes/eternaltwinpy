from typing import TYPE_CHECKING

from eternaltwin.clients import endpoints
from eternaltwin.clients.abc.users import UserClientABC
from eternaltwin.responses import Response
from eternaltwin.tokens import Token

if TYPE_CHECKING:
    from eternaltwin.clients.asyncio.clients import Eternaltwin


class UserClient(UserClientABC):
    """Synchronous implementation of `UserClientABC` using `requests`."""

    client: "Eternaltwin"

    async def me(self, token: Token = None) -> Response:
        """Retrieve currently authenticated user's profile."""
        return await self.client.get(endpoints.SELF, token=token)

    async def get(self, user_id: str, token: Token = None) -> Response:
        """Retrieve a user using their ID."""
        return await self.client.get(endpoints.USER.format(user_id=user_id), token=token)

    async def search(self, query: str = None, limit: int = 20, offset: int = 0, token: Token = None) -> Response:
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
        params = {"q": query or "", "limit": limit, "offset": offset}
        return await self.client.get(endpoints.USERS, params=params, token=token)
