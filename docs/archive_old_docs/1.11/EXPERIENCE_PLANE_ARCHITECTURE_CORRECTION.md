# Experience Plane Architecture Correction

**Date:** January 2026  
**Status:** 🔍 **ROOT CAUSE IDENTIFIED - CORRECTION NEEDED**  
**Critical:** This is the same anti-pattern that caused original websocket/router issues

---

## 🎯 The Problem

We're **mounting Experience Plane routers on Runtime Plane's FastAPI app**, which:
1. **Mixes delivery concerns with execution concerns**
2. **Tightly couples Experience to Runtime**
3. **Repeats the same anti-pattern** that caused original router issues
4. **Violates the architectural vision** from rebuild_implementation_plan_v2.md

---

## 📋 What The Plan Says

From `rebuild_implementation_plan_v2.md` (Phase 6 - Experience Plane):

> **Experience is delivery, not logic.**
> 
> **Interaction Model:**
> - Experience **submits intents** to Runtime
> - Experience **subscribes to execution events**
> - Experience **never invokes domain logic**

### Key Principle:

> **Experience reflects runtime state — it never invents it.**

---

## ❌ Current Anti-Pattern

### What We're Doing (WRONG):

```python
# In main.py lifespan
runtime_app = create_runtime_app(...)  # Runtime Plane app

# ❌ ANTI-PATTERN: Mounting Experience on Runtime
content_router = create_content_router(runtime_service)
runtime_app.include_router(content_router)  # Experience concerns in Runtime

app.mount("/api", runtime_app)  # Mixed concerns
```

### Why This Is Wrong:

1. **Runtime Plane = Execution Authority**
   - Should own sessions, intents, state, sagas
   - Should NOT know about delivery mechanisms
   - Should provide HTTP API for intents

2. **Experience Plane = Delivery Layer**
   - Should own REST, WebSocket, UI surfaces
   - Should be **swappable** (REST, WebSocket, future adapters)
   - Should call Runtime via HTTP, not share FastAPI apps

3. **Tight Coupling**
   - Experience can't be swapped without touching Runtime
   - Router mounting complexity (the original problem)
   - Mixed concerns (delivery + execution)

---

## ✅ Correct Architectural Pattern

### The Vision:

```
┌─────────────────────────────────────────────────────────┐
│ Runtime Plane (Execution Authority)                      │
│                                                          │
│ FastAPI App: /api                                       │
│ - /session/create                                       │
│ - /session/{id}                                         │
│ - /intent/submit  ← Experience calls this               │
│ - /execution/{id}/status                                │
│                                                          │
│ NO delivery concerns                                    │
│ NO Experience routers                                   │
└─────────────────────────────────────────────────────────┘
                          ↑
                          │ HTTP POST /api/intent/submit
                          │
┌─────────────────────────────────────────────────────────┐
│ Experience Plane (Delivery Layer)                        │
│                                                          │
│ FastAPI App: /v1/content                               │
│ - /v1/content/upload                                    │
│ - /v1/content/data-mash/create                          │
│                                                          │
│ Submits intents to Runtime via HTTP                     │
│ Subscribes to execution events (WebSocket/polling)       │
│                                                          │
│ Swappable (REST, WebSocket, future adapters)            │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 Root Cause Analysis

### Why This Happened:

1. **Convenience over architecture** - Easier to mount router than create separate service
2. **Missing separation** - Didn't recognize Experience should be separate
3. **Repeating old patterns** - Same anti-pattern that caused original issues

### The Original Problem:

The original websocket/router issues were caused by:
- Mixing concerns (delivery + execution)
- Tight coupling between layers
- Router mounting complexity
- Shared FastAPI apps

**We're repeating the same mistake.**

---

## ✅ Correct Solution

### Option 1: Test Direct Intent Submission (Immediate)

For testing, use Runtime's `/api/intent/submit` directly:

```bash
# Create session
SESSION_ID=$(curl -s -X POST http://localhost:8000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "test_tenant", "user_id": "test_user"}' \
  | jq -r '.session.session_id')

# Submit upload intent directly to Runtime
curl -X POST http://localhost:8000/api/intent/submit \
  -H "Content-Type: application/json" \
  -d "{
    \"intent_type\": \"content.upload\",
    \"realm\": \"content\",
    \"session_id\": \"$SESSION_ID\",
    \"tenant_id\": \"test_tenant\",
    \"payload\": {
      \"file_data\": \"$(base64 -w 0 /tmp/test_file.csv)\",
      \"filename\": \"test_file.csv\"
    }
  }"
```

### Option 2: Separate Experience Service (Recommended)

```python
# symphainy_platform/experience/experience_service.py

