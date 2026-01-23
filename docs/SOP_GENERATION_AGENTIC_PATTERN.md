# SOP Generation via Interactive Chat - Agentic Pattern

**Date:** January 2026  
**Status:** 🔍 **ARCHITECTURAL GAP IDENTIFIED**

---

## Executive Summary

**CRITICAL ARCHITECTURAL VIOLATION**: Current `JourneyLiaisonAgent` violates the architectural principle:

> **"Liaison agents may explain, guide, and request — but never execute directly."**

**Current State**: `JourneyLiaisonAgent` does both conversation AND SOP generation (execution)

**Required State**: Separate liaison (conversation) from specialist agent (SOP generation reasoning)

---

## Architectural Principle

From `platform_architecture_MVP_context.md`:

> **Liaison agents may explain, guide, and request — but never execute directly.**
>
> All execution goes through:
> * Solution System
> * Civic Systems
> * Runtime

**This keeps chat from becoming a shadow control plane.**

---

## Current Implementation (WRONG)

### JourneyLiaisonAgent (Current - Violates Architecture)

**File**: `symphainy_platform/realms/journey/agents/journey_liaison_agent.py`

**What It Does**:
1. ✅ Handles conversation (`initiate_sop_chat`, `process_chat_message`)
2. ❌ **VIOLATES**: Does pattern matching to extract requirements (execution)
3. ❌ **VIOLATES**: Directly generates SOP structure (execution)
4. ❌ **VIOLATES**: No agentic reasoning - uses simple pattern matching

**Problems**:
- Liaison agent is executing (violates architecture)
- No LLM reasoning about requirements
- Simple pattern matching instead of understanding intent
- Direct SOP generation instead of delegating to specialist

---

## Required Implementation (CORRECT)

### Pattern: Liaison + Specialist Agent

**Two-Agent Pattern**:

1. **JourneyLiaisonAgent** (Conversation Handler)
   - Handles interactive chat
   - Explains, guides, requests
   - Gathers requirements through conversation
   - **DOES NOT EXECUTE** - delegates to specialist

2. **SOPGenerationAgent** (Specialist - Reasoning & Construction)
   - Reasons about requirements (LLM)
   - Understands user intent
   - Constructs SOP structure
   - Uses MCP tools to call services
   - **DOES NOT HANDLE CONVERSATION** - receives requirements from liaison

---

## Correct Architecture

### JourneyLiaisonAgent Responsibilities

**WHAT**: I handle interactive conversation for SOP generation  
**HOW**: I guide users, gather requirements, explain process

**Responsibilities**:
1. ✅ Initiate chat sessions
2. ✅ Process chat messages
3. ✅ Guide users through requirements gathering
4. ✅ Explain what information is needed
5. ✅ Request requirements from users
6. ❌ **DO NOT**: Execute pattern matching
7. ❌ **DO NOT**: Generate SOP structure
8. ✅ **DO**: Delegate to SOPGenerationAgent when ready

**Pattern**:
```
User Message
    ↓
JourneyLiaisonAgent (conversation)
    ↓ (gathers requirements)
    ↓ (when ready)
SOPGenerationAgent (reasoning)
    ↓ (uses MCP tools)
    ↓ (calls services)
SOP Generated
```

### SOPGenerationAgent Responsibilities

**WHAT**: I reason about SOP requirements and construct SOP documents  
**HOW**: I use LLM to understand requirements, reason about structure, use MCP tools

**Responsibilities**:
1. ✅ Reason about user requirements (LLM)
2. ✅ Understand intent and context
3. ✅ Design SOP structure
4. ✅ Use MCP tools to call services
5. ✅ Construct SOP document
6. ❌ **DO NOT**: Handle conversation
7. ❌ **DO NOT**: Interact directly with users

**Pattern**:
```
Requirements (from liaison)
    ↓
SOPGenerationAgent (reasoning)
    ↓ (LLM reasoning about requirements)
    ↓ (design SOP structure)
    ↓ (use MCP tool: journey_generate_sop)
    ↓ (WorkflowConversionService generates SOP)
    ↓
SOP Document
```

