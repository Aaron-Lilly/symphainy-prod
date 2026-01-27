# Reference Implementations Guide

**Purpose:** This document points agents to existing (old) implementations for business logic reference.

⚠️ **CRITICAL WARNING:** These are OLD implementations using OLD architecture. Use them ONLY to understand business logic. DO NOT copy the architecture patterns!

---

## Location of Reference Code

**Base Path:** `../symphainy_platform/` (parent directory from `symphainy_coexistence_fabric/`)

**Full Path:** `symphainy_source_code/symphainy_platform/`

---

## Reference Implementation 1: ingest_file

### File Location
```
../symphainy_platform/realms/content/orchestrators/handlers/ingestion_handlers.py
```

### Function to Study
```python
async def handle_ingest_file(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
```

**Starts around:** Line 29

### What This Shows You

1. **Parameter Extraction:**
   - How `ingestion_type` is determined (upload/edi/api)
   - How `file_content` (hex-encoded) is handled
   - How `ui_name`, `file_type`, `mime_type` are extracted
   - How `boundary_contract_id` is retrieved from context

2. **Ingestion Logic:**
   - How `IngestionAbstraction` is obtained from Public Works
   - How `IngestionRequest` is constructed
   - How file is stored in GCS
   - How GCS path is returned

3. **Artifact Creation:**
   - How `artifact_id` is generated
   - How artifact is registered with `lifecycle_state: PENDING`
   - How materialization is added to artifact record
   - How `boundary_contract_id` is associated

4. **Response Structure:**
   - How structured artifact is created
   - What fields are returned
   - How events are structured

### What NOT to Copy

- ❌ **Class Structure:** `IngestionHandlers(BaseContentHandler)` - You're using `BaseIntentService`
- ❌ **Handler Pattern:** This is an orchestrator handler, not an intent service
- ❌ **Direct Infrastructure:** Any direct database/storage access (use Public Works)
- ❌ **Location:** This lives in `orchestrators/handlers/`, you're building in `realms/content/intent_services/`

### What TO Extract

- ✅ **Business Logic:** How file ingestion actually works
- ✅ **Parameter Handling:** How parameters are validated and used
- ✅ **Public Works Usage:** How abstractions are called
- ✅ **Artifact Patterns:** How artifacts are structured

---

## Reference Implementation 2: save_materialization

### File Location
```
../symphainy_platform/realms/content/orchestrators/content_orchestrator.py
```

### Function to Study
```python
async def _handle_save_materialization(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
```

**Starts around:** Line 1418

### What This Shows You

1. **Parameter Validation:**
   - How `boundary_contract_id` is validated
   - How `file_id` is validated
   - How metadata is extracted from context

2. **Materialization Registration:**
   - How file metadata is retrieved from State Surface
   - How `register_materialization` is called on FileStorageAbstraction
   - What parameters are passed to registration
   - How materialization type/scope/backing_store are handled

3. **Pending Journey Creation:**
   - Look for `create_pending_parse_intent` or similar
   - How ingest_profile/file_type are stored in intent context
   - How pending intent is registered in intent_executions

4. **Lifecycle Transition:**
   - How artifact lifecycle state is updated (PENDING → READY)
   - How State Surface is used for updates

5. **Response Structure:**
   - How structured artifact is created
   - What confirmation fields are returned
   - How events are structured

### What NOT to Copy

- ❌ **Orchestrator Pattern:** This is an orchestrator method, not an intent service
- ❌ **Class Structure:** This is part of `ContentOrchestrator`, not a standalone service
- ❌ **Direct Infrastructure:** Any direct database/storage access (use Public Works)
- ❌ **Location:** This lives in `orchestrators/`, you're building in `realms/content/intent_services/`

### What TO Extract

- ✅ **Business Logic:** How materialization registration works
- ✅ **Pending Journey Pattern:** How to create pending intents
- ✅ **Context Storage:** How to store ingest/file type in intent context
- ✅ **Lifecycle Transitions:** How to update artifact state

---

## How to Use These References

### Step 1: Read the Contract First
Always read the intent contract first to understand what you're building:
- `docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md`
- `docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md`

### Step 2: Read the Base Class
Understand the pattern you should follow:
- `symphainy_platform/bases/intent_service_base.py`

### Step 3: Read the Reference Implementation
Now read the old code to understand the business logic:
- Use the file locations above
- Focus on the specific functions listed
- Extract business logic patterns
- Ignore architectural patterns

### Step 4: Implement Using New Architecture
- Extend `BaseIntentService`
- Follow contract specifications
- Use business logic from references
- Apply new architectural patterns

---

## Key Differences: Old vs New

| Aspect | OLD (Reference) | NEW (What You're Building) |
|--------|----------------|----------------------------|
| **Base Class** | `BaseContentHandler` | `BaseIntentService` |
| **Location** | `orchestrators/handlers/` | `realms/content/intent_services/` |
| **Pattern** | Handler in orchestrator | Standalone intent service |
| **Infrastructure** | May access directly | Public Works only |
| **Telemetry** | May be missing | Required via Nurse SDK |
| **Artifact Registration** | May vary | Via `self.register_artifact()` |

---

## Questions to Answer While Reading References

1. **For ingest_file:**
   - How is hex-encoded file_content decoded?
   - How is GCS path constructed?
   - How is artifact_id generated?
   - How is boundary_contract_id created?
   - What materialization fields are needed?

2. **For save_materialization:**
   - How is materialization registered in index?
   - How is pending parsing journey created?
   - How are ingest/file type stored in context?
   - How is lifecycle state updated?
   - What confirmation is returned?

---

**Last Updated:** January 27, 2026  
**Status:** 🟢 **READY FOR AGENTS**
