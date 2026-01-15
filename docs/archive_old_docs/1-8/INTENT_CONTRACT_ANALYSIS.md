# Intent Contract Analysis
**Date:** January 2026  
**Status:** 🔍 **ANALYSIS & RECOMMENDATIONS**

---

## 🎯 The Question

Is the Intent Contract too simplified for what agents actually need to do?

---

## 📊 Current Intent Contract (From Plan)

```python
class IntentContract(Protocol):
    async def route_intent(intent: Intent) -> Dict[str, Any]
    async def propagate_intent(intent: Intent, target_realm: str) -> Dict[str, Any]
    async def resolve_intent(intent: Intent) -> Optional[Dict[str, Any]]
```

**What it does:**
- Routes intent to realms
- Propagates intent to specific realms
- Resolves intent to execution plan

**What it doesn't do:**
- ❌ Intent understanding (from natural language)
- ❌ Intent classification
- ❌ Intent tracking (across conversations)
- ❌ Intent disambiguation
- ❌ Multi-agent intent coordination

---

## 🔍 What Agents Actually Do

### 1. **Agent Config Files (YAML)**
Agents have rich configuration:
- `role`: Agent's role description
- `goal`: Agent's primary goal
- `backstory`: Agent's backstory
- `instructions`: Behavioral instructions
- `capabilities`: Agent capabilities
- `solution_config`: Solution context

**Example:**
```yaml
agent_name: InsightsLiaisonAgent
role: Insights Analysis Liaison and User Guide
goal: Provide conversational interface and user guidance for insights analysis operations
backstory: |
  You are a friendly and knowledgeable insights analysis liaison...
instructions:
  - Maintain conversation context to provide personalized guidance
  - Understand user intent for insights analysis operations
  - Guide users through insights workflows
```

### 2. **Grounded Reasoning**
Agents use grounded reasoning:
- Fact gathering from tools
- Fact extraction (structured facts)
- Reasoning with facts as constraints
- Validation (fact citations, hallucination detection)

**This is NOT captured by Intent Contract.**

### 3. **Intent Understanding (In Agents)**
Agents have methods like:
```python
async def _understand_user_intent(
    self,
    query: str,
    conversation_context: Dict[str, Any],
    user_context: UserContext
) -> Dict[str, Any]:
    """
    Returns:
        {
            "intent": "analyze" | "drill_down" | "visualize" | "query" | "general",
            "entities": {...},
            "confidence": float
        }
    """
```

**This is NOT captured by Intent Contract.**

### 4. **Execution Plan Generation**
Agents generate ExecutionPlans:
```python
async def generate_plan(
    self,
    goal: str,  # Agent goal or intent
    context: Optional[Dict[str, Any]] = None,
    constraints: Optional[Dict[str, Any]] = None
) -> ExecutionPlan:
```

**This is NOT captured by Intent Contract.**

### 5. **Agent Types (Current & Future)**
- **Chat Agents** (GuideCrossDomainAgent, InsightsLiaisonAgent)
  - Need: Intent understanding, conversation tracking, multi-turn reasoning
- **Grounded Reasoning Agents** (CoexistenceBlueprintSpecialist, RoadmapProposalSpecialist)
  - Need: Fact gathering, reasoning, validation
- **Solution Architect Agents** (Future)
  - Need: Strategic reasoning, solution design, architecture planning
- **City Manager Agents** (Future)
  - Need: Platform governance, lifecycle management, policy enforcement
- **Coding Agents** (Future)
  - Need: Code generation, refactoring, testing

**Current Intent Contract doesn't support these.**

---

## 🤔 Is "Intent" a Normal Concept for Agentic Platforms?

**Yes, but it's usually more sophisticated:**

### Industry Patterns:
1. **Dialogflow/Google**: Intent classification, entity extraction, context tracking
2. **Rasa**: Intent classification, entity extraction, conversation management
3. **LangChain**: Intent understanding, tool selection, plan generation
4. **AutoGPT**: Goal decomposition, intent tracking, plan execution

### What's Missing in Current Contract:
- ❌ **Intent Understanding**: Parse natural language → structured intent
- ❌ **Intent Classification**: Categorize intent (navigate, execute, query, etc.)
- ❌ **Intent Tracking**: Track intent across conversations
- ❌ **Intent Disambiguation**: Resolve ambiguous intents
- ❌ **Intent to Plan**: Convert intent to execution plan
- ❌ **Multi-Agent Intent Coordination**: Coordinate intents across agents

---

## 💡 The Problem

**Current Intent Contract is too simplistic:**
1. It's more like "routing" than "intent understanding"
2. It doesn't capture agent reasoning patterns
3. It doesn't support grounded reasoning
4. It doesn't support complex agent types

