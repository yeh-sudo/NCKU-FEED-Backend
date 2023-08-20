"""Init of flask app and api."""

from datetime import timedelta
import os
from flask import Flask
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
import redis
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)
api = Api(app)
client = MongoClient(os.getenv("MONGO_URI"))
nckufeed_db = client.nckufeed
redis_db = redis.Redis(host=os.getenv("REDIS_HOST"),
                       port=os.getenv("REDIS_PORT"),
                       encoding="utf8",
                       decode_responses=True)


from app import index
from app import recommender
from app import auth, posts, comments, restaurants, search
