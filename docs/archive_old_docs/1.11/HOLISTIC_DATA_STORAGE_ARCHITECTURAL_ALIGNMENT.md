# Holistic Data Storage Architectural Alignment

**Date:** January 2026  
**Status:** 🔍 **COMPREHENSIVE ANALYSIS**  
**Purpose:** Align all storage systems with Runtime Plane and State Surface architecture

---

## 🎯 Executive Summary

This document provides a comprehensive analysis of data storage patterns across the platform, comparing:
- **Historical patterns** (what we had in `symphainy_source`)
- **Current patterns** (what we have now)
- **Best practices** (aligned with Runtime Plane and State Surface)

**Key Principle:**
> **State Surface = Execution state, facts, references, lineage (small, structured, queryable)**  
> **Storage Systems = Actual data (files, documents, embeddings, registries)**

---

## 📊 Storage System Overview

| Storage System | Purpose | What It Stores | Old Pattern | New Pattern | Best Practice |
|---------------|---------|----------------|-------------|-------------|---------------|
| **Supabase** | File metadata | `project_files`, `parsed_data_files`, `embedding_files` | ✅ Working | ⚠️ Schema alignment needed | ✅ Preserve + align |
| **GCS** | File binaries | Raw files, parsed files (Parquet/JSON) | ✅ Working | ✅ Correct | ✅ Preserve |
| **ArangoDB** | Semantic data | Embeddings, semantic graphs, content metadata | ⚠️ Lazy creation | ⚠️ Needs initialization | ✅ Initialize + index |
| **Redis** | Hot state | Execution state, sessions, WAL, cache | ⚠️ Mixed usage | ✅ State Surface | ✅ Runtime-owned |
| **Consul** | Service discovery | Service registrations (KV store) | ✅ Working | ✅ Correct | ✅ Preserve |
| **Curator** | Platform registries | Services, agents, tools, capabilities | ⚠️ In-memory only | ⚠️ In-memory only | ⚠️ Needs persistence? |

---

## 1. Supabase (File Metadata)

### 1.1 Historical Pattern (Old Architecture)

**Tables:**
- `project_files` - Original uploaded files
  - Primary key: `uuid` (UUID)
  - Fields: `ui_name`, `user_id` (TEXT), `tenant_id` (TEXT), `file_type`, `status`, etc.
  - Lineage: `root_file_uuid`, `parent_file_uuid`, `generation`, `lineage_path`
  
- `parsed_data_files` - Parsed file metadata
  - Primary key: `uuid` (UUID)
  - `file_id` (UUID) → links to `project_files.uuid`
  - `parsed_file_id` (TEXT) - GCS path (NOT UUID!)
  - `user_id` (UUID) - References `auth.users` (added via migration)
  - `ui_name` (TEXT) - Added via migration
  - `data_classification` (TEXT) - 'platform' or 'client'
  - `tenant_id` (TEXT) - Required for client data
  
- `embedding_files` - Embedding metadata
  - Primary key: `uuid` (UUID)
  - `file_id` (TEXT) - Original file UUID (as TEXT!)
  - `parsed_file_id` (TEXT) - Parsed file UUID (as TEXT!)
  - `user_id` (TEXT) - User identifier (as TEXT!)
  - `ui_name` (TEXT) - UI-friendly name
  - `data_classification` (TEXT) - 'platform' or 'client'
  - `tenant_id` (TEXT) - Required for client data

**SQL Functions:**
- `get_file_lineage_tree(root_uuid UUID)` - Recursive lineage query
- `get_file_descendants(root_uuid UUID)` - All descendants
- `get_parsed_files_for_file(file_uuid UUID)` - Parsed files for a file
- `get_latest_parsed_file(file_uuid UUID)` - Latest parsed file
- `get_embedding_files_for_parsed_file(parsed_file_uuid TEXT)` - Embeddings for parsed file
- `get_embedding_files_for_file(file_uuid TEXT)` - Embeddings for original file

