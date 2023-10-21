"""Database class variables."""

import os
from fastapi import HTTPException, status
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import redis
from ..models.user import User
from ..models.recommend_list import RecommendList
from .recommend_task import RecommendComputeTask

class RedisDB(object):
    """
    Redis client class and probive some operations.
    """

    client = None
    food_types = ["American Foods",
                  "Taiwanese Foods",
                  "Fast Foods",
                  "Thai Foods",
                  "Soup",
                  "Pizza",
                  "Desserts",
                  "Street Foods",
                  "Drinks",
                  "Cafe",
                  "BBQ",
                  "Indian Foods",
                  "Hong Kong Style Foods",
                  "Vegetarian Diet",
                  "Breakfast",
                  "Korean Foods",
                  "Italian Foods",
                  "Seafood"
                ]

    def __init__(self) -> None:
        if RedisDB.client is None:
            try:
                RedisDB.client = redis.Redis(host=os.getenv("REDIS_HOST"),
                                              port=os.getenv("REDIS_PORT"),
                                              encoding="utf8",
                                              decode_responses=True)
            except ConnectionError as error:
                print(f"Error: Redis connection not established {error}")
            else:
                print("Redis: Connection established.")

    def create_user_hmap(self, uid: str, preferences: list):
        """
        Create hash map in redis for specific user's preference.

        Args:
            uid (str): user's uid
            preferences (list): original preferences of user in database
        """

        for food_type, preference in zip(RedisDB.food_types, preferences):
            RedisDB.client.hset(uid, food_type, preference)

    def increase_preference(self, uid: str, tags: list):
        """
        Increase user's preference according to the restaurant
        the user clicked.

        Args:
            uid (str): user's uid
            tags (list): the restaurant's tags which the user clicked
        """

        for tag in tags:
            RedisDB.client.hincrbyfloat(uid, tag, 0.1)

    def get_preference(self, uid: str):
        """
        Get user's preferences.

        Args:
            uid (str): user's uid
        
        Return:
            list[float]: user's preferences
        """
        preferences = [float(x) for x in RedisDB.client.hvals(uid)]
        return preferences





class NckufeedDB(object):
    """
    MongoDB client class and probive some operations.
    """

    client = None

    def __init__(self) -> None:
        if NckufeedDB.client is None:
            try:
                NckufeedDB.client = MongoClient(os.getenv("MONGO_URI"))
            except ConnectionFailure as error:
                print(f"Error: MongoDB connection not established {error}")
            else:
                print("MongoDB: Connection established.")

    def find_user(self, uid: str):
        """
        Find user's data by user's uid.

        Args:
            uid (str): The user's uid.

        Returns:
            dict: The user's data.
        """

        user_collection = NckufeedDB.client.nckufeed["users"]
        try:
            user = User(**user_collection.find_one({"uid": uid}))
        except OperationFailure as error:
            print(f"Error: Couldn't find user's data {error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="uid not provided.") from error
        return user.model_dump()

    def create_user(self, new_user: dict):
        """
        Create a new user in database.

        Args:
            new_user (dict): New user's data.

        Returns:
            dict: New user's data.
        """

        user_collection = NckufeedDB.client.nckufeed["users"]
        try:
            user_collection.insert_one(new_user)
        except OperationFailure as error:
            print(f"Error: Couldn't insert new user's data to database {error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Can't insert new user.") from error
        print("[NCKUFEED Database] Successfully insert a new user.")
        return new_user

    def modify_user(self, uid: str, user_data: dict):
        """
        Modify a user's data in database.

        Args:
            uid (str): User's uid.
            user_data (dict): User's new data.

        Returns:
            dict: User's new data.
        """

        user_collection = NckufeedDB.client.nckufeed["users"]
        if "nick_name" in user_data:
            try:
                user_collection.update_one(
                    { "uid": uid },
                    { "$set":
                        { "nick_name":
                            user_data["nick_name"]
                        }
                    }
                )
            except OperationFailure as error:
                print(f"Error: Couldn't update user's name {error}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Can't update user's nick_name.") from error
        if "profile_photo" in user_data:
            try:
                user_collection.update_one(
                    { "uid": uid },
                    { "$set":
                        { "profile_photo":
                            user_data["profile_photo"]
                        }
                    }
                )
            except OperationFailure as error:
                print(f"Error: Couldn't update user's profile_photo {error}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Can't update user's profile_photo.") from error
        if "self_intro" in user_data:
            try:
                user_collection.update_one(
                    { "uid": uid },
                    { "$set":
                        { "self_intro":
                            user_data["self_intro"]
                        }
                    }
                )
            except OperationFailure as error:
                print(f"Error: Couldn't update user's self_intro {error}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Can't update user's self_intro.") from error
        if "restaurants_id" in user_data:
            try:
                user_collection.update_one(
                    { "uid": uid },
                    { "$push":
                        { "restaurants_id":
                            user_data["restaurants_id"]
                        }
                    }
                )
            except OperationFailure as error:
                print(f"Error: Couldn't update user's self_intro {error}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Can't update user's self_intro.") from error
        if "preference" in user_data:
            RedisDB().create_user_hmap(uid, user_data["preference"])
            thread = RecommendComputeTask(uid)
            thread.start()
            thread.join()
            RedisDB().create_user_hmap(uid, user_data["preference"])
        user_info = self.find_user(uid)
        return user_info

    def delete_restaurant_id(self, uid: str, restaurant_id: str):
        """
        Delete a restaurant_id in user's data.

        Args:
            uid (str): User's uid.
            restaurant_id (str): The restaurant id which will be delete.

        Returns:
            dict: User's new data.
        """

        user_collection = NckufeedDB.client.nckufeed["users"]
        try:
            user_collection.update_one(
                { "uid": uid },
                { "$pull": { "restaurants_id": restaurant_id } }
            )
        except OperationFailure as error:
            print(f"Error: Couldn't delete restaurant id in user's data {error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Can't delete restaurant id.") from error
        user_info = self.find_user(uid)
        return user_info

    def get_recommendation_list(self, uid: str, page: int):
        """
        Get user's recommendation list.

        Args:
            page (int): Recommend page.
            uid (str): The user's uid from Firebase.

        Returns:
            dict: User's recommendation list.
        """

        recommend_list_collection = NckufeedDB.client.nckufeed["recommend_list"]
        try:
            user_recommendation = list(
                recommend_list_collection.find(
                    {
                        "uid": uid,
                        "page": page
                    },
                    { "_id": 0 }
                )
            )
        except OperationFailure as error:
            print(f"Error: Couldn't get recommendation list {error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Can't get recommendation list.") from error
        recommend_list = RecommendList(
            uid=uid,
            page=page,
            recommendation=user_recommendation[0]["recommendation"]
        )
        return recommend_list.model_dump()

    def get_random_recommendation(self):
        """
        Get user's recommendation list.

        Returns:
            dict: Random recommendation list.
        """

        restaurants_collection = NckufeedDB.client.nckufeed["restaurants"]
        try:
            random_recommendation = list(
                restaurants_collection.aggregate(
                    [
                        { "$sample": { "size": 100 } }
                    ]
                )
            )
        except OperationFailure as error:
            print(f"Error: Couldn't get random recommendation {error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Can't get random recommendation list.") from error
        for recommendation in random_recommendation:
            recommendation["_id"] = str(recommendation["_id"])
        return { "random_recommendation": random_recommendation }
