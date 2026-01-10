# Runtime Plane Gaps Analysis
**Date:** January 2026  
**Status:** 🔍 **ANALYSIS & RECOMMENDATIONS**

---

## 🎯 The Questions

1. Do we need something to capture routing (since we removed Intent Contract)?
2. Are there any other gaps in the runtime plane compared to best practices?

---

## 📊 Current Runtime Plane Capabilities

### What We Have:

1. **Execution Control** (Execution Contract)
   - ✅ Execute plans
   - ✅ Suspend/resume/cancel execution
   - ✅ Get execution status

2. **State Management** (State Contract)
   - ✅ Get/set/delete state
   - ✅ List states by type
   - ✅ Coordinate with Traffic Cop, Conductor, Runtime

3. **Session Management** (Session Contract)
   - ✅ Create/get/update/delete sessions
   - ✅ Session lifecycle

4. **Workflow Management** (Workflow Contract)
   - ✅ Create/execute workflows
   - ✅ Get workflow status

5. **Capability Resolution** (CapabilityResolver)
   - ✅ Resolve capabilities from Smart City
   - ✅ Invoke capabilities via MCP
   - ✅ Discover capabilities

6. **Safety Control** (SafetyController)
   - ✅ Safety states (HALT, REVIEW, APPROVE)
   - ✅ Safety checks

7. **Transport Management** (TransportManager)
   - ✅ WebSocket management
   - ✅ Event emission

8. **State Store** (RuntimeStateStore)
   - ✅ Resumable state
   - ✅ State persistence

---

## 🔍 Routing Analysis

### Current Routing Mechanisms:

1. **Traffic Cop (API Gateway)**
   - Routes HTTP requests to services
   - Load balancing
   - Rate limiting
   - **This is HTTP routing, not execution routing**

2. **CapabilityResolver (Runtime Plane)**
   - Resolves capabilities from Smart City
   - Invokes capabilities via MCP
   - **This is capability resolution, not routing**

3. **Runtime Plane Execution**
   - Executes plans via agents
   - Agents already know what to do (from ExecutionPlan)
   - **No routing needed - agents are already selected**

### Do We Need a Routing Contract?

**Answer: No, but we might need a Capability Resolution Contract**

**Reasoning:**
- **Execution routing is handled by agents**: Agents generate ExecutionPlans that specify what to execute
- **Capability resolution is already handled**: CapabilityResolver resolves capabilities from Smart City
- **HTTP routing is handled by Traffic Cop**: Traffic Cop routes HTTP requests (not a runtime concern)

**However:**
- CapabilityResolver is not a contract - it's an implementation detail
- We might want to expose capability resolution as a contract for observability

---

## 🎯 Best Practices Gaps

### Industry Best Practices for Runtime Planes:

1. **Error Handling & Recovery**
   - ✅ Partial: SafetyController handles safety states
   - ❌ Missing: Retry logic, circuit breakers, error recovery strategies

2. **Timeout Management**
   - ❌ Missing: Execution timeouts, per-node timeouts, timeout policies

3. **Resource Management**
   - ❌ Missing: Rate limiting (different from Traffic Cop), throttling, resource quotas

4. **Observability**
   - ✅ Partial: TransportManager emits events
   - ❌ Missing: Metrics collection, distributed tracing, performance monitoring

5. **Priority & Queueing**
   - ❌ Missing: Execution priority, queue management, priority-based scheduling

6. **Health Checks**
   - ❌ Missing: Runtime health checks, agent health checks, capability health checks

7. **Graceful Degradation**
   - ❌ Missing: Fallback strategies, degraded mode operation

---

## 💡 Recommendations

### Option 1: Add Capability Resolution Contract (Recommended)

**Why:**
- CapabilityResolver is a key runtime function
- Should be observable and testable
- Provides clear interface for capability access

**Contract:**
```python
class CapabilityResolutionContract(Protocol):
    """Capability resolution for runtime execution."""
    
    async def resolve_capability(
        self,
        realm: str,
        capability_name: str
    ) -> Optional[Dict[str, Any]]:
        """Resolve capability from Smart City."""
        ...
    
    async def invoke_capability(
        self,
        realm: str,
        capability_name: str,
        inputs: Dict[str, Any],
        safety_level: str = "normal"
    ) -> Dict[str, Any]:
        """Invoke capability via MCP."""
        ...
    
    async def discover_capabilities(
        self,
        realm: Optional[str] = None
    ) -> Dict[str, Any]:
        """Discover available capabilities."""
        ...
```

**Pros:**
- Makes capability resolution observable
- Provides clear interface
- Enables testing and mocking

**Cons:**
- Adds one more contract
- Might be overkill if CapabilityResolver is simple

---

### Option 2: Add Execution Control Enhancements (Recommended)

**Add to Execution Contract:**

```python
class ExecutionContract(Protocol):
    # Existing methods...
    
    async def execute_with_timeout(
        self,
        execution_plan: ExecutionPlan,
        timeout_seconds: int
    ) -> Dict[str, Any]:
        """Execute with timeout."""
        ...
    
    async def execute_with_retry(
        self,
        execution_plan: ExecutionPlan,
        retry_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute with retry logic."""
        ...
    
    async def get_execution_metrics(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """Get execution metrics."""
        ...
```

**Pros:**
- Enhances existing contract
- Adds essential capabilities
- Aligns with best practices

**Cons:**
- Makes Execution Contract more complex

---

### Option 3: Add Observability Contract (Optional)

**If observability is important:**

```python
class ObservabilityContract(Protocol):
    """Observability for runtime execution."""
    
    async def emit_metric(
        self,
        metric_name: str,
        value: float,
        tags: Dict[str, str]
    ) -> bool:
        """Emit metric."""
        ...
    
    async def start_trace(
        self,
        trace_name: str,
        context: Dict[str, Any]
    ) -> str:
        """Start distributed trace."""
        ...
    
    async def log_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Log event."""
        ...
```

**Pros:**
- Comprehensive observability
- Industry standard

**Cons:**
- Might be handled by Nurse (Smart City)
- Could be overkill for Phase 1

---

## 🎯 Final Recommendation

### Phase 1: Keep It Simple (4 Contracts)

1. **Session Contract** - Session lifecycle
2. **State Contract** - State coordination
3. **Workflow Contract** - Workflow lifecycle
4. **Execution Contract** - Execution control

**Enhance Execution Contract with:**
- Timeout management
- Basic retry logic
- Execution metrics

**Don't add:**
- ❌ Routing Contract (not needed - agents handle routing)
- ❌ Capability Resolution Contract (implementation detail for now)
- ❌ Observability Contract (handled by Nurse/Smart City)

### Phase 2+: Add as Needed

- **Capability Resolution Contract** - If we need to expose capability resolution
- **Observability Contract** - If we need runtime-specific observability
- **Priority/Queueing Contract** - If we need priority-based execution

---

## ✅ Conclusion

**Routing:**
- ❌ No routing contract needed
- ✅ Agents handle execution routing (via ExecutionPlans)
- ✅ Traffic Cop handles HTTP routing (not runtime concern)
- ✅ CapabilityResolver handles capability resolution (implementation detail)

**Gaps:**
- ⚠️ Timeout management (add to Execution Contract)
- ⚠️ Retry logic (add to Execution Contract)
- ⚠️ Execution metrics (add to Execution Contract)
- ✅ Error handling (SafetyController covers this)
- ✅ Observability (TransportManager + Nurse cover this)

**Recommendation:**
- Keep 4 contracts (Session, State, Workflow, Execution)
- Enhance Execution Contract with timeout, retry, metrics
- Add other contracts in Phase 2+ as needed
