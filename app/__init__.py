from flask import Flask
from flask_restful import Api, Resource
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
api = Api(app)
client = MongoClient(os.getenv("MONGO_URI"))
nckufeed_db = client.nckufeed

from app import index
from app import recommender