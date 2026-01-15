# Phase 0: Foundation & Assessment - Execution Plan

**Duration:** Week 1  
**Status:** Ready to Execute  
**Dependencies:** None

---

## Goal

Establish baseline, archive current implementations, audit Public Works, and create execution plans for subsequent phases.

**Success Criteria:**
- ✅ Archive structure created
- ✅ Public Works inventory complete
- ✅ Tech stack gaps documented
- ✅ Execution plans ready
- ✅ Baseline established

---

## Day 1: Archive Current Implementations

### Task 1.1: Create Archive Structure

**Goal:** Archive current implementations for reference (not reuse)

**Tasks:**
1. Create `archive_v1/` directory structure
2. Archive Runtime, Smart City, Realms, Experience, Agentic
3. Archive `main.py`
4. Create archive README documenting what was archived and why

**Files to Create:**
```
archive_v1/
├── README.md                    # What was archived and why
├── runtime_v1/                  # Current Runtime implementation
├── smart_city_v1/               # Current Smart City implementation
├── realms_v1/                   # Current Realms implementation
├── experience_v1/               # Current Experience implementation
├── agentic_v1/                  # Current Agentic implementation
└── main_v1.py                   # Current main.py
```

**Files to Archive:**
- `symphainy_platform/runtime/` → `archive_v1/runtime_v1/`
- `symphainy_platform/smart_city/` → `archive_v1/smart_city_v1/`
- `symphainy_platform/realms/` → `archive_v1/realms_v1/`
- `symphainy_platform/experience/` → `archive_v1/experience_v1/`
- `symphainy_platform/agentic/` → `archive_v1/agentic_v1/`
- `main.py` → `archive_v1/main_v1.py` (copy, don't move yet)

**Archive README Template:**
```markdown
# Archive v1 - Previous Implementation

**Date Archived:** [Date]
**Reason:** Platform rebuild following new architecture guide

## What Was Archived

- Runtime: Previous Runtime implementation (needs rebuild per new architecture)
- Smart City: Previous Smart City implementation (needs rebuild SDK-first)
- Realms: Previous Realms implementation (needs Runtime Participation Contract)
- Experience: Previous Experience implementation (needs rebuild as separate service)
- Agentic: Previous Agentic implementation (needs rebuild per new architecture)
- main.py: Previous main.py (465 lines, needs clean rebuild)

## Why Archived

These implementations don't follow the new architecture guide:
- Runtime doesn't have Intent Model, Execution Context, Execution Lifecycle Manager
- Smart City isn't SDK-first
- Realms don't use Runtime Participation Contract
- Experience isn't a separate service
- main.py is too complex (465 lines)

## Reference Only

This archive is for **reference only**, not for reuse.
New implementations will be built following the architecture guide.
```

**Definition of Done:**
- ✅ Archive structure created
- ✅ All implementations archived
- ✅ Archive README created
- ✅ Original directories removed (archived)

---

### Task 1.2: Create Clean Structure

**Goal:** Create clean directories for rebuild

**Tasks:**
1. Create new `runtime/` directory (empty, ready for rebuild)
2. Create new `civic_systems/` directory
3. Create new `realms/` directory (with Runtime Participation Contract structure)
4. Create new `experience/` directory
5. Create new `main.py` (minimal, follows architecture guide)

**Files to Create:**
```
symphainy_platform/
├── runtime/                     # NEW - Clean rebuild
│   ├── __init__.py
│   └── README.md               # Rebuild plan
├── civic_systems/               # NEW - Clean rebuild
│   ├── __init__.py
│   ├── smart_city/             # SDK + Primitives
│   ├── experience/             # Experience Plane
│   ├── agentic/                # Agentic SDK
│   └── platform_sdk/            # Platform SDK
├── realms/                     # NEW - Clean rebuild
│   ├── __init__.py
│   ├── content/                # Content Realm
│   ├── insights/               # Insights Realm
│   ├── operations/             # Operations Realm
│   └── outcomes/                # Outcomes Realm
└── experience/                 # NEW - Separate service
    ├── __init__.py
    └── README.md
```

**New main.py Template:**
```python
#!/usr/bin/env python3
"""
Symphainy Platform - Main Entry Point

Clean implementation following architecture guide.
Should be < 100 lines.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
import uvicorn

from utilities import get_logger, get_clock
from config import get_env_contract

# Initialize
env = get_env_contract()
logger = get_logger("platform")
clock = get_clock()

# Create FastAPI app
app = FastAPI(
    title="Symphainy Platform",
    description="Governed Execution Platform",
    version="2.0.0"
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}

def main():
    """Main entry point."""
    host = "0.0.0.0"
    port = env.RUNTIME_PORT
    
    logger.info(f"Starting Symphainy Platform v2.0.0 on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=env.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()
```

**Definition of Done:**
- ✅ Clean structure created
- ✅ New main.py created (< 100 lines)
- ✅ README files created for each new directory
- ✅ No old code in new directories

---

## Day 2-3: Public Works Audit

### Task 2.1: Inventory All Adapters

**Goal:** Document all adapters (what exists, what to keep/update)

**Tasks:**
1. List all adapters in `foundations/public_works/adapters/`
2. Document each adapter:
   - What it does
   - What technology it uses
   - Whether to keep, update, or replace
3. Create adapter inventory document

**Files to Create:**
- `current_state/adapter_inventory.md`

**Adapter Inventory Template:**
```markdown
# Adapter Inventory

## Redis Adapter
- **Location:** `adapters/redis_adapter.py`
- **Technology:** Redis
- **Status:** ✅ Keep (update for Streams)
- **Updates Needed:** Add Redis Streams operations (xadd, xread, xgroup)

## ArangoDB Adapter
- **Location:** `adapters/arango_adapter.py` (if exists)
- **Technology:** ArangoDB
- **Status:** ✅ Keep (enhance for graph operations)
- **Updates Needed:** Add graph operations (migrate from Redis Graph)

## Redis Graph Adapter
- **Location:** `adapters/redis_graph_adapter.py` (if exists)
- **Technology:** Redis Graph (deprecated)
- **Status:** ❌ Remove (migrate to ArangoDB)
- **Migration:** Use ArangoDB graph operations instead

## Supabase Adapter
- **Location:** `adapters/supabase_adapter.py`
- **Technology:** Supabase
- **Status:** ✅ Keep
- **Updates Needed:** None

## GCS Adapter
- **Location:** `adapters/gcs_adapter.py`
- **Technology:** Google Cloud Storage
- **Status:** ✅ Keep
- **Updates Needed:** None

## Consul Adapter
- **Location:** `adapters/consul_adapter.py`
- **Technology:** Consul
- **Status:** ✅ Keep
- **Updates Needed:** None

## Meilisearch Adapter
- **Location:** `adapters/meilisearch_adapter.py`
- **Technology:** Meilisearch
- **Status:** ✅ Keep
- **Updates Needed:** None
```

**Definition of Done:**
- ✅ All adapters inventoried
- ✅ Status determined (keep/update/remove)
- ✅ Updates needed documented
- ✅ Inventory document created

---

### Task 2.2: Inventory All Abstractions

**Goal:** Document all abstractions (what exists, what to keep/update)

**Tasks:**
1. List all abstractions in `foundations/public_works/abstractions/`
2. Document each abstraction:
   - What it does
   - What adapters it uses
   - Whether to keep, update, or replace
3. Create abstraction inventory document

**Files to Create:**
- `current_state/abstraction_inventory.md`

**Abstraction Inventory Template:**
```markdown
# Abstraction Inventory

## State Management Abstraction
- **Location:** `abstractions/state_abstraction.py`
- **Protocol:** `protocols/state_protocol.py`
- **Adapters Used:** Redis, ArangoDB
- **Status:** ✅ Keep (update for hot/cold pattern)
- **Updates Needed:** Add hot/cold state pattern

## Knowledge Discovery Abstraction
- **Location:** `abstractions/knowledge_discovery_abstraction.py`
- **Protocol:** `protocols/knowledge_discovery_protocol.py`
- **Adapters Used:** Meilisearch, Redis Graph (→ ArangoDB), ArangoDB
- **Status:** ✅ Keep (update for ArangoDB graph)
- **Updates Needed:** Replace Redis Graph calls with ArangoDB graph calls

## File Storage Abstraction
- **Location:** `abstractions/file_storage_abstraction.py`
- **Protocol:** `protocols/file_storage_protocol.py`
- **Adapters Used:** GCS, Supabase
- **Status:** ✅ Keep
- **Updates Needed:** None

## Auth Abstraction
- **Location:** `abstractions/auth_abstraction.py`
- **Protocol:** `protocols/auth_protocol.py`
- **Adapters Used:** Supabase
- **Status:** ✅ Keep
- **Updates Needed:** None
```

**Definition of Done:**
- ✅ All abstractions inventoried
- ✅ Status determined (keep/update/remove)
- ✅ Updates needed documented
- ✅ Inventory document created

---

### Task 2.3: Inventory All Protocols

**Goal:** Document all protocols (what exists, what to keep/update)

**Tasks:**
1. List all protocols in `foundations/public_works/protocols/`
2. Document each protocol:
   - What it defines
   - What abstractions implement it
   - Whether to keep, update, or replace
3. Create protocol inventory document

**Files to Create:**
- `current_state/protocol_inventory.md`

**Definition of Done:**
- ✅ All protocols inventoried
- ✅ Status determined (keep/update/remove)
- ✅ Updates needed documented
- ✅ Inventory document created

---

## Day 4: Tech Stack Gap Analysis

### Task 4.1: Document Tech Stack Gaps

**Goal:** Identify what's missing for 350k policies and new architecture

**Tasks:**
1. Review current tech stack
2. Identify gaps:
   - Redis Graph → ArangoDB migration
   - WAL scalability (Lists → Streams)
   - Celery removal
   - Metrics export
   - Transactional outbox
   - Hot/cold state pattern
3. Create tech stack gap document

**Files to Create:**
- `current_state/tech_stack_gaps.md`

**Tech Stack Gaps Template:**
```markdown
# Tech Stack Gap Analysis

## Critical Gaps

### 1. Redis Graph → ArangoDB Migration
- **Current:** Using Redis Graph (deprecated)
- **Needed:** ArangoDB graph operations
- **Impact:** High - affects Librarian, Knowledge Discovery
- **Solution:** Create ArangoDB Graph Adapter, update Knowledge Discovery Abstraction

### 2. WAL Scalability
- **Current:** Redis Lists (10k event limit)
- **Needed:** Redis Streams (millions of events)
- **Impact:** High - affects 350k policies use case
- **Solution:** Enhance Redis Adapter, refactor WAL to use Streams

### 3. Celery Removal
- **Current:** Celery mentioned but unclear usage
- **Needed:** Remove or integrate properly
- **Impact:** Medium - cleanup needed
- **Solution:** Audit usage, remove if not needed, or integrate with Runtime

### 4. Metrics Export
- **Current:** OTEL traces only
- **Needed:** Metrics export to Prometheus
- **Impact:** Medium - affects observability
- **Solution:** Update OTEL Collector config

### 5. Transactional Outbox
- **Current:** Not implemented
- **Needed:** For saga reliability
- **Impact:** High - affects saga reliability
- **Solution:** Implement in Phase 2

### 6. Hot/Cold State Pattern
- **Current:** Redis only (volatile)
- **Needed:** Redis (hot) + ArangoDB (cold)
- **Impact:** High - affects state durability
- **Solution:** Implement in Phase 2
```

**Definition of Done:**
- ✅ All gaps identified
- ✅ Impact assessed
- ✅ Solutions documented
- ✅ Gap document created

---

## Day 5: Create Execution Plans

### Task 5.1: Create Phase 1 Execution Plan

**Goal:** Create detailed, executable plan for Phase 1 (Tech Stack Evolution)

**Tasks:**
1. Create `execution/phase_1_execution_plan.md`
2. Include:
   - Redis Graph → ArangoDB migration (detailed steps)
   - WAL Lists → Streams refactor (detailed steps)
   - Celery removal (detailed steps)
   - Metrics export (detailed steps)
3. Each task must have:
   - Files to create/modify
   - Tests to write
   - Definition of Done
   - No stubs/cheats allowed

**Definition of Done:**
- ✅ Phase 1 execution plan created
- ✅ All tasks have files to create/modify
- ✅ All tasks have tests required
- ✅ All tasks have Definition of Done

---

### Task 5.2: Create Current State Index

**Goal:** Create index of current state documentation

**Tasks:**
1. Create `current_state/00_CURRENT_STATE_INDEX.md`
2. Link to all inventory documents
3. Summarize current state
4. Document what's missing

**Definition of Done:**
- ✅ Current state index created
- ✅ All inventories linked
- ✅ Current state summarized
- ✅ Gaps documented

---

## Phase 0 Checklist

Track progress with this checklist:

### Day 1: Archive
- [ ] Archive structure created
- [ ] Runtime archived
- [ ] Smart City archived
- [ ] Realms archived
- [ ] Experience archived
- [ ] Agentic archived
- [ ] main.py archived
- [ ] Archive README created
- [ ] Clean structure created
- [ ] New main.py created (< 100 lines)

### Day 2-3: Public Works Audit
- [ ] All adapters inventoried
- [ ] Adapter inventory document created
- [ ] All abstractions inventoried
- [ ] Abstraction inventory document created
- [ ] All protocols inventoried
- [ ] Protocol inventory document created

### Day 4: Tech Stack Gaps
- [ ] Tech stack gaps identified
- [ ] Impact assessed
- [ ] Solutions documented
- [ ] Gap document created

### Day 5: Execution Plans
- [ ] Phase 1 execution plan created
- [ ] Current state index created
- [ ] All documentation complete

---

## Success Criteria

**Phase 0 is complete when:**
- ✅ All current implementations archived
- ✅ Clean structure created for rebuild
- ✅ Public Works fully inventoried
- ✅ Tech stack gaps documented
- ✅ Phase 1 execution plan ready
- ✅ Current state index complete

**No code should have stubs, cheats, or placeholders.**

---

## Next Steps

After Phase 0, proceed to [Phase 1: Tech Stack Evolution](phase_1_execution_plan.md).

---

## References

- [Architecture Guide](../architecture/north_star.md)
- [Platform Rules](../PLATFORM_RULES.md)
- [Roadmap](../roadmap/00_ROADMAP_INDEX.md)
