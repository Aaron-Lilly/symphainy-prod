# Phase 1: Tech Stack Evolution - Execution Plan

**Duration:** Week 2-3  
**Status:** Ready to Execute (after Phase 0)  
**Dependencies:** Phase 0 complete

---

## Goal

Migrate infrastructure through Public Works adapter swaps. Validate Public Works pattern by showing that infrastructure changes are adapter swaps, not business logic changes.

**Success Criteria:**
- ✅ Redis Graph → ArangoDB complete (adapter swap)
- ✅ WAL using Streams (adapter enhancement)
- ✅ Celery removed (cleanup)
- ✅ Metrics exported (OTEL config)
- ✅ Public Works pattern validated
- ✅ All tests pass (no cheats)

---

## Week 2: Infrastructure Migrations

### Day 1-2: Redis Graph → ArangoDB Migration

#### Task 1.1: Create ArangoDB Graph Adapter

**Goal:** Create adapter for ArangoDB graph operations (replaces Redis Graph)

**Tasks:**
1. Create `foundations/public_works/adapters/arango_graph_adapter.py`
2. Implement graph operations:
   - `create_node()` - Create graph node
   - `create_relationship()` - Create graph relationship
   - `execute_query()` - Execute AQL graph query
   - `find_path()` - Find path between nodes
   - `get_neighbors()` - Get node neighbors
3. Use existing `arango_adapter.py` as reference for connection handling

**Files to Create:**
- `symphainy_platform/foundations/public_works/adapters/arango_graph_adapter.py`

**Adapter Interface:**
```python
class ArangoGraphAdapter:
    """ArangoDB Graph Adapter - Replaces Redis Graph."""
    
    async def create_node(
        self,
        graph_name: str,
        node_id: str,
        labels: List[str],
        properties: Dict[str, Any]
    ) -> bool:
        """Create graph node in ArangoDB."""
        # Real implementation using ArangoDB AQL
        # NO STUBS, NO CHEATS
    
    async def create_relationship(
        self,
        graph_name: str,
        from_node_id: str,
        to_node_id: str,
        relationship_type: str,
        properties: Dict[str, Any]
    ) -> bool:
        """Create graph relationship in ArangoDB."""
        # Real implementation using ArangoDB AQL
        # NO STUBS, NO CHEATS
    
    async def execute_query(
        self,
        graph_name: str,
        query: str,  # AQL query
        params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Execute AQL graph query."""
        # Real implementation using ArangoDB AQL
        # NO STUBS, NO CHEATS
```

**Tests to Write:**
- `tests/foundations/public_works/adapters/test_arango_graph_adapter.py`
  - Test create_node
  - Test create_relationship
  - Test execute_query
  - Test find_path
  - Test get_neighbors
  - **Tests must fail if adapter has stubs/cheats**

**Definition of Done:**
- ✅ ArangoDB Graph Adapter created
- ✅ All graph operations implemented (no stubs)
- ✅ Tests written and passing
- ✅ Tests would fail if adapter had stubs

---

#### Task 1.2: Update Knowledge Discovery Abstraction

**Goal:** Replace Redis Graph calls with ArangoDB Graph calls

**Tasks:**
1. Update `foundations/public_works/abstractions/knowledge_discovery_abstraction.py`
2. Replace Redis Graph adapter with ArangoDB Graph adapter
3. Update methods:
   - `search_redis_graph()` → `search_arango_graph()` (or keep name, swap implementation)
   - `get_redis_graph_neighbors()` → `get_arango_graph_neighbors()`
   - `find_redis_graph_path()` → `find_arango_graph_path()`
4. Keep protocol interface unchanged (swappability)

**Files to Modify:**
- `symphainy_platform/foundations/public_works/abstractions/knowledge_discovery_abstraction.py`

**Key Principle:**
- ✅ Business logic unchanged (Librarian Service)
- ✅ Protocol interface unchanged
- ✅ Only adapter swapped
- ❌ No business logic changes
- ❌ No protocol changes

**Tests to Write:**
- Update existing tests to use ArangoDB Graph
- Verify Librarian Service unchanged
- **Tests must fail if abstraction has stubs/cheats**

**Definition of Done:**
- ✅ Knowledge Discovery Abstraction updated
- ✅ Uses ArangoDB Graph Adapter
- ✅ Protocol interface unchanged
- ✅ Tests updated and passing
- ✅ Librarian Service unchanged (validates pattern)

---

#### Task 1.3: Update Public Works Foundation Service

**Goal:** Register ArangoDB Graph Adapter in foundation service

**Tasks:**
1. Update `foundations/public_works/foundation_service.py`
2. Initialize ArangoDB Graph Adapter
3. Pass to Knowledge Discovery Abstraction
4. Remove Redis Graph Adapter initialization

**Files to Modify:**
- `symphainy_platform/foundations/public_works/foundation_service.py`

**Definition of Done:**
- ✅ ArangoDB Graph Adapter registered
- ✅ Redis Graph Adapter removed
- ✅ Knowledge Discovery Abstraction uses ArangoDB Graph
- ✅ Tests pass

