# Phase 2: Breaking Change Strategy

## Decision: Make Breaking Changes

**Rationale:**
1. This is a **fundamental refactoring**, not a feature addition
2. The architecture plan explicitly states: "Remove direct API calls" and "All API calls through service layer"
3. Backwards compatibility would leave technical debt and two ways to do the same thing
4. Now is the "hall pass" to break things - better to do it right now

## Strategy: Incremental Breaking Changes

### Approach
1. **Make `lib/api/*` functions internal** - Only accessible via hooks
2. **Update all components** to use hooks (no direct `lib/api/*` imports)
3. **Do it incrementally** by feature area (still testable)
4. **Remove direct access** - Components can't bypass the service layer

### Benefits
- ✅ Single source of truth for API calls
- ✅ Forces proper token management through SessionBoundaryProvider
- ✅ Cleaner architecture - one way to do things
- ✅ Easier to maintain - no legacy code paths
- ✅ Better error handling - consistent across all calls

### Implementation Plan

#### Step 1: Mark `lib/api/*` as Internal
- Add `@internal` JSDoc tags
- Add deprecation warnings for direct imports
- Keep functions working but warn developers

#### Step 2: Update Components by Feature Area
Update in logical groups (testable after each group):

**Group 1: File Management** ✅ (Already started)
- FileDashboard ✅
- FileUploader
- ParsePreview
- SimpleFileDashboard

**Group 2: Content Operations**
- ContentPillarUpload
- DataMash
- MetadataExtractor

**Group 3: Insights**
- VARKInsightsPanel
- ConversationalInsightsPanel
- InsightsFileSelector

**Group 4: Operations**
- CoexistenceBluprint
- WizardActive

**Group 5: Auth Forms**
- login-form
- register-form

**Group 6: Admin/Other**
- Admin components
- Other misc components

#### Step 3: Remove Direct Access
After all components are updated:
- Remove exports from `lib/api/*` (or make them truly internal)
- Components can only access via hooks
- Build will fail if anyone tries to import directly

## Migration Pattern

### Before (Direct Import):
```typescript
import { listFiles, deleteFile } from "@/lib/api/fms";

const token = sessionStorage.getItem("access_token");
const files = await listFiles(token);
await deleteFile(uuid, token);
```

### After (Hook-Based):
```typescript
import { useFileAPI } from "@/shared/hooks/useFileAPI";

const { listFiles, deleteFile } = useFileAPI();
const files = await listFiles(); // Token automatically included
await deleteFile(uuid); // Token automatically included
```

## Breaking Changes

### What Breaks
1. **Direct imports from `lib/api/*`** - No longer allowed
2. **Manual token passing** - Tokens come from SessionBoundaryProvider automatically
3. **Direct fetch calls in components** - Must use service layer hooks

### What Stays the Same
1. **API endpoints** - Same backend endpoints
2. **Request/response formats** - Same data structures
3. **Functionality** - Same features, just different access pattern

## Testing Strategy

### Incremental Testing
After each feature group:
1. Test that group's functionality
2. Verify no regressions
3. Check browser console for errors
4. Verify network requests are correct

### Final Verification
1. Build should fail if anyone imports `lib/api/*` directly
2. All components use hooks
3. No direct fetch calls in components
4. All API calls go through service layer

## Rollout Plan

1. **Week 1: File Management** (Already started)
   - ✅ FileDashboard
   - ⏳ FileUploader, ParsePreview, SimpleFileDashboard

2. **Week 1-2: Content & Insights**
   - Content operations
   - Insights components

3. **Week 2: Operations & Auth**
   - Operations components
   - Auth forms

4. **Week 2: Admin & Cleanup**
   - Admin components
   - Final audit
   - Remove direct access

## Success Criteria

- ✅ No direct `lib/api/*` imports in components
- ✅ All components use hooks
- ✅ All API calls go through service layer
- ✅ Service layer uses SessionBoundaryProvider for tokens
- ✅ Build fails if someone tries to import `lib/api/*` directly
- ✅ Consistent error handling across all API calls