**Adapter:**
- `SupabaseFileManagementAdapter` - Raw Supabase client wrapper
- Methods: `create_file()`, `get_file()`, `list_files()`, `create_embedding_file()`, `list_embedding_files()`
- **Missing:** Methods for `parsed_data_files` table

### 1.2 Current Pattern (New Architecture)

**What We Have:**
- ✅ `SupabaseFileAdapter` - Extended with `parsed_data_files` methods
- ✅ `FileMetadataService` - Business logic for file metadata
- ⚠️ **Schema alignment issues:**
  - Using `parsed_file_id` as if it's UUID (it's TEXT - GCS path)
  - Not handling `uuid` as primary key for `parsed_data_files`
  - Field type mismatches (UUID vs TEXT)

### 1.3 Best Practice (Aligned with Runtime Plane)

**Architecture:**
```
File Upload Flow:
1. File data → GCS (via FileStorageAbstraction)
2. File metadata → Supabase `project_files` (via FileMetadataService)
3. File reference → State Surface (via StateSurface.store_file_reference())
4. Lineage fact → State Surface (via StateSurface.store_file_lineage())

Parsing Flow:
1. Parsed file data → GCS (via FileStorageAbstraction)
2. Parsed file metadata → Supabase `parsed_data_files` (via FileMetadataService)
3. Parsed file reference → State Surface
4. Lineage link → State Surface (via StateSurface.link_file_versions())

Embedding Flow:
1. Embedding documents → ArangoDB (via SemanticSearchAbstraction)
2. Embedding metadata → Supabase `embedding_files` (via FileMetadataService)
3. Embedding reference → State Surface
4. Lineage link → State Surface
```

**Key Principles:**
- ✅ **Supabase = Persistent metadata** (source of truth for file metadata)
- ✅ **State Surface = Execution state + lineage facts** (fast lookups during execution)
- ✅ **GCS = File binaries** (actual file data)
- ✅ **ArangoDB = Embedding documents** (semantic data, not file metadata)

**Required Fixes:**
1. ✅ Update `SupabaseFileAdapter` to match schema exactly (UUID vs TEXT)
2. ✅ Add SQL function RPC calls (`get_parsed_files_for_file`, etc.)
3. ✅ Update `FileMetadataService` to use correct field types
4. ✅ Preserve `ui_name` pattern: `"Balances"` → `"parsed_Balances"` → `"embedded_Balances"`

---

## 2. ArangoDB (Semantic Data)

### 2.1 Historical Pattern (Old Architecture)

**Collections:**
- `content_metadata` - Links files to semantic data
  - Fields: `content_id`, `file_id`, `parsed_file_id`, `tenant_id`, `data_classification`
  - Links to: `structured_embeddings`, `semantic_graph_nodes`
  
- `structured_embeddings` - Semantic embeddings for structured data
  - Fields: `content_id`, `file_id`, `parsed_file_id`, `column_name`, `embedding_vector`, `tenant_id`, `data_classification`
  - Indexes: `content_id`, `file_id`, `semantic_id`
  
- `semantic_graph_nodes` - Semantic graph nodes for unstructured data
  - Fields: `content_id`, `file_id`, `entity_id`, `entity_type`, `tenant_id`, `data_classification`
  - Indexes: `content_id`, `file_id`, `entity_id`
  
- `semantic_graph_edges` - Semantic graph edges (edge collection)
  - Fields: `content_id`, `file_id`, `source_entity_id`, `target_entity_id`, `relationship_type`, `tenant_id`
  - Indexes: `content_id`, `file_id`, `source_entity_id`, `target_entity_id`

**Pattern:**
- ✅ Collections created **on-demand** (lazy creation)
- ❌ **No initialization script** (collections created when first used)
- ❌ **No indexes** (created on-demand, may be missing)
- ⚠️ **Tenant filtering** not consistently applied

**Adapter:**
- `ArangoDBAdapter` - Raw ArangoDB client wrapper
- Methods: `create_document()`, `get_document()`, `find_documents()`, `execute_aql()`
- Graph operations: `create_graph()`, `create_vertex()`, `create_edge()`

