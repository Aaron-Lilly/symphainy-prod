# Content & Insights Pillar Implementation Plan

**Date:** January 2026  
**Status:** 📋 **DETAILED IMPLEMENTATION PLAN**  
**Goal:** Bring Content and Insights pillar evolution strategy to life

---

## 🎯 Executive Summary

This plan implements the strategic evolution of Content and Insights pillars to showcase:
- New ingestion capabilities (Upload, EDI, API)
- Enhanced parsing (Kreuzberg, Cobrix, Mainframe, Hybrid)
- Declarative embeddings (HFI wrapper stateless agent)
- Data Mash (platform-native orchestration)
- Multi-level analysis (data quality, structured, unstructured, AAR, PSO, mapping)
- Agentic interactions (Guide + Liaison agents with deep query capabilities)

**Key Principle:**
> Rebuild natively against the new architecture, using legacy code as reference only.

---

## 📋 Architectural Principles (From Q&A)

### 1. Agent Foundation Integration
- ✅ Agents registered during **realm initialization**, not platform startup
- ✅ Realms declare which agents exist, what tools they require, reasoning mode
- ✅ Runtime executes, Agent Foundation manages, Realms define domain intent

### 2. State Surface Usage
- ✅ Realm artifacts (parsed data, analysis results) stored in **durable stores** (GCS, ArangoDB, Supabase)
- ✅ State Surface stores **references, facts, lineage, execution state**
- ✅ Never store large payloads or domain models in State Surface

### 3. Legacy Code Migration
- ❌ **Do NOT migrate legacy code wholesale**
- ✅ Rebuild natively using legacy logic as **reference only**
- ✅ Avoid all legacy anti-patterns (see below)

### 4. Frontend Integration
- ✅ Document frontend contracts (intent schemas, response patterns, state queries)
- ❌ Frontend code changes **out of scope** for this phase
- ✅ Define what UI will need, but don't implement UI changes

### 5. Testing Strategy
- ✅ Lightweight unit and functional testing now
- ✅ Defer full E2E testing until Experience Plane exists
- ✅ Test behavior, not plumbing

---

## ❌ Anti-Patterns to Avoid

1. **Realm-Owned Execution** - Realms creating sessions, managing retries, persisting state directly
2. **Agents Doing Orchestration** - Agents calling other agents, controlling workflows, persisting outputs
3. **Embedding Business Logic in Services** - Services deciding "what should happen next"
4. **Frontend-Driven Control Flow** - UI determining execution order, skipping platform phases
5. **Big-Bang Refactors** - Porting everything first, cleaning up later

**Correct Pattern:**
- Realms declare intent → Runtime executes → State records → Realm consumes results

---

## 🏗️ Implementation Phases

### Phase 0: File Management & Lineage Foundation

**Goal:** Establish file management patterns that preserve user file names, track lineage, and maintain consistent naming (file1 → file1_parsed → file1_embedded)

**Critical:** This phase must be completed **before** Phase 1, as all subsequent phases depend on proper file metadata and lineage tracking.

#### 0.1: Backend - File Metadata Service

**Location:** `symphainy_platform/realms/content/services/file_metadata_service.py`

**Tasks:**
- [ ] Create `FileMetadataService` class
- [ ] Implement `create_file_metadata()` method:
  - Accepts: `file_id`, `ui_name`, `original_filename`, `file_type`, `tenant_id`, `user_id`
  - Stores metadata in Supabase `project_files` table (via SupabaseAdapter)
  - Returns file metadata record
- [ ] Implement `create_parsed_file_metadata()` method:
  - Accepts: `parsed_file_id`, `file_id` (original), `ui_name` (e.g., "parsed_{original_ui_name}"), `tenant_id`, `user_id`
  - Stores metadata in Supabase `parsed_data_files` table
  - Links to original via `file_id` → `project_files.uuid`
  - Returns parsed file metadata record
- [ ] Implement `create_embedding_file_metadata()` method:
  - Accepts: `embedding_id`, `parsed_file_id`, `file_id` (original), `ui_name` (e.g., "embedded_{original_ui_name}"), `tenant_id`, `user_id`
  - Stores metadata in Supabase `embedding_files` table
  - Links to parsed via `parsed_file_id` → `parsed_data_files.parsed_file_id`
  - Links to original via `file_id` → `project_files.uuid`
  - Returns embedding file metadata record
- [ ] Implement `get_file_lineage()` method:
  - Accepts: `file_id` or `ui_name`
  - Returns complete lineage: original → parsed → embedded
  - Queries Supabase tables with proper JOINs
- [ ] Implement `get_file_by_ui_name()` method:
  - Accepts: `ui_name`, `tenant_id`, `user_id`
  - Returns file metadata (supports all three types: uploaded, parsed, embedded)
- [ ] Register service with Content Realm Foundation

**Architecture Pattern:**
```
Supabase Tables (Persistent Metadata):
- project_files: Original uploaded files
  - uuid (file_id)
  - ui_name (user-friendly name, e.g., "Balances")
  - original_filename
  - tenant_id, user_id
  - status: "uploaded"

- parsed_data_files: Parsed file metadata
  - parsed_file_id (UUID)
  - file_id → project_files.uuid (lineage link)
  - ui_name (e.g., "parsed_Balances")
  - tenant_id, user_id
  - status: "parsed"

- embedding_files: Embedding metadata
  - embedding_id (UUID)
  - parsed_file_id → parsed_data_files.parsed_file_id (lineage link)
  - file_id → project_files.uuid (lineage link)
  - ui_name (e.g., "embedded_Balances")
  - tenant_id, user_id
  - status: "embedded"

State Surface (Execution State & References):
- Stores file references (not metadata)
- Stores lineage facts (file_id → parsed_file_id → embedding_id)
- Stores execution state (upload → parse → embed)
```

