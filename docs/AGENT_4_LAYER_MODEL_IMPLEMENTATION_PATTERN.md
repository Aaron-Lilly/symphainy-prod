# Agent 4-Layer Model Implementation Pattern

**Date:** January 24, 2026  
**Status:** ✅ **VALIDATED PATTERN**  
**Reference Agent:** `GuideAgent`

---

## Executive Summary

This document defines the **standard pattern** for implementing agents that fully align with the 4-layer agentic system model. All agents must follow this pattern to ensure consistency, maintainability, and proper integration with the platform's agentic capabilities.

---

## The 4-Layer Model

1. **Layer 1: AgentDefinition** (Platform DNA) - Stable identity, constitution, capabilities, permissions
2. **Layer 2: AgentPosture** (Tenant/Solution) - Behavioral tuning, LLM defaults, compliance mode
3. **Layer 3: AgentRuntimeContext** (Journey/Session) - Ephemeral, assembled at runtime, never stored
4. **Layer 4: Prompt Assembly** (Derived) - Assembled at runtime from layers 1-3

---

## Required Implementation Pattern

### 1. Import Required Models

```python
from ..agent_base import AgentBase
from ..models.agent_runtime_context import AgentRuntimeContext
from symphainy_platform.runtime.execution_context import ExecutionContext
```

### 2. Initialize with Proper Parameters

```python
def __init__(
    self,
    agent_id: str,
    public_works: Optional[Any] = None,
    **kwargs  # Important: Pass through for 4-layer model support
):
    super().__init__(
        agent_id=agent_id,
        agent_type="your_agent_type",
        capabilities=["capability1", "capability2"],
        public_works=public_works,
        **kwargs  # Pass through for agent_definition, agent_posture, etc.
    )
```

