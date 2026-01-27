# Architecture North Star: SymphAIny Coexistence Fabric

**Purpose:** Executive summary explaining how the platform works - the system architecture, data flow, and contract vision.

**Status:** ✅ **ACTIVE**  
**Last Updated:** January 27, 2026

---

## Executive Summary

SymphAIny Coexistence Fabric is **not a platform** - it's a **system**. Everything flows through the **Runtime Execution Engine**, our data brain. The system is built on a three-tier contract hierarchy (Solution → Journey → Intent) that enables parallel development, contract-based testing, and agentic orchestration.

---

## 1. System, Not Platform

### What This Means

**Platform:** A collection of tools and services that users can use independently.

**System:** An integrated, orchestrated whole where all components work together through a central execution engine.

**SymphAIny is a System:**
- All execution flows through Runtime Execution Engine
- All state flows through State Surface (data brain)
- All artifacts flow through Artifact Registry
- All intents flow through Intent Registry
- All journeys flow through Journey Orchestrators

**Why This Matters:**
- Guaranteed consistency
- Centralized observability
- Unified data model
- Contract-based development
- Agentic orchestration

---

## 2. Runtime Execution Engine: The Heart of the System

### What It Is

The **Runtime Execution Engine** (`ExecutionLifecycleManager`) is the central orchestrator that executes all intents in the system.

**Location:** `symphainy_platform/runtime/execution_lifecycle_manager.py`

**Responsibilities:**
- Intent acceptance and validation
- Execution context creation
- Intent execution via realm services
- Artifact handling
- Event publishing (via transactional outbox)
- Execution completion
- WAL (Write-Ahead Logging) for all state changes

**Flow:**
```
Intent Submitted
    ↓
Runtime Execution Engine
    ↓
Intent Registry (find handler)
    ↓
Realm Intent Service (execute)
    ↓
State Surface (register artifacts)
    ↓
Artifact Registry (index artifacts)
    ↓
Event Publishing (via transactional outbox)
    ↓
Execution Complete
```

**Key Principle:** Everything runs through Runtime. No component bypasses Runtime.

---

## 3. Data Brain: State Surface

### What It Is

The **State Surface** (`StateSurface`) is the authoritative ledger for all artifacts in the system - our "data brain."

**Location:** `symphainy_platform/runtime/state_surface.py`

**Responsibilities:**
- Artifact registration and lifecycle management
- Artifact resolution (single source of truth)
- Execution state management
- Session state management
- Artifact lineage tracking

**Components:**
- **Artifact Registry:** Authoritative ledger for artifacts
- **Artifact Index (Supabase):** Discovery/exploration layer
- **State Abstraction:** Swappable backend (ArangoDB, in-memory, etc.)

**Key Principle:** State Surface is authoritative. All artifact queries go through State Surface.

---

## 4. Data Mash: Cross-Pillar Integration

### What It Is

The **Data Mash** is the visualization and integration layer that shows how data flows across all pillars (Content, Insights, Journey, Solution).

**Components:**
- **Artifact Lineage:** Parent-child relationships between artifacts
- **Cross-Pillar Visualization:** How artifacts from different realms connect
- **Solution Synthesis:** Combining artifacts from all realms into solutions

**Flow:**
```
Content Realm (files, parsed content, deterministic embeddings)
    ↓
Insights Realm (semantic embeddings, interpretations, relationships)
    ↓
Journey Realm (workflows, SOPs, coexistence blueprints)
    ↓
Solution Realm (synthesized outcomes, roadmaps, POC proposals)
```

**Key Principle:** Data Mash enables users to see the complete data journey across all realms.

---

## 5. Three-Tier Contract Hierarchy

### The Vision

**Solution Contracts** → **Journey Contracts** → **Intent Contracts**

**Solution Contracts (Business Layer):**
- Define business outcomes
- Define user experiences
- Compose journeys
- Business user-friendly

**Journey Contracts (Workflow Layer):**
- Define technical workflows
- Compose intents
- Define test scenarios
- Developer-friendly

**Intent Contracts (Capability Layer):**
- Define atomic platform capabilities
- Realm intent services (SOA APIs)
- Define parameters and returns
- Technical specification

**Flow:**
```
Solution Contract
    ↓
Journey Contracts (compose intents)
    ↓
Intent Contracts (realm services)
    ↓
Runtime Execution Engine
```