**Frontend Contract:**
```typescript
// Query: GET /api/content/file/{ui_name}/metadata
interface FileMetadata {
  file_id: string;
  ui_name: string;
  original_filename: string;
  file_type: string;
  status: "uploaded" | "parsed" | "embedded";
  tenant_id: string;
  user_id: string;
  created_at: string;
}

// Query: GET /api/content/file/{file_id}/lineage
interface FileLineage {
  original_file: FileMetadata;
  parsed_files: Array<FileMetadata & { parsed_file_id: string }>;
  embedded_files: Array<FileMetadata & { embedding_id: string; parsed_file_id: string }>;
}
```

**Testing:**
- [ ] Unit test: `create_file_metadata()` stores in Supabase
- [ ] Unit test: `create_parsed_file_metadata()` links to original
- [ ] Unit test: `create_embedding_file_metadata()` links to parsed and original
- [ ] Functional test: `get_file_lineage()` returns complete lineage
- [ ] Functional test: `get_file_by_ui_name()` returns correct file

---

#### 0.2: Backend - State Surface Lineage Tracking

**Location:** `symphainy_platform/runtime/state_surface.py`

**Tasks:**
- [ ] Add `store_file_lineage()` method:
  - Accepts: `file_id`, `file_type` ("uploaded" | "parsed" | "embedded"), `parent_file_id` (optional), `ui_name`
  - Stores lineage fact in State Surface:
    ```python
    {
      "file_id": "...",
      "file_type": "uploaded",
      "ui_name": "file1",
      "lineage": {
        "parent_file_id": None,  # Original has no parent
        "child_file_ids": ["parsed_file_id_1", "parsed_file_id_2"]
      }
    }
    ```
  - For parsed files: `parent_file_id` = original `file_id`
  - For embedded files: `parent_file_id` = `parsed_file_id`
- [ ] Add `get_file_lineage_from_state()` method:
  - Accepts: `file_id` or `ui_name`
  - Returns lineage chain from State Surface (fast lookup)
  - Falls back to Supabase if not in State Surface
- [ ] Add `link_file_versions()` method:
  - Accepts: `parent_file_id`, `child_file_id`, `relationship_type` ("parsed_from" | "embedded_from")
  - Updates lineage in State Surface
  - Updates lineage in Supabase (via FileMetadataService)
- [ ] Ensure `store_file()` method:
  - Preserves `ui_name` in metadata
  - Stores lineage reference if parent exists
  - Links to Supabase metadata (via FileMetadataService)

**State Surface Lineage Pattern:**
```python
# State Surface stores lineage facts (references, not data)
{
  "file:tenant:session:file_id": {
    "file_id": "uuid-123",
    "ui_name": "file1",
    "file_type": "uploaded",
    "storage_location": "gcs://bucket/path",
    "lineage": {
      "parent_file_id": None,
      "child_file_ids": ["parsed-uuid-456"],
      "relationships": {
        "parsed-uuid-456": "parsed_from"
      }
    }
  },
  "file:tenant:session:parsed-uuid-456": {
    "file_id": "parsed-uuid-456",
    "ui_name": "file1_parsed",
    "file_type": "parsed",
    "parent_file_id": "uuid-123",
    "storage_location": "gcs://bucket/parsed/path",
    "lineage": {
      "parent_file_id": "uuid-123",
      "child_file_ids": ["embedding-uuid-789"],
      "relationships": {
        "embedding-uuid-789": "embedded_from"
      }
    }
  }
}
```

**Testing:**
- [ ] Unit test: `store_file_lineage()` stores lineage facts
- [ ] Unit test: `get_file_lineage_from_state()` retrieves lineage chain
- [ ] Functional test: `link_file_versions()` updates both State Surface and Supabase

---

#### 0.3: Backend - Content Orchestrator Enhancement

**Location:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Tasks:**
- [ ] Update `handle_upload_intent()` to:
  - Extract `ui_name` from filename (sanitize for display)
  - Call `FileMetadataService.create_file_metadata()` after file upload
  - Store `ui_name` in State Surface metadata
  - Store lineage fact in State Surface (original file, no parent)
- [ ] Update `parse_file()` to:
  - After parsing, generate `parsed_ui_name` = `f"parsed_{original_ui_name}"`
  - Call `FileMetadataService.create_parsed_file_metadata()` with lineage link
  - Store parsed file reference in State Surface with lineage link
  - Call `StateSurface.link_file_versions()` to link parsed → original
- [ ] Add `handle_generate_embeddings_intent()` (for Phase 3) to:
  - After embedding generation, generate `embedded_ui_name` = `f"embedded_{original_ui_name}"`
  - Call `FileMetadataService.create_embedding_file_metadata()` with lineage links
  - Store embedding reference in State Surface with lineage links
  - Call `StateSurface.link_file_versions()` to link embedded → parsed → original

