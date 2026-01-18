# Architecture-Aligned Gap Analysis

**Date:** January 2026  
**Status:** 🔍 **ARCHITECTURE REVIEW COMPLETE**

---

## 🎯 Executive Summary

After reviewing the platform architecture and "rules of the road", I've identified the correct approach to address the two gaps. The backend team's architecture is well-designed, and we need to align frontend expectations with their SDK patterns.

---

## 📐 Architecture Review Findings

### 1. Authentication Architecture ✅

**Backend Pattern:**
- **Security Guard SDK** is initialized in `experience_main.py` during service startup
- SDK is stored in `app.state.security_guard_sdk` for dependency injection
- SDK uses `auth_abstraction` from Public Works (follows abstraction pattern)
- SDK provides `authenticate()` method (returns `AuthenticationResult`)

**Current Implementation:**
- ✅ Security Guard SDK initialized in Experience Plane
- ✅ Available via `app.state.security_guard_sdk`
- ✅ Used in session creation endpoint
- ❌ Auth endpoints (`/api/auth/login`, `/api/auth/register`) not registered

**Architecture Alignment:**
- ✅ Auth endpoints should be in **Experience Plane** (where Security Guard SDK lives)
- ✅ Should use Security Guard SDK (not direct auth abstraction)
- ✅ Follow existing router pattern (like `sessions.py`, `intents.py`)

---

### 2. WebSocket Architecture ⚠️ **NEEDS CLARIFICATION**

**Backend Pattern (from docs):**
- Runtime Foundation owns WebSocket connections
- Endpoint: `/api/runtime/agent`
- Runtime Plane WebSocket router exists in old codebase
- Current Runtime service doesn't have WebSocket router

**Architecture Question:**
- Should WebSocket be in **Runtime service** (where Runtime Foundation lives)?
- Or should it be in **Experience Plane** (where user-facing APIs live)?
- Or should it be in a separate **Runtime Plane** service?

**Current State:**
- ❌ Runtime service has no WebSocket router
- ✅ Experience Plane has WebSocket router (but for execution streaming, not agents)
- ⚠️ Frontend expects `/api/runtime/agent` (suggests Runtime service)

**Architecture Alignment:**
- Need to confirm: Should `/api/runtime/agent` be in Runtime service or Experience Plane?
- Based on endpoint path (`/api/runtime/agent`), suggests Runtime service
- But Runtime service doesn't have agent routing logic (that's in realms)

---

## 🔧 Recommended Approach

### Option A: Follow Endpoint Path (Runtime Service)

**Rationale:**
- Frontend expects `/api/runtime/agent`
- Path suggests Runtime service ownership
- Runtime Foundation owns WebSocket connections (per architecture docs)

**Implementation:**
- Add WebSocket router to Runtime service
- Route messages to appropriate agents via Runtime's agent routing
- Runtime service already has Execution Lifecycle Manager

**Pros:**
- Matches endpoint path expectation
- Aligns with "Runtime Foundation owns WebSocket" pattern
- Runtime has execution context

**Cons:**
- Runtime service doesn't currently have agent routing
- Would need to add agent discovery/routing logic

---

### Option B: Follow User-Facing Pattern (Experience Plane)

**Rationale:**
- Experience Plane handles all user-facing APIs
- WebSocket is user-facing communication
- Experience Plane already has WebSocket router pattern

**Implementation:**
- Add WebSocket router to Experience Plane
- Route to Runtime for agent execution
- Use Runtime Client to submit agent intents

**Pros:**
- Consistent with other user-facing APIs
- Experience Plane already has WebSocket infrastructure
- Can reuse existing Runtime Client

**Cons:**
- Endpoint path would be `/api/experience/agent` (not `/api/runtime/agent`)
- Would require frontend update

---

### Option C: Hybrid (Experience Plane with Runtime Proxy)

**Rationale:**
- Experience Plane handles user-facing
- Runtime handles execution
- Proxy pattern for clean separation

**Implementation:**
- Experience Plane: `/api/runtime/agent` (user-facing endpoint)
- Experience Plane proxies to Runtime for agent execution
- Runtime handles actual agent routing

**Pros:**
- Matches frontend expectation (`/api/runtime/agent`)
- Clean separation of concerns
- Experience Plane = user-facing, Runtime = execution

**Cons:**
- Requires coordination between services
- More complex routing

---

## ✅ Recommended Solution

### 1. Authentication Endpoints ✅ **CLEAR PATH**

**Decision:** Add auth router to Experience Plane

**Rationale:**
- Security Guard SDK already initialized in Experience Plane
- Follows existing router pattern
- User-facing API (belongs in Experience Plane)

**Implementation:**
- Create `symphainy_platform/civic_systems/experience/api/auth.py`
- Use Security Guard SDK from `app.state.security_guard_sdk`
- Follow pattern from `sessions.py` and `intents.py`
- Register in `experience_service.py`

---

### 2. WebSocket Agent Endpoint ⚠️ **NEEDS BACKEND TEAM INPUT**

**Decision:** **ASK BACKEND TEAM** - Which service should own `/api/runtime/agent`?

**Questions for Backend Team:**
1. Should `/api/runtime/agent` be in Runtime service or Experience Plane?
2. Does Runtime service have agent routing capabilities?
3. Should we update frontend to use `/api/experience/agent` instead?
4. Is there a Runtime Plane service that should handle this?

**Recommendation:**
- **If Runtime service:** Add WebSocket router to Runtime, route to agents via Execution Lifecycle Manager
- **If Experience Plane:** Add WebSocket router to Experience Plane, use Runtime Client for execution
- **If separate service:** Update frontend to match actual endpoint

---

## 📋 Implementation Plan

### Phase 1: Authentication (Clear Path) ✅

**File:** `symphainy_platform/civic_systems/experience/api/auth.py` (NEW)

**Pattern to Follow:**
- Use `sessions.py` as template
- Use Security Guard SDK from `app.state.security_guard_sdk`
- Follow existing request/response model pattern
- Use dependency injection pattern

**Key Points:**
- ✅ Use Security Guard SDK (not direct auth abstraction)
- ✅ Follow Public Works abstraction pattern (via SDK)
- ✅ Store in `app.state` for dependency injection
- ✅ Use existing error handling patterns

---

### Phase 2: WebSocket (Needs Clarification) ⚠️

**Pending Backend Team Decision:**
- Which service owns `/api/runtime/agent`?
- How should agent routing work?
- Should frontend endpoint be updated?

**Once Clarified:**
- Implement WebSocket router in appropriate service
- Follow existing WebSocket patterns
- Route messages to agents correctly
- Emit runtime events to frontend

---

## 🎯 Next Steps

1. **Immediate:** Implement authentication endpoints in Experience Plane
2. **Next:** Ask backend team about WebSocket endpoint ownership
3. **Then:** Implement WebSocket based on backend team's guidance
4. **Finally:** Update frontend if needed to match backend design

---

## 📝 Questions for Backend Team

1. **WebSocket Endpoint:**
   - Should `/api/runtime/agent` be in Runtime service or Experience Plane?
   - Does Runtime service have agent routing capabilities?
   - Should we update frontend endpoint expectation?

2. **Agent Routing:**
   - How should agent messages be routed (guide vs liaison)?
   - Should routing happen in Runtime or Experience Plane?
   - How do agents get invoked from WebSocket messages?

3. **Architecture Pattern:**
   - Is there a Runtime Plane service that should handle WebSocket?
   - Should WebSocket be a separate service?
   - What's the canonical pattern for agent WebSocket communication?

---

**Last Updated:** January 2026
