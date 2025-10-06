"""Project service for Taiga API operations."""

from typing import Optional

from app.core.client import TaigaClient
from app.models.project import Project, ProjectMember


class ProjectService:
    """Service for managing Taiga projects."""

    def __init__(self, client: TaigaClient) -> None:
        self.client = client

    async def list_projects(self, member_id: Optional[int] = None) -> list[Project]:
        """
        List all projects accessible to the user.

        Args:
            member_id: Filter by member ID (optional)

        Returns:
            List of projects
        """
        params = {}
        if member_id:
            params["member"] = member_id

        data = await self.client.get("/projects", params=params)
        return [Project(**project) for project in data]

    async def get_project(self, project_id: int) -> Project:
        """
        Get project details by ID.

        Args:
            project_id: Project ID

        Returns:
            Project details
        """
        data = await self.client.get(f"/projects/{project_id}")
        return Project(**data)

    async def get_project_by_slug(self, slug: str) -> Project:
        """
        Get project details by slug.

        Args:
            slug: Project slug

        Returns:
            Project details
        """
        data = await self.client.get(f"/projects/by_slug", params={"slug": slug})
        return Project(**data)

    async def list_project_members(self, project_id: int) -> list[ProjectMember]:
        """
        List all members of a project.

        Args:
            project_id: Project ID

        Returns:
            List of project members
        """
        data = await self.client.get("/memberships", params={"project": project_id})
        return [ProjectMember(**member) for member in data]
