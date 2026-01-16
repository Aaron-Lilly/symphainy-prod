# Content Pillar Integration Test Plan

**Date:** January 2026  
**Status:** 🧪 **COMPREHENSIVE INTEGRATION TEST PLAN**  
**Purpose:** Complete integration testing of Content Pillar after migration to new architecture

---

## 🎯 Test Objectives

Validate that the Content Pillar works end-to-end with the new architecture:
1. ✅ All components render and function correctly
2. ✅ PlatformStateProvider integration works
3. ✅ ContentAPIManager integration works
4. ✅ Runtime-based intent submission works
5. ✅ State management (realm.content) works
6. ✅ End-to-end user flows work

---

## 📋 Test Scope

### Components Under Test
- ✅ FileUploader
- ✅ FileDashboard
- ✅ FileParser
- ✅ ParsePreview
- ✅ DataMash
- ✅ FileSelector

### Integration Points
- ✅ PlatformStateProvider
- ✅ ContentAPIManager
- ✅ Experience Plane Client
- ✅ Runtime API
- ✅ Content Realm

---

## 🧪 Test Cases

### Phase 1: Component Rendering & Basic Functionality

#### Test 1.1: Component Import & Rendering
**Objective:** Verify all components can be imported and render without errors

**Steps:**
1. Navigate to Content Pillar page
2. Verify all components render
3. Check browser console for errors

**Expected Results:**
- ✅ All components render
- ✅ No TypeScript errors
- ✅ No runtime errors
- ✅ No console warnings

**Status:** ⏳ Pending

---

#### Test 1.2: PlatformStateProvider Integration
**Objective:** Verify components can access PlatformStateProvider

**Steps:**
1. Open browser console
2. Check if `usePlatformState` hook works
3. Verify `state.realm.content` is accessible
4. Verify `setRealmState` works

**Expected Results:**
- ✅ `usePlatformState` hook accessible
- ✅ `state.realm.content` structure exists
- ✅ `setRealmState` updates state correctly

**Status:** ⏳ Pending

---

#### Test 1.3: ContentAPIManager Integration
**Objective:** Verify ContentAPIManager can be instantiated and methods are accessible

**Steps:**
1. Verify `useContentAPIManager` hook works
2. Check if manager methods are accessible:
   - `uploadFile()`
   - `listFiles()`
   - `parseFile()`
   - `getParsedFile()`
   - `extractEmbeddings()`
   - `getSemanticInterpretation()`

**Expected Results:**
- ✅ Hook returns ContentAPIManager instance
- ✅ All methods are accessible
- ✅ No errors when accessing methods

**Status:** ⏳ Pending

---

### Phase 2: File Upload Flow

#### Test 2.1: File Upload (Happy Path)
**Objective:** Verify file upload works end-to-end

**Prerequisites:**
- User authenticated
- Session created
- Backend services running

**Steps:**
1. Navigate to Content Pillar
2. Select file type (e.g., Structured Data → CSV)
3. Upload a test file (e.g., `test.csv`)
4. Verify upload completes
5. Check file appears in FileDashboard

**Expected Results:**
- ✅ File uploads successfully
- ✅ `ingest_file` intent submitted to Runtime
- ✅ Execution tracked in PlatformStateProvider
- ✅ File appears in FileDashboard
- ✅ File stored in `state.realm.content.files`
- ✅ Toast notification shows success

**Status:** ⏳ Pending

---

#### Test 2.2: File Upload with Copybook
**Objective:** Verify binary file upload with copybook works

**Steps:**
1. Select file type (Structured Data → Binary/Mainframe)
2. Upload binary file
3. Upload copybook file
4. Verify upload completes

**Expected Results:**
- ✅ Both files upload successfully
- ✅ Copybook reference stored correctly
- ✅ File ready for parsing

**Status:** ⏳ Pending

---

#### Test 2.3: File Upload Error Handling
**Objective:** Verify error handling for failed uploads

**Steps:**
1. Attempt to upload invalid file
2. Attempt to upload without required copybook
3. Verify error messages display

