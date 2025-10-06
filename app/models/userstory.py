"""User story models."""

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.project import ProjectExtraInfo
from app.models.status import StatusExtraInfo
from app.models.user import UserExtraInfo


class UserStoryExtraInfo(BaseModel):
    """User story information embedded in other responses."""

    id: int
    ref: int
    subject: str


class UserStory(BaseModel):
    """Taiga user story model."""

    id: int
    ref: int
    version: int
    subject: str
    description: Optional[str] = None
    project: int
    status: int
    status_extra_info: Optional[StatusExtraInfo] = None
    assigned_to: Optional[int] = None
    assigned_to_extra_info: Optional[UserExtraInfo] = None
    owner: int
    owner_extra_info: Optional[UserExtraInfo] = None
    created_date: datetime
    modified_date: datetime
    finish_date: Optional[datetime] = None
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)
    is_closed: bool = False
    is_blocked: bool = False
    points: Optional[Any] = None  # Can be dict or string
    total_points: Optional[float] = None
    project_extra_info: Optional[ProjectExtraInfo] = None
    milestone: Optional[int] = None
    watchers: list[int] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v: Any) -> list[str]:
        """
        Normalize tags from Taiga API format.

        Taiga returns tags as: [['tag_name', None], ...] or ['tag_name', ...]
        We normalize to: ['tag_name', ...]
        """
        if not v:
            return []

        result = []
        for tag in v:
            if isinstance(tag, list) and len(tag) > 0:
                # Nested format: ['tag_name', None]
                result.append(str(tag[0]))
            elif isinstance(tag, str):
                # Simple format: 'tag_name'
                result.append(tag)

        return result

    class Config:
        populate_by_name = True


class CreateUserStoryRequest(BaseModel):
    """Request model for creating a user story."""

    project: int
    subject: str
    description: Optional[str] = None
    status: Optional[int] = None
    tags: Optional[list[str]] = None


class UpdateUserStoryRequest(BaseModel):
    """Request model for updating a user story."""

    version: int
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None
    assigned_to: Optional[int] = None
    tags: Optional[list[str]] = None
    points: Optional[Any] = None  # Can be string, float, or dict for role-based points
    due_date: Optional[str] = None  # YYYY-MM-DD format
