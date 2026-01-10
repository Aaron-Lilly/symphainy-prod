# Phase 1 Implementation Plan: Foundation
**Date:** January 2026  
**Status:** 📋 **READY TO START**  
**Duration:** Week 1  
**Goal:** Create contracts, runtime surfaces, and grounded reasoning base

---

## 🎯 Phase 1 Objectives

**Approach:** Build stable foundation first, iterate on rest case-by-case

1. ✅ Create **4 Runtime Plane contracts** (Session, State, Workflow, Execution) - **INDEPENDENT & STABLE**

**Note:** Intent Contract removed - agents handle intent understanding, planning, and reasoning directly. See `INTENT_CONTRACT_ANALYSIS.md` for details.
2. ✅ Create 4 runtime surfaces (coordination layers) - **DEPENDS ON RUNTIME CONTRACTS**
3. ✅ Create grounded reasoning agent base - **DEPENDS ON RUNTIME CONTRACTS**
4. ✅ Review base classes (already complete)

**Remaining Contracts:** Build case-by-case as needed (see `PHASE1_IMPLEMENTATION_PLAN_UPDATED.md` for full list):
- Security & Governance (6 contracts) - when security features are needed
- Data Mash (2 contracts) - when data mash features are needed
- Smart City (6 contracts) - when Smart City features are needed
- Realm (7 contracts) - when realm features are needed

**Why This Approach:**
- Runtime contracts are **independent** - they define the execution kernel interface
- Runtime contracts don't depend on other contracts - they're the foundation
- Runtime Plane Service initializes IDLE - no dependencies at startup
- Other contracts can be added incrementally based on actual needs
- Avoids over-engineering before understanding real requirements

**Success Criteria:**
- Runtime contracts are type-safe and enforced
- Runtime contracts are independent (no dependencies on other contracts)
- Runtime surfaces coordinate state properly
- Grounded reasoning base ensures deterministic reasoning
- No ad hoc state storage patterns
- All components follow end-state architecture

---

## 📋 Table of Contents

