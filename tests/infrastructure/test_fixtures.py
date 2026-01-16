"""
Test Fixtures for Infrastructure

Provides pytest fixtures for real infrastructure connections.

WHAT (Test Infrastructure Role): I provide real infrastructure connections for testing
HOW (Test Infrastructure Implementation): I use docker-compose services and create adapters
"""

import pytest
import asyncio
import os
import json
from pathlib import Path
from typing import AsyncGenerator, Optional
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter
from symphainy_platform.foundations.public_works.adapters.arango_adapter import ArangoAdapter
from symphainy_platform.foundations.public_works.adapters.consul_adapter import ConsulAdapter
from symphainy_platform.foundations.public_works.adapters.meilisearch_adapter import MeilisearchAdapter
from symphainy_platform.foundations.public_works.adapters.supabase_adapter import SupabaseAdapter
from symphainy_platform.foundations.public_works.adapters.gcs_adapter import GCSAdapter
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from tests.infrastructure.docker_compose_test import DockerComposeTestManager
from utilities import get_logger

logger = get_logger("TestFixtures")

# Get project root for .env.secrets loading
project_root = Path(__file__).resolve().parents[2]

# Check multiple locations for .env.secrets
secrets_paths = [
    project_root / ".env.secrets",
    project_root / "symphainy_platform" / ".env.secrets",
    Path.home() / ".env.secrets"  # User home as last resort
]

# Test configuration - uses test ports from docker-compose.test.yml
TEST_REDIS_HOST = "localhost"
TEST_REDIS_PORT = int(os.getenv("TEST_REDIS_PORT", "6380"))
TEST_REDIS_DB = 15  # Test database

TEST_ARANGO_URL = f"http://localhost:{os.getenv('TEST_ARANGO_PORT', '8530')}"
TEST_ARANGO_USERNAME = "root"
TEST_ARANGO_PASSWORD = os.getenv("TEST_ARANGO_ROOT_PASSWORD", "test_password")
TEST_ARANGO_DATABASE = "symphainy_platform_test"

TEST_CONSUL_HOST = "localhost"
TEST_CONSUL_PORT = int(os.getenv("TEST_CONSUL_PORT", "8501"))

TEST_MEILISEARCH_HOST = "localhost"
TEST_MEILISEARCH_PORT = int(os.getenv("TEST_MEILISEARCH_PORT", "7701"))
TEST_MEILISEARCH_MASTER_KEY = os.getenv("TEST_MEILISEARCH_MASTER_KEY", "test_master_key")

