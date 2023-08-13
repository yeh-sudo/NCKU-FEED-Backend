"""Provide function and class to change user's preference and compute recommend lists."""

from threading import Thread
from datetime import datetime, timedelta, timezone
import json
from bson import ObjectId
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from flask_jwt_extended import get_jwt, create_access_token
from pymongo.errors import OperationFailure
from app import app, redis_db, nckufeed_db, jwt
from app.models import Restaurant, RecommendList, Comment, Post

food_types = ["American Foods",
              "Taiwanese Foods",
              "Fast Foods",
              "Thai Foods",
              "Soup",
              "Pizza",
              "Desserts",
              "Street Foods",
              "Drinks", "Cafe",
              "BBQ",
              "Indian Foods",
              "Hong Kong Style Foods",
              "Vegetarian Diet",
              "Breakfast",
              "Korean Foods",
              "Italian Foods",
              "Seafood"
            ]

def create_user_hmap(uid: str, preferences: list):
    """Create hash map in redis for specific user's preference.

    Args:
        uid (str): user's uid
        preferences (list): original preferences of user in database

    """

    for food_type, preference in zip(food_types, preferences):
        redis_db.hset(uid, food_type, preference)


def increase_preference(uid: str, tags: list):
    """Increases user's preference according to the restaurant
    the user clicked.

    Args:
        uid (str): user's uid
        tags (list): the restaurant's tags which the user clicked

    """

    for tag in tags:
        redis_db.hincrbyfloat(uid, tag, 0.1)


class RecommendComputeTask(Thread):
    """The class to compute recommend list when user logout.
    """

    def __init__(self, uid: str):
        """Init thread class and some variables

        Args:
            uid (str): user's uid
        
        """
        super(RecommendComputeTask, self).__init__()
        self.__uid = uid

    def run(self):
        """Compute user's preferences and restaurants similarity and insert recommend list
        to database.
        """

        # Get user's new preference from redis
        new_preferences = [float(x) for x in redis_db.hvals(self.__uid)]
        user_collection = nckufeed_db["users"]
        user_collection.update_one({"uid": self.__uid}, {"$set": {"preference": new_preferences}})
        redis_db.delete(self.__uid)
        new_preferences_matrix = np.array(new_preferences, dtype=np.float32)

        # Get all restaurants' info from database
        restaurants = nckufeed_db["restaurants"]
        restaurants_df = pd.DataFrame(list(restaurants.find({})))
        tags = restaurants_df.loc[:, "tags"]

        # One hot encoding tags and compute similarity
        mlb = MultiLabelBinarizer()
        tags_matrix = pd.DataFrame(mlb.fit_transform(tags),
                                   columns=mlb.classes_,
                                   index=tags.index).to_numpy(dtype=np.float32)
        similarity = np.dot(tags_matrix, np.transpose(new_preferences_matrix)).tolist()

        # Insert similarity to dataframe and generate new recommend list
        restaurants_df.insert(0, "similarity", similarity)
        restaurants_df.sort_values(by=["similarity"], ascending=False, inplace=True)

        recommendation = []
        count = 0
        for _, row in restaurants_df.iterrows():
            if count == 30:
                break
            restaurant = Restaurant(
                name=row["name"],
                star=row["star"],
                tags=row["tags"],
                open_hour=[row["open_hour"]],
                address=row["address"],
                phone_number=row["phone_number"],
                service=[row["service"]],
                web=row["web"]
            )
            recommendation.append(restaurant)
            count += 1

        recommend_list = RecommendList(
            uid=self.__uid,
            recommendation=recommendation
        )
        recommend_list_collection = nckufeed_db["recommend_list"]
        recommend_list_collection.update_one({"uid": self.__uid},
                                             {"$set": recommend_list.dict()},
                                             upsert=True)


