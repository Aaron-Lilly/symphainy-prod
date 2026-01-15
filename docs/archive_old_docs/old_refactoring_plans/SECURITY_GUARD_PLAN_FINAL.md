# Security Guard Refactoring Plan - FINAL (Locked In)

**Date:** January 2026  
**Status:** ✅ **LOCKED IN - READY FOR IMPLEMENTATION**  
**Decisions:** Policy Registry Schema (flexible JSONB), Policy Library (scaffold now)

---

## Locked-In Decisions

### ✅ Policy Registry Schema
- **Decision:** Defer full schema definition, use flexible JSONB structure
- **Rationale:** Phase 1 is about moving logic, not perfecting schemas
- **Implementation:** JSONB `policy_data` column, evolvable structure

### ✅ Policy Library
- **Decision:** Scaffold now with minimal implementation
- **Rationale:** SDKs and Primitives need to import from it, prevents circular dependencies
- **Phase 1:** Scaffold structure, define schemas, provide stubs
- **Phase 2:** Full validation/evaluation implementation

---

## Implementation Phases

### Phase 1: Scaffold Core Libraries & Registries

1. **Create Structure:**
   - `civic_systems/smart_city/primitives/`
   - `civic_systems/smart_city/sdk/`
   - `civic_systems/smart_city/registries/`
   - `libraries/policy/`

2. **Policy Registry (Flexible JSONB):**
   - Create Supabase table with JSONB structure
   - Implement `PolicyRegistry` class
   - Migrate hardcoded policies from `/symphainy_source/`
   - Support tenant-specific, action-specific, resource-specific policies

3. **Policy Library (Scaffold):**
   - Create `schemas.py` (Pydantic models)
   - Create `validators.py` (validation stubs)
   - Create `evaluators.py` (evaluation stubs)

### Phase 2-7: (As defined in main plan)

---

## Ready for Curator Question

All decisions are locked in. Ready to proceed with Curator Registry architectural shift analysis.
