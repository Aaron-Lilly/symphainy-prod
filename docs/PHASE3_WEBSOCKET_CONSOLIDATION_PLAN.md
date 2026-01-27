# Phase 3: WebSocket Consolidation - Implementation Plan

**Date:** January 22, 2026  
**Status:** 📋 **IN PROGRESS**

---

## Goal

WebSocket only connects when session is Active. All WebSocket logic consolidated to follow session boundary pattern.

---

## Current State Audit

### ✅ Already Following Session Pattern
- **GuideAgentProvider** - ✅ Only connects when `SessionStatus === Active`
- **RuntimeClient** - ✅ Used by GuideAgentProvider (follows pattern)

### ⚠️ Needs Updates
- **useUnifiedAgentChat** - Creates RuntimeClient but doesn't check SessionStatus
- **ChatAssistant** - Creates its own RuntimeClient (should use GuideAgentProvider or useUnifiedAgentChat)
- **UnifiedWebSocketClient** - Used by ExperiencePlaneClient (needs session check)

---

## Implementation Tasks

### Task 1: Update useUnifiedAgentChat to Check SessionStatus
- Add `useSessionBoundary()` hook
- Only connect when `SessionStatus === Active`
- Disconnect when session becomes Invalid
- No retries on 403/401

### Task 2: Update ChatAssistant to Use useUnifiedAgentChat
- Remove direct RuntimeClient creation
- Use `useUnifiedAgentChat` hook instead
- Follow session boundary pattern

### Task 3: Update UnifiedWebSocketClient (if needed)
- Check if ExperiencePlaneClient uses it with session checks
- If not, add session boundary integration

### Task 4: Validation
- All WebSocket connections check SessionStatus
- No WebSocket connections when session is Invalid
- All components use consolidated pattern

---

## Success Criteria

- ✅ WebSocket only connects when `SessionStatus === Active`
- ✅ WebSocket disconnects on session invalidation
- ✅ No retries on 403/401
- ✅ All WebSocket logic follows session boundary pattern
- ✅ No duplicate WebSocket clients in components

---

## Files to Update

1. `shared/hooks/useUnifiedAgentChat.ts` - Add SessionStatus check
2. `shared/components/chatbot/ChatAssistant.tsx` - Use useUnifiedAgentChat
3. `shared/services/ExperiencePlaneClient.ts` - Check session integration (if needed)

---

## Next Steps

1. Update useUnifiedAgentChat
2. Update ChatAssistant
3. Run validation test
4. Proceed to Phase 4
