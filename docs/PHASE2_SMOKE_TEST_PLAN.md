# Phase 2: Service Layer Standardization - Smoke Test Plan

**Date:** January 22, 2026  
**Purpose:** Validate breaking changes and service layer approach before proceeding

---

## Test Scope

### ✅ What We're Testing
1. **Service Layer Hooks** - Do they work correctly?
2. **Updated Components** - Do they function as before?
3. **Token Management** - Are tokens automatically retrieved?
4. **Breaking Changes** - Do direct imports fail as expected?
5. **No Regressions** - Does existing functionality still work?

### ⏸️ What We're NOT Testing (Yet)
- Full feature testing (that comes later)
- Edge cases and error scenarios (comprehensive testing later)
- Performance (performance testing later)
- All components (just the ones we've updated)

---

## Smoke Tests

### Test 1: Build Validation ✅
**Goal:** Verify breaking changes are enforced

**Steps:**
1. Run `npm run build`
2. Verify build passes
3. Try importing `lib/api/fms` directly in a test file
4. Verify build fails with clear error

**Expected Result:**
- ✅ Build passes for current code
- ✅ Direct import fails (if we've removed exports) OR shows deprecation warning

**Status:** ⏳ To Test

---

### Test 2: Authentication Flow 🔐
**Goal:** Verify AuthProvider works with ServiceLayerAPI

**Steps:**
1. Navigate to login page
2. Enter valid credentials
3. Submit login form
4. Verify login succeeds
5. Check browser console for errors
6. Check network tab - verify request goes to `/api/auth/login`
7. Verify session is created/upgraded

**Expected Result:**
- ✅ Login succeeds
- ✅ No console errors
- ✅ Request includes proper headers
- ✅ Session state updated correctly

**Status:** ⏳ To Test

---

### Test 3: File Listing 📁
**Goal:** Verify FileDashboard works with useFileAPI hook

**Steps:**
1. After login, navigate to file dashboard/content pillar
2. Verify files are loaded
3. Check browser console for errors
4. Check network tab - verify request goes to `/api/fms/files`
5. Verify request includes Authorization header automatically

**Expected Result:**
- ✅ Files load successfully
- ✅ No console errors
- ✅ Request includes Authorization header (automatic)
- ✅ No manual token passing in code

**Status:** ⏳ To Test

---

### Test 4: File Upload 📤
**Goal:** Verify FileUploader works with useFileAPI hook

**Steps:**
1. Navigate to file upload component
2. Select a file
3. Choose file type
4. Upload file
5. Verify upload succeeds
6. Check browser console for errors
7. Check network tab - verify request goes to `/api/file-processing/upload`
8. Verify request includes proper headers automatically

**Expected Result:**
- ✅ File uploads successfully
- ✅ No console errors
- ✅ Request includes Authorization header (automatic)
- ✅ Processing status updates correctly

**Status:** ⏳ To Test

---

### Test 5: File Deletion 🗑️
**Goal:** Verify FileDashboard delete functionality works

**Steps:**
1. In file dashboard, select a file
2. Click delete
3. Confirm deletion
4. Verify file is deleted
5. Check browser console for errors
6. Check network tab - verify DELETE request goes to `/api/fms/{uuid}`
7. Verify request includes Authorization header automatically

**Expected Result:**
- ✅ File deleted successfully
- ✅ File disappears from list
- ✅ No console errors
- ✅ Request includes Authorization header (automatic)

**Status:** ⏳ To Test

---

### Test 6: Agent Events 🤖
**Goal:** Verify AGUIEventProvider works with ServiceLayerAPI

**Steps:**
1. After login, trigger an agent event (e.g., through chatbot)
2. Verify event is sent successfully
3. Check browser console for errors
4. Check network tab - verify request goes to `/global/agent`
5. Verify request includes proper payload

**Expected Result:**
- ✅ Event sent successfully
- ✅ Response received
- ✅ No console errors
- ✅ Request format correct

**Status:** ⏳ To Test

---

### Test 7: Direct Import Prevention 🚫
**Goal:** Verify breaking changes are enforced

**Steps:**
1. Create a test file that imports directly from `lib/api/fms`
2. Try to use it in a component
3. Run build
4. Verify build fails OR shows deprecation warning

**Expected Result:**
- ✅ Build fails with clear error message OR
- ✅ Deprecation warning shown in console
- ✅ Developer is directed to use hooks instead

**Status:** ⏳ To Test

---

## Quick Test Checklist

### Critical Paths (Must Pass)
- [ ] **Build passes** - No TypeScript errors
- [ ] **Login works** - AuthProvider uses ServiceLayerAPI
- [ ] **File listing works** - FileDashboard uses useFileAPI
- [ ] **File upload works** - FileUploader uses useFileAPI
- [ ] **No console errors** - Clean browser console

### Important Paths (Should Pass)
- [ ] **File deletion works** - FileDashboard delete functionality
- [ ] **Agent events work** - AGUIEventProvider uses ServiceLayerAPI
- [ ] **Token management** - Tokens automatically retrieved
- [ ] **Network requests** - Proper headers included automatically

### Nice to Have (Can Test Later)
- [ ] **Error handling** - Errors displayed correctly
- [ ] **Loading states** - UI shows loading correctly
- [ ] **Session invalidation** - Handles 401/403 correctly

---

## Test Execution

### Quick Smoke Test (5-10 minutes)
1. Run build ✅
2. Test login 🔐
3. Test file listing 📁
4. Test file upload 📤
5. Check console for errors 🔍

### Full Smoke Test (15-20 minutes)
1. All quick tests
2. Test file deletion 🗑️
3. Test agent events 🤖
4. Test direct import prevention 🚫
5. Verify network requests 📡

---

## What to Look For

### ✅ Success Indicators
- All tests pass
- No console errors
- Network requests include proper headers
- Functionality works as before
- Tokens automatically managed

### ⚠️ Warning Signs
- Console errors (even if functionality works)
- Missing Authorization headers
- Manual token passing still happening
- Direct imports still working (should fail)

### 🚨 Failure Indicators
- Tests fail
- Functionality broken
- Build errors
- Runtime errors

---

## If Tests Pass

**Proceed with:**
- Update remaining File Management components (ParsePreview, SimpleFileDashboard)
- Create additional hooks (useContentAPI, useInsightsAPI, useOperationsAPI)
- Continue with next component groups

---

## If Tests Fail

**Stop and:**
1. Document the failure
2. Identify root cause
3. Fix the issue
4. Re-test
5. Don't proceed until all critical tests pass

---

## Test Results Template

```
## Test Results - [Date]

### Build Validation
- [ ] Pass / [ ] Fail
- Notes: 

### Authentication Flow
- [ ] Pass / [ ] Fail
- Notes: 

### File Listing
- [ ] Pass / [ ] Fail
- Notes: 

### File Upload
- [ ] Pass / [ ] Fail
- Notes: 

### File Deletion
- [ ] Pass / [ ] Fail
- Notes: 

### Agent Events
- [ ] Pass / [ ] Fail
- Notes: 

### Direct Import Prevention
- [ ] Pass / [ ] Fail
- Notes: 

### Overall Status
- [ ] Ready to Proceed / [ ] Needs Fixes
- Issues Found:
- Next Steps:
```
