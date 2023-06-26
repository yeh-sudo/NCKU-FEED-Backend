from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
cliend = MongoClient(os.getenv("MONGO_URI"))
nckufeed_db = cliend.nckufeed

from app import index
