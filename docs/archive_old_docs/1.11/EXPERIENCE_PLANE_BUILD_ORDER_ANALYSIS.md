# Experience Plane Build Order Analysis

**Date:** January 2026  
**Status:** 🔍 **ANALYSIS - BUILD ORDER DECISION**  
**Question:** Should we implement Experience Plane (Phase 6) before E2E testing?

---

## 📋 Plan Review

### Build Order (from rebuild_implementation_plan_v2.md):

```
Phase 0: Containers & Infra
↓
Phase 1: Runtime Plane (execution + state)
↓
Phase 2: Foundations (shared primitives)
↓
Phase 3: Agent Foundation (reasoning engines)
↓
Phase 4: Smart City Plane (governance & control)
↓
Phase 5: Realm Plane (domain logic)  ← We are here
↓
Phase 6: Experience Plane (delivery)  ← Not yet built
```

### Key Principle:

> **"Nothing above should 'fake' what exists below."**

---

## 🎯 Current State

### ✅ What We've Built:

- ✅ Phase 0: Containers, Infra, Guardrails
- ✅ Phase 1: Runtime Plane (complete)
- ✅ Phase 2: Foundations (Public Works + Curator)
- ✅ Phase 3: Agent Foundation
- ✅ Phase 4: Smart City Plane
- ✅ Phase 5: Realm Plane (Content + Insights - structure complete, services skeleton)

### ❌ What We Haven't Built:

- ❌ Phase 6: Experience Plane (properly)
  - We created handlers but mounted them on Runtime (anti-pattern)
  - We removed the anti-pattern but haven't built Experience Plane as separate service

---

## 🔍 The Question

**Are we putting the cart before the horse by trying to test E2E without Experience Plane?**

### Analysis:

1. **Plan Says:** Experience Plane is Phase 6 (after Realms)
2. **Plan Says:** "Nothing above should 'fake' what exists below"
3. **Current State:** We're trying to test E2E without Experience Plane
4. **What We're Doing:** Testing via direct `/api/intent/submit` (Runtime API)

---

## ✅ Recommendation: YES - Build Experience Plane Now

### Why:

1. **Architectural Completeness**
   - Experience Plane is the delivery layer
   - E2E testing requires delivery layer
   - Testing via Runtime API directly is "faking" Experience Plane

2. **Proper Separation**
   - We just removed the anti-pattern (mounting routers on Runtime)
   - Now we need to build Experience Plane properly (separate service)
   - This completes the architectural vision

3. **Testing Clarity**
   - With Experience Plane, E2E testing is clear:
     - User → Experience Plane → Runtime → Realms
   - Without it, we're testing Runtime directly (not E2E)

4. **Plan Alignment**
   - Phase 5 (Realms) structure is complete
   - Phase 6 (Experience Plane) is next in sequence
   - We're ready to build it

---

## 📊 What Experience Plane Should Be

### From the Plan (Phase 6):

**Experience Foundation:**
- SDKs
- Client helpers
- Auth/session helpers

**Experience Plane:**
- REST
- WebSockets
- Future adapters (CRM, ERP, Voice)

**Interaction Model:**
- Submits intents to Runtime
- Subscribes to execution events
- Never invokes domain logic

---

## 🏗️ Proposed Implementation

### Option 1: Experience Plane as Separate Service (Recommended)

```python
# symphainy_platform/experience/experience_service.py

class ExperienceService:
    """
    Experience Plane Service - Delivery Layer
    
    WHAT: I deliver platform capabilities to users
    HOW: I submit intents to Runtime and subscribe to events
    """
    
    def __init__(self, runtime_url: str):
        self.runtime_url = runtime_url
        self.app = FastAPI(title="Symphainy Experience Plane")
    
    def create_app(self):
        """Create Experience Plane FastAPI app."""
        # REST endpoints
        # WebSocket endpoints
        # All call Runtime via HTTP
        return self.app
```

### Option 2: Experience Plane in Same Container (For Now)

- Separate FastAPI app
- Calls Runtime via HTTP (not shared app)
- Can be moved to separate container later

---

## ✅ Benefits of Building Experience Plane Now

1. ✅ **Complete Architecture** - All phases built in order
2. ✅ **Proper E2E Testing** - User → Experience → Runtime → Realms
3. ✅ **Clear Separation** - Experience is delivery, Runtime is execution
4. ✅ **Swappable** - Can swap REST for WebSocket, future adapters
5. ✅ **Plan Compliance** - Follows build order exactly

---

## 🚀 Implementation Plan

### Phase 6.0: Experience Foundation

1. Create Experience Foundation Service
2. Create SDK/client helpers
3. Create auth/session helpers

### Phase 6.1: Experience Plane (REST)

1. Create Experience Service (separate FastAPI app)
2. Implement REST endpoints:
   - `/v1/content/upload` → submits `content.upload` intent
   - `/v1/content/data-mash/create` → submits `data_mash.create` intent
3. All endpoints call Runtime via HTTP POST `/api/intent/submit`
4. Return execution results

### Phase 6.2: Experience Plane (WebSocket) - Future

1. WebSocket endpoints for execution events
2. Event subscription to Runtime
3. Real-time updates

---

## 📋 Decision

**Recommendation: YES - Build Experience Plane Now**

**Reasoning:**
- We've completed Phase 5 (Realm structure)
- Experience Plane is Phase 6 (next in sequence)
- E2E testing requires delivery layer
- We just fixed the anti-pattern - now build it right
- Matches plan's build order

**Alternative:**
- Continue testing via Runtime API directly
- Build Experience Plane later
- **But this violates "nothing above should fake what exists below"**

---

**Status:** 🔍 **ANALYSIS COMPLETE - RECOMMEND BUILDING EXPERIENCE PLANE NOW**
