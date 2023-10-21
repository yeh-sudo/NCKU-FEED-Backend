"""Provide api for user to get their recommendation lists."""

from typing import Union
from fastapi import APIRouter, Depends, status, HTTPException
from ..utils.jwt import validate_token
from ..utils.databases import NckufeedDB

router = APIRouter()

@router.get("/recommend/{page}", status_code=status.HTTP_200_OK)
async def get_recommendation(page: int, uid: Union[None, str] = Depends(validate_token)):
    """
    GET method for user to get their own recommendation.

    Args:
        page (int): Recommend page.
        uid (str): The user's uid from Firebase.

    Returns:
        dict: User's recommendation list.
    """

    if uid is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="JWT token is invalid.")
    if page is None or page > 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Page is invalid")
    recommend_list = NckufeedDB().get_recommendation_list(uid, page)
    return recommend_list


@router.get("/randomRecomend", status_code=status.HTTP_200_OK)
async def get_random_recommendation():
    """
    GET method for user to get random recommendation.

    Returns:
        dict: Random recommendation list.
    """

    random_recommendation = NckufeedDB().get_random_recommendation()
    return random_recommendation
