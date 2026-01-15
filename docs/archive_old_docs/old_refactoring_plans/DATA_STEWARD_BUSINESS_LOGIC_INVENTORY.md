# Data Steward Business Logic Inventory

**Date:** January 13, 2026  
**Status:** 📋 **ANALYSIS COMPLETE**  
**Purpose:** Complete inventory of business logic to move from abstractions to Platform SDK

---

## Summary

Found **5 abstractions** used by Data Steward, all containing business logic that needs to be moved to Platform SDK.

---

## 1. File Storage Abstraction

**Location (New Codebase):** `symphainy_platform/foundations/public_works/abstractions/file_storage_abstraction.py`

**Business Logic Found:**
- ❌ File hash calculation (`hashlib.sha256`)
- ❌ Content type inference (extension → MIME type mapping)
- ❌ File ID generation (`generate_session_id()`)
- ❌ Metadata enhancement:
  - `created_at`, `updated_at` timestamps
  - `status` defaulting to "uploaded"
  - `deleted` defaulting to False

**Methods with Business Logic:**
- `upload_file()` - Lines 68-141
- `delete_file()` - Lines 170-205 (soft delete logic)

**What Should Return:**
- Raw GCS upload result
- Raw Supabase metadata result
- No business logic, no defaults

---

## 2. File Management Abstraction (Old Codebase Reference)

**Location (Old Codebase):** `symphainy_source/.../file_management_abstraction_gcs.py`

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

**Methods with Business Logic:**
- `create_file()` - Lines 68-151
- `list_files()` - Lines 269-299

**What Should Return:**
- Raw GCS result
- Raw Supabase result
- No business logic

---

## 3. Content Metadata Abstraction

**Location (Old Codebase):** `symphainy_source/.../content_metadata_abstraction.py`

**Business Logic Found:**
- ❌ Content ID generation (UUID if not provided) - Line 66
- ❌ Field validation (required fields: `file_uuid`, `content_type`) - Lines 60-63
- ❌ Business metadata enhancement:
  - `created_at`, `updated_at` timestamps - Lines 72-73
  - `status` defaulting to "active" - Line 74
  - `version` defaulting to 1 - Line 75
  - `analysis_status` defaulting to "pending" - Line 76
- ❌ Relationship checking before deletion (business rule) - Lines 153-157
- ❌ Default status filtering in `search_content_metadata()` - Lines 184-185

**Methods with Business Logic:**
- `create_content_metadata()` - Lines 56-93
- `delete_content_metadata()` - Lines 145-175
- `search_content_metadata()` - Lines 177-199

**What Should Return:**
- Raw ArangoDB document data
- No business logic

---

## 4. Knowledge Governance Abstraction

**Location (Old Codebase):** `symphainy_source/.../knowledge_governance_abstraction.py`

**Business Logic Found:**
- ❌ Policy validation (`_validate_policy_data()`) - Line 77
- ❌ Policy application logic (creates relationships) - Lines 208-253
- ❌ Status filtering - Lines 196-198
- ❌ Business metadata enhancement:
  - `created_at` timestamps - Line 97
  - `status` defaulting to "active" - Line 96

**Methods with Business Logic:**
- `create_governance_policy()` - Lines 64-113
- `apply_governance_policy()` - Lines 208-253
- `get_governance_policies()` - Lines 183-206

**What Should Return:**
- Raw policy data from adapters
- No business logic

---

## 5. State Management Abstraction (for Lineage)

**Location (New Codebase):** `symphainy_platform/foundations/public_works/abstractions/state_abstraction.py`

**Business Logic Found:**
- ❌ Backend selection logic (Redis vs ArangoDB) - Lines 75-83
- ❌ Metadata enhancement:
  - `created_at` timestamps - Line 91
  - `strategy` field - Line 92

**Location (Old Codebase):** `symphainy_source/.../state_management_abstraction.py`

**Additional Business Logic:**
- ❌ State storage configuration (collection names, prefixes)
- ❌ Memory cache management

**What Should Return:**
- Raw state data from adapters
- No business logic

**Note:** Lineage graph construction is in Data Steward service layer (not abstraction), so that's OK.

---

## 6. Messaging Abstraction

**Status:** Need to check if exists and what business logic it contains

---

## Migration Map

### Business Logic → Platform SDK

| Business Logic | Current Location | Move To Platform SDK |
|----------------|------------------|----------------------|
| File UUID/ID generation | File Storage/Management Abstraction | `resolve_file_metadata()` |
| File hash calculation | File Storage Abstraction | `resolve_file_metadata()` |
| Content type inference | File Storage Abstraction | `resolve_file_metadata()` |
| Metadata enhancement (timestamps, status) | All abstractions | `resolve_file_metadata()`, `resolve_content_metadata()` |
| Field validation | All abstractions | Platform SDK (before calling abstractions) |
| Content ID generation | Content Metadata Abstraction | `resolve_content_metadata()` |
| Relationship checking | Content Metadata Abstraction | Platform SDK (before deletion) |
| Policy validation | Knowledge Governance Abstraction | Platform SDK (before calling abstraction) |
| Backend selection | State Management Abstraction | Platform SDK (or remove - let abstraction decide) |

### Policy Logic → Data Steward Primitive

| Policy Logic | Current Location | Move To Primitive |
|--------------|------------------|-------------------|
| Data access decisions | Data Steward service | `evaluate_data_access()` |
| Tenant isolation checks | Data Steward service | `evaluate_data_access()` |
| Data classification checks | Data Steward service | `evaluate_data_access()` |

---

## Next Steps

1. ✅ Complete inventory (this document)
2. 🔄 Refactor File Storage Abstraction
3. 🔄 Create/Refactor Content Metadata Abstraction
4. 🔄 Refactor Knowledge Governance Abstraction
5. 🔄 Refactor State Management Abstraction
6. 🔄 Add Platform SDK methods
7. 🔄 Create Data Steward Primitive
8. 🔄 Test
