# Comprehensive Testing Plan: Foundation Validation

**Status:** Ready to Execute  
**Created:** January 2026  
**Goal:** Validate platform foundation before documentation

---

## Executive Summary

This plan establishes a **docker-based testing infrastructure** and a **holistic integrated test strategy** that validates:

1. **Architectural Compliance** - 5-layer architecture, Public Works pattern, Runtime Participation Contract
2. **Functional Compliance** - MVP showcase use case delivery
3. **Extensibility Vision** - 350k insurance policies, legacy system migration
4. **Frontend Integration Readiness** - API contracts, WebSocket streaming, authentication
5. **Platform Stability** - Error handling, recovery, performance

**Key Principle:** Test against the **same infrastructure as production** (docker-compose) to avoid environment divergence.

---

## Part 1: Docker-Based Testing Infrastructure

### Task 1.1: Create Test Docker Compose Configuration

**Goal:** Separate test infrastructure from production, but use same services

**Files to Create:**
- `docker-compose.test.yml` - Test-specific docker-compose configuration
- `tests/infrastructure/docker_compose_test.py` - Docker compose test utilities
- `tests/infrastructure/test_fixtures.py` - Infrastructure fixtures
- `tests/infrastructure/cleanup.py` - Cleanup utilities

**Implementation:**

#### `docker-compose.test.yml`

```yaml
# Extends docker-compose.yml but with test-specific configurations
version: '3.8'

services:
  # Infrastructure services (same as production)
  redis:
    image: redis:7-alpine
    container_name: symphainy-redis-test
    ports:
      - "6380:6379"  # Different port to avoid conflicts
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3
    networks:
      - symphainy_test_net

  arango:
    image: arangodb:3.11
    container_name: symphainy-arango-test
    ports:
      - "8530:8529"  # Different port
    environment:
      ARANGO_ROOT_PASSWORD: test_password
    healthcheck:
      test: ["CMD-SHELL", "nc -z localhost 8529 || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 30s
    networks:
      - symphainy_test_net

  # Test database isolation
  # Use test databases/collections, cleaned up after tests

networks:
  symphainy_test_net:
    driver: bridge
```

**Key Features:**
- Same services as production
- Different ports to avoid conflicts
- Test-specific databases/collections
- Fast health checks for CI/CD

#### `tests/infrastructure/docker_compose_test.py`

```python
"""
Docker Compose Test Utilities

Manages docker-compose services for testing.
"""

import subprocess
import time
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from utilities import get_logger

logger = get_logger("DockerComposeTest")


class DockerComposeTestManager:
    """Manages docker-compose services for testing."""
    
    def __init__(self, compose_file: str = "docker-compose.test.yml"):
        self.compose_file = compose_file
        self.project_root = Path(__file__).parent.parent.parent
        self.compose_path = self.project_root / compose_file
    
    async def start_services(self, services: Optional[list] = None) -> bool:
        """Start docker-compose services."""
        services = services or ["redis", "arango"]
        cmd = ["docker-compose", "-f", str(self.compose_path), "up", "-d"] + services
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error(f"Failed to start services: {result.stderr}")
                return False
            
            # Wait for health checks
            await self._wait_for_health(services)
            logger.info(f"✅ Services started: {services}")
            return True
        except Exception as e:
            logger.error(f"Error starting services: {e}", exc_info=True)
            return False
    
    async def stop_services(self, services: Optional[list] = None) -> bool:
        """Stop docker-compose services."""
        services = services or ["redis", "arango"]
        cmd = ["docker-compose", "-f", str(self.compose_path), "stop"] + services
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            logger.info(f"✅ Services stopped: {services}")
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error stopping services: {e}", exc_info=True)
            return False
    
    async def cleanup(self) -> bool:
        """Clean up test data and volumes."""
        cmd = ["docker-compose", "-f", str(self.compose_path), "down", "-v"]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            logger.info("✅ Test infrastructure cleaned up")
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error cleaning up: {e}", exc_info=True)
            return False
    
    async def _wait_for_health(self, services: list, timeout: int = 60):
        """Wait for services to become healthy."""
        # Implementation: Check health endpoints
        # For Redis: redis-cli ping
        # For ArangoDB: HTTP health check
        pass
```

#### `tests/infrastructure/test_fixtures.py`

