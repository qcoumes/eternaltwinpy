from datetime import datetime
from types import TracebackType
from typing import Any, Literal, Self
from urllib.parse import urljoin

import aiohttp

from eternaltwin.clients.abc import ClientABC
from eternaltwin.exceptions import RequestError
from eternaltwin.responses import Response
from eternaltwin.tokens import Token
from eternaltwin.users import AnonymousUser, User


class Eternaltwin(ClientABC):
    """Synchronous clients handling communication with EternalTwin."""

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
        super().__init__(url, client_id, client_secret, redirect_uri, timeout, verify_ssl, allow_redirects)
        self.timeout = aiohttp.ClientTimeout(self.timeout)
        self._session = None
        self._session_count = 0

    @property
    def session(self) -> aiohttp.ClientSession:
        """Return the `aiohttp` session."""
        assert self._session is not None, f"{self.__class__.__name__} must be used within a context manager."
        return self._session

    async def __aenter__(self) -> Self:
        """Create a new `aiohttp` session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        self._session_count += 1
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None:
        """Close the `aiohttp` session."""
        self._session_count -= 1
        if self._session_count == 0 and self._session is not None:
            await self.session.close()
            self._session = None

    async def _request(
        self,
        method: Literal["get", "post", "delete", "put", "patch", "options"],
        endpoint: str,
        raise_on_error: bool = True,
        **kwargs: Any,
    ) -> Response:
        """Helper to make a request to EternalTwin."""
        if self.token is not None and "Authorization" not in kwargs.get("headers", {}):
            kwargs["headers"] = kwargs.get("headers", {}) | {"Authorization": f"Bearer {self.token.access_token}"}
        url = urljoin(self.url, endpoint)
        async with self.session.request(
            method, url, **kwargs, timeout=self.timeout, ssl=self.verify_ssl, allow_redirects=self.allow_redirects
        ) as response:
            wrapped = await Response.from_aiohttp(response)
            if wrapped.status_code >= 300 and raise_on_error:
                raise RequestError(wrapped)
            return wrapped

    async def _get(self, endpoint: str, raise_on_error: bool = True, **kwargs: Any) -> Response:
        """Helper to make an authenticated GET request to EternalTwin."""
        async with self:
            return await self._request("get", endpoint, raise_on_error=raise_on_error, **kwargs)

    async def _post(self, endpoint: str, raise_on_error: bool = True, **kwargs: Any) -> Response:
        """Helper to make an authenticated POST request to EternalTwin."""
        async with self:
            return await self._request("post", endpoint, raise_on_error=raise_on_error, **kwargs)

    async def authenticate(self, authorization_code: str = None, token: Token = None) -> Token:
        """Authenticate the client using either an authorization code or an existing token."""
        if not (bool(authorization_code) ^ bool(token)):
            raise ValueError("Either authorization_code xor token must be provided.")

        if token:
            self.token = token
        else:
            headers = {
                "Authorization": f"Basic {self._basic_auth_token()}",
            }
            data = {"grant_type": "authorization_code", "code": authorization_code}
            response = await self._post(self.token_uri, headers=headers, json=data)
            self.token = Token(**response.json())
        return self.token

    async def me(self) -> User | AnonymousUser:
        """Retrieve current user's profile."""
        data = (await self._get(self.self_uri)).json()
        if data.get("type") == "Guest":
            return AnonymousUser()
        return await self.user(data["user"]["id"])

    async def user(self, user_id: str) -> User:
        """Retrieve current user's profile."""
        data = (await self._get(self.users_uri.format(user_id=user_id))).json()
        return User(
            identifier=data["id"],
            username=data["display_name"]["current"]["value"],
            is_administrator=data["is_administrator"],
            created_at=data["created_at"] and datetime.fromisoformat(data["created_at"]),
            deleted_at=data["deleted_at"] and datetime.fromisoformat(data["deleted_at"]),
        )
