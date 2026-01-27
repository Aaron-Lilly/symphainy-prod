# Frontend State Management Migration Checklist

**Date:** January 24, 2026  
**Status:** 📋 **TRACKING DOCUMENT**  
**Purpose:** Track migration from GlobalSessionProvider to PlatformStateProvider

**Key Principle:** This is NOT just a grep exercise. Must capture semantic usage patterns.

---

## Migration Status

**Total Files:** ~30-35 (exact count TBD after full audit)  
**Already Migrated:** ~10 files  
**Partially Migrated:** ~5 files (have placeholders)  
**Needs Migration:** ~15-20 files  
**Progress:** ~30% (many already migrated, but have placeholders)

---

## Migration Checklist Format

For each file, document:

| File | Old Responsibility | New Source | Complexity | Notes |
|------|-------------------|------------|------------|-------|
| `path/to/file.tsx` | What GlobalSession was doing | What replaces it | Simple/Medium/Complex | Hidden issues found |

**Old Responsibility Options:**
- Identity? (session ID, user ID, tenant ID)
- Realm state? (content, insights, journey, outcomes)
- Orchestration? (workflow coordination)
- Convenience cache? (derived values)

**New Source Options:**
- SessionBoundary? (session identity)
- PlatformState? (realm state)
- Realm slice? (specific realm state)
- Derived selector? (computed values)

**Complexity:**
- **Simple:** Direct replacement
- **Medium:** Requires refactoring
- **Complex:** Reveals business logic issues

---

## Critical Components (Priority 1)

**Blocks:** Many other components

| File | Old Responsibility | New Source | Complexity | Notes | Status |
|------|-------------------|------------|------------|-------|--------|
| `shared/components/MainLayout.tsx` | Identity, convenience cache | SessionBoundary | ✅ Complete | Already migrated, one sessionStorage read (acceptable) | ✅ Done |
| `shared/agui/GuideAgentProvider.tsx` | Identity, orchestration | SessionBoundary | ✅ Complete | Already migrated, one sessionStorage read (acceptable) | ✅ Done |
| `shared/components/chatbot/InteractiveChat.tsx` | Identity (session ID for WebSocket) | SessionBoundary | ✅ Complete | Already migrated | ✅ Done |
| `shared/components/chatbot/InteractiveSecondaryChat.tsx` | Identity (session ID for WebSocket) | SessionBoundary | ✅ Complete | Already migrated | ✅ Done |
| `shared/components/chatbot/PrimaryChatbot.tsx` | Identity (session ID for WebSocket) | SessionBoundary | ✅ Complete | Already migrated | ✅ Done |
| `shared/components/chatbot/ChatAssistant.tsx` | TBD | TBD | TBD | Needs audit | ⏳ Pending |
| `shared/components/chatbot/SecondaryChatbot.tsx` | TBD | TBD | TBD | Needs audit | ⏳ Pending |

---

## Pillar Components (Priority 2)

**Migration Order:** Content → Insights → Journey → Outcomes

### Content Pillar

| File | Old Responsibility | New Source | Complexity | Notes | Status |
|------|-------------------|------------|------------|-------|--------|
| `components/content/FileUploader.tsx` | Identity ✅, Realm state ❌ | SessionBoundary ✅, PlatformState ❌ | Medium | Has placeholders (getPillarState/setPillarState), mock user_id, mock file fallback | ⏳ Pending |
| `components/content/FileDashboard.tsx` | Realm state (getPillarState) | PlatformState | Medium | Has placeholder getPillarState/setPillarState | ⏳ Pending |
| `components/content/FileList.tsx` | TBD | TBD | TBD | File not found - may not exist | ⏳ Pending |
| `app/(protected)/pillars/content/page.tsx` | Realm state, orchestration | PlatformState | ✅ Complete | Already using usePlatformState correctly | ✅ Done |
| `components/content/ParsePreview.tsx` | TBD | TBD | TBD | Needs audit | ⏳ Pending |
| (Add more as found) | | | | | |

### Insights Pillar

| File | Old Responsibility | New Source | Complexity | Notes | Status |
|------|-------------------|------------|------------|-------|--------|
| `components/insights/VARKInsightsPanel.tsx` | Identity ✅, Realm state ❌ | SessionBoundary ✅, PlatformState ❌ | Medium | Has placeholders (getPillarState/setPillarState) | ⏳ Pending |
| `components/insights/BusinessAnalysisPanel.tsx` | TBD | TBD | TBD | Needs audit | ⏳ Pending |
| `components/insights/ConversationalInsightsPanel.tsx` | Identity | SessionBoundary | ✅ Complete | Already migrated | ✅ Done |
| `app/(protected)/pillars/insights/page.tsx` | TBD | TBD | TBD | Needs audit | ⏳ Pending |
| `app/(protected)/pillars/insights/components/InsightsDashboard.tsx` | Identity | SessionBoundary | ✅ Complete | Already migrated | ✅ Done |
| `app/(protected)/pillars/insights/components/PermitProcessingSection.tsx` | TBD | TBD | TBD | Needs audit | ⏳ Pending |
| `app/(protected)/pillars/insights/components/PSOViewer.tsx` | TBD | TBD | TBD | Needs audit | ⏳ Pending |
| `app/(protected)/pillars/insights/components/DataMappingSection.tsx` | TBD | TBD | TBD | Needs audit | ⏳ Pending |
| (Add more as found) | | | | | |

### Journey Pillar

