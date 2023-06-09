from animeippo.providers import anilist
from tests import test_data

import pytest


class ResponseStub:
    dictionary = {}

    def __init__(self, dictionary):
        self.dictionary = dictionary

    async def get(self, key):
        return self.dictionary.get(key)

    async def json(self):
        return self.dictionary

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self

    def raise_for_status(self):
        pass


@pytest.mark.asyncio
async def test_ani_user_anime_list_can_be_fetched(mocker):
    provider = anilist.AniListProvider()

    user = "Janiskeisari"

    response = ResponseStub(test_data.ANI_USER_LIST)
    mocker.patch("aiohttp.ClientSession.post", return_value=response)

    animelist = await provider.get_user_anime_list(user)

    assert "Dr. STRONK: OLD WORLD" in animelist["title"].values


@pytest.mark.asyncio
async def test_ani_seasonal_anime_list_can_be_fetched(mocker):
    provider = anilist.AniListProvider()

    year = "2023"
    season = "winter"

    response = ResponseStub(test_data.ANI_SEASONAL_LIST)
    mocker.patch("aiohttp.ClientSession.post", return_value=response)

    animelist = await provider.get_seasonal_anime_list(year, season)

    assert "EDENS KNOCK-OFF 2nd Season" in animelist["title"].values


def test_ani_related_anime_returns_none():
    provider = anilist.AniListProvider()

    animelist = provider.get_related_anime(0)

    assert animelist is None


@pytest.mark.asyncio
async def test_get_single_returns_succesfully(mocker):
    response_json = {"data": [{"test": "test"}], "pageInfo": {"hasNextPage": False}}

    response = ResponseStub(response_json)
    mocker.patch("aiohttp.ClientSession.post", return_value=response)

    page = await anilist.AnilistConnection().request_single("test", {})

    assert page == await response.json()


@pytest.mark.asyncio
async def test_get_all_pages_returns_all_pages(mocker):
    response1 = {
        "data": {
            "Page": {
                "media": {"test": "test2"},
                "pageInfo": {"hasNextPage": True, "currentPage": 0},
            }
        }
    }
    response2 = {
        "data": {
            "Page": {
                "media": {"test": "test2"},
                "pageInfo": {"hasNextPage": True, "currentPage": 1},
            }
        }
    }
    response3 = {
        "data": {
            "Page": {
                "media": {"test": "test1"},
                "pageInfo": {"hasNextPage": False, "currentPage": 2},
            }
        }
    }

    mocker.patch(
        "aiohttp.ClientSession.post",
        side_effect=[ResponseStub(response1), ResponseStub(response2), ResponseStub(response3)],
    )

    final_pages = list(
        [page async for page in anilist.AnilistConnection().requests_get_all_pages("", {})]
    )

    assert len(final_pages) == 3
    assert final_pages[0] == response1["data"]["Page"]
    assert final_pages[2] == response3["data"]["Page"]


@pytest.mark.asyncio
async def test_request_does_not_fail_catastrophically_when_response_is_empty(mocker):
    response = {}

    response = ResponseStub({})
    mocker.patch("aiohttp.ClientSession.post", return_value=response)

    all_pages = list(
        [page async for page in anilist.AnilistConnection().requests_get_all_pages("", {})]
    )

    assert len(all_pages) == 1
    assert all_pages[0] is None


def test_features_can_be_fetched():
    provider = anilist.AniListProvider()

    features = provider.get_features()

    assert len(features) > 0
    assert "genres" in features


@pytest.mark.asyncio
async def test_anilist_returns_None_with_empty_parameters():
    provider = anilist.AniListProvider()

    seasonal_anime = await provider.get_seasonal_anime_list(None, None)
    user_anime = await provider.get_user_anime_list(None)

    assert seasonal_anime is None
    assert user_anime is None
