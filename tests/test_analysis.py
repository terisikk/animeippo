import animeippo.recommendation.analysis as analysis
import animeippo.recommendation.engine as engine
import pandas as pd
import numpy as np
import pytest


def test_jaccard_similarity():
    x_orig = [[True, True, False], [True, False, True]]
    y_orig = [[True, True, False], [True, False, True]]

    distances = analysis.similarity(x_orig, y_orig)

    expected0 = "1.0"
    actual0 = "{:.1f}".format(distances[0][0])

    expected1 = "0.3"
    actual1 = "{:.1f}".format(distances[0][1])

    assert actual0 == expected0
    assert actual1 == expected1


def test_score_by_genre_similarity():
    source_df = pd.DataFrame(
        {
            "genres": [["Action", "Adventure"], ["Action", "Fantasy"]],
            "title": ["Bleach", "Fate/Zero"],
        }
    )
    target_df = pd.DataFrame(
        {"genres": [["Romance", "Comedy"], ["Action", "Adventure"]], "title": ["Kaguya", "Naruto"]}
    )

    recommendations = analysis.score_by_genre_similarity(
        engine.CategoricalEncoder(["Action", "Adventure", "Fantasy"]), target_df, source_df
    )
    expected = "Naruto"
    actual = recommendations.iloc[0]["title"]

    assert actual == expected
    assert recommendations.columns.tolist() == ["genres", "title", "recommend_score"]
    assert not recommendations["recommend_score"].isnull().values.any()


def test_score_by_genre_similarity_weighted():
    source_df = pd.DataFrame(
        {
            "genres": [["Action", "Adventure"], ["Fantasy", "Adventure"]],
            "title": ["Bleach", "Fate/Zero"],
            "user_score": [1, 10],
        }
    )
    target_df = pd.DataFrame(
        {
            "genres": [["Action", "Adventure"], ["Fantasy", "Adventure"]],
            "title": ["Naruto", "Inuyasha"],
        }
    )

    recommendations = analysis.score_by_genre_similarity(
        engine.CategoricalEncoder(["Action", "Adventure", "Fantasy"]),
        target_df,
        source_df,
        weighted=True,
    )
    expected = "Inuyasha"
    actual = recommendations.iloc[0]["title"]

    assert actual == expected
    assert not recommendations["recommend_score"].isnull().values.any()


def test_score_by_cluster_similarity():
    source_df = pd.DataFrame(
        {
            "genres": [["Action", "Adventure"], ["Action", "Fantasy"]],
            "title": ["Bleach", "Fate/Zero"],
            "cluster": [0, 1],
        }
    )
    target_df = pd.DataFrame(
        {"genres": [["Romance", "Comedy"], ["Action", "Adventure"]], "title": ["Kaguya", "Naruto"]}
    )

    recommendations = analysis.score_by_cluster_similarity(
        engine.CategoricalEncoder(["Action", "Adventure", "Fantasy", "Romance", "Comedy"]),
        target_df,
        source_df,
    )
    expected = "Naruto"
    actual = recommendations.iloc[0]["title"]

    assert actual == expected
    assert recommendations.columns.tolist() == ["genres", "title", "recommend_score"]
    assert not recommendations["recommend_score"].isnull().values.any()


def test_score_by_cluster_similarity_weighted():
    source_df = pd.DataFrame(
        {
            "genres": [["Action", "Adventure"], ["Fantasy", "Adventure"]],
            "title": ["Bleach", "Fate/Zero"],
            "user_score": [10, 1],
            "cluster": [0, 1],
        }
    )
    target_df = pd.DataFrame(
        {
            "genres": [["Fantasy", "Adventure"], ["Action", "Adventure"]],
            "title": ["Inuyasha", "Naruto"],
        }
    )
    recommendations = analysis.score_by_cluster_similarity(
        engine.CategoricalEncoder(["Action", "Adventure", "Fantasy", "Romance", "Comedy"]),
        target_df,
        source_df,
        weighted=True,
    )
    expected = "Naruto"
    actual = recommendations.iloc[0]["title"]

    assert actual == expected
    assert recommendations.columns.tolist() == ["genres", "title", "recommend_score"]
    assert not recommendations["recommend_score"].isnull().values.any()


def test_genre_average_scores():
    original = pd.DataFrame(
        {
            "genres": [["Action"], ["Action", "Horror"], ["Action", "Horror", "Romance"]],
            "user_score": [10, 10, 7],
        }
    )

    avg = analysis.genre_average_scores(original)

    assert avg.tolist() == [9.0, 8.5, 7.0]


def test_similarity_weights():
    genre_averages = pd.Series(data=[9.0, 8.0, 7.0], index=["Action", "Horror", "Romance"])

    original = pd.DataFrame(
        {"title": ["Hellsing", "Inuyasha"], "genres": [["Action", "Horror"], ["Action", "Romance"]]}
    )

    weights = original["genres"].apply(analysis.user_genre_weight, args=(genre_averages,))

    assert weights.tolist() == [8.5, 8.0]


def test_similarity_weight_ignores_genres_without_average():
    genre_averages = pd.Series(data=[9.0], index=["Action"])

    genres = ["Action", "Horror"]

    weight = analysis.user_genre_weight(genres, genre_averages)

    assert weight == 9.0


@pytest.mark.filterwarnings("ignore:Mean of empty slice:RuntimeWarning")
def test_similarity_weight_scores_genre_list_containing_only_unseen_genres_as_zero():
    genre_averages = pd.Series(data=[9.0], index=["Romance"])

    original = ["Action", "Horror"]

    weight = analysis.user_genre_weight(original, genre_averages)

    assert weight == 0.0