---

### Day 3-4: WAL Lists → Streams Refactor

#### Task 2.1: Enhance Redis Adapter for Streams

**Goal:** Add Redis Streams operations to Redis Adapter

**Tasks:**
1. Update `foundations/public_works/adapters/redis_adapter.py`
2. Add Streams operations:
   - `xadd()` - Add to stream
   - `xread()` - Read from stream
   - `xgroup_create()` - Create consumer group
   - `xreadgroup()` - Read from consumer group
   - `xack()` - Acknowledge message
   - `xrange()` - Get range of messages
3. Keep existing Redis operations (lists, sets, etc.)

**Files to Modify:**
- `symphainy_platform/foundations/public_works/adapters/redis_adapter.py`

**New Methods:**
```python
async def xadd(
    self,
    stream_name: str,
    fields: Dict[str, str],
    maxlen: Optional[int] = None
) -> str:
    """Add message to Redis stream."""
    # Real implementation using Redis Streams
    # NO STUBS, NO CHEATS

async def xread(
    self,
    streams: Dict[str, str],  # {stream_name: last_id}
    count: Optional[int] = None,
    block: Optional[int] = None
) -> Dict[str, List[Tuple[str, Dict[str, str]]]]:
    """Read from Redis streams."""
    # Real implementation using Redis Streams
    # NO STUBS, NO CHEATS

async def xgroup_create(
    self,
    stream_name: str,
    group_name: str,
    id: str = "0"
) -> bool:
    """Create consumer group for stream."""
    # Real implementation using Redis Streams
    # NO STUBS, NO CHEATS
```

**Tests to Write:**
- `tests/foundations/public_works/adapters/test_redis_adapter_streams.py`
  - Test xadd
  - Test xread
  - Test xgroup_create
  - Test xreadgroup
  - Test xack
  - **Tests must fail if adapter has stubs/cheats**

**Definition of Done:**
- ✅ Redis Adapter enhanced with Streams operations
- ✅ All Streams operations implemented (no stubs)
- ✅ Tests written and passing
- ✅ Existing Redis operations still work

---

#### Task 2.2: Refactor WAL to Use Streams

**Goal:** Replace Redis Lists with Redis Streams in WAL

**Tasks:**
1. Update `runtime/wal.py`
2. Replace list operations with stream operations:
   - `lpush()` → `xadd()`
   - `lrange()` → `xread()` or `xrange()`
   - `ltrim()` → Use `maxlen` in `xadd()`
3. Add consumer groups for replay
4. Add partitioning strategy (tenant + time)
5. Keep WAL interface unchanged

**Files to Modify:**
- `symphainy_platform/runtime/wal.py`

**Key Changes:**
```python
# OLD (Lists):
await self.redis_client.lpush(key, json.dumps(event.to_dict()))
await self.redis_client.ltrim(key, 0, 9999)

# NEW (Streams):
stream_name = f"wal:{tenant_id}:{date}"  # Partition by tenant + date
await self.redis_client.xadd(
    stream_name,
    event.to_dict(),
    maxlen=100000  # Keep last 100k events per partition
)
```

**Partitioning Strategy:**
- Partition by tenant_id + date (e.g., `wal:tenant_1:2026-01-15`)
- Enables scalability (millions of events)
- Enables efficient replay (by tenant + date range)

**Tests to Write:**
- Update existing WAL tests
- Test partitioning
- Test consumer groups
- Test replay
- **Tests must fail if WAL has stubs/cheats**

**Definition of Done:**
- ✅ WAL uses Redis Streams
- ✅ Partitioning implemented
- ✅ Consumer groups implemented
- ✅ WAL interface unchanged
- ✅ Tests updated and passing
- ✅ Runtime usage unchanged (validates pattern)

---

### Day 5: Celery Removal

#### Task 3.1: Audit Celery Usage

**Goal:** Find all Celery usage in codebase

**Tasks:**
1. Search codebase for Celery references
2. Document what Celery was used for
3. Identify replacement (Runtime + Saga Coordinator)
4. Create Celery audit document

**Files to Create:**
- `current_state/celery_audit.md`

**Definition of Done:**
- ✅ All Celery usage found
- ✅ Usage documented
- ✅ Replacement identified
- ✅ Audit document created

---

#### Task 3.2: Remove Celery

**Goal:** Remove Celery from codebase and dependencies

**Tasks:**
1. Remove Celery from `requirements.txt`
2. Remove Celery from `pyproject.toml`
3. Remove Celery from `docker-compose.yml` (if exists)
4. Remove Celery-related code
5. Update documentation

**Files to Modify:**
- `requirements.txt`
- `pyproject.toml`
- `docker-compose.yml` (if Celery service exists)
- Any files with Celery imports

**Definition of Done:**
- ✅ Celery removed from dependencies
- ✅ Celery removed from docker-compose
- ✅ Celery code removed
- ✅ Documentation updated
- ✅ Tests pass (no Celery dependencies)

---

## Week 3: Observability & Validation

### Day 1-2: Metrics Export

