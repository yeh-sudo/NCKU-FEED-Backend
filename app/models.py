from typing import List, Optional
from pydantic import BaseModel, Field

class Rating(BaseModel):
    cleanliness: int = Field(default=0, ge=0)
    service: int = Field(default=0, ge=0)
    deliciousness: int = Field(default=0, ge=0)
    CPR: int = Field(default=0, ge=0)
    overall: int = Field(default=0, ge=0)

class Comment(BaseModel):
    rating: Rating
    content: str

class Restaurant(BaseModel):
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
    uid: str
    nick_name: str
    self_intro: Optional[str]
    profile_photo: Optional[str]
    comments_id: List[str] = Field(default_factory=list)
    post_id: List[str] = Field(default_factory=list)# 若原本沒有，則預設為空的list
    restaurants_id: List[str] = Field(default_factory=list)
    preference: List[float] = Field(default_factory=list)

class Recommend_List(BaseModel):
    nick_name: str
    recommendation: List[Restaurant]

class Post(BaseModel):
    content: str
    picture: Optional[List[str]]
    restaurants_id: str
    like: int = Field(default=0, ge=0)
    comment_id: List[str] = Field(default_factory=list)
