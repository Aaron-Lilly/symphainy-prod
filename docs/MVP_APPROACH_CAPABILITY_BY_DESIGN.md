# MVP Approach: Capability by Design, Implementation by Policy

**Date:** January 20, 2026  
**Status:** 📋 **Architectural Principle**  
**Purpose:** Document the MVP approach for building capabilities with permissive policies

---

## Key Principle

> **Build real infrastructure/capabilities (secure by design), but use permissive policies for MVP (open by policy).**

**Why This Matters:**
- MVP is a demo showcase - won't leave anyone alone with it
- Build the right architecture from the start
- Policies can be tightened for production without changing code
- Example: Zero trust policy that is secure by design, but open by policy for MVP

---

## The Pattern

### 1. Build Real Infrastructure (Capability by Design)

**What:** Build the actual infrastructure, services, and capabilities that will be needed in production.

**Examples:**
- Policy evaluation engine (not hard-coded defaults)
- Lifecycle state machine (not simple status fields)
- Authentication/authorization infrastructure (not bypasses)
- TTL enforcement jobs (not manual cleanup)
- Vector search with pluggable backends (not vendor lock-in)

**Why:**
- Architecture is correct from day one
- No need to rebuild for production
- Infrastructure is "secure by design"

---

### 2. Use Permissive Policies for MVP (Implementation by Policy)

**What:** Configure policies to be permissive for MVP, allowing easy demo/showcase.

**Examples:**
- Materialization policy: Allow all materialization types (no restrictions)
- Lifecycle transitions: Any user can transition any state (no restrictions)
- Access control: Permissive access for demo (can be tightened later)
- TTL: Longer TTLs for MVP (30 days vs 7 days in production)

**Why:**
- Easy to demo and showcase
- No friction during development
- Policies can be tightened without code changes

---

### 3. Tighten Policies for Production (No Code Changes)

**What:** Update policy configuration to be more restrictive for production.

**Examples:**
- Materialization policy: Restrict certain materialization types
- Lifecycle transitions: Require approval for certain transitions
- Access control: Enforce strict access rules
- TTL: Shorter TTLs for production

**Why:**
- No code changes needed
- Infrastructure already supports it
- Just update policy configuration

---

## Implementation Pattern

### Step 1: Design the Real Infrastructure

```python
# Real policy evaluation infrastructure
class MaterializationPolicyStore:
    async def evaluate_policy(
        self,
        tenant_id: str,
        artifact_type: str,
        requested_type: str
    ) -> MaterializationPolicyDecision:
        # Real policy evaluation logic
        # Supports tenant-specific policies
        # Supports platform defaults
        # Supports policy inheritance
        pass
```

### Step 2: Create Permissive MVP Policies

```python
# MVP permissive policy (platform default)
MVP_MATERIALIZATION_POLICY = {
    "allow_all_types": True,
    "default_ttl_days": 30,
    "no_restrictions": True,
    "policy_version": "mvp_1.0"
}

# Store in policy store
await policy_store.create_platform_default_policy(
    policy_data=MVP_MATERIALIZATION_POLICY
)
```

### Step 3: Use Policy Store in Implementation

```python
# Data Steward Primitives uses policy store (not hard-coded defaults)
async def authorize_materialization(
    self,
    contract_id: str,
    tenant_id: str,
    materialization_policy: MaterializationPolicyStore
):
    # Look up policy (tenant-specific or platform default)
    policy = await materialization_policy.get_policy(tenant_id)
    
    # Evaluate policy
    decision = await materialization_policy.evaluate_policy(
        tenant_id=tenant_id,
        artifact_type=artifact_type,
        requested_type=requested_type
    )
    
    # Return decision based on policy
    return decision
```

### Step 4: Tighten Policies for Production (No Code Changes)

```python
# Production restrictive policy (just update configuration)
PRODUCTION_MATERIALIZATION_POLICY = {
    "allow_all_types": False,
    "allowed_types": ["deterministic", "semantic_embedding"],
    "default_ttl_days": 7,
    "require_approval": True,
    "policy_version": "production_1.0"
}

# Update policy store (no code changes needed)
await policy_store.update_platform_default_policy(
    policy_data=PRODUCTION_MATERIALIZATION_POLICY
)
```