#### Task 4.1: Update OTEL Collector Config

**Goal:** Export metrics to Prometheus

**Tasks:**
1. Update `otel-collector-config.yaml`
2. Add Prometheus exporter
3. Export metrics (not just traces)
4. Keep traces to Tempo

**Files to Modify:**
- `otel-collector-config.yaml`

**Updated Config:**
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

exporters:
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true
  prometheus:
    endpoint: "0.0.0.0:8889"
  debug:
    verbosity: normal

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/tempo, debug]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus, debug]
```

**Definition of Done:**
- ✅ OTEL Collector config updated
- ✅ Metrics exported to Prometheus
- ✅ Traces still exported to Tempo
- ✅ Metrics visible in Prometheus

---

#### Task 4.2: Add Prometheus (if needed)

**Goal:** Add Prometheus for metrics collection

**Tasks:**
1. Add Prometheus to `docker-compose.yml`
2. Configure scraping
3. Connect to Grafana (if Grafana exists)
4. Test metrics collection

**Files to Modify:**
- `docker-compose.yml`

**Definition of Done:**
- ✅ Prometheus added to docker-compose
- ✅ Scraping configured
- ✅ Grafana connected (if exists)
- ✅ Metrics visible

---

### Day 3-4: Pattern Validation

#### Task 5.1: Validate Public Works Pattern

**Goal:** Verify that infrastructure changes were adapter swaps

**Tasks:**
1. Review all changes made in Phase 1
2. Verify:
   - Business logic unchanged (Librarian Service, etc.)
   - Protocol interfaces unchanged
   - Only adapters changed
3. Document pattern validation

**Files to Create:**
- `docs/architecture/decisions/ADR_001_public_works_pattern_validation.md`

**Validation Checklist:**
- [ ] Redis Graph → ArangoDB: Only adapter swapped, business logic unchanged
- [ ] WAL Lists → Streams: Only implementation changed, interface unchanged
- [ ] Celery removal: No business logic affected
- [ ] Metrics export: Infrastructure config only

**Definition of Done:**
- ✅ Pattern validation documented
- ✅ All changes verified as adapter swaps
- ✅ Business logic unchanged
- ✅ ADR created

---

### Day 5: Integration Testing

#### Task 6.1: End-to-End Integration Tests

**Goal:** Verify all Phase 1 changes work together

**Tasks:**
1. Create integration tests:
   - Test ArangoDB Graph operations
   - Test WAL with Streams
   - Test metrics export
   - Test no Celery dependencies
2. Run all tests
3. Verify no stubs/cheats

**Files to Create:**
- `tests/integration/phase_1/test_tech_stack_evolution.py`

**Test Scenarios:**
1. **ArangoDB Graph:**
   - Create node
   - Create relationship
   - Query graph
   - Verify Librarian Service works

2. **WAL Streams:**
   - Append event
   - Read events
   - Replay events
   - Verify partitioning

3. **Metrics:**
   - Verify metrics exported
   - Verify Prometheus scraping
   - Verify Grafana dashboards

4. **No Celery:**
   - Verify no Celery imports
   - Verify async work still works
   - Verify Runtime + Saga handle async

**Definition of Done:**
- ✅ Integration tests created
- ✅ All tests pass
- ✅ No stubs/cheats found
- ✅ All functionality works

---

## Phase 1 Checklist

Track progress with this checklist:

### Week 2: Infrastructure Migrations
- [ ] ArangoDB Graph Adapter created
- [ ] ArangoDB Graph Adapter tests pass
- [ ] Knowledge Discovery Abstraction updated
- [ ] Knowledge Discovery Abstraction tests pass
- [ ] Public Works Foundation Service updated
- [ ] Redis Adapter enhanced with Streams
- [ ] Redis Adapter Streams tests pass
- [ ] WAL refactored to use Streams
- [ ] WAL partitioning implemented
- [ ] WAL tests pass
- [ ] Celery usage audited
- [ ] Celery removed

### Week 3: Observability & Validation
- [ ] OTEL Collector config updated
- [ ] Prometheus added (if needed)
- [ ] Metrics exported
- [ ] Public Works pattern validated
- [ ] ADR created
- [ ] Integration tests created
- [ ] All tests pass
- [ ] No stubs/cheats found

---

## Success Criteria

**Phase 1 is complete when:**
- ✅ Redis Graph → ArangoDB complete (adapter swap only)
- ✅ WAL using Streams (implementation change only)
- ✅ Celery removed
- ✅ Metrics exported
- ✅ Public Works pattern validated (business logic unchanged)
- ✅ All tests pass (no cheats)
- ✅ Integration tests pass

**No code should have stubs, cheats, or placeholders.**

---

## Next Steps

After Phase 1, proceed to [Phase 2: Architecture Enhancements](phase_2_execution_plan.md).

---

## References

- [Architecture Guide](../architecture/north_star.md)
- [Platform Rules](../PLATFORM_RULES.md)
- [Roadmap](../roadmap/00_ROADMAP_INDEX.md)
- [Phase 0 Execution Plan](phase_0_execution_plan.md)
