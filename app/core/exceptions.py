"""Custom exceptions for Taiga MCP server."""


class TaigaMCPError(Exception):
    """Base exception for all Taiga MCP errors."""

    pass


class AuthenticationError(TaigaMCPError):
    """Raised when authentication with Taiga API fails."""

    pass


class TaigaAPIError(TaigaMCPError):
    """Raised when a Taiga API request fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ResourceNotFoundError(TaigaAPIError):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, identifier: str) -> None:
        super().__init__(f"{resource_type} with identifier '{identifier}' not found", 404)
        self.resource_type = resource_type
        self.identifier = identifier


class ValidationError(TaigaMCPError):
    """Raised when input validation fails."""

    pass


class ConfigurationError(TaigaMCPError):
    """Raised when configuration is invalid or missing."""

    pass
