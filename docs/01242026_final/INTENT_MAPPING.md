# Intent Mapping - Canonical Reference

**Date:** January 25, 2026  
**Status:** ✅ **CANONICAL - EXTRACTED FROM REALM REGISTRIES**  
**Source of Truth:** Realm `declare_intents()` methods

---

## Executive Summary

This document provides the **canonical mapping** of legacy endpoints to intent types, extracted directly from realm registries. This is the source of truth for Phase 4 frontend migration.

**Key Principle:** Phase 4 isn't about inventing behavior — it's about making the frontend finally obey what the backend already proved.

---

## How to Use This Document

1. **For Migration:** Use this to replace legacy endpoint calls with intent submissions
2. **For Validation:** Verify frontend uses only intents listed here
3. **For Testing:** Ensure Phase 3 E2E tests cover all intents you're migrating to

---

## Content Realm Intents

**Source:** `symphainy_platform/realms/content/content_realm.py::declare_intents()`

### File Ingestion
- **Intent:** `ingest_file`
  - **Legacy Endpoints:**
    - `/api/v1/business_enablement/content/upload-file` → `ingest_file`
    - `/api/v1/content-pillar/upload-file` → `ingest_file`
  - **Pattern:** Two-phase (upload first, then submit intent with `file_id`)
  - **Validated:** ✅ Phase 3 E2E test `test_e2e_parsing_produces_real_results`

### File Management
- **Intent:** `register_file`
  - **Legacy Endpoints:** None (already uses intent pattern)
  
- **Intent:** `save_materialization`
  - **Legacy Endpoints:** None (explicit two-phase flow)
  - **Purpose:** Second phase after `ingest_file` (authorizes materialization)

- **Intent:** `retrieve_file_metadata`
  - **Legacy Endpoints:** `/api/v1/content-pillar/get-file-details/{fileId}` → `retrieve_file_metadata`

- **Intent:** `retrieve_file`
  - **Legacy Endpoints:** None (uses file storage abstraction)

- **Intent:** `list_files`
  - **Legacy Endpoints:**
    - `/api/v1/content-pillar/list-parsed-files` → `list_files`
    - `/api/v1/content-pillar/list-files` → `list_files`

- **Intent:** `get_file_by_id`
  - **Legacy Endpoints:** `/api/v1/business_enablement/content/get-file-details/{fileId}` → `get_file_by_id`

- **Intent:** `delete_file` (via `archive_file` or `purge_file`)
  - **Legacy Endpoints:** `/api/v1/content-pillar/delete-file/{fileId}` → `archive_file` or `purge_file`

### Content Processing
- **Intent:** `parse_content`
  - **Legacy Endpoints:** None (already uses intent pattern)
  - **Validated:** ✅ Phase 3 E2E test `test_e2e_parsing_produces_real_results`

- **Intent:** `extract_deterministic_structure`
  - **Legacy Endpoints:** None (new intent from Phase 2)
  - **Validated:** ✅ Phase 3 E2E test `test_e2e_deterministic_to_semantic_pattern_works`

- **Intent:** `hydrate_semantic_profile`
  - **Legacy Endpoints:** None (new intent from Phase 2)
  - **Validated:** ✅ Phase 3 E2E test `test_e2e_deterministic_to_semantic_pattern_works`

- **Intent:** `extract_embeddings` (legacy)
  - **Legacy Endpoints:** None (deprecated, use `hydrate_semantic_profile`)

- **Intent:** `get_parsed_file`
  - **Legacy Endpoints:** None (uses artifact retrieval)

- **Intent:** `get_semantic_interpretation`
  - **Legacy Endpoints:** None (uses artifact retrieval)

### Bulk Operations
- **Intent:** `bulk_ingest_files`
- **Intent:** `bulk_parse_files`
- **Intent:** `bulk_extract_embeddings`
- **Intent:** `bulk_interpret_data`
- **Legacy Endpoints:** None (new intents, no legacy equivalents)

