# Architectural Requirements Update Summary

**Date:** January 27, 2026  
**Status:** ✅ **COMPREHENSIVE UPDATE COMPLETE**

---

## What Was Added

The `ARCHITECTURAL_REQUIREMENTS.md` document has been significantly expanded from 225 lines to **1,016 lines** with comprehensive patterns and requirements discovered from the codebase review.

---

## New Sections Added

### 11. Base Classes and Inheritance Patterns ✅
- **BaseContentHandler**: Base class for content intent handlers
- **AgentBase**: Base class for all agents
- **MCPServerBase**: Base class for MCP servers

**Key Points:**
- Extend base classes for common functionality
- Base classes provide logger, clock, Public Works access
- Base classes provide enabling services (lazy initialization)
- Base classes provide helper methods (artifact indexing, etc.)

---

### 12. 4-Dimensional Agentic Configuration Pattern ✅
- **Layer 1: AgentDefinition** (Platform DNA - Stable Identity)
- **Layer 2: AgentPosture** (Tenant/Solution - Behavioral Tuning)
- **Layer 3: AgentRuntimeContext** (Journey/Session - Ephemeral)
- **Layer 4: Prompt Assembly** (Derived at Runtime)

**Key Points:**
- All agents must use 4-layer model
- Layer 1: Platform-owned, stable identity (JSON/YAML config files)
- Layer 2: Tenant/solution-scoped behavioral tuning (registry)
- Layer 3: Ephemeral, session-scoped (assembled at runtime)
- Layer 4: Derived from Layers 1-3 (never stored)

**Anti-Patterns:**
- ❌ Hardcoding prompts in agent code
- ❌ Mixing identity and behavior
- ❌ Persisting runtime context

---

### 13. Smart City System Usage ✅
- **Security Guard**: Policy validation and permission checks
- **Data Steward**: Data governance and policy enforcement
- **Traffic Cop**: Rate limiting and traffic management
- **Other Primitives**: City Manager, Conductor, Curator, Librarian, Nurse, Post Office, Materialization Policy

**Key Points:**
- Use Smart City SDKs to prepare execution contracts (Solution & Smart City)
- Runtime uses Primitives to validate contracts (Runtime only)
- **⚠️ CRITICAL:** Runtime never calls SDK methods, only consumes snapshotted registry state

**Pattern:**
1. Use SDK to prepare execution contract
2. Runtime validates contract using Primitives
3. Runtime never calls SDK methods directly

---

### 14. Civic Systems Interaction ✅
- **Experience Plane**: User-facing interfaces, owns REST API and WebSocket endpoints
- **Agentic Framework**: Agent lifecycle management, MCP server management
- **Smart City System**: Policy enforcement, service coordination, registry management

**Key Points:**
- Experience Plane owns `/api/runtime/agent` (WebSocket) - even though path says "runtime"
- Path is a contract (invoke runtime on my behalf), not a locator
- Runtime never knows "users", only execution context

---

### 15. Curator and Experience Registration Patterns ✅
- **Service Registration**: Register service instances with Curator
- **Capability Registration**: Register capabilities with Curator
- **SOA API Registration**: Register SOA APIs with Curator
- **MCP Tool Registration**: Register MCP tools with Curator
- **Curator SDK Usage**: Use Curator SDK for registration and discovery

**Key Points:**
- Curator owns all registries (Service, Capability, SOA API, Tool, Agent)
- Services register with Consul (via Public Works) and local cache
- **⚠️ CRITICAL:** 
  - Curator SDK → Used by Solution & Smart City (registration, discovery)
  - Curator Data → Visible to Runtime (read-only, snapshotted registry state)
  - Runtime → Never calls Curator SDK methods, only consumes snapshotted registry state

---

### 16. SOA API Patterns ✅
- **Pattern:** Create Intent Service → Register SOA API → Expose as MCP Tool (optional)

**Key Points:**
- Intent services must be exposed as SOA APIs for realm-to-realm communication
- SOA API naming: `{service_name}.{api_name}` (e.g., `content_service.parse_file`)
- Optional: Expose as MCP tools for agentic consumption

---

### 17. MCP Server Patterns ✅
- **Pattern:** Extend MCPServerBase → Initialize → Register Tools → Expose to Agents

**Key Points:**
- MCP servers expose realm SOA APIs as MCP tools
- MCP tool naming: `{realm}_{api_name}` (e.g., `content_parse_file`)
- Tools registered via `MCPServerBase.register_tool()`
- Agents use tools via `MCPClientManager.call_tool()`

