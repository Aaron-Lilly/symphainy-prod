# Materialization Policy Pattern Analysis

**Date:** January 19, 2026  
**Status:** 📋 **PATTERN ANALYSIS**  
**Goal:** Understand how policies are managed across the platform

---

## Executive Summary

**Key Finding:** Policies are NOT in Public Works. They follow a Smart City pattern:

1. **Smart City Primitives** = Policy validation (business logic decisions)
2. **Smart City SDKs** = Policy coordination (prepare execution contracts)
3. **Public Works** = Infrastructure only (raw data access, storage operations)
4. **Runtime** = Policy enforcement (uses Primitives to validate)

**Materialization Policy Should Follow This Pattern:**
- Policy decision → Smart City Primitive (like `SecurityGuardPrimitives`)
- Policy enforcement → Public Works (storage operations)
- Policy configuration → Smart City SDK (like `CityManagerSDK`)

---

## Current Policy Pattern Analysis

### Pattern 1: Security Policy (Security Guard)

#### **Smart City Primitive:**
```python
# civic_systems/smart_city/primitives/security_guard_primitives.py
class SecurityGuardPrimitives:
    """Policy validation - pure functions, deterministic, used by Runtime only."""
    
    @staticmethod
    async def check_permission(
        user_id: str,
        tenant_id: str,
        action: str,
        resource: Optional[str],
        policy_store: PolicyStore,
        execution_contract: Dict[str, Any]
    ) -> bool:
        """Check if user has permission (Primitive - policy decision)."""
        # 1. Load policies from policy_store
        # 2. Evaluate policies (deterministic)
        # 3. Return decision (True/False)
```

#### **Smart City SDK:**
```python
# civic_systems/smart_city/sdk/security_guard_sdk.py
class SecurityGuardSDK:
    """Coordination - prepares execution contracts for Runtime validation."""
    
    def __init__(
        self,
        auth_abstraction: AuthenticationProtocol,  # From Public Works
        tenant_abstraction: TenancyProtocol,        # From Public Works
        policy_resolver: Optional[Any] = None
    ):
        # Uses Public Works abstractions to get raw data
        # Prepares execution contracts
    
    async def authenticate(...) -> AuthenticationResult:
        """Coordinate authentication, prepare execution contract."""
        # Uses auth_abstraction to get raw auth data
        # Prepares execution contract with policies
        # Returns contract for Runtime validation
```

#### **Public Works:**
```python
# foundations/public_works/abstractions/auth_abstraction.py
class AuthAbstraction(AuthenticationProtocol):
    """Infrastructure - provides raw authentication data only."""
    
    async def authenticate(...) -> Optional[Dict[str, Any]]:
        """Returns raw data - no business logic, no policy decisions."""
        # Raw authentication data from Supabase
        # No policy evaluation
```

#### **Runtime:**
```python
# Runtime uses SecurityGuardPrimitives to validate execution contracts
# Runtime does NOT use SecurityGuardSDK (SDKs are for Experience/Realms)
```

---

### Pattern 2: Rate Limiting Policy (Traffic Cop)

#### **Smart City Primitive:**
```python
# civic_systems/smart_city/primitives/traffic_cop_primitives.py
class TrafficCopPrimitives:
    """Policy validation - pure functions, deterministic."""
    
    @staticmethod
    async def check_rate_limit(
        tenant_id: str,
        user_id: Optional[str],
        action: str,
        rate_limit_store: RateLimitStore,
        execution_contract: Dict[str, Any]
    ) -> bool:
        """Check rate limit (Primitive - policy decision)."""
        # 1. Get rate limit policies from execution contract
        # 2. Check rate limit store
        # 3. Return decision (True/False)
```

#### **Smart City SDK:**
```python
# civic_systems/smart_city/sdk/traffic_cop_sdk.py
class TrafficCopSDK:
    """Coordination - prepares execution contracts."""
    
    async def validate_session(...) -> SessionValidationResult:
        """Coordinate session validation, prepare execution contract."""
        # Prepares execution contract with rate limit policies
```

#### **Public Works:**
```python
# Public Works provides infrastructure (Redis for rate limit tracking)
# No policy decisions in Public Works
```

---

### Pattern 3: Data Governance Policy (Data Steward)

#### **Smart City Primitive:**
```python
# civic_systems/smart_city/primitives/data_steward_primitives.py
class DataStewardPrimitives:
    """Policy validation - pure functions, deterministic."""
    
    async def check_data_permission(
        self,
        data_id: str,
        user_id: str,
        tenant_id: str,
        action: str
    ) -> DataPermissionCheck:
        """Check data permission (Primitive - policy decision)."""
        # Policy decision: is data access allowed?
```

#### **Public Works:**
```python
# Public Works provides infrastructure (data storage, retrieval)
# No policy decisions in Public Works
```

---

## Materialization Policy Pattern (Proposed)

