# Backend Architecture - Update Summary

**Date:** January 24, 2026  
**Status:** 📋 **RECOMMENDED CHANGES**  
**Reviewer:** Architecture Review vs Current Implementation

---

## Executive Summary

After reviewing yesterday's WebSocket authentication fixes and comparing the current backend codebase against existing architecture documentation, this document outlines recommended updates to reflect the **actual current state** of the backend architecture.

**Key Findings:**
- ✅ **WebSocket endpoint** is in Experience Plane (not Runtime service)
- ✅ **Session creation** supports anonymous sessions
- ✅ **Security Guard SDK** pattern is established
- ✅ **WebSocket authentication** uses JWT validation (fixed January 24, 2026)
- ⚠️ **Backend architecture documentation** is sparse - needs comprehensive guide
- ⚠️ Some patterns documented in plans don't match actual implementation

---

## Current Backend Architecture (From Codebase Analysis)

### Service Organization

```
symphainy_platform/
├── civic_systems/
│   ├── experience/          ← Experience Plane (user-facing APIs)
│   │   ├── api/
│   │   │   ├── sessions.py          ← Session management
│   │   │   ├── auth.py             ← Authentication (if exists)
│   │   │   ├── runtime_agent_websocket.py  ← WebSocket endpoint
│   │   │   └── intents.py         ← Intent submission
│   │   ├── services/
│   │   │   └── guide_agent_service.py
│   │   └── experience_service.py  ← FastAPI app
│   └── smart_city/
│       └── sdk/
│           ├── security_guard_sdk.py  ← Authentication SDK
│           └── traffic_cop_sdk.py     ← Intent orchestration SDK
├── runtime/                 ← Runtime Foundation (execution)
│   ├── runtime_api.py        ← Runtime HTTP API
│   ├── execution_lifecycle_manager.py
│   └── intent_model.py
└── realms/                  ← Realm-specific logic
    ├── content/
    ├── insights/
    ├── journey/
    └── outcomes/
```

### Key Services

1. **Experience Plane** (`civic_systems/experience/`)
   - User-facing APIs
   - Session management
   - WebSocket endpoint (`/api/runtime/agent`)
   - Guide Agent Service
   - Authentication endpoints

2. **Runtime Foundation** (`runtime/`)
   - Execution engine
   - Intent processing
   - Agent orchestration
   - State management

3. **Realms** (`realms/`)
   - Realm-specific orchestrators
   - Realm-specific agents
   - Realm-specific enabling services

---

## Recommended Updates to Backend Architecture Documentation

### 1. Create Comprehensive Backend Architecture Guide

**Current State:**
- ❌ No comprehensive backend architecture guide exists
- ⚠️ Only `execution/backend_architecture_alignment_plan.md` (planning doc, not architecture guide)
- ⚠️ Architecture patterns scattered across multiple planning documents

**Recommended:**
Create `docs/01212026/backend_architecture_guide.md` with:

```markdown
# Backend Architecture Guide (Symphainy Platform)

## 1. Service Architecture Overview

### 1.1 Service Boundaries

**Experience Plane:**
- User-facing APIs
- Session management
- Authentication
- WebSocket endpoints
- Guide Agent Service
- Intent submission interface

**Runtime Foundation:**
- Execution engine
- Intent processing
- Agent orchestration
- State management
- Execution lifecycle

**Realms:**
- Realm-specific logic
- Realm orchestrators
- Realm agents
- Realm enabling services

### 1.2 Service Communication

**Experience Plane → Runtime:**
- HTTP: Intent submission
- HTTP: Session queries
- HTTP: Execution status

**Experience Plane → Realms:**
- Via Runtime (indirect)
- Via Traffic Cop SDK

**Runtime → Realms:**
- Direct invocation
- Via orchestrators
```

---

### 2. Update WebSocket Architecture Documentation

**Current State:**
- `execution/backend_architecture_alignment_plan.md` has questions about WebSocket ownership
- Actual implementation: WebSocket is in Experience Plane

**What's Actually Implemented:**
- ✅ WebSocket endpoint: `/api/runtime/agent` (Experience Plane)
- ✅ File: `civic_systems/experience/api/runtime_agent_websocket.py`
- ✅ Authentication: Uses `access_token` (JWT) + `session_id` (session state)
- ✅ Validation: Security Guard SDK validates JWT
- ✅ Agent routing: Experience Plane routes to Guide Agent or Runtime

**Recommended Update:**
```markdown
### 2.1 WebSocket Agent Endpoint - ✅ IMPLEMENTED

**Location:** Experience Plane (`civic_systems/experience/api/runtime_agent_websocket.py`)

**Endpoint:** `/api/runtime/agent` (WebSocket)

**Ownership:** Experience Plane (despite `/api/runtime/` path - path is contract, not locator)

**Authentication:**
```python
@router.websocket("/agent")
async def runtime_agent_websocket(
    websocket: WebSocket,
    session_token: Optional[str] = Query(None),  # Legacy support
    access_token: Optional[str] = Query(None),   # JWT for authentication
    session_id: Optional[str] = Query(None)      # Session ID for state
):
    # Validate access_token (JWT) with Security Guard SDK
    auth_token = access_token or session_token
    auth_result = await security_guard.validate_token(auth_token)
    
    # Use session_id for session operations
    ws_session_id = session_id or auth_token
