# Gap Implementation Plan - Architecture Aligned

**Date:** January 2026  
**Status:** 📋 **PLAN READY** - Following Backend Architecture Patterns

---

## 🎯 Executive Summary

After reviewing the platform architecture, "rules of the road", and backend SDK patterns, I've identified the correct approach to address the two gaps. We'll follow the backend team's established patterns and may need to update frontend expectations to match their design.

---

## 📐 Architecture Alignment

### Key Findings:

1. **Authentication:**
   - ✅ Security Guard SDK initialized in Experience Plane
   - ✅ SDK has `authenticate()` method
   - ⚠️ Need to check if `auth_abstraction` has `register_user()` method
   - ✅ Pattern: Use SDK from `app.state.security_guard_sdk`

2. **WebSocket:**
   - ⚠️ Frontend expects `/api/runtime/agent`
   - ⚠️ Backend architecture shows `/api/ws/agent` in some docs
   - ⚠️ Need backend team clarification on endpoint location
   - ✅ Experience Plane has Guide Agent Service
   - ✅ Agents are in realms (not directly in Runtime)

---

## 🔧 Implementation Plan

### Gap 1: Authentication Endpoints ✅ **READY**

**Decision:** Add auth router to Experience Plane (follows existing pattern)

**Implementation:**

1. **Check Auth Abstraction Capabilities:**
   - Verify if `auth_abstraction` has `register_user()` method
   - If not, we may need to add it or use a different approach

2. **Create Auth Router:**
   - File: `symphainy_platform/civic_systems/experience/api/auth.py`
   - Follow `sessions.py` pattern
   - Use Security Guard SDK from `app.state.security_guard_sdk`

3. **Register Router:**
   - Update `experience_service.py` to include auth router

**Pattern to Follow:**
```python
# From sessions.py pattern:
def get_security_guard_sdk(request: Request) -> SecurityGuardSDK:
    if not hasattr(request.app.state, "security_guard_sdk"):
        raise RuntimeError("Security Guard SDK not initialized.")
    return request.app.state.security_guard_sdk

@router.post("/login")
async def login(
    request: LoginRequest,
    security_guard: SecurityGuardSDK = Depends(get_security_guard_sdk)
):
    auth_result = await security_guard.authenticate({
        "email": request.email,
        "password": request.password
    })
    # ... handle response
```

---

### Gap 2: WebSocket Agent Endpoint ⚠️ **NEEDS CLARIFICATION**

**Question for Backend Team:**

**Which service should own `/api/runtime/agent` WebSocket endpoint?**

**Options:**

**Option A: Experience Plane** (User-facing pattern)
- ✅ Experience Plane handles all user-facing APIs
- ✅ Experience Plane has Guide Agent Service
- ✅ Experience Plane already has WebSocket router pattern
- ❌ Endpoint would be `/api/experience/agent` (not `/api/runtime/agent`)
- ⚠️ Would require frontend update

**Option B: Runtime Service** (Endpoint path pattern)
- ✅ Matches frontend expectation (`/api/runtime/agent`)
- ✅ Runtime handles execution
- ❌ Runtime doesn't have agent routing logic
- ❌ Agents are in realms, not Runtime service

**Option C: Hybrid** (Experience Plane with Runtime proxy)
- ✅ Experience Plane: `/api/runtime/agent` (user-facing)
- ✅ Experience Plane proxies to Runtime for execution
- ✅ Clean separation of concerns
- ⚠️ More complex routing

**Recommendation:** Ask backend team which option aligns with their architecture.

---

## 📋 Questions for Backend Team

### 1. Authentication

**Question:** Does `auth_abstraction` have a `register_user()` method?

**If Yes:**
- We'll use it via Security Guard SDK
- Implementation straightforward

**If No:**
- Should we add `register_user()` to `auth_abstraction`?
- Or use a different approach for registration?

---

### 2. WebSocket Agent Endpoint

**Question:** Which service should own `/api/runtime/agent` WebSocket endpoint?

**Follow-up Questions:**
- Should the endpoint be `/api/runtime/agent` or `/api/experience/agent`?
- How should agent messages be routed (guide vs liaison)?
- Should routing happen in Runtime or Experience Plane?
- How do agents get invoked from WebSocket messages?

---

## 🚀 Next Steps

1. **Immediate:** Check `auth_abstraction` for `register_user()` method
2. **Next:** Implement authentication router (following clear pattern)
3. **Then:** Ask backend team about WebSocket endpoint ownership
4. **Finally:** Implement WebSocket based on backend team's guidance

---

## 📝 Summary

**Authentication:** ✅ **CLEAR PATH** - Add to Experience Plane, use Security Guard SDK

**WebSocket:** ⚠️ **NEEDS CLARIFICATION** - Ask backend team which service should own endpoint

**Recommendation:** 
- Implement authentication endpoints now (following clear pattern)
- Ask backend team about WebSocket before implementing
- Update frontend if needed to match backend design

---

**Last Updated:** January 2026
