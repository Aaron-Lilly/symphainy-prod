# Phase 1 Contracts Validation Against Existing Patterns
**Date:** January 2026  
**Status:** 🔍 **VALIDATION IN PROGRESS**

---

## 🎯 Purpose

Validate Phase 1 contracts against:
1. Platform infrastructure and Public Works adapters (technical feasibility)
2. Public Works abstractions (alignment with platform thinking)
3. SOA APIs (Smart City and Realm patterns)

---

## 📋 Findings

### 1. Public Works Abstractions Pattern

**Existing Pattern:**
- Protocols in `foundations/public_works_foundation/abstraction_contracts/`
- Examples: `SessionProtocol`, `AuthenticationProtocol`, `WorkflowOrchestrationProtocol`
- Use `Protocol` from `typing` (not `@runtime_checkable`)
- Use dataclasses for request/response models
- Adapters implement protocols (e.g., `RedisSessionAdapter(SessionProtocol)`)

**Key Insight:**
- Public Works uses **Protocol** (not `@runtime_checkable Protocol`)
- Our contracts should align with this pattern OR explicitly document why we're using `@runtime_checkable`

**Action Required:**
- [ ] Review: Should we use `Protocol` (like Public Works) or `@runtime_checkable Protocol` (for runtime checks)?
- [ ] Decision: Use `Protocol` for consistency with Public Works, or use `@runtime_checkable` for runtime validation

---

### 2. Session Management Pattern

**Existing Pattern (Traffic Cop):**
```python
# Traffic Cop uses:
async def create_session(
    self,
    request: SessionRequest,  # Dataclass
    user_context: Optional[Dict[str, Any]] = None
) -> SessionResponse  # Dataclass

# SessionRequest dataclass:
@dataclass
class SessionRequest:
    session_id: str
    user_id: Optional[str] = None
    session_type: str = "web"
    context: Dict[str, Any] = None
    ttl_seconds: int = 3600

# SessionResponse dataclass:
@dataclass
class SessionResponse:
    success: bool
    session_id: str
    status: SessionStatus
    message: Optional[str] = None
    expires_at: Optional[str] = None
    error: Optional[str] = None
```

**Public Works SessionProtocol:**
```python
class SessionProtocol(Protocol):
    async def create_session(
        self,
        context: SessionContext,  # Dataclass
        session_data: Dict[str, Any]
    ) -> Session  # Dataclass
```

**Key Insight:**
- Traffic Cop wraps Public Works `SessionProtocol`
- Traffic Cop uses `SessionRequest`/`SessionResponse` dataclasses
- Public Works uses `SessionContext`/`Session` dataclasses
- Our Session Contract should align with Traffic Cop's interface (not Public Works directly)

**Action Required:**
- [ ] Update Session Contract to use `SessionRequest`/`SessionResponse` pattern (like Traffic Cop)
- [ ] Document that Session Surface coordinates with Traffic Cop (which uses Public Works)

---

### 3. Workflow Management Pattern

**Existing Pattern (Conductor):**
```python
# Conductor uses:
async def create_workflow(
    self,
    request: Dict[str, Any],  # Plain dict (not dataclass)
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]  # Plain dict

async def execute_workflow(
    self,
    request: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

async def get_workflow_status(
    self,
    request: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Public Works WorkflowOrchestrationProtocol:**
```python
class WorkflowOrchestrationProtocol(Protocol):
    async def create_workflow(
        self,
        workflow_definition: WorkflowDefinition  # Dataclass
    ) -> WorkflowExecution  # Dataclass
