"""Database class variables."""

import os
from fastapi import HTTPException, status
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import redis
from ..models.user import User

class RedisDB(object):
    """
    Redis client class and probive some operations.
    """

    client = None

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
    # TODO: add redis operations


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

    def modify_user(self, user: dict):
        """
        Modify a user's data in database.

        Args:
            user (dict): User's new data.

        Returns:
            dict: User's new data.
        """
        # TODO: finish this
