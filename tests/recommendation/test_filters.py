import animeippo.recommendation.filters as filters
import pandas as pd


def test_abstract_filter_can_be_instantiated():
    class ConcreteFilter(filters.AbstractFilter):
        def filter(self, dataframe):
            return super().filter(dataframe)

    filter = ConcreteFilter()
    filter.filter(None)

    assert issubclass(filter.__class__, filters.AbstractFilter)


def test_media_type_filter():
    original = pd.DataFrame({"media_type": ["tv", "tv", "special", "movie"]})

    filter = filters.MediaTypeFilter("tv")

    assert filter.filter(original)["media_type"].tolist() == ["tv", "tv"]

    filter.negative = True

    assert filter.filter(original)["media_type"].tolist() == ["special", "movie"]


def test_feature_filter():
    original = pd.DataFrame({"features": [["Action", "Adventure"], ["Fantasy", "Comedy"]]})

    filter = filters.FeatureFilter("Action")

    assert filter.filter(original)["features"].tolist() == [["Action", "Adventure"]]

    filter.negative = True

    assert filter.filter(original)["features"].tolist() == [["Fantasy", "Comedy"]]


def test_id_filter():
    original = pd.DataFrame({"id": [1, 2, 3, 4], "data": ["a", "b", "c", "d"]})
    original = original.set_index("id")

    filter = filters.IdFilter(1, 3)

    assert filter.filter(original).index.tolist() == [1, 3]

    filter.negative = True

    assert filter.filter(original).index.tolist() == [2, 4]


def test_status_filter():
    original = pd.DataFrame(
        {"status": ["dropped", "completed", "on_hold", "completed", "unwatched"]}
    )

    filter = filters.StatusFilter("completed")

    assert filter.filter(original)["status"].tolist() == ["completed", "completed"]

    filter.negative = True

    assert filter.filter(original)["status"].tolist() == ["dropped", "on_hold", "unwatched"]


def test_rating_filter():
    original = pd.DataFrame({"rating": ["g", "r", "g", "pg_13", "r"]})

    filter = filters.RatingFilter("g", "pg_13")

    assert filter.filter(original)["rating"].tolist() == ["g", "g", "pg_13"]

    filter.negative = True

    assert filter.filter(original)["rating"].tolist() == ["r", "r"]


def test_season_filter():
    original = pd.DataFrame({"start_season": ["2023/winter", "2023/winter", "2023/spring"]})

    filter = filters.StartSeasonFilter(("2023", "winter"))

    assert filter.filter(original)["start_season"].tolist() == ["2023/winter", "2023/winter"]

    filter.negative = True

    assert filter.filter(original)["start_season"].tolist() == ["2023/spring"]


def test_continuation_filter():
    compare = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "title": ["Anime A", "Anime B", "Anime B Spinoff", "Anime C"],
            "status": ["completed", "completed", "completed", "completed"],
        }
    )
    compare = compare.set_index("id")

    filter = filters.ContinuationFilter(compare)

    original = pd.DataFrame(
        {
            "id": [5, 6, 7, 8],
            "title": ["Anime A Season 2", "Anime E Season 2", "Anime B Season 2", "Anime F"],
            "related_anime": [[1], [9], [2, 3], []],
        }
    )
    original = original.set_index("id")

    assert filter.filter(original).index.tolist() == [5, 7, 8]

    filter.negative = True

    assert filter.filter(original).index.tolist() == [6]


def test_filters_work_with_lists():
    original = pd.DataFrame({"id": [1, 2, 3, 4], "data": ["a", "b", "c", "d"]}).set_index("id")

    filter = filters.IdFilter(*[1, 3])

    assert filter.filter(original).index.tolist() == [1, 3]

    filter.negative = True

    assert filter.filter(original).index.tolist() == [2, 4]
