# Phase 2: Service-First Pattern Alignment

**Date:** January 2026  
**Status:** 🔧 **ALIGNMENT REQUIRED**  
**Issue:** Curator should register SERVICES (for Consul), not just capabilities

---

## 🎯 Correct Pattern (from symphainy_source)

### Service Registration Flow

```
Service → Curator.register_service()
  ├─> Registers SERVICE INSTANCE with Consul (via Public Works)
  ├─> Registers CAPABILITIES (Curator capability registry)
  ├─> Registers SOA APIs (Curator SOA API registry)
  └─> Registers MCP tools (Curator MCP tool registry)
```

**Key Insight:** Consul expects SERVICES, not capabilities. Capabilities are metadata about services.

### Service Discovery Flow

```
Runtime → Curator.lookup_capability_by_intent()
  ├─> Returns CapabilityDefinition
  ├─> CapabilityDefinition has service_name
  └─> Runtime → Public Works → Consul → Get service instance
```

---

## ⚠️ What I Built (Incorrect)

**Current Implementation:**
- ✅ Capability registry (correct)
- ✅ Intent → capability lookup (correct)
- ❌ **MISSING:** Service registration (for Consul)
- ❌ **MISSING:** Service discovery abstraction (Public Works)

---

## ✅ What Needs to Be Added

### 1. Service Discovery Abstraction (Public Works)

**File:** `symphainy_platform/foundations/public_works/abstractions/service_discovery_abstraction.py`

**Purpose:** Abstract Consul/Istio/Linkerd service discovery

**Methods:**
- `register_service()` - Register service instance
- `discover_service()` - Discover service instances
- `deregister_service()` - Deregister service

### 2. Service Registration (Curator)

**File:** `symphainy_platform/foundations/curator/foundation_service.py`

**Add:**
- `register_service()` method
- Service instance registry (for Consul)
- Integration with Public Works service discovery abstraction

**Pattern:**
```python
async def register_service(
    self,
    service_instance: Any,
    service_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Register a service with Curator.
    
    1. Register service instance with Consul (via Public Works)
    2. Register capabilities (Curator capability registry)
    3. Register SOA APIs (Curator SOA API registry)
    4. Register MCP tools (Curator MCP tool registry)
    """
```

---

## 🔧 Implementation Plan

### Step 1: Add Service Discovery Abstraction to Public Works

1. Create `service_discovery_abstraction.py`
2. Create `service_discovery_protocol.py` (Protocol)
3. Add Consul adapter (can be minimal for now)
4. Integrate into Public Works Foundation Service

### Step 2: Add Service Registration to Curator

1. Add `register_service()` method
2. Add service instance registry
3. Integrate with Public Works service discovery abstraction
4. Keep capability registry separate (Curator's domain)

### Step 3: Update Curator to Use Service Discovery

1. Get service discovery abstraction from Public Works
2. Use it for Consul registration
3. Keep capability registry as metadata about services

---

## ✅ What's Correct

1. ✅ **Capability registry** - Correct (Curator's domain)
2. ✅ **Intent → capability lookup** - Correct (Curator's domain)
3. ✅ **State abstraction** - Correct (Public Works domain)

---

## ⚠️ What Needs to Be Added

1. ⚠️ **Service discovery abstraction** - Add to Public Works (for Consul/Istio/Linkerd)
2. ⚠️ **Service registration** - Add to Curator (for Consul)
3. ⚠️ **Integration** - Curator uses Public Works service discovery

---

## 🎯 Recommendation

**Align with service-first pattern:**
- Services register themselves (for Consul) ← **ADD THIS**
- Capabilities are metadata about services (Curator registry) ← **KEEP THIS**
- Service discovery is infrastructure (Public Works abstraction) ← **ADD THIS**

**Next Steps:**
1. Add service discovery abstraction to Public Works
2. Add service registration to Curator
3. Integrate Curator with Public Works service discovery

---

**Last Updated:** January 2026
