# Phase 2: Service Layer Standardization - Progress Update

**Date:** January 22, 2026  
**Status:** In Progress - Breaking Changes Implementation

---

## ✅ Completed Today

### 1. Marked All `lib/api/*` Files as Internal
- ✅ `lib/api/fms.ts` - Marked as internal
- ✅ `lib/api/auth.ts` - Marked as internal
- ✅ `lib/api/content.ts` - Marked as internal
- ✅ `lib/api/insights.ts` - Marked as internal
- ✅ `lib/api/operations.ts` - Marked as internal
- ✅ `lib/api/global.ts` - Marked as internal
- ✅ `lib/api/file-processing.ts` - Marked as internal
- ✅ `lib/api/admin.ts` - Marked as internal

All files now have:
- `@internal` JSDoc tag
- Deprecation warnings
- Clear migration path to hooks

### 2. Enhanced useFileAPI Hook
- ✅ Added `uploadAndProcessFile()` function
- ✅ Supports file processing operations
- ✅ Automatically gets tokens from SessionBoundaryProvider

### 3. Updated Components (File Management Group)
- ✅ `FileDashboard.tsx` - Uses `useFileAPI()` hook
- ✅ `FileUploader.tsx` - Uses `useFileAPI()` hook
- ⏳ `ParsePreview.tsx` - Next
- ⏳ `SimpleFileDashboard.tsx` - Next

### 4. Build Status
- ✅ Build passes successfully
- ✅ No TypeScript errors
- ✅ All imports updated

---

## 📋 Next Steps

### Immediate (File Management Group)
1. **Update ParsePreview.tsx**
   - Replace direct `lib/api/fms` imports
   - Use `useFileAPI()` hook
   - Remove manual token passing

2. **Update SimpleFileDashboard.tsx**
   - Replace direct `lib/api/fms` imports
   - Use `useFileAPI()` hook
   - Remove manual token passing

### Next Groups (After File Management)
3. **Content Operations Group**
   - ContentPillarUpload
   - DataMash
   - MetadataExtractor
   - Need to create `useContentAPI()` hook

4. **Insights Group**
   - VARKInsightsPanel
   - ConversationalInsightsPanel
   - InsightsFileSelector
   - Need to create `useInsightsAPI()` hook

5. **Operations Group**
   - CoexistenceBluprint
   - WizardActive
   - Need to create `useOperationsAPI()` hook

---

## Breaking Changes Summary

### What's Breaking
1. **Direct imports from `lib/api/*`** - No longer allowed
2. **Manual token passing** - Tokens come from SessionBoundaryProvider automatically
3. **Direct fetch calls in components** - Must use service layer hooks

### Migration Pattern

**Before:**
```typescript
import { listFiles, uploadFile } from "@/lib/api/fms";
const token = sessionStorage.getItem("access_token");
const files = await listFiles(token);
```

**After:**
```typescript
import { useFileAPI } from "@/shared/hooks/useFileAPI";
const { listFiles, uploadFile } = useFileAPI();
const files = await listFiles(); // Token automatic
```

---

## Success Metrics

- ✅ All `lib/api/*` files marked as internal
- ✅ File Management group 50% complete (2/4 components)
- ✅ Build passes
- ✅ No TypeScript errors
- ⏳ All components using hooks (in progress)

---

## Notes

- Breaking changes are intentional and necessary
- Components will fail to build if they import `lib/api/*` directly
- This enforces proper architecture
- Service layer automatically manages tokens
- Consistent error handling across all API calls