| File | Old Responsibility | New Source | Complexity | Notes | Status |
|------|-------------------|------------|------------|-------|--------|
| `components/operations/CoexistenceBluprint.tsx` | Identity ✅, Realm state ❌ | SessionBoundary ✅, PlatformState ❌ | Medium | Has placeholders (getPillarState/setPillarState) | ⏳ Pending |
| `components/operations/SOPGenerator.tsx` | TBD | TBD | TBD | Needs audit | ⏳ Pending |
| `app/(protected)/pillars/journey/page.tsx` | Identity, realm state, orchestration | SessionBoundary, PlatformState | ✅ Complete | Already using useSessionBoundary and usePlatformState | ✅ Done |
| `app/(protected)/pillars/journey/page-updated.tsx` | Realm state | PlatformState | Medium | Has wrapper functions (compatibility layer) | ⏳ Pending |
| (Add more as found) | | | | | |

### Outcomes Pillar

| File | Old Responsibility | New Source | Complexity | Notes | Status |
|------|-------------------|------------|------------|-------|--------|
| `app/(protected)/pillars/business-outcomes/page.tsx` | Realm state ✅, Orchestration ❌ | PlatformState ✅, Service hooks ❌ | Complex | Already using usePlatformState, but has TODO handlers (handleCreateBlueprint, handleCreatePOC, etc.) | ⏳ Pending |
| `components/experience/RoadmapTimeline.tsx` | TBD | TBD | TBD | Needs audit | ⏳ Pending |
| (Add more as found) | | | | | |

---

## Liaison Agents (Priority 2)

- [ ] `shared/services/content/ContentLiaisonAgent.tsx` (if exists)
- [ ] `shared/services/insights/InsightsLiaisonAgent.tsx` (if exists)
- [ ] `shared/services/operations/OperationsLiaisonAgent.tsx` (if exists)
- [ ] `shared/services/outcomes/SolutionLiaisonAgent.tsx` (if exists)
- [ ] `shared/services/experience/ExperienceLiaisonAgent.tsx` (if exists)

---

## Other Components (Priority 3)

- [ ] (Add as found during audit)

---

## Migration Pattern Reference

### Pattern 1: Session Token Access

**Before:**
```typescript
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
const { guideSessionToken } = useGlobalSession();
```

**After:**
```typescript
import { useSessionBoundary } from '@/shared/state/SessionBoundaryProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';

const { state: sessionState } = useSessionBoundary();
const sessionId = sessionState.sessionId;
```

### Pattern 2: Session State Access

**Before:**
```typescript
const { getPillarState, setPillarState } = useGlobalSession();
const pillarState = getPillarState('content');
```

**After:**
```typescript
const { getRealmState, setRealmState } = usePlatformState();
const realmState = getRealmState('content', 'files');
```

### Pattern 3: Session Creation

**Before:**
```typescript
const { setGuideSessionToken } = useGlobalSession();
await setGuideSessionToken(token);
```

**After:**
```typescript
const { createAnonymousSession, upgradeSession } = useSessionBoundary();
await createAnonymousSession();
await upgradeSession({ user_id, tenant_id, access_token });
```

---

## Testing Checklist

### Per-File Testing (After Each Migration)

- [ ] No TypeScript errors
- [ ] No context errors
- [ ] Component renders correctly
- [ ] Functionality works as expected
- [ ] State persists correctly
- [ ] No console errors
- [ ] **Post-Migration Invariant Check:**
  - [ ] No derived state stored locally that duplicates PlatformState
  - [ ] No session-derived values cached in refs or component state
  - [ ] No implicit assumption that `sessionId` never changes
  - [ ] All session/realm identity is *read*, not *remembered*

**One-Line Rule:**
> **If it depends on session or realm identity, it must be *read*, not *remembered*.**

### Cross-Pillar Navigation Test (After All Pillars Migrated)

- [ ] Navigate Content → Insights → Content
  - [ ] Content realm state is preserved
  - [ ] State does not leak to Insights
  - [ ] State correctly rehydrates from Runtime on return
  - [ ] No remounted defaults (state restored from PlatformState)
- [ ] Navigate Insights → Journey → Insights
  - [ ] Insights realm state is preserved
  - [ ] State does not leak to Journey
  - [ ] State correctly rehydrates from Runtime on return
- [ ] Navigate Journey → Outcomes → Journey
  - [ ] Journey realm state is preserved
  - [ ] State does not leak to Outcomes
  - [ ] State correctly rehydrates from Runtime on return
- [ ] Navigate Outcomes → Content → Outcomes
  - [ ] Outcomes realm state is preserved
  - [ ] State does not leak to Content
  - [ ] State correctly rehydrates from Runtime on return

---

## Hidden Issues Found

**Document any business logic issues discovered during migration:**

| File | Issue Type | Description | Resolution |
|------|-----------|-------------|------------|
| | Cross-realm coupling | | |
| | Business logic in state access | | |
| | Synchronous availability assumption | | |
| | Shadow session state | | |
| | "Sticky" IDs | | |

**Key Principle:**
> **This phase isn't just migration — it's archaeological truth-telling.**
> Finding business logic issues now is a win, not a setback.

---

## CI Guardrail

**After Phase 1 Complete:**
- [ ] Add CI check that fails if `GlobalSessionProvider` is imported anywhere
- [ ] Verify CI check passes (no imports found)
- [ ] Document CI check in build process

**CI Check Pattern:**
```bash
# In CI pipeline
if grep -r "GlobalSessionProvider\|useGlobalSession" --include="*.ts" --include="*.tsx" symphainy-frontend/; then
  echo "❌ ERROR: GlobalSessionProvider still imported"
  exit 1
fi
```

---

## Notes

- Update this checklist as files are migrated
- Document semantic usage for each file
- Mark files as complete when tested and verified
- Add new files found during migration
- Document hidden issues found

---

**Last Updated:** January 24, 2026  
**Status:** 📋 **TRACKING - Phase 1 In Progress**
