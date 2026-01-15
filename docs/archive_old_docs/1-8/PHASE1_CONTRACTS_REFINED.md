# Phase 1 Contracts - Refined & Purpose-Driven
**Date:** January 2026  
**Status:** ✅ **REFINED BASED ON MVP REQUIREMENTS**

---

## 🎯 Purpose

This document defines the **refined contract structure** for Phase 1, based on:
1. MVP showcase requirements (what the platform actually needs to do)
2. Elimination of deprecated concepts
3. Clear, distinct purpose for each contract (no duplication)
4. 1:1 mapping between SOA APIs and MCP tools for agent access

---

## 📋 Contract Design Principles

1. **MVP-First:** Contracts support MVP showcase functionality
2. **No Duplication:** Each contract has a clear, distinct purpose
3. **Agent-Accessible:** All contracts that agents need have 1:1 SOA API → MCP Tool mapping
4. **Pattern Alignment:** Contracts align with existing Public Works patterns
5. **Runtime Focus:** Phase 1 focuses on Runtime Plane contracts (Session, State, Execution, Intent)

---

## 🔍 MVP Requirements → Contract Mapping

### MVP Feature 1: Login & Account Creation
**Required Contracts:**
- ✅ **Authentication Contract** (Security Guard)
- ✅ **Session Contract** (Traffic Cop) - Already in Phase 1

### MVP Feature 2: Landing Page & Solution Context
**Required Contracts:**
- ✅ **Solution Context Contract** (Solution Realm)
- ✅ **Session Contract** (for context persistence)

### MVP Feature 3: Content Pillar
**Required Contracts:**
- ✅ **File Upload Contract** (Data Steward)
- ✅ **File Parsing Contract** (Content Realm)
- ✅ **Semantic Interpretation Contract** (Librarian)

### MVP Feature 4: Insights Pillar
**Required Contracts:**
- ✅ **Quality Assessment Contract** (Insights Realm)
- ✅ **Data Analysis Contract** (Insights Realm)
- ✅ **Data Mapping Contract** (Insights Realm)

### MVP Feature 5: Operations Pillar
**Required Contracts:**
- ✅ **Workflow Generation Contract** (Journey Realm)
- ✅ **SOP Generation Contract** (Journey Realm)
- ✅ **Coexistence Analysis Contract** (Journey Realm)
- ✅ **Platform Journey Contract** (Journey Realm)

### MVP Feature 6: Business Outcomes Pillar
**Required Contracts:**
- ✅ **Roadmap Generation Contract** (Solution Realm)
- ✅ **POC Generation Contract** (Solution Realm)
- ✅ **Platform Solution Contract** (Solution Realm)

### MVP Feature 7: Admin Dashboard
**Required Contracts:**
- ✅ **Admin Dashboard Contract** (Solution Realm)
- ✅ **Platform Health Contract** (Nurse)

### MVP Feature 8: Chat Interface (Guide + Liaison Agents)
**Required Contracts:**
- ✅ **Agent Communication Contract** (Post Office)
- ✅ **Intent Contract** (Runtime Plane) - Already in Phase 1

---

## 📊 Refined Contract Structure

### Phase 1: Runtime Plane Contracts (Foundation)

These are the **core contracts** that enable the Runtime Plane to function:

#### 1. Session Contract
**Purpose:** Session lifecycle management (create, get, update, delete)  
**Implemented By:** Session Surface, Traffic Cop  
**Pattern:** Aligned with Traffic Cop's `SessionRequest`/`SessionResponse` dataclasses  
**MCP Tools:** Yes (agents need session access)

**Methods:**
- `create_session(request: SessionRequest, user_context: Optional[Dict]) -> SessionResponse`
- `get_session(session_id: str, user_context: Optional[Dict]) -> Optional[SessionResponse]`
- `update_session(session_id: str, updates: Dict, user_context: Optional[Dict]) -> SessionResponse`
- `delete_session(session_id: str, user_context: Optional[Dict]) -> SessionResponse`

