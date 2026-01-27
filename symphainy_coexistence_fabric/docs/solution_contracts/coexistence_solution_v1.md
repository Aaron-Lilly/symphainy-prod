# Solution Contract: Coexistence Solution

**Solution:** Coexistence Solution  
**Solution ID:** `coexistence_solution_v1`  
**Status:** DRAFT  
**Priority:** P0  
**Owner:** C-Suite

---

## 1. Business Objective

### Problem Statement
Users need to understand and navigate the SymphAIny platform. The Coexistence Solution provides the human-platform interaction interface that introduces users to platform capabilities and enables conversational navigation.

### Target Users
- **Primary Persona:** New Platform Users
  - **Goals:** Understand platform capabilities, navigate to solutions, get help
  - **Pain Points:** Unclear platform structure, don't know where to start, need guidance

- **Secondary Personas:**
  - **Returning Users:** Quick navigation to solutions, understand new features
  - **Administrators:** Platform overview, solution discovery

### Success Criteria
- **Business Metrics:**
  - 90%+ of users understand platform structure after landing page
  - < 3 clicks to navigate to desired solution
  - 80%+ of users interact with GuideAgent
  - 70%+ user satisfaction with navigation

- **User Satisfaction:**
  - Users understand platform capabilities in < 30 seconds
  - Clear navigation to solutions
  - Helpful conversational interface

- **Adoption Targets:**
  - 100% of users see landing page
  - 80%+ of users interact with GuideAgent
  - 90%+ successful navigation to solutions

---

## 2. Solution Composition

### Composed Journeys

This solution composes the following journeys:

1. **Journey:** Platform Introduction (Journey ID: `journey_coexistence_introduction`)
   - **Purpose:** Introduce platform capabilities and GuideAgent
   - **User Trigger:** User lands on platform (landing page)
   - **Success Outcome:** User understands platform, can navigate to solutions

2. **Journey:** Solution Navigation (Journey ID: `journey_coexistence_navigation`)
   - **Purpose:** Navigate user to desired solution
   - **User Trigger:** User clicks a solution from the navbar to navigate to solution
   - **Success Outcome:** User navigated to solution, solution context established

3. **Journey:** GuideAgent Interaction (Journey ID: `journey_coexistence_guide_agent`)
   - **Purpose:** Enable conversational interaction with GuideAgent
   - **User Trigger:** User initiates conversation with GuideAgent
   - **Success Outcome:** User receives guidance, or get help

### Journey Orchestration

**Chat-First Flow:**
1. User opens chat interface → Journey: Chat Session Management
2. User converses with GuideAgent → Journey: GuideAgent Conversation
3. User toggles to Liaison Agent → Journey: Agent Context Sharing → Journey: Liaison Agent Conversation
4. Agent needs platform action → Journey: Agent-Orchestrator Interaction

**Parallel Flow:**
- Chat journeys can overlap (user can toggle between agents)
- Context sharing happens automatically on agent toggle
- Orchestrator interactions happen in background during conversations
- Multiple agent conversations can be active (one at a time in UI, but context preserved)

---

## 3. User Experience Flows

### Primary User Flow (Chat-First Experience)
```
1. User opens chat interface (right side panel)
   → Chat session initialized
   → GuideAgent active by default
   → GuideAgent greets user and explains platform
   
2. User converses with GuideAgent
   → GuideAgent provides platform-wide guidance
   → GuideAgent can route to solutions or execute orchestrator actions
   → Conversation context maintained
   
3. User toggles to Liaison Agent (e.g., Content Liaison)
   → Context shared from GuideAgent conversation
   → Liaison Agent activated with pillar awareness
   → User receives Content Realm-specific assistance
   
4. User toggles back to GuideAgent
   → Context shared from Liaison Agent conversation
   → GuideAgent continues with full platform awareness
   → Seamless conversation continuity
   
5. Agent executes platform action
   → Agent interacts with orchestrator (governed)
   → Orchestrator executes journey/intent
   → Agent reports results back to user
```

### Alternative Flows
- **Flow A:** User starts with Liaison Agent → Context shared when toggling to GuideAgent
- **Flow B:** Agent-to-agent routing → GuideAgent routes to Liaison Agent with context
- **Flow C:** Multi-pillar conversation → User toggles between multiple Liaison Agents, context preserved
- **Flow D:** Orchestrator-mediated action → Agent calls orchestrator MCP tool, MCP tool validates and executes journey/intent

### Error Flows
- **Error A:** Agent unavailable → Show error, allow retry or switch to other agent
- **Error B:** Context sharing failed → Agent continues with limited context, log error
- **Error C:** Orchestrator interaction failed → Agent reports error, suggests alternative
- **Error D:** Governance violation → Orchestrator rejects action, agent explains limitation