### File Lifecycle
- **Intent:** `archive_file`
- **Intent:** `purge_file`
- **Intent:** `restore_file`
- **Intent:** `validate_file`
- **Intent:** `preprocess_file`
- **Intent:** `search_files`
- **Intent:** `query_files`
- **Intent:** `update_file_metadata`
- **Legacy Endpoints:** None (new intents, no legacy equivalents)

---

## Insights Realm Intents

**Source:** `symphainy_platform/realms/insights/insights_realm.py::declare_intents()`

### Business Analysis
- **Intent:** `analyze_structured_data`
  - **Legacy Endpoints:**
    - `/api/v1/insights-solution/analyze` → `analyze_structured_data`
    - `/api/v1/insights-solution/get-business-summary` → `analyze_structured_data`
  - **Validated:** ✅ Phase 3 E2E test `test_e2e_business_analysis_produces_real_insights`

- **Intent:** `analyze_unstructured_data`
  - **Legacy Endpoints:** `/api/v1/insights-solution/analyze-unstructured` → `analyze_unstructured_data`

### Data Quality
- **Intent:** `assess_data_quality`
  - **Legacy Endpoints:** None (new intent)

### Data Interpretation
- **Intent:** `interpret_data_self_discovery`
  - **Legacy Endpoints:** None (new intent)

- **Intent:** `interpret_data_guided`
  - **Legacy Endpoints:** None (new intent)

### Legacy/Existing
- **Intent:** `analyze_content`
- **Intent:** `interpret_data`
- **Intent:** `map_relationships`
- **Intent:** `query_data`
- **Intent:** `calculate_metrics`
- **Legacy Endpoints:** Various `/api/v1/insights-solution/*` patterns

### Lineage Visualization
- **Intent:** `visualize_lineage`
  - **Legacy Endpoints:** None (new intent)

---

## Journey Realm Intents

**Source:** `symphainy_platform/realms/journey/journey_realm.py::declare_intents()`

### Coexistence Analysis
- **Intent:** `analyze_coexistence`
  - **Legacy Endpoints:**
    - `/api/v1/journey/guide-agent/analyze-user-intent` → `analyze_coexistence` (if coexistence-related)
    - `/api/v1/journey/coexistence-analysis` → `analyze_coexistence`
  - **Validated:** ✅ Phase 3 E2E test `test_e2e_coexistence_analysis_produces_real_analysis`

### Workflow Operations
- **Intent:** `create_workflow`
  - **Legacy Endpoints:** None (uses intent pattern)

- **Intent:** `optimize_process`
  - **Legacy Endpoints:** None (new intent)

### SOP Generation
- **Intent:** `generate_sop`
  - **Legacy Endpoints:** None (uses intent pattern)

- **Intent:** `generate_sop_from_chat`
  - **Legacy Endpoints:** None (new intent)

- **Intent:** `sop_chat_message`
  - **Legacy Endpoints:** None (new intent)

### Blueprint Creation
- **Intent:** `create_blueprint`
  - **Legacy Endpoints:** None (uses intent pattern)

### Guide Agent (Legacy)
- **Legacy Endpoints:**
  - `/api/v1/journey/guide-agent/analyze-user-intent` → Check if coexistence-related → `analyze_coexistence`
  - `/api/v1/journey/guide-agent/get-journey-guidance` → May need new intent or use existing
  - `/api/v1/journey/guide-agent/get-conversation-history/{sessionId}` → Use session state retrieval

---

## Outcomes Realm Intents

**Source:** `symphainy_platform/realms/outcomes/outcomes_realm.py::declare_intents()`

### Synthesis
- **Intent:** `synthesize_outcome`
  - **Legacy Endpoints:** None (uses intent pattern)

