"""Provide api for user to login, register and logout."""

from fastapi import APIRouter, Depends, status, Path, HTTPException
from ..utils.jwt import create_access_token, validate_token
from ..utils.databases import NckufeedDB, RedisDB
from ..models.user import User

router = APIRouter()


@router.get("/user/{uid}", status_code=status.HTTP_200_OK)
async def get_user(uid: str = Path(description="user's uid from Firebase.")):
    """GET method for authentication api.

    Return:
        JWT token.
    """

    if uid is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="uid not provided.")
    user_collection = NckufeedDB.client.nckufeed["users"]
    user = User(**user_collection.find_one({"uid": uid}))
    data = {
        "uid": user.uid,
        "nick_name": user.nick_name,
        "email": user.email
    }
    access_token = create_access_token(data=data)
    return {
        "access_token": access_token,
        "user_info": user.model_dump()
    }


@router.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(new_user: User):
    """POST method for authentication api.

    Return:
        JWT token and status code 201.
    """

    return new_user.model_dump()