**Naming Pattern Enforcement:**
```python
# Original file: "Balances.xlsx"
ui_name = "Balances"  # Extracted from filename, sanitized

# Parsed file:
parsed_ui_name = f"parsed_{ui_name}"  # "parsed_Balances"

# Embedded file:
embedded_ui_name = f"embedded_{ui_name}"  # "embedded_Balances"
```

**Testing:**
- [ ] Functional test: Upload preserves `ui_name`
- [ ] Functional test: Parsing creates `parsed_{ui_name}` and links lineage
- [ ] Functional test: Embedding creates `embedded_{ui_name}` and links lineage

---

#### 0.4: Backend - File Storage Abstraction Enhancement

**Location:** `symphainy_platform/foundations/public_works/abstractions/file_storage_abstraction.py`

**Tasks:**
- [ ] Ensure `upload_file()` method:
  - Preserves `ui_name` in metadata (if provided)
  - Stores metadata in Supabase `project_files` table (via SupabaseFileAdapter)
  - Returns `file_id` and `ui_name` in result
- [ ] Ensure metadata structure includes:
  - `ui_name`: User-friendly display name
  - `original_filename`: Full original filename
  - `file_id`: UUID identifier
  - `tenant_id`, `user_id`: For multi-tenant isolation

**Testing:**
- [ ] Functional test: `upload_file()` preserves `ui_name` in Supabase
- [ ] Functional test: `upload_file()` returns `file_id` and `ui_name`

---

#### 0.5: Documentation - File Management Patterns

**Location:** `docs/file_management_patterns.md`

**Tasks:**
- [ ] Document file naming pattern:
  - Original: `ui_name` (e.g., "Balances")
  - Parsed: `parsed_{ui_name}` (e.g., "parsed_Balances")
  - Embedded: `embedded_{ui_name}` (e.g., "embedded_Balances")
- [ ] Document lineage tracking:
  - Supabase tables for persistent metadata
  - State Surface for execution state and fast lineage lookups
  - Lineage links: `file_id` → `parsed_file_id` → `embedding_id`
- [ ] Document frontend contract:
  - Query files by `ui_name` (not UUID)
  - Display `ui_name` in UI (not UUID)
  - Query lineage to trace embeddings → parsed → original

**Frontend Contract:**
```typescript
// Query files by ui_name (not UUID)
GET /api/content/file/{ui_name}/metadata

// Query lineage
GET /api/content/file/{file_id}/lineage

// List files (returns ui_name for display)
GET /api/content/files?tenant_id={id}&user_id={id}
// Returns: [{ file_id, ui_name, original_filename, status, ... }]
```

**Testing:**
- [ ] Documentation review: Patterns are clear and consistent

---

### Phase 1: Content Pillar Ingestion Evolution

**Goal:** Evolve upload section to ingestion section with Upload, EDI, and API tabs

#### 1.1: Backend - Ingestion Service Enhancement

**Location:** `symphainy_platform/realms/content/services/ingestion_service.py`

**Tasks:**
- [ ] Create `IngestionService` class
- [ ] Implement `ingest_data()` method that:
  - Accepts `IngestionRequest` (from IngestionAbstraction)
  - Routes to appropriate ingestion method (Upload/EDI/API)
  - Stores file via `FileStorageAbstraction`
  - Creates file reference in State Surface
  - Returns `IngestionResult` with `file_id`, `file_reference`, `storage_location`
- [ ] Integrate with existing `IngestionAbstraction` from Public Works
- [ ] Register service with Content Realm Foundation

**Frontend Contract:**
```typescript
// Intent: content.ingest
interface IngestionIntent {
  intent_type: "content.ingest";
  realm: "content";
  payload: {
    ingestion_type: "upload" | "edi" | "api";
    // For upload:
    file_data?: string; // base64
    filename?: string;
    // For EDI:
    edi_connection_id?: string;
    edi_file_id?: string;
    // For API:
    api_endpoint_id?: string;
    api_payload?: any;
    metadata?: Record<string, any>;
  };
}

// Response: Async execution
interface IngestionResponse {
  execution_id: string;
  status: "initiated" | "in_progress" | "completed" | "failed";
  result?: {
    file_id: string;
    file_reference: string;
    storage_location: string;
    ingestion_metadata: Record<string, any>;
  };
}
```

**Testing:**
- [ ] Unit test: `IngestionService.ingest_data()` with each ingestion type
- [ ] Functional test: Upload → File Storage → State Surface reference
- [ ] Functional test: EDI → File Storage → State Surface reference
- [ ] Functional test: API → File Storage → State Surface reference

---

#### 1.2: Backend - Content Orchestrator Enhancement

**Location:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Tasks:**
- [ ] Add `handle_ingest_intent()` method (if not exists)
- [ ] Method should:
  - Accept `content.ingest` intent
  - Call `IngestionService.ingest_data()`
  - After ingestion, automatically trigger parsing
  - Return execution result
- [ ] Ensure existing `handle_upload_intent()` still works (backward compatibility)

**Frontend Contract:**
- Same as 1.1 (no changes needed)

**Testing:**
- [ ] Functional test: `content.ingest` intent → ingestion → parsing
- [ ] Functional test: `content.upload` intent still works (backward compatibility)

---

#### 1.3: Backend - Content Realm Manager Enhancement

**Location:** `symphainy_platform/realms/content/manager.py`

**Tasks:**
- [ ] Register `content.ingest` capability with Curator
- [ ] Initialize `IngestionService` in `ContentRealmManager.initialize()`
- [ ] Pass `IngestionService` to `ContentOrchestrator`

