# OAuth2 Authorization

The OAuth2 authorization process supported by Eternaltwin is described
[here](https://eternaltwin.org/docs/app/etwin-oauth).

It basically rely on redirecting the user to EternalTwin instance with specific
query parameters. Once the user has authenticated, it will be redirected back
to your application with an authorization code that can be exchanged for an
access token.

## Retrieving the Authorization URL

To start the authorization process, you can call
[`User.start_authorization()`][eternaltwin.users.User.start_authorization] to
retrieve a `state`, and an `url`.

The `state` is used to prevent CSRF attacks by signing the request confirming
that the value coming from the response matches the one you sent. It is also
used to match responses to their corresponding requests if you have multiple
ongoing authorization flows, or if the callback is handled by a different 
thread, worker, or process than the one that started the authorization process.

The `state` is a JWT token signed with the key associated with the client.

```python
from eternaltwin.users import User
from eternaltwin.exceptions import InvalidStateError

state, url = User.start_authorization()
```

---

You must then redirect your user to this URL, allowing them to authenticate
on the EternalTwin instance.

## Authorizing the user

Once the user has authenticated himself on the EternalTwin instance, they will
be redirected back to the `redirect_uri` associated with the client with a
`code` and the `state` as query parameters.

You can use both the `code` and the `state` to retrieve the user using the
[`User.from_authorization_code()`][eternaltwin.users.User.from_authorization_code]
method:

```python
request_state =  # The state you sent
authorization_code =  # Extract the received `code`
response_state =  # Extract the received `state`
 
try:
    user = User.from_authorization_code(authorization_code, response_state, state)
except InvalidStateError:
    ...

assert user.is_authenticated is True
```

Any inconsistency in the received state will raise an [`InvalidStateError`][eternaltwin.exceptions.InvalidStateError].

It is not mandatory to pass the `state` you sent to
[`from_authorization_code()`][eternaltwin.users.User.from_authorization_code],
but highly recommended.

If you somehow need to access / store the token, you can access it with
`user.token`. It contains an instance of [`Token`][eternaltwin.tokens.Token].

The returned user is an instance of [`User`][eternaltwin.users.User].
