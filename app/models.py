"""Provide data model for database."""

from typing import List, Optional
from datetime import datetime, timedelta, timezone
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

    uid: str
    target_id: str
    rating: Rating
    content: str

class Restaurant(BaseModel):
    """Restaurant model.
    """

    name: str
    star: float = Field(default=0, ge=0)
    tags: List[str] = Field(default_factory=list)
    open_hour: List[str] = Field(default_factory=list)
    address: Optional[str] = None
    phone_number: Optional[str] = None
    service: List[str] = Field(default_factory=list)
    website: Optional[str] = None

class User(BaseModel):
    """User model.
    """

    uid: str
    nick_name: str
    email: str
    self_intro: Optional[str]
    profile_photo: Optional[str]
    restaurants_id: List[str] = Field(default_factory=list)
    preference: List[float] = Field(default_factory=list)

class RecommendList(BaseModel):
    """Recommend list model. 100 restaurants for one page.
    """

    uid: str
    page: int
    recommendation: List[Restaurant]

class Post(BaseModel):
    """Post model.
    """

    uid: str
    title: str
    content: str # includes picture url
    restaurants_id: str
    like: int = Field(default=0, ge=0)
    comments_id: List[str] = Field(default_factory=list)
    release_time: str = datetime.now(timezone(timedelta(hours=+8))).strftime("%Y-%m-%d, %H:%M:%S")
