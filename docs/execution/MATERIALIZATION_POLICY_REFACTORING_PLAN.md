# Materialization Policy Refactoring Plan

**Date:** January 17, 2026  
**Status:** 📋 **REFACTORING PLAN** (Post-Phase 1 Course Correction)  
**Goal:** Align artifact storage with Materialization Policy architecture

---

## Executive Summary

**Course Correction:** The CTO's architectural guidance (`architecting_for_artifacts.md`) introduces a fundamental shift:

> **"SymphAIny persists meaning by default. Everything else is a policy decision."**

**Key Changes:**
1. **Materialization Policy** - Artifacts are ephemeral by default, persisted by policy
2. **Structured Results** - Realm outputs have `semantic_payload` and `renderings`
3. **Runtime Enforcement** - Runtime (not realms) evaluates policy and stores artifacts
4. **Platform Memory vs Client Memory** - Platform persists meaning, not renderings

**Impact on Phase 1 Work:**
- ✅ `ArtifactStorageProtocol` - Still valid (just called by Runtime, not realms)
- ✅ `ArtifactStorageAbstraction` - Still valid (just called by Runtime, not realms)
- ✅ Supabase schema extension - Still valid
- ⚠️ **NEW:** Materialization Policy evaluation in Runtime
- ⚠️ **NEW:** Structured result format from realms
- ⚠️ **NEW:** Runtime materialization logic

**MVP Strategy:**
- Use Materialization Policy override to persist artifacts (demonstrates policy pattern)
- This makes MVP a **first example** of platform policy overrides

---

## Architectural Alignment Check

### ✅ Confirms Current Architecture

1. **Runtime Execution Engine** - Exists and orchestrates execution
   - `ExecutionLifecycleManager` handles intent → realm → result flow
   - Perfect place to add Materialization Policy evaluation

2. **Realm Results** - Currently return `{"artifacts": {...}, "events": [...]}`
   - Can be extended to structured results with `semantic_payload` and `renderings`
   - Backward compatible (existing format is valid)

3. **State Surface** - Stores execution state
   - Already stores artifacts in execution state
   - Can continue storing semantic payload (platform memory)

4. **Smart City / Solution Configuration** - Policy configuration exists
   - `PolicyConfigurationService` pattern exists
   - Can extend for Materialization Policy

### ✅ Aligns with Materialization Policy Vision

1. **Platform-Native Records (Always Stored)**
   - ✅ Intent - Already stored in Runtime
   - ✅ Journey - Already stored in State Surface
   - ✅ State transitions - Already stored in State Surface
   - ✅ Decisions & governance - Already stored in WAL
   - ✅ References to outcomes - Can store artifact_id references

2. **Derived Artifacts (Conditionally Stored)**
   - ⚠️ Currently: Artifacts stored directly by realms (anti-pattern)
   - ✅ Target: Artifacts stored by Runtime after policy evaluation

3. **Materialization Policy Flow**
   ```
   Realm produces result
   → Smart City tags it with intent + lineage
   → Runtime evaluates Materialization Policy
   → Runtime either:
      - persists (via ArtifactStorageAbstraction)
      - caches
      - discards
   ```

---

## Refactoring Plan

### Phase 1: Materialization Policy Infrastructure (Days 1-2) 🔴

#### 1.1 Create Materialization Policy Protocol

**File:** `symphainy_platform/runtime/policies/materialization_policy_protocol.py`

**Purpose:** Define contract for materialization policy evaluation

