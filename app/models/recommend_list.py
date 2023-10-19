"""Provide recommend list model for database."""

from typing import List
from pydantic import BaseModel
from .restaurant import Restaurant

class RecommendList(BaseModel):
    """Recommend list model. 100 restaurants for one page.
    """

    uid: str
    page: int
    recommendation: List[Restaurant]
