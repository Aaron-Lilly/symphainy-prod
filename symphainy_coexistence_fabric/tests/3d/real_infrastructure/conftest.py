"""
Real Infrastructure Test Fixtures (Genesis-based)

Uses full Genesis (load_platform_config → pre_boot_validate → create_runtime_services →
create_fastapi_app). real_solutions and real_execution_context come from the Genesis-built
app so "what works in test also works in prod."

Depends on genesis_app and genesis_services from tests/3d/conftest.py.
"""

import pytest
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def real_redis_client():
    """Real Redis client (optional connectivity helper)."""
    import redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        if redis_url.startswith("redis://"):
            parts = redis_url.replace("redis://", "").split(":")
            host = parts[0] if len(parts) > 0 else "localhost"
            port = int(parts[1]) if len(parts) > 1 else 6379
        else:
            host = "localhost"
            port = 6379
        client = redis.Redis(host=host, port=port, decode_responses=True)
        client.ping()
        yield client
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")


@pytest.fixture(scope="session")
def real_arangodb_client():
    """Real ArangoDB client (optional connectivity helper)."""
    try:
        from arango import ArangoClient
        arango_url = os.getenv("ARANGO_URL", "http://localhost:8529")
        arango_user = os.getenv("ARANGO_USERNAME", "root")
        arango_password = os.getenv("ARANGO_ROOT_PASSWORD", "test_password")
        arango_db = os.getenv("ARANGO_DATABASE", "symphainy_platform")
        client = ArangoClient(hosts=arango_url)
        sys_db = client.db("_system", username=arango_user, password=arango_password)
        if arango_db not in sys_db.databases():
            sys_db.create_database(arango_db)
        db = client.db(arango_db, username=arango_user, password=arango_password)
        yield db
    except Exception as e:
        pytest.skip(f"ArangoDB not available: {e}")


@pytest.fixture(scope="session")
def real_public_works(genesis_services):
    """Public works from Genesis app (for tests that need public_works directly, e.g. LLM)."""
    if genesis_services is None or getattr(genesis_services, "public_works", None) is None:
        pytest.skip("Genesis public_works not available")
    return genesis_services.public_works


@pytest.fixture(scope="session")
async def real_solutions(genesis_services):
    """Real solutions from Genesis app (same object graph as prod)."""
    if genesis_services is None or getattr(genesis_services, "solution_services", None) is None:
        pytest.skip("Genesis solution_services not available (pre-boot or create_runtime_services failed)")
    return genesis_services.solution_services


@pytest.fixture(scope="session")
async def real_execution_context(genesis_services):
    """Real ExecutionContext with state_surface from Genesis app."""
    if genesis_services is None or getattr(genesis_services, "state_surface", None) is None:
        pytest.skip("Genesis state_surface not available")
    from symphainy_platform.runtime.execution_context import ExecutionContext
    from utilities import generate_event_id
    return ExecutionContext(
        execution_id=generate_event_id(),
        tenant_id="test_tenant_real",
        session_id=f"test_session_{generate_event_id()}",
        intent=None,
        solution_id="test_solution",
        state_surface=genesis_services.state_surface
    )
