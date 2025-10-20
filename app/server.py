"""MCP server for Taiga project management."""

import asyncio
import logging
import sys
from typing import Any, Optional

from fastmcp import FastMCP

from app.config import settings
from app.core.auth import auth_manager
from app.core.client import TaigaClient
from app.core.exceptions import TaigaMCPError
from app.models.epic import CreateEpicRequest
from app.models.task import CreateTaskRequest
from app.models.userstory import CreateUserStoryRequest, UpdateUserStoryRequest
from app.services.epic_service import EpicService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.services.userstory_service import UserStoryService

# Configure logging to stderr (stdout is used for MCP protocol)
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr, not stdout
)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("taiga-mcp")


@mcp.resource("taiga://docs/api")
def get_api_docs() -> str:
    """Get API documentation for Taiga MCP server capabilities."""
    return f"""Taiga MCP Server - API Documentation

This MCP server allows you to interact with Taiga project management platform using natural language.

**Available Tools:**

1. authenticate - Authenticate with Taiga
2. listProjects - List all your Taiga projects
3. getProject - Get detailed information about a specific project
4. listProjectMembers - Get all members of a project
5. createEpic - Create a new epic in a project
6. listEpics - List epics in a project (with pagination)
7. createUserStory - Create a new user story in a project
8. listUserStories - List user stories in a project (with pagination)
9. getUserStory - Get detailed information about a specific user story
10. updateUserStory - Update an existing user story
11. listUserStoryTasks - Get all tasks for a user story
12. createTask - Create a new task within a user story

**Configuration:**

- API URL: {settings.taiga_api_url}
- Authentication: Token-based (auto-refreshed)

**Getting Started:**

1. Authenticate using your Taiga credentials
2. List your projects to get project IDs or slugs
3. Create and manage user stories and tasks

For detailed usage, refer to individual tool descriptions.
"""


@mcp.tool()
async def authenticate(
    username: Optional[str] = None,
    password: Optional[str] = None
) -> str:
    """Authenticate with Taiga API. Uses credentials from environment variables if not provided."""
    await auth_manager.authenticate(username, password)
    async with TaigaClient() as client:
        user_service = UserService(client)
        current_user = await user_service.get_current_user()
    return f"Successfully authenticated as {current_user.full_name} ({current_user.username})."


@mcp.tool()
async def listProjects() -> str:
    """List all projects accessible to the authenticated user."""
    async with TaigaClient() as client:
        project_service = ProjectService(client)
        user_service = UserService(client)
        # Get current user for filtering
        current_user = await user_service.get_current_user()
        projects = await project_service.list_projects(member_id=current_user.id)
    project_list = "\n".join(
        [f"- {p.name} (ID: {p.id}, Slug: {p.slug})" for p in projects]
    )
    return f"Your Taiga Projects:\n\n{project_list}"


@mcp.tool()
async def getProject(projectIdentifier: str) -> str:
    """Get detailed information about a specific project."""
    async with TaigaClient() as client:
        project_service = ProjectService(client)
        project_id, _ = await resolve_project_id(project_service, projectIdentifier)
        project = await project_service.get_project(project_id)
    return f"""Project Details:

Name: {project.name}
ID: {project.id}
Slug: {project.slug}
Description: {project.description or 'No description'}
Created: {project.created_date.strftime('%Y-%m-%d %H:%M:%S')}
Total Members: {project.total_memberships}
Private: {project.is_private}
"""


@mcp.tool()
async def listProjectMembers(projectIdentifier: str) -> str:
    """List all members of a project."""
    async with TaigaClient() as client:
        project_service = ProjectService(client)
        project_id, _ = await resolve_project_id(project_service, projectIdentifier)
        members = await project_service.list_project_members(project_id)
    member_list = "\n".join(
        [
            f"- {m.full_name or (m.user_extra_info.get('full_name') if m.user_extra_info else 'Unknown')} "
            f"(@{m.username or (m.user_extra_info.get('username') if m.user_extra_info else 'unknown')}) - {m.role_name}"
            for m in members
        ]
    )
    return f"Project Members:\n\n{member_list}"


