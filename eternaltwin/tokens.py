import time


class Token:
    """Hold information about a token received from the authorization endpoint."""

    def __init__(self, *, access_token: str, expires_in: int, token_type: str, refresh_token: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiration = int(time.time()) + expires_in - 60  # Remove a 60 seconds leeway
        self.token_type = token_type

    def __repr__(self) -> str:
        return (
            f"Token("
            f"    access_token={self.access_token!r},"
            f"    refresh_token={self.refresh_token!r},"
            f"    expiration={self.expiration!r},"
            f"    token_type={self.token_type!r}"
            f")"
        )

    def has_expired(self) -> bool:
        """Check if the token has expired."""
        return int(time.time()) >= self.expiration
