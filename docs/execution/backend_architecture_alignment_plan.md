# Backend Architecture Alignment Plan

**Date:** January 2026  
**Status:** 📋 **PLAN READY** - Awaiting Backend Team Clarification

---

## 🎯 Executive Summary

After reviewing the platform architecture and "rules of the road", I've identified the correct approach to address the two gaps. The backend team's architecture follows clear patterns, and we need to align our implementation with their SDK design.

---

## 📐 Architecture Findings

### 1. Authentication Pattern ✅ **CLEAR**

**Backend Architecture:**
- **Security Guard SDK** initialized in `experience_main.py`
- Stored in `app.state.security_guard_sdk` for dependency injection
- SDK uses `auth_abstraction` from Public Works (follows abstraction pattern)
- SDK provides `authenticate()` method (returns `AuthenticationResult`)

**Current SDK Methods:**
- ✅ `authenticate(credentials)` - Returns `AuthenticationResult`
- ✅ `validate_token(token)` - Returns `AuthenticationResult`
- ⚠️ Need to check if `register_user()` exists or if registration uses `auth_abstraction` directly

**Pattern to Follow:**
- Use `sessions.py` as template
- Use Security Guard SDK from `app.state.security_guard_sdk`
- Follow existing request/response model pattern
- Use dependency injection pattern

**Decision:** ✅ **Add auth router to Experience Plane** (clear path)

---

### 2. WebSocket Pattern ⚠️ **NEEDS CLARIFICATION**

**Frontend Expectation:**
- Endpoint: `/api/runtime/agent`
- Message format: `{ type: "intent", intent: "...", session_id: "...", agent_type: "guide" | "liaison", pillar: "..." }`
- Response format: Runtime events

**Backend Architecture Questions:**
1. Should `/api/runtime/agent` be in Runtime service or Experience Plane?
2. How should agent messages be routed (guide vs liaison)?
3. Does Runtime service have agent routing capabilities?
4. Should we update frontend endpoint expectation?

**Current State:**
- ❌ Runtime service has no WebSocket router
- ✅ Experience Plane has WebSocket router (for execution streaming)
- ✅ Experience Plane has Guide Agent Service
- ⚠️ Frontend expects `/api/runtime/agent` (suggests Runtime service)

**Architecture Patterns Found:**
- Experience Plane handles user-facing APIs
- Runtime service handles execution
- Guide Agent Service is in Experience Plane
- Agents are in realms (not in Runtime service directly)

**Decision:** ⚠️ **ASK BACKEND TEAM** - Which service should own `/api/runtime/agent`?

---

## 🔧 Implementation Plan

### Phase 1: Authentication Endpoints ✅ **READY TO IMPLEMENT**

**File:** `symphainy_platform/civic_systems/experience/api/auth.py` (NEW)

**Pattern:**
- Follow `sessions.py` as template
- Use Security Guard SDK from `app.state.security_guard_sdk`
- Use existing model pattern (create `auth_model.py` if needed)
- Register in `experience_service.py`

**Key Points:**
- ✅ Use Security Guard SDK (not direct auth abstraction)
- ✅ Follow Public Works abstraction pattern (via SDK)
- ✅ Use dependency injection (`Depends(get_security_guard_sdk)`)
- ✅ Follow existing error handling patterns
- ✅ Return proper response models

**Implementation Steps:**
1. Check if `auth_abstraction` has `register_user()` method
2. Create `auth.py` router following `sessions.py` pattern
3. Create request/response models (or use existing patterns)
4. Register router in `experience_service.py`
5. Test with frontend

---

### Phase 2: WebSocket Agent Endpoint ⚠️ **AWAITING CLARIFICATION**

**Questions for Backend Team:**

1. **Service Ownership:**
   - Should `/api/runtime/agent` be in Runtime service or Experience Plane?
   - Does the endpoint path (`/api/runtime/agent`) indicate Runtime service ownership?

2. **Agent Routing:**
   - How should agent messages be routed (guide vs liaison)?
   - Should routing happen in Runtime or Experience Plane?
   - How do agents get invoked from WebSocket messages?

3. **Architecture Pattern:**
   - Is there a Runtime Plane service that should handle WebSocket?
   - Should WebSocket be a separate service?
   - What's the canonical pattern for agent WebSocket communication?