@mcp.tool()
async def createUserStory(
    projectIdentifier: str,
    subject: str,
    description: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[list[str]] = None
) -> str:
    """Create a new user story in a project."""
    async with TaigaClient() as client:
        project_service = ProjectService(client)
        userstory_service = UserStoryService(client)
        project_id, project_name = await resolve_project_id(project_service, projectIdentifier)

        # Resolve status if provided
        status_id = None
        if status:
            statuses = await userstory_service.get_user_story_statuses(project_id)
            for s in statuses:
                if s.name.lower() == status.lower():
                    status_id = s.id
                    break

        request = CreateUserStoryRequest(
            project=project_id,
            subject=subject,
            description=description,
            status=status_id,
            tags=tags,
        )
        story = await userstory_service.create_user_story(request)
    return f"""User story created successfully!

Subject: {story.subject}
Reference: #{story.ref}
Status: {story.status_extra_info.name if story.status_extra_info else 'Default status'}
Project: {project_name}
"""


@mcp.tool()
async def listUserStories(
    projectIdentifier: str,
    pageSize: int = 100,
    page: Optional[int] = None,
    fetchAll: bool = True
) -> str:
    """List user stories in a project with pagination support."""
    async with TaigaClient() as client:
        project_service = ProjectService(client)
        userstory_service = UserStoryService(client)
        project_id, _ = await resolve_project_id(project_service, projectIdentifier)
        stories = await userstory_service.list_user_stories(
            project_id, page_size=pageSize, page=page, fetch_all=fetchAll
        )

    if not stories:
        return "No user stories found in this project."

    pagination_info = (
        f" (Page {page})"
        if page
        else f" (All {len(stories)} stories)" if fetchAll else ""
    )
    story_list = "\n".join(
        [
            f"- #{s.ref}: {s.subject} (Status: {s.status_extra_info.name if s.status_extra_info else 'Unknown'})"
            for s in stories
        ]
    )
    return f"User Stories in Project{pagination_info}:\n\n{story_list}"


@mcp.tool()
async def getUserStory(
    userStoryIdentifier: str,
    projectIdentifier: Optional[str] = None
) -> str:
    """Get detailed information about a specific user story."""
    async with TaigaClient() as client:
        userstory_service = UserStoryService(client)
        project_service = ProjectService(client)
        user_story_id = await resolve_user_story_id(
            userstory_service, project_service, userStoryIdentifier, projectIdentifier
        )
        story = await userstory_service.get_user_story(user_story_id)

    points_display = "None"
    if story.points:
        if isinstance(story.points, dict):
            points_display = story.points.get("name", "None")
        else:
            points_display = str(story.points)

    return f"""User Story Details:

Subject: {story.subject}
Reference: #{story.ref}
Description: {story.description or 'No description'}
Status: {story.status_extra_info.name if story.status_extra_info else 'Unknown'}
Assigned to: {story.assigned_to_extra_info.full_name if story.assigned_to_extra_info else 'Unassigned'}
Points: {points_display}
Tags: {', '.join(story.tags) if story.tags else 'None'}
Due Date: {story.due_date or 'Not set'}
Created: {story.created_date.strftime('%Y-%m-%d %H:%M:%S')}
Modified: {story.modified_date.strftime('%Y-%m-%d %H:%M:%S')}
Project: {story.project_extra_info.name if story.project_extra_info else 'N/A'}
"""


