"""Provide api for user to login, register and logout."""

from fastapi import APIRouter, Depends, status, Path, HTTPException
from ..utils.jwt import create_access_token, validate_token
from ..utils.databases import NckufeedDB, RedisDB
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
    # TODO: create redis hmap
    user = NckufeedDB().find_user(uid)
    data = {
        "uid": user["uid"],
        "nick_name": user["nick_name"],
        "email": user["email"]
    }
    access_token = create_access_token(data=data)
    return {
        "access_token": access_token,
        "user_info": user
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
    data = {
        "uid": new_user["uid"],
        "nick_name": new_user["nick_name"],
        "email": new_user["email"]
    }
    access_token = create_access_token(data=data)
    return {
        "access_token": access_token,
        "user_info": new_user
    }


@router.put("/user", status_code=status.HTTP_200_OK)
async def modify_user(user: User):
    """
    PUT method for authentication api.

    Args:
        user (User): User's data that needs to be modified.

    Returns:
        dict: User's new data.
    """
    # TODO: finish this