---

#### 2. State Contract
**Purpose:** State coordination (session, workflow, execution, solution, journey state)  
**Implemented By:** State Surface  
**Pattern:** Coordinates with Traffic Cop (session), Conductor (workflow), Runtime (execution)  
**MCP Tools:** Yes (agents need state access)

**Methods:**
- `get_state(state_key: str, state_type: str, context: Dict) -> Optional[Dict]`
- `set_state(state_key: str, state_type: str, state_data: Dict, context: Dict) -> bool`
- `delete_state(state_key: str, state_type: str, context: Dict) -> bool`
- `list_states(state_type: str, filters: Optional[Dict]) -> List[Dict]`

---

#### 3. Workflow Contract
**Purpose:** Workflow lifecycle (create, execute, get status)  
**Implemented By:** State Surface (coordinates with Conductor)  
**Pattern:** Aligned with Conductor's plain dict pattern  
**MCP Tools:** Yes (agents need workflow access)

**Methods:**
- `create_workflow(request: Dict, user_context: Optional[Dict]) -> Dict`
- `execute_workflow(request: Dict, user_context: Optional[Dict]) -> Dict`
- `get_workflow_status(request: Dict, user_context: Optional[Dict]) -> Dict`

---

#### 4. Execution Contract
**Purpose:** Execution control (execute, suspend, resume, cancel)  
**Implemented By:** Execution Surface  
**Pattern:** Runtime Plane execution supervisor  
**MCP Tools:** No (internal to Runtime Plane)

**Methods:**
- `execute(execution_plan: ExecutionPlan) -> Dict`
- `suspend_execution(execution_id: str) -> bool`
- `resume_execution(execution_id: str) -> bool`
- `cancel_execution(execution_id: str) -> bool`
- `get_execution_status(execution_id: str) -> Dict`

---

#### 5. Intent Contract
**Purpose:** Intent propagation (capture, propagate, resolve)  
**Implemented By:** Intent Surface  
**Pattern:** Runtime Plane intent flow  
**MCP Tools:** Yes (agents need intent access)

**Methods:**
- `capture_intent(intent_data: Dict, context: Dict) -> Dict`
- `propagate_intent(intent_id: str, target: str, context: Dict) -> bool`
- `resolve_intent(intent_id: str, resolution: Dict) -> bool`
- `get_intent(intent_id: str) -> Optional[Dict]`

---

### Phase 2: Smart City Contracts (Infrastructure)

These contracts enable Smart City services to function:

#### 6. Authentication Contract
**Purpose:** User authentication (login, account creation)  
**Implemented By:** Security Guard  
**Pattern:** Aligned with Security Guard's authentication module  
**MCP Tools:** Yes (agents need authentication)

**Methods:**
- `authenticate_user(request: Dict, user_context: Optional[Dict]) -> Dict`
- `create_account(request: Dict, user_context: Optional[Dict]) -> Dict`
- `validate_token(token: str, user_context: Optional[Dict]) -> Dict`

---

#### 7. Authorization Contract
**Purpose:** Action authorization (check permissions)  
**Implemented By:** Security Guard  
**Pattern:** Aligned with Security Guard's authorization module  
**MCP Tools:** Yes (agents need authorization)

**Methods:**
- `authorize_action(action: str, resource: str, user_context: Dict) -> bool`
- `check_permissions(user_context: Dict, capability: str, operation: str) -> bool`

---

#### 8. File Lifecycle Contract
**Purpose:** File upload, storage, retrieval, deletion  
**Implemented By:** Data Steward  
**Pattern:** Aligned with Data Steward's file_lifecycle_module  
**MCP Tools:** Yes (agents need file access)

**Methods:**
- `upload_file(file_data: Dict, user_context: Optional[Dict]) -> Dict`
- `get_file(file_id: str, user_context: Optional[Dict]) -> Dict`
- `delete_file(file_id: str, user_context: Optional[Dict]) -> bool`
- `list_files(filters: Optional[Dict], user_context: Optional[Dict]) -> List[Dict]`

