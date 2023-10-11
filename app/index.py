from app import app, nckufeed_db
from app.models import Restaurant, User
from app.utils import create_user_hmap, RecommendComputeTask
from app.utils import DatabaseProcessor
from bson.objectid import ObjectId
import pandas as pd

DB = DatabaseProcessor()
posts_collection = DB.posts_collection
comments_collection = DB.comments_collection
restaurants_collection = DB.restaurants_collection
users_collection = DB.users_collection

@app.route("/hello")
def test():
    return "<h1>test<h1>"
