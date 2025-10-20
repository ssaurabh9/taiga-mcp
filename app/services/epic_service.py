"""Epic service for Taiga API operations."""

from typing import Optional

from app.core.client import TaigaClient
from app.models.epic import CreateEpicRequest, Epic
from app.models.status import EpicStatus


class EpicService:
    """Service for managing Taiga epics."""

    def __init__(self, client: TaigaClient) -> None:
        self.client = client

    async def list_epics(
        self,
        project_id: int,
        page_size: int = 100,
        page: Optional[int] = None,
        fetch_all: bool = True,
    ) -> list[Epic]:
        """
        List epics in a project with pagination support.

        Args:
            project_id: Project ID
            page_size: Number of epics per page (1-100, default: 100)
            page: Specific page number to fetch (optional)
            fetch_all: Whether to fetch all epics across all pages (default: True)

        Returns:
            List of epics
        """
        # Validate page_size
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        # If requesting a specific page without fetch_all
        if page is not None and not fetch_all:
            data = await self.client.get(
                "/epics",
                params={"project": project_id, "page_size": page_size, "page": page},
            )
            return [Epic(**epic) for epic in data]

        # Fetch all epics across all pages
        if fetch_all:
            all_epics: list[Epic] = []
            current_page = 1
            max_pages = 1000  # Safety limit

            while current_page <= max_pages:
                data = await self.client.get(
                    "/epics",
                    params={
                        "project": project_id,
                        "page_size": page_size,
                        "page": current_page,
                    },
                )

                if not data:  # No more data
                    break

                all_epics.extend([Epic(**epic) for epic in data])

                # Check if there are more pages
                # Note: This depends on response headers, we'll break if empty
                if len(data) < page_size:
                    break

                current_page += 1

            return all_epics

        # Default single page request
        data = await self.client.get(
            "/epics",
            params={"project": project_id, "page_size": page_size},
        )
        return [Epic(**epic) for epic in data]

    async def get_epic(self, epic_id: int) -> Epic:
        """
        Get epic details.

        Args:
            epic_id: Epic ID

        Returns:
            Epic details
        """
        data = await self.client.get(f"/epics/{epic_id}")
        return Epic(**data)

    async def create_epic(self, request: CreateEpicRequest) -> Epic:
        """
        Create a new epic.

        Args:
            request: Epic creation request

        Returns:
            Created epic
        """
        data = await self.client.post(
            "/epics",
            request.model_dump(exclude_none=True),
        )
        return Epic(**data)

    async def get_epic_statuses(self, project_id: int) -> list[EpicStatus]:
        """
        Get available statuses for epics in a project.

        Args:
            project_id: Project ID

        Returns:
            List of epic statuses
        """
        data = await self.client.get("/epic-statuses", params={"project": project_id})
        return [EpicStatus(**status) for status in data]
