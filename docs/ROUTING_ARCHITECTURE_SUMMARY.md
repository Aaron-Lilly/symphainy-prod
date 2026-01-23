# Routing Architecture Summary

**Date:** January 2026  
**Status:** ✅ **UNDERSTOOD & IMPLEMENTED**

---

## Executive Summary

**The platform uses a clean routing architecture to keep main.py minimal (< 100 lines).**

**Pattern:**
- `main.py` - Minimal entry point, creates FastAPI app
- `experience_service.py` - Collects and registers all routers via `create_app()`
- Individual router files - Each API module exports a router

---

## Architecture Pattern

### 1. Main Entry Point (`main.py`)
- **Purpose:** Minimal entry point (< 100 lines)
- **Responsibilities:**
  - Create FastAPI app
  - Initialize telemetry
  - Start uvicorn server
- **Does NOT:** Register routers (delegated to services)

### 2. Experience Service (`experience_service.py`)
- **Purpose:** Collects and registers all routers
- **Pattern:** `create_app()` function that:
  - Creates FastAPI app
  - Adds middleware (auth, CORS)
  - Imports routers from various modules
  - Registers all routers via `app.include_router()`
  - Returns configured app

**Current Routers Registered:**
```python
# Core Experience routers
app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(intents_router)
app.include_router(websocket_router)
app.include_router(guide_agent_router)
app.include_router(runtime_agent_websocket_router)

# Metrics API (NEW)
app.include_router(metrics_router)

# Admin Dashboard routers
app.include_router(control_room_router)
app.include_router(developer_view_router)
app.include_router(business_user_view_router)
```

### 3. Individual Router Files
- **Pattern:** Each API module exports a router
- **Location:** `symphainy_platform/civic_systems/experience/api/`
- **Example:**
  ```python
  # guide_agent.py
  router = APIRouter(prefix="/api/v1/guide-agent", tags=["guide-agent"])
  
  @router.post("/chat")
  async def chat(...):
      ...
  ```

### 4. Admin Dashboard Routers
- **Pattern:** Collected in `admin_dashboard/api/__init__.py`
- **Exports:** `control_room_router`, `developer_view_router`, `business_user_view_router`
- **Registered:** In `experience_service.py`

---

## Metrics API Integration

**File:** `symphainy_platform/runtime/metrics_api.py`

**Router:** `router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])`

**Registered In:** `experience_service.py` (line 83)

**Endpoints:**
- `GET /api/v1/metrics/agents`
- `GET /api/v1/metrics/orchestrators`
- `GET /api/v1/metrics/platform`

---

## Benefits of This Pattern

1. **Clean Separation:** Main.py stays minimal
2. **Organized:** Routers grouped by domain (experience, admin, metrics)
3. **Maintainable:** Easy to add new routers
4. **Testable:** Each router can be tested independently
5. **Scalable:** Can split into multiple services if needed

---

## Adding New Routers

**Pattern to Follow:**

1. **Create router file:**
   ```python
   # new_api.py
   router = APIRouter(prefix="/api/v1/new-api", tags=["new-api"])
   
   @router.get("/endpoint")
   async def endpoint():
       ...
   ```

2. **Import in experience_service.py:**
   ```python
   from .api.new_api import router as new_api_router
   ```

3. **Register in create_app():**
   ```python
   app.include_router(new_api_router)
   ```

---

**Status:** Pattern understood, metrics API router registered