**Why This Matters:**
- Parallel development (teams work on different contracts)
- Contract-based testing (validate against contracts)
- Clear specifications (everyone knows what to build)
- Agentic orchestration (agents can read contracts and build)

---

## 6. System Architecture Overview

### Core Components

#### 1. Runtime Execution Engine
- **What:** Central orchestrator for all intent execution
- **Where:** `symphainy_platform/runtime/execution_lifecycle_manager.py`
- **Role:** Execute all intents, manage execution lifecycle

#### 2. State Surface (Data Brain)
- **What:** Authoritative ledger for all artifacts
- **Where:** `symphainy_platform/runtime/state_surface.py`
- **Role:** Register artifacts, resolve artifacts, manage lifecycle

#### 3. Artifact Registry
- **What:** Artifact registration and lifecycle management
- **Where:** `symphainy_platform/runtime/artifact_registry.py`
- **Role:** Store artifact records, manage lifecycle states

#### 4. Intent Registry
- **What:** Intent handler registration and discovery
- **Where:** `symphainy_platform/runtime/intent_registry.py`
- **Role:** Map intents to handlers, enable intent execution

#### 5. Journey Orchestrators
- **What:** Compose intent services into journeys
- **Where:** `symphainy_platform/realms/journey/orchestrators/`
- **Role:** Compose journeys, manage saga coordination, expose as MCP tools

#### 6. Realm Intent Services
- **What:** SOA APIs that provide platform capabilities
- **Where:** `symphainy_platform/realms/{realm}/intent_services/`
- **Role:** Execute intents, return artifacts, align to contracts

---

## 7. Data Flow Architecture

### Intent Execution Flow

```
User Action (Frontend)
    ↓
Experience Plane (REST/WebSocket)
    ↓
Runtime Execution Engine
    ↓
Intent Registry (find handler)
    ↓
Realm Intent Service (execute)
    ↓
Public Works Abstractions (infrastructure)
    ↓
State Surface (register artifacts)
    ↓
Artifact Registry (index artifacts)
    ↓
Event Publishing (via transactional outbox)
    ↓
Response to User
```

### Artifact Flow

```
Intent Service Creates Artifact
    ↓
State Surface (register artifact)
    ↓
Artifact Registry (store artifact record)
    ↓
Artifact Index (Supabase) - discovery layer
    ↓
Materializations (GCS, DuckDB, ArangoDB)
    ↓
Available for Next Intent
```

### Journey Flow

```
User Triggers Journey
    ↓
Journey Orchestrator (Journey Realm)
    ↓
Compose Intent Services
    ↓
Runtime Execution Engine (execute each intent)
    ↓
State Surface (register artifacts)
    ↓
Journey Complete
```

---

## 8. Contract Vision

### Solution → Journey → Intent

**Solution Contracts:**
- Business outcomes
- User experiences
- Journey composition
- Success criteria

**Journey Contracts:**
- Technical workflows
- Intent composition
- Test scenarios
- Completion criteria

**Intent Contracts:**
- Atomic capabilities
- Parameters and returns
- Idempotency keys
- Contract compliance

**Benefits:**
- **Parallel Development:** Teams work on different contracts simultaneously
- **Contract-Based Testing:** Validate implementation against contracts
- **Clear Specifications:** Everyone knows what to build
- **Agentic Orchestration:** Agents can read contracts and build

---

## 9. Smart City Primitives: Policy Enforcement

### What They Are

**Smart City Primitives** are pure functions that enforce policies and validate contracts.

**Key Primitives:**
- **Security Guard:** Authentication and authorization
- **Data Steward:** Data governance and policies
- **Traffic Cop:** Rate limiting and traffic management
- **Nurse:** Telemetry and health monitoring
- **Curator:** Registry coordination

**Pattern:**
- **SDKs:** Prepare execution contracts (Solution & Smart City)
- **Primitives:** Validate contracts (Runtime only)
- **Runtime:** Never calls SDK methods, only consumes snapshotted registry state

---

## 10. Public Works: Infrastructure Abstraction

### What It Is

**Public Works** provides abstractions for all infrastructure access.

**Key Abstractions:**
- **Registry Abstraction:** Database access (Supabase, ArangoDB)
- **Storage Abstraction:** File storage (GCS, S3)
- **Deterministic Compute Abstraction:** DuckDB access (for deterministic embeddings)
- **Semantic Data Abstraction:** ArangoDB access (for semantic embeddings)
- **Service Discovery Abstraction:** Service registration (Consul)

