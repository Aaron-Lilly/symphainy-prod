# Week 0.5: Discovery & Mapping
**Date:** January 2026  
**Status:** ✅ **COMPLETE**  
**Purpose:** Understand existing codebase before building new platform

---

## 🎯 Discovery Summary

Based on analysis of `symphainy_source/symphainy-platform/` and the `CANONICAL_REBUILD_AUDIT.md`, here's what we're working with:

---

## 📊 Existing Codebase Inventory

### ✅ **Foundations (REUSABLE - Refactor to Platform Standards)**

#### 1. **Public Works Foundation** (`foundations/public_works_foundation/`)
**Status:** ✅ **KEEP** (refactor)
- Infrastructure abstractions (file management, metadata, security, etc.)
- 5-layer architecture pattern
- Abstraction contracts (Protocols)
- **Action:** Review abstractions, ensure they align with new Runtime Plane architecture

#### 2. **Curator Foundation** (`foundations/curator_foundation/`)
**Status:** ✅ **KEEP** (refactor)
- Service discovery and capability registry
- MCP server registration
- **Action:** Refocus as capability registry (not executor) - aligns with new plan

#### 3. **Agentic Foundation** (`foundations/agentic_foundation/`)
**Status:** ✅ **KEEP** (enhance)
- Agent SDK base classes
- Tool composition
- **Action:** Add `GroundedReasoningAgentBase` (missing, critical for new architecture)

#### 4. **Experience Foundation** (`foundations/experience_foundation/`)
**Status:** ✅ **KEEP** (refactor)
- SDKs and client helpers
- **Action:** Review for new Experience Plane architecture

#### 5. **DI Container** (`foundations/di_container/`)
**Status:** ✅ **KEEP** (review)
- Dependency injection core
- **Action:** Review initialization order for new architecture

---

### ✅ **Base Classes (REUSABLE - Minor Review)**

#### 1. **FoundationServiceBase** (`bases/foundation_service_base.py`)
**Status:** ✅ **CLEAN** (no anti-patterns)
- No direct state storage
- Proper mixin composition
- **Action:** ✅ **KEEP** (no changes needed)

#### 2. **RealmServiceBase** (`bases/realm_service_base.py`)
**Status:** ✅ **CLEAN** (minor review)
- No direct state storage
- Proper Smart City service discovery
- **Action:** ✅ **KEEP** (review for state patterns)

#### 3. **OrchestratorBase** (`bases/orchestrator_base.py`)
**Status:** ✅ **CLEAN** (review agent initialization)
- No direct state storage
- Proper delegation
- **Action:** ✅ **KEEP** (review agent initialization for new architecture)

#### 4. **Mixins** (`bases/mixins/`)
**Status:** ✅ **CLEAN**
- All mixins are clean (no anti-patterns)
- **Action:** ✅ **KEEP** (all mixins are clean)

---

### ⚠️ **Runtime Plane (EXISTS - Needs Review)**

**Location:** `planes/runtime_plane/`

**Status:** ✅ **EXISTS** (needs review for new architecture)

**Components Found:**
- `runtime_plane_service.py` - Runtime Plane service
- `runtime.py` - Base runtime class
- `agent_runtime.py` - Agent execution
- `data_runtime.py` - Data mash execution
- `execution_plan.py` - Execution plan structure
- `execution_graph.py` - Execution graph structure
- `execution_context.py` - Execution context
- `state_store.py` - State store
- `transport_manager.py` - WebSocket management
- `safety_controller.py` - Safety states
- `capability_resolver.py` - Smart City integration

**Missing Components (Need to Create):**
- ❌ `session_surface.py` - Session lifecycle management
- ❌ `state_surface.py` - State coordination (may exist as `state_store.py` but needs review)
- ❌ `execution_surface.py` - Execution control
- ❌ `intent_surface.py` - Intent propagation (removed per plan - agents handle this)

**Action:** Review existing Runtime Plane components, add missing surfaces

---

### ⚠️ **Smart City Services (REUSABLE - Refactor to Use Runtime Surfaces)**

**Location:** `backend/smart_city/`

**Status:** ✅ **KEEP** (refactor to use runtime surfaces)

**Services Found:**
- Traffic Cop (session management, API gateway)
- Conductor (workflow orchestration)
- Post Office (event publishing)
- Librarian (knowledge management)
- Data Steward (data lifecycle)
- Content Steward (content lifecycle)
- Security Guard (authentication/authorization)
- Nurse (health monitoring)
- City Manager (platform orchestration)

**Action:** Refactor to use Runtime Surfaces (remove ad hoc state storage)

---

### 🔄 **Realms (REBUILD - Extract Business Logic)**

#### 1. **Content Realm** (`backend/content/`)
**Status:** ✅ **REBUILD** (extract deterministic logic)
- Parsing logic (deterministic) → **KEEP**
- Embedding logic (deterministic) → **KEEP**
- Orchestration → **REPLACE** with Runtime Plane

#### 2. **Insights Realm** (`backend/insights/`)
**Status:** ✅ **REBUILD** (extract semantic interpretation)
- Data quality analysis → **KEEP**
- Semantic interpretation → **KEEP**
- Orchestration → **REPLACE** with Runtime Plane

#### 3. **Journey Realm** (`backend/journey/`)
**Status:** ✅ **REBUILD** (extract SOP/workflow logic)
- SOP/workflow logic → **KEEP**
- Orchestration → **REPLACE** with Runtime Plane

