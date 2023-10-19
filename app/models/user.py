"""Provide user model for database."""

from typing import List, Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    """User model.
    """

    uid: Optional[str] = Field(default=None)
    nick_name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    self_intro: Optional[str] = Field(default="")
    profile_photo: Optional[str] = Field(default=None)
    restaurants_id: List[str] = Field(default_factory=list)
    preference: List[float] = Field(default_factory=list)
