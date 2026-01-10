# Phase 2: Curator Registries - Complete Picture

**Date:** January 2026  
**Status:** 🔍 **REVIEWING ACTUAL STRUCTURE**  
**Issue:** I missed that Curator has separate registries for services, agents, and tools

---

## ✅ What Curator Actually Has (from symphainy_source)

### Core Registries in Curator Foundation

1. **Service Registry** (`registered_services` dict)
   - Service instances + metadata
   - Registered via `register_service()`
   - Used for service discovery (Consul)

2. **Capability Registry** (`CapabilityRegistryService`)
   - Service capabilities (what services can do)
   - Registered via `register_capability()` or as part of `register_service()`
   - Used for intent → capability lookup

3. **SOA API Registry** (`soa_api_registry` dict)
   - SOA API endpoints for realm consumption
   - Registered via `register_soa_api()`
   - Used for realm-to-realm communication

4. **MCP Tool Registry** (`mcp_tool_registry` dict)
   - MCP tools for agent access
   - Registered via `register_mcp_tool()`
   - Used for agent-to-service tool access

5. **Agent Capability Registry** (`AgentCapabilityRegistryService`)
   - Agent capabilities (what agents can do)
   - Registered via `register_agent()` or `register_agent_capabilities()`
   - Used for agent discovery and management

6. **MCP Server Registry** (`mcp_server_registry` dict)
   - MCP server instances
   - Registered via `register_mcp_server()`
   - Used for MCP server discovery

---

## ⚠️ What I Built (Incomplete)

**Current Implementation:**
- ✅ Capability registry (correct)
- ✅ Intent → capability lookup (correct)
- ❌ **MISSING:** Service registry
- ❌ **MISSING:** Agent registry
- ❌ **MISSING:** Tool registry
- ❌ **MISSING:** SOA API registry
- ❌ **MISSING:** MCP server registry

---

## 🎯 Correct Pattern

### Registration Methods

1. **Services** → `register_service(service_instance, service_metadata)`
   - Registers service instance (for Consul)
   - Registers capabilities (capability registry)
   - Registers SOA APIs (SOA API registry)
   - Registers MCP tools (MCP tool registry)

2. **Agents** → `register_agent(agent_id, agent_name, characteristics, contracts)`
   - Registers agent capabilities (agent capability registry)
   - Registers agent metadata

3. **Tools** → `register_mcp_tool(tool_name, tool_definition)`
   - Registers MCP tool (MCP tool registry)
   - Used by agents

---

## 🔧 What Needs to Be Added

### 1. Service Registry

**File:** `symphainy_platform/foundations/curator/registry/service_registry.py`

**Purpose:** Track service instances and metadata

**Methods:**
- `register_service(service_instance, service_metadata)`
- `get_service(service_name)`
- `list_services(realm=None)`
- `deregister_service(service_name)`

### 2. Agent Registry

**File:** `symphainy_platform/foundations/curator/registry/agent_registry.py`

**Purpose:** Track agent instances and capabilities

**Methods:**
- `register_agent(agent_id, agent_name, characteristics, contracts)`
- `get_agent(agent_name)`
- `list_agents(realm=None)`
- `deregister_agent(agent_name)`

### 3. Tool Registry

**File:** `symphainy_platform/foundations/curator/registry/tool_registry.py`

**Purpose:** Track MCP tools

**Methods:**
- `register_mcp_tool(tool_name, tool_definition)`
- `get_tool(tool_name)`
- `list_tools(realm=None)`
- `deregister_tool(tool_name)`

### 4. SOA API Registry

**File:** `symphainy_platform/foundations/curator/registry/soa_api_registry.py`

**Purpose:** Track SOA API endpoints

**Methods:**
- `register_soa_api(api_name, api_definition)`
- `get_api(api_name)`
- `list_apis(service_name=None)`

### 5. Integration with Public Works Service Discovery

**File:** `symphainy_platform/foundations/curator/foundation_service.py`

**Update:**
- Get service discovery abstraction from Public Works
- Use it for Consul registration when registering services

---

## ✅ What's Correct

1. ✅ **Capability registry** - Correct (Curator's domain)
2. ✅ **Intent → capability lookup** - Correct (Curator's domain)
3. ✅ **State abstraction** - Correct (Public Works domain)

---

## ⚠️ What Needs to Be Added

1. ⚠️ **Service registry** - Add to Curator
2. ⚠️ **Agent registry** - Add to Curator
3. ⚠️ **Tool registry** - Add to Curator
4. ⚠️ **SOA API registry** - Add to Curator
5. ⚠️ **Service discovery abstraction** - Add to Public Works (for Consul)
6. ⚠️ **Integration** - Curator uses Public Works service discovery

---

## 🎯 Recommendation

**Build complete Curator with all registries:**
- Service registry (for service instances)
- Agent registry (for agent capabilities)
- Tool registry (for MCP tools)
- SOA API registry (for realm-to-realm APIs)
- Capability registry (already built)
- Integration with Public Works service discovery

**Next Steps:**
1. Add all missing registries to Curator
2. Add service discovery abstraction to Public Works
3. Integrate Curator with Public Works service discovery
4. Then proceed with Runtime integration

---

**Last Updated:** January 2026
