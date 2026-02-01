# Disposable Wrapper Pattern

**Status:** Canonical (January 2026)  
**Purpose:** Ensure Platform SDK wrappers can be replaced without breaking capability services  
**Audience:** Team A (Takeoff), Team B (Landing)

---

## The CIO Directive

> *"Every provisional wrapper must be disposable: no logic, no caching, no business assumptions; pure delegation + light shaping only."*

This ensures that when Team A finalizes the real Platform SDK implementations, Team B's capability services continue to work without modification.

---

## What "Disposable" Means

A wrapper is **disposable** if:

1. **No Logic** — Wrapper doesn't make decisions; it delegates
2. **No Caching** — Wrapper doesn't store state between calls
3. **No Business Assumptions** — Wrapper doesn't encode domain knowledge
4. **Pure Delegation** — Wrapper calls underlying service and returns result
5. **Light Shaping** — Wrapper may reshape parameters/results for consistency

### The Test

If you can delete the wrapper class and replace it with a different implementation that has the same method signatures, and all capability services still work — the wrapper is disposable.

---

## Pattern: What Wrappers Should Do

### ✅ ALLOWED: Pure Delegation

```python
class PlatformService:
    """Wrapper delegates to underlying abstraction."""
    
    async def parse(self, file_reference: str, file_type: str, options: dict) -> dict:
        # Get the protocol-typed abstraction
        parser = self._parsers.get(file_type)
        if not parser:
            raise ValueError(f"No parser for: {file_type}")
        
        # Pure delegation - call and return
        result = await parser.parse(file_reference, options)
        
        # Light shaping - consistent return format
        return {
            "file_reference": file_reference,
            "file_type": file_type,
            "parsed_content": result.content,
            "status": "success"
        }
```

### ✅ ALLOWED: Light Shaping

```python
async def ingest_file(self, file_data: bytes, tenant_id: str, ...) -> dict:
    """Light shaping: normalize input format for underlying abstraction."""
    
    # Shape input into protocol format
    request = IngestionRequest(
        ingestion_type=IngestionType.UPLOAD,
        tenant_id=tenant_id,
        data=file_data,
        ...
    )
    
    # Delegate
    result = await self._ingestion.ingest_data(request)
    
    # Shape output for consistent API
    return {
        "success": result.success,
        "file_id": result.file_id,
        "status": "success" if result.success else "failed"
    }
```

### ✅ ALLOWED: Error Normalization

```python
async def visualize(self, data: dict, viz_type: str) -> dict:
    """Normalize errors into consistent format."""
    try:
        result = await self._visual_generation.generate(data, viz_type)
        return {"result": result, "status": "success"}
    except Exception as e:
        # Normalize error format - this is OK
        return {"error": str(e), "status": "failed"}
```

---

## Anti-Pattern: What Wrappers Should NOT Do

### ❌ FORBIDDEN: Business Logic

```python
# BAD - wrapper makes business decisions
async def parse(self, file_reference: str, file_type: str) -> dict:
    # ❌ Business logic in wrapper
    if file_type == "mainframe" and not self._has_copybook(file_reference):
        # This is a business rule, not a wrapper concern
        return {"error": "Mainframe files require copybook", "status": "failed"}
    
    # ❌ More business logic
    if self._file_size(file_reference) > 100_000_000:
        return {"error": "File too large for parsing", "status": "failed"}
```

**Where this belongs:** In the capability service (intent handler), not the wrapper.

### ❌ FORBIDDEN: Caching

```python
# BAD - wrapper caches results
class PlatformService:
    def __init__(self):
        self._parse_cache = {}  # ❌ No caching in wrapper
    
    async def parse(self, file_reference: str, file_type: str) -> dict:
        cache_key = f"{file_reference}:{file_type}"
        
        # ❌ Caching logic
        if cache_key in self._parse_cache:
            return self._parse_cache[cache_key]
        
        result = await self._do_parse(file_reference, file_type)
        self._parse_cache[cache_key] = result  # ❌ Caching
        return result
```