```python
"""
Test Fixtures for Infrastructure

Provides pytest fixtures for real infrastructure connections.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter
from symphainy_platform.foundations.public_works.adapters.arango_adapter import ArangoAdapter
from tests.infrastructure.docker_compose_test import DockerComposeTestManager

# Test configuration
TEST_REDIS_HOST = "localhost"
TEST_REDIS_PORT = 6380
TEST_ARANGO_URL = "http://localhost:8530"
TEST_ARANGO_USERNAME = "root"
TEST_ARANGO_PASSWORD = "test_password"
TEST_ARANGO_DATABASE = "symphainy_platform_test"


@pytest.fixture(scope="session")
async def test_infrastructure():
    """Start test infrastructure once per test session."""
    manager = DockerComposeTestManager()
    
    # Start services
    success = await manager.start_services(["redis", "arango"])
    if not success:
        pytest.fail("Failed to start test infrastructure")
    
    yield
    
    # Cleanup
    await manager.cleanup()


@pytest.fixture
async def test_redis(test_infrastructure) -> AsyncGenerator[RedisAdapter, None]:
    """Get Redis adapter connected to test Redis."""
    adapter = RedisAdapter(
        host=TEST_REDIS_HOST,
        port=TEST_REDIS_PORT,
        db=15  # Test database
    )
    await adapter.connect()
    
    # Clean test database
    await adapter.flushdb()
    
    yield adapter
    
    # Cleanup
    await adapter.flushdb()
    await adapter.disconnect()


@pytest.fixture
async def test_arango(test_infrastructure) -> AsyncGenerator[ArangoAdapter, None]:
    """Get ArangoDB adapter connected to test ArangoDB."""
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
    
    # Cleanup: Delete test collections
    # (Keep database for performance, but clean collections)
    await adapter.disconnect()
```

---

### Task 1.2: Test Data Isolation and Cleanup

**Goal:** Ensure each test is isolated and cleans up after itself

**Files to Create:**
- `tests/infrastructure/test_data_manager.py` - Test data management utilities

**Implementation:**

```python
"""
Test Data Management Utilities

Manages test data isolation and cleanup.
"""

from typing import Dict, Any, List
from symphainy_platform.foundations.public_works.adapters.arango_adapter import ArangoAdapter
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter


class TestDataManager:
    """Manages test data isolation and cleanup."""
    
    def __init__(
        self,
        arango_adapter: ArangoAdapter,
        redis_adapter: RedisAdapter
    ):
        self.arango_adapter = arango_adapter
        self.redis_adapter = redis_adapter
        self.test_collections: List[str] = []
        self.test_keys: List[str] = []
    
    async def create_test_collection(self, collection_name: str) -> bool:
        """Create a test collection and track it for cleanup."""
        success = await self.arango_adapter.create_collection(collection_name)
        if success:
            self.test_collections.append(collection_name)
        return success
    
    async def cleanup(self):
        """Clean up all test data."""
        # Clean ArangoDB collections
        for collection in self.test_collections:
            try:
                await self.arango_adapter.delete_collection(collection)
            except Exception:
                pass  # Collection may not exist
        
        # Clean Redis keys
        for key in self.test_keys:
            try:
                await self.redis_adapter.delete(key)
            except Exception:
                pass
        
        self.test_collections.clear()
        self.test_keys.clear()
```

---

## Part 2: Holistic Integrated Test Plan

### Test Strategy: Three-Layer Testing

#### Layer 1: Unit Tests (Fast, Isolated)
- **Purpose:** Test business logic in isolation
- **Speed:** < 1 second per test
- **Infrastructure:** Mocked
- **When:** Pure functions, business logic, validation

#### Layer 2: Integration Tests (Real Infrastructure)
- **Purpose:** Test component interactions with real infrastructure
- **Speed:** ~5-10 seconds per test
- **Infrastructure:** Real (docker-compose)
- **When:** Adapter + abstraction flows, infrastructure operations

#### Layer 3: E2E Tests (Full Platform)
- **Purpose:** Test complete user journeys
- **Speed:** ~30-60 seconds per test
- **Infrastructure:** Full docker-compose stack
- **When:** Complete workflows, user scenarios

---

### Test Suite Structure

