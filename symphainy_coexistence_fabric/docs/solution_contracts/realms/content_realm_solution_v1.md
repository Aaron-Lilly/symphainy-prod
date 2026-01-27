# Solution Contract: Content Realm Solution

**Solution:** Content Realm Solution  
**Solution ID:** `content_realm_solution_v1`  
**Status:** DRAFT  
**Priority:** P0  
**Owner:** C-Suite

---

## 1. Business Objective

### Problem Statement
Users need to upload, manage, parse, and process files of various types (structured, unstructured, hybrid) to prepare them for analysis. The Content Realm Solution provides file management, parsing, and deterministic embedding capabilities that enable downstream analysis in the Insights Realm.

### Target Users
- **Primary Persona:** Data Analysts, Content Managers
  - **Goals:** Upload files, parse content, create embeddings, manage file lifecycle
  - **Pain Points:** Complex file types, parsing failures, unclear file status, manual embedding creation

### Success Criteria
- **Business Metrics:**
  - 100+ files processed per day
  - 90%+ successful parsing rate
  - < 30 seconds file upload time
  - 100% file lifecycle visibility

---

## 2. Solution Composition

### Composed Journeys

1. **Journey:** File Upload & Materialization (Journey ID: `journey_content_file_upload_materialization`)
   - **Purpose:** Upload file with content type (structured/unstructured/hybrid) and file type selection, materialize for processing
   - **User Trigger:** User selects content type, file type category, uploads file
   - **Success Outcome:** File uploaded, materialized (after explicit save), available for parsing

2. **Journey:** File Parsing (Journey ID: `journey_content_file_parsing`)
   - **Purpose:** Parse uploaded file (resumes pending parsing journey created during save)
   - **User Trigger:** User selects uploaded file from dropdown, clicks parse (resumes pending journey)
   - **Success Outcome:** File parsed, parsed content saved, available for embedding creation
   - **Note:** Parsing journey is created in PENDING status when user saves artifact (save_materialization), with ingest type and file type stored in intent context. User selection resumes and completes the pending journey.

3. **Journey:** Deterministic Embedding Creation (Journey ID: `journey_content_deterministic_embedding`)
   - **Purpose:** Create deterministic embeddings from parsed files
   - **User Trigger:** User selects parsed file from dropdown, clicks create embeddings
   - **Success Outcome:** Deterministic embeddings created, saved, preview displayed

4. **Journey:** File Management (Journey ID: `journey_content_file_management`)
   - **Purpose:** List, view, delete files
   - **User Trigger:** User accesses file dashboard
   - **Success Outcome:** Files listed with status, user can view details and delete files

### Journey Orchestration

**Sequential Flow (Primary):**
1. User uploads file → Journey: File Upload & Materialization
2. User parses file → Journey: File Parsing
3. User creates embeddings → Journey: Deterministic Embedding Creation

**Parallel Flow:**
- File Management can operate independently
- Multiple files can be uploaded/parsed in parallel

---

## 3. User Experience Flows

### Primary User Flow
```
1. User navigates to Content Pillar
   → Sees content type selection (Structured/Unstructured/Hybrid)
   
2. User selects content type
   → Sees file type categories (PDF, CSV, Binary, etc.)
   
3. User selects file type category
   → Sees file upload area
   → Uploads file (and copybook if binary)
   
4. User clicks "Upload File"
   → File uploaded to GCS
   → File status: PENDING (materialization pending)
   
5. User clicks "Save File"
   → Materialization authorized
   → File status: READY (available for parsing)
   
6. User selects uploaded file from dropdown
   → Sees parse options (ingest profile, artifact type)
   
7. User selects ingest profile and artifact type
   → Clicks "Parse File"
   → File parsed, parsed content saved
   → Parsed file available in dropdown
   
8. User selects parsed file from dropdown
   → Clicks "Create Deterministic Embeddings"
   → Embeddings created and saved
   → Preview displayed
```

### Alternative Flows
- **Flow A:** User only uploads files → Skip parsing, files available for other realms
- **Flow B:** User uploads binary file → Copybook required, validated before parsing
- **Flow C:** User deletes file → File archived (soft delete), removed from active list

---

## 4. Non-Functional Requirements

### Performance
- **Response Time:** File upload < 30 seconds
- **Response Time:** File parsing < 60 seconds
- **Response Time:** Embedding creation < 30 seconds
- **Throughput:** Support 50+ concurrent file operations

### Security
- **Authentication:** Requires Security Solution authentication
- **Authorization:** Role-based access control per file
- **Data Privacy:** Files encrypted at rest and in transit

---

## 5. Solution Components

### 5.1 Content Component
**Purpose:** File upload, parsing, embedding creation

**Business Logic:**
- **Journey:** File Upload & Materialization
  - Intent: `ingest_file` - Upload file to GCS
  - Intent: `save_materialization` - Authorize materialization, register in Supabase, create pending parsing journey with ingest type and file type in intent context

