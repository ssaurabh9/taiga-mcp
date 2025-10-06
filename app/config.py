"""Configuration management for Taiga MCP server."""

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Taiga API settings
    taiga_api_url: str = Field(
        default="https://api.taiga.io/api/v1",
        description="Taiga API base URL",
    )
    taiga_username: str = Field(
        default="",
        description="Taiga username or email",
    )
    taiga_password: str = Field(
        default="",
        description="Taiga password",
    )

    # Application settings
    debug: bool = Field(
        default=False,
        description="Enable debug logging",
    )

    # Token expiration (in seconds)
    token_expiration: int = Field(
        default=86400,  # 24 hours
        description="Auth token expiration time in seconds",
    )


# Global settings instance
settings = Settings()
