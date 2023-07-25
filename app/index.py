from app import app
from app.models import Comment, User, Post
from app.utils import create_user_hmap, RecommendComputeTask
from app.utils import DatabaseProcessor
from bson.objectid import ObjectId

DB = DatabaseProcessor()
posts_collection = DB.posts_collection
comments_collection = DB.comments_collection
restaurants_collection = DB.restaurants_collection
users_collection = DB.users_collection


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
    # comment = Comment(**comment_data)
    # comments_collection.insert_one(comment.dict())

    post_data = {
        "title": "good for this one!",
        "content": "<h1>test<h1>",
        "restaurants_id": "test"
    }
    # post = Post(**post_data)
    # posts_collection.insert_one(post.dict())
    # print(post.release_time)
    # get = posts_collection.find_one({"_id": ObjectId("64b91e3d0eb46e5ba28f43e7")})
    # print(get['release_time'])

    restaurant_data = {
        "name": "白吃",
        "comments_id": ["1", "2"],
        "star": 4.3,
        "tags": ["Taiwanese Foods", "Street Foods"],
        "open_hour": ["14:30-20:00", "00:00-04:00"],
        "address": '台南市北區',
        "phone_number": "0424242487",
        "service": ['內用', '外帶'],
        "website": "www.google.com"
    }
    # DB.insert_restaurant(restaurant_data)
    restaurants = DB.get_restaurant_info("白吃")
    print(restaurants)
    return "<h1>test<h1>"