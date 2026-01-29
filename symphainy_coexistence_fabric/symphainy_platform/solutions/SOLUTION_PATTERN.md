# Solution Pattern Documentation

**Status:** Canonical (January 2026)  
**Applies to:** All realm solutions

---

## Overview

This document describes the Solution Pattern used to compose journeys, expose SOA APIs, and wire up with the frontend via Experience SDK.

### Key Principles

1. **One Solution per Realm** - Each realm has one solution (e.g., ContentSolution)
2. **All solutions MUST inherit from BaseSolution** - Contract and shared behavior live in `symphainy_platform/bases/solution_base.py`; type-hint as `BaseSolution` (no separate Protocol). The base is **lean** (see `docs/architecture/SOLUTION_BASE_DISCIPLINE.md`): no ballooning, no compliance layers; only what fixes the documented mismatches.
3. **One MCP Server per Solution** - Prevents server sprawl
4. **Journeys compose intents** - Journey orchestrators compose intent services into complete user workflows
5. **compose_journey intent** - Special intent for programmatic journey invocation

---

## Architecture

```
symphainy_platform/solutions/
├── __init__.py
├── SOLUTION_PATTERN.md
└── content_solution/           # One solution per realm
    ├── __init__.py
    ├── content_solution.py     # Main solution class
    ├── journeys/               # Journey orchestrators
    │   ├── __init__.py
    │   └── file_upload_materialization_journey.py
    └── mcp_server/             # Single MCP server per solution
        ├── __init__.py
        └── content_solution_mcp_server.py
```

---

## Solution Class

The Solution class is the top-level organizational unit. **All solutions MUST inherit from `BaseSolution`** (see `symphainy_platform/bases/solution_base.py`); type-hint as `BaseSolution`. The base provides default implementations for `get_journeys()`, `get_journey()`, `get_experience_sdk_config()`, and a static helper `build_journey_result()` for the standard journey result shape.

### Responsibilities

1. **Compose journeys** - Initialize and manage journey orchestrators
2. **Expose SOA APIs** - Provide solution-level APIs
3. **Handle compose_journey intent** - Route to appropriate journey
4. **Wire Experience SDK** - Provide configuration for frontend integration

### Key Methods

Canonical method list and behavior: **`symphainy_platform/bases/solution_base.py`** (BaseSolution).

```python
class ContentSolution(BaseSolution):  # MUST inherit from BaseSolution
    SOLUTION_ID = "content_solution"
    SUPPORTED_INTENTS = [...]

    # Core methods (subclass must implement)
    async def handle_intent(intent, context) -> Dict
    async def _handle_compose_journey(intent, context) -> Dict

    # Journey management (default from base via _journeys)
    def get_journeys() -> Dict[str, Any]
    def get_journey(journey_id) -> Optional[Any]

    # SOA APIs (subclass must implement)
    def get_soa_apis() -> Dict[str, Dict]

    # MCP Server — async; callers MUST use await
    async def initialize_mcp_server()

    # Experience SDK (default from base; override if needed)
    def get_experience_sdk_config() -> Dict
```

### Standard Journey Result Shape

Every journey `compose_journey` return MUST include: **success**, **artifacts**, **events**, **journey_id**, **journey_execution_id**. On failure set `success: False` and put error details in artifacts or events. Use **`BaseSolution.build_journey_result(success, journey_id, journey_execution_id, artifacts, events)`** so all journeys return the same shape; tests and frontend assert on `success` and known keys.

### Async Contract

**`initialize_mcp_server()` is async.** Tests and callers MUST use `await solution.initialize_mcp_server()` (e.g. in async tests with `@pytest.mark.asyncio`).

---

## Journey Orchestrator

Journey orchestrators compose intent services into complete user workflows.

### Responsibilities

1. **Compose journey** - Execute intents in sequence
2. **Validate parameters** - Ensure journey parameters are valid
3. **Track telemetry** - Record journey start/complete/fail
4. **Provide SOA APIs** - Expose journey actions as APIs

### Key Methods

```python
class FileUploadMaterializationJourney:
    # Journey identification
    JOURNEY_ID = "file_upload_materialization"
    JOURNEY_NAME = "File Upload & Materialization"
    
    # Core method
    async def compose_journey(context, journey_params) -> Dict
    
    # SOA APIs for MCP tools
    def get_soa_apis() -> Dict[str, Dict]
```

### Journey Flow

```
compose_journey(context, params)
    ├── Validate parameters
    ├── Execute step 1 (e.g., ingest_file)
    ├── Execute step 2 (e.g., save_materialization)
    └── Return structured result with artifacts and events
```

---

## MCP Server

One MCP server per solution aggregates tools from all journeys.

### Responsibilities

1. **Collect SOA APIs** - From solution and all journeys
2. **Register MCP tools** - With appropriate naming convention
3. **Provide usage guide** - For agent consumption

### Tool Naming Convention

```
content_{action}
```

Examples:
- `content_upload_file`
- `content_save_materialization`
- `content_upload_and_materialize`
- `content_compose_journey`

