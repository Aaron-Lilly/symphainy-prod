# Phase 5 Legacy API Migration Plan

**Date:** January 25, 2026  
**Status:** 📋 **PLANNING**  
**Purpose:** Complete migration of all legacy API managers to intent-based architecture

---

## Executive Summary

You're absolutely right - **none of the "acceptable" legacy managers are actually acceptable**. We need to complete the migration to 100% intent-based architecture. This plan addresses all remaining legacy API managers and direct API calls.

---

## 🔴 Critical Legacy Issues Found

### 1. OperationsService Direct Calls (Still in Use!)

**Location:** `app/(protected)/pillars/journey/`
- `page-updated.tsx` - Multiple OperationsService calls
- `components/WizardActive/hooks.ts` - OperationsService calls

**Calls Found:**
- `OperationsService.createCoexistenceBlueprintDirectly()`
- `OperationsService.convertSopToWorkflowReal()`
- `OperationsService.convertWorkflowToSopReal()`
- `OperationsService.extractSopFromDocx()`
- `OperationsService.processOperationsConversation()`
- `OperationsService.processOperationsWizardConversation()`
- `OperationsService.processOperationsQuery()`

**Status:** 🔴 **CRITICAL** - Still being used in Journey pillar!

**Action Required:**
- Migrate all OperationsService calls to JourneyAPIManager
- Remove OperationsService usage from Journey pillar
- Verify all operations use intent-based API

---

### 2. OperationsAPIManager (Legacy)

**Location:** `shared/managers/OperationsAPIManager.ts`

**Status:** ⚠️ **LEGACY** - Not used in pillars (good), but should be deprecated

**Action Required:**
- Document as deprecated
- Ensure no new code uses it
- Plan removal after JourneyAPIManager migration complete

---

### 3. BusinessOutcomesAPIManager (Legacy)

**Location:** `shared/managers/BusinessOutcomesAPIManager.ts`

**Status:** ⚠️ **LEGACY** - Not used in pillars (good), but should be deprecated

**Action Required:**
- Document as deprecated
- Ensure no new code uses it
- Plan removal after OutcomesAPIManager migration complete

---

### 4. AdminAPIManager (Admin Operations)

**Location:** `shared/managers/AdminAPIManager.ts`

**Status:** ⚠️ **NEEDS REVIEW** - Used in admin pages

**Usage:**
- Admin dashboard components
- Control room views
- Developer views
- Business user views

**Question:** Should admin operations use intent-based API?

**Recommendation:** 
- **YES** - Admin operations should also use intent-based API for consistency
- Admin intents can be separate (e.g., `admin_*` intents)
- Maintains architectural consistency

**Action Required:**
- Create Admin realm intents (if needed)
- Migrate AdminAPIManager to intent-based API
- Or document why admin operations are exception (if justified)

---

### 5. SessionAPIManager (Session Management)

**Location:** `shared/managers/SessionAPIManager.ts`

**Status:** ⚠️ **NEEDS REVIEW** - Infrastructure layer

**Usage:**
- Session creation
- Session state management

**Question:** Should session management use intent-based API?

**Recommendation:**
- **YES** - Session operations should use intent-based API
- Session intents: `create_session`, `get_session_state`, etc.
- Maintains architectural consistency

**Action Required:**
- Create session intents (if needed)
- Migrate SessionAPIManager to intent-based API
- Or document why session management is exception (if justified)

---

### 6. GuideAgentAPIManager (Guide Agent)

**Location:** `shared/managers/GuideAgentAPIManager.ts`

**Status:** ⚠️ **NEEDS REVIEW** - Agent infrastructure

**Usage:**
- Guide agent interactions
- Intent analysis
- Journey guidance

**Question:** Should agent operations use intent-based API?

**Recommendation:**
- **YES** - Agent operations should use intent-based API
- Agent intents: `analyze_user_intent`, `get_journey_guidance`, etc.
- Maintains architectural consistency

**Action Required:**
- Create agent intents (if needed)
- Migrate GuideAgentAPIManager to intent-based API
- Or document why agent operations are exception (if justified)

---

### 7. LiaisonAgentsAPIManager (Liaison Agents)

**Location:** `shared/managers/LiaisonAgentsAPIManager.ts`

**Status:** ⚠️ **NEEDS REVIEW** - Agent infrastructure

