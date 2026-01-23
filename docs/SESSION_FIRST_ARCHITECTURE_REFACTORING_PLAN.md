# Session-First Architecture Refactoring Plan

**Date:** January 23, 2026  
**Status:** 📋 **PLANNING**  
**Priority:** 🔴 **CRITICAL**

---

## Executive Summary

We've been implementing authentication-first architecture, which creates circular dependencies and deadlocks. The correct pattern is **session-first, authentication-upgrades-session**.

**Key Insight:**
> **A session is required to authenticate. Authentication is not required to start a session.**

---

## The Correct Architecture Pattern

### Three Layers (Not Two)

1. **Interaction Session** (always exists, created on page load)
   - Discovery context
   - UI state
   - Provisional answers
   - Journey progress
   - Ephemeral, non-authoritative, non-privileged

2. **Identity** (optional, attached via authentication)
   - `user_id`
   - `tenant_id`
   - Roles
   - Policy context

3. **Authorization** (policy-bound, activated after authentication)
   - Smart City policies
   - Data Steward rules
   - Artifact promotion
   - Persistence permissions

### Flow

```
Page Load → Anonymous Session Created → User Interacts → Authentication → Session Upgraded → Authorization Activated
```

**NOT:**
```
Page Load → Authentication Required → Session Created (DEADLOCK)
```

---

## Current Problems (What We Need to Fix)

### 1. PlatformStateProvider - Blocking Session Loading Before Auth

**Current (WRONG):**
- Checks for `access_token` before loading session
- Clears session data if no `access_token`
- Prevents session creation before authentication

**Should Be:**
- Creates/loads anonymous session immediately on page load
- Session exists regardless of authentication
- Authentication upgrades session (adds `user_id`, `tenant_id`)

### 2. ExperiencePlaneClient.getSession() - Requiring Auth

**Current (WRONG):**
- Throws error if no `access_token`
- Prevents session API calls before authentication

**Should Be:**
- Allows session API calls without authentication
- Returns anonymous session if no auth
- Returns authenticated session if auth exists

### 3. AuthProvider - Creating Session After Login

**Current (PARTIALLY WRONG):**
- Creates session only after successful login
- Session creation depends on authentication

**Should Be:**
- Session should already exist (created on page load)
- Authentication **upgrades** existing session
- Adds `user_id`, `tenant_id` to existing session

### 4. Backend Session Creation - Requiring Authentication

**Current (NEEDS REVIEW):**
- Need to verify if backend allows anonymous session creation
- May need endpoint that creates session without auth

**Should Be:**
- Endpoint to create anonymous session (no auth required)
- Endpoint to upgrade session with authentication (requires auth)

---

## Refactoring Plan

### Phase 1: Backend - Anonymous Session Support

#### 1.1 Review Current Session Creation Endpoint

**File:** `symphainy_platform/civic_systems/experience/api/sessions.py`

**Current State:**
- `/api/session/create` - May require authentication
- Need to verify if it allows anonymous sessions

**Action Items:**
1. Review `create_session` endpoint
2. Check if it accepts `user_id=None`, `tenant_id=None`
3. If not, create new endpoint `/api/session/create-anonymous` OR modify existing to allow anonymous

#### 1.2 Runtime Session Creation

**File:** `symphainy_platform/runtime/runtime_api.py`

**Current State:**
- `create_session` may require `user_id`, `tenant_id`

**Action Items:**
1. Modify to allow `user_id=None`, `tenant_id=None` for anonymous sessions
2. Update validation to allow anonymous sessions
3. Ensure session can be upgraded later (add `user_id`, `tenant_id`)

#### 1.3 Traffic Cop SDK - Anonymous Session Intents

**File:** `symphainy_platform/civic_systems/smart_city/sdk/traffic_cop_sdk.py`

**Current State:**
- `create_session_intent` may require `user_id`, `tenant_id`

