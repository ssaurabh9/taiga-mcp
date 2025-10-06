"""Task service for Taiga API operations."""

from app.core.client import TaigaClient
from app.models.status import TaskStatus
from app.models.task import CreateTaskRequest, Task, UpdateTaskRequest


class TaskService:
    """Service for managing Taiga tasks."""

    def __init__(self, client: TaigaClient) -> None:
        self.client = client

    async def list_tasks(self, user_story_id: int) -> list[Task]:
        """
        List all tasks for a user story.

        Args:
            user_story_id: User story ID

        Returns:
            List of tasks
        """
        data = await self.client.get("/tasks", params={"user_story": user_story_id})
        return [Task(**task) for task in data]

    async def get_task(self, task_id: int) -> Task:
        """
        Get task details.

        Args:
            task_id: Task ID

        Returns:
            Task details
        """
        data = await self.client.get(f"/tasks/{task_id}")
        return Task(**data)

    async def create_task(self, request: CreateTaskRequest) -> Task:
        """
        Create a new task.

        Args:
            request: Task creation request

        Returns:
            Created task
        """
        data = await self.client.post(
            "/tasks",
            request.model_dump(exclude_none=True),
        )
        return Task(**data)

    async def update_task(self, task_id: int, request: UpdateTaskRequest) -> Task:
        """
        Update an existing task.

        Args:
            task_id: Task ID
            request: Task update request

        Returns:
            Updated task
        """
        data = await self.client.patch(
            f"/tasks/{task_id}",
            request.model_dump(exclude_none=True),
        )
        return Task(**data)

    async def get_task_statuses(self, project_id: int) -> list[TaskStatus]:
        """
        Get available statuses for tasks in a project.

        Args:
            project_id: Project ID

        Returns:
            List of task statuses
        """
        data = await self.client.get("/task-statuses", params={"project": project_id})
        return [TaskStatus(**status) for status in data]
