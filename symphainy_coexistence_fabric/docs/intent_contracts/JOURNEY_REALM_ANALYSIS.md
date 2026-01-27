# Journey Realm Intent Analysis

**Last Updated:** January 27, 2026  
**Purpose:** Cross-reference analysis between journey contracts, backend implementations, and frontend expectations.

---

## 1. Source Documents Analyzed

### Journey Contracts (5 journeys)
1. `journey_journey_coexistence_analysis` - Coexistence Analysis
2. `journey_journey_create_coexistence_blueprint` - Blueprint Creation
3. `journey_journey_sop_creation_chat` - SOP Creation via Chat
4. `journey_journey_workflow_sop_conversion` - Workflow/SOP Conversion
5. `journey_journey_workflow_sop_visualization` - Workflow/SOP Visualization

### Backend Implementation
- `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`
- `symphainy_platform/realms/journey/enabling_services/coexistence_analysis_service.py`
- `symphainy_platform/realms/journey/enabling_services/workflow_conversion_service.py`
- `symphainy_platform/realms/journey/agents/journey_liaison_agent.py`

### Frontend
- `symphainy-frontend/shared/managers/JourneyAPIManager.ts`

---

## 2. Key Findings & Recommendations

### Naming Alignment Needed

| Journey Contract Says | Backend Has | Frontend Uses | **Recommendation** |
|----------------------|-------------|---------------|-------------------|
| `initiate_sop_wizard` | `generate_sop_from_chat` | `processWizardConversation` | **Use `generate_sop_from_chat`** - matches backend |
| `chat_with_journey_agent` | `sop_chat_message` | `processWizardConversation` | **Use `sop_chat_message`** - more specific |
| `save_sop_from_chat` | (part of generate_sop_from_chat) | (integrated) | **Remove** - combined into generation |
| `create_workflow_from_sop` | `create_workflow` | `createWorkflow` | **Use `create_workflow`** - unified |
| `generate_sop_from_workflow` | `generate_sop` | `generateSOP` | **Use `generate_sop`** - unified |
| `select_workflow`, `select_sop` | (not implemented) | (not used) | **Remove** - discovery via separate APIs |
| `generate_visualization` | (part of workflow/sop creation) | (integrated) | **Remove** - integrated into creation |
| `identify_opportunities` | (part of analyze_coexistence) | (integrated) | **Remove** - combined with analysis |
| `create_blueprint` | (moved to Outcomes Realm) | `createBlueprint` | **Move to Outcomes Realm** |

### Missing from Journey Contracts

Frontend expects these intents NOT in current contracts:
- `optimize_process` - Workflow optimization
- `optimize_coexistence_with_content` - Direct content optimization
- `process_operations_conversation` - Operations conversation
- `process_operations_query` - Operations query
- `analyze_user_intent` - Guide agent intent analysis
- `get_journey_guidance` - Guide agent guidance
- `get_conversation_history` - Chat history retrieval
- `send_message_to_pillar_agent` - Cross-pillar messaging
- `get_pillar_conversation_history` - Cross-pillar chat history

### Blueprint Moved to Outcomes Realm

Backend comment: `create_blueprint` moved to Outcomes Realm (blueprints are Purpose-Bound Outcomes).

---

## 3. Recommended Journey Restructure

Based on implementation and frontend usage, recommend reorganizing into functional journeys:

### Coexistence Analysis Journey (2 intents)
1. **`analyze_coexistence`** - Analyze workflow for coexistence opportunities
2. **`optimize_process`** - Optimize workflow process (friction removal)

### SOP Management Journey (3 intents)
1. **`generate_sop`** - Generate SOP from workflow (or via chat mode)
2. **`generate_sop_from_chat`** - Start interactive SOP generation chat
3. **`sop_chat_message`** - Process chat message in SOP session

### Workflow Management Journey (2 intents)
1. **`create_workflow`** - Create workflow from SOP or BPMN file
2. **`get_workflow`** - Retrieve workflow data

### Chat/Agent Operations Journey (6 intents)
1. **`process_operations_conversation`** - Operations conversation
2. **`process_wizard_conversation`** - Wizard conversation
3. **`process_operations_query`** - Operations query
4. **`analyze_user_intent`** - Guide agent intent analysis
5. **`get_journey_guidance`** - Guide agent guidance
6. **`get_conversation_history`** - Chat history retrieval

### Cross-Pillar Operations Journey (2 intents)
1. **`send_message_to_pillar_agent`** - Cross-pillar messaging
2. **`get_pillar_conversation_history`** - Cross-pillar chat history

---

## 4. Implementation vs Contract Gaps

### Backend Implements (Journey Orchestrator)
| Intent | Handler | Status |
|--------|---------|--------|
| `optimize_process` | `_handle_optimize_process` | ✅ Implemented |
| `generate_sop` | `_handle_generate_sop` | ✅ Implemented |
| `create_workflow` | `_handle_create_workflow` | ✅ Implemented |
| `analyze_coexistence` | `_handle_analyze_coexistence` | ✅ Implemented |
| `generate_sop_from_chat` | `_handle_generate_sop_from_chat` | ✅ Implemented |
| `sop_chat_message` | `_handle_sop_chat_message` | ✅ Implemented |

