# Session Handoff: Integration Testing - Import Error Fix

**Date:** January 17, 2026  
**Status:** 🔴 **BLOCKED** - Import error preventing Experience service startup  
**Last Action:** Fixed path resolution issues, added plotly/numpy dependencies, rebuilt container

---

## 🎯 Current Objective

Complete integration testing of authentication and WebSocket endpoints. The Experience service is failing to start due to an import error.

---

## ✅ What's Been Completed

### 1. Plotly Dependency Fix ✅
- **File:** `requirements.txt`
- **Changes:**
  - Added `plotly>=5.0.0`
  - Added `numpy>=1.24.0` (required by plotly)
- **File:** `symphainy_platform/foundations/public_works/adapters/visual_generation_adapter.py`
- **Changes:** Removed optional handling - plotly is now a required dependency

### 2. Path Resolution Fixes ✅
Fixed hardcoded `.parents[N]` in **20+ files** to use dynamic project root detection:

**Experience Service Files:**
- `symphainy_platform/civic_systems/experience/api/guide_agent.py`
- `symphainy_platform/civic_systems/experience/services/guide_agent_service.py`
- All admin dashboard files (7 files)

**Agentic Files:**
- `symphainy_platform/civic_systems/agentic/agent_base.py`
- `symphainy_platform/civic_systems/agentic/agents/stateless_agent.py`
- `symphainy_platform/civic_systems/agentic/agents/guide_agent.py`
- `symphainy_platform/civic_systems/agentic/agents/workflow_optimization_agent.py`
- `symphainy_platform/civic_systems/agentic/agents/proposal_agent.py`
- `symphainy_platform/civic_systems/agentic/agents/eda_analysis_agent.py`
- `symphainy_platform/civic_systems/agentic/agents/insights_eda_agent.py`
- `symphainy_platform/civic_systems/agentic/agents/roadmap_proposal_agent.py`
- `symphainy_platform/civic_systems/agentic/agents/content_liaison_agent.py`
- `symphainy_platform/civic_systems/agentic/agents/workflow_optimization_specialist.py`
- `symphainy_platform/civic_systems/agentic/agents/conversational_agent.py`

**Pattern Applied:**
```python
# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
```

### 3. Authentication Implementation ✅
- **File:** `symphainy_platform/civic_systems/experience/api/auth.py`
- **Endpoints:**
  - `/api/auth/login` - User authentication
  - `/api/auth/register` - User registration
- **Registered in:** `symphainy_platform/civic_systems/experience/experience_service.py`

### 4. WebSocket Implementation ✅
- **File:** `symphainy_platform/civic_systems/experience/api/runtime_agent_websocket.py`
- **Endpoint:** `/api/runtime/agent` (Experience Plane owned)
- **Architecture:** Hybrid model - Experience Plane routes, Runtime executes
- **Documentation:** `docs/ARCHITECTURE_WEBSOCKET_AGENT_ENDPOINT.md`

### 5. Integration Test Script ✅
- **File:** `tests/integration/test_auth_and_websocket_inline.py`
- **Tests:**
  - Health checks (Experience Plane + Runtime)
  - Authentication registration
  - Authentication login
  - WebSocket agent endpoint

---

## 🔴 Current Issue

### Import Error
```
ImportError: cannot import name 'ConversationalAgentBase' from 'symphainy_platform.civic_systems.agentic.agents.conversational_agent'
```

**Location:** `symphainy_platform/civic_systems/agentic/agents/__init__.py` line 6

**Error Context:**
- The class `ConversationalAgentBase` **is defined** in `conversational_agent.py` (line 24)
- The file has correct path resolution code
- The import fails during module load

**Possible Causes:**
1. File not saved after path resolution fix (shows as "unsaved" in some grep results)
2. Circular import issue
3. Import-time error in a dependency (`AgentBase` or `ExecutionContext`)
4. Syntax error preventing class definition

---

## 📋 Files to Check

### Primary File
- `symphainy_platform/civic_systems/agentic/agents/conversational_agent.py`
  - **Line 24:** `class ConversationalAgentBase(AgentBase):`
  - **Line 20:** `from ..agent_base import AgentBase`
  - **Line 21:** `from symphainy_platform.runtime.execution_context import ExecutionContext`

### Import Chain
- `symphainy_platform/civic_systems/agentic/agents/__init__.py` (line 6)
- `symphainy_platform/civic_systems/agentic/agent_base.py`
- `symphainy_platform/runtime/execution_context.py`

---

## 🔧 Debugging Steps

