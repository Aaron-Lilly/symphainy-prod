# Authentication Security Migration Plan: HttpOnly Cookies

**Date:** January 2026  
**Status:** 📋 **PLANNED FOR PRODUCTION**  
**Current:** sessionStorage (interim security improvement)  
**Target:** HttpOnly Cookies (production-ready security)

---

## 🎯 Executive Summary

**Current State:** Using sessionStorage for token storage (better than localStorage, but still vulnerable to XSS)

**Target State:** HttpOnly cookies set by backend (most secure, industry standard)

**Migration Strategy:** Backend-first approach - backend sets cookies, frontend removes token management

---

## 🔒 Security Comparison

### Current: sessionStorage
- ✅ Better than localStorage (cleared on tab close)
- ✅ Not accessible to JavaScript (reduces XSS risk)
- ❌ Still vulnerable to XSS if attacker can execute JavaScript
- ❌ Frontend must manually include token in requests

### Target: HttpOnly Cookies
- ✅ **Most secure** - not accessible to JavaScript at all
- ✅ **Automatic** - browser sends cookies with every request
- ✅ **Industry standard** - OWASP recommended
- ✅ **CSRF protection** - SameSite attribute prevents CSRF attacks
- ✅ **No frontend token management** - backend handles everything

---

## 📋 Implementation Plan

### Phase 1: Backend Changes (Experience Plane)

#### 1.1 Update Auth Router to Set HttpOnly Cookies

**File:** `symphainy_platform/civic_systems/experience/api/auth.py` (or wherever auth endpoints are)

**Changes:**
```python
from fastapi import Response
from fastapi.responses import JSONResponse

@router.post("/login")
async def login_user(request: LoginRequest, response: Response):
    """Authenticate user and set HttpOnly cookie."""
    # ... existing authentication logic ...
    
    # Set HttpOnly cookie with access token
    response.set_cookie(
        key="auth_token",
        value=access_token,
        httponly=True,  # Not accessible to JavaScript
        secure=True,     # Only sent over HTTPS
        samesite="lax",  # CSRF protection
        max_age=3600,    # 1 hour expiration
        path="/",        # Available to all paths
    )
    
    # Set refresh token in separate HttpOnly cookie
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=604800,  # 7 days
            path="/",
        )
    
    # Return response WITHOUT token in body (security best practice)
    return JSONResponse(
        content={
            "success": True,
            "user": {
                "user_id": user_id,
                "email": email,
                "name": name,
                "tenant_id": tenant_id,
                "roles": roles,
                "permissions": permissions
            },
            "message": "Login successful!"
        }
    )
```

#### 1.2 Update Token Validation Middleware

**File:** Create or update authentication middleware

**Changes:**
```python
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

async def get_auth_token(request: Request) -> str:
    """
    Extract auth token from HttpOnly cookie or Authorization header (fallback).
    
    Priority:
    1. HttpOnly cookie (preferred)
    2. Authorization header (for API clients)
    """
    # Try cookie first
    token = request.cookies.get("auth_token")
    
    # Fallback to Authorization header (for API clients)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    return token
```

#### 1.3 Update Logout Endpoint

**File:** Same auth router

**Changes:**
```python
@router.post("/logout")
async def logout_user(response: Response):
    """Clear authentication cookies."""
    response.delete_cookie(
        key="auth_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return {"success": True, "message": "Logged out successfully"}
```

---

### Phase 2: Frontend Changes

#### 2.1 Update AuthProvider

**File:** `symphainy-frontend/shared/auth/AuthProvider.tsx`

**Changes:**
```typescript
// Remove all sessionStorage/localStorage token management
// Backend sets HttpOnly cookies automatically

const login = useCallback(async (email: string, password: Promise<void> => {
  setIsLoading(true);
  setError(null);

  try {
    const { getApiEndpointUrl } = require('@/shared/config/api-config');
    const loginUrl = getApiEndpointUrl('/api/auth/login');
    
    // Include credentials to allow cookies
    const response = await fetch(loginUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // ✅ CRITICAL: Allows cookies to be set/received
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Login failed' }));
      throw new Error(errorData.message || `Login failed: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Backend sets HttpOnly cookies automatically
    // We only store user data (not tokens) in sessionStorage
    const userData: User = {
      id: data.user.user_id,
      email: data.user.email,
      name: data.user.full_name || data.user.name,
      tenant_id: data.user.tenant_id,
      permissions: data.user.permissions || [],
    };

    setUser(userData);
    setIsAuthenticated(true);
    
    // Store ONLY user data (not tokens) in sessionStorage
    if (typeof window !== "undefined") {
      sessionStorage.setItem("user_data", JSON.stringify(userData));
      sessionStorage.setItem("tenant_id", userData.tenant_id);
      sessionStorage.setItem("user_id", userData.id);
      // NO token storage - cookies handle that
    }
    
    setIsLoading(false);
  } catch (err) {
    // ... error handling ...
  }
}, [createSession]);
```

#### 2.2 Update All API Calls to Include Credentials

**File:** All API managers (`ContentAPIManager`, `InsightsAPIManager`, etc.)

**Changes:**
```typescript
// Add credentials: 'include' to all fetch calls
const response = await fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    // Remove Authorization header - cookies handle auth
  },
  credentials: 'include', // ✅ CRITICAL: Sends cookies with request
  body: JSON.stringify(data),
});
```

#### 2.3 Update auth-utils.ts

**File:** `symphainy-frontend/lib/auth-utils.ts`

**Changes:**
```typescript
// Remove getAuthToken() - tokens are in HttpOnly cookies
// Keep isAuthenticated() - check user_data in sessionStorage
// Keep getCurrentUser() - read from sessionStorage
// Keep clearAuth() - clear sessionStorage (cookies cleared by backend on logout)
```

---

### Phase 3: CORS Configuration

#### 3.1 Update Experience Service CORS

**File:** `symphainy_platform/civic_systems/experience/experience_service.py`

**Changes:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],  # Specific origins
    allow_credentials=True,  # ✅ CRITICAL: Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # May be needed for some use cases
)
```

