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
    
    # Consul
    CONSUL_HOST: str = Field(
        default="localhost",
        description="Consul host"
    )
    CONSUL_PORT: int = Field(
        default=8500,
        description="Consul port"
    )
    CONSUL_TOKEN: Optional[str] = Field(
        default=None,
        description="Optional Consul ACL token"
    )
    
    # Traefik
    TRAEFIK_HTTP_PORT: int = Field(
        default=80,
        description="Traefik HTTP port"
    )
    TRAEFIK_HTTPS_PORT: int = Field(
        default=443,
        description="Traefik HTTPS port"
    )
    TRAEFIK_DASHBOARD_PORT: int = Field(
        default=8080,
        description="Traefik dashboard port"
    )
    
    # Observability
    TEMPO_PORT: int = Field(
        default=3200,
        description="Tempo port"
    )
    GRAFANA_PORT: int = Field(
        default=3000,
        description="Grafana port"
    )
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(
        default="http://localhost:4317",
        description="OpenTelemetry exporter endpoint"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # Supabase
    SUPABASE_URL: Optional[str] = Field(
        default=None,
        description="Supabase project URL"
    )
    SUPABASE_ANON_KEY: Optional[str] = Field(
        default=None,
        description="Supabase anonymous/public key"
    )
    SUPABASE_SERVICE_KEY: Optional[str] = Field(
        default=None,
        description="Supabase service role key"
    )
    SUPABASE_JWKS_URL: Optional[str] = Field(
        default=None,
        description="Supabase JWKS URL for JWT verification"
    )
    SUPABASE_JWT_ISSUER: Optional[str] = Field(
        default=None,
        description="Supabase JWT issuer for token validation"
    )
    
    # Google Cloud Storage
    GCS_PROJECT_ID: Optional[str] = Field(
        default=None,
        description="GCP project ID for GCS"
    )
    GCS_BUCKET_NAME: Optional[str] = Field(
        default=None,
        description="GCS bucket name"
    )
    GCS_CREDENTIALS_JSON: Optional[str] = Field(
        default=None,
        description="GCS service account credentials as JSON string"
    )
    
    # Meilisearch
    MEILISEARCH_PORT: int = Field(
        default=7700,
        description="Meilisearch port"
    )
    MEILI_MASTER_KEY: Optional[str] = Field(
        default=None,
        description="Meilisearch master key"
    )
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @validator("RUNTIME_PORT", "SMART_CITY_PORT", "REALMS_PORT", "REDIS_PORT", "ARANGO_PORT", 
               "CONSUL_PORT", "TRAEFIK_HTTP_PORT", "TRAEFIK_HTTPS_PORT", "TRAEFIK_DASHBOARD_PORT",
               "TEMPO_PORT", "GRAFANA_PORT", "MEILISEARCH_PORT")
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
    # Read from environment variables explicitly
    return EnvContract(
        REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379"),
        ARANGO_URL=os.getenv("ARANGO_URL", "http://localhost:8529"),
        ARANGO_ROOT_PASSWORD=os.getenv("ARANGO_ROOT_PASSWORD", "changeme"),
        RUNTIME_PORT=int(os.getenv("RUNTIME_PORT", "8000")),
        SMART_CITY_PORT=int(os.getenv("SMART_CITY_PORT", "8001")),
        REALMS_PORT=int(os.getenv("REALMS_PORT", "8002")),
        REDIS_PORT=int(os.getenv("REDIS_PORT", "6379")),
        ARANGO_PORT=int(os.getenv("ARANGO_PORT", "8529")),
        CONSUL_HOST=os.getenv("CONSUL_HOST", "localhost"),
        CONSUL_PORT=int(os.getenv("CONSUL_PORT", "8500")),
        CONSUL_TOKEN=os.getenv("CONSUL_TOKEN"),
        TRAEFIK_HTTP_PORT=int(os.getenv("TRAEFIK_HTTP_PORT", "80")),
        TRAEFIK_HTTPS_PORT=int(os.getenv("TRAEFIK_HTTPS_PORT", "443")),
        TRAEFIK_DASHBOARD_PORT=int(os.getenv("TRAEFIK_DASHBOARD_PORT", "8080")),
        TEMPO_PORT=int(os.getenv("TEMPO_PORT", "3200")),
        GRAFANA_PORT=int(os.getenv("GRAFANA_PORT", "3000")),
        OTEL_EXPORTER_OTLP_ENDPOINT=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        SUPABASE_URL=os.getenv("SUPABASE_URL"),
        SUPABASE_ANON_KEY=os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY"),
        SUPABASE_SERVICE_KEY=os.getenv("SUPABASE_SERVICE_KEY"),
        SUPABASE_JWKS_URL=os.getenv("SUPABASE_JWKS_URL"),
        SUPABASE_JWT_ISSUER=os.getenv("SUPABASE_JWT_ISSUER"),
        GCS_PROJECT_ID=os.getenv("GCS_PROJECT_ID"),
        GCS_BUCKET_NAME=os.getenv("GCS_BUCKET_NAME"),
        GCS_CREDENTIALS_JSON=os.getenv("GCS_CREDENTIALS_JSON"),
        MEILISEARCH_PORT=int(os.getenv("MEILISEARCH_PORT", "7700")),
        MEILI_MASTER_KEY=os.getenv("MEILI_MASTER_KEY")
    )


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
