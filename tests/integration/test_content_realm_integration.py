"""
Integration Test: Experience → Runtime → Content Realm

Tests the full flow from Experience Plane through Runtime to Content Realm.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from typing import Dict, Any

from utilities import get_logger
from symphainy_platform.runtime.intent_registry import IntentRegistry
from symphainy_platform.runtime.realm_registry import RealmRegistry
from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.runtime.wal import WriteAheadLog
from symphainy_platform.runtime.execution_lifecycle_manager import ExecutionLifecycleManager
from symphainy_platform.runtime.intent_model import IntentFactory
from symphainy_platform.realms.content import ContentRealm


logger = get_logger("ContentRealmIntegrationTests")


@pytest.fixture
async def runtime_setup():
    """Setup Runtime components with Content Realm registered."""
    # Initialize components
    intent_registry = IntentRegistry()
    realm_registry = RealmRegistry(intent_registry)
    state_surface = StateSurface(
        state_management_protocol=None  # Will be injected with real protocol in production
    )
    wal = WriteAheadLog(
        redis_adapter=None  # Will be injected with real adapter in production
    )
    
    execution_lifecycle_manager = ExecutionLifecycleManager(
        intent_registry=intent_registry,
        state_surface=state_surface,
        wal=wal
    )
    
    # Register Content Realm
    content_realm = ContentRealm("content")
    realm_registry.register_realm(content_realm)
    
    return {
        "intent_registry": intent_registry,
        "realm_registry": realm_registry,
        "state_surface": state_surface,
        "wal": wal,
        "execution_lifecycle_manager": execution_lifecycle_manager,
        "content_realm": content_realm
    }


@pytest.mark.asyncio
async def test_content_realm_registration(runtime_setup):
    """
    Test: Content Realm registers with Runtime successfully.
    """
    realm_registry = runtime_setup["realm_registry"]
    
    # Verify realm is registered
    assert "content" in realm_registry.list_realms()
    
    # Verify intents are registered
    content_realm = realm_registry.get_realm("content")
    assert content_realm is not None
    
    declared_intents = content_realm.declare_intents()
    assert "ingest_file" in declared_intents
    assert "parse_content" in declared_intents
    
    logger.info("✅ Content Realm registration validated")


@pytest.mark.asyncio
async def test_ingest_file_intent_flow(runtime_setup):
    """
    Test: Experience → Runtime → Content Realm (ingest_file intent).
    
    Flow:
    1. Create ingest_file intent
    2. Submit to Runtime
    3. Runtime routes to Content Realm
    4. Content Realm processes via orchestrator
    5. Returns artifacts and events
    """
    execution_lifecycle_manager = runtime_setup["execution_lifecycle_manager"]
    
    # Create ingest_file intent
    intent = IntentFactory.create_intent(
        intent_type="ingest_file",
        tenant_id="test_tenant",
        session_id="test_session",
        solution_id="default",
        parameters={"file_id": "test_file_123"}
    )
    
    # Execute intent via Runtime
    result = await execution_lifecycle_manager.execute(intent)
    
    # Verify result
    assert result.success
    assert result.artifacts is not None
    assert "parsed_file_id" in result.artifacts
    assert result.events is not None
    assert len(result.events) > 0
    
    logger.info("✅ ingest_file intent flow validated")


@pytest.mark.asyncio
async def test_get_parsed_file_intent_flow(runtime_setup):
    """
    Test: Experience → Runtime → Content Realm (get_parsed_file intent).
    """
    execution_lifecycle_manager = runtime_setup["execution_lifecycle_manager"]
    
    # Create get_parsed_file intent
    intent = IntentFactory.create_intent(
        intent_type="get_parsed_file",
        tenant_id="test_tenant",
        session_id="test_session",
        solution_id="default",
        parameters={"parsed_file_id": "test_parsed_file_123"}
    )
    
    # Execute intent via Runtime
    result = await execution_lifecycle_manager.execute(intent)
    
    # Verify result
    assert result.success
    assert result.artifacts is not None
    assert "parsed_file" in result.artifacts
    
    logger.info("✅ get_parsed_file intent flow validated")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
