# Working with Users

Users are represented by the [`User`][eternaltwin.users.User] class, which is a
high-level abstraction over the user data returned by the API. It contains
information about the user, such as their identifier, username, and whether
they are administrator or not.

You can retrieve users from the EternalTwin API in three different ways:

* By following the authorization flow (see [OAuth2 Authorization](usage_oauth2.md) for more details).
* Using their identifier.
* Searching for users by their username.

::: eternaltwin.users.User.get
    options:
        heading: "By Identifier"
        toc_label: "By Identifier"
        show_root_heading: true
        show_docstring_description: false
        show_symbol_type_heading: false
        show_labels: false
        separate_signature: true
        show_signature: true
        show_signature_annotations: true

> You can use [`User.aget()`][eternaltwin.users.User.aget] instead for asynchronous requests.

If you have the user's ID (usually in the form of an UUID4), you can directly
retrieve it without following the authorization flow with this method. It will
return an instance of [`User`][eternaltwin.users.User].

```python
from eternaltwin.users import User

user_id = "12345678-1234-1234-1234-123456789012"
user = User.get(user_id)
assert user.identifier == user_id
```

::: eternaltwin.users.User.search
    options:
        heading: "Searching by username"
        toc_label: "Searching by username"
        show_root_heading: true
        show_docstring_description: false
        show_symbol_type_heading: false
        show_labels: false
        separate_signature: true
        show_signature: true
        show_signature_annotations: true

> You can use [`User.asearch()`][eternaltwin.users.User.asearch] instead for asynchronous requests.

If don't have the user's ID, but you know their username, you can search for them using this method instead.

```python
from eternaltwin.users import User

users = User.search("Bob")
```

Note that the return list might be empty, or containis multiple users with
a username containing `"Bob"`.