- **Journey:** File Parsing
  - Intent: `parse_content` - Resume pending parsing journey, parse file using ingest type and file type from intent context
  - Intent: `save_parsed_content` - Save parsed content as artifact

- **Journey:** Deterministic Embedding Creation
  - Intent: `create_deterministic_embeddings` - Create deterministic embeddings from parsed content
  - Intent: `save_embeddings` - Save embeddings as artifact

- **Journey:** File Management
  - Intent: `list_artifacts` - List file artifacts (filtered by type, status)
  - Intent: `get_artifact_metadata` - Get file metadata
  - Intent: `archive_file` - Soft delete file (archive)

**UI Components:**
- Content type selection (Structured/Unstructured/Hybrid)
- File type category selection
- File upload area (drag & drop)
- Copybook upload (for binary files)
- File dashboard (list, view, delete)
- File parser (select file, resume pending parsing journey)
- Embedding creator (select parsed file, create embeddings)
- Parse preview (display parsed content)
- Embedding preview (display deterministic embeddings)

**Coexistence Component:**
- **GuideAgent:** Routes to Content Realm
- **Content Liaison Agent:** Content-specific guidance

**Policies:**
- File upload policies (Smart City: Data Steward)
- File type validation policies (Smart City: Data Steward)
- Parsing policies (Smart City: Data Steward)

**Experiences:**
- REST API: `/api/content/upload`, `/api/content/parse`, `/api/content/embeddings`, `/api/content/files`
- Websocket: Real-time upload progress, parsing status, embedding creation status

---

## 6. Solution Artifacts

### Artifacts Produced
- **File Artifacts:** Uploaded files (lifecycle: PENDING → READY → ARCHIVED)
- **Parsed Content Artifacts:** Parsed file content (lifecycle: PENDING → READY)
- **Deterministic Embedding Artifacts:** Deterministic embeddings (lifecycle: PENDING → READY)

### Artifact Relationships
- **Lineage:**
  - Parsed Content → File
  - Deterministic Embeddings → Parsed Content

---

## 7. Integration Points

### Platform Services
- **Content Realm:** Intent services (`ingest_file`, `parse_content`, `create_deterministic_embeddings`, `list_artifacts`)
- **Journey Realm:** Orchestration services (compose content journeys)
- **State Surface:** Artifact registry and lifecycle management

### Civic Systems
- **Smart City Primitives:** Data Steward, Security Guard, Traffic Cop
- **Agent Framework:** GuideAgent, Content Liaison Agent

---

## 8. Testing & Validation

### Business Acceptance Criteria
- [ ] Users can upload files with content type and file type selection
- [ ] Users can parse files by resuming pending parsing journeys (ingest type and file type stored in intent context during save)
- [ ] Users can create deterministic embeddings from parsed files
- [ ] Users can list, view, and delete files
- [ ] File lifecycle is managed correctly (PENDING → READY → ARCHIVED)
- [ ] Copybook validation works for binary files
- [ ] Materialization requires explicit user action

---

## 9. Solution Registry

### Solution Metadata
- **Solution ID:** `content_realm_solution_v1`
- **Solution Version:** 1.0
- **Deployment Status:** DEVELOPMENT
- **Last Updated:** January 27, 2026

### Journey Dependencies
- **Journey 1:** File Upload & Materialization - Status: IMPLEMENTED
- **Journey 2:** File Parsing - Status: IMPLEMENTED
- **Journey 3:** Deterministic Embedding Creation - Status: IMPLEMENTED
- **Journey 4:** File Management - Status: IMPLEMENTED

### Solution Dependencies
- **Depends on:** Security Solution (authentication), Coexistence Solution (navigation)
- **Required by:** Insights Realm Solution (for parsed content and embeddings)

---

## 10. Coexistence Component

**GuideAgent Integration:**
- **Platform Concierge:** GuideAgent routes to Content Realm for file operations
- **Navigation:** GuideAgent helps navigate content workflows

**Solution-Specific Liaison Agents:**
- **Liaison Agent:** Content Liaison Agent
- **Capabilities:**
  - Help users upload files
  - Explain content types and file types
  - Guide parsing process
  - Explain how parsing journeys are created during save and resumed during parse
  - Guide embedding creation
  - Answer questions about file status

**Conversation Topics:**
- "How do I upload a file?"
- "What content type should I choose?"
- "How do I parse a file?"
- "How does the parsing flow work?"
- "How do I create embeddings?"

---

## 11. Evolution & Roadmap

### Current Version
- **Version:** 1.0
- **Status:** IMPLEMENTED

### Planned Enhancements
- **Version 1.1:** Enhanced file type support
- **Version 1.2:** Batch file upload
- **Version 1.3:** Advanced parsing options

---

**Last Updated:** January 27, 2026  
**Owner:** C-Suite
