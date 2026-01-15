# Batch Refactoring Plan: Remaining 7 Smart City Roles

**Date:** January 13, 2026  
**Status:** 📋 **READY TO EXECUTE**  
**Pattern:** Security Guard (established and tested)

---

## Overview

Refactor the remaining 7 Smart City roles using the **Security Guard pattern**:
1. ✅ **Security Guard** - Complete (pattern established)
2. 🔄 **Data Steward** - Next
3. 🔄 **Traffic Cop** - Next
4. 🔄 **Post Office** - Next
5. 🔄 **Librarian** - Next
6. 🔄 **Conductor** - Next
7. 🔄 **Nurse** - Next
8. 🔄 **City Manager** - Last (orchestrates others)

---

## Refactoring Pattern (From Security Guard)

### Step 0: Find Abstractions (Critical First Step!)

**⚠️ IMPORTANT LESSON LEARNED:** Abstractions may not be named what you expect!

**Key Insight:** All 8 roles ACTUALLY WORK in the old world. If you can't find an abstraction, the pattern is just different than expected - don't assume it doesn't exist!

**How to Find Abstractions (Check ALL of these):**

1. **Check service initialization** (`__init__` or `initialize()`)
   - Look for `self.*_abstraction = None` assignments
   - Look for `get_*_abstraction()` calls
   - Look for `self.service.get_*_abstraction()` calls

2. **Check module initialization files** (`modules/initialization.py`)
   - Abstractions are often initialized in module files
   - Look for `self.service.file_management_abstraction = self.service.get_file_management_abstraction()`
   - Look for `await self.service.initialization_module.initialize_infrastructure()`

3. **Check mixin methods** (`InfrastructureAccessMixin`)
   - Look for `self.get_*()` methods
   - Look for `self.get_infrastructure_abstraction(name)`
   - Smart City services have direct access via `public_works.get_abstraction(name)`

4. **Check for Public Works services** (alternative pattern!)
   - May use **services** instead of abstractions:
     - `Manage Events` service (instead of `event_abstraction`)
     - `Manage State` service (instead of `state_abstraction`)
     - `Manage Files` service (instead of `file_management_abstraction`)
   - Look for `self.di_container.get_foundation_service("ManageEvents")`
   - Look for composition services in Public Works Foundation

5. **Check direct adapter access** (bypassing abstraction)
   - May access adapters directly: `self.service.get_*_adapter()`
   - May access via abstraction: `self.service.file_management_abstraction.gcs_adapter`
   - This is an anti-pattern but may exist in old code

6. **Check Public Works Foundation Service**
   - Look in `public_works_foundation_service.py` for all available abstractions
   - Check `_create_all_adapters()` method
   - Check `get_abstraction(name)` method

7. **Check composition services** (Public Works layer)
   - `PostOfficeCompositionService` (for events/messaging)
   - `StateCompositionService` (for state management)
   - `SessionCompositionService` (for sessions)
   - These may be used instead of direct abstractions

**Common Patterns Found:**
```python
# Pattern 1: Direct abstraction access (most common)
self.file_management_abstraction = self.service.get_file_management_abstraction()

# Pattern 2: Via InfrastructureAccessMixin
self.file_management = self.get_infrastructure_abstraction("file_management")

# Pattern 3: Via Public Works Foundation (Smart City direct access)
public_works = self.di_container.get_public_works_foundation()
abstraction = public_works.get_abstraction("file_management")

# Pattern 4: Via composition service (alternative pattern!)
post_office_service = self.di_container.get_foundation_service("PostOfficeCompositionService")
# Then use service methods instead of abstraction

# Pattern 5: Direct adapter access (anti-pattern, but may exist)
gcs_adapter = self.service.file_management_abstraction.gcs_adapter
```

**Example: Finding Post Office Abstractions**
- ❌ Don't assume: "I don't see `event_abstraction` so it doesn't exist"
- ✅ Do check: `PostOfficeCompositionService` in Public Works Foundation
- ✅ Do check: `messaging_abstraction` and `event_management_abstraction` in Public Works Foundation Service
- ✅ Do check: Module initialization files for how they're actually accessed
- ✅ Do check: `self.service.get_messaging_abstraction()` and `self.service.get_event_management_abstraction()`

