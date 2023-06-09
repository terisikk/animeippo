import asyncio

import animeippo.providers as providers
from animeippo import cache
from animeippo.recommendation.recommender import AnimeRecommender
from animeippo.recommendation import engine, filters, scoring, dataset, categories

import pandas as pd
import numpy as np

DEFAULT_SCORERS = [
    # scoring.FeatureSimilarityScorer(feature_tags, weighted=True),
    scoring.GenreAverageScorer(),
    scoring.ClusterSimilarityScorer(weighted=True),
    # scoring.StudioCountScorer(),
    scoring.StudioAverageScorer(),
    scoring.PopularityScorer(),
    scoring.ContinuationScorer(),
    scoring.SourceScorer(),
    scoring.DirectSimilarityScorer(),
]

DEFAULT_CATEGORIZERS = [
    categories.MostPopularCategory(),
    categories.ContinueWatchingCategory(),
    categories.YourTopPicks(),
    categories.TopUpcoming(),
    categories.ClusterCategory(0),
    categories.SourceCategory(),
    categories.ClusterCategory(1),
    categories.StudioCategory(),
    categories.ClusterCategory(2),
    categories.BecauseYouLiked(0),
    categories.ClusterCategory(3),
    categories.BecauseYouLiked(1),
    categories.ClusterCategory(4),
]


async def get_dataset(provider, user, year, season):
    if season is None:
        user_data, season_data1, season_data2, season_data3, season_data4 = await asyncio.gather(
            provider.get_user_anime_list(user),
            provider.get_seasonal_anime_list(year, "winter"),
            provider.get_seasonal_anime_list(year, "spring"),
            provider.get_seasonal_anime_list(year, "summer"),
            provider.get_seasonal_anime_list(year, "fall"),
        )

        season_data = pd.concat([season_data1, season_data2, season_data3, season_data4])

    else:
        user_data, season_data = await asyncio.gather(
            provider.get_user_anime_list(user),
            provider.get_seasonal_anime_list(year, season),
        )

    data = dataset.UserDataSet(
        user_data,
        season_data,
        provider.get_features(),
    )

    return data


def fill_user_status_data_from_watchlist(seasonal, watchlist):
    seasonal["user_status"] = np.nan
    seasonal["user_status"].update(watchlist["status"])
    return seasonal


async def construct_anilist_data(provider, year, season, user):
    data = await get_dataset(provider, user, year, season)

    if data.seasonal is not None and data.watchlist is not None:
        data.seasonal = fill_user_status_data_from_watchlist(data.seasonal, data.watchlist)
        watchlist_filters = [filters.IdFilter(*data.seasonal.index.to_list(), negative=True)]

        for f in watchlist_filters:
            data.watchlist = f.filter(data.watchlist)

        data.seasonal = filters.ContinuationFilter(data.watchlist).filter(data.seasonal)

    if data.seasonal is not None:
        seasonal_filters = [
            filters.FeatureFilter("Kids", negative=True),
            filters.FeatureFilter("Hentai", negative=True),
            filters.StartSeasonFilter(
                (year, "winter"), (year, "spring"), (year, "summer"), (year, "fall")
            )
            if season is None
            else filters.StartSeasonFilter((year, season)),
        ]

        for f in seasonal_filters:
            data.seasonal = f.filter(data.seasonal)

    return data


async def get_related_anime(indices, provider):
    related_anime = []

    for i in indices:
        anime = await provider.get_related_anime(i)
        related_anime.append(anime.index.to_list())

    return related_anime


async def construct_myanimelist_data(provider, year, season, user):
    data = await get_dataset(provider, user, year, season)

    if data.seasonal is not None:
        seasonal_filters = [
            filters.MediaTypeFilter("tv"),
            filters.RatingFilter("g", "rx", negative=True),
            filters.StartSeasonFilter(
                (year, "winter"), (year, "spring"), (year, "summer"), (year, "fall")
            )
            if season is None
            else filters.StartSeasonFilter((year, season)),
        ]

        for f in seasonal_filters:
            data.seasonal = f.filter(data.seasonal)

        indices = data.seasonal.index.to_list()
        data.seasonal["related_anime"] = await get_related_anime(indices, provider)

    if data.watchlist is not None and data.seasonal is not None:
        data.seasonal = fill_user_status_data_from_watchlist(data.seasonal, data.watchlist)
        watchlist_filters = [filters.IdFilter(*data.seasonal.index.to_list(), negative=True)]

        for f in watchlist_filters:
            data.watchlist = f.filter(data.watchlist)

        data.seasonal = filters.ContinuationFilter(data.watchlist).filter(data.seasonal)

    return data


class RecommenderBuilder:
    def __init__(self):
        self._provider = None
        self._databuilder = None
        self._model = None
        self._seasonal_filters = None
        self._watchlist_filters = None

    def build(self):
        return AnimeRecommender(self._provider, self._model, self._databuilder)

    def provider(self, provider):
        self._provider = provider
        return self

    def databuilder(self, databuilder):
        self._databuilder = databuilder
        return self

    def model(self, model):
        self._model = model
        return self


def create_builder(providername):
    rcache = cache.RedisCache()

    match providername:
        case "anilist":
            return (
                RecommenderBuilder()
                .provider(providers.anilist.AniListProvider(rcache))
                .model(engine.AnimeRecommendationEngine(DEFAULT_SCORERS, DEFAULT_CATEGORIZERS))
                .databuilder(construct_anilist_data)
            )
        case _:
            return (
                RecommenderBuilder()
                .provider(providers.myanimelist.MyAnimeListProvider(rcache))
                .model(engine.AnimeRecommendationEngine(DEFAULT_SCORERS, DEFAULT_CATEGORIZERS))
                .databuilder(construct_myanimelist_data)
            )
