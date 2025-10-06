"""Authentication manager for Taiga API."""

import logging
import time
from typing import Optional

import httpx

from app.config import settings
from app.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages authentication tokens for Taiga API."""

    def __init__(self) -> None:
        self._token: Optional[str] = None
        self._token_expiration: float = 0

    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with a valid token."""
        return self._token is not None and time.time() < self._token_expiration

    async def authenticate(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> str:
        """
        Authenticate with Taiga API and obtain auth token.

        Args:
            username: Taiga username (falls back to settings)
            password: Taiga password (falls back to settings)

        Returns:
            Authentication token

        Raises:
            AuthenticationError: If authentication fails
        """
        user = username or settings.taiga_username
        pwd = password or settings.taiga_password

        if not user or not pwd:
            raise AuthenticationError(
                "Username and password are required. "
                "Please provide them or set TAIGA_USERNAME and TAIGA_PASSWORD environment variables."
            )

        try:
            logger.info(f"Authenticating user: {user}")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.taiga_api_url}/auth",
                    json={
                        "type": "normal",
                        "username": user,
                        "password": pwd,
                    },
                )
                response.raise_for_status()
                data = response.json()

                self._token = data["auth_token"]
                self._token_expiration = time.time() + settings.token_expiration

                logger.info("Authentication successful")
                return self._token

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during authentication: {e.response.status_code}")
            if e.response.status_code == 400:
                raise AuthenticationError(
                    "Invalid credentials. Please check your username and password."
                ) from e
            raise AuthenticationError(f"Authentication failed: {e}") from e
        except httpx.RequestError as e:
            raise AuthenticationError(f"Failed to connect to Taiga API: {e}") from e
        except KeyError as e:
            raise AuthenticationError(
                f"Unexpected response format from Taiga API: missing {e}"
            ) from e

    async def get_token(self) -> str:
        """
        Get current auth token, refreshing if necessary.

        Returns:
            Valid authentication token

        Raises:
            AuthenticationError: If authentication fails
        """
        if not self.is_authenticated:
            await self.authenticate()

        assert self._token is not None  # For type checker
        return self._token

    def clear_token(self) -> None:
        """Clear stored authentication token."""
        self._token = None
        self._token_expiration = 0


# Global auth manager instance
auth_manager = AuthManager()
