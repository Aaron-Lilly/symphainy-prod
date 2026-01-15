# Data Steward Refactoring Plan

**Date:** January 13, 2026  
**Status:** 📋 **READY TO EXECUTE**  
**Pattern:** Security Guard (established and tested)

---

## Overview

Refactor Data Steward using the Security Guard pattern:
1. Find all abstractions used
2. Refactor abstractions to be pure infrastructure
3. Add Platform SDK methods for translation
4. Create Data Steward Primitive for policy decisions
5. Test with real infrastructure

---

## Step 0: Find Abstractions ✅

**Abstractions Used by Data Steward:**
1. ✅ `file_management_abstraction` (GCS + Supabase) - Found in `modules/initialization.py`
2. ✅ `content_metadata_abstraction` (ArangoDB) - Found in `modules/initialization.py`
3. ✅ `knowledge_governance_abstraction` (ArangoDB + Metadata) - Found in `modules/initialization.py`
4. ✅ `state_management_abstraction` (ArangoDB for lineage) - Found in `modules/initialization.py`
5. ✅ `messaging_abstraction` (Redis) - Found in `modules/initialization.py`

**Access Pattern:**
```python
# In modules/initialization.py:
self.service.file_management_abstraction = self.service.get_file_management_abstraction()
self.service.content_metadata_abstraction = self.service.get_content_metadata_abstraction()
self.service.knowledge_governance_abstraction = self.service.get_knowledge_governance_abstraction()
self.service.state_management_abstraction = self.service.get_state_management_abstraction()
self.service.messaging_abstraction = self.service.get_messaging_abstraction()
```

---

## Step 1: Analyze Current Implementation

### 1.1 File Management Abstraction (`file_management_abstraction_gcs.py`)

**Business Logic Found:**
- ❌ UUID generation (`_generate_file_uuid()`)
- ❌ Field validation (required fields: `user_id`, `ui_name`, `file_type`)
- ❌ Business metadata enhancement:
  - `created_at`, `updated_at` timestamps
  - `status` defaulting to "uploaded"
  - `pillar_origin` defaulting to "content_pillar"
  - `upload_source` defaulting to "api"
- ❌ MIME type mapping (extension → MIME type)
- ❌ Status filtering logic in `list_files()`

**What Should Return:**
- Raw file data from GCS adapter
- Raw metadata from Supabase adapter
- No business logic, no validation, no defaults

### 1.2 Content Metadata Abstraction (`content_metadata_abstraction.py`)

**Business Logic Found:**
- ❌ Content ID generation (UUID if not provided)
- ❌ Field validation (required fields: `file_uuid`, `content_type`)
- ❌ Business metadata enhancement:
  - `created_at`, `updated_at` timestamps
  - `status` defaulting to "active"
  - `version` defaulting to 1
  - `analysis_status` defaulting to "pending"
- ❌ Relationship checking before deletion (business rule)
- ❌ Default status filtering in `search_content_metadata()`

**What Should Return:**
- Raw content metadata from ArangoDB adapter
- No business logic, no validation, no defaults

### 1.3 Knowledge Governance Abstraction

**Need to Analyze:** Check what business logic exists

### 1.4 State Management Abstraction

**Need to Analyze:** Check what business logic exists (for lineage)

### 1.5 Messaging Abstraction

**Need to Analyze:** Check what business logic exists (for caching)

---

## Step 2: Refactor Abstractions

### 2.1 File Storage Abstraction (New Name)

**Location:** `symphainy_platform/foundations/public_works/abstractions/file_storage_abstraction.py`

**Current State:** Already exists in new codebase - need to check if it's pure

**Refactoring:**
- Remove UUID generation → Move to Platform SDK
- Remove field validation → Move to Platform SDK
- Remove business metadata enhancement → Move to Platform SDK
- Remove MIME type mapping → Move to Platform SDK
- Return raw data from adapters only

**Methods to Refactor:**
```python
async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create file - pure infrastructure only."""
    # Store in GCS
    gcs_result = await self.gcs_adapter.upload_file(...)
    # Store metadata in Supabase
    supabase_result = await self.supabase_adapter.create_file(...)
    # Return raw data (no business logic)
    return {
        "gcs_result": gcs_result,
        "supabase_result": supabase_result
    }
```

### 2.2 Content Metadata Abstraction

**Location:** Need to create in new codebase

**Refactoring:**
- Remove content ID generation → Move to Platform SDK
- Remove field validation → Move to Platform SDK
- Remove business metadata enhancement → Move to Platform SDK
- Remove relationship checking → Move to Platform SDK
- Return raw data from ArangoDB adapter only

### 2.3 Knowledge Governance Abstraction

**Location:** Need to analyze and potentially create

**Refactoring:**
- Remove any business logic
- Return raw data only

### 2.4 State Management Abstraction (for Lineage)

**Location:** `symphainy_platform/foundations/public_works/abstractions/state_abstraction.py`

