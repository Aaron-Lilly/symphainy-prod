# Phase 1: Semantic Audit of GlobalSessionProvider Usage

**Date:** January 24, 2026  
**Status:** 🔍 **IN PROGRESS**  
**Purpose:** Semantic audit (not just grep) - capture what GlobalSession was doing and what replaces it

---

## Audit Methodology

**This is NOT just a grep exercise.** For each file, we document:

1. **What role GlobalSession was playing:**
   - Identity? (session ID, user ID, tenant ID)
   - Realm state? (content, insights, journey, outcomes)
   - Orchestration? (workflow coordination)
   - Convenience cache? (derived values)

2. **What replaces it:**
   - SessionBoundary? (session identity)
   - PlatformState? (realm state)
   - Realm slice? (specific realm state)
   - Derived selector? (computed values)

3. **Migration complexity:**
   - Simple: Direct replacement
   - Medium: Requires refactoring
   - Complex: Reveals business logic issues

4. **Hidden issues:**
   - Cross-realm coupling
   - Business logic in state access
   - Synchronous availability assumptions
   - Shadow session state
   - "Sticky" IDs

---

## Critical Components (Priority 1)

### 1. `shared/components/MainLayout.tsx`

**Status:** ✅ **ALREADY MIGRATED** (uses `useSessionBoundary`)

**Old Responsibility:** Identity (session ID), convenience cache (access_token check)

**New Source:** `SessionBoundaryProvider` (session identity)

**Migration Complexity:** ✅ **COMPLETE**

**Notes:**
- Already using `useSessionBoundary()`
- Still has one `sessionStorage.getItem("access_token")` read (acceptable - read-only for API calls)
- No migration needed

---

### 2. `shared/agui/GuideAgentProvider.tsx`

**Status:** ✅ **ALREADY MIGRATED** (uses `useSessionBoundary`)

**Old Responsibility:** Identity (session ID), orchestration (WebSocket connection)

**New Source:** `SessionBoundaryProvider` (session identity)

**Migration Complexity:** ✅ **COMPLETE**

**Notes:**
- Already using `useSessionBoundary()`
- Has one `sessionStorage.getItem("access_token")` read (acceptable - read-only for RuntimeClient)
- No migration needed

---

### 3. `shared/components/chatbot/InteractiveChat.tsx`

**Status:** ✅ **ALREADY MIGRATED** (uses `useSessionBoundary`)

**Old Responsibility:** Identity (session ID for WebSocket)

**New Source:** `SessionBoundaryProvider` (session identity)

**Migration Complexity:** ✅ **COMPLETE**

**Notes:**
- Already using `useSessionBoundary()`
- No migration needed

---

### 4. `shared/components/chatbot/InteractiveSecondaryChat.tsx`

**Status:** ✅ **ALREADY MIGRATED** (uses `useSessionBoundary`)

**Old Responsibility:** Identity (session ID for WebSocket)

**New Source:** `SessionBoundaryProvider` (session identity)

**Migration Complexity:** ✅ **COMPLETE**

**Notes:**
- Already using `useSessionBoundary()`
- No migration needed

---

## Pillar Components (Priority 2)

### Content Pillar

#### 1. `components/content/FileUploader.tsx`

**Status:** ⚠️ **PARTIALLY MIGRATED** (has placeholders)

**Old Responsibility:** 
- Identity (session ID) ✅ Migrated
- Realm state (getPillarState/setPillarState) ❌ Placeholder

**New Source:**
- `SessionBoundaryProvider` (session identity) ✅
- `PlatformStateProvider` (realm state) ❌ TODO

**Migration Complexity:** **Medium** - Requires replacing placeholders

**Hidden Issues Found:**
- ❌ Placeholder `getPillarState()` returns `null`
- ❌ Placeholder `setPillarState()` does nothing
- ❌ Mock `user_id: "mock-user"` (line 169)
- ❌ Mock file fallback when sessionId === null (lines 232-288)

**Action Required:**
1. Replace `getPillarState()` with `getRealmState('content', key)`
2. Replace `setPillarState()` with `setRealmState('content', key, value)`
3. Remove mock `user_id: "mock-user"`
4. Remove mock file fallback

---

#### 2. `components/content/FileDashboard.tsx`

**Status:** ⚠️ **NEEDS AUDIT**

**Action:** Read file to determine semantic usage

---

#### 3. `components/content/FileList.tsx`

**Status:** ⚠️ **NEEDS AUDIT**

**Action:** Read file to determine semantic usage

---

#### 4. `app/(protected)/pillars/content/page.tsx`

**Status:** ⚠️ **NEEDS AUDIT**

**Action:** Read file to determine semantic usage

---

### Insights Pillar

#### 1. `components/insights/VARKInsightsPanel.tsx`

**Status:** ⚠️ **PARTIALLY MIGRATED** (has placeholders)

**Old Responsibility:**
- Identity (session ID) ✅ Migrated
- Realm state (getPillarState/setPillarState) ❌ Placeholder

**New Source:**
- `SessionBoundaryProvider` (session identity) ✅
- `PlatformStateProvider` (realm state) ❌ TODO

