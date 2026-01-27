# Quick Start: Turn Agent Loose on Intent Services Pilot

**Status:** 🟢 **READY**

---

## Simple Instructions for Agent

Copy and paste this to your agent:

```
I need you to implement 2 intent services for the SymphAIny Coexistence Fabric platform.

Please:
1. Read .cursor/agent-tasks/INTENT_SERVICES_PILOT.md for the full task specification
2. Read .cursor/agent-tasks/AGENT_INSTRUCTIONS.md for step-by-step guidance
3. Read the intent contracts:
   - docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md
   - docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md
4. Read symphainy_platform/bases/intent_service_base.py to understand the base class
5. Read .cursor/ARCHITECTURAL_REQUIREMENTS.md to understand patterns and constraints

Then implement:
- symphainy_platform/realms/content/intent_services/ingest_file_service.py
- symphainy_platform/realms/content/intent_services/save_materialization_service.py

Both should extend BaseIntentService and follow the contract specifications exactly.
```

---

## What the Agent Should Do

1. **Read all reference materials** (contracts, base classes, requirements)
2. **Create the intent service files** in the correct location
3. **Extend BaseIntentService** and implement `execute()` method
4. **Follow contract specifications** exactly (parameters, returns, artifacts)
5. **Report telemetry** via Nurse SDK
6. **Register artifacts** via State Surface
7. **Use Public Works abstractions** only (no direct infrastructure access)

---

## Success Criteria

The agent's work is successful if:
- ✅ Files are created in correct location
- ✅ Code extends BaseIntentService
- ✅ Implements contract specifications
- ✅ Reports telemetry
- ✅ Registers artifacts
- ✅ Follows architectural requirements
- ✅ Code compiles without errors

---

## After Agent Completes

1. Review the implementation
2. Check contract compliance
3. Identify any gaps or confusion
4. Adjust contracts/instructions as needed
5. Proceed with template generation and scaling

---

**Ready to go!**