**Action Items:**
1. Allow `user_id=None`, `tenant_id=None` for anonymous sessions
2. Create execution contract for anonymous sessions
3. Allow session upgrade (add identity later)

---

### Phase 2: Frontend - Session-First Pattern

#### 2.1 PlatformStateProvider - Create Anonymous Session on Mount

**File:** `symphainy-frontend/shared/state/PlatformStateProvider.tsx`

**Current (WRONG):**
```typescript
// Checks for access_token before loading session
if (!accessToken) {
  // Clear session data - WRONG!
  return;
}
```

**Should Be:**
```typescript
// Always create/load session on mount (anonymous or authenticated)
useEffect(() => {
  // Check if session already exists
  const existingSessionId = sessionStorage.getItem("session_id");
  
  if (existingSessionId) {
    // Load existing session (anonymous or authenticated)
    loadSession(existingSessionId);
  } else {
    // Create new anonymous session
    createAnonymousSession();
  }
}, []);
```

**Action Items:**
1. Remove all `access_token` checks before session loading
2. Create anonymous session on mount if none exists
3. Load existing session regardless of auth status
4. Upgrade session when authentication happens (via AuthProvider callback)

#### 2.2 ExperiencePlaneClient - Allow Anonymous Session Calls

**File:** `symphainy-frontend/shared/services/ExperiencePlaneClient.ts`

**Current (WRONG):**
```typescript
async getSession(sessionId: string, tenantId: string): Promise<Session> {
  if (!accessToken) {
    throw new Error("Cannot get session: user is not authenticated");
  }
  // ...
}
```

**Should Be:**
```typescript
async getSession(sessionId: string, tenantId?: string): Promise<Session> {
  // Allow session calls without authentication
  // tenantId is optional for anonymous sessions
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  // Add Authorization header if access_token exists (optional)
  const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  
  // Make API call regardless of auth status
  // ...
}
```

