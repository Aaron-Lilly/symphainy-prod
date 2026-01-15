# Phase 1 Checklist

**Phase:** Tech Stack Evolution  
**Duration:** Week 2-3  
**Status:** Track progress here

---

## Week 2: Infrastructure Migrations

### Day 1-2: Redis Graph → ArangoDB

#### ArangoDB Graph Adapter
- [ ] `arango_graph_adapter.py` created
- [ ] `create_node()` implemented (no stubs)
- [ ] `create_relationship()` implemented (no stubs)
- [ ] `execute_query()` implemented (no stubs)
- [ ] `find_path()` implemented (no stubs)
- [ ] `get_neighbors()` implemented (no stubs)
- [ ] Adapter tests written
- [ ] Adapter tests pass
- [ ] Tests would fail if adapter had stubs

#### Knowledge Discovery Abstraction
- [ ] Abstraction updated to use ArangoDB Graph
- [ ] Redis Graph calls replaced
- [ ] Protocol interface unchanged
- [ ] Abstraction tests updated
- [ ] Abstraction tests pass
- [ ] Librarian Service unchanged (validates pattern)

#### Public Works Foundation
- [ ] ArangoDB Graph Adapter registered
- [ ] Redis Graph Adapter removed
- [ ] Foundation tests pass

---

### Day 3-4: WAL Lists → Streams

#### Redis Adapter Enhancement
- [ ] `xadd()` implemented (no stubs)
- [ ] `xread()` implemented (no stubs)
- [ ] `xgroup_create()` implemented (no stubs)
- [ ] `xreadgroup()` implemented (no stubs)
- [ ] `xack()` implemented (no stubs)
- [ ] `xrange()` implemented (no stubs)
- [ ] Streams tests written
- [ ] Streams tests pass
- [ ] Existing Redis operations still work

#### WAL Refactor
- [ ] WAL updated to use Streams
- [ ] List operations replaced with Stream operations
- [ ] Partitioning strategy implemented (tenant + date)
- [ ] Consumer groups implemented
- [ ] WAL interface unchanged
- [ ] WAL tests updated
- [ ] WAL tests pass
- [ ] Runtime usage unchanged (validates pattern)

---

### Day 5: Celery Removal

#### Celery Audit
- [ ] All Celery usage found
- [ ] Usage documented
- [ ] Replacement identified (Runtime + Saga)
- [ ] Audit document created

#### Celery Removal
- [ ] Celery removed from `requirements.txt`
- [ ] Celery removed from `pyproject.toml`
- [ ] Celery removed from `docker-compose.yml` (if exists)
- [ ] Celery code removed
- [ ] Documentation updated
- [ ] Tests pass (no Celery dependencies)

---

## Week 3: Observability & Validation

### Day 1-2: Metrics Export

#### OTEL Collector
- [ ] OTEL Collector config updated
- [ ] Prometheus exporter added
- [ ] Metrics pipeline configured
- [ ] Traces pipeline still works
- [ ] Metrics visible in Prometheus

#### Prometheus (if needed)
- [ ] Prometheus added to docker-compose
- [ ] Scraping configured
- [ ] Grafana connected (if exists)
- [ ] Metrics visible

---

### Day 3-4: Pattern Validation

#### Public Works Validation
- [ ] All changes reviewed
- [ ] Business logic unchanged verified
- [ ] Protocol interfaces unchanged verified
- [ ] Only adapters changed verified
- [ ] Pattern validation documented
- [ ] ADR created

---

### Day 5: Integration Testing

#### Integration Tests
- [ ] ArangoDB Graph integration test
- [ ] WAL Streams integration test
- [ ] Metrics export integration test
- [ ] No Celery integration test
- [ ] All integration tests pass
- [ ] No stubs/cheats found

---

## Phase 1 Complete When

- [ ] Redis Graph → ArangoDB complete (adapter swap only)
- [ ] WAL using Streams (implementation change only)
- [ ] Celery removed
- [ ] Metrics exported
- [ ] Public Works pattern validated
- [ ] All tests pass (no cheats)
- [ ] Integration tests pass

**No code should have stubs, cheats, or placeholders.**
