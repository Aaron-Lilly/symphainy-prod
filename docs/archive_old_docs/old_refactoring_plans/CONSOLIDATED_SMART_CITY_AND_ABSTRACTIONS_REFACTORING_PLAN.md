# Consolidated Smart City & Abstractions Refactoring Plan

**Date:** January 2026  
**Status:** 📋 **CONSOLIDATED REFACTORING PLAN**  
**Purpose:** Refactor Smart City to proper location/pattern AND refactor abstractions together

---

## Executive Summary

**The Problem:**
- ❌ Smart City services exist at `symphainy_platform/smart_city/services/` (WRONG LOCATION)
- ✅ Should be at `civic_systems/smart_city/roles/` (Civic System)
- ❌ Current services may not follow new primitive pattern (policy-aware primitives)
- ❌ Services may contain business logic (should be in domain services)
- ❌ Abstractions have business logic that needs to move to appropriate location
- ⚠️ **Risk:** If we dump abstraction business logic into improper Smart City structure, we'll have to refactor again

**The Solution:**
- ✅ **One consolidated plan** to refactor BOTH:
  1. Smart City (move to `civic_systems/smart_city/`, follow new primitive pattern)
  2. Abstractions (remove business logic, make pure)
- ✅ Do this together to avoid technical debt
- ✅ Then proceed with Phase 2/3 plan

**Critical Understanding:**
- Smart City is a **Civic System** (one of 4: Smart City, Experience, Agentic, Platform SDK)
- Smart City roles are **policy-aware primitives** (NOT business logic)
- Policy logic → Smart City roles
- Business logic → Domain services (Content, Insights, Journey, Solution)

---

## Current State Analysis

### Smart City Current Location

**Location:** `symphainy_platform/smart_city/` ✅ **ALREADY IN RIGHT LOCATION**

**What Exists:**
- Smart City services exist at `symphainy_platform/smart_city/services/`
- Foundation service exists
- Protocols exist
- **May not follow new primitive pattern** (need to assess)
- **May have business logic that should be moved from abstractions**

### Smart City Target Structure

**Location:** `symphainy_platform/smart_city/` (same location, refactor in place)

**Target Structure:**
```
symphainy_platform/smart_city/
├── services/
│   ├── security_guard/
│   │   ├── __init__.py
│   │   ├── security_guard_service.py
│   │   └── README.md
│   ├── city_manager/
│   ├── data_steward/
│   ├── librarian/
│   ├── traffic_cop/
│   ├── post_office/
│   ├── conductor/
│   └── nurse/
├── protocols/
│   └── smart_city_service_protocol.py
└── __init__.py
```

---

## Current State (What Exists)

### Smart City Services

**Location:** `symphainy_platform/smart_city/services/` ✅ **ALREADY IN RIGHT LOCATION**

**Services That Exist:**
- ✅ Security Guard (`security_guard/`)
- ✅ City Manager (`city_manager/`)
- ✅ Data Steward (`data_steward/`)
- ✅ Librarian (`librarian/`)
- ✅ Traffic Cop (`traffic_cop/`)
- ✅ Post Office (`post_office/`)
- ✅ Conductor (`conductor/`)
- ✅ Nurse (`nurse/`)

**Current Status:**
- ✅ Some implement `SmartCityServiceProtocol` (Librarian, Data Steward, City Manager, etc.)
- ⚠️ Security Guard does NOT implement protocol (needs refactoring)
- ⚠️ May not be using abstractions correctly (need to assess)
- ⚠️ May need business logic from abstractions moved to them

**Foundation Service:**
- ✅ `SmartCityFoundationService` exists and initializes all services

---

## Consolidated Refactoring Strategy

### Phase 1: Inventory & Assessment (Week 1, Days 1-2)

**Goal:** Understand what exists and what needs to change

**Tasks:**

1. **Inventory Smart City Services**
   - [x] Services exist at `symphainy_platform/smart_city/services/`
   - [ ] Document which services implement `SmartCityServiceProtocol`
   - [ ] Identify which services need protocol compliance
   - [ ] Identify which services use abstractions vs. adapters directly
   - [ ] Identify what business logic exists in services

2. **Inventory Abstractions**
   - [ ] List all abstractions with business logic
   - [ ] Map business logic to Smart City roles
   - [ ] Document what needs to move where

3. **Create Migration Map**
   - [ ] Map: Abstraction Business Logic → Smart City Role
   - [ ] Identify which services need refactoring
   - [ ] Identify dependencies

---

### Phase 2: Smart City Refactoring (Week 1, Days 3-5)