### Key Methods

```python
class ContentSolutionMCPServer(MCPServerBase):
    async def initialize() -> bool
    def get_usage_guide() -> Dict
    async def get_health_status() -> Dict
```

---

## compose_journey Intent Pattern

The special `compose_journey` intent allows programmatic journey invocation.

### Intent Structure

```python
intent = IntentFactory.create_intent(
    intent_type="compose_journey",
    tenant_id=tenant_id,
    session_id=session_id,
    solution_id="content_solution",
    parameters={
        "journey_id": "file_upload_materialization",
        "journey_params": {
            "file_content": "<base64>",
            "file_name": "example.pdf",
            "content_type": "unstructured",
            "file_type": "pdf"
        }
    }
)
```

### Frontend Usage (Experience SDK)

```typescript
// Option 1: Submit compose_journey intent
const result = await experienceSDK.submitIntent({
    intent_type: "compose_journey",
    parameters: {
        journey_id: "file_upload_materialization",
        journey_params: { ... }
    }
});

// Option 2: Use MCP tool directly
const result = await mcpClient.callTool("content_upload_and_materialize", {
    file_content: "<base64>",
    file_name: "example.pdf"
});
```

---

## Adding a New Journey

### Step 1: Create Journey Orchestrator

```python
# symphainy_platform/solutions/content_solution/journeys/file_parsing_journey.py

class FileParsingJourney:
    JOURNEY_ID = "file_parsing"
    JOURNEY_NAME = "File Parsing"
    
    async def compose_journey(self, context, journey_params):
        # Validate
        # Execute steps
        # Return result
    
    def get_soa_apis(self) -> Dict:
        return {
            "parse_file": {...},
            "get_parsed_content": {...}
        }
```

### Step 2: Register in Solution

```python
# In ContentSolution._initialize_journeys()
self._journeys["file_parsing"] = FileParsingJourney(
    public_works=self.public_works,
    state_surface=self.state_surface
)
```

### Step 3: Update Intent Mapping

```python
# In ContentSolution._find_journey_for_intent()
intent_to_journey = {
    ...
    "parse_content": "file_parsing",
}
```

### Step 4: Export from __init__.py

```python
# journeys/__init__.py
from .file_parsing_journey import FileParsingJourney
__all__ = [..., "FileParsingJourney"]
```

---

## Adding a New Solution (for Other Realms)

### Step 1: Create Directory Structure

```
symphainy_platform/solutions/insights_solution/
├── __init__.py
├── insights_solution.py
├── journeys/
│   ├── __init__.py
│   └── data_analysis_journey.py
└── mcp_server/
    ├── __init__.py
    └── insights_solution_mcp_server.py
```

### Step 2: Implement Solution Class

Follow ContentSolution pattern:
- **Inherit from BaseSolution** (symphainy_platform/bases/solution_base.py)
- Define SOLUTION_ID, SUPPORTED_INTENTS
- Override _initialize_journeys() to populate self._journeys
- Implement handle_intent() and get_soa_apis()
- Override get_experience_sdk_config() only if custom shape needed; otherwise base default includes top-level available_journeys and nested structure
- Use BaseSolution.build_journey_result() in journeys for standard result shape

### Step 3: Implement MCP Server

Follow ContentSolutionMCPServer pattern:
- Extend MCPServerBase
- Collect SOA APIs from journeys
- Register tools with realm prefix (e.g., `insights_`)

### Step 4: Export from Solutions Package

```python
# symphainy_platform/solutions/__init__.py
from .insights_solution import InsightsSolution
__all__ = ["ContentSolution", "InsightsSolution"]
```

---

## Best Practices

### Do

- ✅ Inherit from BaseSolution; type-hint as BaseSolution
- ✅ One solution per realm
- ✅ One MCP server per solution
- ✅ Use compose_journey for programmatic invocation
- ✅ Return standard journey result shape (success, artifacts, events, journey_id, journey_execution_id) via BaseSolution.build_journey_result()
- ✅ Journeys compose intents (not implement business logic)
- ✅ Return structured artifacts with semantic_payload and renderings
- ✅ Record telemetry at journey start/complete/fail
- ✅ Validate journey parameters before execution
- ✅ Use await when calling initialize_mcp_server()

### Don't

- ❌ Create multiple MCP servers per solution
- ❌ Implement business logic in Solution class
- ❌ Skip parameter validation
- ❌ Return unstructured results
- ❌ Access infrastructure directly (use Public Works)

---

## Lessons Learned

1. **Journey Orchestrators are thin** - They compose intents, not implement logic
2. **MCP tool naming matters** - Consistent prefix (realm_action) helps agent discovery
3. **State Surface integration** - Journeys update artifact lifecycle, create pending journeys
4. **Telemetry is critical** - Record at journey level for observability
5. **compose_journey is flexible** - Can be invisible to frontend or exposed as API

---

**Last Updated:** January 27, 2026  
**Owner:** Platform Architecture Team
