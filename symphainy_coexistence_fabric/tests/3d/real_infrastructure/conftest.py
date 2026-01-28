"""
Real Infrastructure Test Fixtures

Fixtures that connect to REAL services (Redis, ArangoDB, etc.) instead of mocks.
Uses environment variables to connect to actual infrastructure.
"""

import pytest
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load .env.secrets
def _load_env_secrets():
    possible_paths = [
        project_root / ".env.secrets",
        project_root / "symphainy_platform" / ".env.secrets",
        Path.cwd() / ".env.secrets",
    ]
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path, override=False)
            print(f"✅ Loaded .env.secrets from: {env_path}")
            return True
    return False

_load_env_secrets()


@pytest.fixture(scope="session")
def real_redis_client():
    """Real Redis client connected to actual Redis instance."""
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
        print(f"✅ Connected to real Redis at {host}:{port}")
        yield client
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")


@pytest.fixture(scope="session")
def real_arangodb_client():
    """Real ArangoDB client connected to actual ArangoDB instance."""
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
        print(f"✅ Connected to real ArangoDB at {arango_url}/{arango_db}")
        yield db
    except Exception as e:
        pytest.skip(f"ArangoDB not available: {e}")


# Store PublicWorks instance for reuse
_real_pw_instance = None

@pytest.fixture(scope="session")
async def real_public_works():
    """Real PublicWorksFoundationService connected to actual infrastructure."""
    global _real_pw_instance
    if _real_pw_instance is None:
        from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
        config = {
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "arango_url": os.getenv("ARANGO_URL", "http://localhost:8529"),
            "arango_username": os.getenv("ARANGO_USERNAME", "root"),
            "arango_password": os.getenv("ARANGO_ROOT_PASSWORD", "test_password"),
            "arango_database": os.getenv("ARANGO_DATABASE", "symphainy_platform"),
        }
        pw = PublicWorksFoundationService(config=config)
        try:
            await pw.initialize()
            print("✅ Real PublicWorks initialized")
            _real_pw_instance = pw
            yield pw
        except Exception as e:
            pytest.skip(f"PublicWorks initialization failed: {e}")
    else:
        yield _real_pw_instance


@pytest.fixture
async def real_execution_context(real_state_surface):
    """Real ExecutionContext with actual state surface."""
    from symphainy_platform.runtime.execution_context import ExecutionContext
    from utilities import generate_event_id
    state_surface = await real_state_surface
    return ExecutionContext(
        execution_id=generate_event_id(),
        tenant_id="test_tenant_real",
        session_id=f"test_session_{generate_event_id()}",
        intent=None,
        solution_id="test_solution",
        state_surface=state_surface
    )


@pytest.fixture
async def real_state_surface(real_public_works):
    """Real StateSurface connected to actual Redis/ArangoDB."""
    from symphainy_platform.runtime.state_surface import StateSurface
    # Get PublicWorks from async generator
    async for pw in real_public_works:
        state_abstraction = pw.get_state_abstraction() if hasattr(pw, 'get_state_abstraction') else None
        file_storage = pw.get_file_storage_abstraction() if hasattr(pw, 'get_file_storage_abstraction') else None
        ss = StateSurface(state_abstraction=state_abstraction, file_storage=file_storage)
        print("✅ Real StateSurface initialized")
        return ss


@pytest.fixture
async def real_solutions(real_public_works, real_state_surface):
    """Real solutions initialized with actual infrastructure."""
    from symphainy_platform.solutions import initialize_solutions
    from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
    from symphainy_platform.runtime.intent_registry import IntentRegistry
    registry = SolutionRegistry()
    intent_registry = IntentRegistry()
    services = await initialize_solutions(
        public_works=real_public_works,
        state_surface=real_state_surface,
        solution_registry=registry,
        intent_registry=intent_registry,
        initialize_mcp_servers=False
    )
    print("✅ Real solutions initialized")
    return services