**Goal:** Ensure Smart City services follow new primitive pattern and use abstractions

**Tasks:**

1. **Assess Current Services**
   - [ ] Check which services implement `SmartCityServiceProtocol`
   - [ ] Check which services use abstractions vs. adapters
   - [ ] Identify what needs refactoring

2. **Refactor Each Smart City Service** (if needed)
   - [ ] Ensure implements `SmartCityServiceProtocol` (if not already)
   - [ ] Update to use abstractions (not adapters directly)
   - [ ] Add MCP tools (if applicable)
   - [ ] Ensure proper initialization

3. **Update Dependencies**
   - [ ] Update services to use abstractions from Public Works
   - [ ] Update foundation service (if needed)
   - [ ] Update Runtime integration (if needed)

---

### Phase 3: Abstraction Refactoring (Week 2, Days 1-5)

**Goal:** Remove business logic from abstractions, move to Smart City

**Tasks:**

1. **For Each Abstraction:**
   - [ ] Identify business logic
   - [ ] Move to appropriate Smart City role
   - [ ] Update abstraction to return raw data
   - [ ] Test abstraction is pure

2. **Update Smart City Roles:**
   - [ ] Add harvested business logic
   - [ ] Use abstractions (not adapters)
   - [ ] Test business logic works

3. **Update Integration:**
   - [ ] Update callers to use Smart City roles
   - [ ] Remove temporary bridges
   - [ ] Test end-to-end

---

### Phase 4: Validation & Testing (Week 2, Days 6-7)

**Goal:** Ensure everything works together

**Tasks:**

1. **Run Validation Tests**
   - [ ] Test abstractions are pure
   - [ ] Test Smart City roles have business logic
   - [ ] Test integration works

2. **Update Documentation**
   - [ ] Update architecture docs
   - [ ] Update migration docs
   - [ ] Document new structure

---

## Detailed Refactoring Plan

### Smart City Services to Refactor

**Current Location:** `symphainy_platform/smart_city/services/` ✅ (already in right place)

**Services Status:**

1. **Security Guard** (Identity, authN/Z, zero trust)
   - Current: `symphainy_platform/smart_city/services/security_guard/` ✅
   - Status: ⚠️ Does NOT implement `SmartCityServiceProtocol` (needs refactoring)
   - Business Logic From: Auth Abstraction, Tenant Abstraction
   - Needs: Protocol compliance, use abstractions

2. **City Manager** (Global policy, tenancy, escalation)
   - Current: `symphainy_platform/smart_city/services/city_manager/` ✅
   - Status: ✅ Implements `SmartCityServiceProtocol`
   - Business Logic From: Tenant Abstraction, Auth Abstraction
   - Needs: Ensure uses abstractions, add business logic from abstractions

3. **Data Steward** (Data boundaries, contracts, provenance)
   - Current: `symphainy_platform/smart_city/services/data_steward/` ✅
   - Status: ✅ Implements `SmartCityServiceProtocol`
   - Business Logic From: Content Metadata Abstraction, File Storage Abstraction
   - Needs: Ensure uses abstractions, add business logic from abstractions

4. **Librarian** (Semantic schemas & meaning)
   - Current: `symphainy_platform/smart_city/services/librarian/` ✅
   - Status: ✅ Implements `SmartCityServiceProtocol`
   - Business Logic From: Semantic Search Abstraction, Semantic Data Abstraction
   - Needs: Ensure uses abstractions, add business logic from abstractions

5. **Traffic Cop** (Sessions, execution IDs, correlation)
   - Current: `symphainy_platform/smart_city/services/traffic_cop/` ✅
   - Status: ✅ Implements `SmartCityServiceProtocol`
   - Business Logic From: Session Abstraction (if any)
   - Needs: Ensure uses abstractions

6. **Post Office** (Event routing & ordering)
   - Current: `symphainy_platform/smart_city/services/post_office/` ✅
   - Status: ✅ Implements `SmartCityServiceProtocol`
   - Business Logic From: Event Management Abstraction, Messaging Abstraction (if any)
   - Needs: Ensure uses abstractions

7. **Conductor** (Workflow & saga primitives)
   - Current: `symphainy_platform/smart_city/services/conductor/` ✅
   - Status: ✅ Implements `SmartCityServiceProtocol`
   - Business Logic From: Workflow Orchestration Abstraction
   - Needs: Ensure uses abstractions, add business logic from abstractions