---

#### 9. Semantic Data Contract
**Purpose:** Semantic data storage and retrieval (embeddings, semantic graph, correlation map)  
**Implemented By:** Librarian  
**Pattern:** Aligned with Librarian's semantic_data_storage_module  
**MCP Tools:** Yes (agents need semantic data access)

**Methods:**
- `store_embeddings(content_id: str, embeddings: Dict, user_context: Optional[Dict]) -> Dict`
- `get_embeddings(content_id: str, user_context: Optional[Dict]) -> Dict`
- `vector_search(query_embedding: List[float], limit: int, filters: Optional[Dict], user_context: Optional[Dict]) -> List[Dict]`
- `store_semantic_graph(content_id: str, graph: Dict, user_context: Optional[Dict]) -> Dict`
- `get_semantic_graph(content_id: str, user_context: Optional[Dict]) -> Dict`

---

#### 10. Observability Contract
**Purpose:** Platform observability (events, agent executions, health)  
**Implemented By:** Nurse  
**Pattern:** Aligned with Nurse's observability_module  
**MCP Tools:** Yes (agents need observability access)

**Methods:**
- `record_platform_event(event_type: str, event_data: Dict, trace_id: Optional[str], user_context: Optional[Dict]) -> bool`
- `record_agent_execution(agent_id: str, agent_name: str, response: Dict, trace_id: Optional[str], execution_metadata: Dict, user_context: Optional[Dict]) -> bool`
- `get_observability_data(data_type: str, filters: Dict, limit: int, user_context: Optional[Dict]) -> Dict`
- `get_health_metrics(service_name: Optional[str], user_context: Optional[Dict]) -> Dict`

---

#### 11. Agent Communication Contract
**Purpose:** Agent-to-agent and agent-to-service communication  
**Implemented By:** Post Office  
**Pattern:** Aligned with Post Office's messaging_module  
**MCP Tools:** Yes (agents need communication)

**Methods:**
- `send_message(request: Dict, user_context: Optional[Dict]) -> Dict`
- `get_messages(recipient_id: str, filters: Optional[Dict], user_context: Optional[Dict]) -> List[Dict]`
- `publish_to_agent_channel(channel: str, message: Dict, realm: str, user_context: Optional[Dict]) -> bool`

---

### Phase 3: Realm Contracts (Business Logic)

These contracts enable Realm services to function:

#### 12. Content Processing Contract
**Purpose:** File parsing and semantic interpretation  
**Implemented By:** Content Realm (FileParserService)  
**Pattern:** Aligned with Content Orchestrator's parse_file method  
**MCP Tools:** Yes (agents need content processing)

**Methods:**
- `parse_file(file_id: str, parse_options: Optional[Dict], user_context: Optional[Dict]) -> Dict`
- `analyze_document(document_id: str, analysis_types: List[str], user_context: Optional[Dict]) -> Dict`
- `get_semantic_interpretation(content_id: str, user_context: Optional[Dict]) -> Dict`

---

#### 13. Insights Analysis Contract
**Purpose:** Quality assessment, data analysis, data mapping  
**Implemented By:** Insights Realm (DataAnalyzerService, DataQualityValidationService)  
**Pattern:** Aligned with Insights Orchestrator's analysis methods  
**MCP Tools:** Yes (agents need insights analysis)

**Methods:**
- `assess_quality(file_id: str, user_context: Optional[Dict]) -> Dict`
- `analyze_data(file_id: str, analysis_options: Optional[Dict], user_context: Optional[Dict]) -> Dict`
- `map_data(source_data: Dict, target_schema: Dict, user_context: Optional[Dict]) -> Dict`

---

