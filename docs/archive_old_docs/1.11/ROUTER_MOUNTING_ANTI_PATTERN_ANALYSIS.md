# Router Mounting Anti-Pattern Analysis

**Date:** January 2026  
**Status:** 🔍 **ROOT CAUSE ANALYSIS**  
**Critical:** This is the same type of issue that caused the original websocket/router problems

---

## 🎯 The Core Issue

We're **mixing Experience Plane (delivery) concerns into Runtime Plane (execution)**, which is the same anti-pattern that caused the original websocket/router issues.

---

## ❌ Current Anti-Pattern

### What We're Doing (WRONG):

```python
# In main.py lifespan
runtime_app = create_runtime_app(...)  # Runtime Plane app

# ❌ ANTI-PATTERN: Mounting Experience Plane on Runtime Plane
content_router = create_content_router(runtime_service)
runtime_app.include_router(content_router)  # Experience concerns in Runtime app

app.mount("/api", runtime_app)  # Mixed concerns
```

### Why This Is Wrong:

1. **Runtime Plane is execution authority** - It shouldn't know about delivery mechanisms
2. **Experience Plane is delivery** - It should be swappable (REST, WebSocket, future adapters)
3. **Mixing concerns** - This is the same pattern that caused original router issues
4. **Tight coupling** - Experience can't be swapped without touching Runtime

---

## ✅ Correct Architectural Pattern

### From rebuild_implementation_plan_v2.md:

> **Experience Plane (Phase 6)**
> 
> Experience is **delivery**, not logic.
> 
> **Interaction Model:**
> - Experience **submits intents** to Runtime
> - Experience **subscribes to execution events**
> - Experience **never invokes domain logic**
> 
> This lets:
> - MVP UI
> - Admin UI
> - Customer-facing solutions
> ...all coexist cleanly.

### The Correct Pattern:

```
┌─────────────────────────────────────────────────────────┐
│ Runtime Plane (Execution Authority)                      │
│ - FastAPI app at /api                                    │
│ - Endpoints: /session/create, /intent/submit, etc.      │
│ - NO delivery concerns                                   │
└─────────────────────────────────────────────────────────┘
                          ↑
                          │ HTTP intents
                          │ WebSocket events
                          │
┌─────────────────────────────────────────────────────────┐
│ Experience Plane (Delivery Layer)                        │
│ - SEPARATE FastAPI app/service                          │
│ - Endpoints: /v1/content/upload, /v1/data-mash/create  │
│ - Submits intents to Runtime                            │
│ - Subscribes to execution events                        │
│ - Swappable (REST, WebSocket, future adapters)         │
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

We're **repeating the same mistake** by mounting Experience routers on Runtime.

---

## ✅ Correct Solution

### Option 1: Separate Experience Service (Recommended)

```python
# Experience Plane - Separate service
# symphainy_platform/experience/experience_service.py

class ExperienceService:
    def __init__(self, runtime_url: str):
        self.runtime_url = runtime_url  # e.g., "http://runtime:8000"
        self.app = FastAPI()
    
    async def submit_intent_to_runtime(self, intent: dict):
        """Submit intent to Runtime Plane via HTTP"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.runtime_url}/api/intent/submit",
                json=intent
            )
            return response.json()
    
    def create_app(self):
        """Create Experience Plane FastAPI app"""
        router = APIRouter(prefix="/v1/content")
        
        @router.post("/upload")
        async def upload_file(...):
            # Submit intent to Runtime
            intent = {
                "intent_type": "content.upload",
                "realm": "content",
                "session_id": session_id,
                "tenant_id": tenant_id,
                "payload": {...}
            }
            result = await self.submit_intent_to_runtime(intent)
            return result
        
        self.app.include_router(router)
        return self.app
```

### Option 2: Experience as Separate Container (Best for Production)

```yaml
# docker-compose.yml
services:
  runtime:
    # Runtime Plane - execution only
  
  experience:
    # Experience Plane - delivery only
    # Calls runtime via HTTP
```

---

## 📊 Architecture Comparison

### ❌ Current (Anti-Pattern):

```
main.py
  └─ Runtime App (FastAPI)
      ├─ Runtime endpoints (/session, /intent)
      └─ Experience routers (/v1/content)  ❌ MIXED CONCERNS
```

### ✅ Correct (Architecturally Sound):

```
Runtime Service (main.py)
  └─ Runtime App (FastAPI)
      └─ Runtime endpoints only (/session, /intent)

Experience Service (separate)
  └─ Experience App (FastAPI)
      └─ Experience endpoints (/v1/content)
          └─ Submits intents to Runtime via HTTP
```

---

## 🎯 Key Principles

1. **Runtime Plane = Execution Authority**
   - Owns sessions, intents, state, sagas
   - Doesn't care about delivery mechanisms
   - Provides HTTP API for intents

2. **Experience Plane = Delivery Layer**
   - Owns REST, WebSocket, UI surfaces
   - Submits intents to Runtime
   - Subscribes to execution events
   - Swappable without touching Runtime

3. **Communication = Intents + Events**
   - Experience → Runtime: HTTP intents
   - Runtime → Experience: WebSocket events or polling
   - No shared FastAPI apps

---

## 🚀 Recommended Fix

1. **Remove Experience routers from Runtime app**
2. **Create separate Experience service** that calls Runtime via HTTP
3. **Test intent submission directly** via `/api/intent/submit` first
4. **Then build Experience Plane properly** as separate service

---

## ✅ Validation

This fix ensures:
- ✅ Runtime Plane stays pure (execution only)
- ✅ Experience Plane is swappable (REST, WebSocket, future)
- ✅ No router mounting complexity
- ✅ Clear separation of concerns
- ✅ Matches architectural vision from plan

---

**Status:** 🔍 **ROOT CAUSE IDENTIFIED - ANTI-PATTERN CONFIRMED**