---

## Implementation Plan

### Phase 1: Create SOPGenerationAgent

**File**: `symphainy_platform/realms/journey/agents/sop_generation_agent.py`

**Agent Definition**:
```python
class SOPGenerationAgent(AgentBase):
    """
    SOP Generation Agent - Requirements reasoning and SOP construction.
    
    Uses agentic forward pattern:
    1. Reason about requirements (LLM)
    2. Understand intent and context
    3. Design SOP structure (LLM)
    4. Use MCP tools to call services
    5. Construct SOP document
    
    ARCHITECTURAL PRINCIPLE: Agent reasons, services execute.
    """
    
    async def generate_sop_from_requirements(
        self,
        requirements: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate SOP from requirements gathered through conversation.
        
        Args:
            requirements: Requirements dict (title, description, steps, etc.)
            conversation_history: Full conversation history
            context: Execution context
        
        Returns:
            Dict with generated SOP
        """
        # Step 1: Reason about requirements (LLM)
        reasoning = await self._reason_about_requirements(
            requirements, conversation_history
        )
        
        # Step 2: Design SOP structure (LLM)
        sop_structure = await self._design_sop_structure(
            reasoning, requirements
        )
        
        # Step 3: Use MCP tool to generate SOP
        sop_result = await self.use_tool(
            tool_name="journey_generate_sop",
            parameters={
                "sop_structure": sop_structure,
                "requirements": requirements
            },
            context=context
        )
        
        return {
            "artifact": sop_result,
            "reasoning": reasoning,
            "sop_structure": sop_structure
        }
```

### Phase 2: Refactor JourneyLiaisonAgent

**File**: `symphainy_platform/realms/journey/agents/journey_liaison_agent.py`

**Changes**:
1. Remove pattern matching logic
2. Remove direct SOP generation
3. Add LLM reasoning for conversation understanding
4. Delegate to SOPGenerationAgent when ready

**Updated Pattern**:
```python
async def process_chat_message(
    self,
    session_id: str,
    message: str,
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Process chat message - conversation only, no execution.
    """
    # Use LLM to understand user intent
    intent = await self._understand_intent(message, conversation_history)
    
    # Guide conversation based on intent
    response = await self._generate_guidance_response(intent, sop_structure)
    
    # If requirements are complete, delegate to SOPGenerationAgent
    if self._requirements_complete(sop_structure):
        # Delegate to specialist agent
        sop_result = await self.sop_generation_agent.generate_sop_from_requirements(
            requirements=sop_structure,
            conversation_history=conversation_history,
            context=context
        )
        return {
            "response": "SOP generated!",
            "sop": sop_result
        }
    
    return {
        "response": response,
        "sop_structure": sop_structure
    }
```

### Phase 3: Add MCP Tool

**File**: `symphainy_platform/realms/journey/mcp_server/journey_mcp_server.py`

**Add Tool**:
```python
@tool
async def journey_generate_sop(
    sop_structure: Dict[str, Any],
    requirements: Dict[str, Any],
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Generate SOP from structure and requirements.
    
    ARCHITECTURAL PRINCIPLE: MCP tool exposes orchestrator SOA API.
    """
    # Calls orchestrator._handle_generate_sop_from_structure()
    # Which calls WorkflowConversionService.generate_sop_from_structure()
    pass
```

### Phase 4: Add Orchestrator SOA API

**File**: `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`

**Add Handler**:
```python
async def _handle_generate_sop_from_structure(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle generate_sop_from_structure intent.
    
    Called by MCP tool when SOPGenerationAgent requests SOP generation.
    """
    sop_structure = intent.parameters.get("sop_structure")
    
    # Use service to generate SOP
    sop_result = await self.workflow_conversion_service.generate_sop_from_structure(
        sop_structure=sop_structure,
        tenant_id=context.tenant_id,
        context=context
    )
    
    return {
        "artifacts": {
            "sop": sop_result
        }
    }
```

---

## Agent Responsibilities Matrix

