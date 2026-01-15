"""
Pytest fixtures for Public Works abstraction tests.

Provides fixtures for testing abstractions with real and mock adapters.
"""

import pytest
import os
from typing import Dict, Any, Optional

from symphainy_platform.foundations.public_works.adapters.supabase_adapter import SupabaseAdapter
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter
from symphainy_platform.foundations.public_works.adapters.consul_adapter import ConsulAdapter
from symphainy_platform.foundations.public_works.abstractions.auth_abstraction import AuthAbstraction
from symphainy_platform.foundations.public_works.abstractions.tenant_abstraction import TenantAbstraction
from symphainy_platform.foundations.public_works.abstractions.state_abstraction import StateManagementAbstraction
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService


@pytest.fixture
def supabase_adapter():
    """Create Supabase adapter for testing."""
    return SupabaseAdapter(
        url=os.getenv("SUPABASE_URL", "https://test.supabase.co"),
        anon_key=os.getenv("SUPABASE_ANON_KEY", "test-anon-key"),
        service_key=os.getenv("SUPABASE_SERVICE_KEY", "test-service-key")
    )


@pytest.fixture
def redis_adapter():
    """Create Redis adapter for testing."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    return RedisAdapter(redis_url=redis_url)


@pytest.fixture
def consul_adapter():
    """Create Consul adapter for testing."""
    consul_host = os.getenv("CONSUL_HOST", "localhost")
    consul_port = int(os.getenv("CONSUL_PORT", "8500"))
    return ConsulAdapter(host=consul_host, port=consul_port)


@pytest.fixture
async def auth_abstraction(supabase_adapter):
    """Create Auth abstraction with Supabase adapter."""
    return AuthAbstraction(supabase_adapter=supabase_adapter)


@pytest.fixture
async def tenant_abstraction(supabase_adapter, redis_adapter):
    """Create Tenant abstraction with adapters."""
    return TenantAbstraction(
        supabase_adapter=supabase_adapter,
        redis_adapter=redis_adapter
    )


@pytest.fixture
async def state_abstraction(redis_adapter):
    """Create State abstraction with Redis adapter."""
    return StateManagementAbstraction(redis_adapter=redis_adapter)


@pytest.fixture
async def public_works_foundation():
    """Create Public Works Foundation for testing."""
    foundation = PublicWorksFoundationService()
    await foundation.initialize()
    return foundation


@pytest.fixture
def use_real_infrastructure():
    """Fixture to determine if tests should use real infrastructure."""
    return os.getenv("TEST_USE_REAL_INFRASTRUCTURE", "false").lower() == "true"


@pytest.fixture
def skip_if_no_real_infrastructure(use_real_infrastructure):
    """Skip test if real infrastructure is not available."""
    if not use_real_infrastructure:
        pytest.skip("Real infrastructure not enabled (set TEST_USE_REAL_INFRASTRUCTURE=true)")