### **Smart City Primitive:**
```python
# civic_systems/smart_city/primitives/materialization_policy_primitives.py
class MaterializationPolicyStore:
    """Policy store for materialization policies."""
    
    async def get_materialization_policy(
        self,
        tenant_id: str,
        solution_id: str,
        result_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get materialization policy for tenant/solution/result_type."""
        # MVP: Load from config file
        # Full: Query ArangoDB graph for policies
    
    async def evaluate_policy(
        self,
        policy: Dict[str, Any],
        result_type: str,
        semantic_payload: Dict[str, Any],
        renderings: Dict[str, Any],
        intent: Any,
        context: Any
    ) -> str:  # "persist", "cache", "discard"
        """Evaluate materialization policy."""
        # Policy decision logic


class MaterializationPolicyPrimitives:
    """Policy validation - pure functions, deterministic, used by Runtime only."""
    
    @staticmethod
    async def evaluate_policy(
        result_type: str,
        semantic_payload: Dict[str, Any],
        renderings: Dict[str, Any],
        intent: Any,
        context: Any,
        policy_store: MaterializationPolicyStore,
        execution_contract: Dict[str, Any]
    ) -> MaterializationDecision:  # PERSIST, CACHE, DISCARD
        """Evaluate materialization policy (Primitive - policy decision)."""
        # 1. Get policy from policy_store
        # 2. Evaluate policy (deterministic)
        # 3. Return decision (PERSIST, CACHE, DISCARD)
```

### **Smart City SDK (Optional):**
```python
# civic_systems/smart_city/sdk/materialization_policy_sdk.py
class MaterializationPolicySDK:
    """Coordination - prepares execution contracts for Runtime validation."""
    
    def __init__(
        self,
        config_abstraction: Optional[Any] = None  # From Public Works
    ):
        # Uses Public Works abstractions to get raw config data
        # Prepares execution contracts
    
    async def configure_materialization_policy(
        self,
        solution_id: str,
        policy_overrides: Dict[str, str]
    ) -> Dict[str, Any]:
        """Configure materialization policy, prepare execution contract."""
        # Prepares execution contract with policy configuration
```

### **Public Works:**
```python
# foundations/public_works/abstractions/artifact_storage_abstraction.py
class ArtifactStorageAbstraction(ArtifactStorageProtocol):
    """Infrastructure - provides artifact storage operations only."""
    
    async def store_artifact(...) -> Dict[str, Any]:
        """Store artifact - no policy decisions, just infrastructure."""
        # Stores artifact in GCS/Supabase
        # No policy evaluation
```

### **Runtime:**
```python
# Runtime uses MaterializationPolicyPrimitives to evaluate policy
# Runtime uses ArtifactStorageAbstraction to store artifacts
# Runtime enforces policy decisions
```

---

## Key Insights

### ✅ **Policies Are NOT Infrastructure**
- Policies are business logic decisions (governance)
- Public Works is infrastructure only (raw data access, storage)
- Policies belong in Smart City (governance layer)

### ✅ **Policy Pattern:**
1. **Primitive** = Policy validation (pure functions, deterministic)
2. **SDK** = Policy coordination (prepare execution contracts)
3. **Public Works** = Infrastructure (raw data, storage)
4. **Runtime** = Policy enforcement (uses Primitives)

### ✅ **No Policy Proliferation:**
- All policies follow same pattern
- Policies centralized in Smart City Primitives
- Public Works provides infrastructure only
- Runtime enforces policies using Primitives

### ✅ **Materialization Policy Should:**
- Follow Smart City pattern (not Public Works pattern)
- Be in `MaterializationPolicyPrimitives` (like `SecurityGuardPrimitives`)
- Use `MaterializationPolicyStore` (like `PolicyStore`)
- Runtime uses Primitive to evaluate policy
- Public Works provides storage operations (not policy decisions)

---

## Comparison: Current vs. Proposed

### **Current (Wrong Pattern):**
```
runtime/policies/materialization_policy_abstraction.py  ❌
  → Runtime layer (should be Smart City)
  → Called "abstraction" (should be "primitive")
  → Mixed with Runtime execution logic
```

### **Proposed (Correct Pattern):**
```
civic_systems/smart_city/primitives/materialization_policy_primitives.py  ✅
  → Smart City layer (governance)
  → Called "primitive" (consistent with other policies)
  → Pure functions, deterministic, used by Runtime only
```

---

## Benefits of Following Pattern

### ✅ **Consistency:**
- All policies follow same pattern
- Easy to understand and maintain
- Clear separation of concerns

### ✅ **No Proliferation:**
- Policies centralized in Smart City
- Public Works stays infrastructure-only
- Runtime enforces policies consistently

### ✅ **Proper Layering:**
- Policy decisions → Smart City (governance)
- Policy enforcement → Runtime (execution)
- Infrastructure → Public Works (storage)

---

## Next Steps

1. **Create MaterializationPolicyPrimitives** (follows SecurityGuardPrimitives pattern)
2. **Create MaterializationPolicyStore** (follows PolicyStore pattern)
3. **Update Runtime** to use Primitive (not abstraction)
4. **Keep ArtifactStorageAbstraction** in Public Works (infrastructure only)

---

**Last Updated:** January 19, 2026  
**Status:** 📋 **PATTERN ANALYSIS COMPLETE**  
**Priority:** 🔴 **CRITICAL** (Architectural Alignment)