8. **Nurse** (Telemetry, retries, self-healing)
   - Current: `symphainy_platform/smart_city/services/nurse/` ✅
   - Status: ✅ Implements `SmartCityServiceProtocol`
   - Business Logic From: Telemetry Abstraction, Health Abstraction (if any)
   - Needs: Ensure uses abstractions

---

### Abstractions to Refactor

**Critical (Week 2, Days 1-3):**

1. **Auth Abstraction**
   - Remove: Tenant creation, role extraction, SecurityContext creation
   - Move To: Security Guard, City Manager
   - Return: Raw user data

2. **Tenant Abstraction**
   - Remove: Access validation, configuration management
   - Move To: Security Guard, City Manager
   - Return: Raw tenant data

3. **Content Metadata Abstraction**
   - Remove: ID generation, validation, status management
   - Move To: Data Steward
   - Return: Raw metadata data

4. **Semantic Data Abstraction**
   - Remove: Validation logic, business rules
   - Move To: Librarian
   - Return: Raw semantic data

5. **Workflow Orchestration Abstraction**
   - Remove: Workflow definition/execution logic
   - Move To: Conductor
   - Return: Raw workflow data

**Important (Week 2, Days 4-5):**

6. **Semantic Search Abstraction**
   - Remove: Document ID generation
   - Move To: Librarian
   - Return: Raw search results

7. **File Storage Abstraction**
   - Remove: Content type inference, metadata structuring
   - Move To: Data Steward
   - Return: Raw file data

---

## Refactoring Workflow

### For Each Smart City Role:

**Step 1: Assess Current State**
```bash
# Check what exists (already in right location)
ls -la symphainy_platform/smart_city/services/<role>/
# Review current implementation
cat symphainy_platform/smart_city/services/<role>/*.py
# Check if implements protocol
grep "SmartCityServiceProtocol" symphainy_platform/smart_city/services/<role>/*.py
# Check if uses abstractions
grep "abstraction" symphainy_platform/smart_city/services/<role>/*.py
```

**Step 2: Refactor Service** (if needed)
```python
# Update to follow new pattern:
# - Ensure implements SmartCityServiceProtocol (if not already)
# - Use abstractions (not adapters directly)
# - Add MCP tools (if applicable)
# - Add telemetry
```

**Step 3: Move Business Logic from Abstractions**
```python
# Identify business logic in abstractions
# Move to Smart City role
# Update role to use abstractions (not adapters)
```

**Step 4: Update Abstraction**
```python
# Remove business logic
# Return raw data
# Test is pure
```

**Step 5: Test**
```bash
# Test Smart City role
pytest tests/smart_city/test_<role>_service.py

# Test abstraction
pytest tests/foundations/public_works/test_<abstraction>_abstraction.py
```

---

## Migration Map

### Smart City Services Status

| Service | Location | Protocol Compliance | Uses Abstractions | Status |
|---------|----------|---------------------|-------------------|--------|
| Security Guard | `symphainy_platform/smart_city/services/security_guard/` | ❌ No | ⚠️ Need to check | ⏳ Needs refactoring |
| City Manager | `symphainy_platform/smart_city/services/city_manager/` | ✅ Yes | ⚠️ Need to check | ⏳ May need updates |
| Data Steward | `symphainy_platform/smart_city/services/data_steward/` | ✅ Yes | ⚠️ Need to check | ⏳ May need updates |
| Librarian | `symphainy_platform/smart_city/services/librarian/` | ✅ Yes | ⚠️ Need to check | ⏳ May need updates |
| Traffic Cop | `symphainy_platform/smart_city/services/traffic_cop/` | ✅ Yes | ⚠️ Need to check | ⏳ May need updates |
| Post Office | `symphainy_platform/smart_city/services/post_office/` | ✅ Yes | ⚠️ Need to check | ⏳ May need updates |
| Conductor | `symphainy_platform/smart_city/services/conductor/` | ✅ Yes | ⚠️ Need to check | ⏳ May need updates |
| Nurse | `symphainy_platform/smart_city/services/nurse/` | ✅ Yes | ⚠️ Need to check | ⏳ May need updates |

### Business Logic Migration

