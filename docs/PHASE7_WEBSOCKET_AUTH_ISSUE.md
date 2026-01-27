# Phase 7: WebSocket Authentication Issue - Root Cause Analysis

**Date:** January 24, 2026  
**Status:** 🔍 **ROOT CAUSE IDENTIFIED**

---

## Issue Summary

WebSocket connections to `/api/runtime/agent` are failing with **403 Forbidden**.

**Error:**
```
WebSocket connection to 'ws://35.215.64.103/api/runtime/agent?session_token=...' failed: 
Error during WebSocket handshake: Unexpected response code: 403
```

**Backend Logs:**
```
INFO: connection rejected (403 Forbidden)
INFO: WebSocket /api/runtime/agent?session_token=... 403
```

---

## Root Cause

### The Architecture Mismatch

**Architecture States:**
1. **Anonymous sessions should NOT connect to WebSocket**
2. **WebSocket requires Active (authenticated) session**
3. **WebSocket authentication uses `access_token` (JWT from Supabase)**
4. **`session_id` is for session state, not authentication**

**Current Implementation:**
1. Frontend creates anonymous session on page load ✅
2. Frontend tries to connect WebSocket with `session_id` as `session_token` ❌
3. Backend tries to validate `session_id` as JWT access token ❌
4. SecurityGuard rejects it (not a valid JWT) → 403 ❌

---

## The Flow (What Should Happen)

### Correct Flow
```
1. Page Load → SessionBoundaryProvider creates Anonymous session
2. User on login page (no WebSocket connection yet)
3. User logs in → Authentication succeeds → Session upgraded to Active
4. GuideAgentProvider checks SessionStatus === Active
5. GuideAgentProvider creates RuntimeClient with:
   - accessToken: JWT from Supabase (for authentication)
   - sessionId: Session ID (for session state)
6. RuntimeClient connects WebSocket with BOTH parameters
7. Backend validates accessToken (JWT) for authentication ✅
8. Backend uses sessionId for session state ✅
```

### Current Incorrect Flow
```
1. Page Load → SessionBoundaryProvider creates Anonymous session
2. User on login page
3. Some component tries to connect WebSocket immediately ❌
4. RuntimeClient uses sessionId as "session_token" ❌
5. Backend tries to validate sessionId as JWT ❌
6. SecurityGuard rejects (not a JWT) → 403 ❌
```

---

## The Fix

### Issue 1: Frontend Connecting WebSocket Before Authentication

**Problem:** Something in the frontend is trying to connect WebSocket before the user is authenticated.

**Check:**
- GuideAgentProvider line 497: `if (sessionState.status === SessionStatus.Active && sessionToken)`
- This SHOULD prevent connection before Active status
- But WebSocket is still being attempted on login page

**Hypothesis:** 
- The sessionToken exists (from anonymous session)
- The status might be transitioning to Active prematurely
- OR there's another component creating RuntimeClient

### Issue 2: Backend Expecting JWT for WebSocket Auth

**Problem:** Backend `security_guard.validate_token()` expects a JWT (access token), not a session_id.

**Current Backend Code:**
```python
# Line 139
auth_result = await security_guard.validate_token(auth_token)
```

**What `validate_token()` Does:**
- Validates JWT access token from Supabase
- Expects format: `eyJ...` (JWT)
- Rejects session_id format: `session_5d945c64...`

**Solution:** Backend should:
1. Accept `access_token` for authentication
2. Accept `session_id` for session state
3. Validate `access_token` with SecurityGuard
4. Use `session_id` for session operations
5. NOT try to validate `session_id` as a JWT

---

## The Fixes Required

### Fix 1: Backend - Separate Authentication from Session State

**File:** `symphainy_platform/civic_systems/experience/api/runtime_agent_websocket.py`

**Current (Line 76-78):**
```python
session_token: Optional[str] = Query(None),
access_token: Optional[str] = Query(None),
session_id: Optional[str] = Query(None)
```

**Issue:** Using `session_token` parameter but then mixing it with validation logic

**Solution:**
```python
@router.websocket("/agent")
async def runtime_agent_websocket(
    websocket: WebSocket,
    access_token: Optional[str] = Query(None, description="JWT access token for authentication"),
    session_id: Optional[str] = Query(None, description="Session ID for session state")
):
    # Validate access_token for authentication
    if not access_token:
        await websocket.close(code=1008, reason="Access token required")
        return
    
    # Validate JWT access token
    auth_result = await security_guard.validate_token(access_token)
    if not auth_result:
        await websocket.close(code=1008, reason="Invalid access token")
        return
    
    user_id = auth_result.user_id
    tenant_id = auth_result.tenant_id
    
    # Use session_id for session state (NOT for authentication)
    ws_session_id = session_id or f"session_{user_id}_{tenant_id}"
```

### Fix 2: Frontend - Ensure WebSocket Only Connects When Authenticated

**File:** `symphainy-frontend/shared/agui/GuideAgentProvider.tsx`

**Check Line 497:**
```typescript
if (sessionState.status === SessionStatus.Active && sessionToken) {
```

**This should be correct**, but verify:
1. `sessionState.status` is NOT `Active` until after authentication
2. `sessionToken` is NOT set until after authentication
3. No other component is creating RuntimeClient

### Fix 3: Frontend - Send Correct Parameters

**File:** `symphainy-frontend/shared/services/RuntimeClient.ts`

**Current Line 357:**
```typescript
return `${protocol}://${baseUrl}/api/runtime/agent?access_token=${accessToken}&session_token=${sessionId}`;
```

**Should Be:**
```typescript
return `${protocol}://${baseUrl}/api/runtime/agent?access_token=${accessToken}&session_id=${sessionId}`;
```

**Change:** `session_token` → `session_id` to match backend expectations

---

## Summary

**Root Cause:** Parameter naming and validation mismatch between frontend and backend.

**Frontend sends:** `session_token` = session_id  
**Backend validates:** `session_token` as JWT access token ❌  
**Should be:** Backend validates `access_token` as JWT, uses `session_id` for state ✅

**Status:** Fixes identified, need to apply all three fixes and restart services.

---

## Action Items

1. ✅ Update backend WebSocket to validate `access_token` (not `session_token` or `session_id`)
2. ⏳ Update frontend RuntimeClient to send `session_id` parameter (not `session_token`)
3. ⏳ Verify GuideAgentProvider only connects when `SessionStatus.Active`
4. ⏳ Restart experience service
5. ⏳ Rebuild and restart frontend
6. ⏳ Test WebSocket connection after login

---

**Next:** Apply remaining fixes and test.
