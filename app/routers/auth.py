"""Provide api for user to login, register and logout."""

from typing import Union
from fastapi import APIRouter, Depends, status, Path, HTTPException, BackgroundTasks
from ..utils.jwt import create_access_token, validate_token
from ..utils.databases import NckufeedDB, RedisDB
from ..utils.recommend_task import RecommendComputeTask
from ..models.user import User

router = APIRouter()


@router.get("/user/{uid}", status_code=status.HTTP_200_OK)
async def get_user(uid: str = Path(description="user's uid from Firebase.")):
    """
    GET method for authentication api.

    Args:
        uid (str): The user's uid from Firebase.

    Returns:
        dict: JWT token and user's data.
    """

    if uid is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="uid not provided.")
    user_info = NckufeedDB().find_user(uid)
    RedisDB().create_user_hmap(uid, user_info["preference"])
    access_token = create_access_token(data=uid)
    return {
        "access_token": access_token,
        "user_info": user_info
    }


@router.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(new_user: User):
    """
    POST method for authentication api.

    Args:
        new_user (User): New user's data.

    Returns:
        dict: JWT token and user's data.
    """

    if new_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="new user not provided.")
    new_user = NckufeedDB().create_user(new_user.model_dump())
    access_token = create_access_token(data=new_user["uid"])
    return {
        "access_token": access_token,
        "user_info": new_user
    }


@router.put("/user", status_code=status.HTTP_200_OK)
async def modify_user(user_data: User, uid: Union[None, str] = Depends(validate_token)):
    """
    PUT method for authentication api.

    Args:
        uid (str): User's uid.
        user_data (User): User's data that needs to be modified.

    Returns:
        dict: User's new data.
    """

    if uid is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="JWT token is invalid.")
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="user data not privided.")
    user_info = NckufeedDB().modify_user(uid, user_data)
    return user_info


@router.delete("/user/{restaurant_id}", status_code=status.HTTP_200_OK)
async def delete_restaurant_id(restaurant_id: str, uid: Union[None, str] = Depends(validate_token)):
    """
    Delete method for authentication api.

    Args:
        uid (str): User's uid.
        restaurant_id (str): The restaurant id which will be delete.

    Returns:
        dict: User's new data.
    """

    if restaurant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="restaurant_id is invalid.")
    if uid is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="JWT token is invalid.")
    user_info = NckufeedDB().delete_restaurant_id(uid, restaurant_id)
    return user_info


@router.get("/logout", status_code=status.HTTP_200_OK)
async def logout(background_task: BackgroundTasks, uid: Union[None, str] = Depends(validate_token)):
    """
    GET method for user to logout.

    Args:
        uid (str): User's uid.

    Return:
        Return successful message if logout successfully.
    """

    if uid is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="JWT token is invalid.")

    def compute_recommendation(uid: str):
        compute_recommendation = RecommendComputeTask(uid)
        compute_recommendation.run()

    background_task.add_task(compute_recommendation, uid)
    return { "message": "Logout successfully." }