| Responsibility | JourneyLiaisonAgent | SOPGenerationAgent |
|---------------|-------------------|-------------------|
| Handle conversation | ✅ YES | ❌ NO |
| Guide users | ✅ YES | ❌ NO |
| Gather requirements | ✅ YES | ❌ NO |
| Reason about requirements | ❌ NO | ✅ YES |
| Understand intent | ✅ YES (conversation) | ✅ YES (requirements) |
| Design SOP structure | ❌ NO | ✅ YES |
| Generate SOP | ❌ NO | ✅ YES (via MCP) |
| Use MCP tools | ❌ NO | ✅ YES |
| Call services | ❌ NO | ✅ YES (via MCP) |

---

## Flow Diagram

### Current Flow (WRONG)
```
User Message
    ↓
JourneyLiaisonAgent
    ↓ (pattern matching - execution)
    ↓ (direct SOP generation - execution)
SOP Generated
```

### Required Flow (CORRECT)
```
User Message
    ↓
JourneyLiaisonAgent (conversation)
    ↓ (gathers requirements)
    ↓ (LLM reasoning about conversation)
    ↓ (when requirements complete)
SOPGenerationAgent (reasoning)
    ↓ (LLM reasoning about requirements)
    ↓ (design SOP structure)
    ↓ (use MCP tool: journey_generate_sop)
Journey Orchestrator
    ↓ (SOA API handler)
WorkflowConversionService
    ↓ (generate SOP)
SOP Generated
```

---

## Key Principles

### 1. Liaison Agents Don't Execute

**Rule**: Liaison agents explain, guide, and request — but never execute directly.

**Why**: Keeps chat from becoming a shadow control plane.

### 2. Specialist Agents Reason

**Rule**: Specialist agents reason about requirements and use MCP tools to execute.

**Why**: Separates reasoning from execution, maintains architectural boundaries.

### 3. MCP Tools Expose Orchestrator APIs

**Rule**: MCP tools call orchestrator SOA APIs, which call services.

**Why**: Maintains proper architectural layers (Agent → MCP → Orchestrator → Service).

---

## Migration Path

### Step 1: Create SOPGenerationAgent
- New agent file
- AgentDefinition
- Reasoning methods
- MCP tool usage

### Step 2: Refactor JourneyLiaisonAgent
- Remove execution logic
- Add LLM reasoning for conversation
- Delegate to SOPGenerationAgent
- Keep conversation handling

### Step 3: Add MCP Tool
- `journey_generate_sop` tool
- Exposes orchestrator SOA API

### Step 4: Add Orchestrator Handler
- `_handle_generate_sop_from_structure`
- Calls WorkflowConversionService

### Step 5: Update WorkflowConversionService
- `generate_sop_from_structure` method
- Takes structured requirements
- Generates SOP document

---

## Testing Strategy

### Unit Tests
1. JourneyLiaisonAgent conversation handling
2. SOPGenerationAgent reasoning logic
3. MCP tool integration

### Integration Tests
1. Liaison → Specialist delegation
2. Specialist → MCP → Orchestrator → Service flow
3. End-to-end chat → SOP generation

---

## Acceptance Criteria

1. ✅ JourneyLiaisonAgent handles conversation only (no execution)
2. ✅ SOPGenerationAgent reasons about requirements (LLM)
3. ✅ SOPGenerationAgent uses MCP tools (not direct service calls)
4. ✅ MCP tool exposes orchestrator SOA API
5. ✅ Orchestrator calls service (not agent)
6. ✅ Service generates SOP (pure data processing)
7. ✅ No architectural violations

---

## Estimated Effort

- **SOPGenerationAgent Creation**: 6-8 hours
- **JourneyLiaisonAgent Refactoring**: 4-6 hours
- **MCP Tool Addition**: 2-3 hours
- **Orchestrator Handler**: 2-3 hours
- **Service Method**: 2-3 hours
- **Testing**: 4-6 hours

**Total**: 20-29 hours

---

**Status:** Architectural gap identified, implementation plan ready