```
tests/
├── unit/                          # Layer 1: Fast, isolated
│   ├── adapters/                  # Adapter unit tests
│   ├── abstractions/              # Abstraction unit tests
│   ├── runtime/                   # Runtime unit tests
│   └── realms/                    # Realm unit tests
│
├── integration/                   # Layer 2: Real infrastructure
│   ├── infrastructure/            # Infrastructure integration tests
│   │   ├── test_arango_adapter.py
│   │   ├── test_redis_adapter.py
│   │   ├── test_state_abstraction.py
│   │   ├── test_data_brain.py
│   │   └── test_event_publishing.py
│   ├── runtime/                   # Runtime integration tests
│   │   ├── test_runtime_spine.py
│   │   ├── test_execution_lifecycle.py
│   │   └── test_state_surface.py
│   ├── realms/                    # Realm integration tests
│   │   ├── test_content_realm.py
│   │   ├── test_insights_realm.py
│   │   └── test_journey_realm.py
│   └── civic_systems/             # Civic Systems integration tests
│       ├── test_smart_city.py
│       ├── test_experience_plane.py
│       └── test_agentic_system.py
│
├── e2e/                           # Layer 3: Full platform
│   ├── architectural/            # Architectural compliance tests
│   │   ├── test_5_layer_architecture.py
│   │   ├── test_public_works_pattern.py
│   │   ├── test_runtime_participation_contract.py
│   │   └── test_swappability.py
│   ├── functional/                # Functional compliance tests
│   │   ├── test_mvp_showcase.py
│   │   ├── test_content_pillar.py
│   │   ├── test_insights_pillar.py
│   │   ├── test_operations_pillar.py
│   │   └── test_business_outcomes_pillar.py
│   ├── extensibility/              # Extensibility vision tests
│   │   ├── test_350k_policies.py
│   │   ├── test_legacy_migration.py
│   │   └── test_multi_tenant.py
│   ├── frontend/                   # Frontend integration tests
│   │   ├── test_api_contracts.py
│   │   ├── test_websocket_streaming.py
│   │   ├── test_authentication.py
│   │   └── test_frontend_e2e.py
│   └── stability/                 # Platform stability tests
│       ├── test_error_handling.py
│       ├── test_recovery.py
│       └── test_performance.py
│
└── infrastructure/                # Test infrastructure utilities
    ├── docker_compose_test.py
    ├── test_fixtures.py
    ├── test_data_manager.py
    └── cleanup.py
```

---

## Part 3: Critical Path Tests (Priority Order)

### Phase 1: Infrastructure Foundation (Week 1, Days 1-2)

#### Test 1.1: ArangoDB Adapter

**File:** `tests/integration/infrastructure/test_arango_adapter.py`

**Tests:**
- ✅ Connection and health check
- ✅ Database creation and existence check
- ✅ Collection operations (create, exists, delete)
- ✅ Document operations (insert, get, update, delete)
- ✅ AQL query execution
- ✅ Error handling (connection failures, invalid queries)
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- All operations work with real ArangoDB
- Error handling is graceful
- Test data is isolated and cleaned up

---

#### Test 1.2: ArangoDB Graph Adapter

**File:** `tests/integration/infrastructure/test_arango_graph_adapter.py`

**Tests:**
- ✅ Graph creation and existence check
- ✅ Node operations (create, get, update, delete)
- ✅ Relationship operations (create)
- ✅ Graph queries (find_path, get_neighbors)
- ✅ Semantic similarity search (basic)
- ✅ Error handling
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- All graph operations work with real ArangoDB
- Graph queries return correct results
- Test data is isolated and cleaned up

---

#### Test 1.3: StateAbstraction with ArangoDB

**File:** `tests/integration/infrastructure/test_state_abstraction.py`

**Tests:**
- ✅ Hot/cold state pattern (Redis hot, ArangoDB cold)
- ✅ State storage in Redis (hot state)
- ✅ State storage in ArangoDB (cold state)
- ✅ State retrieval from Redis (hot state)
- ✅ State retrieval from ArangoDB (cold state, fallback)
- ✅ State updates in both backends
- ✅ State deletion from both backends
- ✅ State listing from both backends
- ✅ TTL handling (Redis only)
- ✅ Error handling (backend failures)