### Roadmap Generation
- **Intent:** `generate_roadmap`
  - **Legacy Endpoints:**
    - `/api/v1/business-outcomes-solution/roadmap` → `generate_roadmap`
    - `/api/v1/business-outcomes-pillar/generate-strategic-roadmap` → `generate_roadmap`
  - **Validated:** ✅ Phase 3 E2E test `test_e2e_roadmap_generation_produces_contextually_relevant_recommendations`

### POC Creation
- **Intent:** `create_poc`
  - **Legacy Endpoints:**
    - `/api/v1/business-outcomes-solution/poc-proposal` → `create_poc`
    - `/api/v1/business-outcomes-pillar/generate-proof-of-concept-proposal` → `create_poc`
  - **Validated:** ✅ Phase 3 E2E test `test_e2e_poc_proposal_produces_contextually_relevant_recommendations`

### Solution Creation
- **Intent:** `create_solution`
  - **Legacy Endpoints:** None (uses intent pattern)

### Other Legacy Endpoints
- `/api/v1/business-outcomes-solution/pillar-summaries` → Use `synthesize_outcome` or artifact retrieval
- `/api/v1/business-outcomes-pillar/get-pillar-summaries` → Use `synthesize_outcome` or artifact retrieval
- `/api/v1/business-outcomes-pillar/get-journey-visualization` → Use artifact retrieval

---

## Intent Submission Pattern

### Standard Pattern

```typescript
// ✅ CORRECT: Use intent-based API
const response = await fetch('/api/intent/submit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    intent_type: 'ingest_file',  // From canonical mapping above
    tenant_id: tenantId,
    session_id: sessionId,
    solution_id: solutionId,
    parameters: {
      // Intent-specific parameters (see orchestrator handlers)
      file_id: fileId,  // For two-phase upload
      // ... other parameters
    }
  })
});
```

### Two-Phase File Upload Pattern

**Phase 1: Upload File**
```typescript
// Upload file to GCS (via FileManagementAbstraction)
const uploadResponse = await fetch('/api/content/upload', {
  method: 'POST',
  body: formData  // File content
});

const { file_id, boundary_contract_id } = await uploadResponse.json();
```

**Phase 2: Submit Intent with file_id**
```typescript
// Submit ingest_file intent with file_id
const intentResponse = await fetch('/api/intent/submit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    intent_type: 'ingest_file',
    tenant_id: tenantId,
    session_id: sessionId,
    parameters: {
      file_id: file_id,  // From Phase 1
      boundary_contract_id: boundary_contract_id,  // From Phase 1
      ui_name: fileName,
      file_type: fileType,
      mime_type: mimeType
    }
  })
});
```

**Phase 3: Save Materialization (if needed)**
```typescript
// Explicitly save (materialize) the file
const saveResponse = await fetch('/api/content/save_materialization', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-user-id': userId,
    'x-session-id': sessionId
  },
  body: JSON.stringify({
    boundary_contract_id: boundary_contract_id,
    file_id: file_id,
    tenant_id: tenantId
  })
});
```

---

## Legacy Endpoint → Intent Mapping Summary

