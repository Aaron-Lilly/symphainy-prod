# Quick Start: Cursor Web Agent

**Status:** 🟢 **READY**

---

## ⚠️ CRITICAL: Working Directory

**Repository:** `symphainy_source_code`  
**Working Directory:** `symphainy_coexistence_fabric/` (within the repo)

**All paths are relative to:** `/symphainy_coexistence_fabric/`

---
### Agent Task Prompt

```
Implement 2 intent services for the SymphAIny Coexistence Fabric platform.

REPOSITORY & WORKING DIRECTORY:
- Repository: symphainy_source_code
- Working Directory: symphainy_coexistence_fabric/ (all paths relative to this folder)
- Create feature branch: feature/intent-services-pilot

WORKFLOW:
1. Navigate to symphainy_coexistence_fabric/ directory
2. Create feature branch: feature/intent-services-pilot
3. Read all reference materials (see list below)
4. Review existing implementations for business logic reference
5. Create directory structure: symphainy_platform/realms/content/intent_services/
6. Implement the intent services
7. Validate implementation compiles
8. Commit changes to the feature branch
9. Push the feature branch to origin

START HERE (Read First):
1. symphainy_coexistence_fabric/.cursor/agent-tasks/START_HERE.md - 🚀 Quick start guide

REFERENCE MATERIALS (Read in this order):
1. symphainy_coexistence_fabric/.cursor/agent-tasks/INTENT_SERVICES_PILOT.md - Full task specification
2. symphainy_coexistence_fabric/.cursor/agent-tasks/AGENT_INSTRUCTIONS.md - Step-by-step guidance
3. symphainy_coexistence_fabric/.cursor/agent-tasks/CURSOR_WEB_AGENT_INSTRUCTIONS.md - Web agent specifics
4. symphainy_coexistence_fabric/docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md - Contract for ingest_file
5. symphainy_coexistence_fabric/docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md - Contract for save_materialization
6. symphainy_coexistence_fabric/symphainy_platform/bases/intent_service_base.py - Base class to extend
7. symphainy_coexistence_fabric/.cursor/ARCHITECTURAL_REQUIREMENTS.md - Patterns and constraints

EXISTING IMPLEMENTATIONS (For Business Logic Reference):
⚠️ These are OLD implementations - use for business logic understanding only!
⚠️ DO NOT copy the architecture - follow NEW patterns (BaseIntentService, not BaseContentHandler)

1. symphainy_coexistence_fabric/.cursor/agent-tasks/REFERENCE_IMPLEMENTATIONS.md - 📖 Detailed guide to reference code
2. symphainy_source_code/symphainy_platform/realms/content/orchestrators/handlers/ingestion_handlers.py
   - Function: handle_ingest_file() (line ~29)
   - Shows: file ingestion, GCS storage, artifact creation
3. symphainy_source_code/symphainy_platform/realms/content/orchestrators/content_orchestrator.py
   - Function: _handle_save_materialization() (line ~1418)
   - Shows: materialization registration, pending journey creation

TARGET FILES TO CREATE:
1. symphainy_platform/realms/content/intent_services/ingest_file_service.py
2. symphainy_platform/realms/content/intent_services/save_materialization_service.py
3. symphainy_platform/realms/content/intent_services/__init__.py

REQUIREMENTS:
- Extend BaseIntentService
- Follow contract specifications exactly
- Report telemetry via Nurse SDK
- Register artifacts via State Surface
- Use Public Works abstractions only
- Follow .cursor/ARCHITECTURAL_REQUIREMENTS.md

VALIDATION:
- Code compiles without errors
- Files created in correct location
- Follows BaseIntentService pattern
- Implements contract specifications
- Reports telemetry
- Registers artifacts

COMMIT MESSAGE:
feat: Implement ingest_file and save_materialization intent services

- Created IngestFileService extending BaseIntentService
- Created SaveMaterializationService extending BaseIntentService
- Implemented contract specifications exactly
- Added telemetry reporting via Nurse SDK
- Added artifact registration via State Surface
- Followed architectural requirements
```

---

## What the Agent Should Do

1. **Read all reference materials** (contracts, base classes, requirements)
2. **Create directory structure** (`symphainy_platform/realms/content/intent_services/`)
3. **Implement both intent services** following contracts
4. **Validate implementation** against success criteria
5. **Commit changes** to a feature branch

---

## Success Criteria

- ✅ Files created in correct location
- ✅ Code extends BaseIntentService
- ✅ Implements contract specifications
- ✅ Reports telemetry
- ✅ Registers artifacts
- ✅ Follows architectural requirements
- ✅ Code compiles without errors

---

**Ready to go!**