```python
from typing import Protocol, Dict, Any, Optional
from enum import Enum

class MaterializationDecision(Enum):
    """Materialization decision types."""
    PERSIST = "persist"      # Store artifact permanently
    CACHE = "cache"         # Store temporarily (e.g., for session)
    DISCARD = "discard"      # Don't store (ephemeral)

class MaterializationPolicyProtocol(Protocol):
    """Protocol for materialization policy evaluation."""
    
    async def evaluate_policy(
        self,
        result_type: str,  # 'workflow', 'sop', 'solution', etc.
        semantic_payload: Dict[str, Any],
        renderings: Dict[str, Any],
        intent: Intent,
        context: ExecutionContext,
        solution_config: Optional[Dict[str, Any]] = None
    ) -> MaterializationDecision:
        """
        Evaluate materialization policy for a realm result.
        
        Returns:
            MaterializationDecision: PERSIST, CACHE, or DISCARD
        """
        ...
    
    def get_default_policy(self) -> Dict[str, str]:
        """
        Get default materialization policy.
        
        Returns:
            Dict mapping result_type to decision (default: all ephemeral)
        """
        ...
```

#### 1.2 Create Materialization Policy Abstraction

**File:** `symphainy_platform/runtime/policies/materialization_policy_abstraction.py`

**Purpose:** Implement policy evaluation logic

**Default Policy (Platform-Native):**
```python
DEFAULT_POLICY = {
    # Platform-native records (always stored in State Surface / WAL)
    "intent": "persist",           # Always stored
    "journey": "persist",          # Always stored
    "state_transition": "persist", # Always stored
    "governance_decision": "persist", # Always stored
    
    # Derived artifacts (ephemeral by default)
    "workflow": "discard",         # Ephemeral by default
    "sop": "discard",              # Ephemeral by default
    "blueprint": "discard",        # Ephemeral by default
    "solution": "discard",         # Ephemeral by default
    "roadmap": "discard",          # Ephemeral by default
    "poc": "discard",              # Ephemeral by default
    "visual": "discard",           # Ephemeral by default
}
```

**MVP Override (Solution Configuration):**
```python
MVP_POLICY_OVERRIDE = {
    # MVP persists artifacts for demo purposes
    "workflow": "persist",
    "sop": "persist",
    "blueprint": "persist",
    "solution": "persist",
    "roadmap": "persist",
    "poc": "persist",
    "visual": "persist",
}
```

**Implementation:**
```python
class MaterializationPolicyAbstraction(MaterializationPolicyProtocol):
    """
    Materialization policy abstraction.
    
    Evaluates materialization policy based on:
    - Default platform policy (ephemeral by default)
    - Solution configuration overrides (client-specific)
    - Smart City governance rules (future)
    """
    
    def __init__(
        self,
        default_policy: Optional[Dict[str, str]] = None,
        solution_config: Optional[Dict[str, Any]] = None
    ):
        self.default_policy = default_policy or DEFAULT_POLICY
        self.solution_config = solution_config or {}
        self.logger = get_logger(self.__class__.__name__)
    
    async def evaluate_policy(
        self,
        result_type: str,
        semantic_payload: Dict[str, Any],
        renderings: Dict[str, Any],
        intent: Intent,
        context: ExecutionContext,
        solution_config: Optional[Dict[str, Any]] = None
    ) -> MaterializationDecision:
        """
        Evaluate materialization policy.
        
        Priority:
        1. Solution config override (highest priority)
        2. Default platform policy
        3. DISCARD (safest default)
        """
        # Check solution config override
        solution_policy = solution_config or self.solution_config
        materialization_policy = solution_policy.get("materialization_policy", {})
        
        if result_type in materialization_policy:
            decision_str = materialization_policy[result_type]
            if decision_str == "persist":
                return MaterializationDecision.PERSIST
            elif decision_str == "cache":
                return MaterializationDecision.CACHE
            elif decision_str == "discard":
                return MaterializationDecision.DISCARD
        
        # Check default policy
        if result_type in self.default_policy:
            decision_str = self.default_policy[result_type]
            if decision_str == "persist":
                return MaterializationDecision.PERSIST
            elif decision_str == "cache":
                return MaterializationDecision.CACHE
        
        # Default: DISCARD (ephemeral)
        return MaterializationDecision.DISCARD
    
    def get_default_policy(self) -> Dict[str, str]:
        """Get default materialization policy."""
        return self.default_policy.copy()
```

