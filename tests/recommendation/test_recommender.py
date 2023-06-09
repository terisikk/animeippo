import pandas as pd

from animeippo.recommendation import recommender, dataset
from tests.recommendation.test_engine import ProviderStub
from tests import test_data

from functools import partial


class EngineStub:
    def fit_predict(self, dataset):
        return dataset.seasonal[::-1]

    def categorize_anime(self, dataset):
        return [[1, 2, 3]]


async def databuilder_stub(h, i, j, k, watchlist=None, seasonal=None):
    return dataset.UserDataSet(watchlist, seasonal)


def test_recommender_can_return_plain_seasonal_data():
    seasonal = pd.DataFrame(test_data.FORMATTED_MAL_SEASONAL_LIST)

    provider = ProviderStub()
    engine = None
    databuilder = partial(databuilder_stub, watchlist=None, seasonal=seasonal)

    rec = recommender.AnimeRecommender(provider, engine, databuilder)
    data = rec.recommend_seasonal_anime("2013", "winter")

    assert seasonal.loc[0]["title"] in data.recommendations["title"].to_list()


def test_recommender_can_recommend_seasonal_data_for_user():
    seasonal = pd.DataFrame(test_data.FORMATTED_MAL_SEASONAL_LIST)
    watchlist = pd.DataFrame(test_data.FORMATTED_MAL_USER_LIST)

    provider = ProviderStub()
    engine = EngineStub()
    databuilder = partial(databuilder_stub, watchlist=watchlist, seasonal=seasonal)

    rec = recommender.AnimeRecommender(provider, engine, databuilder)
    data = rec.recommend_seasonal_anime("2013", "winter", "Janiskeisari")

    assert seasonal.loc[0]["title"] in data.recommendations["title"].to_list()


def test_recommender_categories():
    seasonal = pd.DataFrame(test_data.FORMATTED_MAL_SEASONAL_LIST)
    watchlist = pd.DataFrame(test_data.FORMATTED_MAL_USER_LIST)

    provider = ProviderStub()
    engine = EngineStub()
    databuilder = partial(databuilder_stub, watchlist=watchlist, seasonal=seasonal)

    rec = recommender.AnimeRecommender(provider, engine, databuilder)
    data = rec.recommend_seasonal_anime("2013", "winter", "Janiskeisari")
    categories = rec.get_categories(data)

    assert len(categories) > 0
    assert categories == [[1, 2, 3]]
