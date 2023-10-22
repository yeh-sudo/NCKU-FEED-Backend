"""Provide restaurant model for database."""

from typing import List, Optional, Any
from pydantic import BaseModel, Field, model_validator

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

    @model_validator(mode="before")
    @classmethod
    def if_field_is_none(cls, data: Any):
        """Restaurant model validator.
        """

        if isinstance(data, dict):
            if data["tags"] is None:
                data["tags"] = []
            if data["open_hour"] is None:
                data["open_hour"] = []
            if data["service"] is None:
                data["service"] = []
            if data["photos"] is None:
                data["photos"] = []
        return data