#### 1.3 Integrate with Runtime

**File:** `symphainy_platform/runtime/execution_lifecycle_manager.py`

**Changes:**
1. Inject `MaterializationPolicyAbstraction` and `ArtifactStorageAbstraction`
2. After realm execution, evaluate policy
3. Store artifacts if policy says PERSIST

**Code:**
```python
# In __init__
def __init__(
    self,
    intent_registry: IntentRegistry,
    state_surface: StateSurface,
    wal: WriteAheadLog,
    transactional_outbox: Optional[Any] = None,
    materialization_policy: Optional[MaterializationPolicyAbstraction] = None,
    artifact_storage: Optional[ArtifactStorageAbstraction] = None,
    solution_config: Optional[Dict[str, Any]] = None
):
    # ... existing code ...
    self.materialization_policy = materialization_policy
    self.artifact_storage = artifact_storage
    self.solution_config = solution_config or {}

# In execute() method, after Stage 5 (Handle Artifacts)
# Stage 5.5: Evaluate Materialization Policy and Store Artifacts
if artifacts and self.materialization_policy and self.artifact_storage:
    self.logger.info(f"Evaluating materialization policy for {len(artifacts)} artifacts")
    
    for artifact_key, artifact_data in artifacts.items():
        # Determine result_type from artifact_key or artifact_data
        result_type = self._infer_result_type(artifact_key, artifact_data)
        
        # Extract semantic_payload and renderings
        # (For MVP, treat entire artifact as renderings, extract semantic if available)
        semantic_payload = artifact_data.get("semantic_payload", {})
        renderings = artifact_data.copy()
        if "semantic_payload" in renderings:
            del renderings["semantic_payload"]
        
        # Evaluate policy
        decision = await self.materialization_policy.evaluate_policy(
            result_type=result_type,
            semantic_payload=semantic_payload,
            renderings=renderings,
            intent=intent,
            context=context,
            solution_config=self.solution_config
        )
        
        if decision == MaterializationDecision.PERSIST:
            # Store artifact
            try:
                storage_result = await self.artifact_storage.store_composite_artifact(
                    artifact_type=result_type,
                    artifact_data=renderings,
                    tenant_id=intent.tenant_id,
                    metadata={
                        "execution_id": execution_id,
                        "session_id": context.session_id,
                        "intent_id": intent.intent_id,
                        "intent_type": intent.intent_type,
                        "semantic_payload_stored": bool(semantic_payload)
                    }
                )
                
                if storage_result.get("success"):
                    # Store artifact_id reference in state (platform memory)
                    artifacts[f"{artifact_key}_artifact_id"] = storage_result["artifact_id"]
                    artifacts[f"{artifact_key}_storage_path"] = storage_result["storage_path"]
                    self.logger.info(f"Artifact stored: {storage_result['artifact_id']}")
            except Exception as e:
                self.logger.warning(f"Failed to store artifact {artifact_key}: {e}")
        
        elif decision == MaterializationDecision.CACHE:
            # Cache temporarily (e.g., in State Surface)
            self.logger.debug(f"Artifact {artifact_key} cached (not persisted)")
        
        elif decision == MaterializationDecision.DISCARD:
            # Discard (ephemeral)
            self.logger.debug(f"Artifact {artifact_key} discarded (ephemeral)")

def _infer_result_type(self, artifact_key: str, artifact_data: Dict[str, Any]) -> str:
    """Infer result_type from artifact_key or artifact_data."""
    # Try artifact_key first
    if artifact_key in ["workflow", "sop", "blueprint", "solution", "roadmap", "poc"]:
        return artifact_key
    
    # Try artifact_data
    if "result_type" in artifact_data:
        return artifact_data["result_type"]
    
    # Default
    return "unknown"
```

---

### Phase 2: Structured Results (Days 3-4) 🟡

#### 2.1 Update Realm Results to Structured Format

**Purpose:** Prepare realms to return structured results (backward compatible)

