from typing import Any, Literal
from urllib.parse import urljoin

import requests

from eternaltwin.clients import endpoints
from eternaltwin.clients.abc.clients import ClientABC
from eternaltwin.clients.sync.users import UserClient
from eternaltwin.exceptions import RequestError
from eternaltwin.keys import KeyABC
from eternaltwin.responses import Response
from eternaltwin.tokens import Token


class Eternaltwin(ClientABC):
    """Synchronous implementation of `ClientABC` using `requests`."""

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
        self.users: UserClient = UserClient(self)

    def _request(
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
        response = Response.from_requests(
            requests.request(
                method,
                urljoin(self.url, endpoint),
                **kwargs,
                timeout=self.timeout,
                verify=self.verify_ssl,
                allow_redirects=self.allow_redirects,
            )
        )
        if response.status_code >= 300 and raise_on_error:
            raise RequestError(response)
        return response

    def get(self, endpoint: str, raise_on_error: bool = True, token: Token = None, **kwargs: Any) -> Response:
        """Helper to make a GET request to EternalTwin."""
        return self._request("get", endpoint, raise_on_error=raise_on_error, token=token, **kwargs)

    def post(self, endpoint: str, raise_on_error: bool = True, token: Token = None, **kwargs: Any) -> Response:
        """Helper to make a POST request to EternalTwin."""
        return self._request("post", endpoint, raise_on_error=raise_on_error, token=token, **kwargs)

    def token(self, authorization_code: str) -> Token:
        """Retrieve a token using the provided authorization code."""
        headers = {"Authorization": f"Basic {self._basic_auth_token()}"}
        data = {"grant_type": "authorization_code", "code": authorization_code}
        response = self.post(endpoints.TOKEN, headers=headers, json=data)
        return Token(**response.json())
