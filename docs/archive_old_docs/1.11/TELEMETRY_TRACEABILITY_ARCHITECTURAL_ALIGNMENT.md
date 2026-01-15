# Telemetry & Traceability Architectural Alignment

**Date:** January 2026  
**Status:** 🔍 **COMPREHENSIVE ANALYSIS**  
**Purpose:** Ensure telemetry and traceability are properly embedded in platform DNA

---

## 🎯 Executive Summary

**Key Finding:** Telemetry infrastructure exists (OpenTelemetry, OTel Collector, Tempo), but **telemetry collection is incomplete** and **persistent storage is missing**. The platform needs:

1. ✅ **OpenTelemetry SDK integration** - For automatic instrumentation
2. ✅ **Nurse → OpenTelemetry** - Emit telemetry via OTLP
3. ✅ **ObservabilityAbstraction** - Store platform telemetry in ArangoDB
4. ✅ **State Surface separation** - Execution state ≠ Telemetry

**Current State:**
- ✅ Infrastructure ready (OTel Collector, Tempo, Grafana)
- ⚠️ Nurse collects telemetry but only logs it
- ❌ No OpenTelemetry SDK integration
- ❌ No ObservabilityAbstraction
- ❌ No ArangoDB telemetry storage

---

## 📊 Telemetry Flow Comparison

### Historical Pattern (Old Architecture)

```
Application Code
    │
    ├─→ OpenTelemetry SDK (automatic instrumentation)
    │   ├─→ Traces → OTel Collector → Tempo
    │   ├─→ Metrics → OTel Collector → Prometheus
    │   └─→ Logs → OTel Collector → Loki
    │
    └─→ ObservabilityAbstraction (explicit telemetry)
        └─→ ArangoDB Collections:
            ├─→ platform_logs
            ├─→ platform_metrics
            ├─→ platform_traces
            └─→ agent_executions
```

**Key Features:**
- ✅ OpenTelemetry SDK for automatic instrumentation
- ✅ OTel Collector for aggregation
- ✅ Tempo for distributed tracing
- ✅ ArangoDB for persistent platform telemetry storage
- ✅ ObservabilityAbstraction for business logic

### Current Pattern (New Architecture)

```
Runtime Service
    │
    └─→ Observer Pattern
        └─→ Nurse Service
            └─→ _collect_telemetry()
                └─→ logger.info()  ❌ Just logs, doesn't store!
```

**Missing:**
- ❌ No OpenTelemetry SDK integration
- ❌ No OTLP emission from Nurse
- ❌ No ObservabilityAbstraction
- ❌ No ArangoDB telemetry storage

---

## 🔍 Detailed Analysis

### 1. OpenTelemetry Integration

#### 1.1 Historical Pattern

**What Existed:**
- ✅ `TelemetryAdapter` - OpenTelemetry SDK initialization
- ✅ `LoggingInstrumentor().instrument()` - Automatic log-to-trace correlation
- ✅ `FastAPIInstrumentor.instrument_app(app)` - Automatic HTTP span creation
- ✅ OTLP exporter configured
- ✅ Environment variables: `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`

**Files:**
- `foundations/public_works_foundation/infrastructure_adapters/telemetry_adapter.py`
- `main.py` - OpenTelemetry initialization

#### 1.2 Current Pattern

**What We Have:**
- ✅ `docker-compose.yml` - OTel Collector, Tempo configured
- ✅ `otel-collector-config.yaml` - OTLP receiver configured
- ✅ Environment variables in `docker-compose.yml`: `OTEL_EXPORTER_OTLP_ENDPOINT`
- ❌ **No OpenTelemetry SDK initialization** in new architecture
- ❌ **No TelemetryAdapter** in Public Works
- ❌ **No automatic instrumentation**

#### 1.3 Best Practice (Aligned with Runtime Plane)

**Architecture:**
```
Application Startup:
├── Initialize OpenTelemetry SDK
│   ├── TracerProvider (for traces)
│   ├── MeterProvider (for metrics)
│   └── LoggerProvider (for logs)
├── Configure OTLP exporters
│   └── Endpoint: http://otel-collector:4317
└── Instrument application
    ├── LoggingInstrumentor (log-to-trace correlation)
    ├── FastAPIInstrumentor (HTTP spans)
    └── Custom instrumentation (Runtime events)

Runtime Execution:
├── Automatic spans created (via OpenTelemetry SDK)
├── Traces sent to OTel Collector (via OTLP)
└── Tempo stores traces (for distributed tracing)
```

