# Phase 5: State Management Audit

**Date:** January 22, 2026  
**Status:** ✅ **COMPLETE**

---

## 1. Jotai Atoms Audit

### 1.1 Atom Files Found

#### `shared/atoms/chatbot-atoms.ts`
**Atoms:**
- `mainChatbotOpenAtom` (boolean)
- `chatbotAgentInfoAtom` (object)
- `shouldShowSecondaryChatbotAtom` (derived)
- `primaryChatbotHeightAtom` (derived)
- `secondaryChatbotPositionAtom` (derived)
- `primaryChatbotTransformAtom` (derived)
- `chatInputFocusedAtom` (boolean)
- `messageComposingAtom` (boolean)
- `businessAnalysisResultAtom` (any)
- `visualizationResultAtom` (any)
- `anomalyDetectionResultAtom` (any)
- `edaAnalysisResultAtom` (any)

**Status:** ⚠️ **DUPLICATE** - Also defined in `core.ts`

#### `shared/state/core.ts`
**Atoms:**
- `mainChatbotOpenAtom` (boolean) - ⚠️ **DUPLICATE**
- `chatbotAgentInfoAtom` (object) - ⚠️ **DUPLICATE**
- `chatInputFocusedAtom` (boolean) - ⚠️ **DUPLICATE**
- `messageComposingAtom` (boolean) - ⚠️ **DUPLICATE**
- `businessAnalysisResultAtom` (any) - ⚠️ **DUPLICATE**
- `visualizationResultAtom` (any) - ⚠️ **DUPLICATE**
- `anomalyDetectionResultAtom` (any) - ⚠️ **DUPLICATE**
- `edaAnalysisResultAtom` (any) - ⚠️ **DUPLICATE**

**Also includes:**
- `StateManager` interface
- `ApplicationStateManager` class (not used with Jotai)

**Status:** ⚠️ **DUPLICATE** - Should be consolidated

#### `shared/state/derived_atoms.ts`
**Atoms:**
- `shouldShowSecondaryChatbotAtom` (derived) - ⚠️ **DUPLICATE**
- `primaryChatbotHeightAtom` (derived) - ⚠️ **DUPLICATE**
- `secondaryChatbotPositionAtom` (derived) - ⚠️ **DUPLICATE**
- `primaryChatbotTransformAtom` (derived) - ⚠️ **DUPLICATE**
- `allAnalysisResultsAtom` (derived)
- `uiStateSummaryAtom` (derived)
- `stateConsistencyAtom` (derived)

**Imports from:** `core.ts`

**Status:** ⚠️ **DUPLICATE** - Derived atoms also in `chatbot-atoms.ts`

### 1.2 Atom Usage Analysis

**Files Using Atoms (20 total):**
1. `MainLayout.tsx` - Uses `useAtomValue` for chatbot state
2. `InteractiveChat.tsx` - Uses `useSetAtom` for agent info
3. `InteractiveSecondaryChat.tsx` - Uses atoms
4. `PrimaryChatbot.tsx` - Uses atoms
5. `SecondaryChatbot.tsx` - Uses atoms
6. `ChatPanelUI.tsx` - Uses atoms
7. `SecondaryChatPanelUI.tsx` - Uses atoms
8. `journey/page.tsx` - Uses `useSetAtom` for agent info
9. `journey/page-updated.tsx` - Uses `useSetAtom` for agent info
10. `WizardActive.tsx` - Uses atoms
11. `CoexistenceBluprint.tsx` - Uses atoms
12. `business-outcomes/page.tsx` - Uses atoms
13. `insights/page.tsx` - Uses atoms
14. `content/page.tsx` - Uses atoms
15. Plus 5 more files

**Import Patterns:**
- `from "../atoms"` (via index.ts)
- `from "@/shared/atoms/chatbot-atoms"`
- `from "@/shared/state/core"`

---

## 2. useState for Global Concerns Audit

### 2.1 Global useState Found

**In Components:**
- Most `useState` is local component state (OK)
- Some components manage UI state that should be global:
  - Chatbot open/closed state (already in atoms)
  - Sidebar state (in PlatformStateProvider ✅)
  - Current pillar (in PlatformStateProvider ✅)

**Status:** ✅ **GOOD** - Most global state already in providers

