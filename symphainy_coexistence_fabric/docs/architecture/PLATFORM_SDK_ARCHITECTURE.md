# Platform SDK Architecture

**Status:** Canonical (January 2026)  
**Purpose:** Define the Platform SDK - the Semantic Operating System Kernel for SymphAIny.

> **SymphAIny is the Intent-Driven Enterprise Operating System that transforms how organizations integrate, reason, and execute — using intent as the semantic kernel to modernize operations without rewrites and turn integration expertise into reusable products.**

---

## Overview

The Platform SDK is **not just an SDK** — it is the **Semantic Operating System Kernel** that:

1. **Translates** civic protocols into Intent primitives
2. **Defines** the Intent Language that all civic protocols compile into
3. **Enables** Solutions, Journeys, and Intents as first-class computational objects

```
┌─────────────────────────────────────────────────────────────────┐
│                        SOLUTIONS                                │
│              (Productized meaning — client value)               │
├─────────────────────────────────────────────────────────────────┤
│                        JOURNEYS                                 │
│                   (Orchestration logic)                         │
├─────────────────────────────────────────────────────────────────┤
│                         INTENTS                                 │
│    Domain          │    Connective      │    Foundational       │
│  (Client IP)       │   (Product IP)     │     (Core IP)         │
├────────────────────┴────────────────────┴───────────────────────┤
│              PLATFORM SDK — SEMANTIC OS KERNEL                  │
│     ctx.governance │ ctx.reasoning │ ctx.interaction │          │
│     ctx.execution  │ ctx.enabling                               │
├─────────────────────────────────────────────────────────────────┤
│                     CIVIC PROTOCOLS                             │
│     Smart City  │  Agentic  │  Experience  │  Runtime           │
├─────────────────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE LAYER                          │
│     (Public Works — adapters, abstractions, protocols)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Five Semantic Services on ctx

When an intent service executes, it receives `PlatformContext` (`ctx`) with five semantic services:

| Service | Semantic Role | What It Translates |
|---------|--------------|-------------------|
| `ctx.governance` | Governance Semantics | Policy, authority, trust → `assert_authority()`, `delegate()` |
| `ctx.reasoning` | Reasoning Semantics | Thinking, planning, decision → `delegate()`, `plan()`, `decide()` |
| `ctx.interaction` | Interaction Semantics | Perception, conversation → `present()`, `converse()`, `notify()` |
| `ctx.execution` | Execution Semantics | Compute, storage, orchestration → `schedule()`, `store()`, `retrieve()` |
| `ctx.enabling` | Intent Semantics | Meaning, composition, control → `compose()`, `resolve()`, `emit()` |

Plus Runtime-provided resources:
- `ctx.state_surface` — State storage/retrieval (Runtime owns)
- `ctx.wal` — Write-ahead log (Runtime owns)
- `ctx.artifacts` — Artifact registry (Runtime owns)

### The Translation Pattern

The Platform SDK translates low-level protocols into semantic primitives:

```python
# Instead of (low-level protocol):
smart_city_sdk.check_role("EmergencyManager")

# Intent sees (semantic primitive):
ctx.governance.assert_authority("EmergencyResponse")

# Instead of (low-level protocol):
agentic_sdk.spawn_agent(config)

# Intent sees (semantic primitive):
ctx.reasoning.delegate("damage_assessment")

# Instead of (low-level protocol):
runtime.execute_in_container(task)

# Intent sees (semantic primitive):
ctx.execution.schedule("data_ingest")
```

---

## ctx.platform (Capability-Oriented)

`ctx.platform` provides capability-oriented operations that wrap Public Works protocols. The primary axis is **infrastructure swappability** — implementations can be swapped without changing the interface.

### Parsing Operations

```python
# Unified parsing interface
result = await ctx.platform.parse(file_ref, file_type="pdf", options={...})

# Type-specific helpers
result = await ctx.platform.parse_csv(file_ref, options={...})
result = await ctx.platform.parse_pdf(file_ref, options={...})
result = await ctx.platform.parse_excel(file_ref, options={...})
result = await ctx.platform.parse_word(file_ref, options={...})
result = await ctx.platform.parse_mainframe(file_ref, copybook_ref, options={...})
```

### Visualization Operations

```python
result = await ctx.platform.visualize(data, viz_type="chart", options={...})
```

### Embedding Operations

```python
result = await ctx.platform.embed(content, model="text-embedding-ada-002")
```

### Ingestion Operations

```python
result = await ctx.platform.ingest(source, source_type="file", tenant_id, session_id)
```

### Storage Operations

```python
await ctx.platform.store_artifact(artifact_id, data, content_type, tenant_id)
data = await ctx.platform.retrieve_artifact(artifact_id, tenant_id)
```

### Semantic Data Operations

```python
await ctx.platform.store_semantic(content_id, content, embedding, tenant_id)
results = await ctx.platform.search_semantic(query_embedding, tenant_id, limit=10)
```

---

## ctx.governance (Smart City)

`ctx.governance` wraps all 9 Smart City SDKs into a unified governance interface.

| Role | Access | Purpose |
|------|--------|---------|
| Data Steward | `ctx.governance.data_steward` | Data boundaries, materialization, Records of Fact |
| Security Guard | `ctx.governance.auth` | Authentication, authorization |
| Curator | `ctx.governance.registry` | Capability registries |
| Librarian | `ctx.governance.search` | Knowledge search, schemas |
| City Manager | `ctx.governance.policy` | Global policy, tenancy |
| Traffic Cop | `ctx.governance.sessions` | Session management |
| Post Office | `ctx.governance.events` | Event routing |
| Conductor | `ctx.governance.workflows` | Workflow/saga primitives |
| Nurse | `ctx.governance.telemetry` | Telemetry, retries, self-healing |

### Examples

```python
# Check data access boundary
access = await ctx.governance.data_steward.request_data_access(
    intent=intent_dict,
    context=context_dict,
    external_source_type="file",
    external_source_identifier=file_path
)

