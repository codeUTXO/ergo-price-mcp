"""
Configuration management for Ergo Price MCP Server.

This module handles loading and validation of configuration from environment variables
using Pydantic Settings. All configuration is centralized here.
"""

import os
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class CruxAPIConfig(BaseSettings):
    """Configuration for CRUX Finance API."""
    
    base_url: str = Field(
        default="https://api.cruxfinance.io",
        description="Base URL for CRUX Finance API"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for CRUX Finance API (if required)"
    )
    timeout: float = Field(
        default=30.0,
        description="API request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for failed API requests"
    )
    retry_delay: float = Field(
        default=1.0,
        description="Retry delay in seconds (exponential backoff base)"
    )

    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v

    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Max retries must be non-negative")
        return v

    class Config:
        env_prefix = "CRUX_API_"


class CacheConfig(BaseSettings):
    """Configuration for caching system."""
    
    ttl_price: int = Field(
        default=30,
        description="Cache TTL for price data in seconds"
    )
    ttl_metadata: int = Field(
        default=300,
        description="Cache TTL for asset metadata in seconds"
    )
    ttl_history: int = Field(
        default=3600,
        description="Cache TTL for historical data in seconds"
    )
    ttl_static: int = Field(
        default=86400,
        description="Cache TTL for static data in seconds"
    )
    max_size: int = Field(
        default=1000,
        description="Maximum cache size (number of entries)"
    )

    @field_validator('ttl_price', 'ttl_metadata', 'ttl_history', 'ttl_static')
    @classmethod
    def validate_ttl(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("TTL must be positive")
        return v

    @field_validator('max_size')
    @classmethod
    def validate_max_size(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Max size must be positive")
        return v

    class Config:
        env_prefix = "CACHE_"


class MCPServerConfig(BaseSettings):
    """Configuration for MCP server."""
    
    name: str = Field(
        default="ergo-price-mcp",
        description="MCP server name"
    )
    version: str = Field(
        default="1.0.0",
        description="MCP server version"
    )
    description: str = Field(
        default="MCP server for Ergo blockchain pricing data via CRUX Finance API",
        description="MCP server description"
    )

    class Config:
        env_prefix = "MCP_SERVER_"


class LoggingConfig(BaseSettings):
    """Configuration for logging system."""
    
    level: str = Field(
        default="INFO",
        description="Log level"
    )
    format: str = Field(
        default="json",
        description="Log format: json or text"
    )
    requests: bool = Field(
        default=True,
        description="Enable/disable request/response logging"
    )
    file: Optional[str] = Field(
        default=None,
        description="Log file path (optional, logs to console if not set)"
    )

    @field_validator('level')
    @classmethod
    def validate_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @field_validator('format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        valid_formats = {"json", "text"}
        if v.lower() not in valid_formats:
            raise ValueError(f"Log format must be one of {valid_formats}")
        return v.lower()

    class Config:
        env_prefix = "LOG_"


class RateLimitConfig(BaseSettings):
    """Configuration for rate limiting."""
    
    enabled: bool = Field(
        default=True,
        description="Enable rate limiting for CRUX API calls"
    )
    rpm: int = Field(
        default=100,
        description="Requests per minute limit for CRUX API"
    )
    burst: int = Field(
        default=10,
        description="Rate limit burst size"
    )

    @field_validator('rpm', 'burst')
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Rate limit values must be positive")
        return v

    class Config:
        env_prefix = "RATE_LIMIT_"


class DevelopmentConfig(BaseSettings):
    """Configuration for development and testing."""
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    dev_mode: bool = Field(
        default=False,
        description="Enable development mode features"
    )
    mock_crux_api: bool = Field(
        default=False,
        description="Mock CRUX API responses (for testing)"
    )
    test_data_dir: str = Field(
        default="tests/fixtures",
        description="Test data directory"
    )

    class Config:
        env_prefix = ""


class Settings(BaseSettings):
    """Main settings class that combines all configuration sections."""
    
    # Configuration sections as fields
    crux_api: CruxAPIConfig = Field(default_factory=CruxAPIConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    mcp_server: MCPServerConfig = Field(default_factory=MCPServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields


# Global settings instance - initialize lazily
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment variables."""
    global _settings
    _settings = Settings()
    return _settings


# Convenience functions for commonly used config values
def get_crux_api_base_url() -> str:
    """Get CRUX API base URL."""
    return get_settings().crux_api.base_url


def get_crux_api_timeout() -> float:
    """Get CRUX API timeout."""
    return get_settings().crux_api.timeout


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return get_settings().development.debug


def is_dev_mode() -> bool:
    """Check if development mode is enabled."""
    return get_settings().development.dev_mode


def should_mock_crux_api() -> bool:
    """Check if CRUX API should be mocked."""
    return get_settings().development.mock_crux_api 