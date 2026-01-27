# Task 5.6.1: OperationsService Migration Plan

**Date:** January 25, 2026  
**Status:** 🔄 **IN PROGRESS**  
**Priority:** 🔴 **CRITICAL**

---

## Executive Summary

OperationsService is still being used in Journey pillar, bypassing intent-based architecture. This task migrates all OperationsService calls to intent-based API.

---

## OperationsService Calls to Migrate

### File 1: `app/(protected)/pillars/journey/page-updated.tsx`

**Status:** ⚠️ **LEGACY FILE** - Not imported anywhere, but should be migrated or removed

**Calls:**
1. `OperationsService.createCoexistenceBlueprintDirectly()` → `JourneyAPIManager.optimizeCoexistenceWithContent()` or `createBlueprint()`
2. `OperationsService.convertSopToWorkflowReal()` → `JourneyAPIManager.createWorkflow()`
3. `OperationsService.convertWorkflowToSopReal()` → `JourneyAPIManager.generateSOP()`
4. `OperationsService.extractSopFromDocx()` → Need ContentAPIManager or new intent
5. `OperationsService.processOperationsConversation()` → Agent intent (need to create)

### File 2: `app/(protected)/pillars/journey/components/WizardActive/hooks.ts`

**Status:** ✅ **ACTIVE** - Currently in use

**Calls:**
1. `OperationsService.processOperationsWizardConversation()` → Agent intent (need to create)
2. `OperationsService.processOperationsQuery()` → Agent intent (need to create)

---

## Migration Strategy

### Strategy 1: Direct Intent Mapping (Clear Cases)

**1. createCoexistenceBlueprintDirectly**
- **Current:** `OperationsService.createCoexistenceBlueprintDirectly(userRequirements, conversationId, token)`
- **Migrate to:** `JourneyAPIManager.optimizeCoexistenceWithContent(sopContent, workflowContent)`
- **Note:** Need to extract sopContent and workflowContent from userRequirements

**2. convertSopToWorkflowReal**
- **Current:** `OperationsService.convertSopToWorkflowReal(sopData, token)`
- **Migrate to:** `JourneyAPIManager.createWorkflow(sopId, workflowOptions)`
- **Note:** Need sopId, not sopData. May need to create SOP first or use file_id.

**3. convertWorkflowToSopReal**
- **Current:** `OperationsService.convertWorkflowToSopReal(workflowData, token)`
- **Migrate to:** `JourneyAPIManager.generateSOP(workflowId, sopOptions)`
- **Note:** Need workflowId, not workflowData. May need to create workflow first or use file_id.

### Strategy 2: New Intents Needed

**4. extractSopFromDocx**
- **Option A:** Use ContentAPIManager to parse file, then extract SOP
- **Option B:** Create new intent `extract_sop_from_docx`
- **Recommendation:** Option A (use existing ContentAPIManager.parseFile())

**5. processOperationsConversation**
- **Create Intent:** `process_operations_conversation`
- **Parameters:** `message`, `conversation_id`, `context`
- **Realm:** Journey (or Agent realm if we create one)

**6. processOperationsWizardConversation**
- **Create Intent:** `process_wizard_conversation`
- **Parameters:** `message`, `session_id`, `context`
- **Realm:** Journey (or Agent realm if we create one)

**7. processOperationsQuery**
- **Create Intent:** `process_operations_query`
- **Parameters:** `query`, `session_id`, `context`
- **Realm:** Journey (or Agent realm if we create one)

---

## Implementation Plan

### Phase 1: Clear Mappings (Immediate)

1. **Migrate createCoexistenceBlueprintDirectly**
   - Update `page-updated.tsx` to use `JourneyAPIManager.optimizeCoexistenceWithContent()`
   - Extract sopContent and workflowContent from userRequirements

2. **Migrate convertSopToWorkflowReal**
   - Update `page-updated.tsx` to use `JourneyAPIManager.createWorkflow()`
   - Handle sopId requirement (may need to create SOP first or use file_id)

3. **Migrate convertWorkflowToSopReal**
   - Update `page-updated.tsx` to use `JourneyAPIManager.generateSOP()`
   - Handle workflowId requirement (may need to create workflow first or use file_id)

### Phase 2: Agent Operations (Requires New Intents)

4. **Create Agent Intents**
   - `process_operations_conversation`
   - `process_wizard_conversation`
   - `process_operations_query`

5. **Add Methods to JourneyAPIManager**
   - `processOperationsConversation()`
   - `processWizardConversation()`
   - `processOperationsQuery()`

6. **Migrate WizardActive/hooks.ts**
   - Replace OperationsService calls with JourneyAPIManager methods

### Phase 3: File Operations

7. **Migrate extractSopFromDocx**
   - Use ContentAPIManager.parseFile() to parse DOCX
   - Extract SOP from parsed content
   - Or create new intent if needed

---

## Decision Needed

**Question:** Should agent operations (conversation, wizard) use Journey realm intents or a separate Agent realm?

**Options:**
1. **Journey Realm Intents** - `process_operations_conversation`, `process_wizard_conversation`, etc.
2. **Agent Realm Intents** - Create new Agent realm for agent operations
3. **Use Agent API Managers** - Migrate GuideAgentAPIManager/LiaisonAgentsAPIManager to intent-based API

**Recommendation:** Option 1 (Journey realm intents) for now, can refactor to Agent realm later if needed.

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 🔄 **PLANNING**