**Current Format:**
```python
{
    "artifacts": {
        "workflow": {...},
        "workflow_visual": {...}
    },
    "events": [...]
}
```

**Target Format (Structured):**
```python
{
    "artifacts": {
        "workflow": {
            "result_type": "workflow",
            "semantic_payload": {
                "workflow_id": "...",
                "steps": [...],
                "metadata": {...}
            },
            "renderings": {
                "workflow": {...},
                "workflow_visual": {...}
            }
        }
    },
    "events": [...]
}
```

**Migration Strategy:**
- **Phase 2.1:** Update orchestrators to return structured results (optional)
- **Phase 2.2:** Runtime handles both formats (backward compatible)
- **Phase 2.3:** Gradually migrate realms to structured format

**For MVP:** Keep current format, Runtime extracts semantic_payload and renderings

---

### Phase 3: Runtime Integration (Day 5) 🔴

#### 3.1 Update Runtime Initialization

**File:** `symphainy_source_code/runtime_main.py`

**Changes:**
1. Create `MaterializationPolicyAbstraction` with MVP override
2. Get `ArtifactStorageAbstraction` from Public Works
3. Pass to `ExecutionLifecycleManager`

**Code:**
```python
async def initialize_runtime():
    # ... existing initialization ...
    
    # Get Public Works Foundation Service
    public_works = di_container.get("public_works_foundation_service")
    
    # Get Artifact Storage Abstraction
    artifact_storage = public_works.get_artifact_storage_abstraction() if public_works else None
    
    # Create Materialization Policy with MVP override
    from symphainy_platform.runtime.policies.materialization_policy_abstraction import (
        MaterializationPolicyAbstraction,
        MVP_POLICY_OVERRIDE
    )
    
    materialization_policy = MaterializationPolicyAbstraction(
        default_policy=None,  # Use default
        solution_config={
            "materialization_policy": MVP_POLICY_OVERRIDE  # MVP override
        }
    )
    
    # Create Execution Lifecycle Manager with policy and storage
    execution_lifecycle_manager = ExecutionLifecycleManager(
        intent_registry=intent_registry,
        state_surface=state_surface,
        wal=wal,
        transactional_outbox=transactional_outbox,
        materialization_policy=materialization_policy,
        artifact_storage=artifact_storage,
        solution_config={"materialization_policy": MVP_POLICY_OVERRIDE}
    )
```

---

### Phase 4: Testing & Validation (Day 6) 🟢

#### 4.1 Update Tests

**Files:**
- `tests/integration/test_execution_completion.py`
- `tests/integration/agents/test_agent_interactions_comprehensive.py`
- `tests/integration/visual/test_visual_generation_comprehensive.py`

**Changes:**
- Verify artifacts are stored when policy says PERSIST
- Verify artifacts are NOT stored when policy says DISCARD
- Verify MVP override works (artifacts persisted)

#### 4.2 Smoke Test

**File:** `tests/integration/test_materialization_policy_smoke.py`

**Tests:**
1. Policy evaluation (PERSIST, CACHE, DISCARD)
2. MVP override (all artifacts persisted)
3. Default policy (all artifacts discarded)
4. Artifact storage after policy evaluation

---

## Implementation Checklist

### Phase 1: Materialization Policy Infrastructure
- [ ] Create `MaterializationPolicyProtocol`
- [ ] Create `MaterializationPolicyAbstraction`
- [ ] Define default policy (ephemeral by default)
- [ ] Define MVP policy override (persist for demo)
- [ ] Integrate with `ExecutionLifecycleManager`
- [ ] Add policy evaluation after realm execution
- [ ] Add artifact storage after policy evaluation

### Phase 2: Structured Results (Optional for MVP)
- [ ] Define structured result format
- [ ] Update Runtime to handle both formats
- [ ] Update orchestrators to return structured results (optional)