### 2.2 Current Pattern (New Architecture)

**What We Have:**
- ✅ `ArangoDBAdapter` - Exists in old codebase (not yet in new)
- ❌ **No ArangoDB adapter in new architecture** (needs to be added)
- ❌ **No collection initialization** (needs to be added)
- ❌ **No semantic data abstractions** (needs to be added)

### 2.3 Best Practice (Aligned with Runtime Plane)

**Architecture:**
```
Semantic Data Flow:
1. Embedding generation → ArangoDB `structured_embeddings` (via SemanticSearchAbstraction)
2. Semantic graph creation → ArangoDB `semantic_graph_nodes` + `semantic_graph_edges`
3. Content metadata → ArangoDB `content_metadata` (links files to semantic data)
4. Semantic references → State Surface (via StateSurface.store_fact())

State Surface Stores:
- References to ArangoDB documents (content_id, semantic_id)
- Facts about semantic data (confidence, version, model used)
- Lineage: which agent/tool produced which embedding
```

**Key Principles:**
- ✅ **ArangoDB = Semantic data only** (embeddings, graphs, NOT parsed files)
- ✅ **Parsed files = GCS + Supabase** (NOT ArangoDB)
- ✅ **State Surface = References + facts** (NOT embedding vectors)
- ✅ **Collections initialized explicitly** (not lazy creation)
- ✅ **Indexes created at initialization** (for performance)

**Required:**
1. ✅ Add `ArangoDBAdapter` to Public Works (Layer 0)
2. ✅ Create collection initialization script
3. ✅ Create `SemanticSearchAbstraction` (Layer 1) - already exists!
4. ✅ Ensure State Surface stores references only (not embedding vectors)

**Collections to Initialize:**
```python
collections = {
    "content_metadata": {"type": "document"},
    "structured_embeddings": {"type": "document"},
    "semantic_graph_nodes": {"type": "document"},
    "semantic_graph_edges": {"type": "edge"}
}

indexes = {
    "content_metadata": [
        {"fields": ["data_classification"]},
        {"fields": ["tenant_id"]},
        {"fields": ["data_classification", "tenant_id"]},
        {"fields": ["file_id"]}
    ],
    "structured_embeddings": [
        {"fields": ["data_classification"]},
        {"fields": ["tenant_id"]},
        {"fields": ["content_id"]},
        {"fields": ["file_id"]}
    ],
    # ... similar for other collections
}
```

---

## 3. Redis (Hot State & Caching)

### 3.1 Historical Pattern (Old Architecture)

**Usage:**
- ✅ **Session storage** - `RedisSessionAdapter` stores sessions
- ✅ **Cache** - `CacheAdapter` for content/data caching
- ⚠️ **State management** - `StateManagementAbstraction` uses Redis + ArangoDB
- ⚠️ **Mixed patterns** - Some services use Redis directly, some use abstractions

**Pattern:**
- Redis = Hot state (TTL-based)
- ArangoDB = Durable state (persistent)
- Strategy-based: `hot`, `delayed_persist`, `immediate_persist`, `cache_only`

### 3.2 Current Pattern (New Architecture)

**What We Have:**
- ✅ `RedisAdapter` - Raw Redis client wrapper (Layer 0)
- ✅ `StateManagementAbstraction` - Coordinates Redis + ArangoDB (Layer 1)
- ✅ `StateSurface` - Uses `StateManagementAbstraction` (Runtime Plane)
- ✅ **Clear separation:**
  - State Surface = Execution state, facts, references
  - Redis = Hot state backend (via StateManagementAbstraction)
  - Cache = Separate abstraction (for content caching)

### 3.3 Best Practice (Aligned with Runtime Plane)

