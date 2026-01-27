# Agent Implementation Validation Checklist

**Date:** January 27, 2026  
**Status:** ⏳ **AWAITING VALIDATION**

---

## How to Check if Agent Worked

### Step 1: Check for Created Files

```bash
# Check if directory exists
ls -la symphainy_platform/realms/content/intent_services/

# Check for specific files
ls -la symphainy_platform/realms/content/intent_services/ingest_file_service.py
ls -la symphainy_platform/realms/content/intent_services/save_materialization_service.py
ls -la symphainy_platform/realms/content/intent_services/__init__.py
```

**Expected:** All 3 files should exist

---

### Step 2: Check Git Status

```bash
# Check for uncommitted changes
git status

# Check for feature branch
git branch -a | grep intent

# Check recent commits
git log --oneline -5
```

**Expected:** 
- Either uncommitted changes OR
- A feature branch with commits OR
- New commits on main

---

### Step 3: Review Implementation

**Check ingest_file_service.py:**
- [ ] Extends `BaseIntentService`
- [ ] Implements `execute()` method
- [ ] Validates parameters per contract
- [ ] Uses Public Works abstractions (IngestionAbstraction)
- [ ] Registers artifact in State Surface
- [ ] Reports telemetry via Nurse SDK
- [ ] Returns structured artifact per contract

**Check save_materialization_service.py:**
- [ ] Extends `BaseIntentService`
- [ ] Implements `execute()` method
- [ ] Validates parameters per contract
- [ ] Transitions artifact lifecycle (PENDING → READY)
- [ ] Creates pending parsing journey
- [ ] Reports telemetry via Nurse SDK
- [ ] Returns structured artifact per contract

---

### Step 4: Validate Code Quality

```bash
# Check for syntax errors
python3 -m py_compile symphainy_platform/realms/content/intent_services/ingest_file_service.py
python3 -m py_compile symphainy_platform/realms/content/intent_services/save_materialization_service.py

# Check imports
python3 -c "import sys; sys.path.insert(0, '.'); from symphainy_platform.realms.content.intent_services.ingest_file_service import IngestFileService"
```

**Expected:** No syntax errors, imports work

---

### Step 5: Check Contract Compliance

**For each service, verify:**
- [ ] Parameters match contract Section 2
- [ ] Returns match contract Section 3
- [ ] Artifact registration matches contract Section 4
- [ ] Idempotency matches contract Section 5
- [ ] Error handling matches contract Section 8

---

## If Files Don't Exist

### Possible Reasons:
1. **Agent hasn't started yet** - Check agent status/queue
2. **Agent encountered error** - Check agent logs/error messages
3. **Agent created files elsewhere** - Search entire repository
4. **Agent needs more time** - Wait and check again

### What to Do:
1. Check agent status/logs
2. Ask agent: "Did you create the intent service files?"
3. Search for any new Python files created
4. Check if agent created a PR or branch

---

## Success Indicators

✅ **Success if:**
- Files exist in correct location
- Code extends BaseIntentService
- Implements contract specifications
- Compiles without errors
- Follows architectural requirements

❌ **Needs work if:**
- Files missing
- Syntax errors
- Doesn't extend BaseIntentService
- Missing telemetry/artifact registration
- Violates architectural requirements

---

**Last Updated:** January 27, 2026