### Phase 3: Runtime Integration
- [ ] Update `runtime_main.py` to create policy abstraction
- [ ] Pass policy and storage to `ExecutionLifecycleManager`
- [ ] Configure MVP override

### Phase 4: Testing & Validation
- [ ] Create materialization policy smoke test
- [ ] Update execution completion tests
- [ ] Verify MVP override works
- [ ] Verify default policy works (ephemeral)

---

## MVP Policy Override Example

**File:** `symphainy_source_code/config/mvp_materialization_policy.yaml`

```yaml
# MVP Materialization Policy Override
# This demonstrates how clients can configure artifact persistence

materialization_policy:
  # Platform-native records (always persisted in State Surface / WAL)
  intent: persist
  journey: persist
  state_transition: persist
  governance_decision: persist
  
  # Derived artifacts (MVP persists for demo purposes)
  workflow: persist
  sop: persist
  blueprint: persist
  solution: persist
  roadmap: persist
  poc: persist
  visual: persist
  
  # Future: Client-specific overrides
  # business_analysis: cache  # Cache for session
  # chart: discard            # Ephemeral
```

**Usage:**
```python
# In runtime_main.py
solution_config = load_yaml_config("config/mvp_materialization_policy.yaml")
materialization_policy = MaterializationPolicyAbstraction(
    solution_config=solution_config
)
```

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Materialization Policy abstraction created
- ✅ Default policy defined (ephemeral by default)
- ✅ MVP override defined (persist for demo)
- ✅ Runtime evaluates policy after realm execution
- ✅ Runtime stores artifacts when policy says PERSIST

### Phase 2 Complete When:
- ✅ Structured results format defined
- ✅ Runtime handles both formats (backward compatible)
- ✅ Orchestrators can return structured results (optional)

### Phase 3 Complete When:
- ✅ Runtime initialized with policy and storage
- ✅ MVP override configured
- ✅ Artifacts stored after policy evaluation

### Phase 4 Complete When:
- ✅ All tests passing
- ✅ MVP override verified (artifacts persisted)
- ✅ Default policy verified (artifacts discarded)
- ✅ Platform demonstrates policy pattern

---

## Architectural Benefits

### ✅ Preserves Platform Vision
- Platform persists meaning by default
- Artifacts are ephemeral by default
- Policy-driven persistence (not hardcoded)

### ✅ Enables MVP
- MVP uses policy override to persist artifacts
- Demonstrates platform policy pattern
- No architectural compromise

### ✅ Future-Proof
- Clients can configure their own policies
- Smart City can enforce governance rules
- Platform remains coordination-first, memory-minimal

### ✅ Clean Separation
- Realms produce results (don't store)
- Runtime evaluates policy (governance)
- Runtime stores artifacts (enforcement)

---

## Risk Mitigation

### Risk 1: Breaking Changes
**Mitigation:** Backward compatible (Runtime handles both formats)

### Risk 2: Policy Complexity
**Mitigation:** Start simple (default + override), extend later

### Risk 3: Performance Impact
**Mitigation:** Policy evaluation is fast (dict lookup), storage is async

---

## Timeline Summary

| Phase | Days | Deliverables |
|-------|------|--------------|
| Phase 1: Policy Infrastructure | 1-2 | Protocol, Abstraction, Runtime Integration |
| Phase 2: Structured Results | 3-4 | Format definition, Runtime support (optional) |
| Phase 3: Runtime Integration | 5 | runtime_main.py updates, MVP override |
| Phase 4: Testing | 6 | Tests, validation |
| **Total** | **6** | **Materialization Policy Complete** |

---

## Next Steps

1. **Review this plan** - Ensure alignment with CTO's vision
2. **Begin Phase 1** - Create Materialization Policy infrastructure
3. **Test incrementally** - Verify policy evaluation works
4. **Integrate with Runtime** - Add policy evaluation to execution flow
5. **Configure MVP override** - Demonstrate policy pattern

---

**Last Updated:** January 17, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Priority:** 🔴 **CRITICAL** (Architectural Alignment)