**Acceptance Criteria:**
- Hot/cold pattern works correctly
- State retrieval prioritizes hot state, falls back to cold
- Both backends are used correctly
- Test data is isolated and cleaned up

---

#### Test 1.4: DataBrain with ArangoDB

**File:** `tests/integration/infrastructure/test_data_brain.py`

**Tests:**
- ✅ DataBrain initialization
- ✅ Reference registration (file references)
- ✅ Reference retrieval
- ✅ Provenance tracking (data lineage)
- ✅ Provenance retrieval
- ✅ Graph operations (relationships between references)
- ✅ Persistence (references survive restarts)
- ✅ Error handling
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- DataBrain persists references in ArangoDB
- Provenance is tracked correctly
- Graph operations work
- Test data is isolated and cleaned up

---

#### Test 1.5: Event Publishing

**File:** `tests/integration/infrastructure/test_event_publishing.py`

**Tests:**
- ✅ Redis Streams publisher connection
- ✅ Event publishing (single event)
- ✅ Event publishing (batch events)
- ✅ Event consumption (read from stream)
- ✅ Event headers (correlation_id, tenant_id)
- ✅ Error handling (publishing failures)
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- Events are published to Redis Streams
- Events can be consumed
- Error handling is graceful
- Test data is isolated and cleaned up

---

#### Test 1.6: TransactionalOutbox Integration

**File:** `tests/integration/infrastructure/test_transactional_outbox.py`

**Tests:**
- ✅ Event addition to outbox
- ✅ Event publishing from outbox
- ✅ Atomic event publishing (all or nothing)
- ✅ Retry logic (failed publishing)
- ✅ Event ordering
- ✅ Error handling
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- Events are added to outbox atomically
- Events are published correctly
- Retry logic works
- Test data is isolated and cleaned up

---

### Phase 2: Runtime Integration (Week 1, Days 3-4)

#### Test 2.1: Runtime Spine

**File:** `tests/integration/runtime/test_runtime_spine.py`

**Tests:**
- ✅ Runtime initialization
- ✅ Service discovery (Consul integration)
- ✅ Health checks
- ✅ Session creation
- ✅ Intent submission
- ✅ Execution lifecycle
- ✅ Error handling
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- Runtime initializes correctly
- All services are discovered
- Sessions and intents work
- Test data is isolated and cleaned up

---

#### Test 2.2: Execution Lifecycle

**File:** `tests/integration/runtime/test_execution_lifecycle.py`

**Tests:**
- ✅ Intent acceptance
- ✅ Context creation
- ✅ Handler discovery
- ✅ Handler execution
- ✅ Artifact handling
- ✅ Event publishing
- ✅ Execution completion
- ✅ Failure handling
- ✅ Retry logic
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- Complete execution lifecycle works
- Artifacts and events are handled correctly
- Failure handling works
- Test data is isolated and cleaned up

---

#### Test 2.3: State Surface

**File:** `tests/integration/runtime/test_state_surface.py`

**Tests:**
- ✅ Session state management
- ✅ Execution state management
- ✅ File reference retrieval
- ✅ Hot/cold state pattern
- ✅ State persistence
- ✅ Error handling
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- State Surface works with both Redis and ArangoDB
- File references are retrieved correctly
- State persists correctly
- Test data is isolated and cleaned up

---

### Phase 3: Realm Integration (Week 1, Days 4-5)

#### Test 3.1: Content Realm

**File:** `tests/integration/realms/test_content_realm.py`

**Tests:**
- ✅ Realm registration with Runtime
- ✅ File ingestion intent
- ✅ File parsing intent
- ✅ File storage (GCS)
- ✅ File metadata (Supabase)
- ✅ Parsing results (all file types)
- ✅ Preview generation
- ✅ Error handling
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- Content Realm works end-to-end
- All file types are parsed correctly
- Files are stored correctly
- Test data is isolated and cleaned up

---

#### Test 3.2: Insights Realm

**File:** `tests/integration/realms/test_insights_realm.py`

**Tests:**
- ✅ Realm registration with Runtime
- ✅ Quality assessment intent
- ✅ Interactive analysis intent
- ✅ Data mapping intent
- ✅ Semantic embeddings
- ✅ Graph operations (ArangoDB)
- ✅ Error handling
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- Insights Realm works end-to-end
- Semantic analysis works
- Graph operations work
- Test data is isolated and cleaned up