```

**Flow:**
1. Client connects with `access_token` (JWT) + `session_id`
2. Experience Plane validates JWT via Security Guard SDK
3. Experience Plane routes message to appropriate agent:
   - Guide Agent → Guide Agent Service (in Experience Plane)
   - Liaison Agent → Runtime (via intent submission)
4. Agent executes and streams events back

**Agent Routing:**
- Guide Agent: Handled by Guide Agent Service (Experience Plane)
- Liaison Agent: Routed to Runtime for realm agent execution
```

---

### 3. Update Session Architecture Documentation

**Current State:**
- `SESSION_FIRST_ARCHITECTURE_REFACTORING_PLAN.md` describes planned changes
- Actual implementation: Anonymous sessions are supported

**What's Actually Implemented:**
- ✅ Session creation endpoint: `/api/session/create` (Experience Plane)
- ✅ Anonymous session support: `tenant_id` is optional
- ✅ Session upgrade: Can add `user_id`, `tenant_id` to existing session
- ✅ Session retrieval: `/api/session/{session_id}` (tenant_id optional)

**Recommended Update:**
```markdown
### 3.1 Session Management - ✅ IMPLEMENTED

**Location:** Experience Plane (`civic_systems/experience/api/sessions.py`)

**Endpoints:**
- `POST /api/session/create` - Create session (anonymous or authenticated)
- `GET /api/session/{session_id}` - Get session details
- `POST /api/session/create-anonymous` - Create anonymous session (if exists)

**Anonymous Session Support:**
```python
@router.post("/create")
async def create_session(
    request: SessionCreateRequest,
    runtime_client: RuntimeClient = Depends(get_runtime_client),
    security_guard_sdk: SecurityGuardSDK = Depends(get_security_guard_sdk),
    traffic_cop_sdk: TrafficCopSDK = Depends(get_traffic_cop_sdk)
):
    # tenant_id is optional in SessionCreateRequest
    # If not provided, creates anonymous session
```

**Session Upgrade Pattern:**
- Anonymous session created first (no auth required)
- Authentication adds `user_id`, `tenant_id` to existing session
- Session ID remains the same (upgrade, not replacement)
```

---

### 4. Update Authentication Architecture Documentation

**Current State:**
- `execution/backend_architecture_alignment_plan.md` describes planned auth endpoints
- Actual implementation: Security Guard SDK pattern is established

**What's Actually Implemented:**
- ✅ Security Guard SDK: Initialized in `experience_service.py`
- ✅ Stored in `app.state.security_guard_sdk` for dependency injection
- ✅ `validate_token()` method: Validates JWT tokens
- ✅ `authenticate()` method: Authenticates credentials
- ⚠️ Auth endpoints: May exist in `api/auth.py` (needs verification)

**Recommended Update:**
```markdown
### 4.1 Authentication Pattern - ✅ IMPLEMENTED

**Location:** Experience Plane (`civic_systems/experience/`)

**Security Guard SDK:**
- Initialized in `experience_service.py`
- Stored in `app.state.security_guard_sdk`
- Dependency injection pattern: `Depends(get_security_guard_sdk)`

**Methods:**
```python
# Validate JWT token
auth_result = await security_guard.validate_token(access_token)
# Returns: AuthenticationResult with user_id, tenant_id, roles, permissions

# Authenticate credentials
auth_result = await security_guard.authenticate(credentials)
# Returns: AuthenticationResult
```

**Usage Pattern:**
```python
def get_security_guard_sdk(request: Request) -> SecurityGuardSDK:
    if not hasattr(request.app.state, "security_guard_sdk"):
        raise RuntimeError("Security Guard SDK not initialized")
    return request.app.state.security_guard_sdk

@router.post("/endpoint")
async def endpoint(
    security_guard: SecurityGuardSDK = Depends(get_security_guard_sdk)
):
    # Use security_guard for authentication
    pass
```
```

---

### 5. Document WebSocket Authentication Fix (January 24, 2026)

**What Was Fixed:**
- Parameter naming: Frontend now sends `session_id` (not `session_token`)
- Authentication validation: Backend validates `access_token` as JWT (not `session_id`)
- Variable naming: Consistent use of `ws_session_id` throughout