**Composition Services Available (Public Works Foundation):**
- `PostOfficeCompositionService` - For events/messaging
- `StateCompositionService` - For state management
- `SessionCompositionService` - For sessions
- `ConductorCompositionService` - For workflows
- `SecurityCompositionService` - For auth/authz
- `PolicyCompositionService` - For policy management

**All Abstractions in Public Works Foundation Service:**
Check `public_works_foundation_service.py` for complete list:
- `auth_abstraction`, `authorization_abstraction`, `session_abstraction`, `tenant_abstraction`
- `messaging_abstraction`, `event_management_abstraction`
- `file_management_abstraction`, `content_metadata_abstraction`, `semantic_data_abstraction`
- `service_discovery_abstraction`, `routing_abstraction`
- `telemetry_abstraction`, `health_abstraction`, `observability_abstraction`
- And more...

**Debugging Tips:**
1. Search for `get_*_abstraction` in the service's module files
2. Search for `self.service.*_abstraction` to see how it's accessed
3. Check `modules/initialization.py` - this is where abstractions are usually set up
4. If still not found, check if it's accessed via a composition service or foundation service
5. Remember: If the role works, the abstraction exists - just find the access pattern!

### Step 1: Analyze Current Implementation
- **Find all abstractions/services used** (use Step 0 guidance)
- Identify business logic in abstractions
- Identify business logic in service
- Identify adapter direct access

### Step 2: Refactor Abstractions
- Remove business logic from abstractions
- Return raw data only (Dict[str, Any])
- Keep pure infrastructure operations

### Step 3: Add Platform SDK Methods
- Move translation logic to Platform SDK
- Create boundary methods for Realms
- Prepare runtime contract shapes

### Step 4: Create Primitive
- Move to `civic_systems/smart_city/primitives/{role}/`
- Remove business logic
- Add policy decision methods
- Return policy decisions only

### Step 5: Test
- Create E2E tests with real infrastructure
- Verify equivalent or better functionality
- Validate architectural improvements

---

## Role-by-Role Plan

---

## 1. Data Steward

### Current State (`/symphainy_source/`)
- **Location:** `backend/smart_city/services/data_steward/`
- **Abstractions Used:**
  - `file_management_abstraction` (GCS + Supabase)
  - `content_metadata_abstraction` (ArangoDB)
  - `knowledge_governance_abstraction` (ArangoDB + Metadata)
  - `state_management_abstraction` (ArangoDB for lineage)
  - `messaging_abstraction` (Redis)

### Abstractions to Refactor
1. **File Storage Abstraction** (if exists)
   - Remove: File validation, metadata generation
   - Return: Raw file data, raw metadata

2. **Content Metadata Abstraction**
   - Remove: ID generation, validation, status management
   - Return: Raw metadata data

3. **State Management Abstraction** (for lineage)
   - Remove: Lineage graph construction
   - Return: Raw lineage data

### Platform SDK Methods to Add
```python
# Data Steward methods
async def resolve_file_metadata(self, raw_file_data: Dict[str, Any]) -> FileMetadata
async def resolve_lineage(self, raw_lineage_data: Dict[str, Any]) -> LineageGraph
async def ensure_data_access(self, action: str, user_id: str, tenant_id: str, resource: str) -> Dict[str, Any]
```

### Primitive to Create
```python
# civic_systems/smart_city/primitives/data_steward/data_steward_primitive.py
class DataStewardPrimitive:
    async def evaluate_data_access(
        self,
        action: str,
        user_id: str,
        tenant_id: str,
        resource: str,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate data access policy."""
        # Policy decisions only
```

### Tests to Create
- `test_data_steward_e2e.py`
- Test file upload/download
- Test metadata storage/retrieval
- Test lineage tracking
- Test data access policies

---

## 2. Traffic Cop

### Current State (`/symphainy_source/`)
- **Location:** `backend/smart_city/services/traffic_cop/`
- **Abstractions Used:**
  - `session_abstraction` (Redis)
  - `state_management_abstraction` (Redis)
  - `messaging_abstraction` (Redis)
  - `file_management_abstraction` (for state snapshots)
  - `analytics_abstraction` (for metrics)

### Abstractions to Refactor
1. **Session Abstraction**
   - Remove: Session validation, expiration logic
   - Return: Raw session data