---

#### Test 3.3: Journey Realm

**File:** `tests/integration/realms/test_journey_realm.py`

**Tests:**
- ✅ Realm registration with Runtime
- ✅ SOP generation intent
- ✅ Workflow conversion intent
- ✅ Coexistence analysis intent
- ✅ Blueprint generation intent
- ✅ Journey creation intent
- ✅ Error handling
- ✅ Cleanup and isolation

**Acceptance Criteria:**
- Journey Realm works end-to-end
- SOP and workflow operations work
- Coexistence analysis works
- Test data is isolated and cleaned up

---

### Phase 4: Architectural Compliance (Week 2, Days 1-2)

#### Test 4.1: 5-Layer Architecture Compliance

**File:** `tests/e2e/architectural/test_5_layer_architecture.py`

**Tests:**
- ✅ Layer 0 (Adapters) - No business logic
- ✅ Layer 1 (Abstractions) - Business logic, no direct infrastructure
- ✅ Layer 2 (Protocols) - Contracts only
- ✅ Layer 3 (Runtime) - Execution authority
- ✅ Layer 4 (Foundation Service) - Orchestration
- ✅ Layer boundaries are respected
- ✅ No cross-layer violations

**Acceptance Criteria:**
- All layers are correctly implemented
- No architectural violations
- Layer boundaries are respected

---

#### Test 4.2: Public Works Pattern Compliance

**File:** `tests/e2e/architectural/test_public_works_pattern.py`

**Tests:**
- ✅ All infrastructure via abstractions
- ✅ No direct infrastructure calls in business logic
- ✅ Adapter swappability (Redis ↔ ArangoDB)
- ✅ Abstraction contracts are met
- ✅ No direct Redis/ArangoDB/GCS calls in realms

**Acceptance Criteria:**
- Public Works pattern is followed
- No direct infrastructure calls
- Adapters are swappable

---

#### Test 4.3: Runtime Participation Contract Compliance

**File:** `tests/e2e/architectural/test_runtime_participation_contract.py`

**Tests:**
- ✅ Realms declare intents
- ✅ Realms accept runtime context
- ✅ Realms return artifacts and events
- ✅ Realms don't bypass Runtime for state
- ✅ Realms don't orchestrate workflows
- ✅ Realms don't persist authoritative data

**Acceptance Criteria:**
- Runtime Participation Contract is followed
- No contract violations
- Realms work correctly with Runtime

---

### Phase 5: Functional Compliance - MVP Showcase (Week 2, Days 3-4)

#### Test 5.1: Content Pillar (MVP Showcase)

**File:** `tests/e2e/functional/test_content_pillar.py`

**Tests:**
- ✅ User uploads file
- ✅ File is parsed
- ✅ Parsed result is displayed
- ✅ Semantic interpretation is shown
- ✅ All file types work (CSV, Excel, PDF, Word, HTML, Image, JSON, Mainframe)
- ✅ Error handling (invalid files, missing files)
- ✅ Multi-file upload
- ✅ File preview generation

**Acceptance Criteria:**
- Content Pillar works as described in MVP showcase
- All file types are supported
- User experience is smooth

---

#### Test 5.2: Insights Pillar (MVP Showcase)

**File:** `tests/e2e/functional/test_insights_pillar.py`

**Tests:**
- ✅ Quality assessment is generated
- ✅ Interactive analysis works (structured data)
- ✅ Interactive analysis works (unstructured data)
- ✅ Data mapping feature works
- ✅ Virtual pipeline feature works
- ✅ Semantic embeddings are used
- ✅ Error handling

**Acceptance Criteria:**
- Insights Pillar works as described in MVP showcase
- All features are functional
- User experience is smooth

---

#### Test 5.3: Operations Pillar (MVP Showcase)

**File:** `tests/e2e/functional/test_operations_pillar.py`

**Tests:**
- ✅ User uploads workflow/SOP file
- ✅ Visual is generated from workflow
- ✅ Visual is generated from SOP
- ✅ SOP is generated from workflow
- ✅ Workflow is generated from SOP
- ✅ SOP is generated from scratch via chat
- ✅ Coexistence analysis works
- ✅ Coexistence blueprint is generated
- ✅ Platform journey is created from blueprint
- ✅ Error handling

