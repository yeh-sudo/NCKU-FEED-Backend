from pydantic import BaseModel, Field

class Rating(BaseModel):
    cleanliness: int = Field(...)
    service: int = Field(...)
    deliciousness: int = Field(...)
    CPR: int = Field(...)
    overall: int = Field(...)
class Comment(BaseModel):
    rating: Rating
    content: str = Field(...)