# Supabase test configuration (uses hosted test project)
# Load from .env.secrets or secrets_for_cursor.md if available
def load_env_secrets():
    """Load environment variables from .env.secrets or secrets_for_cursor.md if it exists."""
    import re
    
    # Try .env.secrets first
    for secrets_path in secrets_paths:
        if secrets_path.exists():
            logger.info(f"Loading secrets from: {secrets_path}")
            # Store all key-value pairs (last occurrence wins for duplicates)
            env_vars = {}
            with open(secrets_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        # Parse KEY=VALUE or KEY="VALUE"
                        match = re.match(r'^([^=]+)=(.*)$', line)
                        if match:
                            key = match.group(1).strip()
                            value = match.group(2).strip()
                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            # Store (last occurrence wins)
                            env_vars[key] = value
            
            # Set environment variables (only if not already set)
            for key, value in env_vars.items():
                if key not in os.environ:
                    os.environ[key] = value
            break  # Use first found file

# Load .env.secrets
load_env_secrets()

# Test Supabase configuration (from .env.secrets or environment)
# Uses test Supabase project (no rate limiting)
TEST_SUPABASE_URL = os.getenv("SUPABASE_URL", "")  # From secrets file
TEST_SUPABASE_ANON_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")  # From secrets file
TEST_SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SECRET_KEY", "")  # From secrets file
TEST_SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL", "")
TEST_SUPABASE_JWT_ISSUER = os.getenv("SUPABASE_JWT_ISSUER", "")

# GCS test configuration (uses fake-gcs-server emulator)
TEST_GCS_EMULATOR_PORT = int(os.getenv("TEST_GCS_EMULATOR_PORT", "9023"))
TEST_GCS_EMULATOR_HOST = os.getenv("TEST_GCS_EMULATOR_HOST", "http://localhost")
TEST_GCS_PROJECT_ID = os.getenv("TEST_GCS_PROJECT_ID", "test-project")
TEST_GCS_BUCKET_NAME = os.getenv("TEST_GCS_BUCKET_NAME", "symphainy-test-bucket")
# For emulator, we don't need real credentials - use empty dict
TEST_GCS_CREDENTIALS_JSON = os.getenv("TEST_GCS_CREDENTIALS_JSON", "{}")


@pytest.fixture(scope="session")
async def test_infrastructure():
    """
    Start test infrastructure once per test session.
    
    This fixture starts docker-compose services and waits for them to be healthy.
    It cleans up after all tests complete.
    
    Note: If services are already running, it will skip startup.
    """
    manager = DockerComposeTestManager()
    
    # Check if services are already running
    services_running = all([
        manager.is_service_running("redis"),
        manager.is_service_running("arango"),
        manager.is_service_running("consul"),
        manager.is_service_running("meilisearch"),
        manager.is_service_running("gcs-emulator")
    ])
    
    if not services_running:
        # Start services
        logger.info("Starting test infrastructure...")
        
        success = await manager.start_services([
            "redis", "arango", "consul", "meilisearch", "gcs-emulator"
        ])
        if not success:
            pytest.fail("Failed to start test infrastructure")
    else:
        logger.info("Test infrastructure services already running, skipping startup")
    
    yield
    
    # Note: We don't cleanup here to allow services to stay running for other tests
    # Cleanup can be done manually or via separate cleanup command


@pytest.fixture
async def test_redis(test_infrastructure) -> AsyncGenerator[RedisAdapter, None]:
    """
    Get Redis adapter connected to test Redis.
    
    Cleans test database before and after test.
    """
    adapter = RedisAdapter(
        host=TEST_REDIS_HOST,
        port=TEST_REDIS_PORT,
        db=TEST_REDIS_DB  # Test database
    )
    await adapter.connect()
    
    # Clean test database before test
    await adapter.flushdb()
    
    yield adapter
    
    # Cleanup
    try:
        await adapter.flushdb()
        await adapter.disconnect()
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
async def test_arango(test_infrastructure) -> AsyncGenerator[ArangoAdapter, None]:
    """
    Get ArangoDB adapter connected to test ArangoDB.
    
    Uses test database and ensures it exists.
    """
    adapter = ArangoAdapter(
        url=TEST_ARANGO_URL,
        username=TEST_ARANGO_USERNAME,
        password=TEST_ARANGO_PASSWORD,
        database=TEST_ARANGO_DATABASE
    )
    await adapter.connect()
    
    # Ensure test database exists
    if not await adapter.database_exists(TEST_ARANGO_DATABASE):
        await adapter.create_database(TEST_ARANGO_DATABASE)
    
    yield adapter
    
    # Cleanup: Disconnect (keep database for performance)
    try:
        await adapter.disconnect()
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
async def test_consul(test_infrastructure) -> AsyncGenerator[ConsulAdapter, None]:
    """
    Get Consul adapter connected to test Consul.
    """
    adapter = ConsulAdapter(
        host=TEST_CONSUL_HOST,
        port=TEST_CONSUL_PORT
    )
    if adapter.connect():
        yield adapter
        try:
            adapter.disconnect()
        except Exception:
            pass
    else:
        pytest.skip("Consul not available for testing")


@pytest.fixture
async def test_meilisearch(test_infrastructure) -> AsyncGenerator[MeilisearchAdapter, None]:
    """
    Get Meilisearch adapter connected to test Meilisearch.
    """
    adapter = MeilisearchAdapter(
        host=TEST_MEILISEARCH_HOST,
        port=TEST_MEILISEARCH_PORT,
        api_key=TEST_MEILISEARCH_MASTER_KEY
    )
    if adapter.connect():
        yield adapter
        try:
            adapter.disconnect()
        except Exception:
            pass
    else:
        pytest.skip("Meilisearch not available for testing")


@pytest.fixture
async def test_supabase(test_infrastructure) -> AsyncGenerator[SupabaseAdapter, None]:
    """
    Get Supabase adapter connected to hosted test Supabase project.
    
    Uses test Supabase project (no rate limiting).
    Credentials loaded from .env.secrets or environment variables.
    """
    if not TEST_SUPABASE_URL or not TEST_SUPABASE_ANON_KEY:
        pytest.skip("Supabase test credentials not configured. Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in .env.secrets")
    
    adapter = SupabaseAdapter(
        url=TEST_SUPABASE_URL,
        anon_key=TEST_SUPABASE_ANON_KEY,
        service_key=TEST_SUPABASE_SERVICE_KEY if TEST_SUPABASE_SERVICE_KEY else None,
        jwks_url=TEST_SUPABASE_JWKS_URL if TEST_SUPABASE_JWKS_URL else None,
        jwt_issuer=TEST_SUPABASE_JWT_ISSUER if TEST_SUPABASE_JWT_ISSUER else None
    )
    
    yield adapter


@pytest.fixture
async def test_gcs(test_infrastructure) -> AsyncGenerator[GCSAdapter, None]:
    """
    Get GCS adapter connected to fake-gcs-server emulator.
    
    Uses local GCS emulator for testing.
    Sets STORAGE_EMULATOR_HOST environment variable.
    """
    import os
    
    # Set emulator host for google-cloud-storage library
    os.environ["STORAGE_EMULATOR_HOST"] = f"{TEST_GCS_EMULATOR_HOST}:{TEST_GCS_EMULATOR_PORT}"
    
    try:
        credentials_dict = json.loads(TEST_GCS_CREDENTIALS_JSON) if TEST_GCS_CREDENTIALS_JSON else {}
    except (json.JSONDecodeError, TypeError):
        credentials_dict = {}
    
    adapter = GCSAdapter(
        project_id=TEST_GCS_PROJECT_ID,
        bucket_name=TEST_GCS_BUCKET_NAME,
        credentials_json=credentials_dict
    )
    
    # Create test bucket if it doesn't exist
    try:
        if not adapter.bucket_exists(TEST_GCS_BUCKET_NAME):
            adapter.create_bucket(TEST_GCS_BUCKET_NAME)
    except Exception:
        pass  # Bucket may already exist or creation may fail
    
    yield adapter
    
    # Cleanup: Remove emulator host env var
    os.environ.pop("STORAGE_EMULATOR_HOST", None)


@pytest.fixture
async def test_public_works(
    test_redis,
    test_arango,
    test_consul
) -> AsyncGenerator[PublicWorksFoundationService, None]:
    """
    Get Public Works Foundation Service with all adapters configured.
    
    This fixture provides a fully configured Public Works service for testing,
    with all adapters connected to test infrastructure.
    
    Note: Supabase and GCS are optional - Public Works will initialize them from environment.
    """
    # Set environment variables for Public Works initialization
    # These point to our test infrastructure
    os.environ["REDIS_HOST"] = TEST_REDIS_HOST
    os.environ["REDIS_PORT"] = str(TEST_REDIS_PORT)
    os.environ["REDIS_DB"] = str(TEST_REDIS_DB)
    
    os.environ["ARANGO_URL"] = TEST_ARANGO_URL
    os.environ["ARANGO_USERNAME"] = TEST_ARANGO_USERNAME
    os.environ["ARANGO_PASSWORD"] = TEST_ARANGO_PASSWORD
    os.environ["ARANGO_DATABASE"] = TEST_ARANGO_DATABASE
    os.environ["ARANGO_ROOT_PASSWORD"] = TEST_ARANGO_PASSWORD  # For graph adapter
    
    os.environ["CONSUL_HOST"] = TEST_CONSUL_HOST
    os.environ["CONSUL_PORT"] = str(TEST_CONSUL_PORT)
    
    # GCS emulator
    os.environ["GCS_PROJECT_ID"] = TEST_GCS_PROJECT_ID
    os.environ["GCS_BUCKET_NAME"] = TEST_GCS_BUCKET_NAME
    os.environ["STORAGE_EMULATOR_HOST"] = f"{TEST_GCS_EMULATOR_HOST}:{TEST_GCS_EMULATOR_PORT}"
    
    # Create Public Works config with test adapters
    config = {
        "redis": {
            "host": TEST_REDIS_HOST,
            "port": TEST_REDIS_PORT,
            "db": TEST_REDIS_DB
        },
        "arango_url": TEST_ARANGO_URL,
        "arango_username": TEST_ARANGO_USERNAME,
        "arango_password": TEST_ARANGO_PASSWORD,
        "arango_database": TEST_ARANGO_DATABASE,
        "arango_root_password": TEST_ARANGO_PASSWORD,
        "consul": {
            "host": TEST_CONSUL_HOST,
            "port": TEST_CONSUL_PORT
        },
        "gcs_project_id": TEST_GCS_PROJECT_ID,
        "gcs_bucket_name": TEST_GCS_BUCKET_NAME,
        "gcs_credentials_json": {}
    }
    
    # Create Public Works with test config
    public_works = PublicWorksFoundationService(config=config)
    
    # Try to initialize Public Works (creates adapters and abstractions)
    # This is required for visual_generation_abstraction and other abstractions
    # If initialization fails (e.g., missing adapters), we'll continue anyway
    # The realm will handle missing adapters gracefully
    try:
        await public_works.initialize()
    except Exception as e:
        logger.warning(f"Public Works initialization failed (some features may not work): {e}")
        # Continue anyway - realm will handle missing adapters
    
    yield public_works
    
    # Cleanup: Remove test-specific env vars
    for key in ["REDIS_HOST", "REDIS_PORT", "REDIS_DB", "ARANGO_URL", "ARANGO_USERNAME", 
                "ARANGO_PASSWORD", "ARANGO_DATABASE", "CONSUL_HOST", "CONSUL_PORT",
                "GCS_PROJECT_ID", "GCS_BUCKET_NAME", "STORAGE_EMULATOR_HOST"]:
        os.environ.pop(key, None)
    
    # Cleanup handled by individual adapter fixtures


@pytest.fixture
async def clean_test_db(test_arango):
    """
    Clean test database collections before and after test.
    
    This fixture ensures test isolation by cleaning collections.
    """
    # Get list of existing collections
    db = test_arango.get_database()
    if db:
        # Clean all collections before test
        collections = [col['name'] for col in db.collections() if not col['name'].startswith('_')]
        for collection_name in collections:
            try:
                await test_arango.delete_collection(collection_name)
            except Exception:
                pass  # Collection may not exist
    
    yield
    
    # Clean all collections after test
    if db:
        collections = [col['name'] for col in db.collections() if not col['name'].startswith('_')]
        for collection_name in collections:
            try:
                await test_arango.delete_collection(collection_name)
            except Exception:
                pass  # Collection may not exist