---

## 3. Context Providers Audit

### 3.1 Providers Found

#### `SessionBoundaryProvider` ✅
**Purpose:** Session lifecycle management
**State:** Session state (sessionId, status, etc.)
**Scope:** Session-scoped
**Status:** ✅ **CORRECT** - Single authority for session

#### `AGUIStateProvider` ✅
**Purpose:** AGUI (experience layer) state
**State:** AGUI state (artifacts, journey steps, workflows)
**Scope:** Session-scoped (clears on session invalidation)
**Status:** ✅ **CORRECT** - Already properly integrated

#### `PlatformStateProvider` ✅
**Purpose:** Platform state (execution, realm, UI)
**State:**
- Execution state (executions, activeExecutions)
- Realm state (content, insights, journey, outcomes)
- UI state (currentPillar, sidebarOpen, notifications)
**Scope:** Should be session-scoped
**Status:** ⚠️ **NEEDS WORK** - Missing chatbot/UI atoms

#### `AuthProvider` ✅
**Purpose:** Authentication state
**State:** User, tokens, auth status
**Scope:** Session-scoped
**Status:** ✅ **CORRECT**

#### Other Providers:
- `AppProvider` - AGUI app state
- `GuideAgentProvider` - Agent chat state
- `ExperienceLayerProvider` - Experience layer context
- `UserContextProviderComponent` - User context

**Status:** ✅ **REVIEWED** - Most are fine

---

## 4. State Lifecycle Audit

### 4.1 Session Scoping

**✅ Session-Scoped:**
- `SessionBoundaryProvider` - Clears on session invalidation ✅
- `AGUIStateProvider` - Clears on session invalidation ✅

**⚠️ Needs Session Scoping:**
- `PlatformStateProvider` - Should clear on session invalidation
- Jotai atoms - Currently persist across sessions ⚠️

### 4.2 State Clearing

**Current Behavior:**
- `SessionBoundaryProvider` clears session state on `Invalid` ✅
- `AGUIStateProvider` clears AGUI state on `Invalid` ✅
- `PlatformStateProvider` - No clearing logic ⚠️
- Jotai atoms - No clearing logic ⚠️

**Needs:**
- Add state clearing to `PlatformStateProvider`
- Move atoms to provider so they can be cleared
- Clear all state on `SessionStatus.Invalid`

---

## 5. Duplicate Definitions

### 5.1 Duplicate Atoms

**Found:**
- `mainChatbotOpenAtom` - in `chatbot-atoms.ts` and `core.ts`
- `chatbotAgentInfoAtom` - in `chatbot-atoms.ts` and `core.ts`
- `chatInputFocusedAtom` - in `chatbot-atoms.ts` and `core.ts`
- `messageComposingAtom` - in `chatbot-atoms.ts` and `core.ts`
- Analysis result atoms - in `chatbot-atoms.ts` and `core.ts`
- Derived atoms - in `chatbot-atoms.ts` and `derived_atoms.ts`

**Action Required:**
- Consolidate to single source
- Remove duplicates
- Update all imports

---

## 6. Summary

### Issues Found:
1. ⚠️ **Duplicate atom definitions** (chatbot-atoms.ts vs core.ts)
2. ⚠️ **Atoms not in PlatformStateProvider** (should be consolidated)
3. ⚠️ **Atoms persist across sessions** (should be session-scoped)
4. ⚠️ **No state clearing on session invalidation** (for atoms)
5. ⚠️ **20 files using direct atom imports** (should use provider methods)

### What's Good:
1. ✅ `AGUIStateProvider` properly session-scoped
2. ✅ `SessionBoundaryProvider` properly manages session
3. ✅ Most global state already in providers
4. ✅ Provider hierarchy is correct

### Action Plan:
1. Consolidate duplicate atoms
2. Move atoms to `PlatformStateProvider`
3. Add state clearing on session invalidation
4. Update components to use provider methods
5. Remove standalone atom files (or mark deprecated)

---

## Next Steps

1. **Consolidate Atoms** - Remove duplicates, single source
2. **Move to PlatformStateProvider** - Add chatbot/UI state
3. **Add Session Scoping** - Clear state on invalidation
4. **Update Components** - Use provider methods
5. **Validation** - Test state lifecycle
