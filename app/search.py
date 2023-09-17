"""Provide api to get search restaurants."""

from flask_restful import Resource, reqparse
from app import nckufeed_db, api


class Search(Resource):
    """The class provide GET for users to search for wanted restaruants.
    """

    def get(self):
        """GET method to get search results.

        Return:
            List of searching items.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("search_name", type=str, location="args", required=True)
        parser.add_argument("search_region", type=str, location="args", required=True)
        parser.add_argument("search_time", type=str, location="args", required=True)
        args = parser.parse_args()
        print(args.search_name, args.search_region, args.search_time)

        restaurants_collection = nckufeed_db["restaurants"]
        results = list(
            restaurants_collection.aggregate(
                [
                    {
                        "$search": {
                            "index": "searchRestaurants",
                            "text": {
                                "query": "{\
                                    \"name\": {\"$eq\": %s},\
                                    \"frontend_tags\": {\
                                        \"region\": {\"$eq\": %s},\
                                        \"time_period\": {\"$eq\": %s}\
                                    }\
                                }" % (args.search_name, args.search_region, args.search_time),
                                "path": {
                                    "wildcard": "*"
                                },
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

api.add_resource(Search, "/search")
