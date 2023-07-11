from threading import Thread
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from app import redis_db, nckufeed_db
from app.models import Restaurant, Recommend_List

food_types = ["American Foods", "Taiwanese Foods", "Fast Foods", "Thai Foods", "Soup", "Pizza", "Desserts", "Street Foods", "Drinks", "Cafe", "BBQ", "Indian Foods", "Hong Kong Style Foods", "Vegetarian Diet", "Breakfast", "Korean Foods", "Italian Foods", "Seafood"]

def create_user_hmap(nick_name: str, preferences: list):
    """Create hash map in redis for specific user's preference.

    Args:
        nick_name (str): nick name of user to create the hash map
        preferences (list): original preferences of user in database

    """

    for food_type, preference in zip(food_types, preferences):
        redis_db.hset(nick_name, food_type, preference)


def increase_preference(nick_name: str, tags: list):
    """Increases user's preference according to the restaurant
    the user clicked.

    Args:
        nick_name (str): nick name of user to increase preference
        tags (list): the restaurant's tags which the user clicked

    """

    for tag in tags:
        redis_db.hincrbyfloat(nick_name, tag, 0.1)


class RecommendComputeTask(Thread):
    """The class to compute recommend list when user logout.
    """

    def __init__(self, nick_name: str):
        """Init thread class and some variables

        Args:
            nick_name (str): user's nick name
        
        """
        super(RecommendComputeTask, self).__init__()
        self.__nick_name = nick_name

    def run(self):
        """Compute user's preferences and restaurants similarity and insert recommend list
        to database.
        """

        # Get user's new preference from redis
        new_preferences = [float(x) for x in redis_db.hvals(self.__nick_name)]
        redis_db.delete(self.__nick_name)
        new_preferences_matrix = np.array(new_preferences, dtype=np.float32)

        # Get all restaurants' info from database
        restaurants = nckufeed_db["restaurants"]
        restaurants_df = pd.DataFrame(list(restaurants.find({})))
        tags = restaurants_df.loc[:, "tags"]

        # One hot encoding tags and compute similarity
        mlb = MultiLabelBinarizer()
        tags_matrix = pd.DataFrame(mlb.fit_transform(tags), columns=mlb.classes_, index=tags.index).to_numpy(dtype=np.float32)
        similarity = np.dot(tags_matrix, np.transpose(new_preferences_matrix)).tolist()

        # Insert similarity to dataframe and generate new recommend list
        restaurants_df.insert(0, "similarity", similarity)
        restaurants_df.sort_values(by=["similarity"], ascending=False, inplace=True)

        recommendation = []
        for idx, row in restaurants_df.iterrows():
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
            if idx == 30:
                break
        
        recommend_list = Recommend_List(
            nick_name=self.__nick_name,
            recommendation=recommendation
        )
        recommend_list_collection = nckufeed_db["recommend_list"]
        recommend_list_collection.insert_one(recommend_list.dict())
        