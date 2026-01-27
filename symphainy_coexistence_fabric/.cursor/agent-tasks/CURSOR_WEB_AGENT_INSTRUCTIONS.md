# Cursor Web Agent Instructions: Intent Services Pilot

**Task ID:** `intent_services_pilot`  
**Status:** 🟢 **READY FOR CURSOR WEB AGENT**  
**Created:** January 27, 2026

---

## ⚠️ CRITICAL: Repository & Working Directory

### Repository
- **Repository:** `symphainy_source_code`
- **Working Directory:** `symphainy_coexistence_fabric/` (within the repo)
- **All paths are relative to:** `symphainy_coexistence_fabric/`
- **Branch:** Create feature branch `feature/intent-services-pilot`

### Task Location
- **Task File:** `symphainy_coexistence_fabric/.cursor/agent-tasks/INTENT_SERVICES_PILOT.md`
- **Instructions:** `symphainy_coexistence_fabric/.cursor/agent-tasks/AGENT_INSTRUCTIONS.md`
- **This File:** `symphainy_coexistence_fabric/.cursor/agent-tasks/CURSOR_WEB_AGENT_INSTRUCTIONS.md`

---

## Agent Task: Implement Intent Services

### Objective
Implement 2 intent services following contracts and architectural requirements to validate our contract-driven development approach.

### Target Files to Create

1. **`symphainy_platform/realms/content/intent_services/ingest_file_service.py`**
   - Extends `BaseIntentService`
   - Implements `ingest_file` intent per contract
   - Contract: `docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md`

2. **`symphainy_platform/realms/content/intent_services/save_materialization_service.py`**
   - Extends `BaseIntentService`
   - Implements `save_materialization` intent per contract
   - Contract: `docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md`

3. **`symphainy_platform/realms/content/intent_services/__init__.py`**
   - Package initialization file

---

## Step-by-Step Instructions for Agent

### Step 1: Read Reference Materials
Read these files in order:
1. `.cursor/agent-tasks/INTENT_SERVICES_PILOT.md` - Full task specification
2. `.cursor/agent-tasks/AGENT_INSTRUCTIONS.md` - Implementation guidance
3. `docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md` - Contract for ingest_file
4. `docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md` - Contract for save_materialization
5. `symphainy_platform/bases/intent_service_base.py` - Base class to extend
6. `.cursor/ARCHITECTURAL_REQUIREMENTS.md` - Patterns and constraints

### Step 2: Review Reference Implementation (For Business Logic Only)
Read these files to understand business logic:
- `symphainy_platform/realms/content/orchestrators/handlers/ingestion_handlers.py` - Reference for ingest_file logic
- `symphainy_platform/realms/content/orchestrators/content_orchestrator.py` - Reference for save_materialization logic

**Important:** Use these for business logic understanding, but follow NEW architecture patterns (BaseIntentService, not BaseContentHandler).

### Step 3: Create Directory Structure

**Make sure you're in:** `symphainy_coexistence_fabric/` directory

```bash
# From symphainy_coexistence_fabric/ directory:
mkdir -p symphainy_platform/realms/content/intent_services
touch symphainy_platform/realms/content/intent_services/__init__.py
```

**Verify structure:**
```bash
ls -la symphainy_platform/realms/content/intent_services/
# Should show: __init__.py
```

### Step 4: Implement ingest_file_service.py

**Reference Implementation:** `../symphainy_platform/realms/content/orchestrators/handlers/ingestion_handlers.py` (function `handle_ingest_file`)

**Key Requirements:**
- Extend `BaseIntentService` (NOT BaseContentHandler!)
- Implement `execute()` method
- Validate parameters per contract Section 2
- Get `IngestionAbstraction` from Public Works (`self.public_works.ingestion_abstraction`)
- Execute ingestion (upload/edi/api) - see reference implementation for logic
- Register artifact in State Surface (lifecycle_state: PENDING) using `self.register_artifact()`
- Add GCS materialization to artifact record
- Index artifact in Supabase (via Public Works abstraction)
- Report telemetry via Nurse SDK using `self.record_telemetry()`
- Return structured artifact response per contract Section 3

