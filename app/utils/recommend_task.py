"""Provide thread class to compute recommendation."""

from threading import Thread
import random
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from pymongo.errors import OperationFailure
from fastapi import HTTPException, status
from . import databases
from ..models.recommend_list import RecommendList
from ..models.restaurant import Restaurant


class RecommendComputeTask(Thread):
    """
    The class to compute recommend list when user logout and registered.
    """

    def __init__(self, uid: str):
        """
        Init thread class and some variables

        Args:
            uid (str): user's uid
        """

        super(RecommendComputeTask, self).__init__()
        self.__uid = uid

    def run(self):
        """
        Compute user's preferences and restaurants similarity and insert recommend list
        to database.
        """

        # Get's user's new preference from redis
        new_preferences = databases.RedisDB().get_preference(self.__uid)

        # Update user's new preference in database.
        user_collection = databases.NckufeedDB.client.nckufeed["users"]
        try:
            user_collection.update_one(
                { "uid": self.__uid },
                { "$set":
                    { "preference":
                        new_preferences
                    }
                }
            )
        except OperationFailure as error:
            print(f"Error: Couldn't update new preference {error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Can't update preference.") from error
        databases.RedisDB.client.delete(self.__uid)
        new_preferences_matrix = np.array(new_preferences, dtype=np.float32)

        # Get all restaurants' info from database
        restaurants = databases.NckufeedDB.client.nckufeed["restaurants"]
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
        page = 1
        recommend_list_collection = databases.NckufeedDB.client.nckufeed["recommend_list"]
        for _, row in restaurants_df.iterrows():
            if count == 100:
                count = 0
                random.shuffle(recommendation)
                recommend_list = RecommendList(
                    uid=self.__uid,
                    page=page,
                    recommendation=recommendation
                )
                recommend_list_collection.find_one_and_update(
                    { "uid": self.__uid, "page": page },
                    { "$addToSet":
                        { "recommendation":
                            { "$each": recommend_list.model_dump(by_alias=True)["recommendation"] }
                        }
                    },
                    upsert=True
                )
                recommendation = []
                page += 1

            restaurant = Restaurant(
                _id=str(row["_id"]),
                name=row["name"],
                photos=row["photos"],
                star=row["star"],
                tags=row["tags"],
                frontend_tags=row["frontend_tags"],
                open_hour=row["open_hour"],
                address=row["address"],
                phone_number=row["phone_number"],
                service=row["service"],
                website=row["website"],
                gmap_url=row["gmap_url"]
            )
            recommendation.append(restaurant)
            count += 1

        # Add remaining recommend list to database
        recommend_list = RecommendList(
            uid=self.__uid,
            page=page,
            recommendation=recommendation
        )
        recommend_list_collection.find_one_and_update(
            { "uid": self.__uid, "page": page },
            { "$addToSet":
                { "recommendation":
                    { "$each": recommend_list.model_dump(by_alias=True)["recommendation"] }
                }
            },
            upsert=True
        )
