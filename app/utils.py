"""Provide function and class to change user's preference and compute recommend lists."""

from threading import Thread
from datetime import datetime, timedelta, timezone
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from flask_jwt_extended import get_jwt, create_access_token
from app import app, redis_db, nckufeed_db, jwt
from app.models import Restaurant, RecommendList

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
                comments_id=row["comments_id"],
                star=row["star"],
                tags=row["tags"],
                open_hour=row["open_hour"],
                address=row["address"],
                phone_number=row["phone_number"],
                service=row["service"],
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
    def __init__(self):
        self.posts_collection = nckufeed_db["posts"]
        self.restaurants_collection = nckufeed_db["restaurants"]
        self.users_collection = nckufeed_db["users"]
        self.comments_collection = nckufeed_db["comments"]

    def insert_restaurant(self, restaurant_info):
        """Insert one restaurant info

        Args:
            restaurant_info
            e.g.  restaurant_data = {
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

        Return:
            True if insert successfully.
        """
        try:
            restaurant = Restaurant(**restaurant_info)
            self.restaurants_collection.insert_one(restaurant.dict())
            return True
        except Exception as e:
            print("Insert new restaurant failed!!")
            print(e)
            return False

    def get_all_restaurants(self):
        """Get all restaurant info.

        Return:
            False if some error happened, else all restaurant info.
        """
        try:
            restaurants = self.restaurants_collection.find({})
        except:
            print("Get all restaurants error!")
            return False
        else:
            return list(restaurants)

    def get_restaurant_info(self, restaurant_name):
        """Get one restaurant info

        Args:
            restaurant_name (str)

        Return:
            False if some error happened or restaurant not exist, else return specific restaurant info.
        """
        try:
            restaurant = self.restaurants_collection.find_one({"name": restaurant_name})
        except:
            print("Get restaurant info error!")
            return False
        else:
            if restaurant is None:
                print("There is no such restaurant!")
                return False
            else:
                return restaurant