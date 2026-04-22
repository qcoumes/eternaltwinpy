from eternaltwin.enums import AuthorizationType


def test_me_unauthenticated(client):
    response = client.users.me()
    assert response.json().get("type") == AuthorizationType.GUEST


def test_me_authenticated(client, user1_token):
    response = client.users.me(token=user1_token)
    assert response.json().get("type") != AuthorizationType.GUEST
    assert response.json()["user"]["display_name"]["current"]["value"] == "user1"


def test_get_user(client, user1_token):
    response = client.users.get(client.users.me(token=user1_token).json()["user"]["id"])
    assert response.json()["display_name"]["current"]["value"] == "user1"


def test_search_users(client):
    data = client.users.search("user1").json()
    assert data["count"] == 1
    assert data["items"][0]["display_name"]["current"]["value"] == "user1"

    data = client.users.search("user").json()
    assert data["count"] == 2
    assert len(data["items"]) == 2

    data = client.users.search("user", limit=1).json()
    assert data["count"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["display_name"]["current"]["value"] == "user1"

    data = client.users.search("user", limit=1, offset=1).json()
    assert data["count"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["display_name"]["current"]["value"] == "user2"