**Testing:**
- [ ] Unit test: Capability registration
- [ ] Functional test: Realm initialization with IngestionService

---

#### 1.4: Documentation - Frontend Contracts

**Location:** `docs/frontend_contracts/content_ingestion.md`

**Tasks:**
- [ ] Document `content.ingest` intent schema
- [ ] Document response patterns (async execution)
- [ ] Document state queries UI will need:
  - Query execution status: `GET /api/execution/{execution_id}/status`
  - Query file metadata: `GET /api/content/file/{file_id}/metadata`
  - Query ingestion history: `GET /api/content/ingestion/history?tenant_id={id}`

**Note:** Frontend implementation is out of scope, but contracts are documented.

---

### Phase 2: Content Pillar Parsing Results Visualization

**Goal:** Display parsing results with parser metadata and action buttons

#### 2.1: Backend - Parsing Results Service

**Location:** `symphainy_platform/realms/content/services/parsing_results_service.py`

**Tasks:**
- [ ] Create `ParsingResultsService` class
- [ ] Implement `get_parsing_results()` method:
  - Accepts `file_id` or `file_reference`
  - Retrieves parsing results from State Surface (references)
  - Retrieves parsed data from GCS (via FileStorageAbstraction)
  - Returns structured parsing results with metadata
- [ ] Implement `get_parser_metadata()` method:
  - Returns parser type, version, confidence scores
  - Returns schema fingerprint
  - Returns parsing errors/warnings
- [ ] Register service with Content Realm Foundation

**Frontend Contract:**
```typescript
// Query: GET /api/content/parsing/{file_id}/results
interface ParsingResults {
  file_id: string;
  file_reference: string;
  parsing_status: "pending" | "in_progress" | "completed" | "failed";
  parser_type: "structured" | "unstructured" | "hybrid" | "workflow_sop";
  parser_name: "kreuzberg" | "cobrix" | "mainframe" | "excel" | "pdf" | ...;
  parser_version: string;
  schema_fingerprint: string;
  confidence_score: number;
  parsed_data: {
    structured?: any; // Table data
    unstructured?: any; // Text chunks
    hybrid?: {
      structured: any;
      unstructured: any;
      correlation_map: any;
    };
  };
  metadata: {
    field_extraction_confidence: Record<string, number>;
    parsing_errors: string[];
    parsing_warnings: string[];
  };
}
```

**Testing:**
- [ ] Unit test: `get_parsing_results()` with different parser types
- [ ] Functional test: Retrieve parsing results from State Surface + GCS
- [ ] Functional test: Handle missing parsing results gracefully

---

#### 2.2: Backend - Content Orchestrator Enhancement

**Location:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Tasks:**
- [ ] Ensure `parse_file()` method stores parsing metadata in State Surface
- [ ] Add parsing metadata to execution state:
  - Parser type used
  - Parser version
  - Schema fingerprint
  - Confidence scores
- [ ] Store parsed data references (not data itself) in State Surface

**Testing:**
- [ ] Functional test: Parsing stores metadata in State Surface
- [ ] Functional test: Parsed data stored in GCS, references in State Surface

---

#### 2.3: Documentation - Frontend Contracts

**Location:** `docs/frontend_contracts/parsing_results.md`

**Tasks:**
- [ ] Document parsing results query API
- [ ] Document parser metadata structure
- [ ] Document action buttons:
  - "View Full Results" → Detailed parsing view (frontend route)
  - "Create Data Mash" → Submit `data_mash.create` intent
  - "Export Parsed Data" → Download from GCS (via FileStorageAbstraction)

---

### Phase 3: Content Pillar Declarative Embeddings

**Goal:** Display declarative embeddings generated by HFI wrapper stateless agent

#### 3.1: Backend - HFI Wrapper Agent (Stateless)

**Location:** `symphainy_platform/realms/content/agents/hfi_wrapper_agent.py`

**Tasks:**
- [ ] Create `HFIWrapperAgent` class extending `GroundedReasoningAgentBase`
- [ ] Implement `generate_embedding()` method:
  - Accepts text or file_reference
  - Calls HuggingFace Inference Endpoint (via adapter)
  - Returns embedding with metadata
- [ ] Implement `generate_embeddings_batch()` for multiple texts
- [ ] Store embeddings in Meilisearch (via SemanticSearchAbstraction)
- [ ] Store embedding references in State Surface (not embeddings themselves)
- [ ] Register agent with Agent Foundation during Content Realm initialization

**Frontend Contract:**
```typescript
// Intent: content.generate_embeddings
interface GenerateEmbeddingsIntent {
  intent_type: "content.generate_embeddings";
  realm: "content";
  payload: {
    file_reference: string;
    embedding_type?: "field_level" | "document_level" | "both";
    model?: string; // Default: HFI endpoint model
  };
}

// Response: Async execution
interface EmbeddingsResponse {
  execution_id: string;
  status: "initiated" | "in_progress" | "completed" | "failed";
  result?: {
    embedding_id: string;
    embedding_reference: string; // State Surface reference
    model: string;
    dimension: number;
    field_embeddings?: Record<string, string>; // field_name -> embedding_id
    document_embedding?: string; // embedding_id
  };
}

// Query: GET /api/content/embeddings/{file_id}
interface EmbeddingsStatus {
  file_id: string;
  embedding_status: "pending" | "in_progress" | "completed" | "failed";
  embedding_id?: string;
  model?: string;
  dimension?: number;
  generated_at?: string;
}
```