---

### 18. Experience Plane Integration ✅
- **Endpoints:** `/api/runtime/agent` (WebSocket), `/api/runtime/intent` (REST), `/api/runtime/state` (REST)

**Key Points:**
- Experience Plane owns all user-facing endpoints
- Experience Plane routes to Runtime for execution
- Experience Plane streams events back to client
- Runtime is stateless execution engine

---

### 19. Registry Ownership ✅
- **Curator owns all registries:**
  - Service Registry
  - Capability Registry
  - SOA API Registry
  - Tool Registry
  - Agent Registry (via Agentic framework)

**Key Points:**
- All registries live in Curator
- Services register with Curator
- Runtime consumes snapshotted registry state (read-only)

---

### 20. Additional Patterns ✅
- **Execution Context**: Contains tenant_id, user_id, session_id, intent, metadata, state_surface
- **State Surface**: Authoritative ledger for artifacts
- **Artifact Registry**: Artifact registration and lifecycle management

---

### 21. Validation Checklist (Updated) ✅
- Added 7 new checklist items:
  - [ ] Use base classes (BaseContentHandler, AgentBase, MCPServerBase)
  - [ ] Use 4-layer agent model (AgentDefinition, AgentPosture, AgentRuntimeContext, Prompt Assembly)
  - [ ] Use Smart City SDKs (prepare contracts) and Primitives (validate contracts)
  - [ ] Register services/capabilities/SOA APIs with Curator
  - [ ] Expose SOA APIs as MCP tools for agentic consumption
  - [ ] Experience Plane owns user-facing endpoints
  - [ ] Curator owns all registries

---

## Patterns Captured

### Base Classes
✅ BaseContentHandler  
✅ AgentBase  
✅ MCPServerBase  

### 4-Layer Agent Model
✅ AgentDefinition (Layer 1)  
✅ AgentPosture (Layer 2)  
✅ AgentRuntimeContext (Layer 3)  
✅ Prompt Assembly (Layer 4)  

### Smart City System
✅ Security Guard SDK/Primitives  
✅ Data Steward SDK/Primitives  
✅ Traffic Cop SDK/Primitives  
✅ Other Primitives (City Manager, Conductor, Curator, Librarian, Nurse, Post Office, Materialization Policy)  

### Civic Systems
✅ Experience Plane (endpoints, routing)  
✅ Agentic Framework (agents, MCP servers)  
✅ Smart City System (policies, coordination)  

### Registration Patterns
✅ Service Registration  
✅ Capability Registration  
✅ SOA API Registration  
✅ MCP Tool Registration  
✅ Curator SDK Usage  

### SOA API & MCP Patterns
✅ SOA API exposure  
✅ MCP Server patterns  
✅ Tool registration and execution  

### Registry Ownership
✅ Curator owns all registries  
✅ Runtime consumes snapshotted state  

---

## Critical Constraints Documented

### ⚠️ **CRITICAL:** SDK vs Primitives
- **SDKs:** Prepare execution contracts (used by Solution & Smart City)
- **Primitives:** Validate contracts (used by Runtime only)
- **Runtime:** Never calls SDK methods, only consumes snapshotted registry state

### ⚠️ **CRITICAL:** Curator SDK vs Runtime
- **Curator SDK:** Used by Solution & Smart City (registration, discovery)
- **Curator Data:** Visible to Runtime (read-only, snapshotted registry state)
- **Runtime:** Never calls Curator SDK methods, only consumes snapshotted registry state

### ⚠️ **CRITICAL:** Experience Plane vs Runtime
- **Experience Plane:** Owns endpoints (even if path says "runtime")
- **Path:** Contract (invoke runtime on my behalf), not a locator
- **Runtime:** Never knows "users", only execution context

---

## File Statistics

- **Original Size:** 225 lines
- **Updated Size:** 1,016 lines
- **New Content:** ~791 lines
- **New Sections:** 11 major sections (11-21)
- **New Patterns:** 20+ patterns documented

---

## Next Steps

1. ✅ Architectural requirements comprehensively documented
2. ⏳ Web agents can now reference this document when building
3. ⏳ All patterns and constraints captured
4. ⏳ Ready for implementation

---

**Last Updated:** January 27, 2026  
**Status:** ✅ **COMPREHENSIVE - READY FOR AGENT ENFORCEMENT**