**Architecture:**
```
State Surface (Runtime Plane):
├── Uses StateManagementAbstraction (Public Works)
│   ├── Redis (hot state) - TTL-based, fast access
│   └── ArangoDB (durable state) - Persistent, queryable
├── Stores: execution state, facts, references, lineage
└── Does NOT store: file data, embedding vectors, large payloads

Cache Abstraction (Public Works):
├── Uses CacheAdapter (Layer 0)
│   └── Redis (caching) - TTL-based, performance optimization
├── Used by: Content Steward, Data Steward, LLM services
└── Purpose: Content/data caching (NOT execution state)
```

**Key Principles:**
- ✅ **State Surface = Runtime-owned execution state** (via StateManagementAbstraction)
- ✅ **Cache = Content/data caching** (via CacheAbstraction, separate from state)
- ✅ **Redis = Backend for both** (but different abstractions, different purposes)
- ✅ **State Surface stores references** (not data)
- ✅ **TTL-based expiration** (hot state expires, durable state persists)

**Storage Strategy:**
```python
# State Surface (Runtime execution state)
metadata = {
    "backend": "redis",  # or "arango_db"
    "strategy": "hot",  # or "delayed_persist", "immediate_persist"
    "type": "execution_state",  # or "file_lineage", "fact"
    "ttl": 3600  # 1 hour for hot state
}

# Cache (Content/data caching)
cache_abstraction.set(key, value, ttl=3600)  # Separate abstraction
```

**Required:**
1. ✅ Verify State Surface uses StateManagementAbstraction (not direct Redis)
2. ✅ Ensure Cache Abstraction is separate (not mixed with state)
3. ✅ Document when to use State Surface vs Cache Abstraction

---

## 4. Consul (Service Discovery)

### 4.1 Historical Pattern (Old Architecture)

**Usage:**
- ✅ **Service registration** - Services register with Consul
- ✅ **Service discovery** - Services discover each other via Consul
- ✅ **KV store** - Consul KV used for configuration (optional)

**Pattern:**
- Consul = Service registry (not capability registry)
- Services register: `service_name`, `service_id`, `address`, `port`, `tags`, `meta`
- Service discovery: Query by `service_name`, get healthy instances

### 4.2 Current Pattern (New Architecture)

**What We Have:**
- ✅ `ConsulAdapter` - Raw Consul client wrapper (Layer 0)
- ✅ `ServiceDiscoveryAbstraction` - Abstracts Consul (Layer 1)
- ✅ `ServiceRegistry` (Curator) - Uses ServiceDiscoveryAbstraction
- ✅ **Correct pattern:**
  - Services register with Consul (via ServiceDiscoveryAbstraction)
  - Curator tracks service instances (local cache + Consul)
  - Capabilities tracked separately (Curator capability registry)

### 4.3 Best Practice (Aligned with Runtime Plane)

**Architecture:**
```
Service Registration Flow:
1. Service → Curator.register_service()
2. Curator → ServiceDiscoveryAbstraction.register_service()
3. ServiceDiscoveryAbstraction → ConsulAdapter.register_service()
4. Consul → Stores service registration (KV store)
5. Curator → Stores service instance (local cache)

Service Discovery Flow:
1. Runtime → Curator.lookup_capability_by_intent()
2. Curator → Returns CapabilityDefinition (has service_name)
3. Runtime → ServiceDiscoveryAbstraction.discover_service(service_name)
4. ServiceDiscoveryAbstraction → ConsulAdapter.get_service()
5. Consul → Returns healthy service instances
```

**Key Principles:**
- ✅ **Consul = Service registry** (not capability registry)
- ✅ **Curator = Capability registry** (platform ontology, not Consul)
- ✅ **Service discovery = Consul** (infrastructure concern)
- ✅ **Capability lookup = Curator** (platform concern)
- ✅ **Local cache = Performance** (fast lookups, Consul for discovery)

**Storage:**
- **Consul KV:** Service registrations (managed by Consul)
- **Curator (in-memory):** Service instances, capabilities, agents, tools (platform metadata)

**Required:**
1. ✅ Verify Consul stores service registrations correctly
2. ✅ Ensure Curator local cache is separate from Consul
3. ✅ Document service registration lifecycle

---

## 5. Curator (Platform Registries)

