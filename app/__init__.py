from flask import Flask
from flask_restful import Api, Resource
from pymongo import MongoClient
import redis
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
api = Api(app)
client = MongoClient(os.getenv("MONGO_URI"))
nckufeed_db = client.nckufeed
redis_db = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), encoding="utf8", decode_responses=True)

from app import index
from app import recommender