1. [Contracts Implementation](#1-contracts-implementation)
2. [Runtime Surfaces Implementation](#2-runtime-surfaces-implementation)
3. [Grounded Reasoning Base Implementation](#3-grounded-reasoning-base-implementation)
4. [Implementation Order](#4-implementation-order)
5. [Testing Strategy](#5-testing-strategy)
6. [Success Validation](#6-success-validation)

---

## 1. Contracts Implementation

### 1.1 Overview

**Purpose:** Immutable contracts that define interfaces for all platform components.

**Pattern:** Use `Protocol` from `typing` module (aligned with Public Works pattern).

**Location:** `contracts/` directory

**Key Principle:** Contracts = Protocols (no separate protocol layer)

**Refinement:** Contracts have been refined from 60+ to 16 based on:
- MVP showcase requirements
- Elimination of deprecated concepts
- Clear, distinct purpose for each contract (no duplication)
- 1:1 mapping between SOA APIs and MCP tools for agent access

**See:** `PHASE1_CONTRACTS_REFINED.md` for complete contract structure

---

### 1.2 Runtime Contracts

#### 1.2.1 Session Contract

**File:** `contracts/runtime/session.py`

**Purpose:** Define session lifecycle interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional
from datetime import datetime

@runtime_checkable
class SessionContract(Protocol):
    """
    Session Contract - Immutable interface for session management.
    
    Implemented by: Session Surface, Traffic Cop (Smart City)
    """
    
    async def create_session(
        self,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            user_context: User context (tenant_id, user_id, etc.)
        
        Returns:
            Session context with session_id, created_at, etc.
        """
        ...
    
    async def get_session(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session context or None if not found
        """
        ...
    
    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session metadata.
        
        Args:
            session_id: Session identifier
            updates: Dictionary of updates
        
        Returns:
            True if update successful
        """
        ...
    
    async def delete_session(
        self,
        session_id: str
    ) -> bool:
        """
        Delete session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if deletion successful
        """
        ...
```

**Dependencies:** None (foundation contract)

**Validation:** Runtime check via `isinstance(service, SessionContract)`

---

#### 1.2.2 State Contract

**File:** `contracts/runtime/state.py`

**Purpose:** Define state coordination interface

**Implementation:**

```python
from typing import Protocol, Dict, Any, Optional, List

class StateContract(Protocol):
    """
    State Contract - Immutable interface for state coordination.
    
    Implemented by: State Surface
    Coordinates with: Traffic Cop (session state), Conductor (workflow state), Runtime Plane (execution state)
    """
    
    async def get_state(
        self,
        state_key: str,
        state_type: str,  # "session", "workflow", "execution", "solution", "journey"
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get state by key and type.
        
        Args:
            state_key: State identifier (session_id, workflow_id, etc.)
            state_type: Type of state ("session", "workflow", "execution", etc.)
            context: Context for state retrieval
        
        Returns:
            State dictionary or None if not found
        """
        ...
    
    async def set_state(
        self,
        state_key: str,
        state_type: str,
        state_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Set state by key and type.
        
        Args:
            state_key: State identifier
            state_type: Type of state
            state_data: State data to store
            context: Context for state storage
        
        Returns:
            True if state set successfully
        """
        ...
    
    async def delete_state(
        self,
        state_key: str,
        state_type: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Delete state by key and type.
        
        Args:
            state_key: State identifier
            state_type: Type of state
            context: Context for state deletion
        
        Returns:
            True if deletion successful
        """
        ...
    
    async def list_states(
        self,
        state_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List states by type with optional filters.
        
        Args:
            state_type: Type of state
            filters: Optional filters (tenant_id, user_id, etc.)
        
        Returns:
            List of state dictionaries
        """
        ...
```

**Dependencies:** None (foundation contract)

**Validation:** Runtime check via `isinstance(service, StateContract)`

---

#### 1.2.3 Workflow Contract

**File:** `contracts/runtime/workflow.py`

**Purpose:** Define workflow lifecycle interface

**Implementation:**

```python
from typing import Protocol, Dict, Any, Optional

class WorkflowContract(Protocol):
    """
    Workflow Contract - Immutable interface for workflow management.
    
    Implemented by: State Surface (coordinates with Conductor)
    Pattern: Aligned with Conductor's plain dict pattern
    MCP Tools: Yes (agents need workflow access)
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

**Dependencies:** Conductor Service Protocol

**Validation:** Runtime check via `isinstance(service, WorkflowContract)`

**MCP Tools:** `workflow_create`, `workflow_execute`, `workflow_get_status`

---

#### 1.2.4 Execution Contract

**File:** `contracts/runtime/execution.py`

**Purpose:** Define execution control interface

**Implementation:**

```python
from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ExecutionState(Enum):
    """Execution state enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ExecutionPlan:
    """Execution plan structure."""
    realm: str
    capability: str
    context: Dict[str, Any]
    graph: Optional[Any] = None  # ExecutionGraph
    session_id: Optional[str] = None

class ExecutionContract(Protocol):
    """
    Execution Contract - Immutable interface for execution control.
    
    Implemented by: Execution Surface
    Pattern: Runtime Plane execution supervisor
    MCP Tools: No (internal to Runtime Plane)
    """
    
    async def execute(
        self,
        execution_plan: ExecutionPlan
    ) -> Dict[str, Any]:
        """
        Execute an execution plan.
        
        Args:
            execution_plan: Execution plan to execute
        
        Returns:
            Execution result
        """
        ...
    
    async def suspend_execution(
        self,
        execution_id: str
    ) -> bool:
        """
        Suspend execution.
        
        Args:
            execution_id: Execution identifier
        
        Returns:
            True if suspension successful
        """
        ...
    
    async def resume_execution(
        self,
        execution_id: str
    ) -> bool:
        """
        Resume execution.
        
        Args:
            execution_id: Execution identifier
        
        Returns:
            True if resumption successful
        """
        ...
    
    async def cancel_execution(
        self,
        execution_id: str
    ) -> bool:
        """
        Cancel execution.
        
        Args:
            execution_id: Execution identifier
        
        Returns:
            True if cancellation successful
        """
        ...
    
    async def get_execution_status(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """
        Get execution status.
        
        Args:
            execution_id: Execution identifier
        
        Returns:
            Execution status dictionary
        """
        ...
    
    async def execute_with_timeout(
        self,
        execution_plan: ExecutionPlan,
        timeout_seconds: int
    ) -> Dict[str, Any]:
        """
        Execute with timeout.
        
        Args:
            execution_plan: Execution plan to execute
            timeout_seconds: Timeout in seconds
        
        Returns:
            Execution result
        
        Raises:
            TimeoutError: If execution exceeds timeout
        """
        ...
    
    async def execute_with_retry(
        self,
        execution_plan: ExecutionPlan,
        retry_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute with retry logic.
        
        Args:
            execution_plan: Execution plan to execute
            retry_config: Optional retry configuration:
                - max_attempts: int (default: 3)
                - backoff_strategy: str (default: "exponential")
                - initial_delay: float (default: 1.0)
                - max_delay: float (default: 60.0)
        
        Returns:
            Execution result
        """
        ...
    
    async def get_execution_metrics(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """
        Get execution metrics.
        
        Args:
            execution_id: Execution identifier
        
        Returns:
            Metrics dictionary:
                - duration_seconds: float
                - nodes_executed: int
                - nodes_failed: int
                - retry_count: int
                - resource_usage: Dict[str, Any]
        """
        ...
```

**Dependencies:** None (foundation contract)

**Validation:** Runtime check via `isinstance(service, ExecutionContract)`

**Best Practices Coverage:**
- ✅ Timeout management (execute_with_timeout)
- ✅ Retry logic (execute_with_retry)
- ✅ Observability (get_execution_metrics)
- ✅ Error handling (via SafetyController)

---

#### 1.2.4 Intent Contract

**File:** `contracts/runtime/intent.py`

**Purpose:** Define intent propagation interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class Intent:
    """Intent structure."""
    intent_type: str  # "navigate", "execute", "query", etc.
    target_realm: Optional[str] = None
    target_capability: Optional[str] = None
    context: Dict[str, Any] = None
    user_context: Dict[str, Any] = None

class IntentContract(Protocol):
    """
    Intent Contract - Immutable interface for intent propagation.
    
    Implemented by: Intent Surface
    """
    
    async def route_intent(
        self,
        intent: Intent
    ) -> Dict[str, Any]:
        """
        Route intent to appropriate realm/capability.
        
        Args:
            intent: Intent to route
        
        Returns:
            Routing result
        """
        ...
    
    async def propagate_intent(
        self,
        intent: Intent,
        target_realm: str
    ) -> Dict[str, Any]:
        """
        Propagate intent to specific realm.
        
        Args:
            intent: Intent to propagate
            target_realm: Target realm name
        
        Returns:
            Propagation result
        """
        ...
    
    async def resolve_intent(
        self,
        intent: Intent
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve intent to execution plan.
        
        Args:
            intent: Intent to resolve
        
        Returns:
            Execution plan or None if cannot resolve
        """
        ...
```

**Dependencies:** None (foundation contract)

**Validation:** Runtime check via `isinstance(service, IntentContract)`

---

### 1.3 Smart City Contracts

#### 1.3.1 Security Contract

**File:** `contracts/smart_city/security.py`

**Purpose:** Define security interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional

@runtime_checkable
class SecurityContract(Protocol):
    """
    Security Contract - Immutable interface for security operations.
    
    Implemented by: Security Guard (Smart City)
    """
    
    async def authenticate(
        self,
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Authenticate user.
        
        Args:
            credentials: User credentials
        
        Returns:
            Authentication result with token, user_id, etc.
        """
        ...
    
    async def authorize(
        self,
        user_context: Dict[str, Any],
        resource: str,
        action: str
    ) -> bool:
        """
        Authorize user action.
        
        Args:
            user_context: User context
            resource: Resource identifier
            action: Action to authorize
        
        Returns:
            True if authorized
        """
        ...
    
    async def validate_token(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Validate authentication token.
        
        Args:
            token: Authentication token
        
        Returns:
            User context or None if invalid
        """
        ...
```

**Dependencies:** None (foundation contract)

---

#### 1.3.2 Data Contract

**File:** `contracts/smart_city/data.py`

**Purpose:** Define data management interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional, List

@runtime_checkable
class DataContract(Protocol):
    """
    Data Contract - Immutable interface for data management.
    
    Implemented by: Data Steward (Smart City)
    """
    
    async def store_data(
        self,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store data.
        
        Args:
            data: Data to store
            metadata: Data metadata
            context: Storage context
        
        Returns:
            Storage result with data_id, etc.
        """
        ...
    
    async def get_data(
        self,
        data_id: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get data by ID.
        
        Args:
            data_id: Data identifier
            context: Retrieval context
        
        Returns:
            Data dictionary or None if not found
        """
        ...
    
    async def query_data(
        self,
        query: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Query data.
        
        Args:
            query: Query parameters
            context: Query context
        
        Returns:
            List of matching data dictionaries
        """
        ...
```

**Dependencies:** None (foundation contract)

---

#### 1.3.3 Telemetry Contract

**File:** `contracts/smart_city/telemetry.py`

**Purpose:** Define telemetry interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional
from datetime import datetime

@runtime_checkable
class TelemetryContract(Protocol):
    """
    Telemetry Contract - Immutable interface for telemetry operations.
    
    Implemented by: Nurse (Smart City)
    """
    
    async def log_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Log telemetry event.
        
        Args:
            event_type: Event type
            event_data: Event data
            context: Event context
        
        Returns:
            True if logged successfully
        """
        ...
    
    async def get_metrics(
        self,
        metric_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get telemetry metrics.
        
        Args:
            metric_type: Metric type
            filters: Optional filters
        
        Returns:
            Metrics dictionary
        """
        ...
```

**Dependencies:** None (foundation contract)

---

#### 1.3.4 Workflow Contract

**File:** `contracts/smart_city/workflow.py`

**Purpose:** Define workflow management interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional, List

@runtime_checkable
class WorkflowContract(Protocol):
    """
    Workflow Contract - Immutable interface for workflow management.
    
    Implemented by: Conductor (Smart City)
    """
    
    async def create_workflow(
        self,
        workflow_definition: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create workflow.
        
        Args:
            workflow_definition: Workflow definition
            context: Creation context
        
        Returns:
            Workflow result with workflow_id, etc.
        """
        ...
    
    async def execute_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute workflow.
        
        Args:
            workflow_id: Workflow identifier
            context: Execution context
        
        Returns:
            Execution result
        """
        ...
    
    async def get_workflow_status(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        Get workflow status.
        
        Args:
            workflow_id: Workflow identifier
        
        Returns:
            Workflow status dictionary
        """
        ...
```

**Dependencies:** None (foundation contract)

---

#### 1.3.5 Events Contract

**File:** `contracts/smart_city/events.py`

**Purpose:** Define event management interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional, List, Callable

@runtime_checkable
class EventsContract(Protocol):
    """
    Events Contract - Immutable interface for event management.
    
    Implemented by: Post Office (Smart City)
    """
    
    async def publish_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Publish event.
        
        Args:
            event_type: Event type
            event_data: Event data
            context: Event context
        
        Returns:
            True if published successfully
        """
        ...
    
    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], None],
        context: Dict[str, Any]
    ) -> str:
        """
        Subscribe to events.
        
        Args:
            event_type: Event type to subscribe to
            handler: Event handler function
            context: Subscription context
        
        Returns:
            Subscription identifier
        """
        ...
    
    async def unsubscribe(
        self,
        subscription_id: str
    ) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            subscription_id: Subscription identifier
        
        Returns:
            True if unsubscribed successfully
        """
        ...
```

**Dependencies:** None (foundation contract)

---

### 1.4 Realm Contracts

#### 1.4.1 Content Contract

**File:** `contracts/realm/content.py`

**Purpose:** Define Content Realm interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional, List

@runtime_checkable
class ContentContract(Protocol):
    """
    Content Contract - Immutable interface for Content Realm.
    
    Implemented by: Content Realm services
    """
    
    async def upload_file(
        self,
        file_data: bytes,
        metadata: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Upload file.
        
        Args:
            file_data: File data
            metadata: File metadata
            context: Upload context
        
        Returns:
            Upload result with file_id, etc.
        """
        ...
    
    async def parse_file(
        self,
        file_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse file.
        
        Args:
            file_id: File identifier
            context: Parse context
        
        Returns:
            Parse result
        """
        ...
    
    async def get_semantic_interpretation(
        self,
        file_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get semantic interpretation of file.
        
        Args:
            file_id: File identifier
            context: Context
        
        Returns:
            Semantic interpretation result
        """
        ...
```

**Dependencies:** None (foundation contract)

---

#### 1.4.2 Insights Contract

**File:** `contracts/realm/insights.py`

**Purpose:** Define Insights Realm interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional, List

@runtime_checkable
class InsightsContract(Protocol):
    """
    Insights Contract - Immutable interface for Insights Realm.
    
    Implemented by: Insights Realm services
    """
    
    async def assess_quality(
        self,
        data_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess data quality.
        
        Args:
            data_id: Data identifier
            context: Assessment context
        
        Returns:
            Quality assessment result
        """
        ...
    
    async def analyze_data(
        self,
        data_id: str,
        analysis_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze data.
        
        Args:
            data_id: Data identifier
            analysis_type: Type of analysis
            context: Analysis context
        
        Returns:
            Analysis result
        """
        ...
    
    async def map_data(
        self,
        source_data_id: str,
        target_schema: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map data to target schema.
        
        Args:
            source_data_id: Source data identifier
            target_schema: Target schema
            context: Mapping context
        
        Returns:
            Mapping result
        """
        ...
```

**Dependencies:** None (foundation contract)

---

#### 1.4.3 Journey Contract

**File:** `contracts/realm/journey.py`

**Purpose:** Define Journey Realm interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional, List

@runtime_checkable
class JourneyContract(Protocol):
    """
    Journey Contract - Immutable interface for Journey Realm.
    
    Implemented by: Journey Realm services
    """
    
    async def generate_workflow(
        self,
        source: Dict[str, Any],  # SOP or chat
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate workflow from SOP or chat.
        
        Args:
            source: Source (SOP document or chat messages)
            context: Generation context
        
        Returns:
            Workflow generation result
        """
        ...
    
    async def generate_sop(
        self,
        source: Dict[str, Any],  # Workflow or chat
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate SOP from workflow or chat.
        
        Args:
            source: Source (workflow or chat messages)
            context: Generation context
        
        Returns:
            SOP generation result
        """
        ...
    
    async def analyze_coexistence(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze human+AI coexistence opportunities.
        
        Args:
            workflow_id: Workflow identifier
            context: Analysis context
        
        Returns:
            Coexistence analysis result
        """
        ...
    
    async def create_coexistence_blueprint(
        self,
        workflow_id: str,
        analysis_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create coexistence blueprint.
        
        Args:
            workflow_id: Workflow identifier
            analysis_result: Coexistence analysis result
            context: Creation context
        
        Returns:
            Blueprint creation result
        """
        ...
    
    async def create_platform_journey(
        self,
        blueprint_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create platform journey from blueprint.
        
        Args:
            blueprint_id: Blueprint identifier
            context: Creation context
        
        Returns:
            Journey creation result
        """
        ...
```

**Dependencies:** None (foundation contract)

---

#### 1.4.4 Solution Contract

**File:** `contracts/realm/solution.py`

**Purpose:** Define Solution Realm interface

**Implementation:**

```python
from typing import Protocol, runtime_checkable, Dict, Any, Optional, List

@runtime_checkable
class SolutionContract(Protocol):
    """
    Solution Contract - Immutable interface for Solution Realm.
    
    Implemented by: Solution Realm services
    """
    
    async def summarize_pillar_outputs(
        self,
        pillar_outputs: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Summarize outputs from all pillars.
        
        Args:
            pillar_outputs: Outputs from Content, Insights, Journey realms
            context: Summary context
        
        Returns:
            Summary result
        """
        ...
    
    async def generate_roadmap(
        self,
        summary: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate roadmap from pillar summary.
        
        Args:
            summary: Pillar summary
            context: Generation context
        
        Returns:
            Roadmap generation result
        """
        ...
    
    async def generate_poc_proposal(
        self,
        summary: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate POC proposal from pillar summary.
        
        Args:
            summary: Pillar summary
            context: Generation context
        
        Returns:
            POC proposal generation result
        """
        ...
    
    async def create_platform_solution(
        self,
        solution_source: Dict[str, Any],  # Roadmap or POC proposal
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create platform solution from roadmap or POC proposal.
        
        Args:
            solution_source: Roadmap or POC proposal
            context: Creation context
        
        Returns:
            Solution creation result
        """
        ...
```

**Dependencies:** None (foundation contract)

---

## 2. Runtime Surfaces Implementation

### 2.1 Overview

**Purpose:** Coordination layers within Runtime Plane that replace ad hoc state management.

**Key Principle:** Surfaces coordinate, they don't store state directly.

**Location:** `runtime/` directory

**Dependencies:** Contracts (from Section 1)

---

### 2.2 Session Surface

**File:** `runtime/session_surface.py`

**Purpose:** Coordinate session lifecycle

**Implementation Pattern:**

```python
from typing import Dict, Any, Optional
from contracts.runtime.session import SessionContract
from contracts.smart_city.security import SecurityContract

class SessionSurface:
    """
    Session Surface - Coordinates session lifecycle.
    
    Replaces: Ad hoc session creation in services
    Coordinates with: Traffic Cop (Smart City) for session state
    """
    
    def __init__(
        self,
        traffic_cop: Optional[SessionContract] = None,
        security_guard: Optional[SecurityContract] = None,
        logger: Optional[Any] = None
    ):
        self.traffic_cop = traffic_cop
        self.security_guard = security_guard
        self.logger = logger
    
    async def create_session(
        self,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create session via Traffic Cop.
        
        Args:
            user_context: User context
        
        Returns:
            Session context
        """
        if not self.traffic_cop:
            raise RuntimeError("Traffic Cop not available")
        
        # Validate user context via Security Guard
        if self.security_guard:
            token = user_context.get("token")
            if token:
                validated_context = await self.security_guard.validate_token(token)
                if not validated_context:
                    raise ValueError("Invalid token")
                user_context.update(validated_context)
        
        # Create session via Traffic Cop
        session = await self.traffic_cop.create_session(user_context)
        
        return session
    
    async def get_session(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get session via Traffic Cop.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session context or None
        """
        if not self.traffic_cop:
            raise RuntimeError("Traffic Cop not available")
        
        return await self.traffic_cop.get_session(session_id)
    
    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session via Traffic Cop.
        
        Args:
            session_id: Session identifier
            updates: Updates to apply
        
        Returns:
            True if update successful
        """
        if not self.traffic_cop:
            raise RuntimeError("Traffic Cop not available")
        
        return await self.traffic_cop.update_session(session_id, updates)
    
    async def delete_session(
        self,
        session_id: str
    ) -> bool:
        """
        Delete session via Traffic Cop.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if deletion successful
        """
        if not self.traffic_cop:
            raise RuntimeError("Traffic Cop not available")
        
        return await self.traffic_cop.delete_session(session_id)
```

**Dependencies:**
- `contracts/runtime/session.py` (SessionContract)
- `contracts/smart_city/security.py` (SecurityContract)

**Validation:** Implements `SessionContract` protocol

---

### 2.3 State Surface

**File:** `runtime/state_surface.py`

**Purpose:** Coordinate all state (single source of truth)

**Implementation Pattern:**

```python
from typing import Dict, Any, Optional, List
from contracts.runtime.state import StateContract
from contracts.smart_city.workflow import WorkflowContract

class StateSurface:
    """
    State Surface - Coordinates all state (single source of truth).
    
    Replaces: self.active_solutions = {}, self.conversation_history = []
    Coordinates with: Traffic Cop (session state), Conductor (workflow state), Runtime Plane (execution state)
    """
    
    def __init__(
        self,
        traffic_cop: Optional[Any] = None,  # SessionContract
        conductor: Optional[WorkflowContract] = None,
        runtime_plane: Optional[Any] = None,
        logger: Optional[Any] = None
    ):
        self.traffic_cop = traffic_cop
        self.conductor = conductor
        self.runtime_plane = runtime_plane
        self.logger = logger
    
    async def get_state(
        self,
        state_key: str,
        state_type: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get state by key and type.
        
        Routes to appropriate Smart City service based on state_type.
        """
        if state_type == "session":
            if not self.traffic_cop:
                raise RuntimeError("Traffic Cop not available")
            session = await self.traffic_cop.get_session(state_key)
            return session.get("metadata", {}) if session else None
        
        elif state_type == "workflow":
            if not self.conductor:
                raise RuntimeError("Conductor not available")
            workflow_status = await self.conductor.get_workflow_status(state_key)
            return workflow_status
        
        elif state_type == "execution":
            if not self.runtime_plane:
                raise RuntimeError("Runtime Plane not available")
            execution_status = await self.runtime_plane.get_execution_status(state_key)
            return execution_status
        
        else:
            raise ValueError(f"Unknown state type: {state_type}")
    
    async def set_state(
        self,
        state_key: str,
        state_type: str,
        state_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Set state by key and type.
        
        Routes to appropriate Smart City service based on state_type.
        """
        if state_type == "session":
            if not self.traffic_cop:
                raise RuntimeError("Traffic Cop not available")
            return await self.traffic_cop.update_session(
                state_key,
                {"metadata": state_data}
            )
        
        elif state_type == "workflow":
            # Workflow state is managed by Conductor
            # This is a coordination point, not direct storage
            if not self.conductor:
                raise RuntimeError("Conductor not available")
            # Workflow state is updated via workflow execution
            return True
        
        elif state_type == "execution":
            # Execution state is managed by Runtime Plane
            # This is a coordination point, not direct storage
            if not self.runtime_plane:
                raise RuntimeError("Runtime Plane not available")
            # Execution state is updated via execution lifecycle
            return True
        
        else:
            raise ValueError(f"Unknown state type: {state_type}")
    
    async def delete_state(
        self,
        state_key: str,
        state_type: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Delete state by key and type.
        """
        if state_type == "session":
            if not self.traffic_cop:
                raise RuntimeError("Traffic Cop not available")
            return await self.traffic_cop.delete_session(state_key)
        
        elif state_type == "workflow":
            # Workflow deletion handled by Conductor
            return True
        
        elif state_type == "execution":
            # Execution cancellation handled by Runtime Plane
            return True
        
        else:
            raise ValueError(f"Unknown state type: {state_type}")
    
    async def list_states(
        self,
        state_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List states by type with optional filters.
        """
        # Implementation depends on Smart City service capabilities
        # This is a coordination method, not direct query
        return []
```

**Dependencies:**
- `contracts/runtime/state.py` (StateContract)
- `contracts/smart_city/workflow.py` (WorkflowContract)

**Validation:** Implements `StateContract` protocol

---

### 2.4 Execution Surface

**File:** `runtime/execution_surface.py`

**Purpose:** Coordinate execution control

**Implementation Pattern:**

```python
from typing import Dict, Any, Optional
from contracts.runtime.execution import ExecutionContract, ExecutionPlan, ExecutionState
from runtime.session_surface import SessionSurface
from runtime.state_surface import StateSurface

class ExecutionSurface:
    """
    Execution Surface - Coordinates execution control.
    
    Replaces: Ad hoc execution control in agents/services
    Coordinates with: Runtime Plane (AgentRuntime, DataRuntime)
    """
    
    def __init__(
        self,
        runtime_plane: Optional[Any] = None,
        session_surface: Optional[SessionSurface] = None,
        state_surface: Optional[StateSurface] = None,
        logger: Optional[Any] = None
    ):
        self.runtime_plane = runtime_plane
        self.session_surface = session_surface
        self.state_surface = state_surface
        self.logger = logger
    
    async def execute(
        self,
        execution_plan: ExecutionPlan
    ) -> Dict[str, Any]:
        """
        Execute execution plan via Runtime Plane.
        """
        if not self.runtime_plane:
            raise RuntimeError("Runtime Plane not available")
        
        # Get or create session
        if not execution_plan.session_id:
            if not self.session_surface:
                raise RuntimeError("Session Surface not available")
            session = await self.session_surface.create_session(
                execution_plan.context.get("user_context", {})
            )
            execution_plan.session_id = session["session_id"]
        
        # Execute via Runtime Plane
        result = await self.runtime_plane.execute_plan(execution_plan)
        
        return result
    
    async def suspend_execution(
        self,
        execution_id: str
    ) -> bool:
        """
        Suspend execution.
        """
        if not self.runtime_plane:
            raise RuntimeError("Runtime Plane not available")
        
        return await self.runtime_plane.suspend_execution(execution_id)
    
    async def resume_execution(
        self,
        execution_id: str
    ) -> bool:
        """
        Resume execution.
        """
        if not self.runtime_plane:
            raise RuntimeError("Runtime Plane not available")
        
        return await self.runtime_plane.resume_execution(execution_id)
    
    async def cancel_execution(
        self,
        execution_id: str
    ) -> bool:
        """
        Cancel execution.
        """
        if not self.runtime_plane:
            raise RuntimeError("Runtime Plane not available")
        
        return await self.runtime_plane.cancel_execution(execution_id)
    
    async def get_execution_status(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """
        Get execution status.
        """
        if not self.runtime_plane:
            raise RuntimeError("Runtime Plane not available")
        
        return await self.runtime_plane.get_execution_status(execution_id)
```

**Dependencies:**
- `contracts/runtime/execution.py` (ExecutionContract, ExecutionPlan)
- `runtime/session_surface.py` (SessionSurface)
- `runtime/state_surface.py` (StateSurface)

**Validation:** Implements `ExecutionContract` protocol

---

### 2.5 Intent Surface

**File:** `runtime/intent_surface.py`

**Purpose:** Coordinate intent propagation

**Implementation Pattern:**

```python
from typing import Dict, Any, Optional
from contracts.runtime.intent import IntentContract, Intent
from contracts.runtime.execution import ExecutionPlan
from runtime.execution_surface import ExecutionSurface

class IntentSurface:
    """
    Intent Surface - Coordinates intent propagation.
    
    Replaces: Ad hoc intent handling in agents
    Coordinates with: Guide Agents, Liaison Agents
    """
    
    def __init__(
        self,
        execution_surface: Optional[ExecutionSurface] = None,
        logger: Optional[Any] = None
    ):
        self.execution_surface = execution_surface
        self.logger = logger
    
    async def route_intent(
        self,
        intent: Intent
    ) -> Dict[str, Any]:
        """
        Route intent to appropriate realm/capability.
        """
        # Resolve intent to execution plan
        execution_plan = await self.resolve_intent(intent)
        
        if not execution_plan:
            return {
                "success": False,
                "error": "Cannot resolve intent"
            }
        
        # Execute via Execution Surface
        if not self.execution_surface:
            raise RuntimeError("Execution Surface not available")
        
        result = await self.execution_surface.execute(execution_plan)
        
        return {
            "success": True,
            "result": result
        }
    
    async def propagate_intent(
        self,
        intent: Intent,
        target_realm: str
    ) -> Dict[str, Any]:
        """
        Propagate intent to specific realm.
        """
        intent.target_realm = target_realm
        return await self.route_intent(intent)
    
    async def resolve_intent(
        self,
        intent: Intent
    ) -> Optional[ExecutionPlan]:
        """
        Resolve intent to execution plan.
        """
        # Simple resolution: if target_realm and target_capability are specified, create plan
        if intent.target_realm and intent.target_capability:
            return ExecutionPlan(
                realm=intent.target_realm,
                capability=intent.target_capability,
                context=intent.context or {},
                session_id=None
            )
        
        # Otherwise, use Guide Agent to resolve intent
        # (This will be implemented when Guide Agent is available)
        return None
```

**Dependencies:**
- `contracts/runtime/intent.py` (IntentContract, Intent)
- `contracts/runtime/execution.py` (ExecutionPlan)
- `runtime/execution_surface.py` (ExecutionSurface)

**Validation:** Implements `IntentContract` protocol

---

## 3. Grounded Reasoning Base Implementation

### 3.1 Overview

**Purpose:** Base class for critical reasoning agents that ensures deterministic reasoning.

**Key Principle:** Same facts + same tools = same conclusions

**Location:** `foundations/agentic_foundation/agent_sdk/grounded_reasoning_agent_base.py`

**Dependencies:** 
- `foundations/agentic_foundation/agent_sdk/agent_base.py` (AgentBase)

---

### 3.2 Implementation

**File:** `foundations/agentic_foundation/agent_sdk/grounded_reasoning_agent_base.py`

**Implementation Pattern:**

```python
from typing import Dict, Any, List, Optional
from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase
import json

class GroundedReasoningAgentBase(AgentBase):
    """
    Grounded Reasoning Agent Base - Ensures deterministic reasoning.
    
    Key Principle: Same facts + same tools = same conclusions
    
    Flow:
    1. Gather facts via MCP tools
    2. Extract structured facts
    3. Reason with facts as constraints
    4. Validate reasoning against facts
    5. Return validated reasoning
    """
    
    async def generate_grounded_reasoning(
        self,
        goal: str,
        context: Dict[str, Any],
        required_tools: List[str]
    ) -> Dict[str, Any]:
        """
        Generate reasoning grounded in facts from tools.
        
        Args:
            goal: Reasoning goal
            context: Context for reasoning
            required_tools: List of tool names to gather facts from
        
        Returns:
            Validated reasoning result
        """
        # Step 1: Gather facts
        facts = await self._gather_facts(required_tools, context)
        
        # Step 2: Extract structured facts
        structured_facts = await self._extract_facts(facts)
        
        # Step 3: Reason with facts as constraints
        reasoning = await self._reason_with_facts(
            goal=goal,
            facts=structured_facts,
            context=context
        )
        
        # Step 4: Validate reasoning
        validated_reasoning = await self._validate_reasoning(
            reasoning=reasoning,
            facts=structured_facts
        )
        
        return validated_reasoning
    
    async def _gather_facts(
        self,
        required_tools: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gather all facts via MCP tools.
        
        Args:
            required_tools: List of tool names
            context: Context for tool execution
        
        Returns:
            Dictionary mapping tool names to tool results
        """
        facts = {}
        
        for tool_name in required_tools:
            try:
                tool_result = await self.tool_composition.execute_tool(
                    tool_name=tool_name,
                    parameters=context
                )
                facts[tool_name] = tool_result
            except Exception as e:
                self.logger.warning(f"Failed to execute tool {tool_name}: {e}")
                facts[tool_name] = {"error": str(e)}
        
        return facts
    
    async def _extract_facts(
        self,
        facts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured facts from tool outputs.
        
        Args:
            facts: Dictionary of tool results
        
        Returns:
            Structured facts with citations
        """
        extraction_prompt = f"""
        Extract structured facts from these tool outputs.
        Only extract information that is explicitly stated.
        Do not infer or add information.
        
        Tool Outputs:
        {json.dumps(facts, indent=2)}
        
        Return JSON with:
        {{
            "facts": [
                {{"id": "fact_1", "source": "tool_name", "fact": "explicit fact", "confidence": 1.0}}
            ],
            "uncertainties": [
                {{"source": "tool_name", "uncertainty": "what we don't know"}}
            ]
        }}
        """
        
        extraction_result = await self.llm_abstraction.generate_content(
            prompt=extraction_prompt,
            content_type="fact_extraction",
            response_format="json"
        )
        
        return json.loads(extraction_result)
    
    async def _reason_with_facts(
        self,
        goal: str,
        facts: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reason using only provided facts.
        
        Args:
            goal: Reasoning goal
            facts: Structured facts
            context: Reasoning context
        
        Returns:
            Reasoning result with fact citations
        """
        reasoning_prompt = f"""
        You are a critical reasoning agent. Your goal: {goal}
        
        CRITICAL CONSTRAINTS:
        1. You can ONLY use facts provided below
        2. You MUST cite the source fact for each conclusion
        3. You CANNOT add information not in the facts
        4. If you need more information, state what's missing
        
        Facts Available:
        {json.dumps(facts.get('facts', []), indent=2)}
        
        Uncertainties (what we don't know):
        {json.dumps(facts.get('uncertainties', []), indent=2)}
        
        Your Reasoning:
        1. Analyze the goal using ONLY the facts provided
        2. For each conclusion, cite the fact(s) that support it
        3. Identify any gaps in information
        4. Provide strategic recommendations based on facts
        
        Return JSON:
        {{
            "analysis": "your analysis",
            "conclusions": [
                {{"conclusion": "...", "supporting_facts": ["fact_id_1", "fact_id_2"]}}
            ],
            "gaps": ["what information is missing"],
            "recommendations": ["recommendations based on facts"]
        }}
        """
        
        reasoning_result = await self.llm_abstraction.generate_content(
            prompt=reasoning_prompt,
            content_type="critical_reasoning",
            response_format="json"
        )
        
        return json.loads(reasoning_result)
    
    async def _validate_reasoning(
        self,
        reasoning: Dict[str, Any],
        facts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate reasoning against facts.
        
        Args:
            reasoning: Reasoning result
            facts: Structured facts
        
        Returns:
            Validated reasoning
        
        Raises:
            ValidationError: If reasoning is invalid
        """
        # Check all conclusions have fact citations
        for conclusion in reasoning.get('conclusions', []):
            supporting_facts = conclusion.get('supporting_facts', [])
            if not supporting_facts:
                raise ValidationError(
                    f"Conclusion '{conclusion.get('conclusion', 'unknown')}' has no fact citations"
                )
            
            # Verify cited facts exist
            fact_ids = [f.get('id') for f in facts.get('facts', [])]
            for fact_id in supporting_facts:
                if fact_id not in fact_ids:
                    raise ValidationError(
                        f"Cited fact '{fact_id}' does not exist"
                    )
        
        # Check for hallucinations (info not in facts)
        reasoning_text = json.dumps(reasoning)
        facts_text = json.dumps(facts.get('facts', []))
        
        # Use LLM to check for hallucinations
        hallucination_check = await self.llm_abstraction.analyze_text(
            text=reasoning_text,
            analysis_type="hallucination_detection",
            reference_text=facts_text
        )
        
        if hallucination_check.get('has_hallucinations', False):
            raise ValidationError(
                f"Reasoning contains information not in facts: {hallucination_check.get('hallucinations', [])}"
            )
        
        return reasoning


class ValidationError(Exception):
    """Validation error for grounded reasoning."""
    pass
```

**Dependencies:**
- `foundations/agentic_foundation/agent_sdk/agent_base.py` (AgentBase)

**Validation:** 
- All critical reasoning agents inherit from this base
- All reasoning includes fact citations
- No hallucinations in reasoning

---

## 4. Implementation Order

### Week 1: Phase 1 Implementation

#### Day 1-2: Contracts (Foundation)
1. ✅ Create `contracts/` directory structure
2. ✅ Implement Runtime Contracts (5 contracts) - **Phase 1 Focus**
   - Session Contract
   - State Contract
   - Workflow Contract
   - Execution Contract
   - Intent Contract
3. ⏳ Smart City Contracts (6 contracts) - **Phase 2** (see PHASE1_CONTRACTS_REFINED.md)
4. ⏳ Realm Contracts (5 contracts) - **Phase 3** (see PHASE1_CONTRACTS_REFINED.md)
5. ✅ Add `__init__.py` files for imports

**Note:** Phase 1 focuses on Runtime Plane contracts only. Smart City and Realm contracts will be created in subsequent phases.

#### Day 3-4: Runtime Surfaces (Coordination)
1. ✅ Create `runtime/` directory structure
2. ✅ Implement Session Surface
3. ✅ Implement State Surface
4. ✅ Implement Execution Surface
5. ✅ Implement Intent Surface
6. ✅ Wire surfaces into Runtime Plane

#### Day 5: Grounded Reasoning Base
1. ✅ Create `grounded_reasoning_agent_base.py`
2. ✅ Implement fact gathering
3. ✅ Implement fact extraction
4. ✅ Implement reasoning with facts
5. ✅ Implement validation

#### Day 6-7: Integration & Testing
1. ✅ Wire contracts into existing services
2. ✅ Wire surfaces into Runtime Plane
3. ✅ Test contract enforcement
4. ✅ Test surface coordination
5. ✅ Validate no ad hoc state storage

---

## 5. Testing Strategy

### 5.1 Contract Testing

**Purpose:** Ensure contracts are enforced

**Tests:**
- Runtime check: `isinstance(service, Contract)`
- Type checking: `mypy` validation
- Protocol compliance: All methods implemented

**Location:** `tests/contracts/`

---

### 5.2 Surface Testing

**Purpose:** Ensure surfaces coordinate properly

**Tests:**
- Session Surface: Create, get, update, delete sessions
- State Surface: Get, set, delete state by type
- Execution Surface: Execute, suspend, resume, cancel
- Intent Surface: Route, propagate, resolve intents

**Location:** `tests/runtime/surfaces/`

---

### 5.3 Grounded Reasoning Testing

**Purpose:** Ensure deterministic reasoning

**Tests:**
- Same facts + same tools = same conclusions
- Fact citations required
- Hallucination detection works
- Validation catches errors

**Location:** `tests/foundations/agentic_foundation/`

---

## 6. Success Validation

### 6.1 Contracts Validation

- [ ] All 13 contracts created
- [ ] All contracts use `@runtime_checkable Protocol`
- [ ] All contracts are type-safe
- [ ] All contracts are enforced at runtime

---

### 6.2 Surfaces Validation

- [ ] All 4 surfaces created
- [ ] Surfaces coordinate with Smart City services
- [ ] No ad hoc state storage in services
- [ ] Surfaces implement contracts

---

### 6.3 Grounded Reasoning Validation

- [ ] Grounded reasoning base created
- [ ] Fact gathering works
- [ ] Fact extraction works
- [ ] Reasoning with facts works
- [ ] Validation catches errors

---

### 6.4 Architecture Validation

- [ ] No ad hoc state storage patterns
- [ ] All state coordinated via State Surface
- [ ] All sessions coordinated via Session Surface
- [ ] All execution coordinated via Execution Surface
- [ ] All intents coordinated via Intent Surface

---

## 7. Next Steps After Phase 1

1. **Phase 2:** Refactor Smart City services to use surfaces
2. **Phase 3:** Recreate Realms aligned to contracts
3. **Phase 4:** Create Experience Plane
4. **Phase 5:** Integration & Testing

---

**Last Updated:** January 2026  
**Status:** 📋 **READY TO START**
