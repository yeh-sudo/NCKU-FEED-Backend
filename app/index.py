from app import app, nckufeed_db
from app.models import Comment, User, Post
from app.utils import create_user_hmap, RecommendComputeTask
from bson.objectid import ObjectId

comments_collection = nckufeed_db["comments"]
restaurants_collection = nckufeed_db["restaurants"]
users_collection = nckufeed_db["users"]
posts_collection = nckufeed_db["posts"]

@app.route("/")
def index():
    return "<h1>hello<h1>"

@app.route("/test_recommend")
def test():
    user = User(**users_collection.find_one({"uid": "D1MHod9o0ZOEMGCiAhuPQBwEr2a2"}))
    create_user_hmap("D1MHod9o0ZOEMGCiAhuPQBwEr2a2", user.preference)
    thread = RecommendComputeTask("D1MHod9o0ZOEMGCiAhuPQBwEr2a2")
    thread.start()
    return "<h1>test<h1>"

@app.route("/test")
def create():
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

    post_data = {
        "title": "good for this one!",
        "content": "<h1>test<h1>",
        "restaurants_id": "test"
    }
    # comment = Comment(**comment_data)
    # comments_collection.insert_one(comment.dict())
    post = Post(**post_data)
    posts_collection.insert_one(post.dict())
    print(post.release_time)
    # gett = posts_collection.find_one({"_id": ObjectId("64b91e3d0eb46e5ba28f43e7")})
    # print(gett['release_time'])
    return "<h1>test<h1>"