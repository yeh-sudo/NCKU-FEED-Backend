from flask import Flask
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

from app import index
from app.example import example
