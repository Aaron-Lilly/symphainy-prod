# Content Pillar Integration Test Execution Guide

**Date:** January 2026  
**Status:** 🧪 **TEST EXECUTION GUIDE**  
**Purpose:** Step-by-step guide for running Content Pillar integration tests

---

## 🚀 Quick Start

### 1. Start Backend Services
```bash
cd /home/founders/demoversion/symphainy_source_code
docker-compose up -d
```

**Verify services are running:**
```bash
# Check Runtime
curl http://localhost:8000/health

# Check Experience Plane
curl http://localhost:8001/health

# Check Content Realm (via Runtime)
curl http://localhost:8000/api/realms
```

### 2. Start Frontend Dev Server
```bash
cd symphainy-frontend
npm run dev
```

**Verify frontend is running:**
- Open browser: http://localhost:3000
- Should see login page or landing page

### 3. Run Automated Checks
```bash
cd /home/founders/demoversion/symphainy_source_code
./scripts/test_content_pillar.sh
```

---

## 🧪 Manual Test Execution

### Test Phase 1: Component Rendering

#### Test 1.1: Component Import & Rendering
1. Navigate to: http://localhost:3000/pillars/content
2. Open browser DevTools (F12)
3. Check Console tab for errors
4. Verify all components render:
   - FileUploader (top section)
   - FileDashboard (file list)
   - FileParser (parsing section)
   - ParsePreview (preview section)
   - DataMash (semantic layer section)

**Expected:**
- ✅ No console errors
- ✅ All components visible
- ✅ No TypeScript errors in console

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

---

#### Test 1.2: PlatformStateProvider Integration
1. Open browser console
2. Type: `window.__PLATFORM_STATE__` (if set by provider)
3. Check React DevTools:
   - Find PlatformStateProvider in component tree
   - Verify `state.realm.content` exists
   - Verify `setRealmState` function exists

**Expected:**
- ✅ PlatformStateProvider in component tree
- ✅ `state.realm.content` structure exists
- ✅ No context errors

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

---

#### Test 1.3: ContentAPIManager Integration
1. In browser console, verify hook works:
   ```javascript
   // This should work if component is mounted
   // Check React DevTools for ContentAPIManager instance
   ```
2. Verify methods are accessible (check component code)

**Expected:**
- ✅ ContentAPIManager accessible via hook
- ✅ Methods available (uploadFile, listFiles, etc.)

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

---

### Test Phase 2: File Upload Flow

#### Test 2.1: File Upload (Happy Path)
**Prerequisites:**
- User authenticated
- Session created

**Steps:**
1. Navigate to Content Pillar
2. In FileUploader:
   - Select "Structured Data" → "CSV"
   - Click "Choose File" or drag & drop a test CSV file
   - Click "Upload File"
3. Wait for upload to complete
4. Check FileDashboard for uploaded file

**Expected:**
- ✅ Upload progress indicator shows
- ✅ Toast notification: "File uploaded successfully!"
- ✅ File appears in FileDashboard
- ✅ File stored in `state.realm.content.files`
- ✅ Execution tracked in PlatformStateProvider

**Check Runtime:**
```bash
# Check if intent was submitted
curl http://localhost:8000/api/execution/{execution_id}/status
```

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

#### Test 2.2: File Upload with Copybook
**Steps:**
1. In FileUploader:
   - Select "Structured Data" → "Binary/Mainframe"
   - Upload binary file
   - Upload copybook file
   - Click "Upload File"
2. Verify both files upload

**Expected:**
- ✅ Both files upload successfully
- ✅ Copybook reference stored
- ✅ File ready for parsing

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

#### Test 2.3: File Upload Error Handling
**Steps:**
1. Try uploading invalid file (e.g., wrong type)
2. Try uploading binary without copybook
3. Verify error messages display

**Expected:**
- ✅ Error messages display correctly
- ✅ State doesn't break
- ✅ User can retry

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

### Test Phase 3: File Parsing Flow

#### Test 3.1: Parse File (Happy Path)
**Prerequisites:**
- File uploaded successfully (from Test 2.1)

**Steps:**
1. In FileParser:
   - Select uploaded file from dropdown
   - Click "Parse File" button
2. Wait for parsing to complete
3. Check ParsePreview for parsed file

**Expected:**
- ✅ Parse button shows loading state
- ✅ `parse_content` intent submitted to Runtime
- ✅ Execution tracked
- ✅ Toast notification: "File parsed successfully!"
- ✅ Parsed file appears in ParsePreview
- ✅ Preview data displays

**Check Runtime:**
```bash
# Check execution status
curl http://localhost:8000/api/execution/{execution_id}/status
```

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

#### Test 3.2: Parse Binary File with Copybook
**Prerequisites:**
- Binary file uploaded with copybook (from Test 2.2)

**Steps:**
1. Select binary file in FileParser
2. Verify copybook is selected
3. Click "Parse File"
4. Wait for parsing

**Expected:**
- ✅ Parsing uses copybook correctly
- ✅ Parsed data is structured
- ✅ Preview shows parsed data

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