**Where this belongs:** In the underlying abstraction or in the capability service if needed.

### ❌ FORBIDDEN: State Accumulation

```python
# BAD - wrapper accumulates state
class ReasoningService:
    def __init__(self):
        self._conversation_history = []  # ❌ State in wrapper
    
    async def complete(self, prompt: str) -> dict:
        # ❌ Using accumulated state
        full_prompt = "\n".join(self._conversation_history) + "\n" + prompt
        result = await self._llm.complete(full_prompt)
        
        # ❌ Accumulating state
        self._conversation_history.append(prompt)
        self._conversation_history.append(result["content"])
        
        return result
```

**Where this belongs:** In the agent or capability service that manages conversation.

### ❌ FORBIDDEN: Orchestration

```python
# BAD - wrapper orchestrates multiple steps
async def ingest_and_parse(self, file_data: bytes, file_type: str) -> dict:
    # ❌ Multi-step orchestration in wrapper
    ingest_result = await self.ingest_file(file_data)
    if not ingest_result["success"]:
        return ingest_result
    
    parse_result = await self.parse(ingest_result["file_reference"], file_type)
    
    # ❌ Combining results
    return {
        "file_id": ingest_result["file_id"],
        "parsed_content": parse_result["parsed_content"],
        "status": "success"
    }
```

**Where this belongs:** In a Journey or Saga orchestrator, not the wrapper.

---

## Current Platform SDK Wrappers: Compliance Audit

### PlatformService (`ctx.platform`)

| Method | Compliant? | Notes |
|--------|------------|-------|
| `parse()` | ✅ Yes | Pure delegation to parser |
| `parse_csv()`, etc. | ✅ Yes | Convenience delegation |
| `visualize()` | ✅ Yes | Pure delegation |
| `embed()` | ✅ Yes | Pure delegation |
| `ingest_file()` | ✅ Yes | Light shaping + delegation |
| `ingest_edi()` | ✅ Yes | Light shaping + delegation |
| `ingest_api()` | ✅ Yes | Light shaping + delegation |
| `store_artifact()` | ✅ Yes | Pure delegation |
| `retrieve_artifact()` | ✅ Yes | Pure delegation |
| `store_semantic()` | ✅ Yes | Pure delegation |
| `search_semantic()` | ✅ Yes | Pure delegation |
| `get_file_metadata()` | ✅ Yes | Pure delegation |
| `get_pending_intents()` | ✅ Yes | Pure delegation |
| `create_deterministic_embeddings()` | ✅ Fixed | Now accepts optional execution_context parameter |
| `get_parsed_file()` | ✅ Fixed | Now accepts optional execution_context parameter |

**Status:** Both methods now accept an optional `execution_context` parameter. Callers should pass this to maintain proper audit trail. Legacy callers without context will trigger a warning.

### GovernanceService (`ctx.governance`)

| Property | Compliant? | Notes |
|----------|------------|-------|
| `data_steward` | ✅ Yes | Returns SDK instance |
| `auth` | ✅ Yes | Returns SDK instance |
| `registry` | ✅ Yes | Returns SDK instance |
| `search` | ✅ Yes | Returns SDK instance |
| `policy` | ✅ Yes | Returns SDK instance |
| `sessions` | ✅ Yes | Returns SDK instance |
| `events` | ✅ Yes | Returns SDK instance |
| `workflows` | ✅ Yes | Returns SDK instance |
| `telemetry` | ✅ Yes | Returns SDK instance |

**Status:** Fully compliant. GovernanceService is a pure facade that returns pre-built SDK instances.

### ReasoningService (`ctx.reasoning`)

| Property/Method | Compliant? | Notes |
|-----------------|------------|-------|
| `llm.complete()` | ✅ Yes | Pure delegation to adapter |
| `llm.embed()` | ✅ Yes | Pure delegation |
| `agents.get()` | ✅ Yes | Lazy instantiation (initialization logic, acceptable) |
| `agents.invoke()` | ✅ Yes | Delegation to agent |
| `agents.collaborate()` | ⚠️ Deprecated | Orchestration logic - use Journey orchestrators |

