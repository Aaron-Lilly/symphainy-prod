"""
Global pytest configuration and shared fixtures for all test layers.

This file provides:
- Global pytest configuration
- Shared fixtures for common test scenarios
- Test utilities and helpers
- Infrastructure safety checks
"""

import sys
from pathlib import Path

# CRITICAL: Set up Python path BEFORE any other imports
_tests_dir = Path(__file__).parent.resolve()
_project_root = _tests_dir.parent

# Add project root to path
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Now safe to import other modules
import pytest
import asyncio
import os
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from unittest.mock import Mock, AsyncMock

# Pytest hook to ensure path is set before test collection
def pytest_configure(config):
    """Configure pytest - ensure Python path is set before test collection."""
    _tests_dir = Path(__file__).parent.resolve()
    _project_root = _tests_dir.parent
    if str(_project_root) not in sys.path:
        sys.path.insert(0, str(_project_root))

logger = logging.getLogger(__name__)

# Critical environment variables that must NEVER be modified in tests
CRITICAL_ENV_VARS = [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GCLOUD_PROJECT",
    "GOOGLE_CLOUD_PROJECT",
]


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def project_root_path():
    """Return project root path as Path object."""
    return Path(__file__).parent.parent


@pytest.fixture
def test_config():
    """Return test configuration dictionary."""
    return {
        "use_real_infrastructure": os.getenv("TEST_USE_REAL_INFRASTRUCTURE", "false").lower() == "true",
        "redis_url": os.getenv("TEST_REDIS_URL", "redis://localhost:6379"),
        "arangodb_url": os.getenv("TEST_ARANGODB_URL", "http://localhost:8529"),
    }


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    return Mock()


@pytest.fixture
def mock_arangodb():
    """Mock ArangoDB client for testing."""
    return Mock()


@pytest.fixture
def mock_session():
    """Mock session for testing."""
    return {
        "session_id": "test_session_123",
        "tenant_id": "test_tenant",
        "user_id": "test_user",
        "created_at": "2026-01-01T00:00:00Z",
        "context": {},
        "active_sagas": [],
    }


@pytest.fixture
def mock_intent():
    """Mock intent for testing."""
    return {
        "intent_type": "content.upload",
        "realm": "content",
        "session_id": "test_session_123",
        "tenant_id": "test_tenant",
        "payload": {"file_path": "/tmp/test.txt"},
    }


# Import infrastructure test fixtures if available
try:
    from tests.infrastructure.test_fixtures import (
        test_infrastructure,
        test_redis,
        test_arango,
        test_consul,
        test_gcs,
        test_supabase,
        test_meilisearch,
        test_public_works,
        clean_test_db
    )
except ImportError:
    # Infrastructure fixtures not available (e.g., in unit tests)
    pass