**Testing:**
- [ ] Unit test: `HFIWrapperAgent.generate_embedding()` with mock HF adapter
- [ ] Functional test: Generate embeddings → Store in Meilisearch → Store reference in State Surface
- [ ] Functional test: Batch embedding generation

---

#### 3.2: Backend - Embeddings Service

**Location:** `symphainy_platform/realms/content/services/embeddings_service.py`

**Tasks:**
- [ ] Create `EmbeddingsService` class
- [ ] Implement `get_embeddings_status()` method:
  - Accepts `file_id`
  - Queries State Surface for embedding references
  - Returns embedding status and metadata
- [ ] Implement `get_embedding_metadata()` method:
  - Returns model, dimensions, generation timestamp
  - Returns similarity scores (if available)
- [ ] Register service with Content Realm Foundation

**Testing:**
- [ ] Unit test: `get_embeddings_status()` with different states
- [ ] Functional test: Query embedding status from State Surface

---

#### 3.3: Backend - Content Orchestrator Enhancement

**Location:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Tasks:**
- [ ] Add `handle_generate_embeddings_intent()` method
- [ ] Method should:
  - Accept `content.generate_embeddings` intent
  - Call `HFIWrapperAgent.generate_embedding()` (via Agent Foundation)
  - Store embedding references in State Surface
  - Return execution result
- [ ] Optionally: Auto-generate embeddings after parsing (configurable)

**Testing:**
- [ ] Functional test: `content.generate_embeddings` intent → agent execution → State Surface reference

---

#### 3.4: Documentation - Frontend Contracts

**Location:** `docs/frontend_contracts/embeddings.md`

**Tasks:**
- [ ] Document embeddings generation intent
- [ ] Document embeddings status query
- [ ] Document embedding visualization data structure
- [ ] Document integration points (Insights Pillar, Data Mash)

---

### Phase 4: Content Pillar Data Mash Integration

**Goal:** Enable Data Mash creation from parsed content with real-time status tracking

#### 4.1: Backend - Data Mash Orchestrator Enhancement

**Location:** `symphainy_platform/realms/insights/orchestrators/data_mash_orchestrator.py`

**Tasks:**
- [ ] Ensure `create_mash()` method accepts content references
- [ ] Ensure method subscribes to DataMashSaga execution events
- [ ] Store Data Mash status in State Surface (references, not full state)
- [ ] Return execution_id for status tracking

**Frontend Contract:**
```typescript
// Intent: data_mash.create
interface DataMashCreateIntent {
  intent_type: "data_mash.create";
  realm: "insights";
  payload: {
    content_refs: string[]; // file_references from Content Pillar
    options?: {
      target_domain?: string;
      confidence_level?: "high" | "medium" | "low";
    };
  };
}

// Response: Async execution
interface DataMashResponse {
  execution_id: string;
  mash_id: string;
  status: "initiated" | "data_quality" | "semantic_interpretation" | "semantic_mapping" | "registered" | "failed";
  current_phase: string;
  result?: {
    data_quality_report?: any;
    semantic_interpretations?: any;
    canonical_model?: any;
  };
}

// Query: GET /api/insights/data_mash/{mash_id}/status
interface DataMashStatus {
  mash_id: string;
  status: string;
  current_phase: string;
  phases: {
    data_quality: { status: "pending" | "in_progress" | "completed" | "failed"; result?: any };
    semantic_interpretation: { status: "pending" | "in_progress" | "completed" | "failed"; result?: any };
    semantic_mapping: { status: "pending" | "in_progress" | "completed" | "failed"; result?: any };
    registered: { status: "pending" | "in_progress" | "completed" | "failed"; result?: any };
  };
}
```

**Testing:**
- [ ] Functional test: `data_mash.create` intent → DataMashSaga execution
- [ ] Functional test: Status tracking via State Surface queries
- [ ] Functional test: Phase completion events

---

#### 4.2: Backend - Content Orchestrator Enhancement

**Location:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Tasks:**
- [ ] Add helper method to get content references for Data Mash
- [ ] Ensure parsed content references are queryable from State Surface

**Testing:**
- [ ] Functional test: Query content references for Data Mash creation

---

#### 4.3: Documentation - Frontend Contracts

**Location:** `docs/frontend_contracts/data_mash.md`

**Tasks:**
- [ ] Document Data Mash creation intent
- [ ] Document Data Mash status query
- [ ] Document real-time status updates (polling pattern for now, WebSocket later)
- [ ] Document Data Mash results structure

---

### Phase 5: Insights Pillar Data Quality Assessment

**Goal:** Display data quality assessments for binary files, unstructured PDFs, structured data, and hybrid files

#### 5.1: Backend - Data Quality Service Enhancement

**Location:** `symphainy_platform/realms/insights/services/data_quality_service.py`

**Tasks:**
- [ ] Enhance `run_data_quality()` method to support:
  - Binary files: Completeness, structural consistency, null density
  - Unstructured PDFs: Text extraction quality, OCR confidence, structure detection
  - Structured data: Schema validation, field entropy, data type consistency
  - Hybrid files: Both structured and unstructured quality metrics
- [ ] Store quality reports in GCS (via FileStorageAbstraction)
- [ ] Store quality report references in State Surface
- [ ] Return structured quality report with scores and issues