---

## 4. Non-Functional Requirements

### Performance
- **Response Time:** Chat interface load < 1 second
- **Response Time:** Agent message response < 3 seconds
- **Response Time:** Agent toggle (context sharing) < 500ms
- **Response Time:** Orchestrator interaction < 5 seconds
- **Throughput:** Support 500+ concurrent chat sessions
- **Scalability:** Auto-scale agents based on load

### Security
- **Authentication:** Guide Agent Requires Security Solution authentication 
- **Authorization:** Public Access with instructions to login (or create an account) for access to solutions and guide agent
- **Data Privacy:** Conversation history stored securely (if enabled)

### Compliance
- **Regulatory:** GDPR (conversation data)
- **Audit:** Navigation events logged
- **Retention:** Conversation history retained per policy

---

## 5. Solution Components

### 5.1 Coexistence Component (Chat-First)
**Purpose:** Unified conversational interface for human-platform interaction

**Chat Architecture:**
- **Shared Chat Space:** Single chat interface (right side panel) shared by all agents
- **Agent Toggle:** User can toggle between GuideAgent and any Liaison Agent
- **Context Preservation:** Conversation context shared automatically on toggle
- **Multi-Agent Support:** GuideAgent + 4 Liaison Agents (Content, Insights, Journey, Solution)

**Business Logic:**
- **Journey:** Chat Session Management
  - Intent: `initialize_chat_session` - Create chat session with context
  - Intent: `get_chat_session` - Retrieve active chat session
  - Intent: `update_chat_context` - Update shared conversation context

- **Journey:** GuideAgent Conversation
  - Intent: `initiate_guide_agent` - Start GuideAgent conversation
  - Intent: `process_guide_agent_message` - Handle user message to GuideAgent
  - Intent: `route_to_liaison_agent` - GuideAgent routes to Liaison Agent
  - Intent: `execute_orchestrator_action` - GuideAgent requests orchestrator action (governed)

- **Journey:** Liaison Agent Conversation
  - Intent: `initiate_liaison_agent` - Start Liaison Agent conversation (pillar-aware)
  - Intent: `process_liaison_agent_message` - Handle user message to Liaison Agent
  - Intent: `get_pillar_context` - Retrieve pillar-specific context
  - Intent: `execute_pillar_action` - Liaison Agent executes pillar-specific action

- **Journey:** Agent Context Sharing
  - Intent: `share_context_to_agent` - Share context when switching agents
  - Intent: `get_shared_context` - Retrieve shared context for agent
  - Intent: `merge_agent_contexts` - Merge contexts from multiple agents

- **Journey:** Agent-Orchestrator Interaction
  - Intent: `call_orchestrator_mcp_tool` - Agent calls orchestrator MCP tool
  - Intent: `list_available_mcp_tools` - List available orchestrator MCP tools for agent
  - Intent: `validate_mcp_tool_call` - Validate MCP tool call against governance (before execution)

**UI Components:**
- **Chat Interface:** Right side panel with message history
- **Agent Toggle:** UI control to switch between GuideAgent and Liaison Agents
- **Agent Indicator:** Visual indicator showing active agent
- **Context Display:** Show shared context when toggling agents
- **Orchestrator Status:** Show orchestrator action status when agent requests action

**Agent Capabilities:**
- **GuideAgent:**
  - Platform-wide knowledge (all pillars, all solutions)
  - Can call any orchestrator MCP tool (governed)
  - Can route to any Liaison Agent
  - Full conversation context awareness
  - Can execute cross-pillar actions via MCP tools
  - Has access to all MCP tools from all orchestrators

- **Liaison Agents:**
  - Pillar-specific knowledge (Content, Insights, Journey, or Solution)
  - Can call pillar orchestrator MCP tools (governed)
  - Can request GuideAgent assistance
  - Pillar-aware conversation context
  - Can execute pillar-specific actions via MCP tools
  - Has access to pillar-specific MCP tools only

**Policies:**
- Platform access policies (Smart City: Security Guard)
- Solution visibility policies (Smart City: Security Guard)
- Conversation policies (Smart City: Traffic Cop)

**Experiences:**
- REST API:
  - `POST /api/coexistence/chat/session` - Initialize chat session
  - `POST /api/coexistence/chat/guide-agent/message` - Send message to GuideAgent
  - `POST /api/coexistence/chat/liaison-agent/message` - Send message to Liaison Agent
  - `POST /api/coexistence/chat/toggle-agent` - Toggle between agents
  - `GET /api/coexistence/chat/context` - Get shared context
  - `POST /api/coexistence/chat/orchestrator/request` - Request orchestrator action