**Expected Results:**
- ✅ Error messages display correctly
- ✅ State doesn't break
- ✅ User can retry

**Status:** ⏳ Pending

---

### Phase 3: File Parsing Flow

#### Test 3.1: Parse File (Happy Path)
**Objective:** Verify file parsing works end-to-end

**Prerequisites:**
- File uploaded successfully

**Steps:**
1. Select uploaded file in FileParser
2. Click "Parse" button
3. Wait for parsing to complete
4. Verify parsed file appears in ParsePreview

**Expected Results:**
- ✅ `parse_content` intent submitted to Runtime
- ✅ Execution tracked
- ✅ Parsed file appears in ParsePreview
- ✅ Preview data displays correctly
- ✅ Toast notification shows success

**Status:** ⏳ Pending

---

#### Test 3.2: Parse Binary File with Copybook
**Objective:** Verify binary file parsing with copybook

**Prerequisites:**
- Binary file uploaded with copybook

**Steps:**
1. Select binary file in FileParser
2. Verify copybook is selected
3. Click "Parse" button
4. Wait for parsing to complete

**Expected Results:**
- ✅ Parsing uses copybook correctly
- ✅ Parsed data is structured correctly
- ✅ Preview shows parsed data

**Status:** ⏳ Pending

---

#### Test 3.3: Parse Preview Display
**Objective:** Verify parsed file preview displays correctly

**Prerequisites:**
- File parsed successfully

**Steps:**
1. Navigate to ParsePreview component
2. Select parsed file
3. Generate preview
4. Verify preview displays

**Expected Results:**
- ✅ Preview generates successfully
- ✅ Data displays in structured format
- ✅ Tables/charts render correctly

**Status:** ⏳ Pending

---

### Phase 4: Embeddings & Semantic Layer

#### Test 4.1: Extract Embeddings
**Objective:** Verify embedding extraction works

**Prerequisites:**
- File parsed successfully

**Steps:**
1. Navigate to DataMash component
2. Select parsed file
3. Click "Create Embeddings"
4. Wait for extraction to complete

**Expected Results:**
- ✅ `extract_embeddings` intent submitted
- ✅ Embeddings created successfully
- ✅ Embeddings stored in ArangoDB
- ✅ Lineage tracked in Supabase

**Status:** ⏳ Pending

---

#### Test 4.2: Preview Embeddings
**Objective:** Verify embedding preview works

**Prerequisites:**
- Embeddings created

**Steps:**
1. Select content_id in DataMash
2. Click "Preview Embeddings"
3. Verify preview displays

**Expected Results:**
- ✅ Preview generates successfully
- ✅ Semantic metadata displays
- ✅ Column meanings shown

**Status:** ⏳ Pending

---

#### Test 4.3: Semantic Interpretation
**Objective:** Verify semantic interpretation works

**Prerequisites:**
- Embeddings created

**Steps:**
1. Request semantic interpretation
2. Verify interpretation displays

**Expected Results:**
- ✅ `get_semantic_interpretation` intent submitted
- ✅ Interpretation returned
- ✅ Data displays correctly

**Status:** ⏳ Pending

---

### Phase 5: State Management

#### Test 5.1: Realm State Persistence
**Objective:** Verify realm state persists across component re-renders

**Steps:**
1. Upload a file
2. Navigate away from Content Pillar
3. Navigate back
4. Verify file still in state

**Expected Results:**
- ✅ State persists
- ✅ Files still accessible
- ✅ No data loss

**Status:** ⏳ Pending

---

#### Test 5.2: State Synchronization
**Objective:** Verify state syncs with Runtime

**Steps:**
1. Upload file via FileUploader
2. Check FileDashboard
3. Verify both components see same state

**Expected Results:**
- ✅ State synchronized across components
- ✅ No stale data
- ✅ Updates propagate correctly

**Status:** ⏳ Pending

---

### Phase 6: Error Handling & Edge Cases

#### Test 6.1: Network Errors
**Objective:** Verify graceful handling of network errors