---

## Where This Applies

### ✅ Phase 3.1: Materialization Policy

**Current State:**
- Hard-coded MVP defaults in `authorize_materialization()`
- No real policy evaluation

**MVP Approach:**
- Build real policy evaluation infrastructure
- Create policy store with permissive MVP policies
- Use policy store in implementation (not hard-coded defaults)

**Production:**
- Update policy configuration to be restrictive
- No code changes needed

---

### ✅ Phase 2.1: Lifecycle State Tracking

**Current State:**
- No lifecycle state tracking

**MVP Approach:**
- Build real lifecycle state machine
- Use permissive transition policies (any user can transition)
- Store transitions in WAL for audit

**Production:**
- Add transition restrictions via policy
- No code changes needed

---

### ✅ Other Potential Applications

1. **Access Control**
   - Build real auth infrastructure
   - Use permissive access for MVP
   - Tighten access rules for production

2. **TTL Enforcement**
   - Build real enforcement job
   - Use longer TTLs for MVP (30 days)
   - Use shorter TTLs for production (7 days)

3. **Vector Search**
   - Build pluggable backend interface
   - Use ArangoDB for MVP
   - Can swap backends for production without code changes

---

## Benefits

### 1. Architecture is Correct from Day One
- No need to rebuild for production
- Infrastructure is "secure by design"
- Policies are configuration, not code

### 2. Easy to Demo
- Permissive policies allow easy showcase
- No friction during development
- Can demonstrate full capabilities

### 3. Production Ready
- Just update policy configuration
- No code changes needed
- Infrastructure already supports it

### 4. Testable
- Can test with both permissive and strict policies
- Can test policy evaluation logic
- Can test policy inheritance

---

## Anti-Patterns to Avoid

### ❌ Hard-Coded Defaults
```python
# BAD: Hard-coded defaults
access_granted = True  # MVP: Allow access
```

### ❌ Bypasses
```python
# BAD: Bypass infrastructure
if mvp_mode:
    return allow_all()
```

### ❌ No Policy Infrastructure
```python
# BAD: No policy evaluation
# Just return True for MVP
```

---

## Good Patterns

### ✅ Policy Store with Permissive Defaults
```python
# GOOD: Real infrastructure with permissive defaults
policy = await policy_store.get_policy(tenant_id)
decision = await policy.evaluate(request)
return decision
```

### ✅ Configuration-Driven
```python
# GOOD: Policies are configuration
MVP_POLICY = {
    "allow_all_types": True,
    "default_ttl_days": 30
}
```

### ✅ Testable
```python
# GOOD: Can test with different policies
async def test_with_strict_policy():
    policy = StrictPolicy()
    decision = await evaluate(policy)
    assert decision.restricted == True
```

---

## Documentation Requirements

When implementing "capability by design, implementation by policy":

1. **Document the Infrastructure**
   - What infrastructure is built
   - How it works
   - What capabilities it provides

2. **Document the MVP Policies**
   - What policies are used for MVP
   - Why they are permissive
   - How to tighten them for production

3. **Document Production Policies**
   - What policies should be used for production
   - How to update policies
   - What restrictions to add

---

## Examples in Codebase

### Materialization Policy (Phase 3.1)

**Current:** Hard-coded defaults
```python
materialization_type = requested_type or "full_artifact"  # MVP default
```

**Target:** Policy store with permissive defaults
```python
policy = await materialization_policy_store.get_policy(tenant_id)
decision = await policy.evaluate(artifact_type, requested_type)
materialization_type = decision.allowed_type
```

---

## Checklist for Implementation

When implementing a feature with "capability by design, implementation by policy":

- [ ] Build real infrastructure/capability
- [ ] Create policy store/configuration
- [ ] Implement permissive MVP policies
- [ ] Use policy store in implementation (not hard-coded defaults)
- [ ] Document MVP policies
- [ ] Document how to tighten for production
- [ ] Test with both permissive and strict policies
- [ ] Test policy evaluation logic

---

**Last Updated:** January 20, 2026
