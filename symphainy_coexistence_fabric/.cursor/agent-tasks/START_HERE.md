# 🚀 START HERE: Agent Implementation Guide

**For Cursor Web Agents implementing intent services**

---

## ⚠️ CRITICAL: Know Your Location

- **Repository:** `symphainy_source_code`
- **Working Directory:** `symphainy_coexistence_fabric/` (within the repo)
- **All paths below are relative to:** `symphainy_coexistence_fabric/`

---

## 📋 Quick Checklist

Before you start, make sure you understand:

- [ ] You're working in `symphainy_coexistence_fabric/` directory
- [ ] You need to create: `symphainy_platform/realms/content/intent_services/`
- [ ] You're implementing 2 services: `ingest_file_service.py` and `save_materialization_service.py`
- [ ] You MUST extend `BaseIntentService` (NOT BaseContentHandler!)
- [ ] You can reference OLD implementations for business logic only

---

## 🎯 Your Task (Simple Version)

1. **Navigate to:** `symphainy_coexistence_fabric/`
2. **Create directory:** `symphainy_platform/realms/content/intent_services/`
3. **Read contracts:** See "Reference Materials" below
4. **Read old code:** See "Existing Implementations" below (for business logic only!)
5. **Implement:** 2 new services following NEW architecture
6. **Commit:** To feature branch `feature/intent-services-pilot`

---

## 📚 Reference Materials (Read These First)

**Location:** All paths relative to `symphainy_coexistence_fabric/`

1. **Contracts (What to build):**
   - `docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md`
   - `docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md`

2. **Base Class (How to build):**
   - `symphainy_platform/bases/intent_service_base.py`

3. **Architecture Rules:**
   - `.cursor/ARCHITECTURAL_REQUIREMENTS.md`

4. **Full Instructions:**
   - `.cursor/agent-tasks/INTENT_SERVICES_PILOT.md`
   - `.cursor/agent-tasks/AGENT_INSTRUCTIONS.md`
   - `.cursor/agent-tasks/CURSOR_WEB_AGENT_INSTRUCTIONS.md`

---

## 🔍 Existing Implementations (For Business Logic Reference)

⚠️ **WARNING:** These are OLD implementations. Use them ONLY to understand business logic. DO NOT copy the architecture!

**Location:** These are in the PARENT directory (`../symphainy_platform/`)

### For `ingest_file`:

**File:** `../symphainy_platform/realms/content/orchestrators/handlers/ingestion_handlers.py`

**Function:** `async def handle_ingest_file()` (starts around line 29)

**What to learn from it:**
- How file content (hex) is decoded
- How file_type and mime_type are determined
- How GCS path is constructed
- How artifact_id is generated
- How boundary_contract_id is created
- How artifacts are registered with PENDING state

**What NOT to copy:**
- ❌ Don't use `BaseContentHandler` (use `BaseIntentService` instead)
- ❌ Don't copy the class structure
- ❌ Don't copy direct infrastructure access (use Public Works)

### For `save_materialization`:

**File:** `../symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Function:** `async def _handle_save_materialization()` (starts around line 1418)

**What to learn from it:**
- How materialization is registered in the index
- How pending parsing journey is created
- How intent context stores ingest_profile/file_type
- How lifecycle state transitions (PENDING → READY)

**What NOT to copy:**
- ❌ Don't use orchestrator patterns (you're building intent services)
- ❌ Don't copy direct infrastructure access (use Public Works)
- ❌ Don't copy the handler structure

---

## 🏗️ What You're Building

### File 1: `ingest_file_service.py`

**Location:** `symphainy_platform/realms/content/intent_services/ingest_file_service.py`

**Class:** `IngestFileService(BaseIntentService)`

**Key Methods:**
- `async def execute(context, params) -> Dict[str, Any]`

**What it does:**
- Takes file upload (hex-encoded content)
- Stores file in GCS via IngestionAbstraction
- Creates artifact with PENDING lifecycle state
- Returns artifact_id, boundary_contract_id, file_id

### File 2: `save_materialization_service.py`

**Location:** `symphainy_platform/realms/content/intent_services/save_materialization_service.py`

**Class:** `SaveMaterializationService(BaseIntentService)`

**Key Methods:**
- `async def execute(context, params) -> Dict[str, Any]`

**What it does:**
- Takes boundary_contract_id and file_id
- Registers materialization in index
- Creates pending parsing journey (with ingest/file type in context)
- Transitions artifact lifecycle (PENDING → READY)
- Returns confirmation

### File 3: `__init__.py`

**Location:** `symphainy_platform/realms/content/intent_services/__init__.py`

**What it does:**
- Makes the directory a Python package
- Exports the service classes

---

## ✅ Success Criteria

Your implementation is successful if:

- [ ] Files exist in correct location
- [ ] Code extends `BaseIntentService` (not BaseContentHandler!)
- [ ] Implements contract specifications exactly
- [ ] Reports telemetry via Nurse SDK
- [ ] Registers artifacts via State Surface
- [ ] Uses Public Works abstractions only (no direct infrastructure)
- [ ] Code compiles without errors
- [ ] Follows architectural requirements

---

## 🆘 If You Get Stuck

1. **Read the contracts** - They tell you exactly what to build
2. **Read the base class** - It shows you the pattern to follow
3. **Look at old code** - For business logic understanding only
4. **Check architecture doc** - For patterns and constraints
5. **Ask questions** - Document what's unclear

---

## 📝 Next Steps After Implementation

1. Validate code compiles
2. Commit to feature branch: `feature/intent-services-pilot`
3. Push branch to origin
4. Document any questions or ambiguities

---

**Last Updated:** January 27, 2026  
**Status:** 🟢 **READY FOR AGENTS**
