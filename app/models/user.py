"""User models."""

from typing import Optional

from pydantic import BaseModel, Field


class UserExtraInfo(BaseModel):
    """User information embedded in other responses."""

    username: str
    full_name: str = Field(alias="full_name_display")
    photo: Optional[str] = None

    class Config:
        populate_by_name = True


class User(BaseModel):
    """Taiga user model."""

    id: int
    username: str
    full_name: str
    email: str
    photo: Optional[str] = None
    is_active: bool = True
    bio: Optional[str] = None
    lang: Optional[str] = None
    timezone: Optional[str] = None
