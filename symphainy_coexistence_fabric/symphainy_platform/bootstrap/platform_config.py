"""
Layer 1: Platform config (Gate G2 — Config Acquisition + Config Contract).

Single source of truth: (1) acquire env (load env files in order), (2) build
canonical config from os.environ. No other module should read os.environ for
platform infra after this; they use the config dict.

Aligned with CONFIG_ACQUISITION_SPEC and CONFIG_CONTRACT_SPEC.
"""

import os
from typing import Any, Dict

from symphainy_platform.bootstrap.repo_root import get_repo_root


def acquire_env() -> None:
    """
    Load env files in order from repo root (first step of Φ2 when process loads).
    Order: .env.secrets, config/development.env, .env. Later file overrides earlier.
    Uses override=False so process env (e.g. Docker Compose) wins over file values.
    No-op if dotenv not installed; Docker may have already injected env (Φ1).
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    root = get_repo_root()
    for name in (".env.secrets", "config/development.env", ".env"):
        path = root / name
        if path.exists():
            load_dotenv(path, override=False)


def _parse_redis_url(url: str) -> Dict[str, Any]:
    """Parse REDIS_URL into host, port, db, password. Defaults for missing parts."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 6379
    password = parsed.password
    db = 0
    if parsed.path and len(parsed.path) > 1:
        try:
            db = int(parsed.path.lstrip("/").split("/")[0] or "0")
        except ValueError:
            pass
    return {
        "host": host,
        "port": port,
        "db": db,
        "password": password,
    }


def _get_env(key: str, default: str = "") -> str:
    """First env var that is set, or default. No None from os.getenv (use default)."""
    v = os.getenv(key)
    return v if v is not None else default


def _get_env_int(key: str, default: int) -> int:
    try:
        v = os.getenv(key)
        return int(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def _get_env_bool(key: str, default: bool) -> bool:
    v = os.getenv(key)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes")


def build_canonical_config() -> Dict[str, Any]:
    """
    Build the canonical platform config from os.environ only.
    Call after acquire_env() (or when env was injected by Φ1).
    Returns one dict per CONFIG_CONTRACT_SPEC; no env reads after this for platform infra.
    """
    # Redis: REDIS_URL -> nested
    redis_url = _get_env("REDIS_URL", "redis://localhost:6379")
    redis = _parse_redis_url(redis_url)

    # Consul: CONSUL_* -> nested
    consul = {
        "host": _get_env("CONSUL_HOST", "localhost"),
        "port": _get_env_int("CONSUL_PORT", 8500),
        "token": os.getenv("CONSUL_TOKEN"),
    }

    # DuckDB: DUCKDB_* -> nested
    duckdb = {
        "database_path": _get_env("DUCKDB_DATABASE_PATH", "/app/data/duckdb/main.duckdb"),
        "read_only": _get_env_bool("DUCKDB_READ_ONLY", False),
    }

    # Arango: ARANGO_* with naming variants (ARANGO_USERNAME/ARANGO_USER, ARANGO_DATABASE/ARANGO_DB, ARANGO_PASS/ARANGO_ROOT_PASSWORD)
    arango_username = _get_env("ARANGO_USERNAME") or _get_env("ARANGO_USER", "root")
    arango_database = _get_env("ARANGO_DATABASE") or _get_env("ARANGO_DB", "symphainy_platform")
    arango_password = os.getenv("ARANGO_PASS") or os.getenv("ARANGO_ROOT_PASSWORD") or ""

    # Supabase: SUPABASE_PUBLISHABLE_KEY and SUPABASE_SECRET_KEY only (canonical keys supabase_anon_key, supabase_service_key)
    supabase_anon_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    supabase_service_key = os.getenv("SUPABASE_SECRET_KEY")

    # Meilisearch
    meilisearch_port = _get_env_int("MEILISEARCH_PORT", 7700)

    config: Dict[str, Any] = {
        "redis": redis,
        "consul": consul,
        "duckdb": duckdb,
        "arango_url": _get_env("ARANGO_URL", "http://localhost:8529"),
        "arango_username": arango_username,
        "arango_password": arango_password,
        "arango_database": arango_database,
        "supabase_url": os.getenv("SUPABASE_URL"),
        "supabase_anon_key": supabase_anon_key,
        "supabase_service_key": supabase_service_key,
        "supabase_jwks_url": os.getenv("SUPABASE_JWKS_URL"),
        "supabase_jwt_issuer": os.getenv("SUPABASE_JWT_ISSUER"),
        "gcs_project_id": os.getenv("GCS_PROJECT_ID"),
        "gcs_bucket_name": os.getenv("GCS_BUCKET_NAME"),
        "gcs_credentials_json": os.getenv("GCS_CREDENTIALS_JSON"),
        "meilisearch_host": _get_env("MEILISEARCH_HOST", "meilisearch"),
        "meilisearch_port": meilisearch_port,
        "meilisearch_key": os.getenv("MEILI_MASTER_KEY"),
        "runtime_port": _get_env_int("RUNTIME_PORT", 8000),
        "log_level": _get_env("LOG_LEVEL", "INFO"),
        "otel_exporter_otlp_endpoint": _get_env("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip() or None,  # required; no default; pre-boot validates presence and reachability
        # Optional (not required for G3): LLM / capabilities
        "openai_api_key": os.getenv("OPENAI_API_KEY") or os.getenv("LLM_OPENAI_API_KEY"),
        "openai_base_url": os.getenv("OPENAI_BASE_URL"),
        "huggingface_endpoint_url": os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL") or os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT"),
        "huggingface_api_key": os.getenv("HUGGINGFACE_EMBEDDINGS_API_KEY") or os.getenv("HUGGINGFACE_API_KEY"),
    }
    return config


def load_platform_config() -> Dict[str, Any]:
    """
    Gate G2: Acquire env (load env files in order) then build canonical config.
    Single entry point for "config loads". Downstream must not read env for platform infra.
    """
    acquire_env()
    return build_canonical_config()
