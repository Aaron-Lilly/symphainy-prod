# Intent Services Pilot Task

**Task ID:** `intent_services_pilot`  
**Status:** 🟢 **READY FOR AGENT**  
**Priority:** 🔴 **PRIORITY 1** - Validation Pilot  
**Created:** January 27, 2026

---

## Objective

Implement intent services for **2 intent contracts** to validate our contract-driven development approach before scaling to all 89 intents.

---

## Target Intent Contracts

### 1. `ingest_file` Intent Service
- **Contract:** `docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md`
- **Journey:** File Upload & Materialization
- **Realm:** Content Realm
- **Base Class:** `BaseIntentService`

### 2. `save_materialization` Intent Service
- **Contract:** `docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md`
- **Journey:** File Upload & Materialization
- **Realm:** Content Realm
- **Base Class:** `BaseIntentService`

---

## Implementation Requirements

### 1. Create Intent Service Classes

**Location:** `symphainy_platform/realms/content/intent_services/`

**Files to Create:**
- `ingest_file_service.py` - Implements `ingest_file` intent
- `save_materialization_service.py` - Implements `save_materialization` intent

**Pattern:**
```python
from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from typing import Dict, Any, Optional

class IngestFileService(BaseIntentService):
    def __init__(self, public_works, state_surface):
        super().__init__(
            service_id="ingest_file_service",
            intent_type="ingest_file",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Implement according to intent contract
        # Follow contract specifications exactly
        pass
```

### 2. Key Requirements

**Must Follow:**
- ✅ Intent contract specifications exactly
- ✅ BaseIntentService pattern
- ✅ Architectural requirements (`.cursor/ARCHITECTURAL_REQUIREMENTS.md`)
- ✅ Telemetry reporting via Nurse SDK
- ✅ Artifact registration via State Surface
- ✅ Public Works abstractions only (no direct infrastructure access)
- ✅ Contract compliance validation

**Must NOT:**
- ❌ Bypass Runtime Execution Engine
- ❌ Access infrastructure directly (use Public Works only)
- ❌ Skip telemetry reporting
- ❌ Skip artifact registration
- ❌ Violate architectural patterns

### 3. Implementation Steps

#### For `ingest_file` Service:
1. Read intent contract: `docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md`
2. Validate parameters (per contract Section 2)
3. Get `IngestionAbstraction` from Public Works
4. Execute ingestion (upload/edi/api)
5. Register artifact in State Surface (lifecycle_state: PENDING)
6. Add GCS materialization
7. Index artifact in Supabase
8. Report telemetry via Nurse SDK
9. Return structured artifact response (per contract Section 3)
10. Validate contract compliance

#### For `save_materialization` Service:
1. Read intent contract: `docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md`
2. Validate parameters (per contract Section 2)
3. Get file metadata from State Surface
4. Register materialization in materialization index
5. **Create pending parsing journey** (intent_executions table, status: PENDING)
6. **Store ingest type and file type in pending intent context**
7. Transition file artifact lifecycle (PENDING → READY)
8. Report telemetry via Nurse SDK
9. Return structured artifact response (per contract Section 3)
10. Validate contract compliance

---

## Reference Materials

### Contracts
- `docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md`
- `docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md`
- `docs/journey_contracts/content_realm_solution/journey_content_file_upload_materialization.md`

### Base Classes
- `symphainy_platform/bases/intent_service_base.py` - BaseIntentService
- `symphainy_platform/bases/README.md` - Base class documentation

### Architectural Requirements
- `.cursor/ARCHITECTURAL_REQUIREMENTS.md` - All architectural patterns and constraints
- `docs/ARCHITECTURE_NORTH_STAR.md` - System architecture overview

### Existing Implementations (Reference Only)
- `symphainy_platform/realms/content/orchestrators/handlers/ingestion_handlers.py` - Reference implementation
- `symphainy_platform/realms/content/orchestrators/content_orchestrator.py` - Reference implementation

**Note:** Use existing implementations as reference for business logic, but follow new architecture patterns (BaseIntentService, contract compliance, etc.)

---

## Validation Criteria

### Code Quality
- [ ] Extends BaseIntentService correctly
- [ ] Implements `execute()` method per contract
- [ ] Validates parameters per contract
- [ ] Reports telemetry via Nurse SDK
- [ ] Registers artifacts via State Surface
- [ ] Uses Public Works abstractions only
- [ ] Follows contract specifications exactly

### Contract Compliance
- [ ] Parameters match contract Section 2
- [ ] Returns match contract Section 3
- [ ] Artifact registration matches contract Section 4
- [ ] Idempotency matches contract Section 5
- [ ] Error handling matches contract Section 8

### Architectural Compliance
- [ ] No direct infrastructure access
- [ ] All telemetry reported
- [ ] All artifacts registered
- [ ] Contract validation implemented
- [ ] Follows base class patterns

---

## Success Criteria

**This pilot is successful if:**
1. ✅ Both intent services compile without errors
2. ✅ Both services follow BaseIntentService pattern
3. ✅ Both services implement contract specifications
4. ✅ Both services report telemetry
5. ✅ Both services register artifacts correctly
6. ✅ Code follows architectural requirements
7. ✅ Contract compliance validation works

**This pilot will inform:**
- Whether contract structure is sufficient
- Whether base classes provide needed functionality
- Whether architectural requirements are clear
- What adjustments are needed before scaling

---

## Deliverables

1. **Intent Service Files:**
   - `symphainy_platform/realms/content/intent_services/ingest_file_service.py`
   - `symphainy_platform/realms/content/intent_services/save_materialization_service.py`

2. **Package Initialization:**
   - `symphainy_platform/realms/content/intent_services/__init__.py`

3. **Documentation:**
   - Brief README in intent_services directory explaining the pattern

---

## Questions to Answer

After implementation, we need to know:
1. Were the contracts clear enough?
2. Did the base classes provide what was needed?
3. Were architectural requirements clear?
4. What was confusing or missing?
5. What would make this easier to scale?

---

**Last Updated:** January 27, 2026  
**Status:** 🟢 **READY FOR AGENT**
