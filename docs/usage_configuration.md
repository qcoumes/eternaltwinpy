# Configuration

## Connections

Connections manage the creation and configuration of [`Eternaltwin`][eternaltwin.clients.sync.clients.Eternaltwin] clients.
Two handlers are provided ([`connections`][eternaltwin.connections.connections]
and [`async_connections`][eternaltwin.connections.async_connections]), they can be imported from `eternaltwin.connections`.

Instead of directly instantiating [`Eternaltwin`][eternaltwin.clients.sync.clients.Eternaltwin]
(or its asynchronous equivalent), it is recommended to instead use either the
[`connections`][eternaltwin.connections.connections] or [`async_connections`][eternaltwin.connections.async_connections]
handlers. This has several advantages over using the clients directly:

- They can hold connections to different EternalTwin instances, which can be useful for testing and scaling purposes.
- Once configured, they are available from anywhere in your code without the need to pass around an instance of the client.
- They facilitate the use of config dictionaries obtained from other sources (e.g. config files, Django settings, …)

## Configuration

To register your application as a client on EternalTwin, you can follow the
[official documentation](https://eternaltwin.org/docs/app/etwin-oauth).

Once your application is registered, you can configure the handlers by using the
[`configure`][eternaltwin.connections.configure] function to associate aliases with the parameters of your instances :

```python
from eternaltwin.connections import configure
from eternaltwin.keys import HS256Key

ETERNALTWIN_CONFIG = {
    "default": {
        'url': 'https://eternaltwin.org/api/v1/',
        'client_id': "myclient",
        'client_secret': 'mysecret',
        'redirect_uri': 'https://myapp.com/callback',
        'state_key': HS256Key("mykey"),
        'allow_redirects': True,
    },
    "test": {
        'url': 'http://localhost:50321/api/v1"',
        'client_id': "myclient",
        'client_secret': 'mysecret',
        'redirect_uri': 'https://localhost:8080/callback',
        'state_key': HS256Key("mykey"),
        'timeout': 1,
        'verify_ssl': False,
    }
}
configure(**ETERNALTWIN_CONFIG)
```

This will overwrite all existing configuration. You can use the
[`.create_connection`][eternaltwin.connections.Connections.create_connection]
method to create a new connection without overwriting existing ones. See
[Connections API Reference](api_connections.md) for more information.

In this example, a [`HS256`][eternaltwin.keys.HS256Key] key will be used to sign the state parameter during
the authorization process, but other algorithms can be used, including
asymmetric ones. See [Keys API Reference](api_keys.md) for more information.

## Usage

You usually don't need to use the connection handlers directly, and should 
use the higher-level API instead.

Most of the high-level API methods have a `using: str | None = None` argument
that can be used to specify which connection to use (`"default"` is used by
default).

But if you need to, once the handler has been configured, you can use it anywhere in your code by
importing it and calling the [`.get_connection()`][eternaltwin.connections.Connections.get_connection] method.

```python
from eternaltwin.connections import connections, async_connections

client = connections.get_connection()
response = client.user.search("user")

client = async_connections.get_connection("test")
response = await client.user.search("user")
```

By default, the [`.get_connection()`][eternaltwin.connections.Connections.get_connection] method will return the client corresponding to the
`"default"` alias, but you can ask for a specific alias: `.get_connection(<alias>)`.