| Abstraction | Business Logic | Smart City Role | Status |
|------------|----------------|----------------|--------|
| Auth Abstraction | Tenant creation | City Manager | ⏳ TODO |
| Auth Abstraction | Role extraction | Security Guard | ⏳ TODO |
| Auth Abstraction | SecurityContext creation | Security Guard | ⏳ TODO |
| Tenant Abstraction | Access validation | Security Guard | ⏳ TODO |
| Tenant Abstraction | Configuration management | City Manager | ⏳ TODO |
| Content Metadata Abstraction | ID generation | Data Steward | ⏳ TODO |
| Content Metadata Abstraction | Validation rules | Data Steward | ⏳ TODO |
| Semantic Search Abstraction | Document ID generation | Librarian | ⏳ TODO |
| Semantic Data Abstraction | Validation logic | Librarian | ⏳ TODO |
| Workflow Orchestration Abstraction | Workflow definition | Conductor | ⏳ TODO |
| Workflow Orchestration Abstraction | Workflow execution | Conductor | ⏳ TODO |

---

## Implementation Order

### Week 1: Smart City Refactoring + Critical Abstractions

**Day 1-2: Inventory & Assessment**
- [ ] Assess Smart City services (protocol compliance, abstraction usage)
- [ ] Inventory abstractions with business logic
- [ ] Create detailed migration map

**Day 3: Security Guard + Auth Abstraction**
- [ ] Refactor Security Guard to implement `SmartCityServiceProtocol`
- [ ] Ensure Security Guard uses abstractions (not adapters)
- [ ] Move business logic from Auth Abstraction to Security Guard
- [ ] Refactor Auth Abstraction to be pure

**Day 4: City Manager + Tenant Abstraction**
- [ ] Ensure City Manager uses abstractions (not adapters)
- [ ] Move business logic from Tenant Abstraction to City Manager/Security Guard
- [ ] Refactor Tenant Abstraction to be pure

**Day 5: Data Steward + Content Metadata Abstraction**
- [ ] Ensure Data Steward uses abstractions (not adapters)
- [ ] Move business logic from Content Metadata Abstraction to Data Steward
- [ ] Refactor Content Metadata Abstraction to be pure

### Week 2: Remaining Refactoring

**Day 1: Librarian + Semantic Abstractions**
- Refactor Librarian to new location/pattern
- Move business logic from Semantic Search/Data Abstractions
- Refactor Semantic Abstractions to be pure

**Day 2: Conductor + Workflow Abstraction**
- Refactor Conductor to new location/pattern
- Move business logic from Workflow Orchestration Abstraction
- Refactor Workflow Abstraction to be pure

**Day 3: Remaining Smart City Roles**
- Refactor Traffic Cop, Post Office, Nurse
- Move any remaining business logic

**Day 4-5: Validation & Testing**
- Run all validation tests
- Fix any issues
- Update documentation

---

## Success Criteria

### ✅ Smart City Refactoring

- [x] All services exist at `symphainy_platform/smart_city/services/` (already in right location)
- [ ] All services implement `SmartCityServiceProtocol` (Security Guard needs this)
- [ ] All services use abstractions (not adapters directly)
- [ ] All services have business logic from abstractions
- [ ] All imports updated (if needed)

### ✅ Abstraction Refactoring

- [ ] All abstractions return raw data (not business objects)
- [ ] All business logic moved to Smart City roles
- [ ] All abstractions are swappable
- [ ] All abstractions comply with protocols

### ✅ Integration

- [ ] Smart City roles can use abstractions
- [ ] Runtime can use Smart City roles
- [ ] End-to-end flows work
- [ ] All tests pass

---

## Benefits of Consolidated Approach

**1. No Technical Debt**
- ✅ Smart City is in right place from day 1
- ✅ Business logic goes to proper Smart City roles
- ✅ No need to refactor again later

**2. Clean Separation**
- ✅ Abstractions are pure infrastructure
- ✅ Smart City roles have business logic
- ✅ Clear boundaries

**3. Faster Phase 2/3**
- ✅ Smart City is ready for Phase 2/3
- ✅ Abstractions are ready for Runtime
- ✅ No blockers

**4. Better Testing**
- ✅ Can test Smart City roles properly
- ✅ Can test abstractions properly
- ✅ Can test integration properly

---

## Next Steps

1. **Inventory Current State** (Day 1)
   - List all Smart City services
   - List all abstractions with business logic
   - Create detailed migration map

2. **Start Refactoring** (Day 2+)
   - Begin with Security Guard + Auth Abstraction
   - Follow workflow for each role
   - Test as we go

3. **Validate** (Week 2, Days 4-5)
   - Run all validation tests
   - Ensure everything works together

---

## Conclusion

**This consolidated approach:**
- ✅ Solves the chicken-and-egg problem
- ✅ Avoids technical debt
- ✅ Sets us up for Phase 2/3 success
- ✅ Ensures clean architecture from day 1

**Timeline:** 2 weeks for complete refactoring

**Then:** Proceed with Phase 2/3 plan with clean foundation