**Status:** 
- `_lazy_instantiate_agent()` is acceptable — it's initialization/factory logic, not business logic.
- `collaborate()` is **deprecated** — it violates the pattern by containing orchestration logic. Use Journey orchestrators for multi-agent workflows. The method is retained for backward compatibility but emits a deprecation warning.

---

## Recommendations for Team A

When you build the "real" Platform SDK to replace our provisional wrappers:

1. **Keep the method signatures** — Our capability services call these methods
2. **Keep the return shapes** — We expect `{status, artifacts, ...}` patterns
3. **You can change internals** — How you get the protocols, how you wire adapters
4. **You own caching/state** — If needed, implement at abstraction layer

### What Team B Guarantees

Our capability services:
- Call wrapper methods with documented parameters
- Expect documented return shapes
- Do NOT depend on wrapper internals
- Do NOT expect wrapper state between calls

### Safe Replacement Test

```python
# Team A can replace this:
class PlatformService:
    async def parse(self, file_reference, file_type, options) -> dict:
        # Team B's provisional implementation
        ...

# With this:
class PlatformService:
    async def parse(self, file_reference, file_type, options) -> dict:
        # Team A's real implementation
        ...

# As long as return shape matches, Team B's services work.
```

---

## Summary

| Rule | Description |
|------|-------------|
| **No Logic** | Wrappers don't make decisions |
| **No Caching** | Wrappers don't store state |
| **No Business Assumptions** | Wrappers don't encode domain rules |
| **Pure Delegation** | Call underlying service, return result |
| **Light Shaping** | Normalize input/output formats only |

**The guarantee:** If Team A replaces our wrappers with different implementations that have the same method signatures and return shapes, Team B's 52 capability services will continue to work.

---

## Appendix: Method Signatures for Team A Reference

### PlatformService Key Methods

```python
# Parsing
async def parse(file_reference: str, file_type: str, options: dict = None) -> dict
# Returns: {file_reference, file_type, parsed_content, metadata, status}

# Ingestion
async def ingest_file(file_data: bytes, tenant_id: str, session_id: str, 
                      source_metadata: dict, options: dict = None) -> dict
# Returns: {success, file_id, file_reference, storage_location, status}

# Storage
async def store_artifact(artifact_id: str, data: bytes, content_type: str,
                         tenant_id: str, metadata: dict = None) -> dict
# Returns: {artifact_id, storage_location, status}

async def retrieve_artifact(artifact_id: str, tenant_id: str) -> Optional[bytes]
# Returns: bytes or None

# Semantic
async def store_semantic(content_id: str, content: str, embedding: List[float],
                         tenant_id: str, metadata: dict = None) -> dict
# Returns: {content_id, status}

async def search_semantic(query_embedding: List[float], tenant_id: str,
                          limit: int = 10, filters: dict = None) -> List[dict]
# Returns: List of matching content dicts
```

### GovernanceService Properties

```python
# All return SDK instances with their own method contracts
data_steward: DataStewardSDK
auth: SecurityGuardSDK
registry: CuratorSDK
search: LibrarianSDK
policy: CityManagerSDK
sessions: TrafficCopSDK
events: PostOfficeSDK
workflows: ConductorSDK
telemetry: NurseSDK
```

### ReasoningService Methods

```python
# LLM
async def llm.complete(prompt: str, model: str = None, temperature: float = 0.7,
                       max_tokens: int = 1000) -> dict
# Returns: {content, model, usage, finish_reason}

async def llm.embed(content: str, model: str = None) -> dict
# Returns: {embedding, model, dimensions}

# Agents
def agents.get(agent_id: str) -> Optional[Agent]
async def agents.invoke(agent_id: str, params: dict, context: dict = None) -> dict
# Returns: {agent_id, result, status}
```