```

**Key Insight:**
- Conductor uses plain dicts (not dataclasses) for requests/responses
- Public Works uses dataclasses (`WorkflowDefinition`, `WorkflowExecution`)
- Our Workflow Contract should align with Conductor's interface (not Public Works directly)

**Action Required:**
- [ ] Update Workflow Contract to use plain dicts (like Conductor) OR document why we're using dataclasses
- [ ] Document that State Surface coordinates with Conductor (which uses Public Works)

---

### 4. SOA API Pattern

**Existing Pattern:**
```python
# Services define SOA APIs in soa_apis dictionary:
self.soa_apis = {
    "create_session": {
        "endpoint": "/api/traffic-cop/session",
        "method": "POST",
        "description": "Create session",
        "parameters": ["session_id", "user_id", "session_type", "context", "ttl_seconds"]
    },
    "get_session": {
        "endpoint": "/api/traffic-cop/session/{session_id}",
        "method": "GET",
        "description": "Get session",
        "parameters": ["session_id", "user_context"]
    }
}
```

**Key Insight:**
- SOA APIs are defined as dictionaries, not methods
- Methods are separate from SOA API definitions
- Our contracts should define method interfaces, not SOA API structures

**Action Required:**
- [ ] Contracts define method interfaces (correct)
- [ ] SOA API definitions are separate (handled by services)
- [ ] No changes needed

---

### 5. Infrastructure Adapters

**Available Adapters:**
- `redis_session_adapter.py` - Implements `SessionProtocol`
- `redis_state_adapter.py` - Implements state management
- `redis_graph_adapter.py` - Implements workflow orchestration
- `supabase_adapter.py` - Authentication/authorization
- `celery_adapter.py` - Task management
- `arangodb_adapter.py` - Data storage

**Key Insight:**
- Adapters implement Public Works protocols
- Services use adapters via abstractions
- Our contracts should align with what adapters can provide

**Action Required:**
- [ ] Verify contracts align with adapter capabilities
- [ ] Document which adapters support which contracts

---

## 🔧 Required Contract Updates

### 1. Session Contract

**Current (Phase 1 Plan):**
```python
async def create_session(
    self,
    user_context: Dict[str, Any]
) -> Dict[str, Any]
```

**Should Be (Aligned with Traffic Cop):**
```python
async def create_session(
    self,
    request: SessionRequest,
    user_context: Optional[Dict[str, Any]] = None
) -> SessionResponse
```

**Action:**
- [ ] Update Session Contract to use `SessionRequest`/`SessionResponse` dataclasses
- [ ] Import from `backend/smart_city/protocols/traffic_cop_service_protocol`

---

### 2. Workflow Contract

**Current (Phase 1 Plan):**
```python
async def create_workflow(
    self,
    workflow_definition: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]
```

**Should Be (Aligned with Conductor):**
```python
async def create_workflow(
    self,
    request: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Action:**
- [ ] Update Workflow Contract to match Conductor's signature
- [ ] Keep plain dicts (not dataclasses) for consistency

---

### 3. Protocol vs @runtime_checkable

**Decision Needed:**
- Option A: Use `Protocol` (like Public Works) - simpler, no runtime checks
- Option B: Use `@runtime_checkable Protocol` - enables `isinstance()` checks

**Recommendation:** Use `Protocol` for consistency with Public Works, add runtime checks in surfaces if needed.

**Action:**
- [ ] Decision: Use `Protocol` (not `@runtime_checkable`)
- [ ] Update all contracts to use `Protocol`

---

## 📝 Updated Contract Patterns

### Session Contract (Updated)

```python
from typing import Protocol, Optional
from dataclasses import dataclass
from backend.smart_city.protocols.traffic_cop_service_protocol import (
    SessionRequest,
    SessionResponse
)

class SessionContract(Protocol):
    """
    Session Contract - Aligned with Traffic Cop Service Protocol.
    
    Implemented by: Session Surface, Traffic Cop (Smart City)
    """
    
    async def create_session(
        self,
        request: SessionRequest,
        user_context: Optional[Dict[str, Any]] = None
    ) -> SessionResponse:
        """Create a new session."""
        ...
    
    async def get_session(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[SessionResponse]:
        """Get session by ID."""
        ...
    
    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> SessionResponse:
        """Update session metadata."""
        ...
    
    async def delete_session(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> SessionResponse:
        """Delete session."""
        ...
```

---

### Workflow Contract (Updated)

```python
from typing import Protocol, Dict, Any, Optional

class WorkflowContract(Protocol):
    """
    Workflow Contract - Aligned with Conductor Service Protocol.
    
    Implemented by: State Surface, Conductor (Smart City)
    """
    
    async def create_workflow(
        self,
        request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create workflow."""
        ...
    
    async def execute_workflow(
        self,
        request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute workflow."""
        ...
    
    async def get_workflow_status(
        self,
        request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get workflow status."""
        ...
```

---

## ✅ Validation Checklist

- [ ] Session Contract aligned with Traffic Cop pattern
- [ ] Workflow Contract aligned with Conductor pattern
- [ ] Protocol vs @runtime_checkable decision made
- [ ] All contracts use consistent patterns
- [ ] Contracts align with available adapters
- [ ] Contracts align with SOA API patterns
- [ ] Documentation updated with alignment decisions

---

## 🎯 Next Steps

1. **Update Phase 1 Implementation Plan** with validated contract patterns
2. **Document deviations** from existing patterns (if any)
3. **Create alignment matrix** showing contract → service → adapter mapping
4. **Review remaining contracts** (State, Execution, Intent, etc.) for alignment

---

**Last Updated:** January 2026  
**Status:** 🔍 **VALIDATION IN PROGRESS**
