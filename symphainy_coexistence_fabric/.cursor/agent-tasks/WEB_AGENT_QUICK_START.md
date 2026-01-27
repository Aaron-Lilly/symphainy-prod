# Quick Start: Cursor Web Agent

**Status:** 🟢 **READY**

---

## For Cursor Web Agent

### Agent Task Prompt

Copy this prompt for your Cursor Web Agent:

```
Implement 2 intent services for the SymphAIny Coexistence Fabric platform.

WORKFLOW:
1. Clone/pull the repository (if not already available)
2. Create a feature branch: feature/intent-services-pilot
3. Read all reference materials (see list below)
4. Implement the intent services
5. Validate implementation compiles
6. Commit changes to the feature branch
7. Push the feature branch to origin

REFERENCE MATERIALS (Read in this order):
1. .cursor/agent-tasks/INTENT_SERVICES_PILOT.md - Full task specification
2. .cursor/agent-tasks/AGENT_INSTRUCTIONS.md - Step-by-step guidance
3. .cursor/agent-tasks/CURSOR_WEB_AGENT_INSTRUCTIONS.md - Web agent specifics
4. docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md - Contract for ingest_file
5. docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md - Contract for save_materialization
6. symphainy_platform/bases/intent_service_base.py - Base class to extend
7. .cursor/ARCHITECTURAL_REQUIREMENTS.md - Patterns and constraints

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
