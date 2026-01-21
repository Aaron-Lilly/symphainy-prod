# Frontend Two-Phase Materialization Implementation

**Date:** January 19, 2026  
**Status:** ✅ **COMPLETE**

---

## ✅ Implementation Summary

All frontend components have been updated to support the two-phase materialization flow (upload → save).

---

## 📋 Changes Made

### 1. ContentAPIManager (`shared/managers/ContentAPIManager.ts`)

#### Added Types:
- `SaveMaterializationResponse` interface
- `boundary_contract_id` and `materialization_pending` to `UploadResponse`
- `boundary_contract_id` and `materialization_pending` to `ContentFile` interface

#### Updated `uploadFile()`:
- Now waits for execution completion to extract `boundary_contract_id` from execution artifacts
- Returns `boundary_contract_id` and `materialization_pending` in response
- Sets file status to "pending" if materialization is pending

#### Added `saveMaterialization()`:
- New method to call `/api/content/save_materialization` endpoint
- Accepts `boundaryContractId` and `fileId` parameters
- Returns success/error status with message

#### Updated `listFiles()`:
- Now uses Runtime intent submission (`list_files` intent)
- Waits for execution completion
- Extracts files from execution artifacts
- Maps `materialization_pending` and `boundary_contract_id` to response

---

### 2. FileUploader Component (`app/(protected)/pillars/content/components/FileUploader.tsx`)

#### Added State:
- `boundaryContractId`: Stores boundary contract ID from upload
- `fileId`: Stores file ID from upload
- `materializationPending`: Tracks if materialization is pending
- `saving`: Loading state for save operation
- `saveError`: Error message for save operation
- `saveSuccess`: Success state for save operation

#### Updated Upload Flow:
- Stores `boundary_contract_id` and `file_id` from upload response
- Detects `materialization_pending` status
- Shows different message if materialization is pending
- Only resets form if materialization is NOT pending (allows user to save)

#### Added Save Section:
- New UI section shown when `materializationPending === true`
- Amber-colored alert box with clear messaging
- Note: "For MVP purposes, files must be saved for parsing and other activities"
- "Save File" button with loading state
- Error and success messages for save operation
- Auto-resets form after successful save

#### User Experience:
1. User uploads file → sees "File uploaded! Please save..."
2. User clicks "Save File" → button shows "Saving..."
3. On success → shows "File saved successfully!" → form resets
4. On error → shows error message, allows retry

---

### 3. FileDashboard Component (`app/(protected)/pillars/content/components/FileDashboard.tsx`)

#### Updated File Mapping:
- Maps `boundary_contract_id` from API response
- Maps `materialization_pending` from API response
- Sets `materialization_pending` based on status or metadata

#### Updated Status Badges:
- **"Pending Save"** badge (amber) with clock icon for pending files
- **"Saved"** badge (blue) with checkmark icon for saved files
- Other status badges unchanged (Parsed, Validated, Parsing)

#### File Listing:
- Only shows saved files (backend filters by workspace scope)
- Files with `materialization_pending: true` show "Pending Save" badge
- Files that are saved show "Saved" badge

---

### 4. File Types (`shared/types/file.ts`)

#### Updated Interfaces:
- `ContentFile`: Added `boundary_contract_id` and `materialization_pending`
- `FileMetadata`: Added `boundary_contract_id` and `materialization_pending`

---

## 🎯 User Flow

### Complete Flow:
```
1. User selects file and uploads
   ↓
2. Backend creates pending boundary contract
   ↓
3. UI shows: "File uploaded! Please save to enable parsing..."
   [Save File Button]
   ↓
4. User clicks "Save File"
   ↓
5. Backend authorizes materialization (contract → active)
   ↓
6. UI shows: "File saved successfully!"
   ↓
7. File appears in FileDashboard with "Saved" badge
   ↓
8. File is now available for parsing
```

---

## 🔧 Technical Details

### API Endpoints Used:
- **Upload:** `/api/v1/content-pillar/upload-file` (FormData) → `ingest_file` intent
- **Save:** `/api/content/save_materialization?boundary_contract_id=...&file_id=...&tenant_id=...` (POST)
- **List:** `list_files` intent via Runtime

### Headers Required:
- `x-user-id`: User identifier
- `x-session-id`: Session identifier

### Execution Tracking:
- Upload execution tracked via `platformState.trackExecution()`
- Polls execution status to extract `boundary_contract_id`
- List files execution tracked and polled for results

---

## ✅ Testing Checklist

- [ ] Upload file → verify boundary_contract_id is stored
- [ ] Upload file → verify "Save File" button appears
- [ ] Click "Save File" → verify save API is called
- [ ] Save success → verify form resets
- [ ] Save error → verify error message shown
- [ ] FileDashboard → verify only saved files appear
- [ ] FileDashboard → verify "Saved" badge shows
- [ ] Verify workspace-scoped filtering (users only see their files)

---

## 📝 Notes

1. **Backend Dependency:** Requires backend two-phase flow to be working (✅ confirmed working)

2. **Error Handling:** All operations have proper error handling with user-friendly messages

3. **State Management:** Uses PlatformStateProvider for execution tracking

4. **User Experience:** Clear messaging about why files need to be saved

5. **Security:** Files are workspace-scoped (user_id, session_id) - enforced by backend

---

## 🚀 Next Steps

1. Test end-to-end flow in browser
2. Verify error cases (network failures, invalid IDs, etc.)
3. Test with multiple users (verify workspace isolation)
4. Update any additional UI components that reference file status

---

**Last Updated:** January 19, 2026
