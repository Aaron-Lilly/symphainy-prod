# WebSocket Agent Endpoint Architecture

## Question
Frontend expects: `/api/runtime/agent` (WebSocket endpoint)

**Which service should own this endpoint?**
- Runtime Service: matches endpoint path, but Runtime doesn't have agent routing
- Experience Plane: user-facing APIs, has Guide Agent Service, but endpoint would differ
- Hybrid: Experience Plane endpoint that proxies to Runtime

## Architectural Analysis

### Current Architecture

#### Runtime Service
- **Role**: Orchestrates execution lifecycle (intent → execution → completion)
- **Responsibilities**:
  - Intent acceptance and validation
  - Execution context creation
  - Intent routing to realms (via IntentRegistry)
  - Execution state management (StateSurface)
  - Write-ahead logging (WAL)
  - Event publishing
- **Does NOT handle**: Agent routing, agent invocation, conversational flows

#### Experience Plane
- **Role**: User-facing API layer
- **Components**:
  - `GuideAgentService`: Provides Guide Agent API
  - `GuideAgent`: Global concierge for platform navigation
  - WebSocket endpoints: Currently `/api/execution/{execution_id}/stream` (for execution streaming)
- **Responsibilities**:
  - User interaction handling
  - Agent orchestration (Guide Agent, Liaison Agents)
  - Frontend API contracts
  - Session management

#### Agent Architecture
- **Guide Agent**: Global concierge, routes to pillar liaison agents
- **Liaison Agents**: Domain-specific agents (Journey, Insights, Content, etc.)
- **Collaboration Router**: Routes agent-to-agent collaboration requests
- **Agent Registry**: Manages agent instances

### Agent Routing Flow

```
User Message (WebSocket)
  ↓
Guide Agent (analyzes intent)
  ↓
Routes to:
  - Direct intent execution (via Runtime)
  - Pillar Liaison Agent (domain-specific guidance)
  - Multi-agent collaboration (via CollaborationRouter)
```

## Recommendation: **Experience Plane with Runtime Integration**

### Rationale

1. **Separation of Concerns**:
   - **Runtime**: Execution lifecycle, intent → realm routing, state management
   - **Experience Plane**: User interaction, agent orchestration, conversational flows
   - Agents are **user-facing** (conversational, guidance), not execution primitives

2. **Agent Invocation Pattern**:
   - Agents analyze user intent and **generate intents** for Runtime
   - Agents don't execute directly - they orchestrate via Runtime
   - Example: Guide Agent analyzes "upload a file" → creates `ingest_file` intent → Runtime executes

3. **Endpoint Path Alignment**:
   - Frontend expects `/api/runtime/agent` but this is a **user-facing** endpoint
   - Experience Plane can expose `/api/runtime/agent` as a **proxy/alias** to maintain frontend contract
   - Internal routing: Experience Plane → Guide Agent → Runtime (for intent execution)

### Proposed Architecture

```
Frontend WebSocket: /api/runtime/agent
  ↓
Experience Plane WebSocket Handler
  ↓
Guide Agent Service
  ↓
Guide Agent (analyzes user message)
  ↓
Routing Decision:
  ├─ Direct Intent → Runtime.execute(intent)
  ├─ Pillar Liaison → Liaison Agent → Runtime.execute(intent)
  └─ Multi-Agent → Collaboration Router → Agents → Runtime.execute(intent)
  ↓
Runtime.execute(intent) → Realm → Execution Result
  ↓
Stream results back via WebSocket
```

### Implementation Details

#### 1. WebSocket Endpoint Location
**File**: `symphainy_platform/civic_systems/experience/api/websocket.py`
**Endpoint**: `/api/runtime/agent` (maintains frontend contract)

#### 2. Agent Routing Logic
**Location**: `GuideAgentService` or new `AgentRouterService`
**Responsibilities**:
- Receive WebSocket messages
- Route to Guide Agent for intent analysis
- Determine if message requires:
  - Direct intent execution (via Runtime)
  - Liaison agent consultation
  - Multi-agent collaboration
- Invoke appropriate agent(s)
- Convert agent responses to intents
- Execute intents via Runtime
- Stream results back via WebSocket