#### 14. Journey Orchestration Contract
**Purpose:** Workflow/SOP generation, coexistence analysis, platform journey creation  
**Implemented By:** Journey Realm (OperationsJourneyOrchestrator)  
**Pattern:** Aligned with Journey Orchestrator's workflow/SOP methods  
**MCP Tools:** Yes (agents need journey orchestration)

**Methods:**
- `generate_workflow_from_sop(sop_id: str, user_context: Optional[Dict]) -> Dict`
- `generate_sop_from_workflow(workflow_id: str, user_context: Optional[Dict]) -> Dict`
- `generate_sop_from_chat(chat_context: Dict, user_context: Optional[Dict]) -> Dict`
- `analyze_coexistence(workflow_id: str, sop_id: Optional[str], user_context: Optional[Dict]) -> Dict`
- `create_coexistence_blueprint(analysis_result: Dict, user_context: Optional[Dict]) -> Dict`
- `create_platform_journey(blueprint: Dict, user_context: Optional[Dict]) -> Dict`

---

#### 15. Solution Orchestration Contract
**Purpose:** Roadmap generation, POC generation, platform solution creation  
**Implemented By:** Solution Realm (RoadmapGenerationService, POCGenerationService, SolutionComposerService)  
**Pattern:** Aligned with Solution Orchestrator's roadmap/POC methods  
**MCP Tools:** Yes (agents need solution orchestration)

**Methods:**
- `generate_roadmap(pillar_summaries: Dict, roadmap_options: Optional[Dict], user_context: Optional[Dict]) -> Dict`
- `generate_poc_proposal(pillar_summaries: Dict, poc_options: Optional[Dict], user_context: Optional[Dict]) -> Dict`
- `create_platform_solution(solution_type: str, solution_data: Dict, user_context: Optional[Dict]) -> Dict`
- `get_admin_dashboard_summary(user_context: Optional[Dict]) -> Dict`

---

#### 16. Solution Context Contract
**Purpose:** Solution context definition and retrieval  
**Implemented By:** Solution Realm (SolutionManagerService)  
**Pattern:** Aligned with Solution Manager's solution context methods  
**MCP Tools:** Yes (agents need solution context)

**Methods:**
- `define_solution_context(context_data: Dict, user_context: Optional[Dict]) -> Dict`
- `get_solution_context(context_id: str, user_context: Optional[Dict]) -> Dict`
- `update_solution_context(context_id: str, updates: Dict, user_context: Optional[Dict]) -> Dict`

---

## 🔧 Deprecated Concepts Removed

