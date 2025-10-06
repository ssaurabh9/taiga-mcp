"""User service for Taiga API operations."""

from app.core.client import TaigaClient
from app.models.user import User


class UserService:
    """Service for managing Taiga users."""

    def __init__(self, client: TaigaClient) -> None:
        self.client = client

    async def get_current_user(self) -> User:
        """
        Get current authenticated user's information.

        Returns:
            Current user details
        """
        data = await self.client.get("/users/me")
        return User(**data)