| Legacy Endpoint | Intent Type | Realm | Notes |
|----------------|-------------|-------|-------|
| `/api/v1/business_enablement/content/upload-file` | `ingest_file` | Content | Two-phase upload |
| `/api/v1/content-pillar/upload-file` | `ingest_file` | Content | Two-phase upload |
| `/api/v1/content-pillar/delete-file/{fileId}` | `archive_file` or `purge_file` | Content | Check lifecycle requirements |
| `/api/v1/content-pillar/list-parsed-files` | `list_files` | Content | Filter by parsed status |
| `/api/v1/content-pillar/get-file-details/{fileId}` | `get_file_by_id` | Content | Or `retrieve_file_metadata` |
| `/api/v1/business_enablement/content/get-file-details/{fileId}` | `get_file_by_id` | Content | Or `retrieve_file_metadata` |
| `/api/v1/insights-solution/analyze` | `analyze_structured_data` | Insights | ✅ Validated in Phase 3 |
| `/api/v1/insights-solution/get-business-summary` | `analyze_structured_data` | Insights | ✅ Validated in Phase 3 |
| `/api/v1/insights-solution/analyze-unstructured` | `analyze_unstructured_data` | Insights | |
| `/api/v1/journey/guide-agent/analyze-user-intent` | `analyze_coexistence` | Journey | If coexistence-related |
| `/api/v1/journey/guide-agent/get-journey-guidance` | TBD | Journey | May need new intent or use session state |
| `/api/v1/journey/guide-agent/get-conversation-history/{sessionId}` | Session state retrieval | Journey | Use session state, not intent |
| `/api/v1/business-outcomes-solution/roadmap` | `generate_roadmap` | Outcomes | ✅ Validated in Phase 3 |
| `/api/v1/business-outcomes-pillar/generate-strategic-roadmap` | `generate_roadmap` | Outcomes | ✅ Validated in Phase 3 |
| `/api/v1/business-outcomes-solution/poc-proposal` | `create_poc` | Outcomes | ✅ Validated in Phase 3 |
| `/api/v1/business-outcomes-pillar/generate-proof-of-concept-proposal` | `create_poc` | Outcomes | ✅ Validated in Phase 3 |
| `/api/v1/business-outcomes-solution/pillar-summaries` | `synthesize_outcome` | Outcomes | Or artifact retrieval |
| `/api/v1/business-outcomes-pillar/get-pillar-summaries` | `synthesize_outcome` | Outcomes | Or artifact retrieval |
| `/api/v1/business-outcomes-pillar/get-journey-visualization` | Artifact retrieval | Outcomes | Use artifact API, not intent |

---

## Intent Parameters Reference

### Content Realm

#### `ingest_file`
```typescript
{
  file_id: string,  // From Phase 1 upload
  boundary_contract_id: string,  // From Phase 1 upload
  ui_name: string,
  file_type: string,  // "unstructured" | "structured" | "hybrid"
  mime_type: string,
  ingestion_type: "upload" | "edi" | "api"
}
```

#### `parse_content`
```typescript
{
  file_id: string,
  parse_options?: {
    parser_type?: string,
    extract_tables?: boolean,
    extract_images?: boolean
  }
}
```

#### `extract_deterministic_structure`
```typescript
{
  file_id: string
}
```

#### `hydrate_semantic_profile`
```typescript
{
  file_id: string,
  semantic_profile?: string,  // Default: "default"
  model_name?: string  // Default: "text-embedding-ada-002"
}
```

#### `list_files`
```typescript
{
  tenant_id: string,
  session_id?: string,
  file_type?: string,
  status?: string,
  limit?: number,
  offset?: number
}
```

---

### Insights Realm

#### `analyze_structured_data`
```typescript
{
  file_id: string,
  analysis_type?: string,  // "business" | "quality" | "eda"
  options?: {
    include_visualizations?: boolean,
    include_anomalies?: boolean
  }
}
```

---

### Journey Realm

#### `analyze_coexistence`
```typescript
{
  workflow_id: string,
  analysis_options?: {
    include_recommendations?: boolean,
    include_visualizations?: boolean
  }
}
```

#### `generate_sop`
```typescript
{
  workflow_id: string,
  sop_options?: {
    format?: "markdown" | "html" | "pdf",
    include_diagrams?: boolean
  }
}
```

#### `create_blueprint`
```typescript
{
  description: string,
  context?: {
    files?: string[],
    insights?: any,
    journey_data?: any
  }
}
```

---

### Outcomes Realm

#### `generate_roadmap`
```typescript
{
  description?: string,
  synthesis?: any,  // From synthesize_outcome
  context?: {
    files?: string[],
    insights?: any,
    journey_data?: any
  }
}
```

#### `create_poc`
```typescript
{
  description: string,
  poc_options?: {
    scope?: string,
    timeline?: string,
    objectives?: string[]
  },
  synthesis?: any  // From synthesize_outcome
}
```

