# Frontend Session Migration Checklist

**Date:** January 22, 2026  
**Status:** 🔴 **INCOMPLETE MIGRATION**  
**Total Files:** 52 files using `GlobalSessionProvider`

---

## Migration Status

- ✅ **Root Layout:** Using `PlatformStateProvider` (correct)
- ❌ **52 Components:** Still using `GlobalSessionProvider` (needs migration)

---

## Priority 1: Core Infrastructure (BLOCKING)

These components block many others and must be migrated first.

### 1. MainLayout ⚠️ CRITICAL
- **File:** `shared/components/MainLayout.tsx`
- **Status:** ❌ Uses `useGlobalSession()`
- **Impact:** Blocks all protected routes
- **Priority:** HIGHEST
- **Estimated Time:** 30 min

### 2. GuideAgentProvider ⚠️ CRITICAL
- **File:** `shared/agui/GuideAgentProvider.tsx`
- **Status:** ❌ Uses `useGlobalSession()`
- **Impact:** Blocks all agent chat functionality
- **Priority:** HIGHEST
- **Estimated Time:** 30 min

### 3. InteractiveChat ⚠️ CRITICAL
- **File:** `shared/components/chatbot/InteractiveChat.tsx`
- **Status:** ❌ Uses `useGlobalSession()`
- **Impact:** Blocks primary chat
- **Priority:** HIGH
- **Estimated Time:** 20 min

### 4. InteractiveSecondaryChat ⚠️ CRITICAL
- **File:** `shared/components/chatbot/InteractiveSecondaryChat.tsx`
- **Status:** ❌ Uses `useGlobalSession()`
- **Impact:** Blocks secondary chat
- **Priority:** HIGH
- **Estimated Time:** 20 min

---

## Priority 2: Liaison Agents (5 files)

### 5. ContentLiaisonAgent
- **File:** `components/liaison-agents/ContentLiaisonAgent.tsx`
- **Status:** ❌ Uses `useGlobalSession()`
- **Priority:** MEDIUM
- **Estimated Time:** 15 min

### 6. InsightsLiaisonAgent
- **File:** `components/liaison-agents/InsightsLiaisonAgent.tsx`
- **Status:** ❌ Uses `useGlobalSession()`
- **Priority:** MEDIUM
- **Estimated Time:** 15 min

### 7. OperationsLiaisonAgent
- **File:** `components/liaison-agents/OperationsLiaisonAgent.tsx`
- **Status:** ❌ Uses `useGlobalSession()`
- **Priority:** MEDIUM
- **Estimated Time:** 15 min

### 8. SolutionLiaisonAgent
- **File:** `components/liaison-agents/SolutionLiaisonAgent.tsx`
- **Status:** ❌ Uses `useGlobalSession()`
- **Priority:** MEDIUM
- **Estimated Time:** 15 min

### 9. ExperienceLiaisonAgent
- **File:** `components/liaison-agents/ExperienceLiaisonAgent.tsx`
- **Status:** ❌ Uses `useGlobalSession()`
- **Priority:** MEDIUM
- **Estimated Time:** 15 min

---

## Priority 3: Pillar Components (20+ files)

### Content Pillar
- [ ] `app/(protected)/pillars/content/components/FileUploader.tsx`
- [ ] `app/(protected)/pillars/content/components/FileDashboard.tsx`
- [ ] `app/(protected)/pillars/content/components/FileParser.tsx`
- [ ] `app/(protected)/pillars/content/components/ParsePreview.tsx`
- [ ] `app/(protected)/pillars/content/components/ParsePreviewNew.tsx`
- [ ] `app/(protected)/pillars/content/components/FileSelector.tsx`
- [ ] `app/(protected)/pillars/content/components/ContentPillarUpload.tsx`
- [ ] `components/content/FileUploader.tsx`
- [ ] `components/content/FileDashboard.tsx`
- [ ] `components/content/ParsePreview.tsx`
- [ ] `components/content/SimpleFileDashboard.tsx`

### Insights Pillar
- [ ] `app/(protected)/pillars/insights/components/InsightsDashboard.tsx`
- [ ] `app/(protected)/pillars/insights/components/PermitProcessingSection.tsx`
- [ ] `app/(protected)/pillars/insights/components/PSOViewer.tsx`
- [ ] `app/(protected)/pillars/insights/components/DataMappingSection.tsx`
- [ ] `components/insights/VARKInsightsPanel.tsx`
- [ ] `components/insights/ConversationalInsightsPanel.tsx`