### 5.1 Historical Pattern (Old Architecture)

**Registries:**
- ✅ `registered_services` - Service instances (dict)
- ✅ `CapabilityRegistryService` - Service capabilities
- ✅ `AgentCapabilityRegistryService` - Agent capabilities
- ✅ `mcp_tool_registry` - MCP tools (dict)
- ✅ `soa_api_registry` - SOA API endpoints (dict)
- ✅ `mcp_server_registry` - MCP server instances (dict)

**Storage:**
- ⚠️ **In-memory only** (no persistence)
- ⚠️ **Lost on restart** (registries rebuilt on startup)

### 5.2 Current Pattern (New Architecture)

**What We Have:**
- ✅ `ServiceRegistry` - Service instances + Consul integration
- ✅ `CapabilityRegistry` - Service capabilities
- ✅ `AgentRegistry` - Agent capabilities
- ✅ `ToolRegistry` - MCP tools + servers
- ✅ `SOAAPIRegistry` - SOA API endpoints
- ⚠️ **In-memory only** (no persistence)

### 5.3 Best Practice (Aligned with Runtime Plane)

**Architecture:**
```
Curator Registries:
├── Service Registry
│   ├── Local cache (in-memory) - Fast lookups
│   └── Consul (persistent) - Service discovery
├── Capability Registry
│   └── In-memory (platform ontology) - Rebuilt on startup
├── Agent Registry
│   └── In-memory (agent capabilities) - Rebuilt on startup
├── Tool Registry
│   └── In-memory (MCP tools) - Rebuilt on startup
└── SOA API Registry
    └── In-memory (realm APIs) - Rebuilt on startup
```

**Key Principles:**
- ✅ **Service Registry = Consul + local cache** (Consul is persistent)
- ✅ **Other registries = In-memory** (rebuilt on startup from realm initialization)
- ⚠️ **Question:** Should capabilities/agents/tools be persisted?
  - **Option A:** In-memory only (current) - Simple, rebuilt on startup
  - **Option B:** Persist to Consul KV - Survives restarts, but adds complexity
  - **Recommendation:** **Option A** (in-memory) - Registries are metadata, not state

**Storage Decision:**
- ✅ **Services → Consul** (infrastructure concern, needs persistence)
- ✅ **Capabilities/Agents/Tools → In-memory** (platform metadata, rebuilt on startup)
- ✅ **Runtime state → State Surface** (execution state, not registries)

**Required:**
1. ✅ Verify Service Registry uses Consul (persistent)
2. ✅ Document that other registries are in-memory (rebuilt on startup)
3. ✅ Ensure realm initialization rebuilds registries correctly

---

## 6. Local Storage (In-Memory)

### 6.1 Historical Pattern (Old Architecture)

**Usage:**
- ✅ **Tests** - Mock adapters use in-memory storage
- ✅ **Development** - Some services use in-memory fallbacks
- ⚠️ **Mixed patterns** - Some use mocks, some use real adapters

### 6.2 Current Pattern (New Architecture)

**What We Have:**
- ✅ `StateSurface` - `use_memory=True` for tests
- ✅ `InMemoryFileStorage` - For tests
- ✅ Mock adapters - For testing

### 6.3 Best Practice (Aligned with Runtime Plane)

**Architecture:**
```
Test/Development Pattern:
├── StateSurface(use_memory=True) - In-memory state
├── InMemoryFileStorage - In-memory file storage
├── Mock adapters - In-memory backends
└── No external dependencies - Tests run standalone

Production Pattern:
├── StateSurface(state_abstraction=StateManagementAbstraction) - Redis/ArangoDB
├── FileStorageAbstraction - GCS/Supabase
└── Real adapters - Production backends
```

