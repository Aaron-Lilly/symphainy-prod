# Questions for Backend Team - Architecture Alignment

**Date:** January 2026  
**Status:** 📋 **QUESTIONS READY** - Awaiting Backend Team Input

---

## 🎯 Context

We've reviewed the backend architecture and identified two gaps that need to be addressed before E2E testing. Before implementing, we want to ensure we follow your established patterns and SDKs correctly.

---

## 📋 Gap 1: Authentication Endpoints

### Current State:
- ✅ Security Guard SDK initialized in Experience Plane (`experience_main.py`)
- ✅ SDK stored in `app.state.security_guard_sdk`
- ✅ SDK has `authenticate()` method
- ❌ Auth endpoints (`/api/auth/login`, `/api/auth/register`) not registered

### Question 1: User Registration

**Does `auth_abstraction` (AuthenticationProtocol) have a `register_user()` method?**

**Current Protocol Methods:**
- ✅ `authenticate(credentials)` - Login
- ✅ `validate_token(token)` - Token validation
- ✅ `refresh_token(refresh_token)` - Token refresh
- ❓ `register_user()` - Not in protocol definition

**If `register_user()` exists:**
- We'll use it via Security Guard SDK
- Implementation straightforward

**If `register_user()` doesn't exist:**
- Should we add it to `AuthenticationProtocol`?
- Or use a different approach for registration?
- Should registration go through a different abstraction?

### Our Proposed Implementation:

**File:** `symphainy_platform/civic_systems/experience/api/auth.py` (NEW)

**Pattern:**
- Follow `sessions.py` as template
- Use Security Guard SDK from `app.state.security_guard_sdk`
- Use dependency injection pattern
- Follow existing error handling

**Login Endpoint:**
```python
@router.post("/login")
async def login(
    request: LoginRequest,
    security_guard: SecurityGuardSDK = Depends(get_security_guard_sdk)
):
    auth_result = await security_guard.authenticate({
        "email": request.email,
        "password": request.password
    })
    # Return AuthResponse with user_id, tenant_id, roles, permissions
```

**Register Endpoint:**
```python
@router.post("/register")
async def register(
    request: RegisterRequest,
    security_guard: SecurityGuardSDK = Depends(get_security_guard_sdk)
):
    # Need to know: How should registration work?
    # Option A: auth_abstraction.register_user()?
    # Option B: Direct call to auth_abstraction with different method?
    # Option C: Different abstraction?
```

**Questions:**
1. Does `auth_abstraction` have `register_user()` method?
2. If not, should we add it to `AuthenticationProtocol`?
3. What's the correct pattern for user registration?

---

## 📋 Gap 2: WebSocket Agent Endpoint

### Current State:
- ✅ Frontend expects: `/api/runtime/agent` WebSocket endpoint
- ✅ Frontend uses: `RuntimeClient` connecting to `/api/runtime/agent`
- ❌ Runtime service has no WebSocket router
- ✅ Experience Plane has Guide Agent Service
- ✅ Experience Plane has WebSocket router (for execution streaming)

### Question 2: WebSocket Endpoint Ownership

**Which service should own `/api/runtime/agent` WebSocket endpoint?**

**Option A: Runtime Service** (Endpoint path suggests this)
- ✅ Matches frontend expectation (`/api/runtime/agent`)
- ✅ Runtime handles execution
- ❌ Runtime doesn't have agent routing logic
- ❌ Agents are in realms, not Runtime service directly

**Option B: Experience Plane** (User-facing pattern)
- ✅ Experience Plane handles all user-facing APIs
- ✅ Experience Plane has Guide Agent Service
- ✅ Experience Plane already has WebSocket router pattern
- ❌ Endpoint would be `/api/experience/agent` (not `/api/runtime/agent`)
- ⚠️ Would require frontend update

**Option C: Hybrid** (Experience Plane with Runtime proxy)
- ✅ Experience Plane: `/api/runtime/agent` (user-facing endpoint)
- ✅ Experience Plane proxies to Runtime for agent execution
- ✅ Clean separation: Experience = user-facing, Runtime = execution
- ⚠️ More complex routing

### Our Understanding:

**From Architecture Docs:**
- Experience Plane = User-facing APIs
- Runtime = Execution engine
- Agents are in realms (not directly in Runtime)
- Guide Agent Service is in Experience Plane

**From Frontend:**
- Expects `/api/runtime/agent`
- Uses `RuntimeClient` for WebSocket connection
- Sends messages with `agent_type` and `pillar` for routing

### Questions:

1. **Service Ownership:**
   - Should `/api/runtime/agent` be in Runtime service or Experience Plane?
   - Does the endpoint path (`/api/runtime/agent`) indicate Runtime service ownership?

2. **Agent Routing:**
   - How should agent messages be routed (guide vs liaison)?
   - Should routing happen in Runtime or Experience Plane?
   - How do agents get invoked from WebSocket messages?
   - Should we route to Guide Agent Service (Experience Plane) and realm agents (via Runtime)?

3. **Architecture Pattern:**
   - Is there a Runtime Plane service that should handle WebSocket?
   - Should WebSocket be a separate service?
   - What's the canonical pattern for agent WebSocket communication?

4. **Frontend Alignment:**
   - Should we update frontend to match backend design?
   - Or should backend match frontend expectation (`/api/runtime/agent`)?

---

## 🎯 Our Recommendation

### Authentication:
- ✅ **Implement in Experience Plane** (clear pattern)
- ⚠️ **Need clarification on registration method**

### WebSocket:
- ⚠️ **Ask backend team** which service should own endpoint
- ⚠️ **Clarify agent routing pattern**
- ⚠️ **Determine if frontend needs update**

---

## 📝 Next Steps

1. **Backend Team Answers:**
   - Clarify registration method
   - Clarify WebSocket endpoint ownership
   - Clarify agent routing pattern

2. **Implementation:**
   - Implement authentication endpoints (following backend patterns)
   - Implement WebSocket endpoint (based on backend team's guidance)
   - Update frontend if needed to match backend design

3. **Testing:**
   - Test authentication flow
   - Test WebSocket agent communication
   - Verify E2E integration

---

**Last Updated:** January 2026