**Why:**
- Infrastructure swapping without code changes
- Consistent error handling
- Testing with mocks
- Architectural boundaries

---

## 11. Agentic Orchestration

### What It Is

**Agents** reason and propose. **Orchestrators** execute and commit.

**Agent Framework:**
- **AgentBase:** Base class for all agents
- **4-Layer Model:** AgentDefinition, AgentPosture, AgentRuntimeContext, Prompt Assembly
- **MCP Integration:** Agents use MCP tools to access platform capabilities

**MCP Servers:**
- Expose realm SOA APIs as MCP tools
- Enable agentic consumption of platform capabilities
- Base class: `MCPServerBase`

**Pattern:**
```
Agent (reasons, proposes)
    ↓
MCP Tool (calls realm SOA API)
    ↓
Journey Orchestrator (composes intents)
    ↓
Runtime Execution Engine (executes)
    ↓
State Surface (registers artifacts)
```

---

## 12. Telemetry and Observability

### What It Is

**Nurse SDK** coordinates telemetry reporting. **Control Tower** uses Nurse SDK to pull telemetry together.

**Pattern:**
- All components report telemetry via Nurse SDK
- Control Tower intents use Nurse SDK to aggregate telemetry
- Centralized observability and health monitoring

**Components That Report:**
- Journey Orchestrators
- Intent Services
- Agents
- MCP Servers
- Runtime Execution Engine
- State Surface
- Artifact Registry

---

## 13. Storage Strategy

### Deterministic Embeddings → DuckDB

**Rule:** Deterministic embeddings stored in DuckDB (via Public Works abstraction).

**Why:**
- DuckDB optimized for analytical workloads
- Deterministic embeddings are analytical data
- Separation from semantic embeddings (ArangoDB)

### Semantic Embeddings → ArangoDB

**Rule:** Semantic embeddings (interpretations) stored in ArangoDB.

**Why:**
- ArangoDB optimized for graph and semantic search
- Semantic embeddings need relationship capabilities
- Different use case from deterministic embeddings

---

## 14. Key Architectural Principles

### 1. Everything Runs Through Runtime
- No component bypasses Runtime Execution Engine
- All intents flow through Runtime
- Centralized execution guarantees

### 2. State Surface is Authoritative
- All artifact queries go through State Surface
- Artifact Registry is authoritative ledger
- Artifact Index is discovery layer

### 3. Contracts Drive Development
- Solution → Journey → Intent hierarchy
- Contract-based testing
- Parallel development enabled

### 4. Public Works Only
- No direct infrastructure access
- All infrastructure via Public Works abstractions
- Swappable backends

### 5. Smart City Primitives
- SDKs prepare contracts (Solution & Smart City)
- Primitives validate contracts (Runtime only)
- Runtime never calls SDK methods

### 6. Telemetry Everywhere
- All components report via Nurse SDK
- Control Tower aggregates via Nurse SDK
- Centralized observability

---

## 15. System vs Platform: The Difference

### Platform (What We're NOT)
- Collection of independent tools
- Users choose what to use
- No central orchestration
- Fragmented state

### System (What We ARE)
- Integrated, orchestrated whole
- Everything flows through Runtime
- Centralized state (State Surface)
- Unified data model (Artifacts)
- Contract-based development

---

## 16. Data Brain and Data Mash

### Data Brain (State Surface)
- **What:** Authoritative ledger for all artifacts
- **Where:** `symphainy_platform/runtime/state_surface.py`
- **Role:** Single source of truth for all artifacts
- **Components:** Artifact Registry, Artifact Index, Materializations

### Data Mash (Cross-Pillar Integration)
- **What:** Visualization of data flow across all pillars
- **Where:** Solution Realm, Insights Realm (Your Data Mash tab)
- **Role:** Show how artifacts connect across realms
- **Components:** Lineage visualization, cross-pillar synthesis

---

## 17. Solution → Journey → Intent: The Contract Vision

### Solution Contracts
- **Purpose:** Define business outcomes
- **Audience:** Business users, C-Suite
- **Content:** User experiences, success criteria, journey composition
- **Location:** `docs/solution_contracts/`