**Action Items:**
1. Remove `access_token` requirement from `getSession()`
2. Make `tenantId` optional (anonymous sessions don't have tenant)
3. Add `createAnonymousSession()` method
4. Add `upgradeSession()` method (called after authentication)

#### 2.3 AuthProvider - Upgrade Session on Login

**File:** `symphainy-frontend/shared/auth/AuthProvider.tsx`

**Current (PARTIALLY WRONG):**
```typescript
// Creates session after login
const sessionId = await createSession(tenantId, userId, {...});
```

**Should Be:**
```typescript
// Session should already exist (created on page load)
// Upgrade existing session with authentication
const existingSessionId = sessionStorage.getItem("session_id");
if (existingSessionId) {
  await upgradeSession(existingSessionId, {
    user_id: userId,
    tenant_id: tenantId,
    // ...
  });
} else {
  // Fallback: create session if somehow missing (shouldn't happen)
  await createSession(tenantId, userId, {...});
}
```

**Action Items:**
1. Check for existing session before creating new one
2. Add `upgradeSession()` method to PlatformStateProvider
3. Call `upgradeSession()` after successful login
4. Update session state with `user_id`, `tenant_id` after upgrade

#### 2.4 Remove All "Access Token Required" Guards

**Files to Update:**
- `symphainy-frontend/shared/state/PlatformStateProvider.tsx`
- `symphainy-frontend/shared/services/ExperiencePlaneClient.ts`
- `symphainy-frontend/shared/services/UnifiedServiceLayer.ts`
- `symphainy-frontend/shared/agui/GuideAgentProvider.tsx`
- Any other files that check `access_token` before session operations

**Action Items:**
1. Remove all `if (!accessToken) return;` guards from session loading
2. Remove all `access_token` checks before `getSession()` calls
3. Keep `access_token` checks only for:
   - Protected API endpoints (not session endpoints)
   - Authorization decisions (not session loading)
   - WebSocket authentication (still requires auth)

---

### Phase 3: Redirect Logic (Keep This)

#### 3.1 AuthRedirect Component

**File:** `symphainy-frontend/components/auth/auth-redirect.tsx`

**Current (CORRECT):**
- Redirects unauthenticated users to `/login`
- This is correct - we want redirects, but session should still exist

**Action Items:**
- No changes needed
- Session exists, but user is redirected if not authenticated

#### 3.2 Protected Routes

**File:** `symphainy-frontend/app/(protected)/layout.tsx`

**Current (CORRECT):**
- Uses `MainLayout` which may check authentication
- This is fine - redirect logic is separate from session creation

**Action Items:**
- Verify redirect happens AFTER session is created
- Session should exist even on login page (for continuity)

---

### Phase 4: Session Upgrade Flow

#### 4.1 Backend - Session Upgrade Endpoint

**New Endpoint:** `PATCH /api/session/{session_id}/upgrade`

**Request:**
```json
{
  "user_id": "user_123",
  "tenant_id": "tenant_456",
  "metadata": {
    "authenticated_at": "2026-01-23T..."
  }
}
```

**Response:**
```json
{
  "session_id": "session_789",
  "user_id": "user_123",
  "tenant_id": "tenant_456",
  "upgraded_at": "2026-01-23T..."
}
```

**Action Items:**
1. Create new endpoint in `sessions.py`
2. Update Runtime to allow session upgrade
3. Validate that session exists before upgrade
4. Add `user_id`, `tenant_id` to existing session

#### 4.2 Frontend - Session Upgrade Method

**File:** `symphainy-frontend/shared/state/PlatformStateProvider.tsx`

**New Method:**
```typescript
const upgradeSession = useCallback(async (
  sessionId: string,
  userData: { user_id: string; tenant_id: string; metadata?: Record<string, any> }
): Promise<void> => {
  // Call backend to upgrade session
  await client.upgradeSession(sessionId, userData);
  
  // Update local state
  setState((prev) => ({
    ...prev,
    session: {
      ...prev.session,
      sessionId,
      userId: userData.user_id,
      tenantId: userData.tenant_id,
    },
  }));
  
  // Update sessionStorage
  sessionStorage.setItem("user_id", userData.user_id);
  sessionStorage.setItem("tenant_id", userData.tenant_id);
}, [client]);
```

**Action Items:**
1. Add `upgradeSession()` to PlatformStateProvider
2. Add `upgradeSession()` to ExperiencePlaneClient
3. Call from AuthProvider after successful login

---

## Implementation Order

### Step 1: Backend Anonymous Session Support
1. Review and modify session creation to allow anonymous
2. Create session upgrade endpoint
3. Test anonymous session creation
4. Test session upgrade

### Step 2: Frontend Session-First Pattern
1. Remove all `access_token` guards from session loading
2. Create anonymous session on page load
3. Load existing session regardless of auth
4. Test anonymous session works

### Step 3: Session Upgrade Flow
1. Implement backend upgrade endpoint
2. Implement frontend upgrade method
3. Call upgrade from AuthProvider after login
4. Test session upgrade flow

### Step 4: Cleanup
1. Remove all "fixes" that prevented session loading before auth
2. Update documentation
3. Test full flow: anonymous → login → upgraded session

---

## Files to Modify

### Backend
- `symphainy_platform/civic_systems/experience/api/sessions.py` - Allow anonymous, add upgrade
- `symphainy_platform/runtime/runtime_api.py` - Allow anonymous sessions
- `symphainy_platform/civic_systems/smart_city/sdk/traffic_cop_sdk.py` - Anonymous intents

### Frontend
- `symphainy-frontend/shared/state/PlatformStateProvider.tsx` - Session-first pattern
- `symphainy-frontend/shared/services/ExperiencePlaneClient.ts` - Remove auth guards
- `symphainy-frontend/shared/auth/AuthProvider.tsx` - Upgrade instead of create
- `symphainy-frontend/shared/state/AppProviders.tsx` - Provider order (may need adjustment)

---

## Testing Strategy

### Test 1: Anonymous Session Creation
1. Clear all storage
2. Load page (not logged in)
3. Verify session is created automatically
4. Verify session_id is in sessionStorage
5. Verify no API errors

### Test 2: Session Persistence
1. Create anonymous session
2. Interact with UI (add data, navigate)
3. Refresh page
4. Verify session persists
5. Verify data is still there

### Test 3: Session Upgrade
1. Create anonymous session
2. Login
3. Verify session_id doesn't change
4. Verify user_id, tenant_id are added
5. Verify session is now "authenticated"

### Test 4: Redirect with Session
1. Create anonymous session
2. Navigate to protected route
3. Verify redirect to login
4. Verify session still exists after redirect
5. Login
6. Verify redirect back to protected route
7. Verify session is upgraded

---

## Key Principles (Write These Down)

1. **Session is required to authenticate. Authentication is not required to start a session.**
2. **Sessions are about continuity of thought. Authentication is about responsibility for outcomes.**
3. **Anonymous sessions are ephemeral, non-authoritative, non-privileged.**
4. **Authentication upgrades sessions, it doesn't create them.**
5. **Authorization gates apply after authentication, not before session creation.**

---

## Current Backend State (Analysis)

### Session Creation Endpoint (`/api/session/create`)
**File:** `symphainy_platform/civic_systems/experience/api/sessions.py`

**Current Flow:**
1. Requires authentication via `security_guard_sdk.authenticate(request.credentials)`
2. Gets `tenant_id` and `user_id` from auth result
3. Creates session intent via Traffic Cop SDK
4. Submits to Runtime

**Problem:** Cannot create anonymous sessions - requires authentication first.

### Runtime Session Creation
**File:** `symphainy_platform/runtime/runtime_api.py`

**Current State:**
- `SessionCreateRequest` requires:
  - `tenant_id: str` (required)
  - `user_id: str` (required)
- Session state stores `tenant_id` and `user_id`

**Problem:** Cannot create sessions without `tenant_id` and `user_id`.

### Traffic Cop SDK
**File:** `symphainy_platform/civic_systems/smart_city/sdk/traffic_cop_sdk.py`

**Current State:**
- `create_session_intent()` requires:
  - `tenant_id: str`
  - `user_id: str`

**Problem:** Cannot create anonymous session intents.

---

## Implementation Plan

### Phase 1: Backend - Anonymous Session Support

#### 1.1 Create Anonymous Session Endpoint

**New Endpoint:** `POST /api/session/create-anonymous`

**File:** `symphainy_platform/civic_systems/experience/api/sessions.py`

**Implementation:**
```python
@router.post("/create-anonymous", response_model=SessionCreateResponse)
async def create_anonymous_session(
    request: Optional[Dict[str, Any]] = None,
    runtime_client: RuntimeClient = Depends(get_runtime_client),
    traffic_cop_sdk: TrafficCopSDK = Depends(get_traffic_cop_sdk)
):
    """
    Create anonymous session (no authentication required).
    
    Flow:
    1. Prepare anonymous session intent (via Traffic Cop SDK)
    2. Submit intent to Runtime
    3. Runtime validates and creates anonymous session
    4. Return session_id
    """
    try:
        # Create anonymous session intent (no tenant_id, user_id)
        session_intent_data = await traffic_cop_sdk.create_anonymous_session_intent(
            metadata=request.get("metadata") if request else None
        )
        
        # Convert to dict for Runtime
        session_intent = {
            "intent_type": "create_session",
            "tenant_id": None,  # Anonymous - no tenant
            "user_id": None,    # Anonymous - no user
            "session_id": session_intent_data.session_id,
            "execution_contract": session_intent_data.execution_contract,
            "metadata": (request.get("metadata") if request else {}) or {}
        }
        
        # Submit to Runtime
        result = await runtime_client.create_anonymous_session(session_intent)
        
        session_id = result.get("session_id") or session_intent_data.session_id
        
        return SessionCreateResponse(
            session_id=session_id,
            tenant_id="",  # Empty for anonymous
            user_id="",    # Empty for anonymous
            created_at=result.get("created_at", "")
        )
    except Exception as e:
        logger.error(f"Failed to create anonymous session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
```

#### 1.2 Traffic Cop SDK - Anonymous Session Intents

**File:** `symphainy_platform/civic_systems/smart_city/sdk/traffic_cop_sdk.py`

**New Method:**
```python
async def create_anonymous_session_intent(
    self,
    metadata: Optional[Dict[str, Any]] = None
) -> SessionIntent:
    """
    Create anonymous session intent (no authentication required).
    
    Returns:
        SessionIntent with session_id, execution_contract (no tenant_id, user_id)
    """
    # Generate session_id
    session_id = f"session_anonymous_{uuid.uuid4().hex}_{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')}"
    
    # Create execution contract for anonymous session
    execution_contract = {
        "session_type": "anonymous",
        "created_at": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    return SessionIntent(
        session_id=session_id,
        tenant_id=None,  # Anonymous
        user_id=None,    # Anonymous
        execution_contract=execution_contract,
        metadata=metadata or {}
    )
```

#### 1.3 Runtime - Anonymous Session Support

**File:** `symphainy_platform/runtime/runtime_api.py`

**Modify `SessionCreateRequest`:**
```python
class SessionCreateRequest(BaseModel):
    """Request to create a session."""
    intent_type: str = "create_session"
    tenant_id: Optional[str] = None  # Optional for anonymous sessions
    user_id: Optional[str] = None   # Optional for anonymous sessions
    session_id: Optional[str] = None
    execution_contract: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
```

**New Method:**
```python
async def create_anonymous_session(
    self,
    request: SessionCreateRequest
) -> SessionCreateResponse:
    """
    Create anonymous session (no tenant_id, user_id required).
    
    Similar to create_session but allows None for tenant_id and user_id.
    """
    # Same logic as create_session but allows None values
    # ...
```

**Modify `create_session` to handle None values:**
```python
# In create_session method:
session_state = {
    "session_id": session_id,
    "tenant_id": request.tenant_id or None,  # Allow None
    "user_id": request.user_id or None,      # Allow None
    "execution_contract": execution_contract,
    "metadata": request.metadata or {},
    "created_at": datetime.now().isoformat(),
    "status": "active",
    "is_anonymous": request.tenant_id is None or request.user_id is None
}
```

#### 1.4 Session Upgrade Endpoint

**New Endpoint:** `PATCH /api/session/{session_id}/upgrade`

**File:** `symphainy_platform/civic_systems/experience/api/sessions.py`

**Implementation:**
```python
@router.patch("/{session_id}/upgrade", response_model=SessionCreateResponse)
async def upgrade_session(
    session_id: str,
    request: Dict[str, Any],  # { user_id, tenant_id, metadata }
    runtime_client: RuntimeClient = Depends(get_runtime_client),
    security_guard_sdk: SecurityGuardSDK = Depends(get_security_guard_sdk)
):
    """
    Upgrade anonymous session with authentication.
    
    Flow:
    1. Validate access_token (user is authenticated)
    2. Get existing session (must be anonymous)
    3. Update session with user_id, tenant_id
    4. Return upgraded session
    """
    # 1. Validate authentication
    access_token = request.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token required")
    
    auth_result = await security_guard_sdk.validate_token(access_token)
    if not auth_result:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    # 2. Get existing session
    session_data = await runtime_client.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # 3. Upgrade session (add user_id, tenant_id)
    upgraded = await runtime_client.upgrade_session(
        session_id=session_id,
        user_id=auth_result.user_id,
        tenant_id=auth_result.tenant_id,
        metadata=request.get("metadata")
    )
    
    return SessionCreateResponse(
        session_id=session_id,
        tenant_id=auth_result.tenant_id,
        user_id=auth_result.user_id,
        created_at=upgraded.get("created_at", "")
    )
```

**Runtime Method:**
```python
async def upgrade_session(
    self,
    session_id: str,
    user_id: str,
    tenant_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Upgrade anonymous session with user_id and tenant_id.
    """
    # Get existing session
    session_state = await self.state_surface.get_session_state(session_id, None)  # No tenant for anonymous
    if not session_state:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Update session state
    session_state["user_id"] = user_id
    session_state["tenant_id"] = tenant_id
    session_state["is_anonymous"] = False
    session_state["upgraded_at"] = datetime.now().isoformat()
    if metadata:
        session_state["metadata"].update(metadata)
    
    # Store updated session (now with tenant_id)
    await self.state_surface.set_session_state(
        session_id=session_id,
        tenant_id=tenant_id,  # Now has tenant_id
        state=session_state
    )
    
    return session_state
```

---

### Phase 2: Frontend - Session-First Pattern

#### 2.1 PlatformStateProvider - Create Anonymous Session on Mount

**File:** `symphainy-frontend/shared/state/PlatformStateProvider.tsx`

**Remove:**
- All `access_token` checks before session loading
- All session clearing when no `access_token`
- All "authentication required" guards

**Add:**
```typescript
// Create/load session on mount (anonymous or authenticated)
useEffect(() => {
  const initializeSession = async () => {
    // Check if session already exists
    const existingSessionId = typeof window !== 'undefined' 
      ? sessionStorage.getItem("session_id") 
      : null;
    
    if (existingSessionId) {
      // Load existing session (anonymous or authenticated)
      try {
        const session = await client.getSession(existingSessionId);
        if (session) {
          setState((prev) => ({
            ...prev,
            session: {
              sessionId: session.session_id,
              tenantId: session.tenant_id || null,
              userId: session.user_id || null,
              session,
              isLoading: false,
              error: null,
            },
          }));
        }
      } catch (error) {
        // Session doesn't exist or error - create new anonymous session
        await createAnonymousSession();
      }
    } else {
      // No existing session - create new anonymous session
      await createAnonymousSession();
    }
  };
  
  initializeSession();
}, [client]);

const createAnonymousSession = useCallback(async () => {
  try {
    setState((prev) => ({
      ...prev,
      session: { ...prev.session, isLoading: true, error: null },
    }));
    
    const response = await client.createAnonymousSession();
    
    setState((prev) => ({
      ...prev,
      session: {
        sessionId: response.session_id,
        tenantId: null,  // Anonymous
        userId: null,    // Anonymous
        session: {
          session_id: response.session_id,
          tenant_id: null,
          user_id: null,
          created_at: response.created_at,
          metadata: {},
        },
        isLoading: false,
        error: null,
      },
    }));
    
    // Store in sessionStorage
    if (typeof window !== 'undefined') {
      sessionStorage.setItem("session_id", response.session_id);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Failed to create session";
    setState((prev) => ({
      ...prev,
      session: { ...prev.session, isLoading: false, error: errorMessage },
    }));
  }
}, [client]);
```

#### 2.2 ExperiencePlaneClient - Remove Auth Guards

**File:** `symphainy-frontend/shared/services/ExperiencePlaneClient.ts`

**Remove:**
```typescript
// REMOVE THIS:
if (!accessToken) {
  throw new Error("Cannot get session: user is not authenticated");
}
```

**Add:**
```typescript
async createAnonymousSession(): Promise<SessionCreateResponse> {
  const url = getApiEndpointUrl(`/api/session/create-anonymous`);
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({}),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to create anonymous session' }));
    throw new Error(error.detail || `Failed to create anonymous session: ${response.statusText}`);
  }
  
  return await response.json();
}

async upgradeSession(
  sessionId: string,
  userData: { user_id: string; tenant_id: string; access_token: string; metadata?: Record<string, any> }
): Promise<Session> {
  const url = getApiEndpointUrl(`/api/session/${sessionId}/upgrade`);
  
  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userData.access_token}`,
    },
    body: JSON.stringify({
      user_id: userData.user_id,
      tenant_id: userData.tenant_id,
      metadata: userData.metadata,
    }),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to upgrade session' }));
    throw new Error(error.detail || `Failed to upgrade session: ${response.statusText}`);
  }
  
  const data = await response.json();
  return {
    session_id: data.session_id,
    tenant_id: data.tenant_id,
    user_id: data.user_id,
    created_at: data.created_at,
    metadata: data.metadata || {},
  };
}
```

**Modify `getSession`:**
```typescript
async getSession(sessionId: string, tenantId?: string): Promise<Session> {
  // REMOVE access_token requirement
  // Allow session calls without authentication
  const url = getApiEndpointUrl(`/api/session/${sessionId}`);
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  // Add Authorization header if access_token exists (optional)
  const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers,
  });
  
  // ... rest of method
}
```

#### 2.3 AuthProvider - Upgrade Session Instead of Create

**File:** `symphainy-frontend/shared/auth/AuthProvider.tsx`

**Modify `login` method:**
```typescript
// After successful authentication:
const existingSessionId = typeof window !== 'undefined' 
  ? sessionStorage.getItem("session_id") 
  : null;

