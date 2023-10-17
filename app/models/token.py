"""Provide data model for database and other services."""

from pydantic import BaseModel

class Token(BaseModel):
    """Model that will be used in the token endpoint for the response.
    """

    access_token: str
    token_type: str
