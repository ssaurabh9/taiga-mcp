"""Epic models."""

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.project import ProjectExtraInfo
from app.models.status import StatusExtraInfo
from app.models.user import UserExtraInfo


class EpicExtraInfo(BaseModel):
    """Epic information embedded in other responses."""

    id: int
    ref: int
    subject: str


class Epic(BaseModel):
    """Taiga epic model."""

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
    project_extra_info: Optional[ProjectExtraInfo] = None
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


class CreateEpicRequest(BaseModel):
    """Request model for creating an epic."""

    project: int
    subject: str
    description: Optional[str] = None
    status: Optional[int] = None
    tags: Optional[list[str]] = None
