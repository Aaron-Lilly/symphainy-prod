# Phase 1: Provider Consolidation - Migration Status

## ✅ Completed

1. **Archived Duplicate Providers**
   - ✅ `shared/agui/AuthProvider.tsx` → archived
   - ✅ `shared/agui/AppProviders.tsx` → archived
   - ✅ `shared/agui/SessionProvider.tsx` → archived
   - ✅ `shared/agui/GlobalSessionProvider.tsx` → archived
   - ✅ `shared/session/GlobalSessionProvider.tsx` → archived
   - ✅ `shared/components/SessionProvider.tsx` → archived

2. **Updated Core Components**
   - ✅ `shared/components/chatbot/ChatAssistant.tsx` → uses `useSessionBoundary`
   - ✅ `shared/components/chatbot/SecondaryChatbot.tsx` → uses `useSessionBoundary`
   - ✅ `shared/components/chatbot/PrimaryChatbot.tsx` → uses `useSessionBoundary`
   - ✅ `shared/testing/TestUtils.tsx` → uses `SessionBoundaryProvider`

3. **Updated Session Exports**
   - ✅ `shared/session/index.ts` → removed GlobalSessionProvider export

## ⚠️ In Progress - Needs Pillar State Migration

These components use `getPillarState`/`setPillarState` which need migration to `usePlatformState`'s realm state:

1. **`components/operations/CoexistenceBluprint.tsx`**
   - Uses: `getPillarState`, `setPillarState`, `guideSessionToken`
   - Migration: Use `usePlatformState` for realm state, `useSessionBoundary` for session

2. **`components/insights/VARKInsightsPanel.tsx`**
   - Uses: `getPillarState`, `setPillarState`, `guideSessionToken`
   - Migration: Use `usePlatformState` for realm state, `useSessionBoundary` for session

3. **`components/experience/RoadmapTimeline.tsx`**
   - Uses: `getPillarState`
   - Migration: Use `usePlatformState` for realm state

4. **`components/insights/ConversationalInsightsPanel.tsx`**
   - Uses: `guideSessionToken`
   - Migration: Use `useSessionBoundary` for session

5. **`components/content/SimpleFileDashboard.tsx`**
   - Uses: `guideSessionToken`
   - Migration: Use `useSessionBoundary` for session

6. **`components/content/ParsePreview.tsx`**
   - Uses: `getPillarState`, `setPillarState`, `guideSessionToken`
   - Migration: Use `usePlatformState` for realm state, `useSessionBoundary` for session

7. **`components/content/FileUploader.tsx`**
   - Uses: `getPillarState`, `setPillarState`, `guideSessionToken`
   - Migration: Use `usePlatformState` for realm state, `useSessionBoundary` for session

8. **`components/content/FileDashboard.tsx`**
   - Uses: `getPillarState`, `setPillarState`, `guideSessionToken`
   - Migration: Use `usePlatformState` for realm state, `useSessionBoundary` for session

## 📝 Pillar State Migration Notes

**Old API (GlobalSessionProvider):**
```typescript
const { getPillarState, setPillarState } = useGlobalSession();
const state = getPillarState("data"); // or "parsing", "operations", "insights", "experience"
await setPillarState("data", { files: [...] });
```

**New API (PlatformStateProvider):**
```typescript
const { getRealmState, setRealmState } = usePlatformState();
const state = getRealmState("content", "files"); // realm: "content" | "insights" | "journey" | "outcomes"
setRealmState("content", "files", [...]); // key-value pairs
```

**Pillar Name Mapping:**
- `"data"` → `"content"` realm
- `"parsing"` → `"content"` realm (parsing is part of content processing)
- `"operations"` → `"journey"` realm (operations is journey planning)
- `"insights"` → `"insights"` realm (same)
- `"experience"` → `"outcomes"` realm (experience is outcomes)

## Next Steps

1. Update remaining components to use `useSessionBoundary` for session tokens
2. Migrate `getPillarState`/`setPillarState` to `usePlatformState` realm state
3. Test build
4. Verify no regressions