@mcp.tool()
async def updateUserStory(
    userStoryIdentifier: str,
    projectIdentifier: Optional[str] = None,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    assignedTo: Optional[str] = None,
    tags: Optional[list[str]] = None,
    points: Optional[str] = None,
    dueDate: Optional[str] = None
) -> str:
    """Update an existing user story."""
    async with TaigaClient() as client:
        userstory_service = UserStoryService(client)
        project_service = ProjectService(client)
        user_story_id = await resolve_user_story_id(
            userstory_service, project_service, userStoryIdentifier, projectIdentifier
        )

        # Get current story for version and project ID
        current_story = await userstory_service.get_user_story(user_story_id)
        project_id = current_story.project

        # Build update request
        update_data = {"version": current_story.version}

        if subject:
            update_data["subject"] = subject
        if description:
            update_data["description"] = description
        if tags:
            update_data["tags"] = tags
        if points:
            # Note: Taiga uses role-based story points in some configurations
            # Simple projects: points can be a decimal (e.g., 5.0)
            # Complex projects with roles: points is a dict like {"role_id": value}
            # For now, we'll try to use the existing points structure from the story
            points_value = points

            # If current story has points as dict (role-based), we need to maintain that structure
            if isinstance(current_story.points, dict) and current_story.points:
                # Get the first role from existing points and update its value
                role_keys = list(current_story.points.keys())
                if role_keys:
                    first_role = role_keys[0]
                    try:
                        update_data["points"] = {first_role: float(points_value)}
                    except (ValueError, TypeError):
                        logger.warning(f"Could not convert points value '{points_value}' to float")
            else:
                # Simple decimal points
                try:
                    update_data["points"] = float(points_value) if points_value else None
                except (ValueError, TypeError):
                    update_data["points"] = points_value
        if dueDate:
            update_data["due_date"] = dueDate

        # Resolve status if provided
        if status:
            statuses = await userstory_service.get_user_story_statuses(project_id)
            status_found = False
            for s in statuses:
                if s.name.lower() == status.lower():
                    update_data["status"] = s.id
                    status_found = True
                    break
            if not status_found:
                status_names = ", ".join([s.name for s in statuses])
                raise ValueError(f"Status '{status}' not found. Available statuses: {status_names}")

        # Resolve assigned user if provided
        if assignedTo:
            members = await project_service.list_project_members(project_id)
            member_found = False
            for member in members:
                # Get username and full_name from either direct fields or user_extra_info
                username = member.username or (member.user_extra_info.get("username") if member.user_extra_info else None)
                full_name = member.full_name or (member.user_extra_info.get("full_name") if member.user_extra_info else None)

                if username and username.lower() == assignedTo.lower():
                    update_data["assigned_to"] = member.user
                    member_found = True
                    break
                if full_name and full_name.lower() == assignedTo.lower():
                    update_data["assigned_to"] = member.user
                    member_found = True
                    break

            if not member_found:
                usernames = ", ".join([
                    m.username or (m.user_extra_info.get("username") if m.user_extra_info else "unknown")
                    for m in members
                ])
                raise ValueError(f"User '{assignedTo}' not found in project. Available members: {usernames}")

        logger.debug(f"Update data being sent: {update_data}")
        request = UpdateUserStoryRequest(**update_data)
        story = await userstory_service.update_user_story(user_story_id, request)

    points_display = "None"
    if story.points:
        if isinstance(story.points, dict):
            points_display = story.points.get("name", "None")
        else:
            points_display = str(story.points)

    return f"""User story updated successfully!

Subject: {story.subject}
Reference: #{story.ref}
Status: {story.status_extra_info.name if story.status_extra_info else 'Unknown'}
Assigned to: {story.assigned_to_extra_info.full_name if story.assigned_to_extra_info else 'Unassigned'}
Points: {points_display}
Project: {story.project_extra_info.name if story.project_extra_info else 'N/A'}
"""


@mcp.tool()
async def listUserStoryTasks(
    userStoryIdentifier: str,
    projectIdentifier: Optional[str] = None
) -> str:
    """Get all tasks associated with a user story."""
    async with TaigaClient() as client:
        task_service = TaskService(client)
        userstory_service = UserStoryService(client)
        project_service = ProjectService(client)
        user_story_id = await resolve_user_story_id(
            userstory_service, project_service, userStoryIdentifier, projectIdentifier
        )
        tasks = await task_service.list_tasks(user_story_id)

    if not tasks:
        return "No tasks found for this user story."

    task_list = "\n".join(
        [
            f"- #{t.ref}: {t.subject} (Status: {t.status_extra_info.name if t.status_extra_info else 'Unknown'}, "
            f"Assigned: {t.assigned_to_extra_info.full_name if t.assigned_to_extra_info else 'Unassigned'})"
            for t in tasks
        ]
    )
    return f"Tasks in User Story:\n\n{task_list}"


