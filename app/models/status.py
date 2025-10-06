"""Status models for user stories and tasks."""

from pydantic import BaseModel


class StatusExtraInfo(BaseModel):
    """Status information embedded in other responses."""

    name: str
    color: str
    is_closed: bool = False


class UserStoryStatus(BaseModel):
    """User story status model."""

    id: int
    name: str
    slug: str
    order: int
    is_closed: bool
    color: str
    project: int


class TaskStatus(BaseModel):
    """Task status model."""

    id: int
    name: str
    slug: str
    order: int
    is_closed: bool
    color: str
    project: int
