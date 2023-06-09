from flask import Flask, Response, request
from flask_cors import CORS

from animeippo.view import views
from animeippo.recommendation import builder


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
cors = CORS(app, origins="http://localhost:3000")

recommender = builder.create_builder("anilist").build()


@app.route("/api/seasonal")
def seasonal_anime():
    year = request.args.get("year", None)
    season = request.args.get("season", None)

    if not year:
        return "Validation error", 400

    seasonal = recommender.recommend_seasonal_anime(year, season)

    return Response(
        views.web_view(seasonal.sort_values("popularity", ascending=False)),
        mimetype="application/json",
    )


@app.route("/api/recommend")
def recommend_anime():
    user = request.args.get("user", None)
    year = request.args.get("year", None)
    season = request.args.get("season", None)

    if not all([user, year]):
        return "Validation error", 400

    dataset = recommender.recommend_seasonal_anime(year, season, user)
    categories = recommender.get_categories(dataset)

    return Response(
        views.web_view(dataset.recommendations, categories), mimetype="application/json"
    )