@mcp.tool()
async def createEpic(
    projectIdentifier: str,
    subject: str,
    description: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[list[str]] = None
) -> str:
    """Create a new epic in a project."""
    async with TaigaClient() as client:
        project_service = ProjectService(client)
        epic_service = EpicService(client)
        project_id, project_name = await resolve_project_id(project_service, projectIdentifier)

        # Resolve status if provided
        status_id = None
        if status:
            statuses = await epic_service.get_epic_statuses(project_id)
            for s in statuses:
                if s.name.lower() == status.lower():
                    status_id = s.id
                    break

        request = CreateEpicRequest(
            project=project_id,
            subject=subject,
            description=description,
            status=status_id,
            tags=tags,
        )
        epic = await epic_service.create_epic(request)
    return f"""Epic created successfully!

Subject: {epic.subject}
Reference: #{epic.ref}
Status: {epic.status_extra_info.name if epic.status_extra_info else 'Default status'}
Project: {project_name}
"""


@mcp.tool()
async def listEpics(
    projectIdentifier: str,
    pageSize: int = 100,
    page: Optional[int] = None,
    fetchAll: bool = True
) -> str:
    """List epics in a project with pagination support."""
    async with TaigaClient() as client:
        project_service = ProjectService(client)
        epic_service = EpicService(client)
        project_id, _ = await resolve_project_id(project_service, projectIdentifier)
        epics = await epic_service.list_epics(
            project_id, page_size=pageSize, page=page, fetch_all=fetchAll
        )

    if not epics:
        return "No epics found in this project."

    pagination_info = (
        f" (Page {page})"
        if page
        else f" (All {len(epics)} epics)" if fetchAll else ""
    )
    epic_list = "\n".join(
        [
            f"- #{e.ref}: {e.subject} (Status: {e.status_extra_info.name if e.status_extra_info else 'Unknown'})"
            for e in epics
        ]
    )
    return f"Epics in Project{pagination_info}:\n\n{epic_list}"


@mcp.tool()
async def createTask(
    projectIdentifier: str,
    userStoryIdentifier: str,
    subject: str,
    description: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[list[str]] = None
) -> str:
    """Create a new task within a user story."""
    async with TaigaClient() as client:
        project_service = ProjectService(client)
        userstory_service = UserStoryService(client)
        task_service = TaskService(client)
        project_id, project_name = await resolve_project_id(project_service, projectIdentifier)
        user_story_id = await resolve_user_story_id(
            userstory_service, project_service, userStoryIdentifier, projectIdentifier
        )

        # Resolve status if provided
        status_id = None
        if status:
            statuses = await task_service.get_task_statuses(project_id)
            for s in statuses:
                if s.name.lower() == status.lower():
                    status_id = s.id
                    break

        request = CreateTaskRequest(
            project=project_id,
            user_story=user_story_id,
            subject=subject,
            description=description,
            status=status_id,
            tags=tags,
        )
        task = await task_service.create_task(request)
    return f"""Task created successfully!

Subject: {task.subject}
Reference: #{task.ref}
Status: {task.status_extra_info.name if task.status_extra_info else 'Default status'}
Project: {project_name}
User Story: #{task.user_story_extra_info.ref if task.user_story_extra_info else 'N/A'} - {task.user_story_extra_info.subject if task.user_story_extra_info else 'N/A'}
"""


async def resolve_project_id(
    project_service: ProjectService, identifier: str
) -> tuple[int, str]:
    """Resolve project identifier to ID and name."""
    if identifier.isdigit():
        project = await project_service.get_project(int(identifier))
    else:
        project = await project_service.get_project_by_slug(identifier)
    return project.id, project.name


async def resolve_user_story_id(
    userstory_service: UserStoryService,
    project_service: ProjectService,
    user_story_identifier: str,
    project_identifier: Optional[str] = None,
) -> int:
    """Resolve user story identifier to ID."""
    if user_story_identifier.startswith("#"):
        if not project_identifier:
            raise ValueError(
                "Project identifier is required when using user story reference number"
            )

        project_id, _ = await resolve_project_id(project_service, project_identifier)
        ref_number = user_story_identifier[1:]

        stories = await userstory_service.list_user_stories(project_id)
        for story in stories:
            if str(story.ref) == ref_number:
                return story.id

        raise ValueError(f"User story with reference {user_story_identifier} not found")

    return int(user_story_identifier)


if __name__ == "__main__":
    mcp.run()