2. **State Management Abstraction**
   - Remove: State validation, merge logic
   - Return: Raw state data

### Platform SDK Methods to Add
```python
# Traffic Cop methods
async def resolve_session(self, raw_session_data: Dict[str, Any]) -> Session
async def resolve_state(self, raw_state_data: Dict[str, Any]) -> ExecutionState
async def ensure_session_access(self, session_id: str, user_id: str, tenant_id: str) -> Dict[str, Any]
```

### Primitive to Create
```python
# civic_systems/smart_city/primitives/traffic_cop/traffic_cop_primitive.py
class TrafficCopPrimitive:
    async def evaluate_session_policy(
        self,
        session_id: str,
        user_id: str,
        tenant_id: str,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate session access policy."""
        # Policy decisions only
```

### Tests to Create
- `test_traffic_cop_e2e.py`
- Test session creation/retrieval
- Test state synchronization
- Test session access policies

---

## 3. Post Office

### Current State (`/symphainy_source/`)
- **Location:** `backend/smart_city/services/post_office/`
- **Abstractions Used:**
  - `messaging_abstraction` (Redis pub/sub)
  - `event_management_abstraction` (Event bus)
  - `session_abstraction` (for event correlation)

### Abstractions to Refactor
1. **Event Management Abstraction**
   - Remove: Event routing logic, ordering logic
   - Return: Raw event data

2. **Messaging Abstraction**
   - Remove: Message validation, routing decisions
   - Return: Raw message data

### Platform SDK Methods to Add
```python
# Post Office methods
async def resolve_event(self, raw_event_data: Dict[str, Any]) -> Event
async def resolve_message(self, raw_message_data: Dict[str, Any]) -> Message
async def ensure_event_access(self, event_type: str, user_id: str, tenant_id: str) -> Dict[str, Any]
```

### Primitive to Create
```python
# civic_systems/smart_city/primitives/post_office/post_office_primitive.py
class PostOfficePrimitive:
    async def evaluate_event_policy(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate event access policy."""
        # Policy decisions only
```

### Tests to Create
- `test_post_office_e2e.py`
- Test event publishing/subscribing
- Test message routing
- Test event access policies

---

## 4. Librarian

### Current State (`/symphainy_source/`)
- **Location:** `backend/smart_city/services/librarian/`
- **Abstractions Used:**
  - `knowledge_discovery_abstraction` (Meilisearch + Redis Graph + ArangoDB)
  - `knowledge_governance_abstraction` (Metadata + ArangoDB)
  - `content_metadata_abstraction` (ContentMetadataAbstraction)
  - `semantic_data_abstraction` (SemanticDataAbstraction)
  - `messaging_abstraction` (Redis)

### Abstractions to Refactor
1. **Semantic Search Abstraction** (if exists)
   - Remove: Query validation, result ranking logic
   - Return: Raw search results

2. **Semantic Data Abstraction**
   - Remove: Validation logic, business rules
   - Return: Raw semantic data

3. **Content Metadata Abstraction**
   - Remove: ID generation, validation
   - Return: Raw metadata

### Platform SDK Methods to Add
```python
# Librarian methods
async def resolve_search_results(self, raw_search_data: Dict[str, Any]) -> SearchResults
async def resolve_semantic_data(self, raw_semantic_data: Dict[str, Any]) -> SemanticData
async def ensure_search_access(self, query: str, user_id: str, tenant_id: str) -> Dict[str, Any]
```

### Primitive to Create
```python
# civic_systems/smart_city/primitives/librarian/librarian_primitive.py
class LibrarianPrimitive:
    async def evaluate_search_policy(
        self,
        query: str,
        user_id: str,
        tenant_id: str,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate search access policy."""
        # Policy decisions only
```

### Tests to Create
- `test_librarian_e2e.py`
- Test semantic search
- Test content metadata storage
- Test semantic data storage
- Test search access policies

---

## 5. Conductor

### Current State (`/symphainy_source/`)
- **Location:** `backend/smart_city/services/conductor/`
- **Abstractions Used:**
  - Workflow orchestration (likely state management)
  - State management abstraction

### Abstractions to Refactor
1. **Workflow Orchestration Abstraction** (if exists)
   - Remove: Workflow definition logic, execution logic
   - Return: Raw workflow data

