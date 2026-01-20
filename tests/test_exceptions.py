from types import SimpleNamespace
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

from eternaltwin.exceptions import RequestError


def test_bad_request_error_requests(client):
    try:
        side_effect = [SimpleNamespace(status_code=405, content=b"method_not_allowed", url=client.url, headers={})]
        with mock.patch("eternaltwin.clients.sync.requests.request", side_effect=side_effect):
            client._post("/")
    except RequestError as error:
        assert error.response.content == b"method_not_allowed"
        assert error.response.status_code == 405


async def test_bad_request_error_aiohttp(async_client):
    try:
        mock_response = MagicMock()
        mock_response.status = 405
        mock_response.headers = {}
        mock_response.read = AsyncMock(return_value=b"method_not_allowed")
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()
        with mock.patch("eternaltwin.clients.asyncio.aiohttp.ClientSession.request", return_value=mock_response):
            async with async_client:
                await async_client._post("/")
    except RequestError as error:
        assert error.response.content == b"method_not_allowed"
        assert error.response.status_code == 405
