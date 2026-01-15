# Code Preservation Checklist

**Date:** January 2026  
**Purpose:** List of code to preserve during any architectural alignment

---

## ✅ MUST PRESERVE (Working Code)

### 1. EDI & API Ingestion Adapters

**Location:** `symphainy_platform/foundations/public_works/adapters/`

**Files:**
- ✅ `edi_adapter.py` - Full EDI ingestion with AS2 support
- ✅ `api_adapter.py` - API-based ingestion (REST, GraphQL, Webhook)
- ✅ `as2_decryption.py` - AS2 decryption and signature verification
- ✅ `upload_adapter.py` - Direct file upload adapter

**Why Preserve:**
- ✅ Fully implemented and tested
- ✅ Proper abstraction boundaries
- ✅ AS2 decryption working
- ✅ Clean integration with FileStorageAbstraction

**Action:** Keep as-is, may need import path updates if Public Works structure changes

---

### 2. Journey Realm Services

**Location:** `symphainy_platform/realms/journey/services/`

**Files:**
- ✅ `sop_builder_service/sop_builder_service.py` - SOP creation and wizard
- ✅ `workflow_conversion_service/workflow_conversion_service.py` - SOP ↔ Workflow conversion
- ✅ `coexistence_analysis_service/coexistence_analysis_service.py` - Coexistence analysis and blueprints

**Why Preserve:**
- ✅ Deterministic, stateless services (aligns with architecture)
- ✅ Proper State Surface integration
- ✅ All unit tests passing
- ✅ Clean separation of concerns

**Action:** Keep as-is, may need to wrap with Runtime contracts later

---

### 3. Journey Realm Orchestrator

**Location:** `symphainy_platform/realms/journey/orchestrators/`

**Files:**
- ✅ `journey_orchestrator.py` - All 8 saga steps implemented

**Why Preserve:**
- ✅ Proper saga composition
- ✅ All integration tests passing
- ✅ Clean service composition

**Action:** Keep as-is, may need to align with Runtime intent handling

---

### 4. Runtime Core Components

**Location:** `symphainy_platform/runtime/`

**Files:**
- ✅ `state_surface.py` - State management (execution state, facts, references)
- ✅ `write_ahead_log.py` - Execution logging
- ✅ `saga_coordinator.py` - Saga orchestration
- ✅ `runtime_service.py` - Runtime service

**Why Preserve:**
- ✅ Core execution authority (aligns with architecture guide)
- ✅ Proper state management patterns
- ✅ Foundation for Runtime Participation Contract

**Action:** Keep as-is, may need to extend for intent handling

---

### 5. Public Works Foundation Structure

**Location:** `symphainy_platform/foundations/public_works/`

**Structure:**
- ✅ `adapters/` - Layer 0 infrastructure adapters
- ✅ `abstractions/` - Layer 1 infrastructure abstractions
- ✅ `protocols/` - Interface definitions
- ✅ `foundation_service.py` - Layer 4 orchestration

**Why Preserve:**
- ✅ 5-layer architecture pattern (correct)
- ✅ Clean adapter/abstraction separation
- ✅ Proper dependency injection

**Action:** Keep structure, may need to add missing abstractions

---

### 6. Test Suites

**Location:** `tests/realms/journey/`

**Files:**
- ✅ `test_sop_builder_service.py` - SOP service tests
- ✅ `test_workflow_conversion_service.py` - Workflow service tests
- ✅ `test_coexistence_analysis_service.py` - Coexistence service tests
- ✅ `test_journey_orchestrator.py` - Orchestrator integration tests
- ✅ `conftest.py` - Test fixtures

**Why Preserve:**
- ✅ All tests passing
- ✅ Validates working functionality
- ✅ Prevents regressions

**Action:** Keep as-is, update if service interfaces change

---

## ⚠️ REFACTOR (Don't Delete)

### 1. Agentic Foundation

**Current Location:** `symphainy_platform/agentic/`

**Should Be:** `symphainy_platform/foundations/agentic/`

**Files:**
- ⚠️ `agent_base.py`
- ⚠️ `grounded_reasoning_agent_base.py`
- ⚠️ `foundation_service.py`

**Action:** Move folder, update imports, test

---

### 2. Experience Plane

**Current Location:** `symphainy_platform/experience/`

**Status:** Needs alignment with Civic System pattern

**Action:** Review, align with architecture guide, don't delete

---

### 3. Smart City

**Current Location:** `symphainy_platform/smart_city/`

**Status:** Needs alignment with Civic System pattern

**Action:** Review, align with architecture guide, don't delete

---

## ❌ CAN DELETE (If They Exist)

### 1. Duplicate/Unused Adapters

**Check for:**
- Duplicate file storage adapters
- Unused parsing adapters
- Legacy adapters not in use

**Action:** Audit, delete if unused

---

### 2. Legacy Realm Implementations

**Check for:**
- Old realm implementations replaced by new ones
- Broken realm code
- Unused realm services

**Action:** Audit, delete if replaced

---

### 3. Broken Test Files

**Check for:**
- Tests that don't run
- Tests for deleted code
- Tests that are obsolete

**Action:** Fix or delete

---

## 📋 Migration Checklist

When aligning with architecture guide:

- [ ] Move `agentic/` to `foundations/agentic/`
- [ ] Update all imports
- [ ] Run tests (should all pass)
- [ ] Add missing Public Works abstractions (incrementally)
- [ ] Wrap services with Runtime contracts (incrementally)
- [ ] Align Experience Plane with Civic System pattern
- [ ] Align Smart City with Civic System pattern
- [ ] Test after each change

---

## 🎯 Success Criteria

After alignment:

- ✅ All preserved code still works
- ✅ All tests still pass
- ✅ No functionality lost
- ✅ Architecture aligns with guide
- ✅ Frontend deployment works

---

## 📝 Notes

- **Don't delete working code** - Even if it doesn't perfectly align with architecture guide
- **Refactor incrementally** - Test after each change
- **Preserve tests** - They validate functionality
- **Document changes** - Track what moved/refactored
