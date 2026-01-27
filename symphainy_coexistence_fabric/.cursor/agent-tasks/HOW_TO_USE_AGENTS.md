# How to Use Agents: Step-by-Step Guide

**Date:** January 27, 2026

---

## Option 1: Use Cursor AI Chat (Recommended for Now)

Since you're in Cursor IDE, you can use the regular Cursor AI chat to act as the agent:

### Step 1: Open Cursor Chat
- Press `Cmd+L` (Mac) or `Ctrl+L` (Windows/Linux) to open Cursor chat
- Or click the chat icon in the sidebar

### Step 2: Paste the Agent Instructions
Copy and paste this into the chat:

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

### Step 3: Let the AI Work
The AI will:
1. Read all the reference materials
2. Understand the contracts and requirements
3. Implement the intent services
4. Create the files in the correct location

---

## Option 2: Cursor Web Agents (If Available)

Cursor Web Agents are a feature that allows agents to work autonomously on tasks. Here's how to access them:

### Check if Web Agents are Available
1. Look for "Agents" or "Web Agents" in Cursor's menu
2. Check Cursor settings for agent features
3. Look for agent-related commands in Command Palette (`Cmd+Shift+P`)

### If Web Agents are Available:
1. Open the Agents panel
2. Create a new agent task
3. Point it to `.cursor/agent-tasks/INTENT_SERVICES_PILOT.md`
4. Let it run

### If Web Agents are NOT Available:
**Use Option 1** (Cursor AI Chat) - it works the same way for this task.

---

## Option 3: Manual Implementation

If you prefer to implement manually or want to guide the AI step-by-step:

### Step 1: Create Directory Structure
```bash
mkdir -p symphainy_platform/realms/content/intent_services
touch symphainy_platform/realms/content/intent_services/__init__.py
```

### Step 2: Ask AI to Implement Each Service
Ask the AI in chat:
- "Implement ingest_file_service.py following the contract"
- "Implement save_materialization_service.py following the contract"

---

## What to Expect

The AI should:
1. ✅ Read all reference materials
2. ✅ Create the intent service files
3. ✅ Extend BaseIntentService
4. ✅ Implement contract specifications
5. ✅ Include telemetry reporting
6. ✅ Include artifact registration
7. ✅ Follow architectural requirements

---

## Troubleshooting

### "I don't see Agents option"
- Use Cursor AI Chat (Option 1) - it works the same way
- The chat AI can read files and implement code

### "Agent doesn't understand the task"
- Make sure all reference files exist
- Point agent to specific files if needed
- Break the task into smaller steps

### "Agent creates wrong structure"
- Review the base class pattern
- Check the contract specifications
- Provide feedback and ask for corrections

---

## Quick Test

To verify the setup works, try this in Cursor chat:

```
Can you read .cursor/agent-tasks/INTENT_SERVICES_PILOT.md and tell me what the task is?
```

If the AI can read and understand the file, you're ready to proceed with the full implementation.

---

**Recommended:** Start with Option 1 (Cursor AI Chat) - it's the simplest and works immediately.
