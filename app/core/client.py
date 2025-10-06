"""HTTP client wrapper for Taiga API."""

from typing import Any, Optional

import httpx

from app.config import settings
from app.core.auth import auth_manager
from app.core.exceptions import ResourceNotFoundError, TaigaAPIError


class TaigaClient:
    """Async HTTP client for Taiga API with authentication."""

    def __init__(self) -> None:
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "TaigaClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized with auth headers."""
        if self._client is None:
            token = await auth_manager.get_token()
            self._client = httpx.AsyncClient(
                base_url=settings.taiga_api_url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        """
        Make GET request to Taiga API.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            TaigaAPIError: If request fails
        """
        await self._ensure_client()
        assert self._client is not None

        try:
            response = await self._client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_error(e, path)
        except httpx.RequestError as e:
            raise TaigaAPIError(f"Request failed: {e}") from e

    async def post(self, path: str, data: dict[str, Any]) -> Any:
        """
        Make POST request to Taiga API.

        Args:
            path: API endpoint path
            data: JSON request body

        Returns:
            JSON response data

        Raises:
            TaigaAPIError: If request fails
        """
        await self._ensure_client()
        assert self._client is not None

        try:
            response = await self._client.post(path, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_error(e, path)
        except httpx.RequestError as e:
            raise TaigaAPIError(f"Request failed: {e}") from e

    async def patch(self, path: str, data: dict[str, Any]) -> Any:
        """
        Make PATCH request to Taiga API.

        Args:
            path: API endpoint path
            data: JSON request body

        Returns:
            JSON response data

        Raises:
            TaigaAPIError: If request fails
        """
        await self._ensure_client()
        assert self._client is not None

        try:
            response = await self._client.patch(path, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_error(e, path)
        except httpx.RequestError as e:
            raise TaigaAPIError(f"Request failed: {e}") from e

    async def delete(self, path: str) -> None:
        """
        Make DELETE request to Taiga API.

        Args:
            path: API endpoint path

        Raises:
            TaigaAPIError: If request fails
        """
        await self._ensure_client()
        assert self._client is not None

        try:
            response = await self._client.delete(path)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_error(e, path)
        except httpx.RequestError as e:
            raise TaigaAPIError(f"Request failed: {e}") from e

    def _handle_error(self, error: httpx.HTTPStatusError, path: str) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        status_code = error.response.status_code

        if status_code == 404:
            # Try to extract resource type from path
            resource_type = path.split("/")[1] if "/" in path else "Resource"
            raise ResourceNotFoundError(resource_type, path)

        if status_code == 401:
            # Clear invalid token and raise error
            auth_manager.clear_token()
            raise TaigaAPIError("Authentication failed. Token may be invalid.", status_code)

        if status_code == 403:
            raise TaigaAPIError("Permission denied. You don't have access to this resource.", status_code)

        # Try to get error message from response
        try:
            error_data = error.response.json()
            error_message = error_data.get("_error_message", str(error))
        except Exception:
            error_message = str(error)

        raise TaigaAPIError(f"API request failed: {error_message}", status_code)


async def get_client() -> TaigaClient:
    """Factory function to create a new Taiga client."""
    return TaigaClient()
