# Smart City Architecture Analysis

**Date:** January 2026  
**Question:** Should Smart City be a plane, a realm, something else, or both?  
**Question:** Should Smart City use agents, should agents use Smart City, or both?

---

## 🎯 Executive Summary

**Answer: Smart City is BOTH a Plane AND a special Realm, with bidirectional agent relationships.**

1. **Smart City as Plane:** Governance/Control Plane (observes Runtime, enforces policy)
2. **Smart City as Realm:** Platform Realm (special realm that's always present)
3. **Agents ↔ Smart City:** Bidirectional relationship with clear boundaries
   - **Smart City → Agents:** Use agents for policy reasoning (e.g., Security Guard reasoning about security policies)
   - **Agents → Smart City:** Use Smart City for governance checks (e.g., authorization before reasoning)

---

## 📊 Part 1: Smart City as Plane vs Realm

### The Confusion

**Plan v2 says:**
- "PHASE 4 — Smart City Plane"
- "Registers with Runtime"
- "Observes execution"
- "Enforces policy"
- "Does NOT execute domain logic"
- "Does NOT reason"
- "Does NOT own state"

**But some docs say:**
- "Smart City IS a realm"
- "Smart City provides critical business functionality"
- "Smart City services serve as data aggregation points"

### The Resolution: Smart City is BOTH

**Smart City as Plane (Governance/Control):**
- Observes Runtime execution
- Enforces policy
- Emits telemetry
- Registers with Runtime as observers
- Does NOT execute domain logic
- Does NOT own state

**Smart City as Realm (Platform Realm):**
- Special realm that's always present
- Provides platform infrastructure capabilities
- Has services (Security Guard, Traffic Cop, etc.)
- Registers capabilities with Curator
- Can have agents attached (like any realm)

**Key Insight:** Smart City is a **special realm** that also acts as a **governance plane**. It's the platform's "meta-realm" that governs other realms.

---

## 🏗️ Part 2: The 3-Plane Architecture (Clarified)

### Current Understanding

```
┌────────────────────────────────────────┐
│     Intent Plane (Agents)               │
│  "What should happen?"                 │
│  - Reason, plan, decompose             │
│  - Explain, justify                    │
└───────────────▲────────────────────────┘
                │ Plans / Graphs
┌───────────────┴────────────────────────┐
│     Runtime Plane                      │
│  "What happens next?"                  │
│  - Owns execution lifecycle            │
│  - Owns state transitions              │
│  - Owns safety states                  │
└───────────────▲────────────────────────┘
                │ Execution Events
┌───────────────┴────────────────────────┐
│     Capability Plane (Smart City + Realms)│
│  "What exists?"                         │
│  - Smart City (governance)              │
│  - Realms (domain capabilities)         │
└────────────────────────────────────────┘
```

### Smart City's Dual Role

**As Plane (Governance):**
- Observes Runtime execution (via observer pattern)
- Enforces policy (via policy hooks)
- Emits telemetry (via Nurse)

**As Realm (Platform Realm):**
- Provides platform infrastructure capabilities
- Has services (Security Guard, Traffic Cop, etc.)
- Registers capabilities with Curator
- Can have agents attached

---

## 🤝 Part 3: Smart City ↔ Agents Relationship

### The Question

**Should Smart City use agents?**
- Plan says: "Smart City Does NOT Reason"
- But some Smart City services might benefit from reasoning:
  - Security Guard: Reasoning about security policies
  - Librarian: Reasoning about knowledge organization
  - Data Steward: Reasoning about data governance

**Should agents use Smart City?**
- Agents need governance:
  - Authorization checks before reasoning
  - Policy validation
  - Telemetry emission

### The Answer: Bidirectional with Clear Boundaries

**Smart City → Agents (Policy Reasoning):**

**When Smart City Services Use Agents:**
- **Security Guard** uses an agent to reason about security policies
  - Input: Security policy, user context, action request
  - Agent reasons: "Is this action allowed under policy?"
  - Output: Authorization decision (reasoned artifact)
  - Smart City enforces: Uses agent's reasoned artifact to make decision

- **Librarian** uses an agent to reason about knowledge organization
  - Input: Content, metadata, existing knowledge graph
  - Agent reasons: "How should this be organized?"
  - Output: Organization recommendation (reasoned artifact)
  - Smart City enforces: Uses agent's reasoned artifact to organize

- **Data Steward** uses an agent to reason about data governance
  - Input: Data, governance policies, lifecycle rules
  - Agent reasons: "What governance actions are needed?"
  - Output: Governance recommendation (reasoned artifact)
  - Smart City enforces: Uses agent's reasoned artifact to govern

**Key Pattern:**
- Smart City services **use agents for reasoning**
- Agents return **reasoned artifacts**
- Smart City services **enforce** based on artifacts
- **Clear separation:** Reasoning (agents) vs Enforcement (Smart City)

**Agents → Smart City (Governance Checks):**

**When Agents Use Smart City:**
- **Before Reasoning:** Agent checks authorization with Security Guard
  - Agent calls: `security_guard.check_authorization(context)`
  - Security Guard returns: Authorization decision
  - Agent proceeds: Only if authorized

- **During Reasoning:** Agent validates policy with Data Steward
  - Agent calls: `data_steward.validate_policy(artifact, policy)`
  - Data Steward returns: Policy validation result
  - Agent adjusts: Reasoning based on policy constraints

- **After Reasoning:** Agent emits telemetry via Nurse
  - Agent calls: `nurse.emit_telemetry(event)`
  - Nurse records: Telemetry in observability system
  - Agent continues: Normal flow

**Key Pattern:**
- Agents **use Smart City for governance**
- Smart City provides **policy enforcement**
- Agents **comply** with governance
- **Clear separation:** Reasoning (agents) vs Governance (Smart City)

---

## 🎨 Part 4: Recommended Architecture

### Smart City Structure

```
symphainy_platform/
└── smart_city/
    ├── __init__.py
    ├── foundation_service.py          # Smart City Foundation (orchestrates services)
    ├── services/
    │   ├── security_guard/
    │   │   ├── security_guard_service.py
    │   │   └── agents/                # Agents attached to Security Guard
    │   │       └── security_policy_agent.py  # Reasons about security policies
    │   ├── traffic_cop/
    │   │   └── traffic_cop_service.py
    │   ├── post_office/
    │   │   └── post_office_service.py
    │   ├── conductor/
    │   │   └── conductor_service.py
    │   ├── librarian/
    │   │   ├── librarian_service.py
    │   │   └── agents/                # Agents attached to Librarian
    │   │       └── knowledge_organization_agent.py  # Reasons about knowledge
    │   ├── data_steward/
    │   │   ├── data_steward_service.py
    │   │   └── agents/                # Agents attached to Data Steward
    │   │       └── data_governance_agent.py  # Reasons about governance
    │   ├── nurse/
    │   │   └── nurse_service.py
    │   └── city_manager/
    │       └── city_manager_service.py
    └── protocols/
        └── smart_city_service_protocol.py
```

### Smart City Service Pattern (with Agent Support)

```python
# symphainy_platform/smart_city/services/security_guard/security_guard_service.py

from symphainy_platform.agentic import AgentFoundationService
from symphainy_platform.runtime.runtime_service import RuntimeService

class SecurityGuardService(SmartCityServiceProtocol):
    """
    Security Guard Service
    
    WHAT: I enforce security, zero-trust, multi-tenancy
    HOW: I observe Runtime execution and enforce security policies
    
    Uses agents for:
    - Policy reasoning (security_policy_agent)
    - Threat analysis (threat_analysis_agent)
    """
    
    def __init__(
        self,
        public_works_foundation: PublicWorksFoundationService,
        curator_foundation: CuratorFoundationService,
        runtime_service: RuntimeService,
        agent_foundation: AgentFoundationService  # For policy reasoning
    ):
        self.public_works = public_works_foundation
        self.curator = curator_foundation
        self.runtime = runtime_service
        self.agent_foundation = agent_foundation
        
        # Agents attached to Security Guard
        self.security_policy_agent = None  # Will be loaded from agent_foundation
    
    async def initialize(self) -> bool:
        """Initialize Security Guard and load agents."""
        # ... initialization ...
        
        # Load agents for policy reasoning
        self.security_policy_agent = self.agent_foundation.get_agent("security_policy_agent")
        
        return True
    
    async def check_authorization(
        self,
        user_id: str,
        action: str,
        resource: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check authorization using agent for policy reasoning.
        
        Pattern:
        1. Agent reasons about policy
        2. Security Guard enforces based on agent's reasoned artifact
        """
        # Use agent to reason about security policy
        if self.security_policy_agent:
            policy_reasoning = await self.security_policy_agent.reason(
                context={
                    "user_id": user_id,
                    "action": action,
                    "resource": resource,
                    "security_policies": await self._load_security_policies(),
                    "user_context": context
                }
            )
            
            # Extract reasoned artifact
            authorization_decision = policy_reasoning.get("artifacts", {}).get("authorization_decision")
            
            # Enforce based on agent's reasoning
            return {
                "authorized": authorization_decision.get("allowed", False),
                "reason": authorization_decision.get("reason", ""),
                "policy_applied": authorization_decision.get("policy", ""),
                "reasoning_trace": policy_reasoning.get("reasoning", "")
            }
        else:
            # Fallback to deterministic policy check
            return await self._deterministic_authorization_check(user_id, action, resource)
    
    async def observe_execution(self, execution_id: str, event: dict) -> None:
        """Observe Runtime execution and enforce security."""
        # Observe and enforce (no agent needed here - deterministic enforcement)
        pass
```

### Agent Pattern (with Smart City Governance)

```python
# Example: Realm agent that uses Smart City for governance

from symphainy_platform.agentic import GroundedReasoningAgentBase
from symphainy_platform.smart_city.services.security_guard.security_guard_service import SecurityGuardService

class ContentProcessingAgent(GroundedReasoningAgentBase):
    """
    Content Processing Agent
    
    Uses Smart City for:
    - Authorization checks (Security Guard)
    - Policy validation (Data Steward)
    - Telemetry emission (Nurse)
    """
    
    def __init__(
        self,
        agent_name: str,
        capabilities: List[str],
        runtime_service: RuntimeService,
        state_surface: StateSurface,
        security_guard: SecurityGuardService,  # For governance
        data_steward: DataStewardService,       # For policy validation
        nurse: NurseService                     # For telemetry
    ):
        super().__init__(agent_name, capabilities, runtime_service, state_surface)
        self.security_guard = security_guard
        self.data_steward = data_steward
        self.nurse = nurse
    
    async def reason(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Reason about content processing with governance checks.
        
        Pattern:
        1. Check authorization (Smart City)
        2. Gather facts (Runtime)
        3. Reason (Agent)
        4. Validate policy (Smart City)
        5. Emit telemetry (Smart City)
        """
        user_id = context.get("user_id")
        tenant_id = context.get("tenant_id")
        
        # 1. Check authorization (Smart City)
        auth_result = await self.security_guard.check_authorization(
            user_id=user_id,
            action="content_processing",
            resource="content",
            context=context
        )
        
        if not auth_result.get("authorized"):
            return {
                "reasoning": "Authorization denied",
                "artifacts": {},
                "error": "Unauthorized",
                "authorization_result": auth_result
            }
        
        # 2. Gather facts (Runtime)
        facts = await self.gather_facts(
            execution_id=context.get("execution_id"),
            session_id=context.get("session_id"),
            tenant_id=tenant_id
        )
        
        # 3. Reason (Agent)
        reasoning_context = {
            "input_context": context,
            "facts": facts,
            "authorization": auth_result
        }
        
        result = await self._do_reasoning(reasoning_context)
        
        # 4. Validate policy (Smart City)
        policy_validation = await self.data_steward.validate_policy(
            artifact=result.get("artifacts", {}),
            policy_type="content_processing",
            tenant_id=tenant_id
        )
        
        if not policy_validation.get("valid"):
            result["policy_validation"] = policy_validation
            result["artifacts"] = {}  # Clear artifacts if policy violation
        
        # 5. Emit telemetry (Smart City)
        await self.nurse.emit_telemetry({
            "event_type": "agent_reasoning_complete",
            "agent_name": self.agent_name,
            "execution_id": context.get("execution_id"),
            "reasoning_duration": result.get("metadata", {}).get("duration", 0)
        })
        
        return result
```

---

## 🎯 Part 5: Key Principles

### 1. Smart City is BOTH Plane and Realm

**As Plane:**
- Observes Runtime execution
- Enforces policy
- Emits telemetry
- Does NOT execute domain logic
- Does NOT own state

**As Realm:**
- Special platform realm (always present)
- Provides platform infrastructure capabilities
- Has services (Security Guard, Traffic Cop, etc.)
- Can have agents attached (like any realm)

### 2. Bidirectional Agent Relationship

**Smart City → Agents:**
- Smart City services **use agents for policy reasoning**
- Agents return **reasoned artifacts**
- Smart City services **enforce** based on artifacts
- **Clear separation:** Reasoning (agents) vs Enforcement (Smart City)

**Agents → Smart City:**
- Agents **use Smart City for governance**
- Smart City provides **policy enforcement**
- Agents **comply** with governance
- **Clear separation:** Reasoning (agents) vs Governance (Smart City)

### 3. Clear Boundaries

**What Smart City Does:**
- ✅ Observes execution
- ✅ Enforces policy
- ✅ Emits telemetry
- ✅ Uses agents for policy reasoning
- ❌ Does NOT execute domain logic
- ❌ Does NOT own state (except governance state)

**What Agents Do:**
- ✅ Reason about problems
- ✅ Return reasoned artifacts
- ✅ Use Smart City for governance
- ❌ Do NOT write to databases
- ❌ Do NOT emit events directly
- ❌ Do NOT orchestrate workflows

---

## 📋 Part 6: Implementation Recommendations

### Recommendation 1: Smart City as Special Realm + Governance Plane

**Structure:**
- Smart City is a **special realm** (platform realm)
- Smart City services **also act as governance plane** (observe Runtime)
- Smart City services can have **agents attached** (for policy reasoning)

### Recommendation 2: Bidirectional Agent Relationships

**Smart City Services Use Agents:**
- Security Guard → security_policy_agent (policy reasoning)
- Librarian → knowledge_organization_agent (knowledge reasoning)
- Data Steward → data_governance_agent (governance reasoning)

**Agents Use Smart City:**
- Agents → Security Guard (authorization checks)
- Agents → Data Steward (policy validation)
- Agents → Nurse (telemetry emission)

### Recommendation 3: Clear Separation of Concerns

**Reasoning (Agents):**
- "What should happen?" (policy reasoning)
- Returns reasoned artifacts
- No side effects

**Enforcement (Smart City):**
- "What is allowed?" (policy enforcement)
- Uses agent's reasoned artifacts
- Enforces based on artifacts

**Execution (Runtime):**
- "What happens next?" (execution control)
- Executes based on artifacts
- Owns state and lifecycle

---

## ✅ Conclusion

**Smart City is BOTH:**
1. **Plane:** Governance/Control Plane (observes Runtime, enforces policy)
2. **Realm:** Platform Realm (special realm that's always present)

**Agent Relationships are BIDIRECTIONAL:**
1. **Smart City → Agents:** Use agents for policy reasoning
2. **Agents → Smart City:** Use Smart City for governance checks

**Key Principle:**
> Smart City is the governor that uses agents for policy reasoning, while agents use Smart City for governance compliance.

This creates a **symbiotic relationship** with clear boundaries:
- Agents provide **reasoning expertise**
- Smart City provides **governance enforcement**
- Runtime provides **execution control**