**Acceptance Criteria:**
- Operations Pillar works as described in MVP showcase
- All features are functional
- User experience is smooth

---

#### Test 5.4: Business Outcomes Pillar (MVP Showcase)

**File:** `tests/e2e/functional/test_business_outcomes_pillar.py`

**Tests:**
- ✅ Summary visual is generated
- ✅ Roadmap is generated
- ✅ POC proposal is generated
- ✅ Platform solution is created from roadmap
- ✅ Platform solution is created from POC proposal
- ✅ Error handling

**Acceptance Criteria:**
- Business Outcomes Pillar works as described in MVP showcase
- All features are functional
- User experience is smooth

---

#### Test 5.5: Admin Dashboard (MVP Showcase)

**File:** `tests/e2e/functional/test_admin_dashboard.py`

**Tests:**
- ✅ Platform statistics are displayed
- ✅ Client config foundation SDKs are showcased
- ✅ User interaction patterns are shown
- ✅ Error handling

**Acceptance Criteria:**
- Admin Dashboard works as described in MVP showcase
- All features are functional

---

#### Test 5.6: Chat Interface (MVP Showcase)

**File:** `tests/e2e/functional/test_chat_interface.py`

**Tests:**
- ✅ Guide agent (global concierge) works
- ✅ Pillar liaison agents work (one per pillar)
- ✅ Pillar-specific interactions work
- ✅ Deep dives on analysis (Insights pillar)
- ✅ SOP generation (Operations pillar)
- ✅ Error handling

**Acceptance Criteria:**
- Chat Interface works as described in MVP showcase
- All agents work correctly
- User experience is smooth

---

### Phase 6: Extensibility Vision (Week 2, Days 4-5)

#### Test 6.1: 350k Insurance Policies

**File:** `tests/e2e/extensibility/test_350k_policies.py`

**Tests:**
- ✅ Platform handles 350k policies
- ✅ Performance is acceptable (< 1 second per policy)
- ✅ Memory usage is reasonable
- ✅ Concurrent processing works
- ✅ Error handling (partial failures)
- ✅ Recovery from failures
- ✅ Data integrity (no data loss)

**Acceptance Criteria:**
- Platform can handle 350k policies
- Performance is acceptable
- No data loss
- Error handling works

---

#### Test 6.2: Legacy System Migration

**File:** `tests/e2e/extensibility/test_legacy_migration.py`

**Tests:**
- ✅ Legacy system integration (mainframe files)
- ✅ Policy migration workflow
- ✅ Target system integration
- ✅ Data transformation
- ✅ Validation and error handling
- ✅ Rollback capability
- ✅ Progress tracking

**Acceptance Criteria:**
- Legacy system migration works
- Data transformation is correct
- Error handling works
- Rollback works

---

#### Test 6.3: Multi-Tenant Isolation

**File:** `tests/e2e/extensibility/test_multi_tenant.py`

**Tests:**
- ✅ Tenant isolation (data, state, execution)
- ✅ Multi-tenant concurrent execution
- ✅ Tenant-specific configurations
- ✅ Tenant-specific policies
- ✅ Error handling (tenant failures)
- ✅ Data isolation (no cross-tenant access)

**Acceptance Criteria:**
- Multi-tenant isolation works
- No cross-tenant access
- Performance is acceptable
- Error handling works

---

### Phase 7: Frontend Integration (Week 2, Days 5-6)

#### Test 7.1: API Contracts

**File:** `tests/e2e/frontend/test_api_contracts.py`

**Tests:**
- ✅ Authentication API (login, signup, token refresh)
- ✅ Session API (create, get, list)
- ✅ Intent API (submit, status, cancel)
- ✅ File API (upload, list, get, delete)
- ✅ Realm API (content, insights, journey, solution)
- ✅ WebSocket API (connection, streaming, disconnection)
- ✅ Error responses (4xx, 5xx)
- ✅ API versioning

**Acceptance Criteria:**
- All API contracts match frontend expectations
- Error handling is correct
- API versioning works

---

#### Test 7.2: WebSocket Streaming

**File:** `tests/e2e/frontend/test_websocket_streaming.py`

**Tests:**
- ✅ WebSocket connection
- ✅ Execution state streaming
- ✅ Real-time updates
- ✅ Disconnection handling
- ✅ Reconnection handling
- ✅ Error handling
- ✅ Multi-client support

