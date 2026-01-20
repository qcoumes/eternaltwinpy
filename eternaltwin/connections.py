import copy
from typing import Any, Generic, Type, TypeVar

from eternaltwin.clients.abc import ClientABC
from eternaltwin.clients.asyncio import Eternaltwin as AsyncEternaltwin
from eternaltwin.clients.sync import Eternaltwin

C = TypeVar("C", bound=ClientABC)


class Connections(Generic[C]):
    """Holds connections to different EternalTwin API."""

    def __init__(self, client_class: Type[C]) -> None:
        self._client_class = client_class
        self._client: dict[str, C] = {}

    def __getitem__(self, alias: str) -> C:
        return self._client[alias]

    def __setitem__(self, alias: str, client: C) -> None:
        self._client[alias] = client

    def __delitem__(self, alias: str) -> None:
        del self._client[alias]

    def configure(self, **kwargs: Any) -> None:
        """Configure multiple clients at once.

        Useful for passing in config dictionaries obtained from other sources,
        like Django's settings or a configuration management tool.

        Examples
        --------
        ```python
        ETERNALTWIN_CONFIG = {
            "default": {
                'url': 'https://eternaltwin.org/api/v1/',
                'client_id': "myclient",
                'client_secret': 'mysecret',
                'redirect_uri': 'https://myapp.com/callback',
            },
            "test": {
                'url': 'http://localhost:50321/api/v1"',
                'client_id': "myclient",
                'client_secret': 'mysecret',
                'redirect_uri': 'https://localhost:8080/callback',
                'private_key': 'bar',
                'timeout': 1,
                'verify_ssl': False,
                'allow_redirects': True,
            }
        }
        connections.configure(**ETERNALTWIN_CONFIG)
        """
        for k, v in kwargs.items():
            self.create_connection(k, **v)

    def create_connection(self, alias: str, **kwargs: Any) -> Any:
        """Create a client and register it under given alias."""
        client = self._client[alias] = self._client_class(**kwargs)
        return client

    def get_connection(self, alias: str = "default") -> C:
        """Return the client corresponding to alias."""
        return self._client[alias]

    add_connection = __setitem__

    remove_connection = __delitem__


# Using a global instances holding all the connections allows to easily reuse
# them across an application.
connections = Connections(Eternaltwin)
async_connections = Connections(AsyncEternaltwin)


def configure(**kwargs: Any) -> None:  # pragma: no cover
    """Configure both the synchronous and asynchronous clients."""
    connections.configure(**copy.deepcopy(kwargs))
    async_connections.configure(**kwargs)
