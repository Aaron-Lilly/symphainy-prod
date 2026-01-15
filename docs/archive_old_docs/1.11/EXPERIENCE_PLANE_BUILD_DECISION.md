# Experience Plane Build Decision

**Date:** January 2026  
**Status:** ✅ **DECISION: BUILD EXPERIENCE PLANE NOW**  
**Reasoning:** Plan compliance + architectural completeness

---

## 📋 Plan Review

### Build Order (rebuild_implementation_plan_v2.md):

```
Phase 0: Containers & Infra ✅
Phase 1: Runtime Plane ✅
Phase 2: Foundations ✅
Phase 3: Agent Foundation ✅
Phase 4: Smart City Plane ✅
Phase 5: Realm Plane ✅ (structure complete)
Phase 6: Experience Plane ❌ (not yet built properly)
```

### Key Principle:

> **"Nothing above should 'fake' what exists below."**

---

## 🎯 Current Situation

### What We're Doing (Faking Experience Plane):

- Testing E2E via direct Runtime API calls (`/api/intent/submit`)
- This is "faking" Experience Plane - we're bypassing the delivery layer
- Not a true E2E test (User → Experience → Runtime → Realms)

### What We Should Do:

- Build Experience Plane properly (Phase 6)
- Then test true E2E: User → Experience → Runtime → Realms
- Follows plan's build order

---

## ✅ Recommendation: BUILD EXPERIENCE PLANE NOW

### Why:

1. **Plan Compliance**
   - Phase 5 (Realms) structure is complete
   - Phase 6 (Experience Plane) is next in sequence
   - Plan says "bottom-up" - we're ready

2. **Architectural Completeness**
   - Experience Plane is the delivery layer
   - E2E testing requires all layers
   - Can't test E2E without delivery layer

3. **Proper Separation**
   - We just fixed the anti-pattern (removed router mounting)
   - Now build Experience Plane correctly (separate service)
   - Completes the architectural vision

4. **"Nothing Above Should Fake What Exists Below"**
   - Testing via Runtime API = faking Experience Plane
   - Building Experience Plane = proper architecture
   - Matches plan's principle

---

## 🏗️ Experience Plane Implementation Plan

### Phase 6.0: Experience Foundation

**Components:**
- SDKs
- Client helpers
- Auth/session helpers

### Phase 6.1: Experience Plane (REST)

**Architecture:**
```python
# Separate FastAPI service
# Calls Runtime via HTTP POST /api/intent/submit
# Subscribes to execution events (polling for now, WebSocket later)
```

**Endpoints:**
- `POST /v1/content/upload` → submits `content.upload` intent
- `POST /v1/content/data-mash/create` → submits `data_mash.create` intent
- `GET /v1/execution/{id}/status` → polls Runtime for status

**Key Pattern:**
- Experience Plane is **separate service**
- Calls Runtime via HTTP (not shared app)
- No router mounting on Runtime

### Phase 6.2: Experience Plane (WebSocket) - Future

- WebSocket endpoints for real-time execution events
- Event subscription to Runtime
- Real-time updates

---

## 📊 Comparison

### ❌ Current (Faking Experience Plane):

```
User
  ↓ (curl to Runtime API)
Runtime Plane (/api/intent/submit)
  ↓
Realms
```

**Problem:** Bypassing delivery layer, not true E2E

### ✅ Correct (With Experience Plane):

```
User
  ↓ (HTTP POST to Experience)
Experience Plane (/v1/content/upload)
  ↓ (HTTP POST to Runtime)
Runtime Plane (/api/intent/submit)
  ↓
Realms
```

**Benefit:** True E2E, all layers, proper architecture

---

## 🚀 Implementation Steps

1. **Create Experience Foundation Service**
   - SDKs, client helpers, auth helpers

2. **Create Experience Plane Service**
   - Separate FastAPI app
   - REST endpoints
   - Calls Runtime via HTTP

3. **Wire Experience Plane**
   - Same container for now (separate app)
   - Can move to separate container later

4. **Test True E2E**
   - User → Experience → Runtime → Realms
   - All layers working together

---

## ✅ Benefits

1. ✅ **Plan Compliance** - Follows build order exactly
2. ✅ **Architectural Completeness** - All layers built
3. ✅ **Proper E2E Testing** - True end-to-end flow
4. ✅ **No Faking** - Experience Plane is real, not bypassed
5. ✅ **Swappable** - Can swap REST for WebSocket, future adapters

---

## 📋 Decision

**✅ YES - Build Experience Plane Now**

**Reasoning:**
- Phase 5 (Realms) complete
- Phase 6 (Experience Plane) is next
- Plan says "nothing above should fake what exists below"
- E2E testing requires delivery layer
- We just fixed the anti-pattern - now build it right

---

**Status:** ✅ **DECISION MADE - BUILD EXPERIENCE PLANE NOW**
