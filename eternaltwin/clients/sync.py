from datetime import datetime
from typing import Any, Literal
from urllib.parse import urljoin

import requests

from eternaltwin.clients.abc import ClientABC
from eternaltwin.exceptions import RequestError
from eternaltwin.responses import Response
from eternaltwin.tokens import Token
from eternaltwin.users import AnonymousUser, User


class Eternaltwin(ClientABC):
    """Synchronous clients handling communication with EternalTwin."""

    def _request(
        self,
        method: Literal["get", "post", "delete", "put", "patch", "options"],
        endpoint: str,
        raise_on_error: bool = True,
        **kwargs: Any,
    ) -> Response:
        """Helper to make a request to EternalTwin."""
        if self.token is not None and "Authorization" not in kwargs.get("headers", {}):
            kwargs["headers"] = kwargs.get("headers", {}) | {"Authorization": f"Bearer {self.token.access_token}"}
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

    def _get(self, endpoint: str, raise_on_error: bool = True, **kwargs: Any) -> Response:
        """Helper to make an authenticated GET request to EternalTwin."""
        return self._request("get", endpoint, raise_on_error=raise_on_error, **kwargs)

    def _post(self, endpoint: str, raise_on_error: bool = True, **kwargs: Any) -> Response:
        """Helper to make an authenticated POST request to EternalTwin."""
        return self._request("post", endpoint, raise_on_error=raise_on_error, **kwargs)

    def authenticate(self, authorization_code: str = None, token: Token = None) -> Token:
        """Authenticate the client using either an authorization code or an existing token."""
        if not (bool(authorization_code) ^ bool(token)):
            raise ValueError("Either authorization_code xor token must be provided.")

        if token:
            self.token = token
        else:
            headers = {"Authorization": f"Basic {self._basic_auth_token()}"}
            data = {"grant_type": "authorization_code", "code": authorization_code}
            response = self._post(self.token_uri, headers=headers, json=data)
            self.token = Token(**response.json())
        return self.token

    def me(self) -> User | AnonymousUser:
        """Retrieve current user's profile."""
        data = self._get(self.self_uri).json()
        if data.get("type") == "Guest":
            return AnonymousUser()
        return self.user(data["user"]["id"])

    def user(self, user_id: str) -> User:
        """Retrieve current user's profile."""
        data = self._get(self.users_uri.format(user_id=user_id)).json()
        return User(
            identifier=data["id"],
            username=data["display_name"]["current"]["value"],
            is_administrator=data["is_administrator"],
            created_at=data["created_at"] and datetime.fromisoformat(data["created_at"]),
            deleted_at=data["deleted_at"] and datetime.fromisoformat(data["deleted_at"]),
        )
