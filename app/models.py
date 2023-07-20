"""Provide data model for database."""

from typing import List, Optional
from pydantic import BaseModel, Field

class Rating(BaseModel):
    """Rating model.
    """

    cleanliness: int = Field(default=0, ge=0)
    service: int = Field(default=0, ge=0)
    deliciousness: int = Field(default=0, ge=0)
    CPR: int = Field(default=0, ge=0)
    overall: int = Field(default=0, ge=0)

class Comment(BaseModel):
    """Comment model.
    """

    rating: Rating
    content: str

class Restaurant(BaseModel):
    """Restaurant model.
    """

    name: str
    comments_id: List[str] = Field(default_factory=list)
    star: float = Field(default=0, ge=0)
    tags: List[str] = Field(default_factory=list)
    open_hour: str = None
    address: str = None
    phone_number: str = None
    service: str = None
    web: str = None

class User(BaseModel):
    """User model.
    """

    uid: str
    nick_name: str
    email: str
    self_intro: Optional[str]
    profile_photo: Optional[str]
    comments_id: List[str] = Field(default_factory=list)
    restaurants_id: List[str] = Field(default_factory=list)
    preference: List[float] = Field(default_factory=list)

class RecommendList(BaseModel):
    """Recommend list model.
    """

    uid: str
    recommendation: List[Restaurant]

class Post(BaseModel):
    """Post model.
    """

    content: str
    picture: Optional[List[str]]
    restaurants_id: str
    like: int = Field(default=0, ge=0)
    comment_id: List[str] = Field(default_factory=list)