### Removed from Contracts:
1. ❌ **Semantic Contract Contract** - Deprecated concept (semantic contracts are internal to Data Steward)
2. ❌ **Data Policy Contract** - Deprecated concept (policies are internal to Data Steward)
3. ❌ **Lineage Contract** - Deprecated concept (lineage is internal to Data Steward)
4. ❌ **WAL Contract** - Deprecated concept (WAL is internal to Data Steward)
5. ❌ **Quality/Compliance Contract** - Merged into Insights Analysis Contract
6. ❌ **Content Metadata Contract** - Merged into Semantic Data Contract
7. ❌ **Knowledge Management Contract** - Deprecated concept (knowledge is internal to Librarian)
8. ❌ **Vector Search Contract** - Merged into Semantic Data Contract
9. ❌ **Telemetry Contract** - Merged into Observability Contract
10. ❌ **Health Monitoring Contract** - Merged into Observability Contract
11. ❌ **Distributed Tracing Contract** - Merged into Observability Contract
12. ❌ **Alert Management Contract** - Deprecated concept (alerts are internal to Nurse)
13. ❌ **Log Aggregation Contract** - Merged into Observability Contract
14. ❌ **Load Balancing Contract** - Deprecated concept (internal to Traffic Cop)
15. ❌ **Rate Limiting Contract** - Deprecated concept (internal to Traffic Cop)
16. ❌ **API Gateway Contract** - Deprecated concept (internal to Traffic Cop)
17. ❌ **Traffic Analytics Contract** - Deprecated concept (internal to Traffic Cop)
18. ❌ **WebSocket Contract** - Merged into Agent Communication Contract
19. ❌ **Task Management Contract** - Deprecated concept (internal to Conductor)
20. ❌ **Orchestration Pattern Contract** - Deprecated concept (internal to Conductor)
21. ❌ **Security Communication Contract** - Deprecated concept (internal to Security Guard)
22. ❌ **Zero Trust Policy Contract** - Deprecated concept (internal to Security Guard)
23. ❌ **Tenant Isolation Contract** - Deprecated concept (internal to Security Guard)
24. ❌ **Event Management Contract** - Merged into Agent Communication Contract
25. ❌ **Event Subscription Contract** - Merged into Agent Communication Contract
26. ❌ **Pillar Coordination Contract** - Merged into Agent Communication Contract
27. ❌ **Realm Communication Contract** - Merged into Agent Communication Contract
28. ❌ **WebSocket Gateway Contract** - Merged into Agent Communication Contract
29. ❌ **Bootstrap Contract** - Deprecated concept (internal to City Manager)
30. ❌ **Realm Startup Contract** - Deprecated concept (internal to City Manager)
31. ❌ **Service Management Contract** - Deprecated concept (internal to City Manager)
32. ❌ **Platform Governance Contract** - Deprecated concept (internal to City Manager)
33. ❌ **Manager Coordination Contract** - Deprecated concept (internal to City Manager)
34. ❌ **Entity Extraction Contract** - Merged into Content Processing Contract
35. ❌ **Content Embedding Contract** - Merged into Semantic Data Contract
36. ❌ **Visualization Contract** - Deprecated concept (internal to Insights Realm)
37. ❌ **Business Analysis Contract** - Merged into Insights Analysis Contract

---

## 📊 Contract Summary

### Phase 1: Runtime Plane (5 contracts)
1. Session Contract
2. State Contract
3. Workflow Contract
4. Execution Contract
5. Intent Contract

### Phase 2: Smart City (6 contracts)
6. Authentication Contract
7. Authorization Contract
8. File Lifecycle Contract
9. Semantic Data Contract
10. Observability Contract
11. Agent Communication Contract

### Phase 3: Realm (5 contracts)
12. Content Processing Contract
13. Insights Analysis Contract
14. Journey Orchestration Contract
15. Solution Orchestration Contract
16. Solution Context Contract

**Total: 16 contracts** (down from 60+)

---

## ✅ MCP Tool Mapping

**Principle:** Every contract that agents need has a 1:1 SOA API → MCP Tool mapping.

**Contracts with MCP Tools (13):**
1. Session Contract → `session_*` tools
2. State Contract → `state_*` tools
3. Workflow Contract → `workflow_*` tools
4. Intent Contract → `intent_*` tools
5. Authentication Contract → `authenticate_*` tools
6. Authorization Contract → `authorize_*` tools
7. File Lifecycle Contract → `file_*` tools
8. Semantic Data Contract → `semantic_*` tools
9. Observability Contract → `observability_*` tools
10. Agent Communication Contract → `communication_*` tools
11. Content Processing Contract → `content_*` tools
12. Insights Analysis Contract → `insights_*` tools
13. Journey Orchestration Contract → `journey_*` tools
14. Solution Orchestration Contract → `solution_*` tools
15. Solution Context Contract → `solution_context_*` tools

**Contracts without MCP Tools (1):**
- Execution Contract (internal to Runtime Plane)

---

## 🎯 Next Steps

1. **Update Phase 1 Implementation Plan** with refined contract structure
2. **Create contract implementations** following Public Works patterns
3. **Ensure 1:1 SOA API → MCP Tool mapping** for all agent-accessible contracts
4. **Validate against MVP requirements** to ensure completeness

---

**Last Updated:** January 2026  
**Status:** ✅ **REFINED & READY FOR IMPLEMENTATION**