### Step 1: Verify File is Saved
```bash
cd /home/founders/demoversion/symphainy_source_code
# Check if file exists and has correct content
grep -n "class ConversationalAgentBase" symphainy_platform/civic_systems/agentic/agents/conversational_agent.py
```

### Step 2: Check for Syntax Errors
```bash
python3 -m py_compile symphainy_platform/civic_systems/agentic/agents/conversational_agent.py
```

### Step 3: Test Import Directly
```bash
cd /home/founders/demoversion/symphainy_source_code
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from symphainy_platform.civic_systems.agentic.agents.conversational_agent import ConversationalAgentBase
    print('✅ Import successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()
"
```

### Step 4: Check Container Logs
```bash
docker-compose logs experience --tail 100 | grep -A 20 "ImportError"
```

### Step 5: Rebuild and Test
```bash
cd /home/founders/demoversion/symphainy_source_code
docker-compose build experience
docker-compose up -d experience
sleep 40
curl http://localhost:8001/health
```

---

## 🎯 Next Steps After Fix

Once the import error is resolved:

1. **Verify Service Health**
   ```bash
   curl http://localhost:8001/health
   curl http://localhost:8000/health
   ```

2. **Run Integration Tests**
   ```bash
   cd /home/founders/demoversion/symphainy_source_code
   python3 tests/integration/test_auth_and_websocket_inline.py
   ```

3. **Expected Test Results:**
   - ✅ Health checks: PASSED
   - ✅ Auth register: PASSED (may fail if user exists - OK)
   - ✅ Auth login: PASSED
   - ✅ WebSocket: PASSED (may timeout if agent processing - OK for MVP)

---

## 📁 Key Files Reference

### Implementation Files
- `symphainy_platform/civic_systems/experience/api/auth.py` - Auth endpoints
- `symphainy_platform/civic_systems/experience/api/runtime_agent_websocket.py` - WebSocket endpoint
- `symphainy_platform/civic_systems/experience/experience_service.py` - Service registration

### Test Files
- `tests/integration/test_auth_and_websocket_inline.py` - Integration tests
- `scripts/rebuild_and_test.sh` - Rebuild and test script

### Documentation
- `docs/ARCHITECTURE_WEBSOCKET_AGENT_ENDPOINT.md` - WebSocket architecture
- `docs/execution/integration_testing_ready_manual_steps.md` - Manual steps guide
- `docs/execution/backend_review_and_integration_readiness.md` - Backend review

### Configuration
- `requirements.txt` - Dependencies (plotly, numpy added)
- `docker-compose.yml` - Service orchestration

---

## 🔍 Troubleshooting Guide

### If Import Error Persists

1. **Check for Circular Imports:**
   ```bash
   # Check if agent_base imports conversational_agent
   grep -r "conversational_agent" symphainy_platform/civic_systems/agentic/agent_base.py
   ```

2. **Check ExecutionContext Import:**
   ```bash
   # Verify ExecutionContext exists
   ls -la symphainy_platform/runtime/execution_context.py
   ```

3. **Check AgentBase Import:**
   ```bash
   # Verify agent_base can be imported
   python3 -c "from symphainy_platform.civic_systems.agentic.agent_base import AgentBase; print('OK')"
   ```

4. **Try Lazy Import:**
   If circular import is the issue, consider making the import in `__init__.py` lazy or conditional.

### If Service Still Fails

1. **Check All Logs:**
   ```bash
   docker-compose logs experience --tail 200
   ```

2. **Check Runtime Service:**
   ```bash
   docker-compose logs runtime --tail 50
   ```

3. **Verify Dependencies:**
   ```bash
   docker-compose exec experience pip list | grep -E "plotly|numpy"
   ```

---

## 📝 Notes

- **Disk Space:** User freed up 57.3GB - should be sufficient for rebuilds
- **Shell Issues:** Previous session had shell errors - new agent window should resolve
- **File Status:** Some files showed as "unsaved" in grep - verify all changes are saved
- **Docker:** Container was rebuilt successfully but service fails on startup due to import error

---

## 🚀 Quick Start Commands

```bash
# Navigate to project
cd /home/founders/demoversion/symphainy_source_code

# Check current status
docker-compose ps
docker-compose logs experience --tail 30

# Rebuild (after fixing import error)
docker-compose build experience
docker-compose up -d experience

# Wait and check health
sleep 40
curl http://localhost:8001/health

# Run tests
python3 tests/integration/test_auth_and_websocket_inline.py
```

---

**Ready for:** Debug import error → Fix → Rebuild → Integration testing
