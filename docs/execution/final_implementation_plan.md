# Final Implementation Plan - Architecture Aligned

**Date:** January 2026  
**Status:** ✅ **READY TO IMPLEMENT** - Following Backend Architecture Patterns

---

## 🎯 Executive Summary

After reviewing the platform architecture, "rules of the road", and backend SDK patterns, I've identified the correct approach. The backend team has excellent patterns in place, and we can implement both gaps following their established architecture.

---

## ✅ Key Findings

### 1. Authentication ✅ **FULLY SUPPORTED**

**Backend Architecture:**
- ✅ `supabase_adapter` has `sign_up_with_password()` method
- ✅ `auth_abstraction` already has `register_user()` method implemented!
- ✅ Security Guard SDK has `authenticate()` method
- ⚠️ Security Guard SDK needs `register_user()` method added
- ⚠️ `AuthenticationProtocol` needs `register_user()` added to protocol definition

**Implementation Path:**
1. Add `register_user()` to `AuthenticationProtocol` (protocol definition)
2. Add `register_user()` to Security Guard SDK (coordination logic)
3. Create auth router in Experience Plane
4. Use Security Guard SDK pattern (follows `sessions.py`)

---

### 2. WebSocket ⚠️ **NEEDS BACKEND TEAM CLARIFICATION**

**Frontend Expectation:**
- Endpoint: `/api/runtime/agent`
- Uses `RuntimeClient` connecting to `/api/runtime/agent`

**Backend Architecture:**
- Experience Plane has Guide Agent Service
- Agents are in realms (not directly in Runtime)
- Runtime handles execution
- Architecture docs show different endpoint patterns

**Question for Backend Team:**
- Which service should own `/api/runtime/agent`?
- How should agent routing work?

---

## 🔧 Implementation Plan

### Phase 1: Authentication Endpoints ✅ **READY**

#### Step 1: Update AuthenticationProtocol

**File:** `symphainy_platform/foundations/public_works/protocols/auth_protocol.py`

Add `register_user()` method to protocol:

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

Add method following `authenticate()` pattern:

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

Follow `sessions.py` pattern exactly:

```python
"""
Authentication API Endpoints

Follows Security Guard SDK pattern for authentication.
"""
import sys
from pathlib import Path

# Add project root to path
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
        
        # Get access_token from auth_abstraction (need to call it again or store it)
        # For now, we'll need to get token from auth_abstraction directly
        # TODO: Security Guard SDK should return token in AuthenticationResult
        # For MVP, we can get it from auth_abstraction
        
        # Get token from auth_abstraction
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

# In create_app():
app.include_router(auth_router)  # Add after other routers
```

---

### Phase 2: WebSocket Agent Endpoint ⚠️ **AWAITING CLARIFICATION**

**Question for Backend Team:**

**Which service should own `/api/runtime/agent` WebSocket endpoint?**

**Options:**
- **Runtime Service:** Matches endpoint path, Runtime handles execution
- **Experience Plane:** User-facing APIs, already has Guide Agent Service
- **Hybrid:** Experience Plane endpoint that proxies to Runtime

**Once Clarified:**
- Implement WebSocket router in appropriate service
- Route messages to agents correctly
- Emit runtime events to frontend

---

## 📋 Summary

**Authentication:** ✅ **READY** - All pieces in place, just need to wire them together

**WebSocket:** ⚠️ **AWAITING CLARIFICATION** - Need backend team input on endpoint ownership

**Recommendation:**
- Implement authentication endpoints now (following clear pattern)
- Ask backend team about WebSocket before implementing
- Update frontend if needed to match backend design

---

**Last Updated:** January 2026