# Validate session
session = await ctx.governance.sessions.validate_session(session_id, tenant_id)

# Search knowledge
results = await ctx.governance.search.search_knowledge(query, tenant_id)

# Record telemetry
await ctx.governance.telemetry.record_telemetry(data, tenant_id)
```

---

## ctx.reasoning (Agentic)

`ctx.reasoning` wraps the Agentic civic system for LLM and agent access.

### LLM Service

```python
# Complete a prompt
result = await ctx.reasoning.llm.complete(
    prompt="Analyze this data...",
    model="gpt-4",
    temperature=0.7,
    max_tokens=1000
)

# Generate embeddings
result = await ctx.reasoning.llm.embed(content, model="text-embedding-ada-002")
```

### Agent Service

```python
# Get an agent
agent = ctx.reasoning.agents.get("guide_agent")

# Invoke an agent
result = await ctx.reasoning.agents.invoke("sop_generation_agent", params)

# Invoke by type
result = await ctx.reasoning.agents.invoke_by_type("analysis", params)

# Multi-agent collaboration
result = await ctx.reasoning.agents.collaborate(
    agent_ids=["agent1", "agent2"],
    task=task_definition
)

# List agents
agents = ctx.reasoning.agents.list()
types = ctx.reasoning.agents.list_types()
```

---

## Creating Intent Services

Use `PlatformIntentService` as the base class for new intent services:

```python
from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)

class ParseContentService(PlatformIntentService):
    intent_type = "parse_content"
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        # Validate parameters
        is_valid, error = self.validate_params(ctx, ["file_reference", "file_type"])
        if not is_valid:
            return {"status": "failed", "error": error}
        
        # Get parameters
        file_ref = self.get_param(ctx, "file_reference")
        file_type = self.get_param(ctx, "file_type")
        
        # Parse using ctx.platform
        result = await ctx.platform.parse(file_ref, file_type)
        
        if result["status"] == "failed":
            return {"artifacts": {}, "events": [], "status": "failed", "error": result["error"]}
        
        # Create and register artifact
        artifact = self.create_artifact_record(
            artifact_id=f"parsed:{ctx.execution_id}",
            artifact_type="parsed_content",
            ctx=ctx,
            semantic_descriptor=SemanticDescriptor(
                content_type="parsed_document",
                summary=f"Parsed {file_type} content"
            )
        )
        await self.register_artifact(artifact, ctx)
        
        return {
            "artifacts": {"parsed_content": result["parsed_content"]},
            "events": [{"type": "content_parsed", "file_type": file_type}],
            "status": "success"
        }
```

---

## Migration from BaseIntentService

### Old Pattern (BaseIntentService)

```python
class OldService(BaseIntentService):
    def __init__(self, service_id, intent_type, public_works, state_surface):
        super().__init__(service_id, intent_type, public_works, state_surface)
    
    async def execute(self, context: ExecutionContext, params: Dict) -> Dict:
        # Direct access to public_works
        parser = self.public_works.pdf_processing_abstraction
        result = await parser.parse(...)
        return {"artifacts": {...}, "events": [...]}
```

### New Pattern (PlatformIntentService)

```python
class NewService(PlatformIntentService):
    intent_type = "my_intent"
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        # Use ctx.platform for capability operations
        result = await ctx.platform.parse(file_ref, file_type="pdf")
        
        # Use ctx.governance for Smart City SDKs
        access = await ctx.governance.data_steward.request_data_access(...)
        
        # Use ctx.reasoning for LLM/agents
        analysis = await ctx.reasoning.llm.complete(prompt)
        
        return {"artifacts": {...}, "events": [...], "status": "success"}
```

---

## Boundary Rules

### What Intent Services CAN Access

- `ctx.platform.*` — All capability operations
- `ctx.governance.*` — All Smart City SDKs
- `ctx.reasoning.*` — LLM and agents
- `ctx.state_surface` — State storage (Runtime)
- `ctx.artifacts` — Artifact registry (Runtime)
- `ctx.wal` — Write-ahead log (Runtime)

### What Intent Services CANNOT Access

- Public Works abstractions directly (use `ctx.platform` instead)
- Runtime internals
- Civic system internals
- Infrastructure directly (Redis, Arango, GCS, etc.)

### Experience Surfaces

Experience surfaces (UIs, dashboards, agents, MCP servers) use **Experience SDK only**:
- `query_state`, `invoke_intent`, `trigger_journey`, `subscribe`

They do NOT access Platform SDK (`ctx`).

---

## File Structure

```
symphainy_platform/civic_systems/platform_sdk/
├── __init__.py                    # Exports
├── context.py                     # PlatformContext, PlatformContextFactory
├── intent_service_base.py         # PlatformIntentService base class
└── services/
    ├── __init__.py
    ├── governance_service.py      # ctx.governance (Smart City)
    ├── reasoning_service.py       # ctx.reasoning (Agentic)
    └── platform_service.py        # ctx.platform (capabilities)
```

---

## References

- [CANONICAL_PLATFORM_ARCHITECTURE.md](CANONICAL_PLATFORM_ARCHITECTURE.md) — Platform structure
- [EXPERIENCE_SDK_CONTRACT.md](EXPERIENCE_SDK_CONTRACT.md) — Experience SDK for external consumers
- [RUNTIME_CONTRACTS.md](RUNTIME_CONTRACTS.md) — Runtime participation contracts
- [BOOT_PHASES.md](BOOT_PHASES.md) — Boot sequence

---

**Last Updated:** January 29, 2026  
**Owner:** Platform Architecture Team
