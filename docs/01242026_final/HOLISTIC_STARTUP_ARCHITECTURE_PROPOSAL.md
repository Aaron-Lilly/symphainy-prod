# Holistic Startup Architecture Proposal

**Date:** January 26, 2026  
**Status:** ✅ **CTO VALIDATED - REFINED IMPLEMENTATION**  
**Context:** Platform needs proper service wiring and dependency injection

**CTO Feedback:** ✅ Directionally correct. Refinement: Separate service graph creation from FastAPI app creation.

---

## Executive Summary

The platform currently has a **disconnect** between:
- **Service implementations** (ExecutionLifecycleManager, StateSurface, PublicWorksFoundationService, etc.)
- **API route registration** (runtime_api.py creates routes but they're not wired into main.py)
- **Container startup** (Dockerfile references `runtime_main.py` which doesn't exist)

**Proposed Solution:** A **holistic startup architecture** that:
1. Maintains lightweight `main.py` (as intended)
2. Creates a **service initialization module** that wires dependencies
3. Follows **Option C (Fully Hosted)** deployment pattern from hybrid cloud strategy
4. Supports **containerized, modular architecture** ready for GKE/Cloud Run

---

## Current State Analysis

### What We Have ✅
- ✅ Service implementations (ExecutionLifecycleManager, StateSurface, PublicWorksFoundationService)
- ✅ API route definitions (runtime_api.py with `create_runtime_app()`)
- ✅ Docker Compose orchestration (startup.sh)
- ✅ Foundation service with 5-layer architecture
- ✅ Dependency injection pattern in PublicWorksFoundationService

### What's Missing ❌
- ❌ Service initialization/wiring logic
- ❌ Dependency injection container setup
- ❌ Route registration in main.py
- ❌ `runtime_main.py` (referenced in Dockerfile but doesn't exist)
- ❌ Proper service lifecycle management

---

## Proposed Architecture

### Three-Layer Startup Pattern (CTO-Refined)

**Key Insight:** Separate service graph creation from FastAPI app creation.

```
┌─────────────────────────────────────────┐
│  Layer 1: runtime_main.py (Entry)      │
│  - Load config                          │
│  - Call create_runtime_services()        │
│  - Call create_fastapi_app(services)    │
│  - Start uvicorn                        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Layer 2: create_runtime_services()    │
│  - Build object graph                   │
│  - Initialize PublicWorksFoundation     │
│  - Create ExecutionLifecycleManager     │
│  - Create StateSurface                 │
│  - Wire RegistryAbstraction             │
│  - Return RuntimeServices object        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Layer 3: create_fastapi_app(services) │
│  - Receives RuntimeServices             │
│  - Registers all API routes             │
│  - Configures middleware                │
│  - Returns FastAPI app instance         │
└─────────────────────────────────────────┘
```

**Benefits:**
- ✅ Testable services without FastAPI
- ✅ FastAPI without infrastructure
- ✅ Zero circular imports
- ✅ Clear ownership boundaries

---

## Implementation Plan (CTO-Refined)

### Step 1: Create RuntimeServices Object

**File:** `symphainy_platform/runtime/runtime_services.py`

**Purpose:** Container for all long-lived runtime services

**Pattern:**
```python
@dataclass
class RuntimeServices:
    """Container for all long-lived runtime services."""
    public_works: PublicWorksFoundationService
    state_surface: StateSurface
    execution_lifecycle_manager: ExecutionLifecycleManager
    registry_abstraction: RegistryAbstraction
    artifact_storage: ArtifactStorageAbstraction
    file_storage: FileStorageAbstraction
    # ... other services
```

**Why:** Makes ownership explicit and testable.

---

### Step 2: Create Service Factory (Separated)

**File:** `symphainy_platform/runtime/service_factory.py`

**Purpose:** Build object graph (separate from FastAPI)

**Key Functions:**

```python
def create_runtime_services(config: Dict[str, Any]) -> RuntimeServices:
    """
    Build the runtime object graph.
    
    Initialization Order:
    1. PublicWorksFoundationService (infrastructure layer)
    2. StateSurface (with ArtifactRegistry)
    3. ExecutionLifecycleManager (with StateSurface, WAL, etc.)
    4. RegistryAbstraction (from PublicWorksFoundationService)
    
    Returns: RuntimeServices object with all services
    """
    # ... wiring logic ...
    return RuntimeServices(...)

def create_fastapi_app(services: RuntimeServices) -> FastAPI:
    """
    Create FastAPI app with routes (receives services, doesn't create them).
    
    Args:
        services: RuntimeServices object with all dependencies
    
    Returns: Configured FastAPI app
    """
    from .runtime_api import create_runtime_app
    return create_runtime_app(
        execution_lifecycle_manager=services.execution_lifecycle_manager,
        state_surface=services.state_surface,
        registry_abstraction=services.registry_abstraction,
        artifact_storage=services.artifact_storage,
        file_storage=services.file_storage
    )
```

**Key Principle:** Services are created once, FastAPI receives them.

---

### Step 3: Create runtime_main.py (Entry Point)

**File:** `runtime_main.py`

**Purpose:** Process entry point (non-negotiable, must be boring)

**Pattern:**
```python
#!/usr/bin/env python3
"""Runtime service entry point - one function call, zero logic."""

from symphainy_platform.runtime.service_factory import (
    create_runtime_services,
    create_fastapi_app
)
from symphainy_platform.config import get_env_contract
import uvicorn

def main():
    """Entry point: load config → create services → create app → start server."""
    config = get_env_contract()
    
    # Build object graph
    services = create_runtime_services(config)
    
    # Create FastAPI app (receives services, doesn't create them)
    app = create_fastapi_app(services)
    
    # Start server
    uvicorn.run(app, host="0.0.0.0", port=config.RUNTIME_PORT)

if __name__ == "__main__":
    main()
```

**Rule:** If you can't explain the entry point in one sentence, it's wrong.

---

### Step 4: Update main.py (Optional - for local dev)

**File:** `main.py`

**Changes:**
- Can call `runtime_main.main()` or duplicate the pattern
- Keep it minimal (< 50 lines)

---

### Step 4: Service Initialization Sequence

**Critical Order:**
1. **Infrastructure Adapters** (Redis, Arango, Supabase, GCS, etc.)
2. **PublicWorksFoundationService** (wires all adapters → abstractions)
3. **StateSurface** (with ArtifactRegistry)
4. **WriteAheadLog** (for audit trail)
5. **ExecutionLifecycleManager** (with StateSurface, WAL, IntentRegistry)
6. **RegistryAbstraction** (from PublicWorksFoundationService)
7. **FastAPI App** (with all routes)

---

## Detailed Service Factory Implementation

### PublicWorksFoundationService Initialization

```python
# Initialize Public Works Foundation Service
public_works = PublicWorksFoundationService(config=config)

# Initialize adapters (Layer 0)
public_works.initialize_adapters()

# Initialize abstractions (Layer 1)
public_works.initialize_abstractions()

# Get RegistryAbstraction for artifact/index queries
registry_abstraction = public_works.registry_abstraction
```

### StateSurface Initialization

```python
# Create StateSurface with ArtifactRegistry
state_surface = StateSurface(
    redis_adapter=public_works.redis_adapter,
    # ... other dependencies
)

# ArtifactRegistry is created inside StateSurface.__init__
```

### ExecutionLifecycleManager Initialization

```python
# Create IntentRegistry
intent_registry = IntentRegistry()

# Register intent handlers (from realms)
# ... register handlers ...

# Create WriteAheadLog
wal = WriteAheadLog(
    redis_adapter=public_works.redis_adapter
)

# Create ExecutionLifecycleManager
execution_lifecycle_manager = ExecutionLifecycleManager(
    intent_registry=intent_registry,
    state_surface=state_surface,
    wal=wal,
    artifact_storage=public_works.artifact_storage_abstraction,
    # ... other dependencies
)
```

### FastAPI App Creation

```python
# Create FastAPI app with all routes
app = create_runtime_app(
    execution_lifecycle_manager=execution_lifecycle_manager,
    state_surface=state_surface,
    registry_abstraction=registry_abstraction,
    artifact_storage=public_works.artifact_storage_abstraction,
    file_storage=public_works.file_storage_abstraction
)
```

---

## Alignment with Hybrid Cloud Strategy (Option C)

### Deployment Model

**Current (MVP):**
- All services in Docker Compose
- Single VM or local development

**Target (Option C - Fully Hosted):**
- **Data Plane:** Supabase Cloud, MemoryStore (Redis), ArangoDB Oasis
- **Control Plane:** GKE StatefulSets (Curator, DI Container, Telemetry)
- **Execution Plane:** Cloud Run (Realms, APIs, Frontend)
- **Service Plane:** Hugging Face Inference API, OpenAI, Anthropic

### Service Factory Benefits

1. **Container-Ready:** Services initialized in containers
2. **Cloud-Native:** Adapters can point to managed services
3. **Modular:** Each service can be deployed independently
4. **Testable:** Factory function can be tested in isolation
5. **Scalable:** Services can be split across containers later

---

## File Structure

```
symphainy_platform/
├── runtime/
│   ├── service_factory.py      # NEW: Dependency injection & wiring
│   ├── runtime_api.py          # EXISTING: Route definitions
│   ├── execution_lifecycle_manager.py
│   ├── state_surface.py
│   └── ...
├── foundations/
│   └── public_works/
│       └── foundation_service.py
└── ...

main.py                          # UPDATED: Calls service_factory
runtime_main.py                  # NEW: Container entry point
```

---

## Benefits

### 1. Maintains Lightweight main.py ✅
- `main.py` stays < 50 lines
- All complexity in `service_factory.py`

### 2. Proper Dependency Injection ✅
- Centralized wiring logic
- Clear initialization order
- Easy to test and mock

### 3. Container-Ready ✅
- Works with Docker Compose
- Ready for GKE/Cloud Run
- Follows Option C deployment pattern

### 4. Modular & Scalable ✅
- Services can be split later
- Adapters can point to managed services
- Supports hybrid cloud migration

### 5. Testable ✅
- Factory function can be tested
- Services can be mocked
- Integration tests can use factory

---

## Migration Path

### Phase 1: Create Service Factory (Immediate)
1. Create `service_factory.py`
2. Wire PublicWorksFoundationService
3. Wire StateSurface
4. Wire ExecutionLifecycleManager
5. Wire RegistryAbstraction
6. Return configured FastAPI app

### Phase 2: Update Entry Points
1. Update `main.py` to use service factory
2. Create `runtime_main.py` for Docker
3. Verify Docker container starts

### Phase 3: Test & Validate
1. Run integration tests
2. Verify all API routes work
3. Test artifact listing/resolution
4. Test pending intents

### Phase 4: Document & Refine
1. Document initialization order
2. Add error handling
3. Add health checks
4. Add graceful shutdown

---

## Questions for CIO/CTO Review

1. **Service Factory Pattern:** Does this approach align with your vision for dependency injection?

2. **Initialization Order:** Is the proposed sequence correct? (Infrastructure → Foundation → Runtime → API)

3. **Container Strategy:** Should we support both `main.py` (local) and `runtime_main.py` (container), or consolidate?

4. **Error Handling:** How should we handle initialization failures? (Fail fast? Retry? Fallback?)

5. **Configuration:** Should configuration come from environment variables, config files, or both?

6. **Testing:** Should the service factory be testable in isolation, or only via integration tests?

---

## Implementation Status

### ✅ Completed

1. **RuntimeServices object** - Created (`runtime_services.py`)
2. **Service factory** - Created (`service_factory.py`)
   - `create_runtime_services()` - Builds object graph
   - `create_fastapi_app()` - Creates FastAPI app (receives services)
3. **Runtime entry point** - Created (`runtime_main.py`)
   - Loads config
   - Creates services
   - Creates app
   - Starts server
4. **Runtime lifecycle diagram** - Created (`RUNTIME_LIFECYCLE_DIAGRAM.md`)

### ⏳ Remaining

1. **Update Dockerfile.runtime** - Point to `runtime_main.py` (already correct)
2. **Register intent handlers** - Explicitly register handlers in `create_runtime_services()`
3. **Test end-to-end** - Verify all routes work
4. **Update main.py** - Optionally call `runtime_main.main()` for local dev

---

## Status

**Proposal:** ✅ **CTO VALIDATED**

**Implementation:** ✅ **COMPLETE** (ready for testing)

**Guardrails:** ✅ **DOCUMENTED** (four red flags)

**Next:** Test and validate end-to-end