**Frontend Contract:**
```typescript
// Query: GET /api/insights/data_quality/{mash_id}/report
interface DataQualityReport {
  mash_id: string;
  overall_quality_score: number; // 0-1
  analysis_type: "binary" | "unstructured_pdf" | "structured" | "hybrid";
  quality_metrics: {
    completeness: number;
    structural_consistency?: number;
    null_density?: number;
    text_extraction_quality?: number;
    ocr_confidence?: number;
    schema_validation?: number;
    field_entropy?: Record<string, number>;
    data_type_consistency?: Record<string, number>;
  };
  issues: Array<{
    field?: string;
    issue_type: "warning" | "error" | "critical";
    description: string;
    confidence: number;
  }>;
  report_reference: string; // State Surface reference
  generated_at: string;
}
```

**Testing:**
- [ ] Unit test: `run_data_quality()` with each analysis type
- [ ] Functional test: Quality report generation → GCS storage → State Surface reference
- [ ] Functional test: Quality report retrieval

---

#### 5.2: Backend - Insights Orchestrator Enhancement

**Location:** `symphainy_platform/realms/insights/orchestrators/data_mash_orchestrator.py`

**Tasks:**
- [ ] Ensure DataMashSaga DATA_QUALITY phase calls `DataQualityService`
- [ ] Store quality report references in State Surface after phase completion
- [ ] Make quality reports queryable by mash_id

**Testing:**
- [ ] Functional test: DataMashSaga DATA_QUALITY phase → quality report generation

---

#### 5.3: Documentation - Frontend Contracts

**Location:** `docs/frontend_contracts/data_quality.md`

**Tasks:**
- [ ] Document data quality report query API
- [ ] Document quality metrics structure
- [ ] Document issue categorization
- [ ] Document quality actions (Fix Issues, Export Report, Re-analyze)

---

### Phase 6: Insights Pillar Multi-Type Analysis

**Goal:** Support structured, unstructured, AAR, PSO, and data mapping analysis types

#### 6.1: Backend - Analysis Services Enhancement

**Location:** `symphainy_platform/realms/insights/services/`

**Tasks:**
- [ ] Enhance `SemanticInterpretationService` to support:
  - Structured analysis: Statistical summaries, distributions, correlations, anomalies
  - Unstructured analysis: Text analysis (sentiment, topics, entities), document structure, key phrases
- [ ] Create `AARAnalysisService` (if not exists):
  - Process analysis
  - Outcome assessment
  - Improvement recommendations
- [ ] Create `PSOAnalysisService` (if not exists):
  - Step-by-step process analysis
  - Bottleneck identification
  - Optimization suggestions
- [ ] Enhance `SemanticMappingService` to support:
  - Field mapping visualization
  - Canonical model display
  - Mapping confidence scores
  - Mapping conflicts/warnings
- [ ] Store analysis results in GCS/ArangoDB (not State Surface)
- [ ] Store analysis result references in State Surface

**Frontend Contract:**
```typescript
// Intent: insights.analyze
interface AnalysisIntent {
  intent_type: "insights.analyze";
  realm: "insights";
  payload: {
    mash_id: string;
    analysis_type: "structured" | "unstructured" | "aar" | "pso" | "mapping";
    options?: Record<string, any>;
  };
}

// Response: Async execution
interface AnalysisResponse {
  execution_id: string;
  analysis_id: string;
  status: "initiated" | "in_progress" | "completed" | "failed";
  result?: {
    analysis_reference: string; // State Surface reference
    analysis_type: string;
    summary: any;
    detailed_results?: any;
  };
}

// Query: GET /api/insights/analysis/{analysis_id}/results
interface AnalysisResults {
  analysis_id: string;
  analysis_type: string;
  status: "completed" | "failed";
  summary: any;
  detailed_results?: any;
  result_reference: string;
}
```

**Testing:**
- [ ] Unit test: Each analysis service with mock data
- [ ] Functional test: Analysis execution → result storage → State Surface reference
- [ ] Functional test: Analysis result retrieval

---

#### 6.2: Backend - Insights Orchestrator Enhancement

**Location:** `symphainy_platform/realms/insights/orchestrators/data_mash_orchestrator.py`

**Tasks:**
- [ ] Ensure DataMashSaga phases call appropriate analysis services
- [ ] Store analysis result references in State Surface
- [ ] Make analysis results queryable by mash_id and analysis_type

**Testing:**
- [ ] Functional test: DataMashSaga phases → analysis services → result storage

---

#### 6.3: Documentation - Frontend Contracts

**Location:** `docs/frontend_contracts/analysis_types.md`

**Tasks:**
- [ ] Document each analysis type intent
- [ ] Document analysis results structure for each type
- [ ] Document tabbed interface pattern (frontend guidance)

---

### Phase 7: Insights Pillar Multi-Level Query Interface

**Goal:** Enable multi-level queries with Guide and Liaison agents

#### 7.1: Backend - Guide Agent (Global Concierge)

**Location:** `symphainy_platform/agentic/agents/guide_agent.py` (new)

**Tasks:**
- [ ] Create `GuideAgent` class extending `GroundedReasoningAgentBase`
- [ ] Implement `interpret_query()` method:
  - Accepts natural language query
  - Determines which realm/pillar the query belongs to
  - Routes to appropriate liaison agent
  - Returns query interpretation and routing