#### 3.2 Update Frontend API Config

**File:** `symphainy-frontend/shared/config/api-config.ts`

**Ensure:** All API calls use `credentials: 'include'`

---

## 🔄 Migration Steps

### Step 1: Backend Implementation (Week 1)
1. ✅ Update auth router to set HttpOnly cookies
2. ✅ Update token validation to read from cookies
3. ✅ Update logout to clear cookies
4. ✅ Test with Postman/curl (verify cookies are set)

### Step 2: Frontend Updates (Week 1-2)
1. ✅ Update AuthProvider to remove token storage
2. ✅ Add `credentials: 'include'` to all API calls
3. ✅ Update auth-utils to remove token access
4. ✅ Test login/logout flow

### Step 3: Testing (Week 2)
1. ✅ Test authentication flow end-to-end
2. ✅ Verify cookies are set and sent automatically
3. ✅ Test logout clears cookies
4. ✅ Test token refresh (if implemented)
5. ✅ Security testing (XSS, CSRF)

### Step 4: Deployment (Week 2-3)
1. ✅ Deploy backend changes
2. ✅ Deploy frontend changes
3. ✅ Monitor for issues
4. ✅ Rollback plan ready

---

## ⚠️ Important Considerations

### 1. CORS Configuration
- **Must** set `allow_credentials=True` in CORS middleware
- **Must** specify exact origins (not `["*"]`) when using credentials
- **Must** use `credentials: 'include'` in all frontend fetch calls

### 2. SameSite Cookie Attribute
- `SameSite=Lax` - Good balance (prevents CSRF, allows normal navigation)
- `SameSite=Strict` - More secure but may break some flows
- `SameSite=None` - Only if cross-site cookies needed (requires Secure)

### 3. Secure Flag
- **Must** use `Secure=True` in production (HTTPS only)
- Can be `False` in development (HTTP)

### 4. Token Refresh
- Refresh tokens should also be in HttpOnly cookies
- Implement refresh endpoint that reads from cookie
- Frontend doesn't need to manage refresh tokens

### 5. Backward Compatibility
- Consider supporting both cookies AND Authorization header during migration
- Gradually deprecate Authorization header support

---

## 📊 Security Benefits

### Before (sessionStorage)
- ❌ Vulnerable to XSS (if attacker can execute JavaScript)
- ❌ Frontend must manually manage tokens
- ❌ Tokens visible in DevTools
- ✅ Cleared on tab close

### After (HttpOnly Cookies)
- ✅ **Not accessible to JavaScript** (XSS protection)
- ✅ **Automatic** - browser handles everything
- ✅ **Not visible in DevTools** (HttpOnly)
- ✅ **CSRF protection** (SameSite attribute)
- ✅ **Industry standard** (OWASP recommended)

---

## 🧪 Testing Checklist

### Backend Testing
- [ ] Login sets HttpOnly cookie
- [ ] Cookie has correct attributes (HttpOnly, Secure, SameSite)
- [ ] Token validation reads from cookie
- [ ] Logout clears cookies
- [ ] Refresh token works (if implemented)
- [ ] CORS allows credentials

### Frontend Testing
- [ ] Login flow works (no token in response body)
- [ ] API calls automatically include cookies
- [ ] Logout clears user data
- [ ] Session persists across page refreshes
- [ ] Works in different browsers
- [ ] Works with HTTPS

### Security Testing
- [ ] XSS cannot access tokens (HttpOnly)
- [ ] CSRF protection works (SameSite)
- [ ] Tokens not in localStorage/sessionStorage
- [ ] Tokens not in response body
- [ ] Secure flag works (HTTPS only)

---

## 📚 References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [MDN: Using HTTP cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [FastAPI: Setting cookies](https://fastapi.tiangolo.com/advanced/response-cookies/)
- [OWASP: XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

---

## 🎯 Success Criteria

- ✅ All tokens stored in HttpOnly cookies (not accessible to JavaScript)
- ✅ Frontend doesn't manage tokens (backend handles everything)
- ✅ All API calls automatically include cookies
- ✅ CORS properly configured for credentials
- ✅ Security testing passes (XSS, CSRF)
- ✅ No tokens in localStorage/sessionStorage
- ✅ Production-ready security posture

---

**Status:** Ready for implementation when moving to production. Current sessionStorage implementation provides interim security improvement over localStorage.