#### Test 3.3: Parse Preview Display
**Prerequisites:**
- File parsed successfully (from Test 3.1)

**Steps:**
1. Navigate to ParsePreview component
2. Select parsed file from dropdown
3. Click "Generate Preview" (if needed)
4. Verify preview displays

**Expected:**
- ✅ Preview generates successfully
- ✅ Data displays in structured format
- ✅ Tables/charts render correctly

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

### Test Phase 4: Embeddings & Semantic Layer

#### Test 4.1: Extract Embeddings
**Prerequisites:**
- File parsed successfully (from Test 3.1)

**Steps:**
1. Navigate to DataMash component
2. Select parsed file
3. Click "Create Embeddings" button
4. Wait for extraction to complete

**Expected:**
- ✅ `extract_embeddings` intent submitted
- ✅ Embeddings created successfully
- ✅ Toast notification shows success
- ✅ Embeddings stored in ArangoDB
- ✅ Lineage tracked in Supabase

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

#### Test 4.2: Preview Embeddings
**Prerequisites:**
- Embeddings created (from Test 4.1)

**Steps:**
1. In DataMash, select content_id
2. Click "Preview Embeddings"
3. Verify preview displays

**Expected:**
- ✅ Preview generates successfully
- ✅ Semantic metadata displays
- ✅ Column meanings shown

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

#### Test 4.3: Semantic Interpretation
**Prerequisites:**
- Embeddings created (from Test 4.1)

**Steps:**
1. Request semantic interpretation
2. Verify interpretation displays

**Expected:**
- ✅ `get_semantic_interpretation` intent submitted
- ✅ Interpretation returned
- ✅ Data displays correctly

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

### Test Phase 5: State Management

#### Test 5.1: Realm State Persistence
**Steps:**
1. Upload a file (from Test 2.1)
2. Navigate away from Content Pillar
3. Navigate back
4. Verify file still in state

**Expected:**
- ✅ State persists
- ✅ Files still accessible
- ✅ No data loss

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

#### Test 5.2: State Synchronization
**Steps:**
1. Upload file via FileUploader
2. Check FileDashboard
3. Verify both components see same state

**Expected:**
- ✅ State synchronized across components
- ✅ No stale data
- ✅ Updates propagate correctly

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

### Test Phase 6: Error Handling & Edge Cases

#### Test 6.1: Network Errors
**Steps:**
1. Disconnect network (or stop backend)
2. Attempt file upload
3. Verify error handling

**Expected:**
- ✅ Error message displays
- ✅ State doesn't break
- ✅ User can retry

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

#### Test 6.2: Session Expiry
**Steps:**
1. Let session expire (or manually clear)
2. Attempt file operation
3. Verify re-authentication flow

**Expected:**
- ✅ Session expiry detected
- ✅ User redirected to login
- ✅ State preserved

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

#### Test 6.3: Concurrent Operations
**Steps:**
1. Upload multiple files simultaneously
2. Parse multiple files simultaneously
3. Verify all operations complete

**Expected:**
- ✅ All operations tracked
- ✅ No race conditions
- ✅ State updates correctly

**Result:** ⬜ PASS / ⬜ FAIL / ⬜ SKIP

**Notes:**
_________________________________________________

---

## 📊 Test Results Summary

**Test Date:** ___________  
**Tester:** ___________  
**Environment:** ___________  

### Phase 1: Component Rendering
- Test 1.1: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 1.2: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 1.3: ⬜ PASS / ⬜ FAIL / ⬜ SKIP

### Phase 2: File Upload Flow
- Test 2.1: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 2.2: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 2.3: ⬜ PASS / ⬜ FAIL / ⬜ SKIP

### Phase 3: File Parsing Flow
- Test 3.1: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 3.2: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 3.3: ⬜ PASS / ⬜ FAIL / ⬜ SKIP

### Phase 4: Embeddings & Semantic Layer
- Test 4.1: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 4.2: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 4.3: ⬜ PASS / ⬜ FAIL / ⬜ SKIP

### Phase 5: State Management
- Test 5.1: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 5.2: ⬜ PASS / ⬜ FAIL / ⬜ SKIP

### Phase 6: Error Handling
- Test 6.1: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 6.2: ⬜ PASS / ⬜ FAIL / ⬜ SKIP
- Test 6.3: ⬜ PASS / ⬜ FAIL / ⬜ SKIP

### Overall Results
- **Total Tests:** 18
- **Passed:** ___
- **Failed:** ___
- **Skipped:** ___

### Critical Issues Found:
_________________________________________________
_________________________________________________

### Non-Critical Issues Found:
_________________________________________________
_________________________________________________

### Recommendations:
_________________________________________________
_________________________________________________

---

## 🚀 Next Steps

**If All Tests Pass:**
- ✅ Content Pillar is ready
- ✅ Proceed with Insights Realm integration
- ✅ Document learnings

**If Tests Fail:**
- ❌ Fix critical issues
- ❌ Re-test affected areas
- ❌ Update test plan based on findings

---

**Happy Testing!** 🎯
