from pydantic import BaseModel, Field
from typing import List

class Rating(BaseModel):
    cleanliness: int = Field(...)
    service: int = Field(...)
    deliciousness: int = Field(...)
    CPR: int = Field(...)
    overall: int = Field(...)
    
class Comment(BaseModel):
    rating: Rating
    content: str = Field(...)

class Restaurant(BaseModel):
    name: str
    comments_id: List[str]
    star: float
    tags: List[str]
    open_hour: str
    address: str
    phone_number: str
    service: str
    web: str

class User(BaseModel):
    nick_name: str
    self_intro: str
    profile_photo: str
    comments_id: List[str]
    post_id: List[str]
    restaruants_id: List[str]
    preference: List[float]
