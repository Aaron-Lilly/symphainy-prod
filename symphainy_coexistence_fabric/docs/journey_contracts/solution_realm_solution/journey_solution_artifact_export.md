# Journey Contract: Artifact Export

**Journey:** Artifact Export  
**Journey ID:** `journey_solution_artifact_export`  
**Solution:** Solution Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔵 **PRIORITY 2** - Supporting journey

---

## 1. Journey Overview

### Purpose
Export solution artifacts (blueprint, POC, or roadmap) in various formats (JSON, DOCX, YAML). The export generates a downloadable file and provides a download URL for the user.

### Intents in Journey

| Step | Intent | Description |
|------|--------|-------------|
| 1 | `export_artifact` | Export artifact in specified format |

### Journey Flow
```
[User selects artifact and export format]
    ↓
[Frontend calls OutcomesAPIManager.exportArtifact(type, id, format)]
    ↓
[export_artifact intent submitted to Runtime]
    ↓
[OutcomesOrchestrator._handle_export_artifact()]
    ↓
[Validate artifact_type and artifact_id]
    ↓
[ExportService.export_artifact()]
    ↓
[Generate export file in specified format]
    ↓
[Store export file (GCS)]
    ↓
[Return download URL and filename]
    ↓
[Frontend initiates download]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- `export` - Export result
  - `download_url`: URL to download the exported file
  - `filename`: Suggested filename for download
  - `format`: Export format (json, docx, yaml)
  - `artifact_type`: Type of exported artifact
  - `artifact_id`: ID of exported artifact

### Artifact Lifecycle State Transitions
- Export is a transient artifact (download URL may expire)
- Source artifact lifecycle unchanged

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `export_artifact` | N/A | Generates new export each time |

### Journey Completion Definition

**Journey is considered complete when:**
- Artifact retrieved from Artifact Plane
- Export file generated in specified format
- Download URL returned to frontend
- Frontend initiates file download

---

## 2. Scenario 1: Happy Path

### Test Description
Complete journey works end-to-end without failures.

### Prerequisites
- Valid session with tenant_id and session_id
- Artifact exists in Artifact Plane (blueprint, POC, or roadmap)
- Artifact ID known

### Steps
1. [x] User selects artifact to export
2. [x] User selects export format: "json", "docx", or "yaml"
3. [x] User clicks "Export" button
4. [x] `export_artifact` intent executes with artifact_type, artifact_id, export_format
5. [x] ExportService retrieves artifact and generates export
6. [x] Export file stored and download URL generated
7. [x] Frontend initiates download

### Verification
- [x] Observable artifacts: export with download_url and filename
- [x] Export file in correct format
- [x] Download URL accessible
- [x] Event emitted: `artifact_exported`

### Status
✅ Implemented

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when export fails.

### Failure Injection Points (Test Each)
- **Option A:** Missing artifact_type or artifact_id (validation failure)
- **Option B:** Invalid artifact_type (not blueprint/poc/roadmap)
- **Option C:** Artifact not found
- **Option D:** Export service fails (storage error)

### Steps (Example: Invalid artifact_type)
1. [x] User provides invalid artifact_type ✅
2. [x] `export_artifact` intent executes
3. [x] Validation fails → ❌ **FAILURE**
4. [x] Journey returns error: "Invalid artifact_type: X. Must be 'blueprint', 'poc', or 'roadmap'"
5. [x] User can select valid type and retry

### Verification
- [x] Invalid artifact_type rejected with clear error
- [x] Valid types listed in error message
- [x] State remains consistent
- [x] User can retry with correct input

### Status
✅ Tested

---

## 4. Scenario 3: Partial Success

### Test Description
N/A - Single intent journey. Partial success not applicable.

---

## 5. Scenario 4: Retry/Recovery

### Test Description
Journey recovers correctly when user retries after failure.

### Steps
1. [x] User triggers export → ❌ **FAILS** (e.g., storage error)
2. [x] User clicks "Export" again
3. [x] `export_artifact` intent executes → ✅ **SUCCEEDS**
4. [x] Download URL provided
5. [x] Journey completes

### Verification
- [x] Journey recovers correctly
- [x] New export generated
- [x] Retry succeeds

### Status
✅ Tested

---

## 6. Scenario 5: Boundary Violation

### Test Description
Journey rejects invalid inputs.

### Boundary Violation Points
- **Option A:** No session
- **Option B:** Missing artifact_type or artifact_id
- **Option C:** Invalid artifact_type value
- **Option D:** Invalid export_format

### Steps (Example: Missing artifact_id)
1. [x] User triggers export without artifact_id
2. [x] `export_artifact` intent executes → ❌ **BOUNDARY VIOLATION**
3. [x] Journey rejects request: "artifact_type and artifact_id are required"
4. [x] User can select artifact and retry

### Verification
- [x] Missing parameters rejected with clear error
- [x] State remains consistent
- [x] User can correct issue and retry

### Status
✅ Tested

---

## 7. Integration Points

### Platform Services
- **Outcomes Realm:** `OutcomesOrchestrator._handle_export_artifact()`
- **Artifact Plane:** Artifact retrieval
- **GCS:** Export file storage
- **Runtime:** ExecutionLifecycleManager for intent execution

### Enabling Services
- `ExportService.export_artifact()`

### Frontend
- `OutcomesAPIManager.exportArtifact(artifactType, artifactId, format)`

---

## 8. Architectural Verification

### Intent Flow
- [x] All intents use intent-based API (submitIntent)
- [x] All intents flow through Runtime
- [x] All intents have execution_id
- [x] Parameter validation: artifact_type, artifact_id required

### Export Formats
- [x] JSON - Machine-readable format
- [x] DOCX - Document format for humans
- [x] YAML - Configuration-friendly format

### Observability
- [x] execution_id present in all logs
- [x] Telemetry recorded
- [x] Export events tracked

---

## 9. SRE Verification

### Error Handling
- [x] Invalid artifact_type provides clear error
- [x] Missing artifact provides clear error
- [x] Storage failures handled gracefully

### State Persistence
- [x] Export is transient (download URL may expire)
- [x] Source artifact unchanged
- [x] Export can be regenerated

### Boundaries
- [x] Browser → Frontend: "Export" with format selection
- [x] Frontend → Backend: submitIntent("export_artifact", { artifact_type, artifact_id, export_format })
- [x] Backend → Runtime: ExecutionLifecycleManager.execute()
- [x] Runtime → Realm: OutcomesOrchestrator.handle_intent()
- [x] Realm → ExportService: export_artifact()
- [x] ExportService → GCS: store export file

---

## 10. Gate Status

**Journey is "done" only when:**
- [x] ✅ Happy path works
- [x] ✅ Injected failure handled
- [x] ✅ N/A - Partial success
- [x] ✅ Retry/recovery works
- [x] ✅ Boundary violation rejected
- [x] ✅ Architectural verification passes
- [x] ✅ Observability guarantees met
- [x] ✅ SRE verification passes

**Current Status:** ✅ **IMPLEMENTED**

---

**Last Updated:** January 27, 2026  
**Owner:** Solution Realm Solution Team  
**Implementation:** `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_export_artifact`  
**Frontend:** `symphainy-frontend/shared/managers/OutcomesAPIManager.ts::exportArtifact()`
