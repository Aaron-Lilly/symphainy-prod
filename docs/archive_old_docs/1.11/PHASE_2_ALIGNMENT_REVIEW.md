# Phase 2 Alignment Review: Services vs Capabilities

**Date:** January 2026  
**Status:** 🔍 **REVIEW IN PROGRESS**  
**Issue:** Curator pattern alignment with Consul service discovery

---

## 📋 Key Insight

**Consul expects SERVICES, not capabilities.**

The pattern should be:
1. **Services register themselves** → Consul (service discovery)
2. **Services register their capabilities** → Curator (capability registry)
3. **Intent → capability lookup** → Curator (not Consul)
4. **Service discovery** → Consul (which service instance is where)

---

## 🔍 Current Implementation vs. Required Pattern

### What I Built (Incorrect)

**Curator Foundation:**
- ✅ Capability registry (correct)
- ✅ Intent → capability lookup (correct)
- ❌ **MISSING:** Service registration (for Consul)
- ❌ **MISSING:** Service discovery integration

**Public Works Foundation:**
- ✅ State abstraction (correct)
- ❌ **MISSING:** Service discovery abstraction (needed for Consul)

### What's Actually Needed

**Curator Foundation should:**
1. ✅ Register capabilities (what I built)
2. ✅ Provide intent → capability lookup (what I built)
3. ⚠️ **ADD:** Service registration (for Consul service discovery)
4. ⚠️ **ADD:** Integration with Public Works service discovery abstraction

**Public Works Foundation should:**
1. ✅ State abstraction (what I built)
2. ⚠️ **ADD:** Service discovery abstraction (for Consul/Istio/Linkerd)

---

## 🎯 Correct Pattern (from symphainy_source)

### Service Registration Flow

```
Service → Curator.register_service() 
  ├─> Registers service instance with Consul (via Public Works)
  ├─> Registers capabilities (capability registry)
  ├─> Registers SOA APIs (SOA API registry)
  └─> Registers MCP tools (MCP tool registry)
```

### Service Discovery Flow

```
Runtime → Curator.lookup_capability_by_intent()
  ├─> Returns CapabilityDefinition
  ├─> CapabilityDefinition has service_name
  └─> Runtime → Public Works → Consul → Get service instance
```

---

## 🔧 Required Changes

### 1. Add Service Registration to Curator

**File:** `symphainy_platform/foundations/curator/foundation_service.py`

**Add:**
- `register_service()` method
- Service instance registry (for Consul)
- Integration with Public Works service discovery abstraction

### 2. Add Service Discovery Abstraction to Public Works

**File:** `symphainy_platform/foundations/public_works/abstractions/service_discovery_abstraction.py`

**Add:**
- Service discovery protocol
- Consul adapter integration
- Service registration/lookup methods

### 3. Update Curator to Use Service Discovery Abstraction

**File:** `symphainy_platform/foundations/curator/foundation_service.py`

**Update:**
- Use Public Works service discovery abstraction for Consul registration
- Keep capability registry separate (Curator's domain)

---

## ✅ What's Correct

1. ✅ **Capability registry** - Correct (Curator's domain)
2. ✅ **Intent → capability lookup** - Correct (Curator's domain)
3. ✅ **State abstraction** - Correct (Public Works domain)

---

## ⚠️ What Needs to Be Added

1. ⚠️ **Service registration** - Add to Curator (for Consul)
2. ⚠️ **Service discovery abstraction** - Add to Public Works (for Consul/Istio/Linkerd)
3. ⚠️ **Integration** - Curator uses Public Works service discovery

---

## 🎯 Recommendation

**Align with service-first pattern:**
- Services register themselves (for Consul)
- Capabilities are metadata about services (Curator registry)
- Service discovery is infrastructure (Public Works abstraction)

**Next Steps:**
1. Add service discovery abstraction to Public Works
2. Add service registration to Curator
3. Integrate Curator with Public Works service discovery

---

**Last Updated:** January 2026
