# Quick Start: Cursor Web Agent

**Status:** 🟢 **READY**

---

## For Cursor Web Agent

### Agent Task Prompt

Copy this prompt for your Cursor Web Agent:

```
Implement 2 intent services for the SymphAIny Coexistence Fabric platform.

Task Details:
- Read .cursor/agent-tasks/INTENT_SERVICES_PILOT.md for full specification
- Read .cursor/agent-tasks/AGENT_INSTRUCTIONS.md for step-by-step guidance
- Read .cursor/agent-tasks/CURSOR_WEB_AGENT_INSTRUCTIONS.md for web agent specifics

Target Files:
1. symphainy_platform/realms/content/intent_services/ingest_file_service.py
2. symphainy_platform/realms/content/intent_services/save_materialization_service.py

Contracts:
- docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md
- docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md

Base Class:
- symphainy_platform/bases/intent_service_base.py

Requirements:
- Extend BaseIntentService
- Follow contract specifications exactly
- Report telemetry via Nurse SDK
- Register artifacts via State Surface
- Use Public Works abstractions only
- Follow .cursor/ARCHITECTURAL_REQUIREMENTS.md

Create the files, implement the services, and ensure they compile without errors.
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