### Journey Contracts
- **Purpose:** Define technical workflows
- **Audience:** Developers, architects
- **Content:** Intent composition, test scenarios, completion criteria
- **Location:** `docs/journey_contracts/`

### Intent Contracts
- **Purpose:** Define atomic platform capabilities
- **Audience:** Developers, realm teams
- **Content:** Parameters, returns, idempotency, contract compliance
- **Location:** `docs/intent_contracts/`

**Benefits:**
- Clear specifications at every level
- Parallel development enabled
- Contract-based testing
- Agentic orchestration

---

## 18. How It All Works Together

### User Journey Example

```
1. User uploads file (Frontend)
    ↓
2. Experience Plane receives request
    ↓
3. Runtime Execution Engine executes `ingest_file` intent
    ↓
4. Content Realm Intent Service handles intent
    ↓
5. Public Works stores file in GCS
    ↓
6. State Surface registers file artifact
    ↓
7. Artifact Registry stores artifact record
    ↓
8. Artifact Index (Supabase) indexes for discovery
    ↓
9. User sees file in dashboard
    ↓
10. User parses file
    ↓
11. Runtime Execution Engine executes `parse_content` intent
    ↓
12. Content Realm Intent Service parses file
    ↓
13. State Surface registers parsed content artifact (with lineage)
    ↓
14. User creates deterministic embeddings
    ↓
15. Runtime Execution Engine executes `create_deterministic_embeddings` intent
    ↓
16. Content Realm Intent Service creates embeddings
    ↓
17. Public Works stores embeddings in DuckDB (via abstraction)
    ↓
18. State Surface registers embeddings artifact
    ↓
19. User creates semantic embeddings
    ↓
20. Insights Realm Intent Service creates semantic embeddings
    ↓
21. Public Works stores in ArangoDB (via abstraction)
    ↓
22. State Surface registers semantic embeddings artifact
    ↓
23. Data Mash shows complete lineage
```

**Key Points:**
- Everything flows through Runtime Execution Engine
- All artifacts registered in State Surface
- All storage via Public Works abstractions
- Complete lineage tracked
- Telemetry reported at every step

---

## 19. Why This Architecture

### Benefits

1. **Consistency:** Everything runs through Runtime, guaranteed consistency
2. **Observability:** Centralized telemetry, complete journey traces
3. **Testability:** Contract-based testing, 3D testability
4. **Scalability:** Micro-module architecture, swappable backends
5. **Maintainability:** Clear boundaries, contract-driven development
6. **Agentic:** Agents can read contracts and build

### Trade-offs

1. **Centralization:** Runtime is single point of execution (but not failure - can scale)
2. **Abstraction Overhead:** Public Works adds abstraction layer (but enables swapping)
3. **Contract Discipline:** Must maintain contracts (but enables parallel development)

---

## 20. Next Steps

### For Developers

1. **Read Contracts:** Start with solution contracts, then journey, then intent
2. **Use Base Classes:** Extend BaseOrchestrator, BaseIntentService, AgentBase, MCPServerBase
3. **Follow Patterns:** Public Works only, telemetry reporting, contract compliance
4. **Test Against Contracts:** Validate implementation against contracts

### For Agents

1. **Read Architecture North Star:** Understand system architecture
2. **Read Contracts:** Understand what to build
3. **Follow Architectural Requirements:** No anti-patterns
4. **Use Base Classes:** Don't reinvent the wheel

---

## 21. Key Takeaways

1. ✅ **System, Not Platform:** Everything flows through Runtime Execution Engine
2. ✅ **Data Brain:** State Surface is authoritative ledger for all artifacts
3. ✅ **Data Mash:** Cross-pillar integration and visualization
4. ✅ **Contract Vision:** Solution → Journey → Intent hierarchy
5. ✅ **Public Works Only:** No direct infrastructure access
6. ✅ **Smart City Primitives:** SDKs prepare, Primitives validate
7. ✅ **Telemetry Everywhere:** Nurse SDK for reporting, Control Tower for aggregation
8. ✅ **Storage Strategy:** DuckDB for deterministic, ArangoDB for semantic
9. ✅ **Agentic Orchestration:** Agents reason, Orchestrators execute
10. ✅ **Contract-Based Development:** Parallel development, clear specifications

---

**Last Updated:** January 27, 2026  
**Owner:** Architecture Team  
**Status:** ✅ **ACTIVE - REFERENCE THIS FOR SYSTEM UNDERSTANDING**
