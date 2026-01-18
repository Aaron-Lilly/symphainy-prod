# Architecture Review & Implementation Plan

**Date:** January 2026  
**Status:** ✅ **REVIEW COMPLETE** - Ready for Implementation (with one clarification needed)

---

## 🎯 Executive Summary

After thoroughly reviewing the backend platform architecture, "rules of the road", and SDK patterns, I've identified the correct approach to address both gaps. The backend team has excellent patterns in place, and we can implement following their established architecture.

---

## ✅ Architecture Review Findings

### 1. Authentication Architecture ✅ **FULLY SUPPORTED**

**Backend Implementation:**
- ✅ `supabase_adapter` has `sign_up_with_password()` method (line 149)
- ✅ `auth_abstraction` already has `register_user()` method implemented! (line 250)
- ✅ Security Guard SDK initialized in Experience Plane (`experience_main.py`)
- ✅ SDK stored in `app.state.security_guard_sdk` for dependency injection
- ✅ SDK has `authenticate()` method (returns `AuthenticationResult`)

**What's Missing:**
- ⚠️ `AuthenticationProtocol` doesn't define `register_user()` in protocol (but implementation exists)
- ⚠️ Security Guard SDK doesn't have `register_user()` method (needs to be added)

**Implementation Path:** ✅ **CLEAR**
1. Add `register_user()` to `AuthenticationProtocol` (protocol definition)
2. Add `register_user()` to Security Guard SDK (coordination logic)
3. Create auth router in Experience Plane (follow `sessions.py` pattern)
4. Register router in `experience_service.py`

---

### 2. WebSocket Architecture ⚠️ **NEEDS CLARIFICATION**

**Frontend Expectation:**
- ✅ Endpoint: `/api/runtime/agent`
- ✅ Uses `RuntimeClient` connecting to `/api/runtime/agent`
- ✅ Message format: `{ type: "intent", intent: "...", session_id: "...", agent_type: "guide" | "liaison", pillar: "..." }`

**Backend State:**
- ❌ Runtime service has no WebSocket router
- ✅ Experience Plane has Guide Agent Service
- ✅ Experience Plane has WebSocket router (for execution streaming: `/api/execution/{id}/stream`)
- ⚠️ Architecture docs show different endpoint patterns (`/api/ws/agent` vs `/api/runtime/agent`)

**Architecture Patterns Found:**
- Experience Plane = User-facing APIs
- Runtime = Execution engine
- Agents are in realms (not directly in Runtime)
- Guide Agent Service is in Experience Plane

**Question for Backend Team:**
- Which service should own `/api/runtime/agent`?
- How should agent routing work?

---

## 🔧 Implementation Plan

### Gap 1: Authentication Endpoints ✅ **READY TO IMPLEMENT**

#### Step 1: Add register_user to AuthenticationProtocol

**File:** `symphainy_platform/foundations/public_works/protocols/auth_protocol.py`

Add method to protocol definition (implementation already exists in `AuthAbstraction`):

```python
class AuthenticationProtocol(Protocol):
    # ... existing methods ...
    
    async def register_user(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Register new user.
        
        Returns raw data only - no business logic, no SecurityContext.
        Platform SDK will translate this to SecurityContext.
        
        Args:
            credentials: Registration credentials (email, password, user_metadata, etc.)
        
        Returns:
            Optional[Dict[str, Any]]: Raw registration data or None if failed
        """
        ...
```

#### Step 2: Add register_user to Security Guard SDK

**File:** `symphainy_platform/civic_systems/smart_city/sdk/security_guard_sdk.py`

Add method following `authenticate()` pattern exactly:

```python
async def register_user(
    self,
    credentials: Dict[str, Any]
) -> Optional[AuthenticationResult]:
    """
    Coordinate user registration (SDK - prepares execution contract).
    
    Returns execution-ready contract that Runtime will validate via primitives.
    
    Args:
        credentials: Registration credentials (email, password, name, etc.)
    
    Returns:
        AuthenticationResult with execution contract, or None if failed
    """
    try:
        # 1. Call auth abstraction (pure infrastructure)
        auth_data = await self.auth_abstraction.register_user(credentials)
        
        if not auth_data or not auth_data.get("success"):
            self.logger.warning(f"Registration failed: {auth_data.get('error', 'Unknown error')}")
            return None
        
        user_id = auth_data.get("user_id")
        email = auth_data.get("email", "")
        
        # 2. Get tenant context (pure infrastructure)
        # For new users, tenant may not exist yet - create default
        tenant_info = await self.tenant_abstraction.get_user_tenant_info(user_id)
        
        if not tenant_info:
            # For new users, create default tenant context
            tenant_id = f"tenant_{user_id}"  # Default tenant
            roles = ["user"]
            permissions = ["read", "write"]
        else:
            tenant_id = tenant_info.get("tenant_id") or tenant_info.get("primary_tenant_id")
            roles = tenant_info.get("roles", ["user"])
            permissions = tenant_info.get("permissions", ["read", "write"])
        
        # 3. Prepare execution contract (for Runtime validation)
        execution_contract = {
            "action": "register_user",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "email": email,
            "roles": roles,
            "permissions": permissions,
            "timestamp": self.clock.now_iso()
        }
        
        return AuthenticationResult(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            permissions=permissions,
            roles=roles,
            execution_contract=execution_contract
        )
        
    except Exception as e:
        self.logger.error(f"Registration coordination failed: {e}", exc_info=True)
        return None
```

