"""User story service for Taiga API operations."""

from typing import Optional

from app.core.client import TaigaClient
from app.models.status import UserStoryStatus
from app.models.userstory import (
    CreateUserStoryRequest,
    UpdateUserStoryRequest,
    UserStory,
)


class UserStoryService:
    """Service for managing Taiga user stories."""

    def __init__(self, client: TaigaClient) -> None:
        self.client = client

    async def list_user_stories(
        self,
        project_id: int,
        page_size: int = 100,
        page: Optional[int] = None,
        fetch_all: bool = True,
    ) -> list[UserStory]:
        """
        List user stories in a project with pagination support.

        Args:
            project_id: Project ID
            page_size: Number of stories per page (1-100, default: 100)
            page: Specific page number to fetch (optional)
            fetch_all: Whether to fetch all stories across all pages (default: True)

        Returns:
            List of user stories
        """
        # Validate page_size
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        # If requesting a specific page without fetch_all
        if page is not None and not fetch_all:
            data = await self.client.get(
                "/userstories",
                params={"project": project_id, "page_size": page_size, "page": page},
            )
            return [UserStory(**story) for story in data]

        # Fetch all stories across all pages
        if fetch_all:
            all_stories: list[UserStory] = []
            current_page = 1
            max_pages = 1000  # Safety limit

            while current_page <= max_pages:
                data = await self.client.get(
                    "/userstories",
                    params={
                        "project": project_id,
                        "page_size": page_size,
                        "page": current_page,
                    },
                )

                if not data:  # No more data
                    break

                all_stories.extend([UserStory(**story) for story in data])

                # Check if there are more pages
                # Note: This depends on response headers, we'll break if empty
                if len(data) < page_size:
                    break

                current_page += 1

            return all_stories

        # Default single page request
        data = await self.client.get(
            "/userstories",
            params={"project": project_id, "page_size": page_size},
        )
        return [UserStory(**story) for story in data]

    async def get_user_story(self, user_story_id: int) -> UserStory:
        """
        Get user story details.

        Args:
            user_story_id: User story ID

        Returns:
            User story details
        """
        data = await self.client.get(f"/userstories/{user_story_id}")
        return UserStory(**data)

    async def create_user_story(self, request: CreateUserStoryRequest) -> UserStory:
        """
        Create a new user story.

        Args:
            request: User story creation request

        Returns:
            Created user story
        """
        data = await self.client.post(
            "/userstories",
            request.model_dump(exclude_none=True),
        )
        return UserStory(**data)

    async def update_user_story(
        self, user_story_id: int, request: UpdateUserStoryRequest
    ) -> UserStory:
        """
        Update an existing user story.

        Args:
            user_story_id: User story ID
            request: User story update request

        Returns:
            Updated user story
        """
        data = await self.client.patch(
            f"/userstories/{user_story_id}",
            request.model_dump(exclude_none=True),
        )
        return UserStory(**data)

    async def get_user_story_statuses(self, project_id: int) -> list[UserStoryStatus]:
        """
        Get available statuses for user stories in a project.

        Args:
            project_id: Project ID

        Returns:
            List of user story statuses
        """
        data = await self.client.get("/userstory-statuses", params={"project": project_id})
        return [UserStoryStatus(**status) for status in data]