### Journey Pillar
- [ ] `app/(protected)/pillars/journey/page-updated.tsx`
- [ ] `app/(protected)/pillars/journey/components/WizardActive/hooks.ts`
- [ ] `app/(protected)/pillars/journey/components/CoexistenceBlueprint/hooks.ts`
- [ ] `components/operations/WizardActive.tsx`
- [ ] `components/operations/CoexistenceBluprint.tsx`

### Outcomes Pillar
- (Check for any usage)

---

## Priority 4: Other Components (15+ files)

- [ ] `components/experience/RoadmapTimeline.tsx`
- [ ] `shared/components/chatbot/SecondaryChatbot.tsx`
- [ ] `shared/components/chatbot/PrimaryChatbot.tsx`
- [ ] `shared/components/chatbot/ChatAssistant.tsx`
- [ ] `shared/agui/AGUIEventProvider.tsx`
- [ ] `shared/agui/AuthProvider.tsx` (check if needed)
- [ ] `shared/agui/AppProviders.tsx` (old version - DELETE)

---

## Priority 5: Tests & Documentation (10+ files)

- [ ] `tests/e2e/semantic-components.spec.ts`
- [ ] `__tests__/GlobalSessionProvider.test.tsx`
- [ ] `__tests__/FileDashboard.test.tsx`
- [ ] `__tests__/content-pillar.test.tsx`
- [ ] `docs/troubleshooting.md`
- [ ] `docs/state-management.md`
- [ ] `docs/archived_plans/SESSION_MIGRATION_GUIDE.md` (update)
- [ ] `status.md`

---

## Migration Pattern

### Step 1: Update Imports

**Before:**
```typescript
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
```

**After:**
```typescript
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useAuth } from '@/shared/auth/AuthProvider'; // if auth token needed
```

### Step 2: Update Hook Usage

**Before:**
```typescript
const { guideSessionToken } = useGlobalSession();
```

**After:**
```typescript
// Option 1: Use session ID from PlatformState
const { state } = usePlatformState();
const sessionId = state.session.sessionId;

// Option 2: Use auth token (for backward compatibility)
const { sessionToken } = useAuth();
```

### Step 3: Update State Access

**Before:**
```typescript
const { getPillarState, setPillarState } = useGlobalSession();
const pillarState = getPillarState('content');
```

**After:**
```typescript
const { getRealmState, setRealmState } = usePlatformState();
const realmState = getRealmState('content', 'key');
```

### Step 4: Test

1. Check for context errors
2. Verify session state access
3. Test component functionality
4. Check browser console for errors

---

## Cleanup Tasks (After Migration)

1. **Delete Old Files:**
   - [ ] `shared/agui/GlobalSessionProvider.tsx`
   - [ ] `shared/agui/AppProviders.tsx` (old version)
   - [ ] `shared/session/GlobalSessionProvider.tsx` (if duplicate)

2. **Remove Unused Imports:**
   - [ ] Search for `useGlobalSession` (should be 0 results)
   - [ ] Search for `GlobalSessionProvider` (should be 0 results)

3. **Update Documentation:**
   - [ ] Mark migration as complete
   - [ ] Update architecture docs
   - [ ] Update component docs

---

## Testing Checklist

After each migration:

- [ ] No context errors in browser console
- [ ] Component renders correctly
- [ ] Session state accessible
- [ ] No TypeScript errors
- [ ] No runtime errors
- [ ] Functionality works as expected

---

## Estimated Timeline

- **Phase 1 (Core Infrastructure):** 2 hours
- **Phase 2 (Liaison Agents):** 1.5 hours
- **Phase 3 (Pillar Components):** 4-6 hours
- **Phase 4 (Other Components):** 2-3 hours
- **Phase 5 (Tests & Cleanup):** 1-2 hours

**Total:** 10-14 hours

---

## Notes

- Migrate incrementally (one component at a time)
- Test after each migration
- Rollback if issues found
- Document any special cases

---

**Last Updated:** January 22, 2026  
**Status:** Ready for migration execution
