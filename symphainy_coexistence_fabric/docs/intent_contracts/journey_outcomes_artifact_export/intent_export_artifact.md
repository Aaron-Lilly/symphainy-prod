# Intent Contract: export_artifact

**Intent:** export_artifact  
**Intent Type:** `export_artifact`  
**Journey:** Artifact Export (`journey_solution_artifact_export`)  
**Realm:** Solution Realm (Implementation: Outcomes Realm)  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔵 **PRIORITY 2**

---

## 1. Intent Overview

### Purpose
Export solution artifacts (blueprint, POC, or roadmap) in various formats (JSON, DOCX, YAML). The export generates a downloadable file and provides a download URL for the user.

### Intent Flow
```
[Frontend: OutcomesAPIManager.exportArtifact(type, id, format)]
    ↓
[submitIntent("export_artifact", { artifact_type, artifact_id, export_format })]
    ↓
[Runtime: ExecutionLifecycleManager.execute()]
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
```

### Expected Observable Artifacts
- `export` - Export result
  - `download_url`: URL to download the exported file
  - `filename`: Suggested filename for download
  - `format`: Export format used
  - `artifact_type`: Type of exported artifact
  - `artifact_id`: ID of exported artifact

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `artifact_type` | `string` | Type: "blueprint", "poc", or "roadmap" | Enum validation |
| `artifact_id` | `string` | ID of artifact to export | Required, non-empty |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `export_format` | `string` | Format: "json", "docx", or "yaml" | `"json"` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `session_id` | `string` | Session identifier | Runtime (required) |
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `execution_id` | `string` | Execution identifier | Runtime |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "export": {
      "download_url": "https://storage.googleapis.com/bucket/exports/roadmap_abc123.json",
      "filename": "roadmap_abc123.json",
      "format": "json",
      "artifact_type": "roadmap",
      "artifact_id": "roadmap_abc123",
      "exported_at": "2026-01-27T10:00:00Z"
    }
  },
  "events": [
    {
      "type": "artifact_exported",
      "artifact_type": "roadmap",
      "artifact_id": "roadmap_abc123",
      "export_format": "json"
    }
  ]
}
```

### Error Response

```json
{
  "error": "Invalid artifact_type: invalid. Must be 'blueprint', 'poc', or 'roadmap'",
  "error_code": "VALIDATION_ERROR",
  "execution_id": "exec_abc123"
}
```

---

## 4. Export Formats

### JSON Export
- Machine-readable format
- Full artifact data
- Filename: `{artifact_type}_{artifact_id}.json`

### DOCX Export
- Document format for humans
- Formatted sections and tables
- Filename: `{artifact_type}_{artifact_id}.docx`

### YAML Export
- Configuration-friendly format
- Structured data
- Filename: `{artifact_type}_{artifact_id}.yaml`

---

## 5. Idempotency

### Idempotency Key
```
N/A - Not idempotent
```

### Scope
- Per export request
- Generates new export each time

### Behavior
- Each invocation generates a new export file
- Download URLs may expire
- Export can be regenerated anytime

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_export_artifact`

### Key Implementation Steps
1. Validate artifact_type ("blueprint", "poc", "roadmap")
2. Validate artifact_id (required)
3. Initialize ExportService with public_works
4. Call ExportService.export_artifact()
5. Service retrieves artifact from Artifact Plane
6. Service generates export file in requested format
7. Service stores file in GCS
8. Return download_url and filename

### Dependencies
- **Public Works:** Used by ExportService
- **Services:** `ExportService.export_artifact()`
- **GCS:** Export file storage
- **Artifact Plane:** Artifact retrieval (via ExportService)

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// OutcomesAPIManager.exportArtifact()
async exportArtifact(
  artifactType: "blueprint" | "poc" | "roadmap",
  artifactId: string,
  format: "json" | "docx" | "yaml" = "json"
): Promise<{ success: boolean; download_url?: string; filename?: string; error?: string }> {
  const platformState = this.getPlatformState();
  
  // Session validation
  if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
    throw new Error("Session required to export artifact");
  }

  // Parameter validation
  if (!artifactType || !artifactId) {
    throw new Error("artifact_type and artifact_id are required for export");
  }

  // Submit intent
  const execution = await platformState.submitIntent(
    "export_artifact",
    {
      artifact_type: artifactType,
      artifact_id: artifactId,
      export_format: format
    }
  );

  // Wait for execution
  const result = await this._waitForExecution(execution, platformState);

  if (result.status === "completed" && result.artifacts?.export) {
    const exportResult = result.artifacts.export;
    
    return {
      success: true,
      download_url: exportResult.download_url,
      filename: exportResult.filename
    };
  }
  
  throw new Error(result.error || "Failed to export artifact");
}
```

### Expected Frontend Behavior
1. User selects artifact to export
2. User selects export format (JSON, DOCX, YAML)
3. User clicks "Export" button
4. Call `exportArtifact(type, id, format)`
5. Show loading state during export
6. Initiate download when URL is returned
7. Show success message

---

## 8. Error Handling

### Validation Errors
- Missing artifact_type or artifact_id → `"artifact_type and artifact_id are required"`
- Invalid artifact_type → `"Invalid artifact_type: X. Must be 'blueprint', 'poc', or 'roadmap'"`
- No session → `"Session required to export artifact"`

### Runtime Errors
- Artifact not found → Error returned from ExportService
- Storage failure → Error returned
- Format generation failure → Error returned

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "export_artifact"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User selects artifact
2. User selects export format
3. User clicks "Export"
4. Export file generated
5. Download URL returned
6. Download initiates

### Boundary Violations
- Invalid artifact_type → Validation error with valid options
- Missing artifact_id → Validation error

### Failure Scenarios
- Artifact not found → Error returned
- Storage failure → Error returned
- Format generation failure → Error returned

---

## 10. Contract Compliance

### Required Artifacts
- `export` - Required (with download_url, filename)

### Required Events
- `artifact_exported` - Required

### Export Lifecycle
- Export is transient (download URL may expire)
- Source artifact unchanged
- Export can be regenerated anytime

### Cross-Reference Analysis

| Source | Expectation | Implementation | Notes |
|--------|-------------|----------------|-------|
| **Journey Contract** | Export in multiple formats | ✅ Implemented | JSON, DOCX, YAML |
| **Solution Contract** | Provide download URL | ✅ Implemented | GCS storage |
| **Frontend** | Initiate download | ✅ Implemented | URL returned |

---

**Last Updated:** January 27, 2026  
**Owner:** Solution Realm Solution Team  
**Status:** ✅ **IMPLEMENTED**
