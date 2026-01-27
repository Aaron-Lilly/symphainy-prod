# Phase 7: Remaining Issues

**Date:** January 24, 2026

---

## Issues Identified

### 1. ✅ Fixed: 404 for `/pillars/operation`
**Status:** Fixed - All references updated to `/pillars/journey`
- ✅ `SolutionWelcomePage.tsx` - Fixed
- ✅ `SOPWorkflowTab.tsx` - Fixed
- ✅ `IntegrationHintsPanel.tsx` - Fixed (2 instances)
- ✅ `SecondaryChatbot.tsx` - Fixed
- ✅ `pillars.ts` - Already correct

**Action Required:** Frontend rebuilt and restarted. Refresh browser to see changes.

---

### 2. ⚠️ WebSocket 403 Forbidden Error
**Status:** Backend Authentication Issue

**Error:**
```
WebSocket connection to 'ws://35.215.64.103/api/runtime/agent?session_token=...' failed: 
Error during WebSocket handshake: Unexpected response code: 403
```

**Root Cause:**
The WebSocket connection is being rejected by the backend with a 403 Forbidden response. This indicates:
- The session token is being sent correctly
- The backend is receiving the request
- The backend is rejecting it due to authentication/authorization

**Possible Causes:**
1. **Session token format/validation** - Backend may not recognize the session token format
2. **Authorization check** - Backend may require additional permissions/headers
3. **WebSocket upgrade handling** - Traefik or backend may not be properly handling WebSocket upgrade
4. **CORS/Origin issues** - Backend may be rejecting based on origin

**Investigation Needed:**
- Check backend logs for WebSocket connection attempts
- Verify session token validation in backend
- Check Traefik WebSocket routing configuration
- Verify backend WebSocket endpoint authentication

**Next Steps:**
1. Check `symphainy-experience` logs for WebSocket connection attempts
2. Verify session token is valid and properly formatted
3. Check backend WebSocket authentication middleware
4. Verify Traefik is properly forwarding WebSocket upgrade headers

---

### 3. ⚠️ Login Error Messages Not Displaying
**Status:** Fixed in code, requires frontend rebuild

**Fix Applied:**
- Updated `LoginForm` to check `authError` from AuthProvider
- Added display of both `errors.general` and `authError`
- Increased timeout for checking auth state

**Action Required:** 
- Frontend has been rebuilt and restarted
- Refresh browser (hard refresh: Ctrl+Shift+R or Cmd+Shift+R)
- Try logging in with invalid credentials to verify error display

---

## Testing Checklist

### After Frontend Rebuild:
- [ ] Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
- [ ] Check console for `/pillars/operation` 404 - should be gone
- [ ] Try logging in with invalid credentials - should see error message
- [ ] Try logging in with valid credentials - should succeed
- [ ] Check WebSocket connection after login - may still show 403 (backend issue)

### WebSocket 403 Investigation:
- [ ] Check `symphainy-experience` container logs
- [ ] Check `symphainy-runtime` container logs
- [ ] Verify session token format matches backend expectations
- [ ] Check Traefik WebSocket routing configuration
- [ ] Verify backend WebSocket authentication middleware

---

## Summary

**Frontend Issues:** ✅ Fixed (requires browser refresh)
**Backend Issues:** ⚠️ WebSocket 403 needs investigation

The frontend routing issues are resolved. The WebSocket 403 is a backend authentication issue that needs investigation in the backend services.

---

**Next Action:** Hard refresh browser and test login error display. Then investigate WebSocket 403 in backend logs.
