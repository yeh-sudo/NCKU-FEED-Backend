"""Establish connection or delete connection between application and MongoDB, Redis."""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import redis

def connect_to_database():
    """
    Connect to database.

    Return:
        object: connection to database.
    """

    try:
        connection = MongoClient(os.getenv("MONGO_URI"))
    except ConnectionFailure as error:
        print(f"Error: MongoDB connection not established {error}")
    else:
        print("MongoDB: Connection established.")
    return connection

def connect_to_redis():
    """
    Connect to Redis.

    Return:
        object: connection to Redis.
    """

    try:
        connection = redis.Redis(host=os.getenv("REDIS_HOST"),
                                 port=os.getenv("REDIS_PORT"),
                                 encoding="utf8",
                                 decode_responses=True)
    except ConnectionError as error:
        print(f"Error: Redis connection not established {error}")
    else:
        print("Redis: Connection established.")
    return connection