**Options:**

**Option A: Runtime Service (if endpoint path indicates ownership)**
- Add WebSocket router to Runtime service
- Route messages to agents via Execution Lifecycle Manager
- Runtime handles agent execution

**Option B: Experience Plane (if user-facing pattern)**
- Add WebSocket router to Experience Plane
- Use Guide Agent Service for guide messages
- Route liaison messages to Runtime for realm agents
- Endpoint would be `/api/experience/agent` (requires frontend update)

**Option C: Hybrid (Experience Plane with Runtime Proxy)**
- Experience Plane: `/api/runtime/agent` (user-facing endpoint)
- Experience Plane proxies to Runtime for agent execution
- Clean separation: Experience = user-facing, Runtime = execution

**Recommendation:** Ask backend team which option aligns with their architecture.

---

## 📋 Detailed Implementation

### Authentication Router Implementation

**File:** `symphainy_platform/civic_systems/experience/api/auth.py`

```python
"""
Authentication API Endpoints

Follows Security Guard SDK pattern for authentication.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK

router = APIRouter(prefix="/api/auth", tags=["authentication"])
logger = get_logger("ExperienceAPI.Auth")


def get_security_guard_sdk(request: Request) -> SecurityGuardSDK:
    """Dependency to get Security Guard SDK."""
    if not hasattr(request.app.state, "security_guard_sdk"):
        raise RuntimeError("Security Guard SDK not initialized. Check Experience service startup.")
    return request.app.state.security_guard_sdk


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    roles: Optional[list] = None
    permissions: Optional[list] = None
    message: Optional[str] = None
    error: Optional[str] = None


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    security_guard: SecurityGuardSDK = Depends(get_security_guard_sdk)
):
    """
    Login user.
    
    Uses Security Guard SDK to authenticate user.
    """
    try:
        # Use Security Guard SDK to authenticate
        auth_result = await security_guard.authenticate({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_result:
            return AuthResponse(
                success=False,
                error="Authentication failed"
            )
        
        # TODO: Get access_token from auth_abstraction
        # For now, return user context
        return AuthResponse(
            success=True,
            user_id=auth_result.user_id,
            tenant_id=auth_result.tenant_id,
            roles=auth_result.roles,
            permissions=auth_result.permissions
        )
    except Exception as e:
        logger.error(f"Login failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    security_guard: SecurityGuardSDK = Depends(get_security_guard_sdk)
):
    """
    Register new user.
    
    Uses Security Guard SDK (via auth_abstraction) to register user.
    """
    try:
        # Check if auth_abstraction has register_user method
        # If not, we may need to add it or use a different approach
        auth_abstraction = security_guard.auth_abstraction
        
        # TODO: Check if register_user exists in auth_abstraction
        # If yes, use it. If no, we need to add it to auth_abstraction
        
        # For now, placeholder (will be implemented based on auth_abstraction capabilities)
        return AuthResponse(
            success=False,
            error="Registration not yet implemented - checking auth_abstraction capabilities"
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

**Update:** `symphainy_platform/civic_systems/experience/experience_service.py`

```python
from .api.auth import router as auth_router

# In create_app():
app.include_router(auth_router)  # Add this line after other routers
```

---

## ⚠️ Open Questions for Backend Team

### 1. Authentication

**Question:** Does `auth_abstraction` have a `register_user()` method, or should we add it?

**Current State:**
- Security Guard SDK has `authenticate()` method
- Need to check if `auth_abstraction` has `register_user()`
- If not, should we add it to `auth_abstraction` or use a different approach?

---

### 2. WebSocket Agent Endpoint

**Question:** Which service should own `/api/runtime/agent` WebSocket endpoint?

**Options:**
- **Runtime Service:** Matches endpoint path, Runtime handles execution
- **Experience Plane:** User-facing APIs, already has Guide Agent Service
- **Separate Service:** Runtime Plane or dedicated WebSocket service

**Follow-up Questions:**
- How should agent messages be routed (guide vs liaison)?
- Should routing happen in Runtime or Experience Plane?
- How do agents get invoked from WebSocket messages?

---

## 🎯 Next Steps

1. **Immediate:** Check `auth_abstraction` for `register_user()` method
2. **Next:** Implement authentication router (login first, then register based on capabilities)
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