@app.after_request
def refresh_expiring_jwts(response):
    """Check if the jwt is expired and refresh the jwt token
    """

    try:
        claims = get_jwt()
        exp_timestamp = claims["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(days=3))
        if target_timestamp > exp_timestamp:
            additional_claims = {
                "uid": claims["uid"],
                "nick_name": claims["nick_name"],
                "email": claims["email"]
            }
            access_token = create_access_token(claims["uid"], additional_claims=additional_claims)
            data = response.get_json()
            data["access_token"] = access_token
            response.data = json.dumps(data)
        return response
    except(RuntimeError, KeyError):
        return response


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(_, jwt_payload: dict):
    """Check if the token is valid.

    Return:
        True if token is revoked.
    """

    jti = jwt_payload["jti"]
    token_in_redis = redis_db.get(jti)
    return token_in_redis is not None


# CRUD
class DatabaseProcessor:
    """Provide functions to take some operation on database.
    """

    def __init__(self):
        self.posts_collection = nckufeed_db["posts"]
        self.restaurants_collection = nckufeed_db["restaurants"]
        self.users_collection = nckufeed_db["users"]
        self.comments_collection = nckufeed_db["comments"]

    """used"""
    def insert_restaurant(self, restaurant_info):
        """Insert one restaurant info

        Args:
            restaurant_info
            e.g.  restaurant_data = {
                    "name": "白吃",
                    "star": 4.3,
                    "tags": ["Taiwanese Foods", "Street Foods"],
                    "open_hour": ["14:30-20:00", "00:00-04:00"],
                    "address": '台南市北區',
                    "phone_number": "0424242487",
                    "service": ['內用', '外帶'],
                    "website": "www.google.com"
                   }

        Return:
            True if insert successfully.
        """

        try:
            restaurant = Restaurant(**restaurant_info)
            self.restaurants_collection.insert_one(restaurant.dict())
            return True
        except OperationFailure as error:
            print("Insert new restaurant failed!!")
            print(error)
            return False

    def get_all_restaurants(self):
        """Get all restaurant info.

        Return:
            False if some error happened, else all restaurant info.
        """
        try:
            restaurants = self.restaurants_collection.find({}, {"_id":0})
        except OperationFailure:
            print("Get all restaurants error!")
            return False
        else:
            return list(restaurants)

    """used"""
    def get_restaurant_info(self, restaurant_id):
        """Get one restaurant info

        Args:
            restaurant_id (str)

        Return:
            False if some error happened or restaurant not exist,
            else return specific restaurant info.
        """

        try:
            restaurant = self.restaurants_collection.find_one({"_id": ObjectId(restaurant_id)})
        except OperationFailure:
            print("Get restaurant info error!")
            return False
        else:
            if restaurant is None:
                print("There is no such restaurant!")
                return False
            else:
                restaurant['_id'] = str(restaurant['_id'])
                return restaurant

    """used"""
    def insert_comment(self, json_input):
        """Insert one comment info

        Args:
            json_input
            e.g. comment_data = {
                    "content": "這家餐廳真棒！",
                    "rating": {
                        "cleanliness": 9,
                        "service": 8,
                        "deliciousness": 9,
                        "CPR": 7,
                        "overall": 9
                    },
                    "uid": "",
                    "target_id": ""
                }

            Return:
                True if insert successfully.
        """

        try:
            comment = Comment(**json_input)
            self.comments_collection.insert_one(comment.dict())
            return True
        except OperationFailure as error:
            print("Insert new restaurant failed!!")
            print(error)
            return False

    """used"""
    def update_comment_content(self, json_input):
        """Update one comment's content

        Args:
            json_input
            e.g.  json_input = {
                    "_id": "",
                    "content": "I don't like it actually"
                  }
        Return:
            False if some error happened or comment not exist,
            else True
        """
        try:
            comment = self.comments_collection.find_one_and_update({'_id': ObjectId(json_input['_id'])},
                                                                   {'$set': {'content': json_input['content']}})
        except OperationFailure:
            print("update_comment_content operation failed!")
            return False
        else:
            if comment is None:
                print("There is no such comment!")
                return False
            else:
                return True

    """used"""
    def get_comment_from_restaurant_or_post(self, target_id):
        """Get all comments from a restaurant or post

            Args:
                target_id (restaurant's _id or post's _id)

            Return:
                False if some error happened,
                else return a comment list.
        """
        try:
            comments = self.comments_collection.find({"target_id": target_id})
        except OperationFailure:
            print("get_comment_from_restaurant_or_post operation failed!")
            return False
        else:
            if comments is None:
                print("There is no such comment!")
                return False
            else:
                return list(comments)

    """used"""
    def delete_comment(self, comment_id):
        """Delete one comment

        Args:
            comment_id (_id)

        Return:
            False if some error happened,
            else True
        """
        try:
            comment = self.comments_collection.find_one_and_delete({'_id': ObjectId(comment_id)})
        except OperationFailure:
            print('delete_comment operation failed!')
            return False
        else:
            if comment is None:
                print("There is no such comment!")
                return False
            else:
                return True

    """used"""
    def insert_post(self, json_input):
        """Insert one post
        Args:
            json_input
            e.g. post_data = {
                    "uid": "D1MHod9o0ZOEMGCiAhuPQBwEr2a2"
                    "title": "這家是舒服的",
                    "content": "我給滿分",
                    "restaurants_id": "123"
                }
                "like", "comments_id", "release_time" can be null
                Return:
                    True if insert successfully.
        """

        try:
            post = Post(**json_input)
            self.posts_collection.insert_one(post.dict())
            return True
        except OperationFailure as error:
            print("Insert new post failed!!")
            print(error)
            return False

    """used"""
    def get_post(self, post_id):
        """Get post information

            Args:
                post_id (post's _id)

            Return:
                False if some error happened,
                else return a post.
        """
        try:
            post = self.posts_collection.find_one({"_id": ObjectId(post_id)})
        except OperationFailure:
            print("get_post operation failed!")
            return False
        else:
            if post is None:
                print("There is no such post!")
                return False
            else:
                post['_id'] = str(post['_id'])
                return post

    """used"""
    def delete_post(self, post_id):
        """Delete one post

        Args:
            post_id (_id)
            e.g.:
            {
                "id": "64d10a7279e8302c9c3a050a"
            }

        Return:
            False if some error happened,
            else True
        """
        try:
            post = self.posts_collection.find_one_and_delete({'_id': ObjectId(post_id)})
        except OperationFailure:
            print('delete_post operation failed!')
            return False
        else:
            if post is None:
                print("There is no such post!")
                return False
            else:
                return True

    """used"""
    def update_post_content(self, json_input):
        """Update one post's content

        Args:
            json_input
                e.g.  json_input = {
                        "_id": "",
                        "content": "I don't like it actually"
                      }
                      
        Return:
            False if some error happened or post not exist,
            else True
        """
        try:
            post = self.posts_collection.find_one_and_update({'_id': ObjectId(json_input['_id'])},
                                                                   {'$set': {'content': json_input['content']}})
        except OperationFailure:
            print("update_post_content operation failed!")
            return False
        else:
            if post is None:
                print("There is no such post!")
                return False
            else:
                return True

    """used"""
    def update_post_title(self, json_input):
        """Update one post's title

        Args:
            json_input
                e.g.  json_input = {
                        "_id": "",
                        "title": "Good enough"
                      }

        Return:
            False if some error happened or post not exist,
            else True
        """
        try:
            post = self.posts_collection.find_one_and_update({'_id': ObjectId(json_input['_id'])},
                                                                   {'$set': {'title': json_input['title']}})
        except OperationFailure:
            print("update_post_title operation failed!")
            return False
        else:
            if post is None:
                print("There is no such post!")
                return False
            else:
                return True

    """used"""
    def update_restaurant_open_hour(self, json_input):
        """Update one restaurant's open hour

        Args:
            json_input
                e.g.  json_input = {
                        "_id": "",
                        "open_hour": ["14:30-20:00", "00:00-04:00"]
                      }

        Return:
            False if some error happened or restaurant not exist,
            else True
        """
        try:
            restaurant = self.restaurants_collection.find_one_and_update({'_id': ObjectId(json_input["_id"])},
                                                                         {'$set': {'open_hour':json_input['open_hour']}})
        except OperationFailure:
            print("update_restaurant_open_hour operation failed!")
            return False
        else:
            if restaurant is None:
                print('There is no such restaurant')
                print(json_input['_id'])
                return False
            else:
                return True

    """used"""
    def update_restaurant_phone_number(self, json_input):
        """Update one restaurant's phone_number

        Args:
            json_input
                e.g.  json_input = {
                        "_id": "",
                        "phone_number": "0933455455"
                      }

        Return:
            False if some error happened or restaurant not exist,
            else True
        """
        try:
            restaurant = self.restaurants_collection.find_one_and_update({'_id': ObjectId(json_input['_id'])},
                                                                         {'$set': {'phone_number':json_input['phone_number']}})
        except OperationFailure:
            print("update_restaurant_phone_number operation failed!")
            return False
        else:
            if restaurant is None:
                print('There is no such restaurant')
                print(json_input['_id'])
                return False
            else:
                return True

    """used"""
    def update_restaurant_service(self, json_input):
        """Update one restaurant's service

        Args:
            json_input
                e.g.  json_input = {
                        "_id": "",
                        "service": ["外帶", "外送"]
                      }

        Return:
            False if some error happened or restaurant not exist,
            else True
        """
        try:
            restaurant = self.restaurants_collection.find_one_and_update({'_id': ObjectId(json_input['_id'])},
                                                                         {'$set': {'service':json_input['service']}})
        except OperationFailure:
            print("update_restaurant_service operation failed!")
            return False
        else:
            if restaurant is None:
                print('There is no such restaurant')
                return False
            else:
                return True

    """used"""
    def update_restaurant_website(self, json_input):
        """Update one restaurant's web

        Args:
            json_input
                e.g.  json_input = {
                        "_id": "",
                        "web": "www.facebook.com"
                      }

        Return:
            False if some error happened or restaurant not exist,
            else True
        """
        try:
            restaurant = self.restaurants_collection.find_one_and_update({'_id': ObjectId(json_input['_id'])},
                                                                         {'$set': {'website':json_input['website']}})
        except OperationFailure:
            print("update_restaurant_web operation failed!")
            return False
        else:
            if restaurant is None:
                print('There is no such restaurant')
                return False
            else:
                return True

    """used"""
    def delete_restaurant(self, restaurant_id):
        """Delete one post

            Args:
                restaurant_id (_id)
                e.g.:
                {
                    "id": "64d10a7279e8302c9c3a050a"
                }

            Return:
                False if some error happened,
                else True
        """
        try:
            restaurant = self.restaurants_collection.find_one_and_delete({'_id': ObjectId(restaurant_id)})
        except OperationFailure:
            print('delete_restaurant operation failed!')
            return False
        else:
            if restaurant is None:
                print("There is no such restaurant!")
                return False
            else:
                return True