if (existingSessionId) {
  // Upgrade existing anonymous session
  try {
    await upgradeSession(existingSessionId, {
      user_id: userId,
      tenant_id: tenantId,
      access_token: accessToken,
      metadata: {
        email: userEmail,
        authenticated_at: new Date().toISOString(),
      },
    });
    
    // Session is now upgraded - no need to create new one
    sessionId = existingSessionId;
  } catch (upgradeError) {
    console.error("Failed to upgrade session, creating new one:", upgradeError);
    // Fallback: create new session if upgrade fails
    sessionId = await createSession(tenantId, userId, {...});
  }
} else {
  // No existing session - create new one (shouldn't happen, but fallback)
  sessionId = await createSession(tenantId, userId, {...});
}
```

**Add `upgradeSession` method:**
```typescript
const upgradeSession = useCallback(async (
  sessionId: string,
  userData: { user_id: string; tenant_id: string; access_token: string; metadata?: Record<string, any> }
): Promise<void> => {
  // Call PlatformStateProvider's upgradeSession
  // This will call ExperiencePlaneClient.upgradeSession
  // ...
}, []);
```

---

## Questions to Answer

1. **Backend:** Does `/api/session/create` currently allow anonymous sessions?
   - **Answer:** NO - it requires authentication via `security_guard_sdk.authenticate()`

2. **Backend:** Do we need a separate endpoint for anonymous vs authenticated session creation?
   - **Answer:** YES - Create `/api/session/create-anonymous` for anonymous, keep `/api/session/create` for authenticated

3. **Backend:** Can Runtime handle sessions without `user_id`/`tenant_id`?
   - **Answer:** NEEDS MODIFICATION - Currently requires both. Need to make Optional.

4. **Frontend:** Should anonymous sessions expire? If so, when?
   - **Answer:** TBD - Recommend 24 hours or on browser close (sessionStorage)

5. **Frontend:** Should we show different UI for anonymous vs authenticated sessions?
   - **Answer:** TBD - For MVP, same UI but redirect to login for protected actions

---

**Next Steps:**
1. ✅ Review backend session creation endpoints (DONE)
2. ⏳ Implement anonymous session support (backend)
3. ⏳ Refactor frontend to session-first pattern
4. ⏳ Test and validate

---

**Last Updated:** January 23, 2026
