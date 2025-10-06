"""Project models."""

from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, field_validator


class ProjectExtraInfo(BaseModel):
    """Project information embedded in other responses."""

    id: int
    name: str
    slug: str


class Project(BaseModel):
    """Taiga project model."""

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    created_date: datetime
    modified_date: datetime
    owner: Union[int, dict[str, Any]]  # Can be int or dict with owner info
    is_private: bool = True
    total_memberships: int = Field(default=0)
    total_story_points: Optional[float] = None
    is_backlog_activated: bool = True
    is_kanban_activated: bool = False
    is_wiki_activated: bool = True
    is_issues_activated: bool = True

    @field_validator("owner", mode="before")
    @classmethod
    def extract_owner_id(cls, v: Any) -> int:
        """Extract owner ID from int or dict."""
        if isinstance(v, dict):
            return v.get("id", 0)
        return v

    class Config:
        populate_by_name = True


class ProjectMember(BaseModel):
    """Project membership model."""

    id: int
    user: int
    role: int
    role_name: str
    project: int
    is_admin: bool
    user_extra_info: Optional[dict[str, Any]] = None  # Contains username, full_name, photo
    # Additional fields that may be present in the response
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    color: Optional[str] = None
    photo: Optional[str] = None

    class Config:
        populate_by_name = True
        extra = "allow"  # Allow extra fields from API
