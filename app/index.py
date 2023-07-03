from app import app, nckufeed_db
from app.models import Rating, Comment


@app.route("/")
def index():
    print("hello")
    return "<h1>hello<h1>"


@app.route("/test")
def create():
    comment_collection = nckufeed_db["comment"]
    comment_data = {
        "content": "這家餐廳真棒！",
        "rating": {
            "cleanliness": 9,
            "service": 8,
            "deliciousness": 9,
            "CPR": 7,
            "overall": 9
        }
    }
    comment = Comment(**comment_data)
    comment_collection.insert_one(comment.dict())
    return "<h1>test<h1>"