**Acceptance Criteria:**
- WebSocket streaming works correctly
- Real-time updates are delivered
- Disconnection/reconnection works

---

#### Test 7.3: Authentication Integration

**File:** `tests/e2e/frontend/test_authentication.py`

**Tests:**
- ✅ User registration
- ✅ User login
- ✅ Token refresh
- ✅ Session management
- ✅ Authorization (role-based access)
- ✅ Multi-tenant authentication
- ✅ Error handling (invalid credentials, expired tokens)

**Acceptance Criteria:**
- Authentication works correctly
- Authorization works correctly
- Multi-tenant authentication works

---

#### Test 7.4: Frontend E2E

**File:** `tests/e2e/frontend/test_frontend_e2e.py`

**Tests:**
- ✅ Complete user journey (login → upload → parse → analyze)
- ✅ All pillars work from frontend
- ✅ Chat interface works from frontend
- ✅ Admin dashboard works from frontend
- ✅ Error handling (network failures, API errors)
- ✅ Performance (page load, API response times)

**Acceptance Criteria:**
- Frontend E2E works correctly
- All features are accessible from frontend
- Performance is acceptable

---

### Phase 8: Platform Stability (Week 2, Days 6-7)

#### Test 8.1: Error Handling

**File:** `tests/e2e/stability/test_error_handling.py`

**Tests:**
- ✅ Infrastructure failures (Redis, ArangoDB, GCS)
- ✅ Service failures (Runtime, Experience, Realms)
- ✅ Invalid input handling
- ✅ Timeout handling
- ✅ Rate limiting
- ✅ Error propagation
- ✅ Error logging
- ✅ User-friendly error messages

**Acceptance Criteria:**
- Error handling is graceful
- Errors are logged correctly
- User-friendly error messages
- No crashes or data loss

---

#### Test 8.2: Recovery

**File:** `tests/e2e/stability/test_recovery.py`

**Tests:**
- ✅ Service restart recovery
- ✅ Infrastructure restart recovery
- ✅ Partial failure recovery
- ✅ Data consistency after recovery
- ✅ Execution replay (from WAL)
- ✅ State recovery
- ✅ Saga compensation

**Acceptance Criteria:**
- Recovery works correctly
- Data consistency is maintained
- Execution can be replayed
- No data loss

---

#### Test 8.3: Performance

**File:** `tests/e2e/stability/test_performance.py`

**Tests:**
- ✅ API response times (< 200ms for simple operations)
- ✅ File parsing performance (< 5s for 1MB file)
- ✅ Concurrent execution (100+ concurrent intents)
- ✅ Memory usage (reasonable for workload)
- ✅ Database query performance
- ✅ Graph operation performance
- ✅ Load testing (1000+ requests)

**Acceptance Criteria:**
- Performance is acceptable
- No memory leaks
- Concurrent execution works
- Load testing passes

---

## Part 4: Test Execution Strategy

### Test Execution Order

1. **Infrastructure Tests** (Phase 1) - Must pass first
2. **Runtime Integration Tests** (Phase 2) - Depends on Phase 1
3. **Realm Integration Tests** (Phase 3) - Depends on Phase 2
4. **Architectural Compliance Tests** (Phase 4) - Depends on Phase 3
5. **Functional Compliance Tests** (Phase 5) - Depends on Phase 4
6. **Extensibility Vision Tests** (Phase 6) - Depends on Phase 5
7. **Frontend Integration Tests** (Phase 7) - Depends on Phase 5
8. **Platform Stability Tests** (Phase 8) - Depends on all previous phases

### Test Execution Commands

```bash
# Phase 1: Infrastructure Tests
pytest tests/integration/infrastructure/ -v -m infrastructure

# Phase 2: Runtime Integration Tests
pytest tests/integration/runtime/ -v -m runtime

# Phase 3: Realm Integration Tests
pytest tests/integration/realms/ -v -m realms

# Phase 4: Architectural Compliance Tests
pytest tests/e2e/architectural/ -v -m architectural

# Phase 5: Functional Compliance Tests
pytest tests/e2e/functional/ -v -m functional

# Phase 6: Extensibility Vision Tests
pytest tests/e2e/extensibility/ -v -m extensibility

# Phase 7: Frontend Integration Tests
pytest tests/e2e/frontend/ -v -m frontend

# Phase 8: Platform Stability Tests
pytest tests/e2e/stability/ -v -m stability

# All Tests
pytest tests/ -v
```

