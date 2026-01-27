# Agent Pilot Summary

**Date:** January 27, 2026  
**Status:** 🟢 **READY FOR AGENT**

---

## What We've Set Up

### 1. ✅ Intent Contracts (2 completed)
- `docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md`
- `docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md`

### 2. ✅ Base Classes
- `symphainy_platform/bases/intent_service_base.py` - BaseIntentService
- `symphainy_platform/bases/orchestrator_base.py` - BaseOrchestrator

### 3. ✅ Architectural Requirements
- `.cursor/ARCHITECTURAL_REQUIREMENTS.md` - All patterns and constraints
- `docs/ARCHITECTURE_NORTH_STAR.md` - System architecture overview

### 4. ✅ Agent Task Instructions
- `.cursor/agent-tasks/INTENT_SERVICES_PILOT.md` - Detailed task specification
- `.cursor/agent-tasks/AGENT_INSTRUCTIONS.md` - Step-by-step agent guide

### 5. ✅ Template Generation Script
- `scripts/generate_intent_contracts.py` - Generate templates from journey contracts

---

## Agent Task

**Implement 2 intent services:**
1. `ingest_file` Intent Service
2. `save_materialization` Intent Service

**Location:** `symphainy_platform/realms/content/intent_services/`

**Pattern:** Extend `BaseIntentService`, follow contracts exactly

---

## How to Turn Agent Loose

### Option 1: Direct Agent Assignment
Point agent to:
- Task: `.cursor/agent-tasks/INTENT_SERVICES_PILOT.md`
- Instructions: `.cursor/agent-tasks/AGENT_INSTRUCTIONS.md`
- Contracts: `docs/intent_contracts/journey_content_file_upload_materialization/`

### Option 2: Cursor Web Agents
If using Cursor Web Agents:
1. Ensure GitHub access configured (see `.cursor/GITHUB_SETUP.md`)
2. Agent reads task from `.cursor/agent-tasks/`
3. Agent implements following instructions
4. Agent commits changes to branch

### Option 3: Manual Agent Instructions
Provide agent with:
```
Read: .cursor/agent-tasks/INTENT_SERVICES_PILOT.md
Read: .cursor/agent-tasks/AGENT_INSTRUCTIONS.md
Read: docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md
Read: docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md
Read: symphainy_platform/bases/intent_service_base.py
Read: .cursor/ARCHITECTURAL_REQUIREMENTS.md

Implement:
- symphainy_platform/realms/content/intent_services/ingest_file_service.py
- symphainy_platform/realms/content/intent_services/save_materialization_service.py
```

---

## What We'll Learn

After agent completes:
1. ✅ Are contracts clear enough?
2. ✅ Do base classes provide needed functionality?
3. ✅ Are architectural requirements clear?
4. ✅ What's confusing or missing?
5. ✅ What would make this easier to scale?

---

## Next Steps After Pilot

1. **Review agent output** - Check implementation quality
2. **Identify gaps** - What was missing or unclear?
3. **Adjust contracts** - Refine based on learnings
4. **Generate remaining templates** - Run `scripts/generate_intent_contracts.py`
5. **Final review** - Review all ~87 contracts against implementations
6. **Scale up** - Turn agents loose on all contracts

---

**Status:** 🟢 **READY FOR AGENT**
