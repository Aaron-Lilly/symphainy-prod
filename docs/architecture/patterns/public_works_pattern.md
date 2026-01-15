# Public Works Pattern

**Status:** Canonical Pattern  
**Purpose:** Enable infrastructure swappability

---

## Overview

Public Works is the **infrastructure abstraction layer** that enables swappability.

**Key Principle:** All infrastructure access flows through Public Works abstractions. This enables swapping infrastructure (Redis → ArangoDB, etc.) without changing business logic.

---

## 5-Layer Architecture

```
Layer 4: Foundation Service (Orchestration)
  ↓
Layer 3: Composition Services (N/A for Public Works)
  ↓
Layer 2: Protocols (Contracts)
  ↓
Layer 1: Abstractions (Business Logic)
  ↓
Layer 0: Adapters (Technology Bindings)
```

### Layer 0: Adapters (Technology Bindings)

**Purpose:** Raw technology bindings.

**Examples:**
- `RedisAdapter` - Direct Redis client calls
- `ArangoAdapter` - Direct ArangoDB client calls
- `SupabaseAdapter` - Direct Supabase client calls

**Rules:**
- ✅ Direct technology calls only
- ✅ No business logic
- ✅ No platform awareness
- ❌ No business logic
- ❌ No platform concepts

### Layer 1: Abstractions (Business Logic)

**Purpose:** Business logic that coordinates adapters.

**Examples:**
- `StateManagementAbstraction` - Coordinates Redis + ArangoDB for state
- `KnowledgeDiscoveryAbstraction` - Coordinates Meilisearch + ArangoDB for search
- `FileStorageAbstraction` - Coordinates GCS + Supabase for file storage

**Rules:**
- ✅ Business logic (coordination, validation, transformation)
- ✅ Uses adapters (Layer 0)
- ✅ Implements protocols (Layer 2)
- ❌ No direct technology calls
- ❌ No platform execution awareness

### Layer 2: Protocols (Contracts)

**Purpose:** Define contracts for swappability.

**Examples:**
- `StateManagementProtocol` - Contract for state operations
- `KnowledgeDiscoveryProtocol` - Contract for knowledge operations
- `FileStorageProtocol` - Contract for file operations

**Rules:**
- ✅ Define interface only
- ✅ Enable swappability
- ❌ No implementation
- ❌ No business logic

### Layer 4: Foundation Service (Orchestration)

**Purpose:** Orchestrate all adapters and abstractions.

**Example:**
- `PublicWorksFoundationService` - Initializes and wires all adapters/abstractions

**Rules:**
- ✅ Orchestration only
- ✅ Dependency injection
- ❌ No business logic
- ❌ No execution

---

## Swappability Pattern

### Example: Redis Graph → ArangoDB Migration

**Before (Redis Graph):**
```python
# Adapter (Layer 0)
class RedisGraphAdapter:
    async def execute_query(self, query: str):
        return await self.redis_client.execute_command("GRAPH.QUERY", query)

# Abstraction (Layer 1)
class KnowledgeDiscoveryAbstraction:
    def __init__(self, redis_graph_adapter):
        self.redis_graph = redis_graph_adapter
    
    async def search_graph(self, query: str):
        return await self.redis_graph.execute_query(query)
```

**After (ArangoDB):**
```python
# Adapter (Layer 0) - SWAPPED
class ArangoGraphAdapter:
    async def execute_query(self, query: str):
        return await self.arango_client.execute_query(query)

# Abstraction (Layer 1) - UPDATED (only adapter reference)
class KnowledgeDiscoveryAbstraction:
    def __init__(self, arango_graph_adapter):  # Adapter swapped
        self.arango_graph = arango_graph_adapter  # Reference updated
    
    async def search_graph(self, query: str):
        return await self.arango_graph.execute_query(query)  # Same interface
```

**Business Logic (Librarian Service):**
```python
# UNCHANGED - Validates pattern!
class LibrarianService:
    def __init__(self, knowledge_discovery_abstraction):
        self.knowledge_discovery = knowledge_discovery_abstraction
    
    async def search(self, query: str):
        return await self.knowledge_discovery.search_graph(query)  # Same call
```

**Result:** Business logic unchanged. Only adapter swapped. Pattern validated.

---

## When to Use

### ✅ Use Public Works For:
- All infrastructure access (Redis, ArangoDB, Supabase, GCS, etc.)
- All file operations
- All state operations
- All authentication
- All service discovery

### ❌ Don't Use Public Works For:
- Business logic (belongs in Realms)
- Execution logic (belongs in Runtime)
- Governance logic (belongs in Smart City)
- Domain logic (belongs in Realms)

---

## Migration Pattern

When migrating infrastructure:

1. **Create New Adapter** (Layer 0)
   - Implement same interface as old adapter
   - Use new technology

2. **Update Abstraction** (Layer 1)
   - Swap adapter reference
   - Keep business logic unchanged
   - Keep protocol interface unchanged

3. **Update Foundation Service** (Layer 4)
   - Register new adapter
   - Remove old adapter

4. **Validate Pattern**
   - Business logic unchanged
   - Protocol interface unchanged
   - Only adapter swapped

---

## Benefits

1. **Swappability:** Swap infrastructure without changing business logic
2. **Testability:** Mock adapters for testing
3. **Flexibility:** Support multiple infrastructure options
4. **Validation:** Pattern validates itself (easy migrations = good pattern)

---

## References

- [Architecture Guide](north_star.md)
- [Platform Rules](../PLATFORM_RULES.md)
- [Execution Plans](../execution/00_EXECUTION_INDEX.md)
