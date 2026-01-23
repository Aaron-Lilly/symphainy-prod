# Strategic WebSocket & Session Management Analysis

**Date:** January 23, 2026  
**Status:** Critical Architectural Review  
**Context:** WebSocket connection failures preventing platform launch

---

## Executive Summary

The platform is experiencing a **fundamental architectural mismatch** between:
1. **Frontend expectations** (session tokens generated client-side)
2. **Backend architecture** (sessions must exist in Runtime via Traffic Cop SDK)
3. **WebSocket authentication** (requires valid Runtime session)

This is causing a **cascade of failures** before the user even logs in.

---

## 1. What Went Wrong in `/symphainy_source/`

### Historical Problems (Inferred from Architecture Docs)

Based on the architecture documentation and current errors, the old version likely had:

1. **State Synchronization Issues:**
   - WebSocket connections without proper session state
   - Race conditions between session creation and WebSocket connection
   - Frontend and backend state out of sync

2. **Session Management Fragmentation:**
   - Sessions created in multiple places
   - No single source of truth
   - Session tokens not validated against Runtime state

3. **WebSocket Authentication Failures:**
   - Connections accepted before authentication
   - Session tokens not validated
   - Resource exhaustion from unauthenticated connections

4. **Architectural Coupling:**
   - Runtime knowing about user-facing concerns
   - Experience Plane executing agents directly
   - No clear separation between intent and execution

---

## 2. How the New Architecture Was Designed to Prevent It

### Runtime Plane + State Surface Architecture

**Core Principle:**
> **Only Realms touch data. Everything else governs, observes, or intends.**

**Key Design Elements:**

1. **State Surface (Centralized State):**
   - Single source of truth for execution state
   - Write-ahead logging (WAL) for consistency
   - State machine for artifact lifecycle

2. **Traffic Cop SDK (Session Management):**
   - Sessions created via Traffic Cop → Runtime
   - Runtime validates via primitives
   - Sessions exist in Runtime before use

3. **Experience Plane Ownership:**
   - Experience Plane owns WebSocket endpoints (even `/api/runtime/agent`)
   - Experience Plane handles authentication
   - Experience Plane routes agents, Runtime executes

4. **Clear Separation:**
   - Experience = Intent + Context Boundary
   - Runtime = Execution Engine (stateless)
   - Agents generate intents, Runtime executes

### Intended Flow

```
1. User logs in → Auth Provider
2. Auth Provider → Experience Plane `/api/auth/login`
3. Experience Plane → Security Guard SDK (authenticate)
4. Experience Plane → Traffic Cop SDK (create session intent)
5. Traffic Cop SDK → Runtime (create session)
6. Runtime → Validates via primitives → Creates session
7. Experience Plane → Returns session_token
8. Frontend → Stores session_token
9. Frontend → Connects WebSocket with session_token
10. Experience Plane → Validates token → Accepts connection
```

---

## 3. Why It's Not Working

### Critical Issues Identified

#### Issue 1: Session Endpoints Not Routed

**Error:** `GET /api/session/{session_id} 404`  
**Error:** `POST /api/session/create 404`

**Root Cause:**
- Traefik routing doesn't include `/api/session` path
- Experience service has the endpoint, but Traefik isn't routing to it

**Evidence:**
```yaml
# Current routing (docker-compose.yml)
- traefik.http.routers.experience.rule=PathPrefix(`/api/sessions`) || PathPrefix(`/api/intent`) || ...
```

**Problem:** Router uses `/api/sessions` (plural) but endpoint is `/api/session` (singular)

#### Issue 2: Frontend Creating Sessions Before Login

**Error:** `Failed to load session: Session {session_id} not found`  
**Error:** `Failed to create session`

**Root Cause:**
- Frontend is generating session tokens client-side
- Frontend tries to load/create sessions before authentication
- Sessions don't exist in Runtime because they were never created via Traffic Cop SDK

**Evidence from Console:**
```
ℹ️ No valid session found
GET /api/session/{session_id} 404
POST /api/session/create 404
```

#### Issue 3: WebSocket Authentication Failing

**Error:** `WebSocket handshake: Unexpected response code: 403`

**Root Cause:**
- WebSocket endpoint requires valid session token
- Session token validation fails because:
  - Session doesn't exist in Runtime (never created)
  - OR session token format doesn't match what Security Guard SDK expects

**Evidence:**
```python
# runtime_agent_websocket.py line 135-138
auth_result = await security_guard.validate_token(session_token)
if not auth_result:
    await websocket.close(code=1008, reason="Invalid session token")
```

#### Issue 4: Frontend Connecting Before Platform Ready

**Error:** `Max reconnect attempts reached` (before login)

**Root Cause:**
- Frontend is trying to establish WebSocket connection on page load
- This happens before user authentication
- No valid session exists, so connection fails
- Frontend retries 5 times, exhausting attempts

---

## 4. Strategic & Holistic Solution

### Phase 1: Fix Immediate Routing Issues

**Priority: CRITICAL**

1. **Fix Traefik Routing:**
   ```yaml
   # Add /api/session to Experience router
   - traefik.http.routers.experience.rule=PathPrefix(`/api/sessions`) || PathPrefix(`/api/session`) || ...
   ```

2. **Verify Session Endpoints:**
   - `/api/session/create` → Experience service
   - `/api/session/{session_id}` → Experience service

