"""Provide api to get search restaurants."""

from flask_restful import Resource
from app import nckufeed_db, api


class Search(Resource):
    """The class provide GET for users to search for wanted restaruants.
    """

    def get(self, search_string):
        """GET method to get search results.

        Return:
            List of searching items.
        """

        restaurants_collection = nckufeed_db["restaurants"]
        results = list(
            restaurants_collection.aggregate(
                [
                    {
                        "$search": {
                            "index": "restaurants",
                            "text": {
                                "query": search_string,
                                "path": "name",
                                "fuzzy": {
                                    "maxEdits": 2
                                }
                            }
                        }
                    },
                    {
                        "$limit": 100
                    }
                ]
            )
        )
        for result in results:
            result["_id"] = str(result["_id"])
        return { "result": results }, 200

api.add_resource(Search, "/search/<string:search_string>")