**Key Principles:**
- ✅ **OpenTelemetry SDK = Automatic instrumentation** (spans, metrics, logs)
- ✅ **OTLP = Standard protocol** (OpenTelemetry Protocol)
- ✅ **OTel Collector = Aggregation** (receives, processes, exports)
- ✅ **Tempo = Distributed tracing** (trace storage and query)

**Required:**
1. ✅ Add `TelemetryAdapter` to Public Works (Layer 0)
2. ✅ Initialize OpenTelemetry SDK in `main.py`
3. ✅ Configure OTLP exporters
4. ✅ Add automatic instrumentation (LoggingInstrumentor, FastAPIInstrumentor)

---

### 2. Nurse Service Telemetry Collection

#### 2.1 Historical Pattern

**What Existed:**
- ✅ Nurse observes Runtime execution
- ✅ Nurse collects telemetry
- ✅ Nurse emits to ObservabilityAbstraction
- ✅ ObservabilityAbstraction stores in ArangoDB

#### 2.2 Current Pattern

**What We Have:**
```python
async def _collect_telemetry(self, execution_id: str, event: dict):
    """Collect telemetry data."""
    # Emit to telemetry abstraction (Public Works)
    # For now, just log
    self.logger.info(
        "Telemetry collected",
        metadata={
            "execution_id": execution_id,
            "event_type": event.get("event_type"),
            "timestamp": self.clock.now_iso()
        }
    )
```