#### 3. Runtime Integration
- Experience Plane calls `RuntimeClient.execute(intent)` for intent execution
- Runtime handles execution lifecycle (WAL, state, events)
- Experience Plane streams execution events back to frontend

#### 4. Agent Invocation Pattern
```python
# In Experience Plane WebSocket handler
async def handle_agent_message(message: str, context: ExecutionContext):
    # 1. Analyze with Guide Agent
    guide_response = await guide_agent.analyze_user_intent(message, context)
    
    # 2. Route based on analysis
    if guide_response.needs_liaison:
        liaison_agent = get_liaison_agent(guide_response.target_pillar)
        liaison_response = await liaison_agent.consult(guide_response, context)
        intent = liaison_response.to_intent()
    else:
        intent = guide_response.to_intent()
    
    # 3. Execute via Runtime
    result = await runtime_client.execute(intent)
    
    # 4. Stream results
    await websocket.send_json(result)
```

### Routing Decision Matrix

| User Message Type | Routing Path | Agent(s) Involved |
|------------------|--------------|-------------------|
| "Upload a file" | Guide → Direct Intent | Guide Agent only |
| "What insights can I get from my data?" | Guide → Insights Liaison → Intent | Guide + Insights Liaison |
| "Create a workflow from my SOP" | Guide → Journey Liaison → Intent | Guide + Journey Liaison |
| "Compare my data quality across files" | Guide → Multi-Agent Collaboration | Guide + Multiple Liaisons |

### Key Principles

1. **Runtime owns execution, not agent routing**
   - Runtime receives intents (from agents or directly)
   - Runtime doesn't know about agents
   - Agents are Experience Plane concern

2. **Experience Plane owns user interaction**
   - WebSocket connections
   - Agent orchestration
   - Conversational flows
   - Frontend API contracts

3. **Agents generate intents, don't execute**
   - Agents analyze and recommend
   - Agents create intents for Runtime
   - Runtime executes intents

4. **Maintain frontend contract**
   - Endpoint can be `/api/runtime/agent` (proxy from Experience Plane)
   - Or `/api/experience/agent` (more accurate, but requires frontend change)
   - Recommendation: Use `/api/runtime/agent` as proxy to maintain contract

### Implementation Steps

1. **Add WebSocket endpoint to Experience Plane**
   - File: `symphainy_platform/civic_systems/experience/api/websocket.py`
   - Endpoint: `/api/runtime/agent` (or `/api/experience/agent` if frontend can change)
   - Handler: `handle_agent_websocket(websocket: WebSocket)`

2. **Create Agent Router Service** (optional, or extend GuideAgentService)
   - File: `symphainy_platform/civic_systems/experience/services/agent_router_service.py`
   - Responsibilities:
     - Route messages to Guide Agent
     - Determine routing path (direct, liaison, collaboration)
     - Invoke appropriate agents
     - Convert agent responses to intents
     - Execute intents via Runtime

3. **Integrate with Runtime**
   - Use `RuntimeClient` to execute intents
   - Stream execution events back via WebSocket
   - Handle execution lifecycle (errors, timeouts, etc.)

4. **Agent Response Format**
   - Agents return structured responses
   - Responses include:
     - Intent recommendations
     - User guidance messages
     - Next steps
   - Router converts to intents for Runtime

### Alternative: Runtime Endpoint (NOT RECOMMENDED)

If we put the endpoint in Runtime:
- ❌ Runtime would need agent routing logic (violates separation of concerns)
- ❌ Runtime would need to know about Guide/Liaison agents (coupling)
- ❌ Agents are user-facing, not execution primitives
- ❌ Would require Runtime to handle conversational flows

### Summary

**Recommended Approach**: Experience Plane owns `/api/runtime/agent` endpoint
- Maintains frontend contract (can proxy `/api/runtime/agent`)
- Proper separation of concerns (agents = user-facing, Runtime = execution)
- Agents generate intents → Runtime executes
- Experience Plane orchestrates agent conversations
- Runtime handles execution lifecycle

**Routing Flow**:
1. WebSocket message → Experience Plane
2. Experience Plane → Guide Agent (analyze intent)
3. Guide Agent → Route decision (direct/liaison/collaboration)
4. Appropriate agent(s) → Generate intent(s)
5. Experience Plane → Runtime.execute(intent)
6. Runtime → Execute via realm
7. Results → Stream back via WebSocket
