# Curator Refactoring & Evolution Plan

**Date:** January 2026  
**Status:** 📋 **COMPREHENSIVE PLAN**  
**Goal:** Evolve Curator from Foundation (wrapping Consul) to Smart City role (governance + registries)

---

## Executive Summary

### Current State (symphainy_source)
- ❌ Curator is a **Foundation** (infrastructure layer)
- ❌ Wraps Consul directly (bastardized service mesh pattern)
- ❌ Tries to expose all platform capabilities (services, agents, MCP tools)
- ❌ Over-estimation of what service mesh provides
- ❌ Services register with Curator → Curator registers with Consul
- ❌ Runtime likely calls Curator directly (or via DI container)

### Future State (Target Architecture)
- ✅ Curator is a **Smart City role** (governance, not infrastructure)
- ✅ Owns **registries** (Supabase-backed, data-backed catalogs)
- ✅ Exposes **SDK** (not SOA APIs) - avoids circularity
- ✅ **Uses/reads Consul** (doesn't become it)
- ✅ Services still register with **Consul** (infrastructure layer)
- ✅ Runtime asks **Curator** (not Consul directly)
- ✅ Three distinct concepts separated:
  - **Service Mesh** (Consul/Istio) = Infrastructure, liveness
  - **Capability Registry** (Supabase) = Governance, meaning
  - **Runtime Registry View** (ephemeral) = Execution truth

---

## Part 1: Architectural Analysis

### 1.1 Current Curator Implementation Analysis

**Location in `/symphainy_source/`:**
- `foundations/curator_foundation/curator_foundation_service.py`
- `foundations/curator_foundation/infrastructure_adapters/consul_adapter.py`
- `foundations/curator_foundation/infrastructure_abstractions/service_registration_abstraction.py`
- `foundations/curator_foundation/services/capability_registry_service.py`

**Current Responsibilities (Too Many):**
1. Service registration (Consul)
2. Service discovery (Consul)
3. Capability registry (in-memory)
4. Agent capability registry (in-memory)
5. MCP tool registry (in-memory)
6. SOA API registry (in-memory)
7. Pattern validation
8. Anti-pattern detection
9. Documentation generation

**Problems:**
- ❌ Mixing infrastructure (Consul) with governance (capabilities)
- ❌ In-memory registries (lost on restart)
- ❌ No separation between "what exists" (Consul) and "what it means" (Curator)
- ❌ Circular dependencies (Curator registers itself)
- ❌ Runtime can't distinguish between liveness and capability

---

### 1.2 Three Distinct Concepts (The Unlock)

#### 1️⃣ Service Mesh (Infrastructure)
**What:** Consul, Istio (future), Linkerd (future)  
**Owns:** Liveness, location, health  
**Answers:** "Is service X alive?", "Where is it?"  
**Managed by:** Public Works (infrastructure abstraction)

#### 2️⃣ Capability Registry (Governance)
**What:** Supabase-backed libraries  
**Owns:** Meaning, contracts, capabilities, versioning  
**Answers:** "What does service X mean?", "What capabilities does it expose?", "Is it allowed to execute now?"  
**Managed by:** Curator (Smart City role)

#### 3️⃣ Runtime Registry View (Ephemeral)
**What:** Created per execution, filtered by context  
**Owns:** Execution truth for a specific tenant/context  
**Answers:** "What may execute now for this tenant/context?"  
**Created by:** Curator SDK (fuses governance + liveness)

---

## Part 2: Target Architecture

### 2.1 Curator as Smart City Role

**Location:** `civic_systems/smart_city/roles/curator/`

**Type:** Smart City Primitive (policy-aware, governance-focused)

**Responsibilities:**
1. **Own registries** (Supabase-backed)
2. **Validate capabilities** (policy-aware)
3. **Compose Runtime Registry View** (fuses governance + liveness)
4. **Version management** (capability lifecycle)

**NOT Responsible For:**
- ❌ Service registration (that's Consul/Public Works)
- ❌ Service discovery (that's Consul/Public Works)
- ❌ Health monitoring (that's Consul/Public Works)
- ❌ Traffic routing (that's service mesh)

---

### 2.2 Curator SDK (Boundary Zone)

**Location:** `civic_systems/smart_city/sdk/curator_sdk.py`

**Purpose:** Boundary zone for Runtime and Realms

**Responsibilities:**
1. **Translate intent → capability lookup**
2. **Compose Runtime Registry View** (fuses Supabase registries + Consul liveness)
3. **Apply policy filters** (tenant, security, context)
4. **Emit runtime contract shape**

**Example:**
```python
# Runtime calls Curator SDK
runtime_view = await curator_sdk.get_runtime_registry_view(
    intent="content.parse",
    tenant_id="tenant_123",
    security_context=security_context
)

# Returns filtered, policy-aware view:
# {
#   "capabilities": [...],  # From Supabase registry
#   "services": [...],      # From Consul (filtered by policy)
#   "allowed": True,
#   "policy_context": {...}
# }
```

---

### 2.3 Curator Registries (Supabase-Backed)

**Location:** `civic_systems/smart_city/registries/`

**Type:** Data-backed catalogs (not in-memory)

**Registries:**
1. **Capability Registry** (`capability_registry.py`)
   - Stores: capability definitions, contracts, versioning
   - Backed by: Supabase `capabilities` table
   - Owned by: Curator

2. **Service Registry** (`service_registry.py`)
   - Stores: service metadata, capabilities, contracts
   - Backed by: Supabase `services` table
   - **Note:** This is a projection of Consul + governance metadata

3. **Agent Registry** (`agent_registry.py`)
   - Stores: agent definitions, MCP tool sets, reasoning scopes
   - Backed by: Supabase `agents` table
   - Owned by: Curator

4. **Contract Registry** (`contract_registry.py`)
   - Stores: service contracts, API schemas, versioning
   - Backed by: Supabase `contracts` table
   - Owned by: Curator

**Schema Pattern (Flexible JSONB):**
```sql
-- capabilities table
CREATE TABLE capabilities (
    capability_id UUID PRIMARY KEY,
    capability_name VARCHAR(255) NOT NULL,
    capability_type VARCHAR(100),  -- service, agent, tool, etc.
    realm VARCHAR(100),             -- content, insights, operations, solution
    capability_data JSONB,          -- Flexible structure
    version VARCHAR(50),
    tenant_id UUID,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    status VARCHAR(50)              -- active, deprecated, maintenance
);

-- services table (projection of Consul + governance)
CREATE TABLE services (
    service_id UUID PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    consul_service_id VARCHAR(255), -- Link to Consul
    realm VARCHAR(100),
    service_data JSONB,             -- Capabilities, contracts, metadata
    version VARCHAR(50),
    tenant_id UUID,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    status VARCHAR(50)
);
```

---

### 2.4 Curator Primitive (Policy-Aware)

**Location:** `civic_systems/smart_city/primitives/curator/`

**Type:** Pure primitive (no side effects, policy decisions only)

**Methods:**
```python
class CuratorPrimitive:
    """
    Curator Primitive - Policy-aware governance decisions.
    
    Only called by Runtime (via SDK).
    Makes policy decisions about capabilities, services, contracts.
    """
    
    async def validate_capability(
        self,
        capability_id: str,
        tenant_id: str,
        security_context: SecurityContext
    ) -> Dict[str, Any]:
        """
        Validate capability access.
        
        Policy Logic Only:
        - Is capability allowed for tenant?
        - Is capability version compatible?
        - Does security context permit access?
        """
        ...
    
    async def validate_service_contract(
        self,
        service_id: str,
        contract_version: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Validate service contract.
        
        Policy Logic Only:
        - Is contract version allowed?
        - Is service allowed for tenant?
        - Are contract requirements met?
        """
        ...
    
    async def compose_runtime_view(
        self,
        intent: str,
        tenant_id: str,
        security_context: SecurityContext,
        consul_liveness: List[Dict[str, Any]]  # From Consul
    ) -> Dict[str, Any]:
        """
        Compose Runtime Registry View.
        
        Policy Logic Only:
        - Filter capabilities by policy
        - Filter services by policy
        - Apply tenant isolation
        - Return policy-aware view
        """
        ...
```

---

## Part 3: Service Registration Flow (Updated)

### 3.1 Service Registration (Infrastructure Layer)

**Services register with Consul** (as they always have):

```python
# Service startup
from symphainy_platform.foundations.public_works.abstractions.service_discovery_abstraction import ServiceDiscoveryAbstraction

# Register with Consul (via Public Works)
await service_discovery.register_service(
    service_name="content_manager",
    address="0.0.0.0",
    port=8001,
    health_check="/health",
    metadata={
        "realm": "content",
        "version": "1.0.0"
    }
)
```

**Consul stores:**
- Service instance location
- Health status
- Basic metadata

**Curator does NOT register services with Consul.**

---

### 3.2 Capability Registration (Governance Layer)

**Services register capabilities with Curator** (via SDK):

```python
# Service startup (after Consul registration)
from civic_systems.smart_city.sdk.curator_sdk import CuratorSDK

# Register capabilities with Curator (Supabase registry)
await curator_sdk.register_capability(
    capability_name="content.parse",
    service_name="content_manager",  # Links to Consul service
    realm="content",
    contract={
        "input": {...},
        "output": {...}
    },
    version="1.0.0"
)
```

**Curator stores in Supabase:**
- Capability definition
- Service link (service_name → Consul)
- Contract schema
- Version information

---

### 3.3 Runtime Discovery Flow

**Runtime asks Curator (not Consul directly):**

```python
# Runtime needs to execute "content.parse"
from civic_systems.smart_city.sdk.curator_sdk import CuratorSDK

# Get Runtime Registry View (fuses governance + liveness)
runtime_view = await curator_sdk.get_runtime_registry_view(
    intent="content.parse",
    tenant_id=tenant_id,
    security_context=security_context
)

# Runtime view contains:
# - Capability definition (from Supabase)
# - Service instances (from Consul, filtered by policy)
# - Policy context
# - Allowed/denied status

if runtime_view["allowed"]:
    # Get service instance from Consul (via Public Works)
    service_instance = await service_discovery.discover_service(
        service_name=runtime_view["capability"]["service_name"]
    )
    # Execute...
```

**Key Insight:**
- Runtime never calls Consul directly
- Runtime always asks Curator
- Curator fuses governance (Supabase) + liveness (Consul)
- Policy is applied at Curator level, not Consul level

---

## Part 4: Implementation Plan

### Phase 1: Scaffold Structure (During Phase 1 of Security Guard)

**Timing:** **During Phase 1** (scaffold only, no implementation)

**Rationale:**
- Establishes structure early
- Prevents rework later
- Minimal effort (just directories and `__init__.py`)

**Tasks:**
1. Create `civic_systems/smart_city/roles/curator/` directory
2. Create `civic_systems/smart_city/sdk/curator_sdk.py` (stub)
3. Create `civic_systems/smart_city/registries/capability_registry.py` (stub)
4. Create `civic_systems/smart_city/registries/service_registry.py` (stub)
5. Create `civic_systems/smart_city/registries/agent_registry.py` (stub)
6. Create `civic_systems/smart_city/registries/contract_registry.py` (stub)
7. Create Supabase tables (flexible JSONB schema)

**Deliverable:** Structure in place, ready for implementation

---

### Phase 2: Public Works Service Discovery Abstraction

**Timing:** **After Phase 1** (before Curator implementation)

**Rationale:**
- Curator needs to read from Consul (via abstraction)
- Establishes clean boundary between infrastructure and governance

**Tasks:**
1. Create `symphainy_platform/foundations/public_works/abstractions/service_discovery_abstraction.py`
2. Create `symphainy_platform/foundations/public_works/adapters/consul_adapter.py` (if not exists)
3. Implement `ServiceDiscoveryProtocol`:
   - `register_service()`
   - `discover_service()`
   - `deregister_service()`
   - `get_service_health()`
4. Ensure abstraction returns raw data (no business logic)

**Deliverable:** Public Works abstraction for Consul service discovery

---

### Phase 3: Curator Registries (Supabase-Backed)

**Timing:** **After Phase 2**

**Rationale:**
- Registries are the foundation of Curator
- Need to be queryable before SDK can use them

**Tasks:**
1. **Capability Registry:**
   - Implement `CapabilityRegistry` class
   - Back with Supabase `capabilities` table
   - Methods: `register_capability()`, `get_capability()`, `list_capabilities()`, `update_capability()`

2. **Service Registry:**
   - Implement `ServiceRegistry` class
   - Back with Supabase `services` table
   - Methods: `register_service_metadata()`, `get_service_metadata()`, `link_consul_service()`

3. **Agent Registry:**
   - Implement `AgentRegistry` class
   - Back with Supabase `agents` table
   - Methods: `register_agent()`, `get_agent()`, `list_agents()`

4. **Contract Registry:**
   - Implement `ContractRegistry` class
   - Back with Supabase `contracts` table
   - Methods: `register_contract()`, `get_contract()`, `validate_contract()`

**Migration:**
- Extract hardcoded capabilities from `/symphainy_source/` Curator
- Migrate to Supabase registries
- Preserve existing capability definitions

**Deliverable:** All registries queryable from Supabase

---

### Phase 4: Curator SDK (Boundary Zone)

**Timing:** **After Phase 3**

**Rationale:**
- SDK is the boundary for Runtime and Realms
- Needs registries to be functional first

**Tasks:**
1. **Implement `CuratorSDK` class:**
   - `register_capability()` - Register capability with registry
   - `get_runtime_registry_view()` - Compose Runtime Registry View
   - `lookup_capability_by_intent()` - Intent → capability lookup
   - `validate_service_contract()` - Contract validation

2. **Runtime Registry View Composition:**
   - Query Supabase registries (governance)
   - Query Consul (via Public Works) for liveness
   - Apply policy filters (tenant, security, context)
   - Return filtered, policy-aware view

3. **Integration with Public Works:**
   - Use `ServiceDiscoveryAbstraction` to read Consul
   - Never write to Consul (that's Public Works' job)

**Deliverable:** Curator SDK functional, Runtime can use it

---

### Phase 5: Curator Primitive (Policy-Aware)

**Timing:** **After Phase 4**

**Rationale:**
- Primitive is called by Runtime (via SDK)
- Needs SDK to be functional first

**Tasks:**
1. **Implement `CuratorPrimitive` class:**
   - `validate_capability()` - Policy decision on capability access
   - `validate_service_contract()` - Policy decision on contract
   - `compose_runtime_view()` - Policy decision on Runtime view composition

2. **Policy Integration:**
   - Query Policy Registry (from Security Guard refactoring)
   - Apply tenant isolation rules
   - Apply security policies
   - Apply execution constraints

3. **Pure Primitive:**
   - No side effects
   - No infrastructure calls
   - Only policy decisions

**Deliverable:** Curator Primitive functional, policy-aware

---

### Phase 6: Service Registration Migration

**Timing:** **After Phase 5**

**Rationale:**
- Services need to register with both Consul (infrastructure) and Curator (governance)
- Migration ensures no functionality loss

**Tasks:**
1. **Update Service Registration Pattern:**
   - Services register with Consul (via Public Works) - unchanged
   - Services register capabilities with Curator (via SDK) - new

2. **Migration Script:**
   - Extract existing service registrations from `/symphainy_source/`
   - Register services with Consul (if not already)
   - Register capabilities with Curator (Supabase)

3. **Update Realm Services:**
   - Update service startup to use new pattern
   - Remove direct Curator Foundation calls
   - Use Curator SDK instead

**Deliverable:** All services registered correctly, no functionality loss

---

### Phase 7: Runtime Integration

**Timing:** **After Phase 6** (when Runtime is being built)

**Rationale:**
- Runtime needs to use Curator SDK for capability discovery
- This is when Runtime execution engine is implemented

**Tasks:**
1. **Update Runtime to use Curator SDK:**
   - Replace direct Consul calls with Curator SDK
   - Use `get_runtime_registry_view()` for capability lookup
   - Apply policy-aware views

2. **Runtime Registry View Usage:**
   - Runtime creates view per execution context
   - View is filtered by tenant, security, policy
   - View is ephemeral (not persisted)

**Deliverable:** Runtime uses Curator SDK, no direct Consul calls

---

### Phase 8: Testing & Validation

**Timing:** **After Phase 7**

**Tasks:**
1. **Unit Tests:**
   - Curator registries (Supabase queries)
   - Curator SDK (view composition)
   - Curator Primitive (policy decisions)

2. **Integration Tests:**
   - Service registration flow (Consul + Curator)
   - Runtime discovery flow (Curator SDK)
   - Policy filtering (tenant isolation)

3. **E2E Tests:**
   - Full service registration → capability discovery → execution flow
   - Verify no functionality loss from `/symphainy_source/`

**Deliverable:** All tests passing, equivalent or better functionality

---

## Part 5: Migration Strategy

### 5.1 Extract from `/symphainy_source/`

**Current Registries (In-Memory):**
- `registered_services` (dict)
- `CapabilityRegistryService` (in-memory)
- `AgentCapabilityRegistryService` (in-memory)
- `mcp_tool_registry` (dict)
- `soa_api_registry` (dict)

**Migration Steps:**
1. Extract all capability definitions
2. Extract all service metadata
3. Extract all agent definitions
4. Extract all contract definitions
5. Migrate to Supabase registries
6. Preserve versioning and metadata

---

### 5.2 Preserve Functionality

**Critical:** Must maintain equivalent or better functionality

**Verification:**
- All services can still register
- All capabilities can still be discovered
- Runtime can still find services
- Policy filtering works correctly
- Tenant isolation is preserved

---

## Part 6: Key Architectural Decisions

### 6.1 Curator is NOT a Foundation

**Decision:** Curator is a Smart City role, not infrastructure

**Rationale:**
- Governance is not infrastructure
- Policy decisions belong in Smart City
- Infrastructure (Consul) belongs in Public Works

---

### 6.2 Curator Exposes SDK, Not SOA APIs

**Decision:** Curator SDK is imported, not called via HTTP

**Rationale:**
- Avoids circularity (Curator doesn't register itself)
- Smart City is inside platform boundary
- Faster than network hops
- Simpler dependency management

---

### 6.3 Services Register with Consul (Infrastructure)

**Decision:** Services register with Consul via Public Works, not Curator

**Rationale:**
- Consul is infrastructure, not governance
- Services need to be discoverable by infrastructure
- Curator reads Consul, doesn't own it

---

### 6.4 Capabilities Register with Curator (Governance)

**Decision:** Services register capabilities with Curator via SDK

**Rationale:**
- Capabilities are governance, not infrastructure
- Curator owns meaning, Consul owns liveness
- Separation of concerns

---

### 6.5 Runtime Asks Curator, Not Consul

**Decision:** Runtime uses Curator SDK for capability discovery

**Rationale:**
- Runtime needs policy-aware views
- Curator fuses governance + liveness
- Consul alone doesn't have policy context

---

## Part 7: Implementation Timing Recommendation

### ✅ Recommended: **Scaffold During Phase 1, Implement After Phase 1**

**Rationale:**
1. **Phase 1 Focus:** Security Guard refactoring establishes the pattern (primitives, SDKs, registries)
2. **Scaffold Early:** Create structure during Phase 1 so it's ready
3. **Implement Later:** After Phase 1, we'll have:
   - Established pattern (Security Guard)
   - Policy Registry in place
   - Platform SDK structure
   - Clear separation of concerns

4. **Natural Progression:**
   - Phase 1: Security Guard (auth, policy)
   - Phase 2: Curator (capabilities, services)
   - Phase 3: Other Smart City roles

**Timeline:**
- **Phase 1 (Current):** Scaffold Curator structure (minimal effort)
- **After Phase 1:** Implement Curator (Phases 2-8 above)

---

## Part 8: Success Criteria

### Phase 1 (Scaffold) Complete When:
- [ ] Directory structure created
- [ ] Stub files in place
- [ ] Supabase tables created (flexible JSONB)
- [ ] No breaking changes

### Full Implementation Complete When:
- [ ] All registries queryable from Supabase
- [ ] Curator SDK functional
- [ ] Curator Primitive policy-aware
- [ ] Services register with both Consul and Curator
- [ ] Runtime uses Curator SDK (not Consul directly)
- [ ] All tests passing
- [ ] Equivalent or better functionality than `/symphainy_source/`
- [ ] Three concepts clearly separated (Service Mesh, Capability Registry, Runtime View)

---

## Part 9: Questions & Answers

### Q1: What happens to existing Consul registrations?

**A:** Services continue to register with Consul (unchanged). Curator reads from Consul but doesn't manage it.

---

### Q2: How do we migrate existing in-memory registries?

**A:** Extract capability definitions from `/symphainy_source/` Curator, migrate to Supabase registries, preserve all metadata.

---

### Q3: What if a service is in Consul but not in Curator registry?

**A:** Curator can still discover it from Consul, but it won't have capability metadata. Services should register capabilities with Curator for full functionality.

---

### Q4: How does Curator handle service mesh changes (Consul → Istio)?

**A:** Public Works abstraction handles service mesh swap. Curator continues to read from abstraction (unchanged). Only Public Works adapter changes.

---

### Q5: What about MCP tools and agents?

**A:** MCP tools stay in Agentic SDK (not globally registered). Agents register with Curator Agent Registry. Curator doesn't expose MCP tools globally.

---

## Summary

This plan evolves Curator from a Foundation (wrapping Consul) to a Smart City role (governance + registries), clearly separating:

1. **Service Mesh** (Consul) = Infrastructure, liveness
2. **Capability Registry** (Supabase) = Governance, meaning
3. **Runtime Registry View** (ephemeral) = Execution truth

**Key Unlock:** Curator SDK fuses governance (Supabase) + liveness (Consul) into policy-aware views for Runtime, without circularity or infrastructure coupling.

**Timing:** Scaffold during Phase 1, implement after Phase 1 (when Security Guard pattern is established).