#### 4. **Solution Realm** (`backend/solution/`)
**Status:** ✅ **REBUILD** (extract roadmap/proposal logic)
- Roadmap/proposal logic → **KEEP**
- Orchestration → **REPLACE** with Runtime Plane

---

### 🔄 **Agents (EXTRACT & REFACTOR)**

**Location:** `backend/business_enablement_old/agents/` and `backend/*/agents/`

**Critical Agents to Extract:**
1. **CoexistenceBlueprintSpecialist** → `realms/journey/agents/`
2. **WorkflowGenerationSpecialist** → `realms/journey/agents/`
3. **SOPGenerationSpecialist** → `realms/journey/agents/`
4. **RoadmapProposalSpecialist** → `realms/solution/agents/`
5. **BusinessAnalysisSpecialist** → `realms/solution/agents/`

**Anti-Patterns Found:**
- ❌ Direct state storage in `DeclarativeAgentBase` (`conversation_history = []`)
- ❌ Agents managing state lifecycle

**Action:** Extract agents, refactor to use `GroundedReasoningAgentBase`, remove state storage

---

### ✅ **Utilities (KEEP)**

**Location:** `utilities/`

**Status:** ✅ **KEEP** (review)
- Error handling
- Logging
- Configuration
- Validation
- Security
- Telemetry

**Action:** ✅ **KEEP** (review each utility)

---

### ✅ **Configuration (KEEP)**

**Location:** `config/`

**Status:** ✅ **KEEP** (review)
- Environment loading
- Infrastructure config
- Business logic config

**Action:** ✅ **KEEP** (review config files)

---

## 🎯 Capability Inventory

### What Exists (Valuable Logic)

| Capability | Location | Status | Action |
|------------|----------|--------|--------|
| **Deterministic Parsing** | `backend/content/` | ✅ Keep | Extract logic, rebuild orchestration |
| **Deterministic Embeddings** | `backend/content/` | ✅ Keep | Extract logic, rebuild orchestration |
| **Data Quality Analysis** | `backend/insights/` | ✅ Keep | Extract logic, rebuild orchestration |
| **Semantic Interpretation** | `backend/insights/` | ✅ Keep | Extract logic, rebuild orchestration |
| **SOP/Workflow Logic** | `backend/journey/` | ✅ Keep | Extract logic, rebuild orchestration |
| **Roadmap/Proposal Logic** | `backend/solution/` | ✅ Keep | Extract logic, rebuild orchestration |
| **Infrastructure Abstractions** | `foundations/public_works_foundation/` | ✅ Keep | Review, refactor |
| **Service Discovery** | `foundations/curator_foundation/` | ✅ Keep | Refocus as registry |
| **Agent SDK** | `foundations/agentic_foundation/` | ✅ Keep | Add grounded reasoning base |
| **Base Classes** | `bases/` | ✅ Keep | Review, minor changes |
| **Runtime Plane Core** | `planes/runtime_plane/` | ✅ Keep | Review, add surfaces |

### What's Missing (Need to Create)

| Capability | Priority | Action |
|------------|----------|--------|
| **Session Surface** | CRITICAL | Create in `runtime/session_surface.py` |
| **State Surface** | CRITICAL | Review `state_store.py`, may need refactor |
| **Execution Surface** | CRITICAL | Create in `runtime/execution_surface.py` |
| **GroundedReasoningAgentBase** | CRITICAL | Create in `foundations/agentic_foundation/` |
| **Experience Plane** | HIGH | Create REST/WebSocket handlers |
| **Contracts** | HIGH | Create Protocol-based contracts |

---

## 📋 Mapping Strategy

### Step 1: Foundations → New Platform
- ✅ Keep all foundations (refactor to align with new architecture)
- ✅ Keep base classes (minor review)
- ✅ Keep utilities (review)

### Step 2: Runtime Plane → New Platform
- ✅ Review existing Runtime Plane components
- ✅ Add missing surfaces (Session, State, Execution)
- ✅ Integrate with new architecture

### Step 3: Smart City → New Platform
- ✅ Keep all Smart City services
- ✅ Refactor to use Runtime Surfaces
- ✅ Remove ad hoc state storage

### Step 4: Realms → New Platform
- ✅ Extract business logic (parsing, embeddings, analysis, etc.)
- ✅ Rebuild orchestration using Runtime Plane
- ✅ Wire agents correctly

### Step 5: Agents → New Platform
- ✅ Extract critical reasoning agents
- ✅ Refactor to use `GroundedReasoningAgentBase`
- ✅ Remove state storage anti-patterns

---

## ✅ Discovery Complete

**Key Findings:**
1. ✅ Foundations are solid (need refactoring, not rebuilding)
2. ✅ Base classes are clean (minor review)
3. ✅ Runtime Plane exists (needs surfaces added)
4. ✅ Smart City services exist (need refactoring)
5. ✅ Realms need rebuilding (extract logic, replace orchestration)
6. ✅ Agents need extraction and refactoring

**Next Steps:**
1. ✅ Scaffold new platform structure (Week 0)
2. ✅ Start Runtime Plane v0 (Week 1)
3. ✅ Add missing surfaces and components

---

**Last Updated:** January 2026  
**Status:** ✅ **READY FOR WEEK 0 SCAFFOLDING**
