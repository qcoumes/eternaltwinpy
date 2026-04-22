import copy
from typing import Any, Generic, Type, TypeVar

from eternaltwin.clients.abc.clients import ClientABC
from eternaltwin.clients.asyncio.clients import Eternaltwin as AsyncEternaltwin
from eternaltwin.clients.sync.clients import Eternaltwin

Client = TypeVar("Client", bound=ClientABC)


__all__ = ["connections", "async_connections", "configure", "Connections"]


class Connections(Generic[Client]):
    """Holds connections to different EternalTwin API."""

    def __init__(self, client_class: Type[Client]) -> None:
        self._client_class = client_class
        self._client: dict[str, Client] = {}

    def __getitem__(self, alias: str) -> Client:
        return self._client[alias]

    def __setitem__(self, alias: str, client: Client) -> None:
        self._client[alias] = client

    def __delitem__(self, alias: str) -> None:
        del self._client[alias]

    def configure(self, **kwargs: Any) -> None:
        """Configure multiple clients at once.

        Useful for passing in config dictionaries obtained from other sources,
        like Django's settings or a configuration management tool. Overwrite
        all existing connections.

        Examples
        --------
        ```python
        ETERNALTWIN_CONFIG = {
            "default": {
                'url': 'https://eternaltwin.org/api/v1/',
                'client_id': "myclient",
                'client_secret': 'mysecret',
                'state_key': HS256Key("mykey"),
                'redirect_uri': 'https://myapp.com/callback',
            },
            "test": {
                'url': 'http://localhost:50321/api/v1"',
                'client_id': "myclient",
                'client_secret': 'mysecret',
                'redirect_uri': 'https://localhost:8080/callback',
                'state_key': HS256Key("mykey"),
                'timeout': 1,
                'verify_ssl': False,
                'allow_redirects': True,
            }
        }
        connections.configure(**ETERNALTWIN_CONFIG)
        ```
        """
        self._client.clear()
        for k, v in kwargs.items():
            self.create_connection(k, **v)

    def create_connection(self, alias: str, **kwargs: Any) -> Any:
        """Create a client and register it under given alias."""
        client = self._client[alias] = self._client_class(**kwargs)
        return client

    def get_connection(self, alias: str = None) -> Client:
        """Return the client corresponding to alias."""
        try:
            return self._client[alias or "default"]
        except KeyError:
            raise KeyError(f"No connection found for alias '{alias or 'default'}'.")

    add_connection = __setitem__

    remove_connection = __delitem__


connections: Connections[Eternaltwin] = Connections(Eternaltwin)
"""Global instance holding all the synchronous connections configured with `configure()`."""

async_connections: Connections[AsyncEternaltwin] = Connections(AsyncEternaltwin)
"""Global instance holding all the asynchronous connections configured with `configure()`."""


def configure(**kwargs: Any) -> None:  # pragma: no cover
    """Configure both the synchronous and asynchronous clients."""
    connections.configure(**copy.deepcopy(kwargs))
    async_connections.configure(**kwargs)