- [ ] Implement `execute_global_query()` method:
  - Handles queries that span multiple realms
  - Coordinates with multiple liaison agents
  - Aggregates results
- [ ] Register agent with Agent Foundation at platform startup (not realm initialization)

**Frontend Contract:**
```typescript
// Intent: guide.interpret_query
interface GuideQueryIntent {
  intent_type: "guide.interpret_query";
  realm: "guide";
  payload: {
    query: string; // Natural language query
    context?: {
      current_pillar?: string;
      session_id?: string;
    };
  };
}

// Response: Synchronous
interface GuideQueryResponse {
  interpretation: {
    intent: string;
    target_realm: "content" | "insights" | "journey" | "solution";
    target_liaison_agent: string;
    query_parameters: Record<string, any>;
  };
  routing: {
    should_route_to_liaison: boolean;
    liaison_agent_name: string;
  };
}
```

**Testing:**
- [ ] Unit test: `interpret_query()` with various query types
- [ ] Functional test: Query interpretation → liaison agent routing

---

#### 7.2: Backend - Enhanced Content Liaison Agent

**Location:** `symphainy_platform/realms/content/agents/content_liaison_agent.py` (new)

**Tasks:**
- [ ] Create `ContentLiaisonAgent` class extending `GroundedReasoningAgentBase`
- [ ] Implement `handle_query()` method:
  - Accepts interpreted query from Guide Agent
  - Executes content-specific queries:
    - "Show me all parsed Excel files"
    - "Which files used Kreuzberg parser?"
    - "Show files with parsing errors"
    - "List all content in Data Mash X"
  - Uses Runtime tools for fact gathering
  - Queries State Surface for content metadata
  - Returns query results
- [ ] Implement `provide_guidance()` method:
  - Ingestion guidance (Upload vs EDI vs API)
  - Parsing guidance (parser selection, results interpretation)
  - Data Mash guidance (phase explanation, content selection)
- [ ] Register agent with Agent Foundation during Content Realm initialization

**Frontend Contract:**
```typescript
// Intent: content.liaison.query
interface ContentLiaisonQueryIntent {
  intent_type: "content.liaison.query";
  realm: "content";
  payload: {
    query: string;
    query_type: "list_files" | "parser_info" | "parsing_errors" | "data_mash_content" | "guidance";
    parameters?: Record<string, any>;
  };
}

// Response: Synchronous or Async (depending on query complexity)
interface ContentLiaisonQueryResponse {
  query_id: string;
  status: "completed" | "in_progress";
  results?: any;
  guidance?: string;
  suggestions?: string[];
}
```

**Testing:**
- [ ] Unit test: `handle_query()` with different query types
- [ ] Functional test: Query execution → Runtime tools → State Surface → results
- [ ] Functional test: Guidance generation

---

#### 7.3: Backend - Enhanced Insights Liaison Agent

**Location:** `symphainy_platform/realms/insights/agents/insights_liaison_agent.py` (new)

**Tasks:**
- [ ] Create `InsightsLiaisonAgent` class extending `GroundedReasoningAgentBase`
- [ ] Implement `handle_query()` method:
  - Accepts interpreted query from Guide Agent
  - Executes insights-specific queries:
    - Level 1: "Show me my aging reports"
    - Level 2: "Show me customers who are more than 90 days late"
    - Level 3: "Show me the names and contact info for customers >90 days late"
  - Uses Runtime tools for fact gathering
  - Queries State Surface for analysis results
  - Queries Meilisearch for semantic search
  - Returns query results with drill-down capabilities
- [ ] Implement `provide_guidance()` method:
  - Analysis guidance (type selection, results interpretation)
  - Query assistance (formulation, refinement)
  - Deep dive support (multi-level navigation)
  - Data Mash guidance (results interpretation, mapping improvements)
- [ ] Register agent with Agent Foundation during Insights Realm initialization

**Frontend Contract:**
```typescript
// Intent: insights.liaison.query
interface InsightsLiaisonQueryIntent {
  intent_type: "insights.liaison.query";
  realm: "insights";
  payload: {
    query: string;
    query_level: 1 | 2 | 3; // Multi-level query depth
    context?: {
      previous_query_id?: string;
      mash_id?: string;
    };
  };
}

// Response: Synchronous or Async
interface InsightsLiaisonQueryResponse {
  query_id: string;
  query_level: number;
  status: "completed" | "in_progress";
  results: {
    summary: any;
    detailed_results?: any;
    drill_down_options?: Array<{
      query: string;
      query_level: number;
      description: string;
    }>;
  };
  guidance?: string;
}
```

**Testing:**
- [ ] Unit test: `handle_query()` with different query levels
- [ ] Functional test: Multi-level query execution → fact gathering → results
- [ ] Functional test: Drill-down query generation

---

#### 7.4: Backend - Query Orchestration Service

**Location:** `symphainy_platform/runtime/query_orchestration_service.py` (new)

**Tasks:**
- [ ] Create `QueryOrchestrationService` class
- [ ] Implement `execute_query()` method:
  - Accepts natural language query
  - Calls Guide Agent for interpretation
  - Routes to appropriate liaison agent
  - Coordinates multi-level queries
  - Aggregates results
- [ ] Integrate with Runtime Service for execution tracking
- [ ] Store query history in State Surface (references, not full queries)