#### Step 3: Create Auth Router

**File:** `symphainy_platform/civic_systems/experience/api/auth.py` (NEW)

Follow `sessions.py` pattern exactly - same structure, same dependency injection:

```python
"""
Authentication API Endpoints

Follows Security Guard SDK pattern for authentication.
"""
import sys
from pathlib import Path

# Add project root to path (same pattern as sessions.py)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK

router = APIRouter(prefix="/api/auth", tags=["authentication"])
logger = get_logger("ExperienceAPI.Auth")


def get_security_guard_sdk(request: Request) -> SecurityGuardSDK:
    """Dependency to get Security Guard SDK (same pattern as sessions.py)."""
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
        
        # Get access_token from auth_abstraction
        # Note: Security Guard SDK's authenticate() doesn't return token
        # We need to get it from auth_abstraction directly
        auth_abstraction = security_guard.auth_abstraction
        auth_data = await auth_abstraction.authenticate({
            "email": request.email,
            "password": request.password
        })
        
        access_token = auth_data.get("access_token") if auth_data else None
        refresh_token = auth_data.get("refresh_token") if auth_data else None
        
        return AuthResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
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
        # Use Security Guard SDK to register user
        auth_result = await security_guard.register_user({
            "email": request.email,
            "password": request.password,
            "user_metadata": {
                "name": request.name,
                "full_name": request.name
            }
        })
        
        if not auth_result:
            return AuthResponse(
                success=False,
                error="Registration failed"
            )
        
        # Get access_token from auth_abstraction
        auth_abstraction = security_guard.auth_abstraction
        auth_data = await auth_abstraction.register_user({
            "email": request.email,
            "password": request.password,
            "user_metadata": {
                "name": request.name,
                "full_name": request.name
            }
        })
        
        access_token = auth_data.get("access_token") if auth_data else None
        refresh_token = auth_data.get("refresh_token") if auth_data else None
        
        return AuthResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=auth_result.user_id,
            tenant_id=auth_result.tenant_id,
            roles=auth_result.roles,
            permissions=auth_result.permissions
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

#### Step 4: Register Router

**File:** `symphainy_platform/civic_systems/experience/experience_service.py`

```python
from .api.auth import router as auth_router

# In create_app(), after other routers:
app.include_router(auth_router)
```

---

### Gap 2: WebSocket Agent Endpoint ⚠️ **AWAITING BACKEND TEAM CLARIFICATION**

**Question for Backend Team:**

**Which service should own `/api/runtime/agent` WebSocket endpoint?**

**Options:**

**Option A: Runtime Service**
- ✅ Matches frontend expectation (`/api/runtime/agent`)
- ✅ Runtime handles execution
- ❌ Runtime doesn't have agent routing logic
- ❌ Agents are in realms, not Runtime service directly

**Option B: Experience Plane**
- ✅ Experience Plane handles all user-facing APIs
- ✅ Experience Plane has Guide Agent Service
- ✅ Experience Plane already has WebSocket router pattern
- ❌ Endpoint would be `/api/experience/agent` (not `/api/runtime/agent`)
- ⚠️ Would require frontend update

**Option C: Hybrid (Experience Plane with Runtime Proxy)**
- ✅ Experience Plane: `/api/runtime/agent` (user-facing endpoint)
- ✅ Experience Plane proxies to Runtime for agent execution
- ✅ Clean separation: Experience = user-facing, Runtime = execution
- ⚠️ More complex routing

**Follow-up Questions:**
1. How should agent messages be routed (guide vs liaison)?
2. Should routing happen in Runtime or Experience Plane?
3. How do agents get invoked from WebSocket messages?
4. Should we update frontend to match backend design?

---

## 📊 Implementation Readiness

| Gap | Backend Support | Frontend Ready | Implementation Status |
|-----|----------------|----------------|----------------------|
| **Authentication** | ✅ Full support | ✅ Ready | ✅ **READY TO IMPLEMENT** |
| **WebSocket** | ⚠️ Needs clarification | ✅ Ready | ⚠️ **AWAITING CLARIFICATION** |

---

## 🚀 Next Steps

### Immediate (Authentication):
1. ✅ Add `register_user()` to `AuthenticationProtocol`
2. ✅ Add `register_user()` to Security Guard SDK
3. ✅ Create auth router in Experience Plane
4. ✅ Register router in `experience_service.py`
5. ✅ Test with frontend

### Next (WebSocket):
1. ⚠️ Ask backend team about endpoint ownership
2. ⚠️ Implement WebSocket router based on their guidance
3. ⚠️ Update frontend if needed to match backend design

---

## 📝 Summary

**Authentication:** ✅ **READY** - All backend pieces exist, just need to wire them together following established patterns

**WebSocket:** ⚠️ **AWAITING CLARIFICATION** - Need backend team input on endpoint ownership and routing pattern

**Recommendation:**
- Implement authentication endpoints now (following clear backend patterns)
- Ask backend team about WebSocket before implementing
- Update frontend if needed to match backend design (they publish SDKs for us to follow)

---

**Last Updated:** January 2026
