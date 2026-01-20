import time


class Token:
    """Hold information about a token received from the authorization endpoint."""

    def __init__(self, *, access_token: str, expires_in: int, token_type: str, refresh_token: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiration = int(time.time()) + expires_in - 60  # Remove a 60 seconds leeway
        self.token_type = token_type

    def has_expired(self) -> bool:
        """Check if the token has expired."""
        return int(time.time()) >= self.expiration
