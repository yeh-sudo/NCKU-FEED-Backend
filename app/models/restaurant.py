"""Provide restaurant model for database."""

from typing import List, Optional
from pydantic import BaseModel, Field, validator

class Restaurant(BaseModel):
    """Restaurant model.
    """

    restaurant_id: Optional[str] = Field(alias="_id")
    name: str
    photos: List[str] = Field(default_factory=list)
    star: float = Field(default=0, ge=0)
    tags: List[str] = Field(default_factory=list)
    frontend_tags: object
    open_hour: List[str] = Field(default_factory=list)
    address: Optional[str] = None
    phone_number: Optional[str] = None
    service: List[str] = Field(default_factory=list)
    website: Optional[str] = None
    gmap_url: Optional[str] = None

    @classmethod
    @validator("tags", "open_hour", "service", "photos", always=True, pre=True)
    def if_field_is_none(cls, value):
        """Restaurant model validator.
        """

        if value is None:
            return []
        return value
