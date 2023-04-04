import pandas as pd
import numpy as np
import scipy.spatial.distance as scdistance

import animeippo.providers.myanimelist as mal
import animeippo.recommendation.util as pdutil


def similarity(x_orig, y_orig, metric="jaccard"):
    distances = scdistance.cdist(x_orig, y_orig, metric=metric)

    return pd.DataFrame(1 - distances)


def similarity_of_anime_lists(dataframe1, dataframe2, encoder):
    similarities = similarity(
        encoder.encode(dataframe1["genres"]), encoder.encode(dataframe2["genres"])
    )
    similarities = similarities.apply(np.nanmean, axis=1)

    return similarities


def score_by_cluster_similarity(encoder, target_df, source_df, weighted=False):
    scores = pd.DataFrame(index=target_df.index)

    for cluster_id, cluster in source_df.groupby("cluster"):
        similarities = similarity_of_anime_lists(target_df, cluster, encoder)

        if weighted:
            averages = cluster["user_score"].mean() / 10
            similarities = similarities * averages

        scores["cluster_" + str(cluster_id)] = similarities

    target_df["recommend_score"] = scores.apply(np.max, axis=1)

    return target_df.sort_values("recommend_score", ascending=False)


def score_by_genre_similarity(encoder, target_df, source_df, weighted=False):
    similarities = similarity_of_anime_lists(target_df, source_df, encoder)

    if weighted:
        averages = genre_average_scores(source_df)
        similarities = pdutil.normalize_column(similarities) + (
            1.5
            * pdutil.normalize_column(
                target_df["genres"].apply(user_genre_weight, args=(averages,))
            )
        )
        similarities = similarities / 2

    target_df["recommend_score"] = similarities

    return target_df.sort_values("recommend_score", ascending=False)


def genre_average_scores(dataframe):
    gdf = dataframe.explode("genres")

    return gdf.groupby("genres")["user_score"].mean()


def user_genre_weight(genres, averages):
    mean = np.nanmean([averages.get(genre, np.nan) for genre in genres])
    mean = mean if not np.isnan(mean) else 0.0

    return mean
