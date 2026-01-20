from datetime import datetime
from typing import Any


class AnonymousUser:
    """Represents an anonymous user."""

    is_guest: bool = True

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, AnonymousUser)


class User:
    """Represents a user."""

    is_guest: bool = False

    def __init__(
        self,
        identifier: str,
        username: str,
        is_administrator: bool,
        created_at: datetime | None,
        deleted_at: datetime | None,
    ) -> None:
        self.identifier = identifier
        self.username = username
        self.is_administrator = is_administrator
        self.created_at = created_at
        self.deleted_at = deleted_at

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, User) and self.identifier == other.identifier