**Frontend Contract:**
```typescript
// Intent: query.execute
interface QueryExecuteIntent {
  intent_type: "query.execute";
  realm: "runtime";
  payload: {
    query: string;
    query_level?: 1 | 2 | 3;
    context?: Record<string, any>;
  };
}

// Response: Async execution
interface QueryExecuteResponse {
  execution_id: string;
  query_id: string;
  status: "initiated" | "in_progress" | "completed" | "failed";
  result?: {
    interpretation: any;
    results: any;
    drill_down_options?: any[];
  };
}
```

**Testing:**
- [ ] Functional test: Query execution → Guide Agent → Liaison Agent → results
- [ ] Functional test: Multi-level query coordination
- [ ] Functional test: Query history storage

---

#### 7.5: Documentation - Frontend Contracts

**Location:** `docs/frontend_contracts/multi_level_queries.md`

**Tasks:**
- [ ] Document query execution intent
- [ ] Document query levels and examples
- [ ] Document drill-down query pattern
- [ ] Document query history access

---

### Phase 8: Testing & Integration

**Goal:** Comprehensive testing of all implemented features

#### 8.1: Unit Testing

**Tasks:**
- [ ] Unit tests for all new services
- [ ] Unit tests for all new agents
- [ ] Unit tests for orchestrator enhancements
- [ ] Mock all external dependencies (FileStorage, Meilisearch, HF adapter)

#### 8.2: Functional Testing

**Tasks:**
- [ ] Functional test: Upload → Parsing → Embeddings → Data Mash flow
- [ ] Functional test: EDI ingestion → Parsing → Data Mash flow
- [ ] Functional test: API ingestion → Parsing → Data Mash flow
- [ ] Functional test: Data Quality assessment for all analysis types
- [ ] Functional test: Multi-type analysis execution
- [ ] Functional test: Multi-level query execution
- [ ] Functional test: Guide Agent → Liaison Agent routing

#### 8.3: Integration Testing

**Tasks:**
- [ ] Integration test: Content Pillar E2E (ingestion → parsing → embeddings → Data Mash)
- [ ] Integration test: Insights Pillar E2E (Data Mash → quality → analysis → queries)
- [ ] Integration test: Cross-pillar flow (Content → Insights)
- [ ] Integration test: Agent interactions (Guide → Liaison)

**Note:** Full E2E testing deferred until Experience Plane exists.

---

## 📋 Implementation Checklist

### Foundation (Must Complete First)
- [ ] **Phase 0: File Management & Lineage Foundation**
  - [ ] Phase 0.1: File Metadata Service (Supabase integration, ui_name preservation)
  - [ ] Phase 0.2: State Surface Lineage Tracking (store_file_lineage, link_file_versions)
  - [ ] Phase 0.3: Content Orchestrator Enhancement (ui_name preservation, lineage linking)
  - [ ] Phase 0.4: File Storage Abstraction Enhancement (ui_name in metadata)
  - [ ] Phase 0.5: Documentation (file management patterns, frontend contracts)

### Content Pillar
- [ ] Phase 1: Ingestion Evolution (Upload, EDI, API)
- [ ] Phase 2: Parsing Results Visualization
- [ ] Phase 3: Declarative Embeddings
- [ ] Phase 4: Data Mash Integration
- [ ] Phase 7.2: Enhanced Content Liaison Agent

### Insights Pillar
- [ ] Phase 5: Data Quality Assessment
- [ ] Phase 6: Multi-Type Analysis
- [ ] Phase 7.3: Enhanced Insights Liaison Agent

### Platform-Wide
- [ ] Phase 7.1: Guide Agent (Global Concierge)
- [ ] Phase 7.4: Query Orchestration Service
- [ ] Phase 8: Testing & Integration

---

## 🎯 Success Criteria

1. **File Management & Lineage (Phase 0):**
   - ✅ User file names preserved (`ui_name` pattern)
   - ✅ Consistent naming: file1 → file1_parsed → file1_embedded
   - ✅ Lineage tracked: embeddings → parsed → original
   - ✅ Files queryable by `ui_name` (not just UUID)
   - ✅ Frontend can display user-friendly names

2. **Content Pillar:**
   - ✅ Users can ingest via Upload, EDI, or API (backend ready)
   - ✅ Parsing results are queryable with metadata
   - ✅ Embeddings are generated and queryable
   - ✅ Data Mash can be created from parsed content
   - ✅ Content Liaison Agent provides deep guidance

2. **Insights Pillar:**
   - ✅ Data quality assessments are available for all file types
   - ✅ Multiple analysis types are executable
   - ✅ Multi-level queries are supported
   - ✅ Data Mash results are queryable
   - ✅ Insights Liaison Agent provides deep guidance

4. **Platform Showcase:**
   - ✅ All new capabilities are accessible via intents
   - ✅ Architecture is showcased (Runtime, State Surface, Agents)
   - ✅ Agents demonstrate reasoning capabilities
   - ✅ Data Mash demonstrates platform orchestration

---

## 📝 Notes

1. **Frontend Implementation:** Out of scope for this phase. Only contracts are documented.

2. **State Surface Usage:** Always store references and facts, never large payloads or domain models.

3. **Agent Registration:** Agents registered during realm initialization, not platform startup.

4. **Legacy Code:** Use as reference only, rebuild natively.

5. **Testing:** Lightweight now, full E2E later when Experience Plane exists.

---

**Status:** 📋 **IMPLEMENTATION PLAN COMPLETE - READY FOR EXECUTION**
