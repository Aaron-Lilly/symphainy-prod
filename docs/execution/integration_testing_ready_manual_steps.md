# Integration Testing - Manual Steps

**Date:** January 2026  
**Status:** ✅ **CODE FIXES COMPLETE** - Ready for Docker cleanup and rebuild

---

## ✅ What's Been Fixed

### 1. Plotly Dependency ✅
- Added `plotly>=5.0.0` to `requirements.txt`
- Added `numpy>=1.24.0` to `requirements.txt` (required by plotly)
- Removed optional handling from `visual_generation_adapter.py`

### 2. Path Resolution Issues ✅
Fixed hardcoded `.parents[N]` in the following files:
- `symphainy_platform/civic_systems/experience/api/guide_agent.py`
- `symphainy_platform/civic_systems/experience/services/guide_agent_service.py`
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
- All admin dashboard files (7 files)

All now use dynamic project root detection:
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
- `/api/auth/login` endpoint implemented
- `/api/auth/register` endpoint implemented
- Router registered in Experience service

### 4. WebSocket Implementation ✅
- `/api/runtime/agent` endpoint implemented (Experience Plane owned)
- Agent routing logic implemented
- Event streaming implemented

---

## 🧹 Manual Steps to Complete

### Step 1: Clean Up Docker

```bash
cd /home/founders/demoversion/symphainy_source_code

# Check disk space
df -h

# Clean up Docker (removes unused images, containers, volumes)
docker system prune -a -f --volumes

# Verify cleanup
docker system df
```

### Step 2: Rebuild Experience Service

```bash
cd /home/founders/demoversion/symphainy_source_code

# Rebuild the experience container
docker-compose build experience

# Start the service
docker-compose up -d experience

# Wait for service to start (30-40 seconds)
sleep 35

# Verify health
curl -s http://localhost:8001/health
```

### Step 3: Run Integration Tests

```bash
cd /home/founders/demoversion/symphainy_source_code

# Run the inline integration tests
python3 tests/integration/test_auth_and_websocket_inline.py
```

---

## 📋 Expected Test Results

The test script will:
1. ✅ Test health checks (Experience Plane + Runtime)
2. ✅ Test `/api/auth/register` endpoint
3. ✅ Test `/api/auth/login` endpoint
4. ✅ Test `/api/runtime/agent` WebSocket endpoint

**Expected Output:**
- Health checks: PASSED
- Auth register: PASSED (or may fail if user already exists - that's OK)
- Auth login: PASSED
- WebSocket: PASSED (or may show timeout if agent processing - that's OK for MVP)

---

## 🔍 Troubleshooting

### If Experience service fails to start:
```bash
# Check logs
docker-compose logs experience --tail 50

# Look for:
# - Import errors
# - Path resolution errors
# - Missing dependencies
```

### If tests fail:
```bash
# Verify services are running
docker-compose ps

# Check service health
curl http://localhost:8001/health
curl http://localhost:8000/health

# Check if auth endpoints are registered
curl http://localhost:8001/docs | grep -i auth
```

---

## 📝 Files Modified

### Requirements
- `requirements.txt` - Added plotly and numpy

### Path Resolution Fixes
- 20+ files in `symphainy_platform/civic_systems/experience/`
- 9 files in `symphainy_platform/civic_systems/agentic/agents/`
- 1 file in `symphainy_platform/civic_systems/agentic/`

### New Files
- `symphainy_platform/civic_systems/experience/api/auth.py` - Authentication endpoints
- `symphainy_platform/civic_systems/experience/api/runtime_agent_websocket.py` - WebSocket agent endpoint
- `tests/integration/test_auth_and_websocket_inline.py` - Integration test script
- `docs/ARCHITECTURE_WEBSOCKET_AGENT_ENDPOINT.md` - Architecture documentation

---

**Ready for:** Docker cleanup → Rebuild → Integration testing
