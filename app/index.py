from app import app, nckufeed_db
from app.models import Comment, User
from app.utils import create_user_hmap, RecommendComputeTask

@app.route("/")
def index():
    return "<h1>hello<h1>"

@app.route("/test_recommend")
def test():
    users_collection = nckufeed_db["users"]
    user = User(**users_collection.find_one({"nick_name": "yehsudo"}))
    create_user_hmap("yehsudo", user.preference)
    thread = RecommendComputeTask("yehsudo")
    thread.start()
    del thread
    return "<h1>test<h1>"

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