### Phase 2: Fix Session Lifecycle

**Priority: CRITICAL**

**Problem:** Frontend is generating session tokens, but sessions don't exist in Runtime.

**Solution:** Sessions must be created server-side via Traffic Cop SDK.

**Required Changes:**

1. **Frontend: Remove Client-Side Session Generation**
   - Don't generate session tokens in frontend
   - Wait for session_token from login response

2. **Backend: Ensure Login Creates Session**
   ```python
   # In /api/auth/login endpoint
   # After authentication:
   1. Authenticate user (Security Guard SDK)
   2. Create session via Traffic Cop SDK → Runtime
   3. Return session_token in login response
   ```

3. **Frontend: Use Session from Login**
   ```typescript
   // After successful login
   const { session_token } = await login(email, password);
   // Store session_token
   // THEN connect WebSocket
   ```

### Phase 3: Fix WebSocket Connection Timing

**Priority: HIGH**

**Problem:** Frontend connects WebSocket before authentication.

**Solution:** Defer WebSocket connection until after successful login.

**Required Changes:**

1. **Frontend: Conditional WebSocket Connection**
   ```typescript
   // Only connect WebSocket if:
   // 1. User is authenticated
   // 2. Valid session_token exists
   // 3. Session exists in Runtime
   
   if (isAuthenticated && sessionToken && sessionExists) {
     connectWebSocket();
   }
   ```

2. **Backend: Validate Session Before WebSocket**
   - Current code validates token (good)
   - But should also verify session exists in Runtime
   - Return 403 if session doesn't exist

### Phase 4: Architectural Alignment

**Priority: MEDIUM**

**Ensure the flow matches the architecture:**

1. **Login Flow:**
   ```
   Frontend → POST /api/auth/login
   Experience → Security Guard SDK (authenticate)
   Experience → Traffic Cop SDK (create session intent)
   Traffic Cop → Runtime (create session)
   Runtime → Returns session_id
   Experience → Returns session_token to frontend
   ```

2. **WebSocket Flow:**
   ```
   Frontend → ws://.../api/runtime/agent?session_token=...
   Experience → Security Guard SDK (validate token)
   Experience → Runtime (verify session exists)
   Experience → Accept connection
   ```

---

## 5. Questions for CTO

### Critical Questions

1. **Session Token Format:**
   - What format should session tokens be?
   - Should they be the session_id from Runtime?
   - Or a separate JWT/opaque token?

2. **Session Creation Timing:**
   - Should sessions be created during login?
   - Or should they be created on-demand when needed?
   - What's the intended lifecycle?

3. **Frontend Session Management:**
   - Should frontend generate session tokens?
   - Or should all sessions be server-side only?
   - What's the expected frontend pattern?

4. **WebSocket Connection Timing:**
   - Should WebSocket connect immediately on page load?
   - Or only after user authentication?
   - What's the expected UX flow?

5. **Session Validation:**
   - Should WebSocket validate session exists in Runtime?
   - Or just validate token format?
   - What's the security model?

6. **State Surface Integration:**
   - How does State Surface relate to sessions?
   - Should sessions be stored in State Surface?
   - Or separate storage?

### Architecture Questions

7. **Traffic Cop SDK:**
   - Is Traffic Cop SDK fully implemented?
   - Does it properly create sessions in Runtime?
   - Are there any known issues?

8. **Security Guard SDK:**
   - Does token validation check Runtime for session existence?
   - Or just validate token format/signature?
   - What's the validation flow?

9. **Runtime Session Storage:**
   - Where are sessions stored in Runtime?
   - Redis? ArangoDB? State Surface?
   - How are they queried?

10. **Error Handling:**
    - What should happen if session creation fails?
    - What should happen if WebSocket validation fails?
    - What's the recovery flow?

---

## Recommended Immediate Actions

### ✅ Action 1: Fix Traefik Routing (COMPLETED)
- ✅ Added `/api/session` to Experience router
- ✅ Restart Traefik
- ✅ Test: `curl http://localhost:80/api/session/create` → Returns 401 (expected, needs auth)

### Action 2: Verify Session Creation Flow (15 minutes)
- Check if `/api/auth/login` creates sessions
- Verify Traffic Cop SDK is called
- Verify Runtime receives session creation request
- **Current Issue:** Login doesn't create sessions - frontend calls `createSession()` separately

### Action 3: Fix Frontend Session Management (30 minutes)
- **Current Issue:** Frontend calls `createSession()` after login, but this may fail
- **Solution:** Either:
  - Option A: Login should create session automatically (backend)
  - Option B: Frontend should call `/api/session/create` after login (needs auth token)
- Defer WebSocket connection until after session exists

### Action 4: Add Session Validation (30 minutes)
- Verify session exists in Runtime before WebSocket accept
- Return clear error if session doesn't exist
- Log validation failures for debugging
- **Current Issue:** WebSocket validates token but doesn't verify session exists in Runtime

---

## Success Criteria

✅ **Sessions:**
- `/api/session/create` returns 200 (not 404)
- `/api/session/{session_id}` returns 200 (not 404)
- Sessions exist in Runtime after login

✅ **WebSocket:**
- Connection succeeds after login
- No 403 errors
- No "session not found" errors

✅ **Frontend:**
- No connection attempts before login
- WebSocket connects only after authentication
- No "max reconnect attempts" errors

---

**Last Updated:** January 23, 2026
