[![PyPI Version](https://badge.fury.io/py/eternaltwinpy.svg)](https://badge.fury.io/py/eternaltwinpy)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](#) 
[![License AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-brightgreen.svg)](https://github.com/qcoumes/eternaltwinpy/blob/master/LICENSE)
![Tests](https://github.com/qcoumes/eternaltwinpy/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/qcoumes/eternaltwinpy/graph/badge.svg?token=PLpPwU6540)](https://codecov.io/gh/qcoumes/eternaltwinpy)
[![CodeFactor](https://www.codefactor.io/repository/github/qcoumes/eternaltwinpy/badge)](https://www.codefactor.io/repository/github/qcoumes/eternaltwinpy)

# EternalTwin Python Client

**eternaltwinpy** is an unofficial Python client for the EternalTwin API. It let you authenticate and retrieve users
information.

You can view the full documentation at [https://eternaltwinpy.readthedocs.io/en/latest/](https://eternaltwinpy.readthedocs.io/en/latest/).

## Features

- Provides a high-level API to make authorization and user information retrieval easier.
- Provides a low-level API to interact directly with the EternalTwin API.
- Support both synchronous and asynchronous HTTP requests.

## Requirements

`eternaltwinpy` supports the [officially supported versions of Python](https://devguide.python.org/versions/)
(mainstream & LTS).

## Installation

Install via `pip`:

```bash
pip install eternaltwinpy
```

or `poetry`:

```bash
poetry add eternaltwinpy
```

##  Quickstart

### Configure the connection
See [Configuration](https://eternaltwinpy.readthedocs.io/en/latest/usage_configuration) for more details.
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

### Oauth2 Authorization

See [OAuth2 Authorization](https://eternaltwinpy.readthedocs.io/en/latest/usage_oauth2) for more details.

```python
from eternaltwin.users import User
from eternaltwin.exceptions import InvalidStateError

# Generate a state and an authorization URL.
# The state can be used to find which auth request the response corresponds to
# if the callback is handled by a different thread, worker, or process than the
# one that created the auth request.
state, url = User.start_authorization()

# Redirect the user to the url, once authenticated EternalTwin will redirect
# back to your `redirect_uri` with additional query parameters `code` and `state`.
authorization_code =  # Extract the `code`
response_state =  # Extract the `state`

# Ensure the state is as expected to prevent CSRF attacks. 
try:
    user = User.from_authorization_code(authorization_code, response_state, state)
except InvalidStateError:
    ...

assert user.is_authenticated is True
print(user.identifier)
# "<user_id>"
print(user.username)
# "<username>"
```

### Retrieving User Information

See [Working with Users](https://eternaltwinpy.readthedocs.io/en/latest/usage_users) for more details.

```python
from eternaltwin.users import User

# Get a specific user by ID
user = User.get("<user_id>")
print(user.identifier)
# "<user_id>"
print(user.username)
# "Bob"

# Search for users by username
users = User.search("Jhon")
```