**Usage:**
- Liaison agent interactions
- Pillar-specific conversations

**Question:** Should agent operations use intent-based API?

**Recommendation:**
- **YES** - Agent operations should use intent-based API
- Agent intents: `send_message_to_pillar_agent`, `get_pillar_conversation_history`, etc.
- Maintains architectural consistency

**Action Required:**
- Create agent intents (if needed)
- Migrate LiaisonAgentsAPIManager to intent-based API
- Or document why agent operations are exception (if justified)

---

## Proposed Task 5.6: Complete Legacy API Migration

### Goal
Migrate ALL remaining legacy API managers to intent-based architecture.

### Scope

#### Critical (User-Facing)
1. **OperationsService Migration** (Journey Pillar)
   - Migrate all OperationsService calls to JourneyAPIManager
   - Remove OperationsService from Journey pillar
   - Verify intent-based flow

#### High Priority (Infrastructure)
2. **SessionAPIManager Migration**
   - Create session intents (if needed)
   - Migrate to intent-based API
   - Or document exception with justification

3. **GuideAgentAPIManager Migration**
   - Create agent intents (if needed)
   - Migrate to intent-based API
   - Or document exception with justification

4. **LiaisonAgentsAPIManager Migration**
   - Create agent intents (if needed)
   - Migrate to intent-based API
   - Or document exception with justification

#### Medium Priority (Admin)
5. **AdminAPIManager Migration**
   - Create admin intents (if needed)
   - Migrate to intent-based API
   - Or document exception with justification

#### Low Priority (Deprecation)
6. **OperationsAPIManager Deprecation**
   - Document as deprecated
   - Ensure no usage
   - Plan removal

7. **BusinessOutcomesAPIManager Deprecation**
   - Document as deprecated
   - Ensure no usage
   - Plan removal

---

## Detailed Migration Plan

### Task 5.6.1: OperationsService Migration (CRITICAL)

**Priority:** 🔴 **CRITICAL**

**Files to Fix:**
1. `app/(protected)/pillars/journey/page-updated.tsx`
   - `OperationsService.createCoexistenceBlueprintDirectly()` → `JourneyAPIManager.createBlueprint()`
   - `OperationsService.convertSopToWorkflowReal()` → `JourneyAPIManager.createWorkflow()`
   - `OperationsService.convertWorkflowToSopReal()` → `JourneyAPIManager.generateSOP()`
   - `OperationsService.extractSopFromDocx()` → Need to create intent or use ContentAPIManager
   - `OperationsService.processOperationsConversation()` → Need to create intent or use agent API
   - `OperationsService.processOperationsWizardConversation()` → Need to create intent or use agent API
   - `OperationsService.processOperationsQuery()` → Need to create intent or use agent API

2. `app/(protected)/pillars/journey/components/WizardActive/hooks.ts`
   - `OperationsService.processOperationsWizardConversation()` → Need to create intent or use agent API
   - `OperationsService.processOperationsQuery()` → Need to create intent or use agent API

**Action:**
1. Audit each OperationsService call
2. Map to appropriate intent or API manager
3. Migrate to intent-based API
4. Remove OperationsService imports
5. Verify functionality

**Estimated Time:** 3-5 hours

---

### Task 5.6.2: SessionAPIManager Migration

**Priority:** ⚠️ **HIGH**

**Current Operations:**
- `createUserSession()` - Direct API call
- `getSessionDetails()` - Direct API call
- `getSessionState()` - Direct API call

**Options:**
1. **Create Session Intents:**
   - `create_session` intent
   - `get_session_details` intent
   - `get_session_state` intent

2. **Keep Direct API (Justify):**
   - Document why session management is exception
   - Must have strong architectural justification

**Recommendation:** Create session intents for consistency

**Estimated Time:** 2-3 hours

---

### Task 5.6.3: GuideAgentAPIManager Migration

**Priority:** ⚠️ **HIGH**

**Current Operations:**
- `analyzeUserIntent()` - Direct API call
- `getJourneyGuidance()` - Direct API call
- `getConversationHistory()` - Direct API call

**Options:**
1. **Create Agent Intents:**
   - `analyze_user_intent` intent
   - `get_journey_guidance` intent
   - `get_conversation_history` intent

2. **Keep Direct API (Justify):**
   - Document why agent operations are exception
   - Must have strong architectural justification