**Recommended Addition:**
```markdown
### 5.1 WebSocket Authentication Fix (January 24, 2026)

**Issue:** WebSocket connections failing with 403 Forbidden

**Root Cause:**
- Frontend sent `session_token` parameter (actually session_id)
- Backend tried to validate session_id as JWT
- Security Guard SDK rejected (session_id is not JWT format)

**Fix Applied:**
1. Frontend: Changed parameter from `session_token` to `session_id`
2. Backend: Validate `access_token` (JWT) for authentication
3. Backend: Use `session_id` for session state (not authentication)
4. Backend: Support both `access_token` and `session_token` (backward compatibility)

**Current Implementation:**
```python
# Accept both parameter names (backward compatibility)
auth_token = access_token or session_token

# Validate JWT (not session_id)
auth_result = await security_guard.validate_token(auth_token)

# Use session_id for session operations
ws_session_id = session_id or auth_token
```

**Reference:** `docs/PHASE7_AUTH_ISSUE_FIXED.md` for full details
```

---

### 6. Document SDK Pattern

**Current State:**
- SDKs exist but pattern not well documented
- Security Guard SDK, Traffic Cop SDK are used

**What's Actually Implemented:**
- ✅ Security Guard SDK: Authentication abstraction
- ✅ Traffic Cop SDK: Intent orchestration
- ✅ SDKs initialized in `experience_service.py`
- ✅ Stored in `app.state` for dependency injection

**Recommended Addition:**
```markdown
### 6.1 SDK Pattern - ✅ IMPLEMENTED

**Location:** `civic_systems/smart_city/sdk/`

**SDKs:**
- `SecurityGuardSDK`: Authentication abstraction
- `TrafficCopSDK`: Intent orchestration

**Initialization:**
```python
# In experience_service.py
security_guard_sdk = SecurityGuardSDK(auth_abstraction=public_works.get_auth_abstraction())
traffic_cop_sdk = TrafficCopSDK(...)

app.state.security_guard_sdk = security_guard_sdk
app.state.traffic_cop_sdk = traffic_cop_sdk
```

**Usage:**
```python
def get_security_guard_sdk(request: Request) -> SecurityGuardSDK:
    return request.app.state.security_guard_sdk

@router.post("/endpoint")
async def endpoint(
    security_guard: SecurityGuardSDK = Depends(get_security_guard_sdk)
):
    # Use SDK
    pass
```

**Abstraction Pattern:**
- SDKs wrap Public Works abstractions
- Provides consistent interface
- Enables dependency injection
- Allows testing/mocking
```

---

## Summary of Changes

### ✅ Updates Needed (Reflect Actual Implementation)

1. **Create Comprehensive Backend Architecture Guide:**
   - Service boundaries and responsibilities
   - Service communication patterns
   - SDK pattern documentation
   - Authentication pattern documentation

2. **Update WebSocket Documentation:**
   - Document that WebSocket is in Experience Plane (not Runtime)
   - Document authentication parameter requirements
   - Document agent routing logic
   - Document January 24, 2026 fix

3. **Update Session Documentation:**
   - Document anonymous session support
   - Document session upgrade pattern
   - Document actual endpoint implementations

4. **Update Authentication Documentation:**
   - Document Security Guard SDK pattern
   - Document dependency injection pattern
   - Document actual methods available

### ⚠️ Additions Needed (Document Current State)

5. **New Section: SDK Pattern**
   - Document SDK initialization
   - Document dependency injection pattern
   - Document abstraction layer

6. **New Section: Service Communication**
   - Document Experience Plane → Runtime communication
   - Document Experience Plane → Realms communication
   - Document Runtime → Realms communication

### 📋 Verification Needed

7. **Auth Endpoints:**
   - Verify if `api/auth.py` exists
   - Document actual auth endpoints
   - Document registration endpoint (if exists)

8. **Session Upgrade Endpoint:**
   - Verify if session upgrade endpoint exists
   - Document upgrade pattern
   - Document upgrade flow

---

## Priority

**High Priority (Create/Update Immediately):**
- Create comprehensive backend architecture guide
- Document WebSocket architecture (recently fixed)
- Document session architecture (core functionality)

**Medium Priority (Update Soon):**
- Document authentication pattern
- Document SDK pattern
- Document service communication

**Low Priority (Can Wait):**
- Verify and document auth endpoints
- Verify and document session upgrade endpoint

---

## Next Steps

1. ✅ Review this summary
2. ⏳ Create `docs/01212026/backend_architecture_guide.md`
3. ⏳ Update `execution/backend_architecture_alignment_plan.md` with actual implementation
4. ⏳ Verify auth endpoints and document
5. ⏳ Verify session upgrade endpoint and document

---

## Files to Review/Update

**Create:**
- `docs/01212026/backend_architecture_guide.md` (comprehensive guide)

**Update:**
- `docs/execution/backend_architecture_alignment_plan.md` (mark questions as resolved)
- Add WebSocket fix documentation

**Verify:**
- `civic_systems/experience/api/auth.py` (does it exist? what endpoints?)
- Session upgrade endpoint (does it exist? where?)

---

**Last Updated:** January 24, 2026
