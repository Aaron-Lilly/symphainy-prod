# Phase 2: Service Layer Standardization - Testing Checklist

## What We've Changed

### ✅ New Files Created
1. **`shared/services/ServiceLayerAPI.ts`**
   - Unified API interface for all service calls
   - Authentication, Agent, Intent & Execution, Session APIs

2. **`shared/hooks/useServiceLayerAPI.ts`**
   - React hook that wraps ServiceLayerAPI
   - Automatically gets session tokens from SessionBoundaryProvider

3. **`shared/hooks/useFileAPI.ts`**
   - React hook for file management operations
   - Automatically gets session tokens from SessionBoundaryProvider

### ✅ Components Updated
1. **`shared/auth/AuthProvider.tsx`**
   - ✅ Now uses `ServiceLayerAPI.loginUser()` instead of direct fetch
   - ✅ Now uses `ServiceLayerAPI.registerUser()` instead of direct fetch
   - ✅ Removed manual fetch calls

2. **`shared/agui/AGUIEventProvider.tsx`**
   - ✅ Now uses `ServiceLayerAPI.sendAgentEvent()` instead of direct fetch
   - ✅ Removed manual fetch calls

3. **`components/content/FileDashboard.tsx`**
   - ✅ Now uses `useFileAPI()` hook instead of direct `lib/api/fms` imports
   - ✅ Removed manual token passing
   - ✅ Uses `listFiles()` and `deleteFile()` from hook

## Testing Checklist

### 🔐 Authentication Flow
- [ ] **Login**
  - Navigate to login page
  - Enter credentials and submit
  - Verify: Login succeeds
  - Verify: User is redirected appropriately
  - Verify: Session is created/upgraded via SessionBoundaryProvider
  - Check browser console for errors

- [ ] **Registration**
  - Navigate to registration page
  - Enter new user details and submit
  - Verify: Registration succeeds
  - Verify: User is authenticated after registration
  - Verify: Session is created/upgraded via SessionBoundaryProvider
  - Check browser console for errors

### 🤖 Agent Events
- [ ] **Agent Event Sending**
  - After login, trigger an agent event (e.g., through chatbot or guide agent)
  - Verify: Event is sent successfully
  - Verify: Response is received
  - Check browser console for errors
  - Check network tab: Verify request goes to `/global/agent` endpoint

### 📁 File Management
- [ ] **List Files**
  - Navigate to file dashboard/content pillar
  - Verify: Files are loaded successfully
  - Check browser console for errors
  - Check network tab: Verify request goes to `/api/fms/files` with proper auth headers

- [ ] **Delete File**
  - Select a file and delete it
  - Verify: File is deleted successfully
  - Verify: File disappears from list
  - Check browser console for errors
  - Check network tab: Verify DELETE request goes to `/api/fms/{uuid}` with proper auth headers

### 🔍 General Checks
- [ ] **Build Status**
  - Verify: `npm run build` completes successfully
  - Verify: No TypeScript errors
  - Verify: No console errors on page load

- [ ] **Session Management**
  - Verify: Session tokens are retrieved from SessionBoundaryProvider (not sessionStorage directly)
  - Verify: No manual token passing in updated components
  - Check browser console: Look for any "Not authenticated" errors

- [ ] **Network Requests**
  - Open browser DevTools → Network tab
  - Verify: All API requests include proper Authorization headers
  - Verify: All API requests include proper session tokens where needed
  - Verify: No CORS errors
  - Verify: No 401/403 errors (unless expected for unauthenticated requests)

## Expected Behavior

### ✅ What Should Work
- Login/Registration should work exactly as before
- File listing and deletion should work exactly as before
- Agent events should work exactly as before
- All API calls should automatically include proper authentication tokens

### ⚠️ What Might Be Different
- **Token Management**: Tokens are now retrieved from SessionBoundaryProvider automatically
- **Error Messages**: Error messages might be slightly different (from ServiceLayerAPI)
- **Network Requests**: Request format should be the same, but headers are managed automatically

## Known Issues / Notes

### Components NOT Yet Updated
These components still use direct API calls and should work as before:
- `components/content/FileUploader.tsx`
- `components/content/ParsePreview.tsx`
- `components/content/SimpleFileDashboard.tsx`
- Other content/insights/operations components

These will be updated in the next phase.

### Testing Strategy
1. **Test Updated Components First**
   - Focus on AuthProvider (login/register)
   - Focus on AGUIEventProvider (agent events)
   - Focus on FileDashboard (list/delete files)

2. **Verify No Regressions**
   - Test that existing functionality still works
   - Check that error handling still works
   - Verify that loading states still work

3. **Check Browser Console**
   - Look for any new errors
   - Look for any deprecation warnings
   - Verify no "Cannot find" or "undefined" errors

## If Issues Are Found

### Common Issues & Fixes

1. **"Not authenticated" errors**
   - Check: Is SessionBoundaryProvider properly initialized?
   - Check: Is access_token in sessionStorage?
   - Fix: Ensure SessionBoundaryProvider is at root of component tree

2. **401/403 errors on API calls**
   - Check: Are tokens being retrieved correctly?
   - Check: Are tokens expired?
   - Fix: Verify ServiceLayerAPI is using correct token source

3. **"Cannot find module" errors**
   - Check: Are new files in correct locations?
   - Fix: Verify imports are correct

4. **TypeScript errors**
   - Check: Are all types exported correctly?
   - Fix: Verify ServiceLayerAPI exports match usage

## Next Steps After Testing

Once testing is complete:
1. If all tests pass → Continue with remaining components
2. If issues found → Fix issues before proceeding
3. Document any findings or edge cases