**Key Points:**
- Always pass `**kwargs` to parent to support 4-layer model parameters
- Pass `public_works` to parent (don't store separately unless needed)
- Don't override parent's initialization logic

### 3. Implement `_process_with_assembled_prompt()` (REQUIRED)

**This is the abstract method that MUST be implemented by all agents.**

```python
async def _process_with_assembled_prompt(
    self,
    system_message: str,
    user_message: str,
    runtime_context: AgentRuntimeContext,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Process request with assembled prompt (4-layer model).
    
    This method is called by AgentBase.process_request() after assembling
    the system and user messages from the 4-layer model.
    
    ARCHITECTURAL PRINCIPLE: Agents use the assembled prompts and runtime context
    to perform their work. The system_message includes business context from
    runtime_context, and user_message contains the user's actual request.
    
    Args:
        system_message: Assembled system message (from layers 1-3)
        user_message: Assembled user message (contains the user's request)
        runtime_context: Runtime context with business_context, journey_goal, etc.
        context: Execution context
    
    Returns:
        Dict with non-executing artifacts:
        {
            "artifact_type": "proposal" | "blueprint" | "ranked_options",
            "artifact": {...},
            "confidence": float
        }
    """
    # Step 1: Extract the actual request from user_message
    message = user_message.strip()
    
    # Step 2: Try to extract from runtime_context.business_context if available
    if hasattr(runtime_context, 'business_context') and runtime_context.business_context:
        if runtime_context.business_context.get("message"):
            message = runtime_context.business_context.get("message")
    
    # Step 3: If message looks like JSON, try to parse it
    if message.startswith("{") or message.startswith("["):
        try:
            import json
            parsed = json.loads(message)
            if isinstance(parsed, dict):
                message = parsed.get("message", parsed.get("text", message))
        except (json.JSONDecodeError, ValueError):
            pass  # Use message as-is
    
    # Step 4: Use runtime_context for business context, journey_goal, etc.
    business_context = runtime_context.business_context or {}
    journey_goal = runtime_context.journey_goal or ""
    human_preferences = runtime_context.human_preferences or {}
    
    # Step 5: Perform agent-specific logic
    # ... your agent's core logic here ...
    
    # Step 6: Return non-executing artifact
    return {
        "artifact_type": "proposal",  # or "blueprint", "ranked_options"
        "artifact": {
            # Your agent's response structure
        },
        "confidence": 0.8
    }
```

**Key Points:**
- Extract message from `user_message` (may be plain text or JSON)
- Use `runtime_context.business_context` for business context
- Use `runtime_context.journey_goal` for current goal
- Use `runtime_context.human_preferences` for user preferences
- Return proper artifact structure

### 4. Update `process_request()` (Optional but Recommended)

```python
async def process_request(
    self,
    request: Dict[str, Any],
    context: ExecutionContext,
    runtime_context: Optional[AgentRuntimeContext] = None
) -> Dict[str, Any]:
    """
    Process a request using agent capabilities.
    
    ARCHITECTURAL PRINCIPLE: This method delegates to AgentBase.process_request()
    which implements the 4-layer model. For backward compatibility, it can also
    be called directly, but the 4-layer flow is preferred.
    
    Args:
        request: Request dictionary
        context: Runtime execution context
        runtime_context: Optional pre-assembled runtime context (from orchestrator)
    
    Returns:
        Dict with non-executing artifacts
    """
    # If runtime_context is provided, use it; otherwise let AgentBase assemble it
    if runtime_context:
        # Use provided runtime context - assemble prompts and process
        system_message = self._assemble_system_message(runtime_context)
        user_message = self._assemble_user_message(request, runtime_context)
        return await self._process_with_assembled_prompt(
            system_message=system_message,
            user_message=user_message,
            runtime_context=runtime_context,
            context=context
        )
    else:
        # Delegate to parent's process_request which implements 4-layer model
        return await super().process_request(request, context, runtime_context=None)
```

**Key Points:**
- Accept optional `runtime_context` parameter (call site responsibility)
- If provided, use it directly (orchestrator assembled it)
- If not provided, delegate to parent (AgentBase will assemble it)

---

## Pattern Validation Checklist

For each agent, verify:

- [ ] Imports `AgentRuntimeContext` from models
- [ ] `__init__` passes `**kwargs` to parent
- [ ] `__init__` passes `public_works` to parent
- [ ] Implements `_process_with_assembled_prompt()` method
- [ ] `_process_with_assembled_prompt()` extracts message from `user_message`
- [ ] `_process_with_assembled_prompt()` uses `runtime_context.business_context`
- [ ] `_process_with_assembled_prompt()` uses `runtime_context.journey_goal`
- [ ] `_process_with_assembled_prompt()` returns proper artifact structure
- [ ] `process_request()` accepts optional `runtime_context` parameter
- [ ] `process_request()` delegates to parent if `runtime_context` not provided

---

## Example: GuideAgent Implementation

See `symphainy_platform/civic_systems/agentic/agents/guide_agent.py` for the complete reference implementation.

**Key Implementation Details:**
- Extracts message from `user_message` (handles JSON format)
- Uses `runtime_context.business_context` for business context
- Uses `runtime_context.journey_goal` for journey goal
- Maintains backward compatibility with existing `process_chat_message()` method
- Returns proper artifact structure with `artifact_type`, `artifact`, and `confidence`

---

## Migration Strategy

### For Existing Agents

1. **Add imports:**
   ```python
   from ..models.agent_runtime_context import AgentRuntimeContext
   ```

2. **Update `__init__`:**
   - Add `**kwargs` parameter
   - Pass `**kwargs` to `super().__init__()`

3. **Implement `_process_with_assembled_prompt()`:**
   - Extract message from `user_message`
   - Use `runtime_context` for business context
   - Call existing agent logic
   - Return proper artifact structure

4. **Update `process_request()` (optional):**
   - Add `runtime_context` parameter
   - Delegate to parent if not provided

### For New Agents

Follow the pattern from the start - implement `_process_with_assembled_prompt()` as the primary method.

---

## Common Patterns

### Pattern 1: Simple Message Processing

```python
async def _process_with_assembled_prompt(...):
    message = user_message.strip()
    # Process message
    result = await self._do_work(message, runtime_context, context)
    return {
        "artifact_type": "proposal",
        "artifact": result,
        "confidence": 0.8
    }
```

### Pattern 2: JSON Request Parsing

```python
async def _process_with_assembled_prompt(...):
    # Try to parse JSON
    try:
        import json
        request_data = json.loads(user_message)
        action = request_data.get("action")
        params = request_data.get("params", {})
    except (json.JSONDecodeError, ValueError):
        # Fallback to plain text
        action = "default"
        params = {"message": user_message}
    
    # Process based on action
    result = await self._handle_action(action, params, runtime_context, context)
    return result
```

### Pattern 3: Business Context Integration

```python
async def _process_with_assembled_prompt(...):
    # Use business context from runtime_context
    business_context = runtime_context.business_context or {}
    industry = business_context.get("industry")
    systems = business_context.get("systems", [])
    
    # Use journey goal
    journey_goal = runtime_context.journey_goal or ""
    
    # Process with context
    result = await self._process_with_context(
        message=user_message,
        industry=industry,
        systems=systems,
        journey_goal=journey_goal,
        context=context
    )
    return result
```

---

## Testing

After implementing the pattern:

1. **Unit Test:** Verify `_process_with_assembled_prompt()` is called correctly
2. **Integration Test:** Verify 4-layer model flow works end-to-end
3. **Runtime Test:** Verify agent starts without errors
4. **Functional Test:** Verify agent produces correct artifacts

---

## Status

✅ **Pattern Validated** - GuideAgent implementation serves as reference

**Next Steps:**
- Apply this pattern to all remaining agents
- Update orchestrators to assemble runtime context (call site responsibility)
- Ensure all agents use the 4-layer model consistently

---

**Last Updated:** January 24, 2026