import httpx
from fastapi import FastAPI, APIRouter, UploadFile, File, Form
from typing import Optional

class ExperienceService:
    """
    Experience Plane Service - Delivery Layer
    
    WHAT: I deliver platform capabilities to users
    HOW: I submit intents to Runtime and subscribe to events
    """
    
    def __init__(self, runtime_url: str = "http://runtime:8000"):
        self.runtime_url = runtime_url
        self.app = FastAPI(title="Symphainy Experience Plane")
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Experience Plane routes."""
        router = APIRouter(prefix="/v1/content", tags=["content"])
        
        @router.post("/upload")
        async def upload_file(
            file: UploadFile = File(...),
            tenant_id: str = Form(...),
            session_id: str = Form(...)
        ):
            """Upload file by submitting intent to Runtime."""
            # Read file
            file_data = await file.read()
            file_data_b64 = base64.b64encode(file_data).decode('utf-8')
            
            # Submit intent to Runtime
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.runtime_url}/api/intent/submit",
                    json={
                        "intent_type": "content.upload",
                        "realm": "content",
                        "session_id": session_id,
                        "tenant_id": tenant_id,
                        "payload": {
                            "file_data": file_data_b64,
                            "filename": file.filename
                        }
                    }
                )
                return response.json()
        
        self.app.include_router(router)
    
    def get_app(self) -> FastAPI:
        """Get Experience Plane FastAPI app."""
        return self.app
```

### Option 3: Experience as Separate Container (Best for Production)

```yaml
# docker-compose.yml
services:
  runtime:
    # Runtime Plane - execution only
    # Endpoints: /api/session, /api/intent, /api/execution
  
  experience:
    # Experience Plane - delivery only
    # Endpoints: /v1/content/upload, /v1/data-mash/create
    # Calls runtime via HTTP
    environment:
      - RUNTIME_URL=http://runtime:8000
```

---

## 📊 Architecture Comparison

### ❌ Current (Anti-Pattern):

```
main.py
  └─ Runtime App (FastAPI)
      ├─ Runtime endpoints (/session, /intent)
      └─ Experience routers (/v1/content)  ❌ MIXED CONCERNS
          └─ Calls runtime_service directly  ❌ TIGHT COUPLING
```

### ✅ Correct (Architecturally Sound):

```
Runtime Service (main.py)
  └─ Runtime App (FastAPI)
      └─ Runtime endpoints only (/session, /intent)
          └─ Pure execution authority

Experience Service (separate)
  └─ Experience App (FastAPI)
      └─ Experience endpoints (/v1/content)
          └─ Submits intents to Runtime via HTTP
          └─ Subscribes to execution events
          └─ Swappable delivery layer
```

---

## 🎯 Key Principles

1. **Runtime Plane = Execution Authority**
   - Owns sessions, intents, state, sagas
   - Doesn't care about delivery mechanisms
   - Provides HTTP API for intents
   - **NO Experience routers**

2. **Experience Plane = Delivery Layer**
   - Owns REST, WebSocket, UI surfaces
   - Submits intents to Runtime via HTTP
   - Subscribes to execution events (WebSocket/polling)
   - Swappable without touching Runtime
   - **NO direct calls to runtime_service**

3. **Communication = Intents + Events**
   - Experience → Runtime: HTTP POST `/api/intent/submit`
   - Runtime → Experience: WebSocket events or polling `/api/execution/{id}/status`
   - **NO shared FastAPI apps**
   - **NO router mounting**

---

## 🚀 Recommended Fix Strategy

### Phase 1: Immediate (Testing)

1. **Remove Experience routers from Runtime app**
2. **Test E2E flow via direct intent submission** to `/api/intent/submit`
3. **Validate the architecture works** without router mounting

### Phase 2: Proper Experience Plane (Next)

1. **Create separate Experience service** that calls Runtime via HTTP
2. **Implement WebSocket event subscription** for execution events
3. **Deploy as separate container** (or same container, separate app)

---

## ✅ Validation

This fix ensures:
- ✅ Runtime Plane stays pure (execution only)
- ✅ Experience Plane is swappable (REST, WebSocket, future)
- ✅ No router mounting complexity
- ✅ Clear separation of concerns
- ✅ Matches architectural vision from plan
- ✅ **Fixes the root cause** of original router issues

---

## 📝 Next Steps

1. **Remove Experience router mounting** from main.py
2. **Test direct intent submission** via `/api/intent/submit`
3. **Validate E2E flow works** without router mounting
4. **Then build Experience Plane properly** as separate service

---

**Status:** 🔍 **ROOT CAUSE IDENTIFIED - ANTI-PATTERN CONFIRMED - CORRECTION PLAN READY**