- WebSocket:
  - Chat interface (real-time messages)
  - Agent toggle events
  - Context sharing events
  - Orchestrator action status updates

### 5.2 Security Component
**Purpose:** Authentication integration

**Integration:**
- Landing page is public but Guide Agent and Solution Navigation require authentication
- Guide Access and Solution Navigation require Security (redirect to login page if not authorized)
- GuideAgent only available in authenticated modes

### 5.3 Control Tower Component
**Purpose:** Coexistence observability

**Capabilities:**
- View landing page metrics
- Monitor GuideAgent interactions
- Track solution navigation patterns
- Analyze user onboarding flow

### 5.4 Policies Component
**Purpose:** Coexistence governance

**Smart City Primitives:**
- **Security Guard:** Platform access policies, solution visibility policies
- **Traffic Cop:** Conversation rate limiting, navigation policies
- **City Manager:** Solution catalog management

**Default Policies:**
- Public landing page access
- Solution visibility based on user permissions
- GuideAgent rate limiting (if needed)
- Conversation history retention (30 days)

### 5.5 Experiences Component
**Purpose:** API and real-time communication

**REST API:**
- `GET /api/coexistence/introduce` - Get platform introduction
- `POST /api/coexistence/navigate` - Navigate to solution
- `POST /api/coexistence/guide-agent/message` - Send message to GuideAgent
- `GET /api/coexistence/solutions` - List available solutions

**Websocket:**
- GuideAgent chat interface
- Real-time navigation updates
- Solution context changes

### 5.6 Business Logic Component
**Purpose:** Core coexistence workflows

**Journeys:**
- Platform Introduction Journey
- Solution Navigation Journey
- GuideAgent Interaction Journey

**Intents:**
- **Chat Session:** `initialize_chat_session`, `get_chat_session`, `update_chat_context`
- **GuideAgent:** `initiate_guide_agent`, `process_guide_agent_message`, `route_to_liaison_agent`, `execute_orchestrator_action`
- **Liaison Agent:** `initiate_liaison_agent`, `process_liaison_agent_message`, `get_pillar_context`, `execute_pillar_action`
- **Context Sharing:** `share_context_to_agent`, `get_shared_context`, `merge_agent_contexts`
- **Orchestrator Interaction:** `call_orchestrator_mcp_tool`, `list_available_mcp_tools`, `validate_mcp_tool_call`

---

## 6. Solution Artifacts

### Artifacts Produced
- **Chat Session Artifacts:** Chat session metadata (session_id, active_agent, created_at)
- **Conversation Artifacts:** Agent conversations (messages, timestamps, agent_type)
- **Context Artifacts:** Shared conversation context (cross-agent context, pillar context)
- **Orchestrator Request Artifacts:** Agent-orchestrator interaction requests (governed actions)
- **Agent Toggle Artifacts:** Agent switch events (from_agent, to_agent, context_shared)

### Artifact Relationships
- **Lineage:** Navigation Event → User, Conversation → User
- **Dependencies:** Coexistence Solution enables all other solutions

---

## 7. Integration Points

### Platform Services
- **Coexistence Realm:** Intent services for chat, agents, context sharing, MCP tool interactions
- **Journey Realm:** Orchestration services (exposed as MCP tools via MCP servers)
- **Agent Framework:** GuideAgent (platform concierge), Liaison Agents (pillar-specific)
- **MCP Servers:** Orchestrators expose intent services as MCP tools (registered via Curator)
- **Curator:** Registry of MCP tools (agents discover tools via Curator)

### Civic Systems
- **Smart City Primitives:** Security Guard, Traffic Cop, City Manager
- **Agent Framework:** GuideAgent (platform concierge)
- **Platform SDK:** Realm SDK for coexistence services

### External Systems
- **None** (platform-internal solution)

---

## 8. Testing & Validation

### Business Acceptance Criteria
- [ ] Users can access landing page
- [ ] Users understand platform capabilities
- [ ] Users can navigate to solutions
- [ ] GuideAgent provides helpful guidance
- [ ] Solution navigation works correctly
- [ ] Conversation interface is responsive

### User Acceptance Testing
- [ ] End-to-end platform introduction workflow
- [ ] End-to-end solution navigation workflow
- [ ] End-to-end GuideAgent interaction workflow
- [ ] Error handling workflow
- [ ] Unauthenticated vs authenticated flows

### Contract-Based Testing
- [ ] All intent contracts validated
- [ ] All journey contracts validated
- [ ] Solution contract validated
- [ ] Contract violations detected and prevented