**Steps:**
1. Disconnect network
2. Attempt file upload
3. Verify error handling

**Expected Results:**
- ✅ Error message displays
- ✅ State doesn't break
- ✅ User can retry

**Status:** ⏳ Pending

---

#### Test 6.2: Session Expiry
**Objective:** Verify handling of expired sessions

**Steps:**
1. Let session expire
2. Attempt file operation
3. Verify re-authentication flow

**Expected Results:**
- ✅ Session expiry detected
- ✅ User redirected to login
- ✅ State preserved

**Status:** ⏳ Pending

---

#### Test 6.3: Concurrent Operations
**Objective:** Verify handling of concurrent file operations

**Steps:**
1. Upload multiple files simultaneously
2. Parse multiple files simultaneously
3. Verify all operations complete

**Expected Results:**
- ✅ All operations tracked
- ✅ No race conditions
- ✅ State updates correctly

**Status:** ⏳ Pending

---

## 📊 Test Execution Checklist

### Pre-Test Setup
- [ ] Backend services running (Runtime, Experience Plane, Content Realm)
- [ ] Frontend dev server running
- [ ] User authenticated
- [ ] Session created
- [ ] Test files prepared

### Test Execution
- [ ] Phase 1: Component Rendering
- [ ] Phase 2: File Upload Flow
- [ ] Phase 3: File Parsing Flow
- [ ] Phase 4: Embeddings & Semantic Layer
- [ ] Phase 5: State Management
- [ ] Phase 6: Error Handling

### Post-Test
- [ ] Document test results
- [ ] Document any issues found
- [ ] Create bug reports for failures
- [ ] Update test status

---

## 🚦 Success Criteria

**Minimum for MVP:**
- ✅ All components render
- ✅ File upload works
- ✅ File parsing works
- ✅ State management works
- ✅ No critical errors

**Ideal:**
- ✅ All test cases pass
- ✅ End-to-end flows work
- ✅ Error handling works
- ✅ Performance acceptable
- ✅ User experience smooth

---

## 📝 Test Results Template

**Test Date:** ___________  
**Tester:** ___________  
**Environment:** ___________  

### Phase 1: Component Rendering
- [ ] Test 1.1: PASS / FAIL / SKIP
- [ ] Test 1.2: PASS / FAIL / SKIP
- [ ] Test 1.3: PASS / FAIL / SKIP

### Phase 2: File Upload Flow
- [ ] Test 2.1: PASS / FAIL / SKIP
- [ ] Test 2.2: PASS / FAIL / SKIP
- [ ] Test 2.3: PASS / FAIL / SKIP

### Phase 3: File Parsing Flow
- [ ] Test 3.1: PASS / FAIL / SKIP
- [ ] Test 3.2: PASS / FAIL / SKIP
- [ ] Test 3.3: PASS / FAIL / SKIP

### Phase 4: Embeddings & Semantic Layer
- [ ] Test 4.1: PASS / FAIL / SKIP
- [ ] Test 4.2: PASS / FAIL / SKIP
- [ ] Test 4.3: PASS / FAIL / SKIP

### Phase 5: State Management
- [ ] Test 5.1: PASS / FAIL / SKIP
- [ ] Test 5.2: PASS / FAIL / SKIP

### Phase 6: Error Handling
- [ ] Test 6.1: PASS / FAIL / SKIP
- [ ] Test 6.2: PASS / FAIL / SKIP
- [ ] Test 6.3: PASS / FAIL / SKIP

### Issues Found:
_________________________________________________
_________________________________________________
_________________________________________________

### Notes:
_________________________________________________
_________________________________________________
_________________________________________________

---

## 🚀 Next Steps After Testing

**If All Tests Pass:**
- ✅ Content Pillar is ready for production
- ✅ Proceed with Insights Realm integration
- ✅ Document learnings

**If Tests Fail:**
- ❌ Fix critical issues
- ❌ Re-test affected areas
- ❌ Update test plan based on findings

---

**This comprehensive test plan ensures the Content Pillar is solid before proceeding!** 🎯
