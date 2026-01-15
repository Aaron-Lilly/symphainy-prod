# Finding Abstractions Guide

**Date:** January 13, 2026  
**Status:** 📋 **LESSON LEARNED**  
**Purpose:** How to find abstractions when they're not where you expect

---

## Key Insight

**⚠️ CRITICAL:** All 8 Smart City roles ACTUALLY WORK in the old world. If you can't find an abstraction, the pattern is just different than expected - don't assume it doesn't exist!

---

## Where to Look

### 1. Service Initialization (`__init__` or `initialize()`)

```python
# Look for these patterns:
self.file_management_abstraction = None
self.content_metadata_abstraction = None
self.messaging_abstraction = None
```

### 2. Module Initialization Files (`modules/initialization.py`)

```python
# Abstractions are often initialized here:
self.service.file_management_abstraction = self.service.get_file_management_abstraction()
self.service.content_metadata_abstraction = self.service.get_content_metadata_abstraction()
```

### 3. InfrastructureAccessMixin Methods

```python
# Smart City services can access abstractions via:
self.get_infrastructure_abstraction("file_management")
self.get_file_management_abstraction()
self.get_messaging_abstraction()
```

### 4. Public Works Foundation Service

**Location:** `foundations/public_works_foundation/public_works_foundation_service.py`

**All Available Abstractions:**
- `auth_abstraction`
- `authorization_abstraction`
- `session_abstraction`
- `tenant_abstraction`
- `messaging_abstraction`
- `event_management_abstraction`
- `file_management_abstraction`
- `content_metadata_abstraction`
- `semantic_data_abstraction`
- `service_discovery_abstraction`
- `routing_abstraction`
- `telemetry_abstraction`
- `health_abstraction`
- `observability_abstraction`
- And more...

**Access Pattern:**
```python
public_works = self.di_container.get_public_works_foundation()
abstraction = public_works.get_abstraction("file_management")
```

### 5. Composition Services (Alternative Pattern!)

**Location:** `foundations/public_works_foundation/composition_services/`

**Available Services:**
- `PostOfficeCompositionService` - For events/messaging
- `StateCompositionService` - For state management
- `SessionCompositionService` - For sessions
- `ConductorCompositionService` - For workflows
- `SecurityCompositionService` - For auth/authz
- `PolicyCompositionService` - For policy management

**Access Pattern:**
```python
post_office_service = self.di_container.get_foundation_service("PostOfficeCompositionService")
# Then use service methods instead of abstraction
```

### 6. Direct Adapter Access (Anti-Pattern, but May Exist)

```python
# May access adapters directly:
gcs_adapter = self.service.file_management_abstraction.gcs_adapter
supabase_adapter = self.service.file_management_abstraction.supabase_adapter
```

---

## Common Patterns

### Pattern 1: Direct Abstraction Access (Most Common)

```python
# In service __init__:
self.file_management_abstraction = None

# In module initialization:
self.service.file_management_abstraction = self.service.get_file_management_abstraction()

# In module methods:
result = await self.service.file_management_abstraction.create_file(...)
```

### Pattern 2: Via InfrastructureAccessMixin

```python
# Direct access via mixin:
self.file_management = self.get_infrastructure_abstraction("file_management")
```

### Pattern 3: Via Public Works Foundation (Smart City Direct Access)

```python
# Smart City services have direct access:
public_works = self.di_container.get_public_works_foundation()
abstraction = public_works.get_abstraction("file_management")
```

### Pattern 4: Via Composition Service

```python
# Alternative pattern - use composition service:
post_office_service = self.di_container.get_foundation_service("PostOfficeCompositionService")
# Then use service methods
```

### Pattern 5: Direct Adapter Access (Anti-Pattern)

```python
# Bypassing abstraction (anti-pattern, but may exist):
gcs_adapter = self.service.file_management_abstraction.gcs_adapter
result = await gcs_adapter.upload_file(...)
```

---

## Debugging Checklist

When you can't find an abstraction:

1. ✅ **Search service code** for `get_*_abstraction` calls
2. ✅ **Search module files** for `self.service.*_abstraction` usage
3. ✅ **Check `modules/initialization.py`** - abstractions are usually set up here
4. ✅ **Check Public Works Foundation Service** - see all available abstractions
5. ✅ **Check composition services** - may use services instead of abstractions
6. ✅ **Check mixin methods** - `InfrastructureAccessMixin` provides access methods
7. ✅ **Remember:** If the role works, the abstraction exists - just find the access pattern!

---

## Examples

### Example 1: Finding Data Steward Abstractions

**What to look for:**
- `file_management_abstraction` ✅ Found in `modules/initialization.py`
- `content_metadata_abstraction` ✅ Found in `modules/initialization.py`
- `knowledge_governance_abstraction` ✅ Found in `modules/initialization.py`
- `state_management_abstraction` ✅ Found in `modules/initialization.py`
- `messaging_abstraction` ✅ Found in `modules/initialization.py`

**Access pattern:**
```python
# In modules/initialization.py:
self.service.file_management_abstraction = self.service.get_file_management_abstraction()
```

### Example 2: Finding Post Office Abstractions

**What to look for:**
- `messaging_abstraction` ✅ Found in `modules/initialization.py`
- `event_management_abstraction` ✅ Found in `modules/initialization.py`
- `PostOfficeCompositionService` ✅ Alternative pattern in Public Works Foundation

**Access pattern:**
```python
# In modules/initialization.py:
self.service.messaging_abstraction = self.service.get_messaging_abstraction()
self.service.event_management_abstraction = self.service.get_event_management_abstraction()
```

### Example 3: Finding Traffic Cop Abstractions

**What to look for:**
- `session_abstraction` ✅ Found in `modules/initialization.py`
- `state_management_abstraction` ✅ Found in `modules/initialization.py`
- `SessionCompositionService` ✅ Alternative pattern in Public Works Foundation

**Access pattern:**
```python
# In modules/initialization.py:
self.service.session_abstraction = self.service.get_session_abstraction()
self.service.state_management_abstraction = self.service.get_state_management_abstraction()
```

---

## Key Takeaways

1. **All roles work** - If you can't find it, the pattern is just different
2. **Check module initialization files** - This is where abstractions are usually set up
3. **Check Public Works Foundation** - Complete list of available abstractions
4. **Check composition services** - Alternative pattern for accessing infrastructure
5. **Don't assume** - Search thoroughly before concluding an abstraction doesn't exist
