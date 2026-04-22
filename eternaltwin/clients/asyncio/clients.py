from typing import Any, Literal
from urllib.parse import urljoin

import aiohttp

from eternaltwin.clients import endpoints
from eternaltwin.clients.abc.clients import ClientABC
from eternaltwin.clients.asyncio.users import UserClient
from eternaltwin.exceptions import RequestError
from eternaltwin.keys import KeyABC
from eternaltwin.responses import Response
from eternaltwin.tokens import Token


class Eternaltwin(ClientABC):
    """Asynchronous implementation of `ClientABC` using `aiohttp`."""

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
        super().__init__(
            client_id,
            client_secret,
            redirect_uri,
            state_key,
            url=url,
            scheme=scheme,
            host=host,
            port=port,
            prefix=prefix,
            timeout=timeout,
            verify_ssl=verify_ssl,
            allow_redirects=allow_redirects,
        )
        self.timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(timeout)
        self.users: UserClient = UserClient(self)

    async def _request(
        self,
        method: Literal["get", "post", "delete", "put", "patch", "options"],
        endpoint: str,
        raise_on_error: bool = True,
        token: Token = None,
        **kwargs: Any,
    ) -> Response:
        """Helper to make a request to EternalTwin."""
        if token is not None and "Authorization" not in kwargs.get("headers", {}):
            kwargs["headers"] = kwargs.get("headers", {}) | {"Authorization": f"Bearer {token.access_token}"}
        url = urljoin(self.url, endpoint)
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, **kwargs, timeout=self.timeout, ssl=self.verify_ssl, allow_redirects=self.allow_redirects
            ) as response:
                wrapped = await Response.from_aiohttp(response)
        if wrapped.status_code >= 300 and raise_on_error:
            raise RequestError(wrapped)
        return wrapped

    async def get(self, endpoint: str, raise_on_error: bool = True, token: Token = None, **kwargs: Any) -> Response:
        """Helper to make a GET request to EternalTwin."""
        return await self._request("get", endpoint, raise_on_error=raise_on_error, token=token, **kwargs)

    async def post(self, endpoint: str, raise_on_error: bool = True, token: Token = None, **kwargs: Any) -> Response:
        """Helper to make a POST request to EternalTwin."""
        return await self._request("post", endpoint, raise_on_error=raise_on_error, token=token, **kwargs)

    async def token(self, authorization_code: str) -> Token:
        """Retrieve a token using the provided authorization code."""
        headers = {"Authorization": f"Basic {self._basic_auth_token()}"}
        data = {"grant_type": "authorization_code", "code": authorization_code}
        response = await self.post(endpoints.TOKEN, headers=headers, json=data)
        return Token(**response.json())