**What agents actually need:**
1. **Intent Understanding Contract** (NLP → structured intent)
2. **Intent Tracking Contract** (conversation context)
3. **Intent Resolution Contract** (disambiguation)
4. **Intent to Plan Contract** (intent → ExecutionPlan)

---

## 🎯 Recommendations

### Option 1: Remove Intent Contract (Simplest)
**If intent is handled by agents themselves:**
- Agents already understand intent (via `_understand_user_intent`)
- Agents already generate plans (via `generate_plan`)
- Intent Contract adds no value

**Pros:**
- Simpler architecture
- No unnecessary abstraction
- Agents handle intent directly

**Cons:**
- No centralized intent coordination
- No cross-agent intent tracking

### Option 2: Expand Intent Contract (More Robust)
**Make it a proper Intent Understanding Contract:**

```python
class IntentUnderstandingContract(Protocol):
    """Intent understanding and coordination."""
    
    async def understand_intent(
        self,
        query: str,
        conversation_context: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Understand user intent from natural language.
        
        Returns:
            {
                "intent": str,
                "entities": Dict,
                "confidence": float,
                "intent_type": "navigate" | "execute" | "query" | "general"
            }
        """
        ...
    
    async def track_intent(
        self,
        intent_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Track intent across conversations."""
        ...
    
    async def resolve_intent(
        self,
        intent: Dict[str, Any],
        agent_capabilities: List[str]
    ) -> Optional[ExecutionPlan]:
        """
        Resolve intent to execution plan.
        
        Uses agent capabilities to determine best agent.
        """
        ...
    
    async def coordinate_intent(
        self,
        intent: Dict[str, Any],
        agents: List[str]
    ) -> Dict[str, Any]:
        """Coordinate intent across multiple agents."""
        ...
```

**Pros:**
- Centralized intent understanding
- Cross-agent coordination
- Intent tracking

**Cons:**
- More complex
- May duplicate agent logic
- Agents already do this

### Option 3: Rename to Routing Contract (Most Accurate)
**If it's just routing:**

```python
class RoutingContract(Protocol):
    """Route requests to appropriate realms/capabilities."""
    
    async def route_request(
        self,
        request: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request to appropriate realm/capability."""
        ...
```

**Pros:**
- Accurate naming
- Simple and clear
- No false promises

**Cons:**
- Doesn't capture intent understanding
- May not be needed if agents handle routing

---

## 🎯 My Recommendation

**Option 1: Remove Intent Contract**

**Reasoning:**
1. **Agents already handle intent:**
   - Agents understand intent (via `_understand_user_intent`)
   - Agents generate plans (via `generate_plan`)
   - Agents track conversation context (via config `stateful: true`)

2. **Intent Contract doesn't add value:**
   - It's just routing, which agents already do
   - It doesn't capture grounded reasoning
   - It doesn't support complex agent types

3. **Grounded reasoning is separate:**
   - Grounded reasoning is in `GroundedReasoningAgentBase`
   - It's not about "intent" - it's about "reasoning with facts"

4. **Agent config files handle agent identity:**
   - YAML configs define agent role, goal, backstory
   - This is agent configuration, not "intent"

**What to keep:**
- ✅ **Session Contract** - Session lifecycle
- ✅ **State Contract** - State coordination
- ✅ **Workflow Contract** - Workflow lifecycle
- ✅ **Execution Contract** - Execution control
- ❌ **Intent Contract** - Remove (agents handle this)

---

## 📋 Updated Runtime Contracts (4 instead of 5)

1. **Session Contract** - Session lifecycle
2. **State Contract** - State coordination
3. **Workflow Contract** - Workflow lifecycle
4. **Execution Contract** - Execution control

**Intent is handled by:**
- Agents (intent understanding)
- AgentPlanner (intent → ExecutionPlan)
- GroundedReasoningAgentBase (reasoning with facts)
- Agent config files (agent identity/goals)

---

## ✅ Conclusion

**The Intent Contract is too simplified and doesn't capture what agents actually do.**

**Recommendation:** Remove it. Agents already handle intent understanding, planning, and reasoning. The Intent Contract adds no value and creates false expectations.

**Grounded reasoning and agent capabilities are handled by:**
- `GroundedReasoningAgentBase` (reasoning)
- `AgentPlanner` (planning)
- Agent config files (agent identity)
- Agent methods (intent understanding)

**This is sufficient for:**
- ✅ Chat agents
- ✅ Grounded reasoning agents
- ✅ Solution Architect agents (future)
- ✅ City Manager agents (future)
- ✅ Coding agents (future)