**Key Principles:**
- ✅ **In-memory = Tests only** (not production)
- ✅ **Swappable backends** (via abstractions)
- ✅ **No hard dependencies** (tests don't require Redis/ArangoDB/GCS)

**Required:**
1. ✅ Ensure all abstractions support in-memory backends for tests
2. ✅ Document test patterns (use_memory=True, mock adapters)

---

## 7. Holistic Data Flow

### 7.1 File Upload → Parse → Embed Flow

```
1. File Upload:
   ├── File data → GCS (FileStorageAbstraction)
   ├── File metadata → Supabase `project_files` (FileMetadataService)
   ├── File reference → State Surface (StateSurface.store_file_reference())
   └── Lineage fact → State Surface (StateSurface.store_file_lineage())

2. File Parsing:
   ├── Parsed file data → GCS (FileStorageAbstraction)
   ├── Parsed file metadata → Supabase `parsed_data_files` (FileMetadataService)
   ├── Parsed file reference → State Surface
   └── Lineage link → State Surface (StateSurface.link_file_versions())

3. Embedding Generation:
   ├── Embedding documents → ArangoDB `structured_embeddings` (SemanticSearchAbstraction)
   ├── Embedding metadata → Supabase `embedding_files` (FileMetadataService)
   ├── Embedding reference → State Surface
   └── Lineage link → State Surface
```

### 7.2 Execution State Flow

```
Runtime Execution:
├── Intent submission → Runtime Service
├── Execution state → State Surface (StateSurface.set_execution_state())
├── Saga steps → State Surface (StateSurface.store_saga_step())
├── WAL entries → Redis (via StateManagementAbstraction, hot state)
└── Facts/references → State Surface (StateSurface.store_fact())

Agent Execution:
├── Agent reasoning → Agent Foundation
├── Reasoning artifacts → State Surface (StateSurface.store_fact())
├── Tool calls → Runtime (via Runtime tools)
└── Results → State Surface (references only, not data)
```

### 7.3 Service Registration Flow

```
Service Startup:
├── Service → Curator.register_service()
├── Service instance → Curator ServiceRegistry (local cache)
├── Service registration → Consul (via ServiceDiscoveryAbstraction)
├── Capabilities → Curator CapabilityRegistry (in-memory)
├── Agents → Curator AgentRegistry (in-memory)
└── Tools → Curator ToolRegistry (in-memory)
```

---

## 8. Infrastructure Updates Required

### 8.1 Supabase SQL Updates

**Required:**
1. ✅ **Verify schema matches** - Run SQL scripts from `symphainy_source`:
   - `create_file_management_schema.sql` - `project_files` table
   - `create_parsed_data_files_schema.sql` - `parsed_data_files` table
   - `create_embedding_files_schema.sql` - `embedding_files` table
   - `add_ui_name_to_parsed_data_files.sql` - Migration
   - `add_user_id_to_parsed_data_files.sql` - Migration

2. ✅ **Verify SQL functions exist:**
   - `get_file_lineage_tree(root_uuid UUID)`
   - `get_file_descendants(root_uuid UUID)`
   - `get_parsed_files_for_file(file_uuid UUID)`
   - `get_latest_parsed_file(file_uuid UUID)`
   - `get_embedding_files_for_parsed_file(parsed_file_uuid TEXT)`
   - `get_embedding_files_for_file(file_uuid TEXT)`

3. ✅ **Verify indexes exist:**
   - All tables: `user_id`, `tenant_id`, `ui_name` indexes
   - `parsed_data_files`: `file_id`, `parsed_file_id` indexes
   - `embedding_files`: `file_id`, `parsed_file_id` indexes

**Action Items:**
- [ ] Run SQL scripts in Supabase SQL Editor
- [ ] Verify all tables exist with correct schema
- [ ] Verify all SQL functions exist
- [ ] Verify all indexes exist

### 8.2 ArangoDB Collection Initialization

**Required:**
1. ✅ **Create initialization script:**
   - File: `scripts/initialize_arangodb_collections.py`
   - Creates: `content_metadata`, `structured_embeddings`, `semantic_graph_nodes`, `semantic_graph_edges`
   - Creates indexes: `data_classification`, `tenant_id`, `content_id`, `file_id`

2. ✅ **Run initialization:**
   - As part of deployment process
   - Before first use of semantic data

**Action Items:**
- [ ] Create `scripts/initialize_arangodb_collections.py`
- [ ] Add to deployment process
- [ ] Verify collections exist
- [ ] Verify indexes exist

### 8.3 Consul Configuration

**Required:**
1. ✅ **Verify Consul is running** (docker-compose)
2. ✅ **Verify service registration works** (test registration)
3. ✅ **Verify service discovery works** (test discovery)

**Action Items:**
- [ ] Verify Consul container is healthy
- [ ] Test service registration via ServiceDiscoveryAbstraction
- [ ] Test service discovery via ServiceDiscoveryAbstraction

### 8.4 Redis Configuration

**Required:**
1. ✅ **Verify Redis is running** (docker-compose)
2. ✅ **Verify State Surface uses Redis** (via StateManagementAbstraction)
3. ✅ **Verify Cache Abstraction uses Redis** (separate from state)

**Action Items:**
- [ ] Verify Redis container is healthy
- [ ] Test State Surface storage (via StateManagementAbstraction)
- [ ] Test Cache Abstraction (separate from state)

---

## 9. Best Practices Summary

### 9.1 Storage Responsibility Matrix

| Data Type | Storage System | Abstraction | Purpose |
|-----------|---------------|-------------|---------|
| **File binaries** | GCS | FileStorageAbstraction | Large file storage |
| **File metadata** | Supabase | FileMetadataService | Persistent metadata |
| **Execution state** | Redis (hot) / ArangoDB (durable) | StateManagementAbstraction | Runtime execution state |
| **Facts/references** | Redis (hot) / ArangoDB (durable) | StateManagementAbstraction | Execution facts |
| **Lineage facts** | Redis (hot) / ArangoDB (durable) | StateManagementAbstraction | File lineage |
| **Embedding documents** | ArangoDB | SemanticSearchAbstraction | Semantic data |
| **Content cache** | Redis | CacheAbstraction | Performance optimization |
| **Service registrations** | Consul | ServiceDiscoveryAbstraction | Service discovery |
| **Platform registries** | In-memory (Curator) | Curator registries | Platform metadata |

### 9.2 State Surface Principles

**What State Surface Stores:**
- ✅ Execution state (session_id, execution_id, saga_id, phase, status)
- ✅ Facts ("Field X maps to Policy Number with 0.93 confidence")
- ✅ References (GCS URIs, Supabase row IDs, ArangoDB document IDs)
- ✅ Lineage facts (file_id → parsed_file_id → embedding_id)
- ✅ Policy metadata (access scope, tenancy, retention)

**What State Surface Does NOT Store:**
- ❌ File data (bytes, blobs)
- ❌ Embedding vectors (large arrays)
- ❌ Parsed data (DataFrames, JSON documents)
- ❌ Large payloads (> few KB)
- ❌ Domain models (SOPs, workflows, blueprints)

### 9.3 Storage System Principles

**Supabase:**
- ✅ Persistent metadata (source of truth)
- ✅ Fast queries (indexed, relational)
- ✅ Multi-tenant isolation (RLS policies)
- ✅ SQL functions for complex queries

**ArangoDB:**
- ✅ Semantic data (embeddings, graphs)
- ✅ Graph queries (relationships, traversals)
- ✅ Document storage (flexible schema)
- ✅ NOT for file binaries or parsed files

**Redis:**
- ✅ Hot state (TTL-based, fast access)
- ✅ Cache (performance optimization)
- ✅ WAL (write-ahead log)
- ✅ NOT for durable state (use ArangoDB)

**Consul:**
- ✅ Service discovery (infrastructure concern)
- ✅ Service registrations (persistent)
- ✅ NOT for platform metadata (use Curator)

**Curator:**
- ✅ Platform registries (capabilities, agents, tools)
- ✅ In-memory (rebuilt on startup)
- ✅ Service instances (local cache + Consul)

---

## 10. Action Items Summary

### 10.1 Immediate (Phase 0)

1. **Supabase Schema Alignment:**
   - [ ] Update `SupabaseFileAdapter` to match schema (UUID vs TEXT)
   - [ ] Add SQL function RPC calls
   - [ ] Update `FileMetadataService` field types
   - [ ] Run SQL scripts in Supabase SQL Editor

2. **ArangoDB Initialization:**
   - [ ] Create `scripts/initialize_arangodb_collections.py`
   - [ ] Add ArangoDB adapter to Public Works
   - [ ] Create collections and indexes
   - [ ] Verify semantic data storage works

3. **State Surface Verification:**
   - [ ] Verify State Surface stores references only (not data)
   - [ ] Verify file lineage tracking works
   - [ ] Verify execution state storage works

### 10.2 Short-term (Phase 1-2)

1. **Curator Persistence (Optional):**
   - [ ] Decide: In-memory vs Consul KV for capabilities/agents/tools
   - [ ] If Consul KV: Add persistence layer
   - [ ] If in-memory: Document rebuild-on-startup pattern

2. **Documentation:**
   - [ ] Document storage responsibility matrix
   - [ ] Document State Surface principles
   - [ ] Document when to use which storage system

### 10.3 Long-term (Phase 3+)

1. **Performance Optimization:**
   - [ ] Add Redis caching for frequent queries
   - [ ] Add ArangoDB indexes for graph queries
   - [ ] Add Supabase indexes for lineage queries

2. **Monitoring:**
   - [ ] Add storage system health checks
   - [ ] Add storage usage metrics
   - [ ] Add storage performance monitoring

---

## 11. Decision Points

### 11.1 Curator Persistence

**Question:** Should Curator registries (capabilities, agents, tools) be persisted?

**Option A: In-Memory Only (Current)**
- ✅ Simple (no persistence layer)
- ✅ Rebuilt on startup (from realm initialization)
- ✅ Fast (no database queries)
- ❌ Lost on restart (but rebuilt automatically)

**Option B: Consul KV**
- ✅ Survives restarts
- ✅ Can query across instances
- ❌ Adds complexity (Consul KV management)
- ❌ May not be needed (registries are metadata, not state)

**Recommendation:** **Option A (In-Memory)** - Registries are platform metadata, not execution state. They're rebuilt on startup from realm initialization, which is the correct pattern.

### 11.2 ArangoDB for Parsed Files

**Question:** Should parsed files be stored in ArangoDB?

**Decision:** **NO** - Parsed files are:
- ✅ Stored in GCS (binary storage)
- ✅ Metadata in Supabase (relational queries)
- ❌ NOT in ArangoDB (not semantic data)

**Rationale:**
- ArangoDB is for semantic data (embeddings, graphs)
- Parsed files are client data (GCS + Supabase pattern)
- Clear boundary: client data vs platform intelligence

### 11.3 State Surface Durability

**Question:** Should State Surface use ArangoDB for durable state?

**Decision:** **YES** - State Surface should:
- ✅ Use Redis for hot state (fast, TTL-based)
- ✅ Use ArangoDB for durable state (persistent, queryable)
- ✅ Strategy-based: `hot` → Redis, `delayed_persist` → ArangoDB

**Rationale:**
- Execution state needs durability (for saga recovery)
- Facts need queryability (for lineage queries)
- References need persistence (for audit trails)

---

## 12. Conclusion

**Key Takeaways:**
1. ✅ **State Surface = Execution state, facts, references** (not data)
2. ✅ **Supabase = File metadata** (persistent, relational)
3. ✅ **ArangoDB = Semantic data** (embeddings, graphs, NOT parsed files)
4. ✅ **Redis = Hot state + cache** (TTL-based, fast)
5. ✅ **Consul = Service discovery** (infrastructure concern)
6. ✅ **Curator = Platform registries** (in-memory, rebuilt on startup)

**Next Steps:**
1. Fix Supabase schema alignment
2. Add ArangoDB initialization
3. Verify State Surface patterns
4. Test end-to-end storage flows

---

**Status:** Ready for implementation review and infrastructure updates.
