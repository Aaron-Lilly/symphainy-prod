# Critical Questions for CTO - WebSocket & Session Architecture

**Date:** January 23, 2026  
**Context:** Platform cannot launch due to WebSocket/session failures  
**Priority:** URGENT

---

## Executive Summary

The platform is experiencing a **cascade of failures** before users can even log in:

1. **Session endpoints returning 404** (`/api/session/create`, `/api/session/{session_id}`)
2. **WebSocket connections failing with 403** (authentication/authorization)
3. **Frontend trying to connect before sessions exist**
4. **Session tokens generated but sessions don't exist in Runtime**

This suggests a **fundamental architectural mismatch** between:
- How sessions are supposed to be created (Traffic Cop SDK → Runtime)
- How the frontend is trying to use them (client-side generation)
- How WebSocket authentication works (validates against Runtime)

---

## Critical Questions

### 1. Session Lifecycle & Creation

**Question:** When and how should sessions be created?

**Current Behavior:**
- Frontend calls `createSession()` after login (line 160 in AuthProvider.tsx)
- But `/api/session/create` returns 404 (routing issue)
- Sessions never get created in Runtime

**Expected Behavior (from architecture docs):**
- Login → Security Guard SDK (authenticate)
- Login → Traffic Cop SDK (create session intent)
- Traffic Cop → Runtime (create session)
- Return session_token

**Questions:**
- Should sessions be created **during login** (automatic)?
- Or should they be created **on-demand** when needed?
- What's the intended flow: Login → Session Creation → WebSocket Connection?

### 2. Session Token Format & Validation

**Question:** What format should session tokens be, and how are they validated?

**Current Behavior:**
- Frontend generates session tokens client-side
- WebSocket validates via `security_guard.validate_token(session_token)`
- Validation fails (403) because session doesn't exist

**Questions:**
- Should session tokens be the **session_id from Runtime**?
- Or should they be **separate JWT/opaque tokens**?
- Does `SecurityGuardSDK.validate_token()` check if session exists in Runtime?
- Or does it only validate token format/signature?

### 3. Frontend Session Management

**Question:** Should the frontend generate session tokens, or are they server-side only?

**Current Behavior:**
- Frontend calls `createSession()` after login
- This generates a session token client-side
- But the session doesn't exist in Runtime

**Questions:**
- Should **all sessions be server-side only**?
- Should login response include `session_token`?
- Or should frontend call `/api/session/create` after login?
- What's the expected frontend pattern?

### 4. WebSocket Connection Timing

**Question:** When should the WebSocket connect?

**Current Behavior:**
- Frontend tries to connect WebSocket on page load
- This happens **before login**
- No valid session exists, so connection fails
- Frontend retries 5 times, exhausting attempts

**Questions:**
- Should WebSocket connect **only after successful login**?
- Or should it connect on page load and wait for authentication?
- What's the expected UX flow?

### 5. Session Endpoint Routing

**Question:** Why are session endpoints returning 404?

**Current Behavior:**
- `/api/session/create` → 404
- `/api/session/{session_id}` → 404
- Endpoint exists in Experience service (`sessions.py`)
- But Traefik routing may not include `/api/session`

**Questions:**
- Should `/api/session/*` routes go to Experience service?
- Or should they go to Runtime service?
- What's the correct routing configuration?

### 6. Traffic Cop SDK Implementation

**Question:** Is Traffic Cop SDK fully implemented and working?

**Current Behavior:**
- Architecture docs say sessions should be created via Traffic Cop SDK
- But we're seeing 404 errors on session endpoints
- Not clear if Traffic Cop SDK is being called

**Questions:**
- Is Traffic Cop SDK fully implemented?
- Does it properly create sessions in Runtime?
- Are there any known issues or missing pieces?
- Should we be using Traffic Cop SDK, or direct Runtime API?

### 7. State Surface Integration

**Question:** How does State Surface relate to sessions?

**Current Behavior:**
- Architecture mentions State Surface for centralized state
- But sessions seem to be managed separately
- Not clear how they integrate

**Questions:**
- Should sessions be stored in State Surface?
- Or separate storage (Redis, ArangoDB)?
- How does State Surface relate to session lifecycle?
- Is State Surface fully implemented?

### 8. Runtime Session Storage

**Question:** Where are sessions stored in Runtime, and how are they queried?

**Current Behavior:**
- WebSocket tries to validate session
- But session doesn't exist
- Not clear where sessions should be stored

**Questions:**
- Where are sessions stored in Runtime? (Redis? ArangoDB? State Surface?)
- How does Runtime query sessions?
- What's the session data model?
- How are sessions retrieved for validation?

### 9. Authentication Middleware

**Question:** How does AuthenticationMiddleware relate to WebSocket authentication?

**Current Behavior:**
- Experience service has `AuthenticationMiddleware`
- WebSocket endpoint validates tokens directly
- Not clear if middleware applies to WebSocket

**Questions:**
- Does `AuthenticationMiddleware` apply to WebSocket endpoints?
- Or does WebSocket handle authentication separately?
- What's the intended authentication flow for WebSocket?

### 10. Error Recovery & User Experience

**Question:** What should happen when sessions/WebSocket fail?

**Current Behavior:**
- Frontend retries WebSocket 5 times
- Then gives up
- User sees errors before even logging in

**Questions:**
- What's the expected error recovery flow?
- Should frontend retry indefinitely?
- Or fail gracefully and show user message?
- What's the intended UX when things go wrong?

---

## Architecture Alignment Questions

### 11. Experience Plane vs Runtime

**Question:** What's the exact responsibility split for sessions?

**From Architecture Docs:**
- Experience Plane = Intent + Context Boundary
- Runtime = Execution Engine
- Experience Plane owns WebSocket endpoints

**Questions:**
- Should Experience Plane create sessions?
- Or should Runtime create sessions?
- Who owns session lifecycle management?
- What's the exact flow?

### 12. Session Intent Pattern

**Question:** Should session creation use the "intent" pattern?

**From Architecture Docs:**
- Traffic Cop SDK creates "session intent"
- Runtime validates via primitives
- Runtime creates session

**Questions:**
- Is this pattern fully implemented?
- Or should we use direct API calls?
- What's the current state of this pattern?

---

## Immediate Blockers

### Blocker 1: Session Endpoints Not Routed
- **Issue:** `/api/session/*` returning 404
- **Fix:** Add `/api/session` to Traefik routing
- **Status:** In progress

### Blocker 2: Frontend Creating Sessions Before They Exist
- **Issue:** Frontend generates session tokens, but sessions don't exist in Runtime
- **Fix:** Need to understand correct flow
- **Status:** Needs CTO input

### Blocker 3: WebSocket Authentication Failing
- **Issue:** 403 errors on WebSocket connection
- **Fix:** Need to understand token validation flow
- **Status:** Needs CTO input

### Blocker 4: Frontend Connecting Before Login
- **Issue:** WebSocket tries to connect before authentication
- **Fix:** Defer connection until after login
- **Status:** Can fix, but need to understand intended flow

---

## Recommended Next Steps

1. **Immediate:** Fix Traefik routing for `/api/session`
2. **Urgent:** Get CTO answers to questions above
3. **Critical:** Align frontend session management with backend architecture
4. **Critical:** Fix WebSocket connection timing
5. **Important:** Verify Traffic Cop SDK implementation

---

**Last Updated:** January 23, 2026
