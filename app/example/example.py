from app import app
import os

@app.route("/example")
def hello():
    return "hello"
