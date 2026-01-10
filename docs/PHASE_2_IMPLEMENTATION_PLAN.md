# Phase 2 Implementation Plan

**Date:** January 2026  
**Status:** 🎯 **READY TO START**  
**Based on:** `rebuild_implementation_plan_v2.md`

---

## 📋 Executive Summary

Phase 2 builds the Foundations layer that serves the Runtime Plane:
1. **Public Works Foundation** - Infrastructure abstractions (adapters, abstractions, IO, infra bindings)
2. **Curator Foundation** - Capability registry (intent → capability lookup)

**Key Principle:** Everything uses abstractions for swappability.

---

## 🎯 Phase 2 Requirements

### Public Works Foundation

**5-Layer Architecture:**
```
Layer 0: Infrastructure Adapters (Raw Technology)
Layer 1: Infrastructure Abstractions (Business Logic)
Layer 2: Infrastructure Registries (Initialization)
Layer 3: Composition Services (Orchestration)
Layer 4: Foundation Service (Public Works Foundation Service)
```

**Rules:**
- Foundations never call realms
- Foundations never reason
- Foundations are deterministic

### Curator Foundation

**Refocused as Capability Registry:**
- Registers capabilities
- Describes: inputs, outputs, determinism, owning realm
- Provides lookup: `intent → capability`

**NOT execution** - Runtime executes, Curator just registers/looks up.

---

## 📊 Implementation Strategy

### Approach: Build Minimal, Essential Components First

**Phase 2.1: Core Abstractions (Week 1)**
1. State Management Abstraction (for Runtime Plane)
2. Basic adapters (Redis, ArangoDB)
3. Public Works Foundation Service structure

**Phase 2.2: Curator Foundation (Week 1-2)**
1. Capability registry
2. Intent → capability lookup
3. Capability registration API

**Phase 2.3: Integration (Week 2)**
1. Integrate Runtime Plane with Public Works abstractions
2. Update State Surface to use abstractions
3. Test end-to-end

---

## 🔧 Implementation Steps

### Step 1: Create Public Works Foundation Structure

**Directory:** `symphainy_platform/foundations/public_works/`

**Structure:**
```
public_works/
├── __init__.py
├── adapters/          # Layer 0: Raw technology clients
│   ├── __init__.py
│   ├── redis_adapter.py
│   └── arango_adapter.py
├── abstractions/      # Layer 1: Business logic abstractions
│   ├── __init__.py
│   └── state_abstraction.py
├── registries/        # Layer 2: Initialization
│   ├── __init__.py
│   └── infrastructure_registry.py
├── protocols/          # Abstraction contracts (Protocols)
│   ├── __init__.py
│   └── state_protocol.py
└── foundation_service.py  # Layer 4: Foundation Service
```

### Step 2: Create Curator Foundation Structure

**Directory:** `symphainy_platform/foundations/curator/`

**Structure:**
```
curator/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── capability_definition.py
├── registry/
│   ├── __init__.py
│   └── capability_registry.py
└── foundation_service.py
```

---

## 🎯 Priority Order

1. **State Management Abstraction** (highest priority - Runtime needs it)
2. **Redis Adapter** (needed for state abstraction)
3. **Public Works Foundation Service** (orchestrates everything)
4. **Curator Foundation** (capability registry)
5. **ArangoDB Adapter** (for durable state - can be minimal initially)

---

**Last Updated:** January 2026