### Backend SOA APIs
| API | Handler | Description |
|-----|---------|-------------|
| `optimize_process` | `_handle_optimize_process_soa` | Optimize workflow |
| `generate_sop` | `_handle_generate_sop_soa` | Generate SOP |
| `create_workflow` | `_handle_create_workflow_soa` | Create workflow |
| `generate_sop_from_structure` | `_handle_generate_sop_from_structure_soa` | Generate from structure |
| `get_workflow` | `_handle_get_workflow_soa` | Get workflow |
| `analyze_coexistence` | `_handle_analyze_coexistence_soa` | Analyze coexistence |
| `get_sop` | `_handle_get_sop_soa` | Get SOP |

### Frontend Expects
| Method | Intent | Implemented |
|--------|--------|-------------|
| `optimizeProcess` | `optimize_process` | ✅ Backend has |
| `generateSOP` | `generate_sop` | ✅ Backend has |
| `createWorkflow` | `create_workflow` | ✅ Backend has |
| `optimizeCoexistenceWithContent` | `optimize_coexistence_with_content` | ⚠️ Not in orchestrator |
| `analyzeCoexistence` | `analyze_coexistence` | ✅ Backend has |
| `createBlueprint` | `create_blueprint` | ⚠️ Moved to Outcomes |
| `processOperationsConversation` | `process_operations_conversation` | ⚠️ Not in orchestrator |
| `processWizardConversation` | `process_wizard_conversation` | ⚠️ Maps to sop_chat_message |
| `processOperationsQuery` | `process_operations_query` | ⚠️ Not in orchestrator |
| `analyzeUserIntent` | `analyze_user_intent` | ⚠️ Not in orchestrator |
| `getJourneyGuidance` | `get_journey_guidance` | ⚠️ Not in orchestrator |
| `getConversationHistory` | `get_conversation_history` | ⚠️ Not in orchestrator |
| `sendMessageToPillarAgent` | `send_message_to_pillar_agent` | ⚠️ Not in orchestrator |
| `getPillarConversationHistory` | `get_pillar_conversation_history` | ⚠️ Not in orchestrator |

---

## 5. Final Intent List for Journey Realm

Based on cross-reference analysis, these are the recommended intents:

### Coexistence Analysis Journey
1. **`analyze_coexistence`** - Analyze workflow for coexistence opportunities
2. **`optimize_process`** - Optimize workflow process

### SOP Management Journey
3. **`generate_sop`** - Generate SOP from workflow
4. **`generate_sop_from_chat`** - Start interactive SOP generation
5. **`sop_chat_message`** - Process chat message in SOP session
6. **`get_sop`** - Retrieve SOP data

### Workflow Management Journey
7. **`create_workflow`** - Create workflow from SOP or BPMN
8. **`get_workflow`** - Retrieve workflow data

### Guide Agent Operations Journey (to be implemented)
9. **`analyze_user_intent`** - Analyze user intent
10. **`get_journey_guidance`** - Get guidance from Guide Agent
11. **`get_conversation_history`** - Get conversation history

### Cross-Pillar Operations Journey (to be implemented)
12. **`send_message_to_pillar_agent`** - Send message to pillar agent
13. **`get_pillar_conversation_history`** - Get pillar conversation history

---

## 6. Key Decisions

| Decision | Rationale |
|----------|-----------|
| Use `generate_sop` not `generate_sop_from_workflow` | Simpler, matches implementation |
| Use `create_workflow` not `create_workflow_from_sop` | Unified - handles both SOP and BPMN |
| Use `sop_chat_message` not `chat_with_journey_agent` | More specific to SOP context |
| Remove `select_workflow`/`select_sop` | Discovery via list_artifacts, not separate intents |
| Remove `generate_visualization` | Integrated into workflow/SOP creation |
| Move `create_blueprint` to Outcomes | Blueprints are Purpose-Bound Outcomes |
| Add Guide Agent intents | Frontend expects them |
| Add Cross-Pillar intents | Frontend expects them |

---

## 7. Enabling Services

| Service | Purpose | Methods |
|---------|---------|---------|
| `WorkflowConversionService` | Workflow operations | `optimize_workflow`, `generate_sop`, `create_workflow`, `parse_bpmn_file`, `generate_sop_from_structure` |
| `CoexistenceAnalysisService` | Coexistence analysis | `analyze_coexistence`, `create_blueprint` |
| `VisualGenerationService` | Generate visuals | `generate_workflow_visual`, `generate_sop_visual` |

---

## 8. Agents

| Agent | Purpose | Methods |
|-------|---------|---------|
| `JourneyLiaisonAgent` | Interactive SOP generation | `initiate_sop_chat`, `process_chat_message`, `generate_sop_from_chat` |
| `SOPGenerationAgent` | SOP generation (specialist) | Delegated from JourneyLiaisonAgent |
| `CoexistenceAnalysisAgent` | Coexistence analysis | `analyze_coexistence` (optional) |

---

**Next Steps:**
1. Create comprehensive intent contracts for implemented intents
2. Mark missing intents as "TO BE IMPLEMENTED" in contracts
3. Update journey contracts to align with implementation

---

**Last Updated:** January 27, 2026  
**Owner:** Journey Realm Solution Team
