from eternaltwin.enums import AuthorizationType


async def test_me_unauthenticated(async_client):
    response = await async_client.users.me()
    assert response.json().get("type") == AuthorizationType.GUEST


async def test_me_authenticated(async_client, user1_token):
    response = await async_client.users.me(token=user1_token)
    assert response.json().get("type") != AuthorizationType.GUEST
    assert response.json()["user"]["display_name"]["current"]["value"] == "user1"


async def test_get_user(async_client, user1_token):
    response = await async_client.users.get((await async_client.users.me(token=user1_token)).json()["user"]["id"])
    assert response.json()["display_name"]["current"]["value"] == "user1"


async def test_search_users(async_client):
    data = (await async_client.users.search("user1")).json()
    assert data["count"] == 1
    assert data["items"][0]["display_name"]["current"]["value"] == "user1"

    data = (await async_client.users.search("user")).json()
    assert data["count"] == 2
    assert len(data["items"]) == 2

    data = (await async_client.users.search("user", limit=1)).json()
    assert data["count"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["display_name"]["current"]["value"] == "user1"

    data = (await async_client.users.search("user", limit=1, offset=1)).json()
    assert data["count"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["display_name"]["current"]["value"] == "user2"
