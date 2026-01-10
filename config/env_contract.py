"""
Environment Contract

Phase 0 Utility: Defines environment variable contract (no .env guessing).

WHAT (Utility): I provide environment variable validation and defaults
HOW (Implementation): I use Pydantic for validation
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, validator


class EnvContract(BaseModel):
    """
    Environment variable contract.
    
    Defines all required and optional environment variables with validation.
    """
    
    # Infrastructure
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    ARANGO_URL: str = Field(
        default="http://localhost:8529",
        description="ArangoDB connection URL"
    )
    ARANGO_ROOT_PASSWORD: str = Field(
        default="changeme",
        description="ArangoDB root password"
    )
    
    # Service Ports
    RUNTIME_PORT: int = Field(
        default=8000,
        description="Runtime service port"
    )
    SMART_CITY_PORT: int = Field(
        default=8001,
        description="Smart City service port"
    )
    REALMS_PORT: int = Field(
        default=8002,
        description="Realms service port"
    )
    
    # Redis Port (for docker-compose)
    REDIS_PORT: int = Field(
        default=6379,
        description="Redis port (for docker-compose)"
    )
    
    # Arango Port (for docker-compose)
    ARANGO_PORT: int = Field(
        default=8529,
        description="ArangoDB port (for docker-compose)"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @validator("RUNTIME_PORT", "SMART_CITY_PORT", "REALMS_PORT", "REDIS_PORT", "ARANGO_PORT")
    def validate_port(cls, v):
        """Validate port number."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_env_contract() -> EnvContract:
    """
    Get environment contract from environment variables.
    
    Returns:
        EnvContract instance with validated environment variables
    """
    return EnvContract()


def get_env_value(key: str, default: Optional[str] = None) -> str:
    """
    Get environment variable value.
    
    Args:
        key: Environment variable key
        default: Default value if not set
    
    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default) if default else os.getenv(key)