#### `synthesize_outcome`
```typescript
{
  context?: {
    files?: string[],
    insights?: any,
    journey_data?: any,
    outcomes_data?: any
  }
}
```

---

## Migration Rules

### Rule 1: Two-Phase File Upload
- ✅ Upload file first (Phase 1)
- ✅ Submit `ingest_file` intent with `file_id` (Phase 2)
- ✅ Save materialization if needed (Phase 3)
- ❌ Do NOT send file content in intent parameters

### Rule 2: Remove Legacy Endpoints Completely
- ✅ Remove legacy endpoint call
- ✅ Replace with intent submission
- ❌ Do NOT keep legacy endpoint as fallback
- ❌ Do NOT silently fallback to legacy

### Rule 3: Error Handling
- ✅ Show user-friendly error messages
- ✅ Log migration warnings in dev console
- ❌ Do NOT add retry logic (belongs in Runtime)
- ❌ Do NOT call legacy endpoints on failure

### Rule 4: State Persistence
- ✅ Leave `setRealmState()` TODO in place
- ✅ Add clarifying comment: "Frontend-only continuity, state persisted via intents/artifacts"
- ❌ Do NOT implement Runtime persistence in Phase 4 (defer to Phase 5)

---

## Validation Checklist

For each migrated endpoint:

- [ ] Legacy endpoint completely removed
- [ ] Replaced with `/api/intent/submit` pattern
- [ ] Intent type matches canonical mapping above
- [ ] Parameters match orchestrator handler expectations
- [ ] Two-phase upload pattern used (if file upload)
- [ ] Error handling shows user-friendly messages
- [ ] No fallback to legacy endpoints
- [ ] Tested end-to-end after migration
- [ ] Phase 3 E2E tests still pass

---

## Testing Strategy

### Required Tests

1. **Test Each Pillar After Migration**
   - Migrate one pillar
   - Run it end-to-end
   - Stop if anything fails

2. **Re-run Phase 3 E2E Tests**
   - These are regression lock
   - If one fails, fix before proceeding
   - All 6 E2E tests must pass

### Optional Tests

- **Add new E2E tests?** Only if:
  - You introduce new intent types
  - You change artifact semantics
  - Otherwise, reuse existing suite

**Rule of Thumb:** If frontend migration requires new backend E2E tests, something is wrong.

---

## Files to Migrate

### Content Pillar
- `symphainy-frontend/app/(protected)/pillars/content/components/ContentPillarUpload.tsx`
- `symphainy-frontend/shared/services/content/file-processing.ts`
- `symphainy-frontend/shared/managers/ContentAPIManager.ts`
- `symphainy-frontend/app/(protected)/pillars/content/components/FileDashboard.tsx`
- `symphainy-frontend/app/(protected)/pillars/content/components/DataMash.tsx`
- `symphainy-frontend/app/(protected)/pillars/content/components/ParsePreview.tsx`
- `symphainy-frontend/app/(protected)/pillars/content/components/MetadataExtractor.tsx`

### Insights Pillar
- `symphainy-frontend/shared/services/insights/core.ts`

### Journey Pillar
- `symphainy-frontend/shared/managers/GuideAgentAPIManager.ts`

### Business Outcomes Pillar
- `symphainy-frontend/shared/managers/BusinessOutcomesAPIManager.ts`
- `symphainy-frontend/shared/services/business-outcomes/solution-service.ts`

---

## Next Steps

1. ✅ **Task 4.7 Complete:** Intent mapping extracted from realm registries
2. **Create Migration Helper:** Thin wrapper utility (no semantic abstraction)
3. **Migrate Content Pillar First:** Start with file upload (highest impact)
4. **Test After Each Pillar:** Don't proceed if tests fail
5. **Re-run Phase 3 E2E Tests:** Validate regression lock

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **CANONICAL - READY FOR MIGRATION**