**What to extract from reference implementation:**
- How file_content (hex) is decoded
- How file_type and mime_type are determined
- How GCS path is constructed
- How artifact_id is generated
- How boundary_contract_id is created

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
        # Validate intent type (base class does this, but be explicit)
        if context.intent.intent_type != self.intent_type:
            raise ValueError(f"Intent type mismatch")
        
        # Record telemetry (start)
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        # Validate parameters per contract
        # Get IngestionAbstraction from Public Works
        # Execute ingestion
        # Register artifact
        # Report telemetry (complete)
        # Return structured artifact
        pass
```

### Step 5: Implement save_materialization_service.py

**Reference Implementation:** `../symphainy_platform/realms/content/orchestrators/content_orchestrator.py` (function `_handle_save_materialization` around line 1418)

**Key Requirements:**
- Extend `BaseIntentService` (NOT BaseContentHandler!)
- Implement `execute()` method
- Validate parameters per contract Section 2
- Get file metadata from State Surface using `self.state_surface`
- Register materialization in materialization index - see reference for pattern
- **Create pending parsing journey** (intent_executions table, status: PENDING)
  - Use intent registry to create pending intent
  - Intent type: `parse_content`
  - Status: `PENDING`
- **Store ingest type and file type in pending intent context**
  - See reference implementation for how context is structured
- Transition file artifact lifecycle (PENDING → READY) using State Surface
- Report telemetry via Nurse SDK using `self.record_telemetry()`
- Return structured artifact response per contract Section 3

**What to extract from reference implementation:**
- How materialization is registered in the index
- How `create_pending_parse_intent` works (or equivalent pattern)
- How intent context stores ingest_profile/file_type
- How lifecycle state is updated

### Step 6: Validate Implementation

**Checklist:**
- [ ] Both services extend BaseIntentService
- [ ] Both implement `execute()` method
- [ ] Parameters validated per contracts
- [ ] Telemetry reported via Nurse SDK
- [ ] Artifacts registered via State Surface
- [ ] Public Works abstractions used (no direct infrastructure access)
- [ ] Contract specifications followed exactly
- [ ] Code compiles without errors

---

## Critical Rules

### ✅ MUST DO
- Extend BaseIntentService
- Implement contract specifications exactly
- Report telemetry via Nurse SDK (`self.record_telemetry()`)
- Register artifacts via State Surface (`self.register_artifact()`)
- Use Public Works abstractions only
- Validate parameters per contract
- Return structured artifacts per contract

### ❌ MUST NOT DO
- Access infrastructure directly (use Public Works only)
- Skip telemetry reporting
- Skip artifact registration
- Bypass Runtime Execution Engine
- Violate architectural patterns
- Use BaseContentHandler (use BaseIntentService instead)

---

## Success Criteria

The implementation is successful if:
- ✅ Files are created in correct location
- ✅ Code extends BaseIntentService
- ✅ Implements contract specifications
- ✅ Reports telemetry
- ✅ Registers artifacts
- ✅ Follows architectural requirements
- ✅ Code compiles without errors

---

## Questions to Answer After Implementation

1. Were the contracts clear enough?
2. Did the base classes provide what was needed?
3. Were architectural requirements clear?
4. What was confusing or missing?
5. What would make this easier to scale?

---

## Deliverables

1. **Intent Service Files:**
   - `symphainy_platform/realms/content/intent_services/ingest_file_service.py`
   - `symphainy_platform/realms/content/intent_services/save_materialization_service.py`

2. **Package Initialization:**
   - `symphainy_platform/realms/content/intent_services/__init__.py`

3. **Documentation:**
   - Brief comments in code explaining key decisions
   - Any notes about ambiguities or questions

---

**Last Updated:** January 27, 2026  
**Status:** 🟢 **READY FOR CURSOR WEB AGENT**