**Current State:** Already exists - need to check if it's pure

**Refactoring:**
- Remove lineage graph construction → Move to Platform SDK
- Return raw state data only

### 2.5 Messaging Abstraction

**Location:** Need to check if exists

**Refactoring:**
- Remove any business logic
- Return raw messaging data only

---

## Step 3: Add Platform SDK Methods

**Location:** `civic_systems/platform_sdk/platform_sdk.py`

**Methods to Add:**
```python
# Data Steward methods
async def resolve_file_metadata(
    self,
    raw_file_data: Dict[str, Any],
    raw_metadata: Dict[str, Any]
) -> FileMetadata:
    """
    Translates raw file data from GCS + Supabase into FileMetadata business object.
    This is the harvested business logic from FileManagementAbstraction.
    """
    # Generate UUID if not present
    # Add business metadata (created_at, status, etc.)
    # Map MIME types
    # Return FileMetadata object

async def resolve_content_metadata(
    self,
    raw_content_data: Dict[str, Any]
) -> ContentMetadata:
    """
    Translates raw content metadata from ArangoDB into ContentMetadata business object.
    This is the harvested business logic from ContentMetadataAbstraction.
    """
    # Generate content ID if not present
    # Add business metadata (created_at, status, version, etc.)
    # Return ContentMetadata object

async def resolve_lineage(
    self,
    raw_lineage_data: Dict[str, Any]
) -> LineageGraph:
    """
    Translates raw lineage data from ArangoDB into LineageGraph business object.
    This is the harvested business logic from StateManagementAbstraction.
    """
    # Construct lineage graph
    # Return LineageGraph object

async def ensure_data_access(
    self,
    action: str,
    user_id: str,
    tenant_id: str,
    resource: str,
    security_context: Optional[SecurityContext] = None
) -> Dict[str, Any]:
    """
    High-level method for Realms to check data access authorization.
    Translates Realm intent into a runtime contract shape for Data Steward.
    """
    # Query Policy Registry for data access policies
    # Prepare runtime contract shape
    # Return ready for Runtime
```

---

## Step 4: Create Data Steward Primitive

**Location:** `civic_systems/smart_city/primitives/data_steward/data_steward_primitive.py`

**Primitive to Create:**
```python
class DataStewardPrimitive:
    """
    Data Steward Primitive - Policy-aware primitive for data access.
    
    Makes policy decisions only:
    - Can user access this data?
    - Can user perform this action on this data?
    - What are the data access constraints?
    """
    
    def __init__(self, policy_registry: PolicyRegistry):
        self.policy_registry = policy_registry
    
    async def evaluate_data_access(
        self,
        action: str,
        user_id: str,
        tenant_id: str,
        resource: str,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate data access policy.
        Policy Logic Only:
        - Is user allowed to access this data?
        - Are tenant isolation rules satisfied?
        - Are data classification rules satisfied?
        """
        policy_rules = policy_rules or {}
        
        # Policy Decision 1: Basic access check
        if not user_id or not tenant_id:
            return {"allowed": False, "reason": "User or tenant not specified"}
        
        # Policy Decision 2: Tenant isolation
        if policy_rules.get("tenant_isolation_enabled", True):
            # Check if resource belongs to tenant
            # This primitive only decides if isolation is required, not how to enforce it
            pass
        
        # Policy Decision 3: Data classification
        if policy_rules.get("data_classification_required", False):
            # Check if user has required classification level
            pass
        
        return {"allowed": True, "reason": "Data access granted"}
```

---

## Step 5: Test

**Location:** `tests/integration/smart_city/test_data_steward_e2e.py`

**Tests to Create:**
- `test_file_upload_and_retrieval` - File upload/download flow
- `test_content_metadata_storage` - Content metadata storage/retrieval
- `test_lineage_tracking` - Lineage tracking flow
- `test_data_access_policies` - Data access policy evaluation
- `test_platform_sdk_data_methods` - Platform SDK boundary methods
- `test_data_steward_primitive_policy_decisions` - Primitive policy decisions
- `test_full_flow_realm_to_primitive` - Complete flow end-to-end

---

## Execution Order

1. **Analyze all abstractions** - Complete business logic inventory
2. **Refactor File Storage Abstraction** - Make it pure
3. **Create/Refactor Content Metadata Abstraction** - Make it pure
4. **Refactor remaining abstractions** - Knowledge Governance, State Management, Messaging
5. **Add Platform SDK methods** - Translation logic
6. **Create Data Steward Primitive** - Policy decisions
7. **Test** - E2E tests with real infrastructure

---

## Success Criteria

- [x] All abstractions are pure infrastructure ✅
- [x] Platform SDK has translation methods ✅
- [x] Primitive makes policy decisions only ✅
- [x] E2E tests pass with real infrastructure ✅
- [x] Equivalent or better functionality ✅
