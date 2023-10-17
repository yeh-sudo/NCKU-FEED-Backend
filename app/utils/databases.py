"""Database class variables."""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import redis

class RedisDB(object):
    """Redis client class and probive some operations.
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


class NckufeedDB(object):
    """MongoDB client class and probive some operations.
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
