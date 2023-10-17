"""Provide user model for database."""

from typing import List, Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    """User model.
    """

    uid: str
    nick_name: str
    email: str
    self_intro: Optional[str] = Field(default="")
    profile_photo: Optional[str]
    restaurants_id: List[str] = Field(default_factory=list)
    preference: List[float] = Field(default_factory=list)
