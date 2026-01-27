"""
Service Configuration Helper

Supports both local (Docker) and external (Option C) service configurations.
Loads .env.secrets for sensitive data (LLM keys, GCS, Supabase, etc.).

Usage:
    from symphainy_platform.config.service_config import get_service_url
    
    redis_url = get_service_url("REDIS_URL", "redis://redis:6379")
    arango_url = get_service_url("ARANGO_URL", "http://arango:8529")
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


def _load_env_secrets() -> None:
    """Load .env.secrets file if it exists."""
    project_root = Path(__file__).resolve().parents[3]
    
    # Try multiple possible paths for .env.secrets
    possible_paths = [
        project_root / "symphainy_platform" / ".env.secrets",  # Expected location
        project_root / ".env.secrets",  # Project root
        project_root.parent / ".env.secrets",  # Parent directory
        Path.cwd() / ".env.secrets",  # Current working directory
    ]
    
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path, override=False)  # Don't override existing env vars
            break


# Load .env.secrets at module import
_load_env_secrets()


def get_service_url(env_var: str, default: str) -> str:
    """
    Get service URL from environment variable with fallback to default.
    
    Supports both local (Docker) and external (Option C) configurations:
    - Local: redis://redis:6379, http://arango:8529
    - External: redis://upstash.io:6379, https://arango.oasis.cloud
    
    Args:
        env_var: Environment variable name (e.g., "REDIS_URL")
        default: Default value if env var not set (typically local Docker service)
    
    Returns:
        Service URL from environment or default
    """
    return os.getenv(env_var, default)


def get_redis_url() -> str:
    """Get Redis URL (local or external)."""
    return get_service_url("REDIS_URL", "redis://redis:6379")


def get_arango_url() -> str:
    """Get ArangoDB URL (local or external)."""
    return get_service_url("ARANGO_URL", "http://arango:8529")


def get_meilisearch_url() -> str:
    """Get Meilisearch URL (local or external)."""
    return get_service_url("MEILISEARCH_URL", "http://meilisearch:7700")


def get_consul_host() -> str:
    """Get Consul host (local or external)."""
    return get_service_url("CONSUL_HOST", "consul")


def get_consul_port() -> int:
    """Get Consul port."""
    return int(os.getenv("CONSUL_PORT", "8500"))


def get_runtime_url() -> str:
    """Get Runtime API URL (local or external)."""
    return get_service_url("RUNTIME_URL", "http://runtime:8000")


def is_local_mode() -> bool:
    """
    Check if running in local (Docker) mode vs external (Option C) mode.
    
    Returns True if using local Docker service names, False if using external URLs.
    """
    redis_url = get_redis_url()
    arango_url = get_arango_url()
    
    # If URLs contain docker service names, assume local mode
    local_indicators = ["redis:", "arango:", "meilisearch:", "consul"]
    return any(indicator in redis_url or indicator in arango_url 
              for indicator in local_indicators)