**Recommendation:** Create agent intents for consistency

**Estimated Time:** 2-3 hours

---

### Task 5.6.4: LiaisonAgentsAPIManager Migration

**Priority:** ⚠️ **HIGH**

**Current Operations:**
- `sendMessageToPillarAgent()` - Direct API call
- `getPillarConversationHistory()` - Direct API call

**Options:**
1. **Create Agent Intents:**
   - `send_message_to_pillar_agent` intent
   - `get_pillar_conversation_history` intent

2. **Keep Direct API (Justify):**
   - Document why agent operations are exception
   - Must have strong architectural justification

**Recommendation:** Create agent intents for consistency

**Estimated Time:** 2-3 hours

---

### Task 5.6.5: AdminAPIManager Migration

**Priority:** ⚠️ **MEDIUM**

**Current Operations:**
- Many admin operations (health, metrics, statistics, etc.)

**Options:**
1. **Create Admin Intents:**
   - `admin_*` intents for all admin operations
   - Maintains consistency

2. **Keep Direct API (Justify):**
   - Document why admin operations are exception
   - Must have strong architectural justification

**Recommendation:** Create admin intents for consistency (can be lower priority)

**Estimated Time:** 4-6 hours

---

### Task 5.6.6: OperationsAPIManager Deprecation

**Priority:** ⚠️ **LOW**

**Action:**
1. Document as deprecated
2. Add deprecation warnings
3. Ensure no new usage
4. Plan removal after OperationsService migration

**Estimated Time:** 1 hour

---

### Task 5.6.7: BusinessOutcomesAPIManager Deprecation

**Priority:** ⚠️ **LOW**

**Action:**
1. Document as deprecated
2. Add deprecation warnings
3. Ensure no new usage
4. Plan removal

**Estimated Time:** 1 hour

---

## Total Estimated Time

- **Task 5.6.1 (OperationsService):** 3-5 hours 🔴
- **Task 5.6.2 (SessionAPIManager):** 2-3 hours ⚠️
- **Task 5.6.3 (GuideAgentAPIManager):** 2-3 hours ⚠️
- **Task 5.6.4 (LiaisonAgentsAPIManager):** 2-3 hours ⚠️
- **Task 5.6.5 (AdminAPIManager):** 4-6 hours ⚠️
- **Task 5.6.6 (OperationsAPIManager):** 1 hour
- **Task 5.6.7 (BusinessOutcomesAPIManager):** 1 hour

**Total:** 15-22 hours (2-3 days)

---

## Priority Order

### 🔴 Critical (Fix Before Testing)
1. **Task 5.6.1: OperationsService Migration** - Still used in Journey pillar!

### ⚠️ High Priority (Fix Before Testing)
2. **Task 5.6.2: SessionAPIManager Migration**
3. **Task 5.6.3: GuideAgentAPIManager Migration**
4. **Task 5.6.4: LiaisonAgentsAPIManager Migration**

### ⚠️ Medium Priority (Can Do After Testing)
5. **Task 5.6.5: AdminAPIManager Migration**

### ⚠️ Low Priority (Documentation)
6. **Task 5.6.6: OperationsAPIManager Deprecation**
7. **Task 5.6.7: BusinessOutcomesAPIManager Deprecation**

---

## Recommendation

**Add Task 5.6 to Phase 5** with the following priority:

1. **Task 5.6.1 (OperationsService)** - 🔴 **CRITICAL** - Must fix before testing
2. **Tasks 5.6.2-5.6.4 (Infrastructure)** - ⚠️ **HIGH** - Should fix before testing
3. **Task 5.6.5 (Admin)** - ⚠️ **MEDIUM** - Can do after testing
4. **Tasks 5.6.6-5.6.7 (Deprecation)** - ⚠️ **LOW** - Documentation only

**Total Critical/High Priority:** 9-14 hours (1.5-2 days)

---

## Updated Phase 5 Tasks

### ✅ Completed
- Task 5.3: Purpose-Bound Outcomes Lifecycle
- Task 5.4: Code Quality & Documentation
- Task 5.5: Final Anti-Pattern Fix (save_materialization)

### ⏳ Remaining
- Task 5.6: Complete Legacy API Migration (NEW)
- Task 5.2: Records of Fact Promotion
- Task 5.1: TTL Enforcement

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 📋 **PLAN READY - AWAITING APPROVAL**
