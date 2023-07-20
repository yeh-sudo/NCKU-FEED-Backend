"""Provide api to get recommend list of specific user."""

from flask_restful import Resource
from flask_jwt_extended import get_jwt, jwt_required
from app import nckufeed_db, api
from app.models import RecommendList


class Recommender(Resource):
    """The class provide GET for frontend to get recommend list.
    """

    @jwt_required()
    def get(self):
        """GET method to get recommend list from database.

        Return:
            List of recommendation.
        """

        uid = get_jwt()["uid"]
        recommend_list_collection = nckufeed_db["recommend_list"]
        recommendation = RecommendList(**recommend_list_collection.find_one({"uid": uid}))
        return recommendation.dict(), 200

api.add_resource(Recommender, "/recommend")
