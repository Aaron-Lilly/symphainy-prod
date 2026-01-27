"""
Configuration Helper

Provides helper functions to read configuration with fallback patterns,
matching the original ConfigAdapter behavior.

WHAT: I provide configuration reading with fallback patterns
HOW: I read from environment variables with multiple name support
"""

import os
from typing import Optional
from pathlib import Path


def _find_env_secrets() -> Optional[Path]:
    """Find .env.secrets file in common locations."""
    from pathlib import Path
    
    # Priority order: current project first, then fallback to original project
    possible_paths = [
        # Current project (highest priority)
        Path(__file__).parent.parent / "symphainy_platform" / ".env.secrets",
        Path("symphainy_platform/.env.secrets"),
        Path("symphainy-platform/.env.secrets"),
        Path(".env.secrets"),
        # Original project (fallback)
        Path("../symphainy_source/symphainy-platform/.env.secrets"),
        Path("../symphainy_source/.env.secrets"),
        Path(__file__).parent.parent.parent / "symphainy_source" / "symphainy-platform" / ".env.secrets"
    ]
    
    for path in possible_paths:
        full_path = path.resolve()
        if full_path.exists():
            return full_path
    
    return None


def load_env_file(file_path: str) -> dict:
    """
    Load environment variables from .env file.
    
    Args:
        file_path: Path to .env file
    
    Returns:
        Dict of key-value pairs
    """
    env_vars = {}
    if not os.path.exists(file_path):
        return env_vars
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    env_vars[key.strip()] = value
    except Exception:
        pass
    
    return env_vars


def get_supabase_url() -> Optional[str]:
    """
    Get Supabase URL with fallback to .env.secrets file.
    
    Returns:
        Supabase URL or None
    """
    # Try environment variable first
    url = os.getenv("SUPABASE_URL")
    if url:
        return url
    
    # Try loading from .env.secrets
    env_secrets = _find_env_secrets()
    if env_secrets:
        env_vars = load_env_file(str(env_secrets))
        return env_vars.get("SUPABASE_URL")
    
    return None


def get_supabase_anon_key() -> Optional[str]:
    """
    Get Supabase anon key (uses SUPABASE_PUBLISHABLE_KEY).
    
    Uses SUPABASE_PUBLISHABLE_KEY (Supabase new naming convention).
    Legacy names (SUPABASE_ANON_KEY, SUPABASE_KEY) are deprecated and no longer supported.
    
    Returns:
        Supabase anon key or None
    """
    # Try environment variables (new Supabase naming only)
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    if key:
        return key
    
    # Try loading from .env.secrets
    env_secrets = _find_env_secrets()
    if env_secrets:
        env_vars = load_env_file(str(env_secrets))
        return (
            env_vars.get("SUPABASE_PUBLISHABLE_KEY")
        )
    
    return None


def get_supabase_service_key() -> Optional[str]:
    """
    Get Supabase service key (uses SUPABASE_SECRET_KEY).
    
    Uses SUPABASE_SECRET_KEY (Supabase new naming convention).
    Legacy names (SUPABASE_SERVICE_KEY, SUPABASE_KEY) are deprecated and no longer supported.
    
    Returns:
        Supabase service key or None
    """
    # Try environment variables (new Supabase naming only)
    key = os.getenv("SUPABASE_SECRET_KEY")
    if key:
        return key
    
    # Try loading from .env.secrets
    env_secrets = _find_env_secrets()
    if env_secrets:
        env_vars = load_env_file(str(env_secrets))
        return (
            env_vars.get("SUPABASE_SECRET_KEY")
        )
    
    return None


def get_gcs_project_id() -> Optional[str]:
    """Get GCS project ID."""
    project_id = os.getenv("GCS_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    if project_id:
        return project_id
    
    # Try loading from .env.secrets
    env_secrets = _find_env_secrets()
    if env_secrets:
        env_vars = load_env_file(str(env_secrets))
        return env_vars.get("GCS_PROJECT_ID") or env_vars.get("GOOGLE_CLOUD_PROJECT")
    
    return None


def get_gcs_bucket_name() -> Optional[str]:
    """Get GCS bucket name."""
    bucket_name = os.getenv("GCS_BUCKET_NAME") or os.getenv("GCS_BUCKET")
    if bucket_name:
        return bucket_name
    
    # Try loading from .env.secrets
    env_secrets = _find_env_secrets()
    if env_secrets:
        env_vars = load_env_file(str(env_secrets))
        return env_vars.get("GCS_BUCKET_NAME") or env_vars.get("GCS_BUCKET")
    
    return None


def get_gcs_credentials_json() -> Optional[str]:
    """Get GCS credentials JSON string."""
    creds = os.getenv("GCS_CREDENTIALS_JSON")
    if creds:
        return creds
    
    # Try loading from .env.secrets
    env_secrets = _find_env_secrets()
    if env_secrets:
        env_vars = load_env_file(str(env_secrets))
        return env_vars.get("GCS_CREDENTIALS_JSON")
    
    return None


def get_openai_api_key() -> Optional[str]:
    """
    Get OpenAI API key with fallback to .env.secrets file.
    
    Supports both LLM_OPENAI_API_KEY and OPENAI_API_KEY.
    
    Returns:
        OpenAI API key or None
    """
    # Try environment variables (both naming conventions)
    key = os.getenv("LLM_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if key:
        return key
    
    # Try loading from .env.secrets
    env_secrets = _find_env_secrets()
    if env_secrets:
        env_vars = load_env_file(str(env_secrets))
        return env_vars.get("LLM_OPENAI_API_KEY") or env_vars.get("OPENAI_API_KEY")
    
    return None


def get_huggingface_endpoint_url() -> Optional[str]:
    """
    Get HuggingFace embeddings endpoint URL with fallback to .env.secrets file.
    
    Returns:
        HuggingFace endpoint URL or None
    """
    # Try environment variable
    url = os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
    if url:
        return url
    
    # Try loading from .env.secrets
    env_secrets = _find_env_secrets()
    if env_secrets:
        env_vars = load_env_file(str(env_secrets))
        return env_vars.get("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
    
    return None


def get_huggingface_api_key() -> Optional[str]:
    """
    Get HuggingFace API key with fallback to .env.secrets file.
    
    Supports both HUGGINGFACE_EMBEDDINGS_API_KEY and HUGGINGFACE_API_KEY.
    
    Returns:
        HuggingFace API key or None
    """
    # Try environment variables (both naming conventions)
    key = os.getenv("HUGGINGFACE_EMBEDDINGS_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
    if key:
        return key
    
    # Try loading from .env.secrets
    env_secrets = _find_env_secrets()
    if env_secrets:
        env_vars = load_env_file(str(env_secrets))
        return env_vars.get("HUGGINGFACE_EMBEDDINGS_API_KEY") or env_vars.get("HUGGINGFACE_API_KEY")
    
    return None