---

## Part 5: CI/CD Integration

### GitHub Actions Workflow

**File:** `.github/workflows/comprehensive_testing.yml`

```yaml
name: Comprehensive Testing

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  infrastructure-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Start test infrastructure
        run: docker-compose -f docker-compose.test.yml up -d redis arango
      - name: Wait for services
        run: sleep 30
      - name: Run infrastructure tests
        run: pytest tests/integration/infrastructure/ -v
      - name: Cleanup
        run: docker-compose -f docker-compose.test.yml down -v

  runtime-tests:
    runs-on: ubuntu-latest
    needs: infrastructure-tests
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Start test infrastructure
        run: docker-compose -f docker-compose.test.yml up -d
      - name: Wait for services
        run: sleep 60
      - name: Run runtime tests
        run: pytest tests/integration/runtime/ -v
      - name: Cleanup
        run: docker-compose -f docker-compose.test.yml down -v

  e2e-tests:
    runs-on: ubuntu-latest
    needs: runtime-tests
    if: github.ref == 'refs/heads/main' || github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Start full stack
        run: docker-compose -f docker-compose.test.yml up -d
      - name: Wait for services
        run: sleep 120
      - name: Run E2E tests
        run: pytest tests/e2e/ -v
      - name: Cleanup
        run: docker-compose -f docker-compose.test.yml down -v
```

---

## Part 6: Success Criteria

### Infrastructure Foundation (Phase 1)
- ✅ All infrastructure adapters work with real services
- ✅ StateAbstraction hot/cold pattern works
- ✅ DataBrain persistence works
- ✅ Event publishing works
- ✅ All tests pass reliably

### Runtime Integration (Phase 2)
- ✅ Runtime initializes correctly
- ✅ Execution lifecycle works
- ✅ State Surface works
- ✅ All tests pass reliably

### Realm Integration (Phase 3)
- ✅ All realms work end-to-end
- ✅ All intents are handled correctly
- ✅ All tests pass reliably

### Architectural Compliance (Phase 4)
- ✅ 5-layer architecture is followed
- ✅ Public Works pattern is followed
- ✅ Runtime Participation Contract is followed
- ✅ No architectural violations

### Functional Compliance (Phase 5)
- ✅ MVP showcase use case works
- ✅ All pillars work correctly
- ✅ Chat interface works
- ✅ Admin dashboard works

### Extensibility Vision (Phase 6)
- ✅ Platform handles 350k policies
- ✅ Legacy system migration works
- ✅ Multi-tenant isolation works

### Frontend Integration (Phase 7)
- ✅ All API contracts match frontend
- ✅ WebSocket streaming works
- ✅ Authentication works
- ✅ Frontend E2E works

### Platform Stability (Phase 8)
- ✅ Error handling is graceful
- ✅ Recovery works correctly
- ✅ Performance is acceptable

---

## Part 7: Timeline

### Week 1: Infrastructure & Core Integration
- **Days 1-2:** Infrastructure tests (ArangoDB, Redis, State, DataBrain, Events)
- **Days 3-4:** Runtime integration tests
- **Days 4-5:** Realm integration tests

### Week 2: Compliance & Validation
- **Days 1-2:** Architectural compliance tests
- **Days 3-4:** Functional compliance tests (MVP showcase)
- **Days 4-5:** Extensibility vision tests
- **Days 5-6:** Frontend integration tests
- **Days 6-7:** Platform stability tests

### Week 3: Fixes & Documentation
- **Days 1-3:** Fix issues found in testing
- **Days 4-5:** Re-run all tests
- **Days 5-7:** Document what works

---

## Part 8: Next Steps

1. **Create docker-compose.test.yml** (Task 1.1)
2. **Create test infrastructure utilities** (Task 1.2)
3. **Implement Phase 1 tests** (Infrastructure foundation)
4. **Run Phase 1 tests and fix issues**
5. **Continue with subsequent phases**
6. **Document what works**

---

**Remember:** The goal is to validate the foundation before documenting. Test first, document what works.