---

## 9. Solution Registry

### Solution Metadata
- **Solution ID:** `coexistence_solution_v1`
- **Solution Version:** 1.0
- **Deployment Status:** DEVELOPMENT
- **Last Updated:** January 27, 2026

### Journey Dependencies
- **Journey 1:** Platform Introduction - Status: PLANNED
- **Journey 2:** Solution Navigation - Status: PLANNED
- **Journey 3:** GuideAgent Interaction - Status: PLANNED

### Solution Dependencies
- **Depends on:** Security Solution (for authenticated features)
- **Required by:** All other solutions (provides navigation and guidance)

---

## 10. Coexistence Component

### Human Interaction Interface
This solution IS the coexistence component - it provides the primary human-platform interaction interface.

**Chat-First Architecture:**
- **Shared Chat Interface:** Single chat panel (right side) shared by all agents
- **Agent Toggle:** User can switch between GuideAgent and any Liaison Agent
- **Context Continuity:** Conversation context automatically shared on agent toggle

**GuideAgent (Platform Concierge):**
- **Scope:** Platform-wide knowledge (all pillars, all solutions, all orchestrators)
- **Capabilities:**
  - Answer platform questions
  - Navigate to solutions
  - Route to Liaison Agents
  - Execute orchestrator actions (governed)
  - Access cross-pillar information
- **Context:** Full platform awareness, can access any realm's context

**Liaison Agents (Pillar-Specific):**
- **Scope:** Pillar-specific knowledge (Content, Insights, Journey, or Solution)
- **Capabilities:**
  - Answer pillar-specific questions
  - Execute pillar-specific actions
  - Request GuideAgent assistance
  - Interact with pillar orchestrators (governed)
- **Context:** Pillar-aware, can access pillar context and request GuideAgent help

**Context Sharing:**
- **Automatic:** Context shared automatically when toggling agents
- **Bidirectional:** Context flows both ways (GuideAgent ↔ Liaison Agents)
- **Merged:** Multiple agent contexts can be merged for comprehensive awareness
- **Persistent:** Context persists across agent toggles and session restarts

**Orchestrator Interactions (via MCP Tools):**
- **MCP Tool-Based:** Agents interact with orchestrators via MCP tools (not direct service calls)
- **Governed:** All MCP tool calls are validated against governance policies before execution
- **Tool Discovery:** Agents can discover available MCP tools via Curator registry
- **Request-Based:** Agents call MCP tools, tools validate and execute journey/intent
- **Status Updates:** Agents receive MCP tool responses with execution status
- **Error Handling:** Governance violations result in MCP tool errors with clear messages
- **Tool Registration:** Orchestrators register their intent services as MCP tools via Curator

**Conversation Topics:**
- **GuideAgent:** "What is SymphAIny?", "What can I do?", "Navigate to Content Solution", "Execute file upload journey" (via MCP tool)
- **Liaison Agents:** "How do I parse a file?" (Content - via Content orchestrator MCP tool), "What insights are available?" (Insights - via Insights orchestrator MCP tool), "Create a workflow" (Journey - via Journey orchestrator MCP tool), "Build a solution" (Solution - via Solution orchestrator MCP tool)

**MCP Tool Integration:**
- **Tool Discovery:** Agents query Curator for available MCP tools
- **Tool Execution:** Agents call MCP tools with parameters, tools execute orchestrator intents
- **Tool Responses:** MCP tools return execution results to agents
- **Governance:** MCP tools validate requests against Smart City policies before execution

---

## 11. Evolution & Roadmap

### Current Version
- **Version:** 1.0
- **Status:** DRAFT

### Planned Enhancements
- **Version 1.1:** Enhanced GuideAgent capabilities
- **Version 1.2:** Personalized solution recommendations
- **Version 1.3:** Multi-language support
- **Version 1.4:** Voice interface (future)

---

**Last Updated:** January 27, 2026  
**Owner:** C-Suite
n liaison agents

**Conversation Topics:**
- "What is SymphAIny?"
- "What can I do with this platform?"
- "How do I get started?"
- "Navigate me to [Solution Name]"
- "What solutions are available?"
- "How does coexistence work?"

---

## 11. Evolution & Roadmap

### Current Version
- **Version:** 1.0
- **Status:** DRAFT

### Planned Enhancements
- **Version 1.1:** Enhanced GuideAgent capabilities
- **Version 1.2:** Personalized solution recommendations
- **Version 1.3:** Multi-language support
- **Version 1.4:** Voice interface (future)

---

**Last Updated:** January 27, 2026  
**Owner:** C-Suite