**Issues:**
- ❌ Only logs telemetry (doesn't store)
- ❌ No OpenTelemetry SDK integration
- ❌ No ObservabilityAbstraction
- ❌ No ArangoDB storage

#### 2.3 Best Practice (Aligned with Runtime Plane)

**Architecture:**
```
Runtime Execution Event
    │
    └─→ Runtime._notify_observers()
        └─→ Nurse.observe_execution()
            ├─→ _collect_telemetry()
            │   ├─→ OpenTelemetry SDK (emit span/metric/log)
            │   │   └─→ OTLP → OTel Collector → Tempo
            │   └─→ ObservabilityAbstraction (store platform telemetry)
            │       └─→ ArangoDB Collections
            ├─→ _update_health_metrics()
            └─→ _manage_trace()
```

**Key Principles:**
- ✅ **Nurse = Telemetry collection point** (via observer pattern)
- ✅ **OpenTelemetry SDK = Automatic instrumentation** (spans, metrics)
- ✅ **ObservabilityAbstraction = Platform telemetry storage** (ArangoDB)
- ✅ **Dual path:** OTLP (for distributed tracing) + ArangoDB (for platform data)

**Required:**
1. ✅ Add OpenTelemetry SDK to Nurse
2. ✅ Emit telemetry via OTLP (to OTel Collector)
3. ✅ Add ObservabilityAbstraction to Public Works
4. ✅ Store platform telemetry in ArangoDB

---

### 3. ObservabilityAbstraction (Platform Telemetry Storage)

#### 3.1 Historical Pattern

**What Existed:**
- ✅ `ObservabilityAbstraction` - Business logic for telemetry storage
- ✅ ArangoDB collections:
  - `platform_logs` - Platform log entries
  - `platform_metrics` - Platform metrics
  - `platform_traces` - Platform trace correlation
  - `agent_executions` - Agent execution records
- ✅ Methods:
  - `record_platform_log()`
  - `record_platform_metric()`
  - `record_platform_trace()`
  - `record_agent_execution()`

**Storage Pattern:**
- All telemetry classified as `data_classification = "platform"`
- `tenant_id` optional (for attribution)
- Indexes on `trace_id`, `timestamp`, `service_name`

#### 3.2 Current Pattern

**What We Have:**
- ❌ **No ObservabilityAbstraction** in new architecture
- ❌ **No ArangoDB telemetry collections** initialized
- ❌ **No platform telemetry storage**

#### 3.3 Best Practice (Aligned with Runtime Plane)

**Architecture:**
```
ObservabilityAbstraction (Public Works Layer 1)
├── Uses ArangoDBAdapter (Layer 0)
├── Stores platform telemetry:
│   ├── platform_logs (platform log entries)
│   ├── platform_metrics (platform metrics)
│   ├── platform_traces (trace correlation)
│   └── agent_executions (agent execution records)
└── Business logic:
    ├── Data classification (platform vs client)
    ├── Tenant attribution (optional)
    ├── Indexing (trace_id, timestamp, service_name)
    └── Retention policies
```

**Key Principles:**
- ✅ **ObservabilityAbstraction = Platform telemetry storage** (ArangoDB)
- ✅ **OpenTelemetry = Distributed tracing** (Tempo)
- ✅ **Separation:** Platform data (ArangoDB) vs Distributed traces (Tempo)
- ✅ **State Surface ≠ Telemetry** (execution state vs observability data)

**Storage Strategy:**
```python
# Platform telemetry (ObservabilityAbstraction → ArangoDB)
{
    "data_classification": "platform",
    "tenant_id": "tenant_123",  # Optional (for attribution)
    "trace_id": "trace_abc",
    "service_name": "runtime",
    "event_type": "execution_started",
    "timestamp": "2026-01-01T00:00:00Z",
    "metadata": {...}
}

# Distributed traces (OpenTelemetry → Tempo)
{
    "trace_id": "trace_abc",
    "spans": [...],
    "attributes": {...}
}
```

**Required:**
1. ✅ Add `ObservabilityAbstraction` to Public Works
2. ✅ Initialize ArangoDB collections (platform_logs, platform_metrics, platform_traces, agent_executions)
3. ✅ Add indexes (trace_id, timestamp, service_name)
4. ✅ Wire Nurse → ObservabilityAbstraction

---

### 4. State Surface vs Telemetry

#### 4.1 Key Distinction

**State Surface:**
- ✅ Execution state (session_id, execution_id, saga_id, phase, status)
- ✅ Facts ("Field X maps to Policy Number with 0.93 confidence")
- ✅ References (GCS URIs, Supabase row IDs, ArangoDB document IDs)
- ✅ Lineage facts (file_id → parsed_file_id → embedding_id)
- ❌ **NOT telemetry** (observability data)

**Telemetry:**
- ✅ Observability data (logs, metrics, traces)
- ✅ Performance metrics (execution time, throughput)
- ✅ Error events (exceptions, failures)
- ✅ Agent execution records
- ❌ **NOT execution state** (that's State Surface)

#### 4.2 Storage Separation

```
Execution State (State Surface):
├── Redis (hot state) - Fast access, TTL-based
└── ArangoDB (durable state) - Persistent, queryable
    └── Collections: execution_state, facts, references, lineage

Telemetry (Observability):
├── OpenTelemetry SDK → OTLP → OTel Collector → Tempo
│   └── Distributed traces (for debugging)
└── ObservabilityAbstraction → ArangoDB
    └── Collections: platform_logs, platform_metrics, platform_traces, agent_executions
```

**Key Principles:**
- ✅ **State Surface = Execution truth** (what happened, what's true now)
- ✅ **Telemetry = Observability** (how it happened, performance, errors)
- ✅ **Clear separation** (different purposes, different storage)

---

## 5. ArangoDB Telemetry Collections

### 5.1 Collections Required

**From Old Architecture:**
```python
collections = {
    "platform_logs": {
        "type": "document",
        "description": "Stores platform log entries"
    },
    "platform_metrics": {
        "type": "document",
        "description": "Stores platform metrics"
    },
    "platform_traces": {
        "type": "document",
        "description": "Stores platform trace correlation data"
    },
    "agent_executions": {
        "type": "document",
        "description": "Stores agent execution records"
    }
}
```

**Indexes Required:**
```python
indexes = {
    "platform_logs": [
        {"fields": ["trace_id"]},
        {"fields": ["timestamp"]},
        {"fields": ["service_name"]},
        {"fields": ["data_classification", "tenant_id"]}
    ],
    "platform_metrics": [
        {"fields": ["trace_id"]},
        {"fields": ["timestamp"]},
        {"fields": ["metric_name"]},
        {"fields": ["data_classification", "tenant_id"]}
    ],
    "platform_traces": [
        {"fields": ["trace_id"]},
        {"fields": ["timestamp"]},
        {"fields": ["data_classification", "tenant_id"]}
    ],
    "agent_executions": [
        {"fields": ["agent_id"]},
        {"fields": ["trace_id"]},
        {"fields": ["timestamp"]},
        {"fields": ["data_classification", "tenant_id"]}
    ]
}
```

### 5.2 Schema Pattern

**Platform Telemetry Document:**
```python
{
    "_key": "log_abc123",
    "data_classification": "platform",
    "tenant_id": "tenant_123",  # Optional (for attribution)
    "trace_id": "trace_abc",
    "service_name": "runtime",
    "event_type": "execution_started",
    "timestamp": "2026-01-01T00:00:00Z",
    "log_level": "info",  # For platform_logs
    "message": "Execution started",
    "metadata": {
        "execution_id": "exec_123",
        "session_id": "session_456",
        "saga_id": "saga_789"
    }
}
```

---

## 6. Implementation Requirements

### 6.1 OpenTelemetry SDK Integration

**File:** `symphainy_platform/foundations/public_works/adapters/telemetry_adapter.py`

**Required:**
```python
class TelemetryAdapter:
    """
    OpenTelemetry SDK adapter.
    
    Initializes OpenTelemetry SDK and provides tracer/meter.
    """
    
    def __init__(self, service_name: str, endpoint: str = None):
        # Initialize TracerProvider
        # Initialize MeterProvider
        # Configure OTLP exporters
        # Get tracer and meter
```

**Integration:**
```python
# main.py
from symphainy_platform.foundations.public_works.adapters.telemetry_adapter import TelemetryAdapter

# Initialize OpenTelemetry
telemetry_adapter = TelemetryAdapter(
    service_name="symphainy-platform",
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
)

# Instrument application
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

LoggingInstrumentor().instrument()
FastAPIInstrumentor.instrument_app(app)
```

### 6.2 ObservabilityAbstraction

**File:** `symphainy_platform/foundations/public_works/abstractions/observability_abstraction.py`

**Required:**
```python
class ObservabilityAbstraction(ObservabilityProtocol):
    """
    Observability abstraction for platform telemetry storage.
    
    Stores platform telemetry in ArangoDB.
    """
    
    async def record_platform_log(...) -> Dict[str, Any]:
        """Record platform log entry."""
    
    async def record_platform_metric(...) -> Dict[str, Any]:
        """Record platform metric."""
    
    async def record_platform_trace(...) -> Dict[str, Any]:
        """Record platform trace correlation."""
    
    async def record_agent_execution(...) -> Dict[str, Any]:
        """Record agent execution."""
```

### 6.3 Nurse Service Enhancement

**File:** `symphainy_platform/smart_city/services/nurse/nurse_service.py`

**Required:**
```python
async def _collect_telemetry(self, execution_id: str, event: dict):
    """Collect telemetry data."""
    
    # 1. Emit to OpenTelemetry SDK (for distributed tracing)
    if self.telemetry_adapter:
        tracer = self.telemetry_adapter.get_tracer()
        with tracer.start_as_current_span("execution_event") as span:
            span.set_attribute("execution_id", execution_id)
            span.set_attribute("event_type", event.get("event_type"))
            # ... more attributes
    
    # 2. Store in ObservabilityAbstraction (for platform telemetry)
    if self.observability_abstraction:
        await self.observability_abstraction.record_platform_log(
            log_level="info",
            message=f"Execution event: {event.get('event_type')}",
            service_name="runtime",
            trace_id=span.context.trace_id if span else None,
            metadata={
                "execution_id": execution_id,
                "event": event
            }
        )
```

### 6.4 ArangoDB Collection Initialization

**File:** `scripts/initialize_arangodb_collections.py`

**Required:**
```python
# Add telemetry collections
collections = {
    # ... existing collections ...
    "platform_logs": {"type": "document"},
    "platform_metrics": {"type": "document"},
    "platform_traces": {"type": "document"},
    "agent_executions": {"type": "document"}
}

# Add indexes
indexes = {
    # ... existing indexes ...
    "platform_logs": [
        {"fields": ["trace_id"]},
        {"fields": ["timestamp"]},
        {"fields": ["service_name"]}
    ],
    # ... similar for other collections
}
```

---

## 7. Best Practices Summary

### 7.1 Telemetry Flow

```
Runtime Execution
    │
    ├─→ OpenTelemetry SDK (automatic)
    │   └─→ OTLP → OTel Collector → Tempo
    │       └─→ Distributed tracing (for debugging)
    │
    └─→ Nurse Service (observer)
        └─→ ObservabilityAbstraction
            └─→ ArangoDB
                └─→ Platform telemetry (for analysis)
```

### 7.2 Storage Responsibility

| Data Type | Storage | Purpose |
|-----------|---------|---------|
| **Execution state** | State Surface (Redis/ArangoDB) | What happened, what's true now |
| **Distributed traces** | Tempo (via OpenTelemetry) | How it happened (debugging) |
| **Platform telemetry** | ArangoDB (via ObservabilityAbstraction) | Observability data (analysis) |
| **Facts/references** | State Surface (Redis/ArangoDB) | Execution facts, lineage |
| **Lineage facts** | State Surface (Redis/ArangoDB) | File lineage, data flow |

### 7.3 Key Principles

1. ✅ **OpenTelemetry SDK = Automatic instrumentation** (spans, metrics, logs)
2. ✅ **OTLP = Standard protocol** (OpenTelemetry Protocol)
3. ✅ **OTel Collector = Aggregation** (receives, processes, exports)
4. ✅ **Tempo = Distributed tracing** (trace storage and query)
5. ✅ **ObservabilityAbstraction = Platform telemetry storage** (ArangoDB)
6. ✅ **State Surface ≠ Telemetry** (execution state vs observability)
7. ✅ **Nurse = Telemetry collection point** (via observer pattern)

---

## 8. Action Items

### 8.1 Immediate (Phase 0)

1. **OpenTelemetry SDK Integration:**
   - [ ] Add `TelemetryAdapter` to Public Works (Layer 0)
   - [ ] Initialize OpenTelemetry SDK in `main.py`
   - [ ] Configure OTLP exporters
   - [ ] Add automatic instrumentation (LoggingInstrumentor, FastAPIInstrumentor)

2. **ObservabilityAbstraction:**
   - [ ] Add `ObservabilityAbstraction` to Public Works (Layer 1)
   - [ ] Add `ObservabilityProtocol` (Layer 2)
   - [ ] Wire to ArangoDBAdapter
   - [ ] Add methods: `record_platform_log()`, `record_platform_metric()`, etc.

3. **ArangoDB Collections:**
   - [ ] Update `scripts/initialize_arangodb_collections.py`
   - [ ] Add collections: `platform_logs`, `platform_metrics`, `platform_traces`, `agent_executions`
   - [ ] Add indexes (trace_id, timestamp, service_name)
   - [ ] Run initialization script

4. **Nurse Service Enhancement:**
   - [ ] Add OpenTelemetry SDK integration
   - [ ] Emit telemetry via OTLP
   - [ ] Store telemetry via ObservabilityAbstraction
   - [ ] Test end-to-end telemetry flow

### 8.2 Short-term (Phase 1-2)

1. **Telemetry Correlation:**
   - [ ] Ensure trace_id propagation through all layers
   - [ ] Correlate OpenTelemetry traces with ArangoDB platform telemetry
   - [ ] Add trace_id to State Surface facts

2. **Performance Optimization:**
   - [ ] Batch telemetry writes (reduce ArangoDB load)
   - [ ] Add telemetry sampling (reduce volume)
   - [ ] Add retention policies (cleanup old telemetry)

### 8.3 Long-term (Phase 3+)

1. **Advanced Observability:**
   - [ ] Add custom metrics (execution time, throughput)
   - [ ] Add alerting (based on telemetry)
   - [ ] Add dashboards (Grafana integration)

---

## 9. Conclusion

**Key Takeaways:**
1. ✅ **OpenTelemetry is still the right answer** (industry standard)
2. ✅ **ArangoDB is still the right answer** (for persistent platform telemetry)
3. ⚠️ **Not properly embedded** (missing OpenTelemetry SDK, ObservabilityAbstraction)
4. ✅ **Runtime Plane and State Surface don't change this** (telemetry is separate from execution state)

**Next Steps:**
1. Add OpenTelemetry SDK integration
2. Add ObservabilityAbstraction
3. Initialize ArangoDB telemetry collections
4. Enhance Nurse Service
5. Test end-to-end telemetry flow

---

**Status:** Ready for implementation to embed telemetry in platform DNA.
