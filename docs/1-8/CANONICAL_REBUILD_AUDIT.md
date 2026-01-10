# Canonical Rebuild Audit & Mapping
**Date:** January 2026  
**Status:** 🔄 **IN PROGRESS**  
**Purpose:** Complete file-by-file audit and mapping for clean rebuild

---

## 🎯 Executive Summary

This document is the **canonical source of truth** for rebuilding the platform. Every file, directory, and component is audited and mapped to the new architecture.

**Key Principles:**
- ✅ No shortcuts - everything audited
- ✅ Clean architecture - no anti-patterns
- ✅ Native support for end-state vision
- ✅ Contracts = Protocols (no separate protocol layer)

---

## 📋 Table of Contents

1. [Root Directory Audit (symphainy_source/)](#root-directory-audit)
2. [Platform Root Directory Audit (symphainy-platform/)](#platform-root-directory-audit)
3. [Directory-by-Directory Audit](#directory-by-directory-audit)
4. [Base Classes Review](#base-classes-review)
5. [Gap Analysis](#gap-analysis)

---

## 1. Root Directory Audit (symphainy_source/)

### Files to Bring Over

| File | Current Location | New Location | Action | Notes |
|------|-----------------|--------------|--------|-------|
| `docker-compose.yml` | `symphainy_source/` | `symphainy_source_code/` | ✅ **KEEP** (refactor) | Main compose file - needs path updates |
| `docker-compose.prod.yml` | `symphainy_source/` | `symphainy_source_code/` | ✅ **KEEP** (refactor) | Production compose - needs path updates |
| `docker-compose.test.yml` | `symphainy_source/` | `symphainy_source_code/` | ✅ **KEEP** (refactor) | Test compose - needs path updates |
| `docker-compose.ci.yml` | `symphainy_source/` | `symphainy_source_code/` | ✅ **KEEP** (refactor) | CI compose - needs path updates |
| `docker-compose.option-c.yml` | `symphainy_source/` | `symphainy_source_code/` | ⚠️ **REVIEW** | Option C deployment - may not be needed |
| `Dockerfile.e2e` | `symphainy_source/` | `symphainy_source_code/` | ⚠️ **REVIEW** | E2E testing - may not be needed yet |
| `README.md` | `symphainy_source/` | `symphainy_source_code/` | ✅ **KEEP** (update) | Update for new architecture |
| `scripts/` | `symphainy_source/scripts/` | `symphainy_source_code/scripts/` | ✅ **KEEP** (review) | Review each script |

### Files to Archive (Don't Bring)

| File | Reason |
|------|--------|
| `BREAKING_CHANGE_*.md` | Historical documentation |
| `RUNTIME_PLANE_*.md` | Historical documentation |
| `TEST_RESULTS_*.md` | Historical test results |
| `test_*.py` (root level) | Move to tests/ or archive |
| `coverage.xml` | Generated file |
| `tests_old_archive/` | Archive - don't bring |
| `archive/` | Archive - don't bring |

### Directories to Review

| Directory | Action | Notes |
|-----------|--------|-------|
| `docs/` | ✅ **KEEP** (selective) | Keep architectural docs, archive implementation docs |
| `services/` | ⚠️ **REVIEW** | May be legacy - need to audit |
| `logs/` | ❌ **DON'T BRING** | Runtime logs - don't commit |

---

## 2. Platform Root Directory Audit (symphainy-platform/)

### Root Files

| File | Action | New Location | Refactor Needed |
|------|--------|--------------|-----------------|
| `main.py` | ✅ **REBUILD** | `symphainy_source_code/main.py` | Complete rebuild (~150 lines) |
| `main_cloud_ready.py` | ❌ **ARCHIVE** | N/A | Legacy - don't bring |
| `pyproject.toml` | ✅ **KEEP** (update) | `symphainy_source_code/pyproject.toml` | Update dependencies |
| `poetry.lock` | ✅ **KEEP** (regenerate) | `symphainy_source_code/poetry.lock` | Regenerate after dependency updates |
| `requirements.txt` | ✅ **KEEP** (update) | `symphainy_source_code/requirements.txt` | Update for new architecture |
| `Dockerfile` | ✅ **KEEP** (refactor) | `symphainy_source_code/Dockerfile` | Update paths |
| `Dockerfile.ci` | ✅ **KEEP** (refactor) | `symphainy_source_code/Dockerfile.ci` | Update paths |
| `README.md` | ✅ **KEEP** (update) | `symphainy_source_code/README.md` | Update for new architecture |
| `celery_app.py` | ⚠️ **REVIEW** | `symphainy_source_code/celery_app.py` | May not be needed in new architecture |
| `startup.sh` | ✅ **KEEP** (refactor) | `symphainy_source_code/scripts/startup.sh` | Update paths |
| `stop.sh` | ✅ **KEEP** (refactor) | `symphainy_source_code/scripts/stop.sh` | Update paths |
| `logs.sh` | ✅ **KEEP** (refactor) | `symphainy_source_code/scripts/logs.sh` | Update paths |
| `test_config.env` | ⚠️ **REVIEW** | `symphainy_source_code/config/test_config.env` | May be redundant |
| `coverage.xml` | ❌ **DON'T BRING** | N/A | Generated file |
| `=2.7.0` | ❌ **DON'T BRING** | N/A | Errant file |
| `poetry` | ❌ **DON'T BRING** | N/A | Binary file |

### Configuration Files

| File | Action | New Location | Notes |
|------|--------|--------------|-------|
| `docker-compose.infrastructure.yml` | ✅ **KEEP** (refactor) | `symphainy_source_code/docker-compose.infrastructure.yml` | Infrastructure services |
| `loki-config.yaml` | ✅ **KEEP** | `symphainy_source_code/config/loki-config.yaml` | Observability config |
| `tempo-config.yaml` | ✅ **KEEP** | `symphainy_source_code/config/tempo-config.yaml` | Observability config |
| `otel-collector-config.yaml` | ✅ **KEEP** | `symphainy_source_code/config/otel-collector-config.yaml` | Observability config |
| `grafana-datasources.yaml` | ✅ **KEEP** | `symphainy_source_code/config/grafana-datasources.yaml` | Observability config |
| `traefik-config/` | ✅ **KEEP** (review) | `symphainy_source_code/config/traefik-config/` | Review all files |

### Documentation Files (Root)

| File | Action | Notes |
|------|--------|-------|
| `POETRY_LOCK_*.md` | ❌ **ARCHIVE** | Historical documentation |
| `SECRETS_*.md` | ⚠️ **REVIEW** | May contain useful patterns |
| `SECURITY_*.md` | ⚠️ **REVIEW** | May contain useful patterns |
| `credential_file_for_reference.md` | ❌ **ARCHIVE** | Historical reference |
| `env_secrets_*.md` | ❌ **ARCHIVE** | Historical reference |

---

## 3. Directory-by-Directory Audit

### 3.1 bases/ Directory

**Purpose:** Base classes for all services, orchestrators, and agents

**Status:** ⚠️ **NEEDS COMPREHENSIVE REVIEW**

#### Files to Review

| File | Action | Notes |
|------|--------|-------|
| `foundation_service_base.py` | ✅ **KEEP** (review) | Review for anti-patterns |
| `realm_service_base.py` | ✅ **KEEP** (review) | Review for anti-patterns |
| `smart_city_role_base.py` | ✅ **KEEP** (review) | Review for anti-patterns |
| `orchestrator_base.py` | ✅ **KEEP** (review) | Review for anti-patterns |
| `manager_service_base.py` | ✅ **KEEP** (review) | Review for anti-patterns |
| `plane_service_base.py` | ✅ **KEEP** (review) | Review for anti-patterns |
| `startup_policy.py` | ✅ **KEEP** | Startup policy enum |
| `protocols/` | ⚠️ **DECISION NEEDED** | Contracts = Protocols? |
| `mixins/` | ✅ **KEEP** (review) | Review each mixin |
| `mcp_server/` | ✅ **KEEP** (review) | Review MCP server base |

#### Anti-Patterns to Check

- [ ] Direct state storage in base classes
- [ ] Ad hoc service discovery
- [ ] Mixed concerns (business logic in infrastructure)
- [ ] Hardcoded dependencies
- [ ] Circular dependencies
- [ ] Protocol/contract drift

---

### 3.2 foundations/ Directory

**Purpose:** Foundation services (infrastructure layer)

**Status:** ✅ **MOSTLY REUSABLE** (with refactoring)

#### Directories

| Directory | Action | Notes |
|-----------|--------|-------|
| `di_container/` | ✅ **KEEP** (refactor) | DI Container - core infrastructure |
| `public_works_foundation/` | ✅ **KEEP** (refactor) | Infrastructure abstractions |
| `curator_foundation/` | ✅ **KEEP** (refactor) | Service discovery |
| `agentic_foundation/` | ✅ **KEEP** (refactor) | Agent SDK |
| `experience_foundation/` | ✅ **KEEP** (refactor) | Experience SDK |
| `client_config_foundation/` | ⚠️ **REVIEW** | May be part of agentic_idp |
| `tenant_config_foundation/` | ⚠️ **REVIEW** | May be part of smart_city |
| `platform_gateway_foundation/` | ⚠️ **REVIEW** | May be part of smart_city |
| `runtime_foundation_archived/` | ❌ **DON'T BRING** | Archived - runtime is now a plane |
| `communication_foundation_archived/` | ❌ **DON'T BRING** | Archived - functionality distributed |

---

### 3.3 planes/ Directory

**Purpose:** Runtime Plane (execution kernel)

**Status:** ✅ **KEEP** (review for completeness)

#### Files

| File | Action | Notes |
|------|--------|-------|
| `runtime_plane_service.py` | ✅ **KEEP** (review) | Review for state architecture |
| `runtime.py` | ✅ **KEEP** (review) | Base runtime class |
| `agent_runtime.py` | ✅ **KEEP** (review) | Agent execution |
| `data_runtime.py` | ✅ **KEEP** (review) | Data mash execution |
| `execution_plan.py` | ✅ **KEEP** | Execution plan structure |
| `execution_graph.py` | ✅ **KEEP** | Execution graph structure |
| `execution_context.py` | ✅ **KEEP** | Execution context |
| `state_store.py` | ✅ **KEEP** (review) | Review for state architecture |
| `transport_manager.py` | ✅ **KEEP** (review) | WebSocket management |
| `safety_controller.py` | ✅ **KEEP** | Safety states |
| `capability_resolver.py` | ✅ **KEEP** | Smart City integration |

#### Missing Files (Need to Create)

- [ ] `session_surface.py` - Session lifecycle management
- [ ] `state_surface.py` - State coordination
- [ ] `execution_surface.py` - Execution control
- [ ] `intent_surface.py` - Intent propagation

---

### 3.4 backend/ Directory

**Purpose:** Business logic (realms, services, orchestrators)

**Status:** ⚠️ **90-100% RECREATION NEEDED**

#### Directories

| Directory | Action | Notes |
|-----------|--------|-------|
| `smart_city/` | ✅ **KEEP** (refactor) | Smart City services - refactor to use runtime surfaces |
| `solution/` | ✅ **REBUILD** | Solution Realm - recreate aligned to contracts |
| `journey/` | ✅ **REBUILD** | Journey Realm - recreate aligned to contracts |
| `content/` | ✅ **REBUILD** | Content Realm - recreate aligned to contracts |
| `insights/` | ✅ **REBUILD** | Insights Realm - recreate aligned to contracts |
| `business_enablement/` | ⚠️ **REVIEW** | May be legacy - check if still used |
| `business_enablement_old/` | ✅ **EXTRACT** | Extract agents and business logic |
| `agentic/` | ⚠️ **REVIEW** | May be legacy - check if still used |
| `api/` | ⚠️ **REVIEW** | May be legacy - experience plane handles this |

---

### 3.5 utilities/ Directory

**Purpose:** Platform utilities

**Status:** ✅ **KEEP** (review)

#### Directories

| Directory | Action | Notes |
|-----------|--------|-------|
| `error/` | ✅ **KEEP** | Error handling utilities |
| `health/` | ✅ **KEEP** | Health monitoring utilities |
| `logging/` | ✅ **KEEP** | Logging utilities |
| `telemetry_reporting/` | ✅ **KEEP** | Telemetry utilities |
| `security_authorization/` | ✅ **KEEP** | Security utilities |
| `validation/` | ✅ **KEEP** | Validation utilities |
| `serialization/` | ✅ **KEEP** | Serialization utilities |
| `configuration/` | ✅ **KEEP** | Configuration utilities |
| `tenant/` | ✅ **KEEP** | Tenant management utilities |

---

### 3.6 config/ Directory

**Purpose:** Configuration files

**Status:** ✅ **KEEP** (review)

#### Files

| File | Action | Notes |
|------|--------|-------|
| `environment_loader.py` | ✅ **KEEP** | Environment loading |
| `infrastructure.yaml` | ✅ **KEEP** | Infrastructure config |
| `business-logic.yaml` | ✅ **KEEP** | Business logic config |
| `*.env` files | ✅ **KEEP** | Environment templates |

---

### 3.7 scripts/ Directory

**Purpose:** Operational scripts

**Status:** ✅ **KEEP** (review)

#### Files to Review

- [ ] `startup.sh` - Update paths
- [ ] `stop.sh` - Update paths
- [ ] `deploy.sh` - Update paths
- [ ] All other scripts - Review each

---

### 3.8 Other Directories

| Directory | Action | Notes |
|-----------|--------|-------|
| `tests/` | ⚠️ **DEFER** | Revisit with CI/CD roadmap |
| `docs/` | ✅ **KEEP** (selective) | Keep architectural docs |
| `grafana/` | ✅ **KEEP** | Grafana provisioning |
| `arangodb-init/` | ✅ **KEEP** | ArangoDB initialization |
| `platform_infrastructure/` | ⚠️ **REVIEW** | May be legacy |
| `main/` | ⚠️ **REVIEW** | May be legacy |
| `utils/` | ⚠️ **REVIEW** | May duplicate utilities/ |
| `agentic/` | ⚠️ **REVIEW** | May be legacy |

---

## 4. Base Classes Review

### 4.1 foundation_service_base.py

**Status:** ✅ **CLEAN** (no anti-patterns found)

**Findings:**
- ✅ No direct state storage
- ✅ Proper mixin composition
- ✅ Clean initialization pattern
- ✅ No hardcoded dependencies

**Action:** ✅ **KEEP** (no changes needed)

---

### 4.2 realm_service_base.py

**Status:** ⚠️ **NEEDS REVIEW** (potential anti-patterns)

**Findings:**
- ✅ No direct state storage found in base class
- ✅ Proper mixin composition
- ✅ Clean Smart City service discovery via Curator
- ⚠️ Uses `_smart_city_services = {}` cache (acceptable - ephemeral cache)
- ⚠️ Uses `_enabling_services = {}` cache (acceptable - ephemeral cache)

**Action:** ✅ **KEEP** (minor review for state patterns)

---

### 4.3 orchestrator_base.py

**Status:** ⚠️ **NEEDS REVIEW** (agent initialization patterns)

**Findings:**
- ✅ No direct state storage found
- ✅ Proper delegation to RealmServiceBase
- ⚠️ Uses `self._agents: Dict[str, Any] = {}` (acceptable - agent registry)
- ⚠️ Uses `self._enabling_services = {}` (acceptable - service registry)
- ✅ Clean agent initialization pattern via `initialize_agent()`

**Action:** ✅ **KEEP** (review agent initialization for new architecture)

---

### 4.4 Mixins Review

**Status:** ⚠️ **NEEDS REVIEW** (state patterns)

**Mixins Reviewed:**
- ✅ `utility_access_mixin.py` - Clean
- ✅ `infrastructure_access_mixin.py` - Clean
- ✅ `security_mixin.py` - Clean
- ✅ `performance_monitoring_mixin.py` - Clean
- ⚠️ `platform_capabilities_mixin.py` - Uses `_smart_city_services = {}` cache (acceptable)
- ✅ `communication_mixin.py` - Clean
- ✅ `micro_module_support_mixin.py` - Clean

**Findings:**
- ✅ No direct state manipulation (caches are acceptable)
- ✅ Clean abstractions
- ✅ No mixed concerns

**Action:** ✅ **KEEP** (all mixins are clean)

---

### 4.5 Agent Base Classes Review

**Status:** ⚠️ **ANTI-PATTERN FOUND**

**Files Reviewed:**
- `foundations/agentic_foundation/agent_sdk/agent_base.py` - Base agent class
- `backend/business_enablement_old/agents/declarative_agent_base.py` - Declarative agent base

**Anti-Patterns Found:**

1. **Direct State Storage in DeclarativeAgentBase:**
   ```python
   # Line 110: DeclarativeAgentBase
   self.conversation_history: List[Dict[str, Any]] = []  # ❌ ANTI-PATTERN
   ```
   **Issue:** Agents storing conversation state directly
   **Fix:** Use State Surface for conversation state

2. **Stateful Pattern in Agents:**
   ```python
   # Line 108: DeclarativeAgentBase
   self.stateful = self.agent_config.get("stateful", False)
   self.max_conversation_history = self.agent_config.get("max_conversation_history", 10)
   ```
   **Issue:** Agents managing their own state lifecycle
   **Fix:** State Surface coordinates state, agents request state

**Action:** ⚠️ **REFACTOR** (remove direct state storage, use State Surface)

---

## 5. Gap Analysis

### 5.1 Missing Components (MUST CREATE)

#### Contracts (NEW - Need to Create)

**Priority: CRITICAL** - Contracts are the foundation of the architecture

- [ ] `contracts/runtime/session.py` - SessionContract (Protocol)
- [ ] `contracts/runtime/state.py` - StateContract (Protocol)
- [ ] `contracts/runtime/execution.py` - ExecutionContract (Protocol)
- [ ] `contracts/runtime/intent.py` - IntentContract (Protocol)
- [ ] `contracts/smart_city/security.py` - SecurityContract (Protocol)
- [ ] `contracts/smart_city/data.py` - DataContract (Protocol)
- [ ] `contracts/smart_city/telemetry.py` - TelemetryContract (Protocol)
- [ ] `contracts/smart_city/workflow.py` - WorkflowContract (Protocol)
- [ ] `contracts/smart_city/events.py` - EventsContract (Protocol)
- [ ] `contracts/realm/content.py` - ContentContract (Protocol)
- [ ] `contracts/realm/insights.py` - InsightsContract (Protocol)
- [ ] `contracts/realm/journey.py` - JourneyContract (Protocol)
- [ ] `contracts/realm/solution.py` - SolutionContract (Protocol)

**Implementation Pattern:**
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class SessionContract(Protocol):
    """Session contract - enforced at runtime."""
    async def create_session(self, user_context: Dict[str, Any]) -> SessionContext:
        ...
    
    async def get_session(self, session_id: str) -> SessionContext:
        ...
```

#### Runtime Surfaces (MISSING - CRITICAL)

**Priority: CRITICAL** - These replace ad hoc state management

- [ ] `runtime/session_surface.py` - Session lifecycle management
  - Replaces: Ad hoc session creation in services
  - Coordinates with: Traffic Cop (Smart City) for session state
  - Responsibilities: Create, get, update, delete sessions

- [ ] `runtime/state_surface.py` - State coordination
  - Replaces: `self.active_solutions = {}`, `self.conversation_history = []`
  - Coordinates with: Traffic Cop (session state), Runtime Plane (execution state), Conductor (workflow state)
  - Responsibilities: Single source of truth for all state

- [ ] `runtime/execution_surface.py` - Execution control
  - Replaces: Ad hoc execution control in agents/services
  - Coordinates with: Runtime Plane (AgentRuntime, DataRuntime)
  - Responsibilities: Execute plans, manage execution lifecycle

- [ ] `runtime/intent_surface.py` - Intent propagation
  - Replaces: Ad hoc intent handling in agents
  - Coordinates with: Guide Agents, Liaison Agents
  - Responsibilities: Route intents, propagate context

#### Critical Reasoning Agents (MISSING - EXTRACT FROM business_enablement_old)

**Priority: HIGH** - These are critical for MVP functionality

**Journey Realm Agents:**
- [ ] `realms/journey/agents/coexistence_blueprint_specialist.py`
  - Source: `backend/business_enablement_old/agents/coexistence_blueprint_specialist.py`
  - Action: Extract and refactor to use GroundedReasoningAgentBase
  - Purpose: Generate coexistence blueprints for human+AI optimization

- [ ] `realms/journey/agents/workflow_generation_specialist.py`
  - Source: `backend/business_enablement_old/agents/workflow_generation_specialist.py`
  - Action: Extract and refactor to use GroundedReasoningAgentBase
  - Purpose: Generate workflows from SOPs or chat

- [ ] `realms/journey/agents/sop_generation_specialist.py`
  - Source: `backend/business_enablement_old/agents/sop_generation_specialist.py`
  - Action: Extract and refactor to use GroundedReasoningAgentBase
  - Purpose: Generate SOPs from workflows or chat

**Solution Realm Agents:**
- [ ] `realms/solution/agents/roadmap_proposal_specialist.py`
  - Source: `backend/business_enablement_old/agents/roadmap_proposal_specialist.py`
  - Action: Extract and refactor to use GroundedReasoningAgentBase
  - Purpose: Generate roadmaps from pillar outputs

- [ ] `realms/solution/agents/business_analysis_specialist.py`
  - Source: `backend/business_enablement_old/agents/business_analysis_specialist.py`
  - Action: Extract and refactor to use GroundedReasoningAgentBase
  - Purpose: Generate POC proposals from pillar outputs

**Note:** GuideCrossDomainAgent already exists in `backend/solution/agents/guide_cross_domain_agent.py` ✅

#### Grounded Reasoning Base (NEW - CRITICAL)

**Priority: CRITICAL** - Ensures deterministic reasoning

- [ ] `foundations/agentic_foundation/agent_sdk/grounded_reasoning_agent_base.py`
  - Purpose: Base class for critical reasoning agents
  - Pattern: Fact gathering → Structured extraction → LLM reasoning → Validation
  - Ensures: Same facts + same tools = same conclusions
  - Prevents: Hallucinations, inconsistent conclusions

**Implementation Pattern:**
```python
class GroundedReasoningAgentBase(AgentBase):
    async def generate_grounded_reasoning(
        self,
        goal: str,
        context: Dict[str, Any],
        required_tools: List[str]
    ) -> Dict[str, Any]:
        # 1. Gather facts via MCP tools
        facts = await self._gather_facts(required_tools, context)
        
        # 2. Extract structured facts
        structured_facts = await self._extract_facts(facts)
        
        # 3. Reason with facts as constraints
        reasoning = await self._reason_with_facts(goal, structured_facts, context)
        
        # 4. Validate reasoning against facts
        validated_reasoning = await self._validate_reasoning(reasoning, structured_facts)
        
        return validated_reasoning
```

#### Experience Plane (MISSING)

**Priority: HIGH** - Frontend integration

- [ ] `experience/rest/` - REST API handlers
- [ ] `experience/websocket/` - WebSocket handlers (may already exist in runtime plane)
- [ ] `experience/adapters/` - Frontend adapters

**Note:** Check if `experience/` directory exists (it doesn't in current structure)

---

### 5.2 Components Needing Refactoring

#### Foundations

- [ ] `foundations/di_container/` - Review initialization order
- [ ] `foundations/public_works_foundation/` - Review abstractions
- [ ] `foundations/curator_foundation/` - Review service discovery
- [ ] `foundations/agentic_foundation/` - Add grounded reasoning
- [ ] `foundations/experience_foundation/` - Review for new architecture

#### Smart City Services

- [ ] All Smart City services - Refactor to use runtime surfaces
- [ ] Remove ad hoc state storage
- [ ] Ensure contracts compliance

#### Realms

- [ ] All realms - Recreate aligned to contracts
- [ ] Extract business logic from business_enablement_old
- [ ] Wire agents correctly

---

## 6. Decision Log

### Protocol Decision

**Decision:** Contracts = Protocols (no separate protocol layer)

**Rationale:**
- Protocols always get out of sync
- Contracts are the source of truth
- Single source of truth prevents drift
- Simpler architecture

**Implementation:**
- Contracts use `@runtime_checkable Protocol`
- Services implement contracts directly
- No separate `protocols/` directory

---

### State Architecture Decision

**Decision:** State Surface coordinates all state

**Rationale:**
- Current architecture has ad hoc state everywhere
- Need single source of truth
- State Surface coordinates, doesn't store

**Implementation:**
- State Surface coordinates with Traffic Cop (session state)
- State Surface coordinates with Runtime Plane (execution state)
- State Surface coordinates with Conductor (workflow state)
- No ad hoc state storage in services/agents

---

## 6. Detailed File-by-File Mapping

### 6.1 Root Directory Files

| File | Current | New Location | Action | Refactor Needed |
|------|---------|--------------|--------|-----------------|
| `docker-compose.yml` | `symphainy_source/` | `symphainy_source_code/` | ✅ KEEP | Update paths |
| `docker-compose.prod.yml` | `symphainy_source/` | `symphainy_source_code/` | ✅ KEEP | Update paths |
| `docker-compose.test.yml` | `symphainy_source/` | `symphainy_source_code/` | ✅ KEEP | Update paths |
| `docker-compose.ci.yml` | `symphainy_source/` | `symphainy_source_code/` | ✅ KEEP | Update paths |
| `README.md` | `symphainy_source/` | `symphainy_source_code/` | ✅ KEEP | Update for new architecture |

### 6.2 Platform Root Files

| File | Current | New Location | Action | Refactor Needed |
|------|---------|--------------|--------|-----------------|
| `main.py` | `symphainy-platform/` | `symphainy_source_code/main.py` | ✅ REBUILD | Complete rebuild (~150 lines) |
| `pyproject.toml` | `symphainy-platform/` | `symphainy_source_code/pyproject.toml` | ✅ KEEP | Update dependencies |
| `Dockerfile` | `symphainy-platform/` | `symphainy_source_code/Dockerfile` | ✅ KEEP | Update paths |
| `celery_app.py` | `symphainy-platform/` | `symphainy_source_code/celery_app.py` | ⚠️ REVIEW | May not be needed |

### 6.3 Bases Directory

| File | Current | New Location | Action | Refactor Needed |
|------|---------|--------------|--------|-----------------|
| `foundation_service_base.py` | `bases/` | `bases/foundation_service_base.py` | ✅ KEEP | None |
| `realm_service_base.py` | `bases/` | `bases/realm_service_base.py` | ✅ KEEP | Review state patterns |
| `orchestrator_base.py` | `bases/` | `bases/orchestrator_base.py` | ✅ KEEP | Review agent initialization |
| `platform_capabilities_mixin.py` | `bases/mixins/` | `bases/mixins/platform_capabilities_mixin.py` | ✅ KEEP | None |

### 6.4 Foundations Directory

| Directory | Current | New Location | Action | Refactor Needed |
|-----------|---------|--------------|--------|-----------------|
| `di_container/` | `foundations/` | `foundations/di_container/` | ✅ KEEP | Review initialization order |
| `public_works_foundation/` | `foundations/` | `foundations/public_works_foundation/` | ✅ KEEP | Review abstractions |
| `curator_foundation/` | `foundations/` | `foundations/curator_foundation/` | ✅ KEEP | Review service discovery |
| `agentic_foundation/` | `foundations/` | `foundations/agentic_foundation/` | ✅ KEEP | Add grounded reasoning base |
| `experience_foundation/` | `foundations/` | `foundations/experience_foundation/` | ✅ KEEP | Review for new architecture |

### 6.5 Runtime Plane

| File | Current | New Location | Action | Refactor Needed |
|------|---------|--------------|--------|-----------------|
| `runtime_plane_service.py` | `planes/runtime_plane/` | `runtime/runtime_plane_service.py` | ✅ KEEP | Review state architecture |
| `agent_runtime.py` | `planes/runtime_plane/` | `runtime/agent_runtime.py` | ✅ KEEP | None |
| `state_store.py` | `planes/runtime_plane/` | `runtime/state_store.py` | ✅ KEEP | Review for state surface |
| `session_surface.py` | ❌ MISSING | `runtime/session_surface.py` | ✅ CREATE | NEW |
| `state_surface.py` | ❌ MISSING | `runtime/state_surface.py` | ✅ CREATE | NEW |
| `execution_surface.py` | ❌ MISSING | `runtime/execution_surface.py` | ✅ CREATE | NEW |
| `intent_surface.py` | ❌ MISSING | `runtime/intent_surface.py` | ✅ CREATE | NEW |

### 6.6 Backend Realms

| Directory | Current | New Location | Action | Refactor Needed |
|-----------|---------|--------------|--------|-----------------|
| `smart_city/` | `backend/smart_city/` | `smart_city/` | ✅ KEEP | Refactor to use runtime surfaces |
| `solution/` | `backend/solution/` | `realms/solution/` | ✅ REBUILD | Recreate aligned to contracts |
| `journey/` | `backend/journey/` | `realms/journey/` | ✅ REBUILD | Recreate aligned to contracts |
| `content/` | `backend/content/` | `realms/content/` | ✅ REBUILD | Recreate aligned to contracts |
| `insights/` | `backend/insights/` | `realms/insights/` | ✅ REBUILD | Recreate aligned to contracts |
| `business_enablement_old/` | `backend/business_enablement_old/` | ❌ ARCHIVE | ✅ EXTRACT | Extract agents only |

### 6.7 Agents

| Agent | Current | New Location | Action | Refactor Needed |
|-------|---------|--------------|--------|-----------------|
| `GuideCrossDomainAgent` | `backend/solution/agents/` | `realms/solution/agents/` | ✅ KEEP | Review for grounded reasoning |
| `CoexistenceBlueprintSpecialist` | `backend/business_enablement_old/agents/` | `realms/journey/agents/` | ✅ EXTRACT | Refactor to GroundedReasoningAgentBase |
| `WorkflowGenerationSpecialist` | `backend/business_enablement_old/agents/` | `realms/journey/agents/` | ✅ EXTRACT | Refactor to GroundedReasoningAgentBase |
| `SOPGenerationSpecialist` | `backend/business_enablement_old/agents/` | `realms/journey/agents/` | ✅ EXTRACT | Refactor to GroundedReasoningAgentBase |
| `RoadmapProposalSpecialist` | `backend/business_enablement_old/agents/` | `realms/solution/agents/` | ✅ EXTRACT | Refactor to GroundedReasoningAgentBase |
| `BusinessAnalysisSpecialist` | `backend/business_enablement_old/agents/` | `realms/solution/agents/` | ✅ EXTRACT | Refactor to GroundedReasoningAgentBase |

---

## 7. Anti-Patterns Found

### 7.1 Direct State Storage

**Location:** `backend/business_enablement_old/agents/declarative_agent_base.py:110`

**Issue:**
```python
self.conversation_history: List[Dict[str, Any]] = []  # ❌ ANTI-PATTERN
```

**Fix:** Use State Surface for conversation state

### 7.2 Agents Managing State Lifecycle

**Location:** `backend/business_enablement_old/agents/declarative_agent_base.py:108-109`

**Issue:**
```python
self.stateful = self.agent_config.get("stateful", False)
self.max_conversation_history = self.agent_config.get("max_conversation_history", 10)
```

**Fix:** State Surface coordinates state, agents request state

### 7.3 Ad Hoc State Storage in Services

**Status:** ✅ **NOT FOUND** (grep search found no instances)

**Action:** ✅ **CLEAN** - No ad hoc state storage in services

---

## 8. Next Steps

### Phase 1: Foundation (Week 1) - ✅ **IMPLEMENTATION PLAN CREATED**

**See:** `docs/PHASE1_IMPLEMENTATION_PLAN.md` for detailed implementation guide

1. ✅ Create contracts (all 13 contracts)
2. ✅ Create runtime surfaces (4 surfaces)
3. ✅ Create grounded reasoning base
4. ✅ Review and refactor base classes

**Implementation Plan Includes:**
- Detailed file structures for all contracts
- Implementation patterns for all surfaces
- Grounded reasoning base implementation
- Step-by-step implementation order
- Testing strategy
- Success validation criteria

### Phase 2: Core Infrastructure (Week 2)
1. ✅ Refactor foundations (review initialization order)
2. ✅ Refactor Smart City services (use runtime surfaces)
3. ✅ Refactor runtime plane (integrate surfaces)

### Phase 3: Realms (Week 3-4)
1. ✅ Recreate Content Realm (aligned to contracts)
2. ✅ Recreate Insights Realm (aligned to contracts)
3. ✅ Recreate Journey Realm (aligned to contracts, extract agents)
4. ✅ Recreate Solution Realm (aligned to contracts, extract agents)

### Phase 4: Experience Plane (Week 5)
1. ✅ Create experience/rest/ handlers
2. ✅ Create experience/websocket/ handlers
3. ✅ Create experience/adapters/ for frontend

### Phase 5: Integration & Testing (Week 6)
1. ✅ Wire everything together
2. ✅ Test end-to-end flows
3. ✅ Validate against MVP requirements

---

## 9. Summary

### What We're Keeping (Mostly Reusable)
- ✅ Foundations (with refactoring)
- ✅ Base classes (with minor review)
- ✅ Smart City services (with refactoring)
- ✅ Runtime Plane core (with surface additions)
- ✅ Utilities (keep as-is)
- ✅ Config files (keep as-is)
- ✅ Docker compose files (update paths)

### What We're Rebuilding (90-100%)
- ✅ All Realms (Content, Insights, Journey, Solution)
- ✅ Main.py (complete rebuild)
- ✅ Experience Plane (new)

### What We're Creating (NEW)
- ✅ Contracts (13 contracts)
- ✅ Runtime Surfaces (4 surfaces)
- ✅ Grounded Reasoning Base
- ✅ Experience Plane

### What We're Extracting
- ✅ Critical reasoning agents from business_enablement_old

### What We're NOT Bringing
- ❌ Archived code
- ❌ Legacy implementations
- ❌ Test files (defer to CI/CD roadmap)
- ❌ Historical documentation

---

**Last Updated:** January 2026  
**Status:** ✅ **COMPLETE** - Ready for rebuild
