# Operations Realm Intent Analysis

**Last Updated:** January 27, 2026  
**Purpose:** Cross-reference analysis between journey contracts, backend implementations, and frontend expectations.

---

## 1. Naming Clarification

The Operations Realm was previously called "Journey Realm" but was renamed to avoid collision with "journey" as a platform capability:

| Term | Definition |
|------|------------|
| **Operations Realm** | User-facing domain for workflow/SOP management and coexistence analysis |
| **Journey** | Platform capability (invisible to users) - orchestration mechanism |
| **OperationsSolution** | Platform construct that composes journeys and exposes SOA APIs |

---

## 2. Source Documents Analyzed

### Journey Contracts (4 journeys)
1. `journey_operations_workflow_management` - Workflow Management
2. `journey_operations_sop_management` - SOP Management
3. `journey_operations_coexistence_analysis` - Coexistence Analysis
4. `journey_operations_process_optimization` - Process Optimization

### Backend Implementation
- `symphainy_coexistence_fabric/symphainy_platform/realms/operations/intent_services/`
- `symphainy_platform/solutions/operations_solution/`

### Frontend
- `symphainy-frontend/shared/managers/JourneyAPIManager.ts` (to be renamed OperationsAPIManager)

---

## 3. Final Intent List for Operations Realm

### Workflow Management Journey
1. **`create_workflow`** - Create workflow from SOP or BPMN file
2. **`get_workflow`** - Retrieve workflow data

### SOP Management Journey
3. **`generate_sop`** - Generate SOP from workflow
4. **`generate_sop_from_chat`** - Start interactive SOP generation
5. **`sop_chat_message`** - Process chat message in SOP session
6. **`get_sop`** - Retrieve SOP data

### Coexistence Analysis Journey
7. **`analyze_coexistence`** - Analyze workflow for coexistence opportunities

### Process Optimization Journey
8. **`optimize_process`** - Optimize workflow process

---

## 4. Implementation Status

### Intent Services (Coexistence Fabric)
| Intent | Service | Status |
|--------|---------|--------|
| `optimize_process` | `OptimizeProcessService` | ✅ Implemented |
| `generate_sop` | `GenerateSOPService` | ✅ Implemented |
| `create_workflow` | `CreateWorkflowService` | ✅ Implemented |
| `analyze_coexistence` | `AnalyzeCoexistenceService` | ✅ Implemented |
| `generate_sop_from_chat` | `GenerateSOPFromChatService` | ✅ Implemented |
| `sop_chat_message` | `SOPChatMessageService` | ✅ Implemented |

### SOA APIs
| API | Handler | Description |
|-----|---------|-------------|
| `optimize_process` | `process_optimization_journey` | Optimize workflow |
| `generate_sop` | `sop_management_journey` | Generate SOP |
| `create_workflow` | `workflow_management_journey` | Create workflow |
| `analyze_coexistence` | `coexistence_analysis_journey` | Analyze coexistence |
| `start_sop_chat` | `sop_management_journey` | Start SOP chat session |

### Frontend Expects
| Method | Intent | Implemented |
|--------|--------|-------------|
| `optimizeProcess` | `optimize_process` | ✅ Backend has |
| `generateSOP` | `generate_sop` | ✅ Backend has |
| `createWorkflow` | `create_workflow` | ✅ Backend has |
| `analyzeCoexistence` | `analyze_coexistence` | ✅ Backend has |
| `processWizardConversation` | `sop_chat_message` | ✅ Backend has |

---

## 5. Key Decisions

| Decision | Rationale |
|----------|-----------|
| Rename "Journey Realm" to "Operations Realm" | Avoid collision with platform "journey" capability |
| Use `generate_sop` not `generate_sop_from_workflow` | Simpler, matches implementation |
| Use `create_workflow` not `create_workflow_from_sop` | Unified - handles both SOP and BPMN |
| Use `sop_chat_message` not `chat_with_journey_agent` | More specific to SOP context |
| Move `create_blueprint` to Outcomes Realm | Blueprints are Purpose-Bound Outcomes |

---

## 6. Enabling Services

| Service | Purpose | Methods |
|---------|---------|---------|
| `OptimizeProcessService` | Process optimization | `execute()` → friction points, recommendations |
| `GenerateSOPService` | SOP generation | `execute()` → SOP document |
| `CreateWorkflowService` | Workflow creation | `execute()` → workflow structure |
| `AnalyzeCoexistenceService` | Coexistence analysis | `execute()` → opportunities, risks |
| `GenerateSOPFromChatService` | Chat session init | `execute()` → session context |
| `SOPChatMessageService` | Chat message processing | `execute()` → response, updated draft |

---

## 7. Agents (Agentic-Forward Pattern)

| Agent | Purpose | Integration |
|-------|---------|-------------|
| `OperationsLiaisonAgent` | Interactive SOP/workflow guidance | Called at orchestrator layer |
| `CoexistenceAnalysisAgent` | AI-powered coexistence analysis | Optional, fallback to deterministic |

---

**Next Steps:**
1. Update frontend JourneyAPIManager to OperationsAPIManager
2. Complete integration tests for Operations Solution
3. Update Experience SDK bindings

---

**Last Updated:** January 27, 2026  
**Owner:** Operations Realm Solution Team