**Migration Complexity:** **Medium** - Requires replacing placeholders

**Hidden Issues Found:**
- ❌ Placeholder `getPillarState()` returns `null`
- ❌ Placeholder `setPillarState()` does nothing

**Action Required:**
1. Replace `getPillarState()` with `getRealmState('insights', key)`
2. Replace `setPillarState()` with `setRealmState('insights', key, value)`

---

#### 2. `components/insights/BusinessAnalysisPanel.tsx`

**Status:** ⚠️ **NEEDS AUDIT**

**Action:** Read file to determine semantic usage

---

#### 3. `app/(protected)/pillars/insights/page.tsx`

**Status:** ⚠️ **NEEDS AUDIT**

**Action:** Read file to determine semantic usage

---

#### 4. `app/(protected)/pillars/insights/components/InsightsDashboard.tsx`

**Status:** ⚠️ **NEEDS AUDIT**

**Action:** Read file to determine semantic usage

---

### Journey Pillar

#### 1. `components/operations/CoexistenceBluprint.tsx`

**Status:** ⚠️ **PARTIALLY MIGRATED** (has placeholders)

**Old Responsibility:**
- Identity (session ID) ✅ Migrated
- Realm state (getPillarState/setPillarState) ❌ Placeholder

**New Source:**
- `SessionBoundaryProvider` (session identity) ✅
- `PlatformStateProvider` (realm state) ❌ TODO

**Migration Complexity:** **Medium** - Requires replacing placeholders

**Hidden Issues Found:**
- ❌ Placeholder `getPillarState()` returns `null`
- ❌ Placeholder `setPillarState()` does nothing

**Action Required:**
1. Replace `getPillarState()` with `getRealmState('journey', key)`
2. Replace `setPillarState()` with `setRealmState('journey', key, value)`

---

#### 2. `components/operations/SOPGenerator.tsx`

**Status:** ⚠️ **NEEDS AUDIT**

**Action:** Read file to determine semantic usage

---

#### 3. `app/(protected)/pillars/journey/page.tsx`

**Status:** ⚠️ **NEEDS AUDIT**

**Action:** Read file to determine semantic usage

---

#### 4. `app/(protected)/pillars/journey/page-updated.tsx`

**Status:** ⚠️ **PARTIALLY MIGRATED**

**Notes:**
- Has wrapper functions: `getPillarState()` → `getRealmState()`, `setPillarState()` → `setRealmState()`
- This is a compatibility layer - may need to remove wrapper and use directly

**Action:** Review if wrapper is needed or can be removed

---

### Outcomes Pillar

#### 1. `app/(protected)/pillars/business-outcomes/page.tsx`

**Status:** ⚠️ **PARTIALLY MIGRATED** (has TODOs)

**Old Responsibility:**
- Realm state (cross-pillar data access)
- Orchestration (artifact generation)

**New Source:**
- `PlatformStateProvider` (realm state) ✅ Already using
- Service layer hooks ❌ TODOs for handlers

**Migration Complexity:** **Complex** - Has TODOs for artifact generation

**Hidden Issues Found:**
- ❌ TODO handlers: `handleCreateBlueprint()`, `handleCreatePOC()`, `handleGenerateRoadmap()`, `handleExportArtifact()`
- ✅ Already using `usePlatformState()` for realm state

**Action Required:**
1. Implement TODO handlers (Task 4.4 in Phase 4)
2. Connect to Outcomes realm endpoints

---

## Other Components (Priority 3)

### Files Found (Need Audit):

- `components/content/ParsePreview.tsx`
- `components/experience/RoadmapTimeline.tsx`
- `components/insights/ConversationalInsightsPanel.tsx`
- `app/(protected)/pillars/insights/components/PermitProcessingSection.tsx`
- `app/(protected)/pillars/insights/components/PSOViewer.tsx`
- `app/(protected)/pillars/insights/components/DataMappingSection.tsx`
- `shared/components/chatbot/ChatAssistant.tsx`
- `shared/components/chatbot/SecondaryChatbot.tsx`
- `shared/components/chatbot/PrimaryChatbot.tsx` ✅ Already migrated

**Action:** Audit each file to determine semantic usage

---

## Summary

### Migration Status

**Total Files:** ~52 (exact count TBD after full audit)

**Already Migrated:** ~8 files (MainLayout, GuideAgentProvider, InteractiveChat, InteractiveSecondaryChat, PrimaryChatbot, etc.)

**Partially Migrated:** ~5 files (FileUploader, VARKInsightsPanel, CoexistenceBluprint, business-outcomes/page, journey/page-updated)

**Needs Migration:** ~39 files (TBD after full audit)

**Needs Audit:** ~20+ files (need to read to determine semantic usage)

---

## Next Steps

1. **Complete Semantic Audit** - Read remaining files to document semantic usage
2. **Update MIGRATION_CHECKLIST.md** - Add all files with semantic columns
3. **Prioritize by Complexity** - Start with simple, then medium, then complex
4. **Begin Migration** - Start with Task 1.2 (Core Infrastructure - already mostly done)

---

**Last Updated:** January 24, 2026  
**Status:** 🔍 **AUDIT IN PROGRESS**
