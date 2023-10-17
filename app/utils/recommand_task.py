"""Recommand task and functions"""

# TODO: modify redis import
from app import redis_db

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

def create_user_hmap(uid: str, preferences: list):
    """Create hash map in redis for specific user's preference.

    Args:
        uid (str): user's uid
        preferences (list): original preferences of user in database

    """

    for food_type, preference in zip(food_types, preferences):
        redis_db.hset(uid, food_type, preference)
