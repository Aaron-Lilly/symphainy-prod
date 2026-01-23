# Frontend Session Cleanup Fix

**Date:** January 23, 2026  
**Issue:** Frontend making API calls before login, trying to access non-existent sessions  
**Status:** ✅ **FIXED**

---

## Problem

Frontend was making session API calls on page load before user authentication:
- `PlatformStateProvider` tried to load session from localStorage on mount
- `UserContextProvider` tried to restore session on mount
- Old session data in storage caused 404 errors
- "No valid session found" logs appeared before login

**Errors:**
```
api/session/session_5d945c64-efa7-40cf-ada7-d382a8d37d08_21e0fcba-8662-4b99-bc0e-244b2bcfaabb_2026-01-23T01:44:54.007743:1  Failed to load resource: the server responded with a status of 404 (Not Found)
Failed to load session: Error: Session session_5d945c64-efa7-40cf-ada7-d382a8d37d08_21e0fcba-8662-4b99-bc0e-244b2bcfaabb_2026-01-23T01:44:54.007743 not found
```

---

## Root Cause

1. **PlatformStateProvider** (line 507-532):
   - Loaded session data from localStorage on mount
   - Made API call to `getSession()` even if user wasn't authenticated
   - No check for `access_token` before loading session

2. **UserContextProvider** (line 160-183):
   - Called `restoreSession()` on mount
   - `restoreSession()` called `validateSession()` which made API call to `/api/auth/me`
   - No check for authentication before attempting restoration

3. **Stale Session Data**:
   - Old session IDs in localStorage/sessionStorage from previous sessions
   - Frontend tried to use them even though sessions no longer exist

---

## Fixes Applied

### 1. PlatformStateProvider (`shared/state/PlatformStateProvider.tsx`)

**Before:**
- Loaded session from localStorage on mount
- Made API call to get session details
- No authentication check

**After:**
- Checks for `access_token` before loading session
- Clears stale session data if not authenticated
- Only loads session if user is authenticated
- Handles 404 errors gracefully (clears stale data)

**Changes:**
```typescript
// Only load session if user is authenticated (has access_token)
const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;

if (!accessToken) {
  // Clear stale session data
  localStorage.removeItem("session_id");
  // ...
  return;
}
```

### 2. UserContextProvider (`lib/contexts/UserContextProvider.tsx`)

**Before:**
- Called `restoreSession()` on mount unconditionally
- Made API call to validate session

**After:**
- Checks for `access_token` before attempting restoration
- Skips restoration if user is not authenticated
- No API calls before authentication

**Changes:**
```typescript
// Check if user is authenticated (has access_token) before attempting restoration
const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;

if (!accessToken) {
  console.log('ℹ️ No valid session found (user not authenticated)');
  setIsLoading(false);
  return;
}
```

### 3. ExperiencePlaneClient (`lib/api/experience-layer-client.ts`)

**Before:**
- `restoreSession()` loaded from localStorage
- Always called `validateSession()` which made API call

**After:**
- Checks for `access_token` first
- Uses sessionStorage (new format) or localStorage (old format)
- Only validates with backend for old format
- New format doesn't require validation (session just created on login)

**Changes:**
```typescript
// Check for access_token first (indicates user is authenticated)
const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;

if (!accessToken) {
  return false; // Don't try to restore if not authenticated
}
```

### 4. AuthProvider (`shared/auth/AuthProvider.tsx`)

**Before:**
- Restored session from storage without checking authentication

**After:**
- Checks for `access_token` before restoring
- Clears stale session data if not authenticated

**Changes:**
```typescript
// Check for access_token first - if not present, user is not authenticated
const accessToken = sessionStorage.getItem("access_token");

if (!accessToken) {
  // Clear stale session data
  sessionStorage.removeItem("session_id");
  // ...
  return;
}
```

### 5. ExperiencePlaneClient.getSession (`shared/services/ExperiencePlaneClient.ts`)

**Before:**
- No Authorization header

**After:**
- Includes `Authorization: Bearer {access_token}` header
- Only makes call if access_token exists

**Changes:**
```typescript
// Get access_token for authentication
const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;

if (accessToken) {
  headers['Authorization'] = `Bearer ${accessToken}`;
}
```

### 6. MainLayout (`shared/components/MainLayout.tsx`)

**Before:**
- Checked `localStorage.getItem("auth_token")`
- Token matching logic was incorrect

**After:**
- Checks `sessionStorage.getItem("access_token")`
- Proper token matching (access_token and session_id are different)

**Changes:**
```typescript
// Verify that both access_token and session_id exist
const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;
const sessionId = typeof window !== 'undefined' ? sessionStorage.getItem("session_id") : null;
const tokenMatches = accessToken && sessionId && guideSessionToken === sessionId;
```

---

## Result

### ✅ Before Login
- No API calls to session endpoints
- No 404 errors
- "No valid session found" is just an info log (expected)
- Stale session data is cleared

### ✅ After Login
- Session data loaded from storage
- API calls made with proper authentication
- Session synced with Runtime

---

## Files Changed

1. `symphainy-frontend/shared/state/PlatformStateProvider.tsx`
2. `symphainy-frontend/lib/contexts/UserContextProvider.tsx`
3. `symphainy-frontend/lib/api/experience-layer-client.ts`
4. `symphainy-frontend/shared/auth/AuthProvider.tsx`
5. `symphainy-frontend/shared/services/ExperiencePlaneClient.ts`
6. `symphainy-frontend/shared/components/MainLayout.tsx`

---

## Testing

### Expected Behavior:
1. **Before Login:**
   - Page loads without errors
   - No API calls to `/api/session/*`
   - "No valid session found" is just an info log (not an error)
   - No 404 errors in console

2. **After Login:**
   - Session data loaded
   - API calls work correctly
   - No errors

---

**Last Updated:** January 23, 2026
