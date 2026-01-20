from typing import TYPE_CHECKING

from eternaltwin.responses import Response

if TYPE_CHECKING:
    from eternaltwin.states import State


class EternalTwinError(Exception):
    """Base class for all exceptions raised by this package."""

    pass


class InvalidStateError(EternalTwinError):
    """Raised when a decoded state is invalid."""

    def __init__(self, message: str, state: "State"):
        self.message = message
        self.state = state

    def __str__(self) -> str:
        return self.message


class RequestError(EternalTwinError):
    """Raised when a request to EternalTwin fails."""

    def __init__(self, response: Response, message: str = None):
        self.response = response
        self.message = message or "Request to '{url}' failed with status code '{status_code}':\n{content}"

    def __str__(self) -> str:
        return self.message.format(
            url=self.response.url, status_code=self.response.status_code, content=self.response.content
        )