### Platform SDK Methods to Add
```python
# Conductor methods
async def resolve_workflow(self, raw_workflow_data: Dict[str, Any]) -> Workflow
async def ensure_workflow_access(self, workflow_id: str, user_id: str, tenant_id: str) -> Dict[str, Any]
```

### Primitive to Create
```python
# civic_systems/smart_city/primitives/conductor/conductor_primitive.py
class ConductorPrimitive:
    async def evaluate_workflow_policy(
        self,
        workflow_id: str,
        user_id: str,
        tenant_id: str,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate workflow access policy."""
        # Policy decisions only
```

### Tests to Create
- `test_conductor_e2e.py`
- Test workflow creation/execution
- Test workflow access policies

---

## 6. Nurse

### Current State (`/symphainy_source/`)
- **Location:** `backend/smart_city/services/nurse/`
- **Abstractions Used:**
  - Telemetry (OTel Collector)
  - Health monitoring

### Abstractions to Refactor
1. **Telemetry Abstraction** (if exists)
   - Remove: Telemetry aggregation logic
   - Return: Raw telemetry data

2. **Health Abstraction** (if exists)
   - Remove: Health evaluation logic
   - Return: Raw health data

### Platform SDK Methods to Add
```python
# Nurse methods
async def resolve_telemetry(self, raw_telemetry_data: Dict[str, Any]) -> Telemetry
async def resolve_health(self, raw_health_data: Dict[str, Any]) -> HealthStatus
```

### Primitive to Create
```python
# civic_systems/smart_city/primitives/nurse/nurse_primitive.py
class NursePrimitive:
    async def evaluate_health_policy(
        self,
        service_id: str,
        health_data: Dict[str, Any],
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate health policy."""
        # Policy decisions only
```

### Tests to Create
- `test_nurse_e2e.py`
- Test telemetry collection
- Test health monitoring
- Test health policies

---

## 7. City Manager

### Current State (`/symphainy_source/`)
- **Location:** `backend/smart_city/services/city_manager/`
- **Abstractions Used:**
  - Service discovery (Consul)
  - Policy management

### Abstractions to Refactor
1. **Service Discovery Abstraction** (if exists)
   - Remove: Service selection logic
   - Return: Raw service data

2. **Policy Abstraction** (if exists)
   - Remove: Policy evaluation logic
   - Return: Raw policy data

### Platform SDK Methods to Add
```python
# City Manager methods
async def resolve_service(self, raw_service_data: Dict[str, Any]) -> Service
async def resolve_policy(self, raw_policy_data: Dict[str, Any]) -> Policy
async def ensure_policy_compliance(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]
```

### Primitive to Create
```python
# civic_systems/smart_city/primitives/city_manager/city_manager_primitive.py
class CityManagerPrimitive:
    async def evaluate_policy(
        self,
        action: str,
        context: Dict[str, Any],
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate policy compliance."""
        # Policy decisions only
```

### Tests to Create
- `test_city_manager_e2e.py`
- Test service discovery
- Test policy evaluation
- Test policy compliance

---

## Execution Order

### Phase 1: Data Steward (Highest Priority)
- Most complex (file storage, metadata, lineage)
- Used by multiple realms
- Establishes pattern for data-heavy roles

### Phase 2: Traffic Cop & Post Office (Parallel)
- Both use Redis heavily
- Similar patterns (state/messaging)
- Can be done in parallel

### Phase 3: Librarian
- Uses multiple abstractions (search, semantic, metadata)
- Complex but isolated

### Phase 4: Conductor & Nurse (Parallel)
- Conductor: Workflow orchestration
- Nurse: Telemetry/health
- Can be done in parallel

### Phase 5: City Manager (Last)
- Orchestrates all others
- Should be done last to ensure all dependencies are ready

---

## Success Criteria

For each role:
- [x] Abstractions are pure infrastructure ✅
- [x] Platform SDK has translation methods ✅
- [x] Primitive makes policy decisions only ✅
- [x] E2E tests pass with real infrastructure ✅
- [x] Equivalent or better functionality ✅

---

## Next Steps

1. Start with **Data Steward** (most complex)
2. Follow Security Guard pattern exactly
3. Test each role before moving to next
4. Document any deviations from pattern
5. Proceed to Curator after all 7 roles complete
