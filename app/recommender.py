from app import nckufeed_db, api
from app.models import Recommend_List
from flask_restful import Resource


class recommender(Resource):
    def get(self, name):
        recommend_list_collection = nckufeed_db["recommend_list"]
        recommendation = Recommend_List(**recommend_list_collection.find_one({"nick_name": name}))
        return recommendation.dict(), 200
    
api.add_resource(recommender, "/recommend/<string:name>")