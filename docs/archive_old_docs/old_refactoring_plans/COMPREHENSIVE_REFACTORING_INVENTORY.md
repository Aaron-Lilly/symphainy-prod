# Comprehensive Smart City & Abstractions Refactoring Inventory

**Date:** January 2026  
**Status:** 📋 **COMPREHENSIVE INVENTORY**  
**Purpose:** Complete inventory of ALL abstractions and Smart City roles requiring refactoring

---

## Executive Summary

**Scope:**
- ✅ **17 existing abstractions** in `symphainy_platform/foundations/public_works/abstractions/`
- ❌ **6 critical missing abstractions** (events, telemetry, session, workflow, policy, messaging)
- ❌ **15+ important missing abstractions** (authorization, content metadata, semantic data, etc.)
- ✅ **8 Smart City services** (all need location change, some need refactoring)
- 🔴 **Multiple abstractions with business logic** (auth, tenant, semantic search, file storage, etc.)

**This is a significant refactoring effort covering 40+ components.**

---

## Part 1: Existing Abstractions Inventory

### Current Abstractions in `symphainy_platform/foundations/public_works/abstractions/`

| # | Abstraction | Status | Business Logic? | Needs Refactoring? | Target Location |
|---|-------------|--------|----------------|-------------------|-----------------|
| 1 | `auth_abstraction.py` | ✅ Exists | 🔴 YES | ✅ YES | Policy → Security Guard, Translation → Platform SDK |
| 2 | `tenant_abstraction.py` | ✅ Exists | 🔴 YES | ✅ YES | Policy → Security Guard/City Manager, Translation → Platform SDK |
| 3 | `file_storage_abstraction.py` | ✅ Exists | 🟡 Minor | ✅ YES | Minor fixes (content type inference) |
| 4 | `semantic_search_abstraction.py` | ✅ Exists | 🟡 Minor | ✅ YES | Don't generate document IDs |
| 5 | `state_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | Good example (pure infrastructure) |
| 6 | `service_discovery_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | Good example (pure infrastructure) |
| 7 | `ingestion_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | Good (pure infrastructure) |
| 8 | `pdf_processing_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | File processing (pure infrastructure) |
| 9 | `word_processing_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | File processing (pure infrastructure) |
| 10 | `excel_processing_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | File processing (pure infrastructure) |
| 11 | `csv_processing_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | File processing (pure infrastructure) |
| 12 | `json_processing_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | File processing (pure infrastructure) |
| 13 | `text_processing_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | File processing (pure infrastructure) |
| 14 | `image_processing_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | File processing (pure infrastructure) |
| 15 | `html_processing_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | File processing (pure infrastructure) |
| 16 | `mainframe_processing_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | File processing (pure infrastructure) |
| 17 | `kreuzberg_processing_abstraction.py` | ✅ Exists | ✅ NO | ❌ NO | File processing (pure infrastructure) |

**Summary:**
- ✅ **11 abstractions are good** (no business logic, pure infrastructure)
- 🔴 **2 abstractions have critical business logic** (auth, tenant)
- 🟡 **2 abstractions have minor business logic** (file storage, semantic search)

---

## Part 2: Missing Abstractions Inventory

### Critical Missing Abstractions (Required for Phase 2/3)

| # | Abstraction | Status in `symphainy_source` | Condition | Action |
|---|-------------|------------------------------|-----------|--------|
| 1 | **Event Management** | ✅ EXISTS | 🟡 Minor refactoring | Copy + remove `correlation_id`/`tenant_id` params |
| 2 | **Telemetry** | ✅ EXISTS | ✅ Good | Copy as-is |
| 3 | **Session** | ✅ EXISTS | 🟡 Minor refactoring | Copy + remove session data extraction |
| 4 | **Policy** | ✅ EXISTS | ✅ Good | Copy as-is |
| 5 | **Messaging** | ✅ EXISTS | 🟡 Minor refactoring | Copy + remove `correlation_id`/`tenant_id` params |
| 6 | **Workflow Orchestration** | ✅ EXISTS | 🔴 Major refactoring | Copy + remove workflow definition/execution logic |

### Important Missing Abstractions (Required for Full Functionality)

| # | Abstraction | Status in `symphainy_source` | Condition | Action |
|---|-------------|------------------------------|-----------|--------|
| 7 | **Authorization** | ✅ EXISTS | 🔴 Major refactoring | Copy + remove ALL business logic |
| 8 | **Content Metadata** | ✅ EXISTS | 🔴 Major refactoring | Copy + remove ID generation, validation, status |
| 9 | **Semantic Data** | ✅ EXISTS | 🔴 Major refactoring | Copy + remove validation, business rules |
| 10 | **Routing** | ✅ EXISTS | ✅ Good | Copy as-is |
| 11 | **Task Management** | ✅ EXISTS | 🟡 Needs review | Copy + review for business logic |
| 12 | **Observability** | ✅ EXISTS | 🟡 Needs review | Copy + review for business logic |
| 13 | **Health** | ✅ EXISTS | 🟡 Needs review | Copy + review for business logic |
| 14 | **Alert Management** | ✅ EXISTS | 🟡 Needs review | Copy + review for business logic |
| 15 | **Log Aggregation** | ✅ EXISTS | 🟡 Needs review | Copy + review for business logic |
| 16 | **Knowledge Discovery** | ✅ EXISTS | 🟡 Needs review | Copy + review for business logic |
| 17 | **Metadata Management** | ✅ EXISTS | 🟡 Needs review | Copy + review for business logic |
| 18 | **Knowledge Governance** | ✅ EXISTS | 🟡 Needs review | Copy + review for business logic |

**Summary:**
- ✅ **3 can copy as-is** (telemetry, policy, routing)
- 🟡 **9 need minor refactoring** (remove params, review for business logic)
- 🔴 **6 need major refactoring** (remove significant business logic)

---

## Part 3: Smart City Roles Inventory

### All 8 Smart City Services

| # | Service | Current Location | Target Location | Protocol? | Needs Refactoring? |
|---|---------|-----------------|-----------------|-----------|-------------------|
| 1 | **Security Guard** | `symphainy_platform/smart_city/services/security_guard/` | `civic_systems/smart_city/roles/security_guard/` | ❌ No | ✅ YES (has business logic) |
| 2 | **City Manager** | `symphainy_platform/smart_city/services/city_manager/` | `civic_systems/smart_city/roles/city_manager/` | ✅ Yes | 🟡 Minor (location only) |
| 3 | **Data Steward** | `symphainy_platform/smart_city/services/data_steward/` | `civic_systems/smart_city/roles/data_steward/` | ✅ Yes | 🟡 Minor (location only) |
| 4 | **Librarian** | `symphainy_platform/smart_city/services/librarian/` | `civic_systems/smart_city/roles/librarian/` | ✅ Yes | 🟡 Minor (location only) |
| 5 | **Traffic Cop** | `symphainy_platform/smart_city/services/traffic_cop/` | `civic_systems/smart_city/roles/traffic_cop/` | ✅ Yes | 🟡 Minor (location only) |
| 6 | **Post Office** | `symphainy_platform/smart_city/services/post_office/` | `civic_systems/smart_city/roles/post_office/` | ✅ Yes | 🟡 Minor (location only) |
| 7 | **Conductor** | `symphainy_platform/smart_city/services/conductor/` | `civic_systems/smart_city/roles/conductor/` | ✅ Yes | 🟡 Minor (location only) |
| 8 | **Nurse** | `symphainy_platform/smart_city/services/nurse/` | `civic_systems/smart_city/roles/nurse/` | ✅ Yes | 🟡 Minor (location only) |

**Summary:**
- ✅ **7 services** just need location change
- 🔴 **1 service** (Security Guard) needs major refactoring (remove business logic, add protocol)

---

## Part 4: Complete Migration Map

### Abstraction → Smart City Role / SDK / Domain Service

#### Policy Logic → Smart City Roles

| Abstraction | Policy Logic | Smart City Role | Method |
|------------|--------------|----------------|--------|
| Auth Abstraction | Auth validation | Security Guard | `evaluate_auth()` |
| Tenant Abstraction | Access validation | Security Guard | `validate_tenant_access()` |
| Tenant Abstraction | Policy enforcement | City Manager | `validate_policy()` |
| Authorization Abstraction | Permission checking | Security Guard | `check_permission()` |
| Authorization Abstraction | Access validation | Security Guard | `validate_access()` |
| Session Abstraction | Session semantics | Traffic Cop | `get_session()` |
| Event Management Abstraction | Event routing | Post Office | `publish_event()` |
| Workflow Orchestration Abstraction | Workflow primitives | Conductor | `get_saga_primitives()` |
| Policy Abstraction | Policy evaluation | City Manager | `evaluate_policy()` |

#### Translation Logic → SDKs

| Abstraction | Translation Logic | SDK | Method |
|------------|-------------------|-----|--------|
| Auth Abstraction | Tenant resolution | Platform SDK | `resolve_security_context()` |
| Auth Abstraction | Role mapping | Platform SDK | `resolve_security_context()` |
| Auth Abstraction | Permission projection | Platform SDK | `resolve_security_context()` |
| Auth Abstraction | SecurityContext creation | Platform SDK | `resolve_security_context()` |
| Tenant Abstraction | Tenant creation logic | Platform SDK | `resolve_tenant()` |
| Content Metadata Abstraction | ID generation | Realm SDK | `translate_content_intent()` |
| Content Metadata Abstraction | Validation rules | Realm SDK | `translate_content_intent()` |
| Semantic Data Abstraction | Embedding validation | Realm SDK | `translate_semantic_intent()` |
| Workflow Orchestration Abstraction | Workflow definition | Realm SDK | `translate_workflow_intent()` |

#### Business Logic → Domain Services

| Abstraction | Business Logic | Domain Service |
|------------|----------------|----------------|
| Content Metadata Abstraction | Content processing | Content Realm |
| Semantic Data Abstraction | Semantic graph operations | Content Realm |
| Workflow Orchestration Abstraction | Workflow execution | Journey Realm |

---

## Part 5: Refactoring Priority & Timeline

### Phase 1: Critical Missing Abstractions (Week 1, Days 1-3)

**Goal:** Add 6 critical abstractions needed for Phase 2/3

1. **Event Management Abstraction** (Day 1)
   - Copy from `symphainy_source`
   - Remove `correlation_id`/`tenant_id` params
   - Test is pure infrastructure

2. **Telemetry Abstraction** (Day 1)
   - Copy from `symphainy_source` (as-is)
   - Test is pure infrastructure

3. **Session Abstraction** (Day 2)
   - Copy from `symphainy_source`
   - Remove session data extraction
   - Test is pure infrastructure

4. **Policy Abstraction** (Day 2)
   - Copy from `symphainy_source` (as-is)
   - Test is pure infrastructure

5. **Messaging Abstraction** (Day 3)
   - Copy from `symphainy_source`
   - Remove `correlation_id`/`tenant_id` params
   - Test is pure infrastructure

6. **Workflow Orchestration Abstraction** (Day 3)
   - Copy from `symphainy_source`
   - Remove workflow definition/execution logic
   - Test is pure infrastructure

### Phase 2: Critical Business Logic Fixes (Week 1, Days 4-5)

**Goal:** Remove business logic from existing abstractions

7. **Auth Abstraction** (Day 4)
   - Remove tenant creation, role extraction, SecurityContext creation
   - Return raw user data only
   - Move policy logic to Security Guard
   - Move translation logic to Platform SDK

8. **Tenant Abstraction** (Day 5)
   - Remove access validation, configuration management
   - Return raw tenant data only
   - Move policy logic to Security Guard/City Manager
   - Move translation logic to Platform SDK

### Phase 3: Security Guard + Platform SDK (Week 2, Days 1-2)

**Goal:** Refactor Security Guard and create Platform SDK

9. **Security Guard Role** (Day 1)
   - Move to `civic_systems/smart_city/roles/security_guard/`
   - Implement `SmartCityRoleProtocol`
   - Add policy logic (from Auth/Tenant abstractions)
   - Remove business logic (move to Platform SDK)

10. **Platform SDK Foundation** (Day 1-2)
    - Create `civic_systems/platform_sdk/`
    - Add `resolve_security_context()` (translation logic)
    - Add `resolve_tenant()` (translation logic)
    - Test translation logic works

### Phase 4: Remaining Smart City Roles (Week 2, Days 3-5)

**Goal:** Move all Smart City roles to correct location

11. **City Manager** (Day 3)
    - Move to `civic_systems/smart_city/roles/city_manager/`
    - Ensure uses abstractions (not adapters)
    - Add policy logic (from Tenant Abstraction)

12. **Data Steward** (Day 3)
    - Move to `civic_systems/smart_city/roles/data_steward/`
    - Ensure uses abstractions (not adapters)

13. **Librarian** (Day 4)
    - Move to `civic_systems/smart_city/roles/librarian/`
    - Ensure uses abstractions (not adapters)

14. **Traffic Cop** (Day 4)
    - Move to `civic_systems/smart_city/roles/traffic_cop/`
    - Ensure uses abstractions (not adapters)

15. **Post Office** (Day 5)
    - Move to `civic_systems/smart_city/roles/post_office/`
    - Ensure uses abstractions (not adapters)

16. **Conductor** (Day 5)
    - Move to `civic_systems/smart_city/roles/conductor/`
    - Ensure uses abstractions (not adapters)

17. **Nurse** (Day 5)
    - Move to `civic_systems/smart_city/roles/nurse/`
    - Ensure uses abstractions (not adapters)

### Phase 5: Minor Abstraction Fixes (Week 3, Days 1-2)

**Goal:** Fix minor business logic issues

18. **File Storage Abstraction** (Day 1)
    - Make content type inference optional
    - Accept metadata as-is

19. **Semantic Search Abstraction** (Day 2)
    - Don't generate document IDs
    - Require document ID as parameter

### Phase 6: Important Missing Abstractions (Week 3, Days 3-5)

**Goal:** Add important abstractions for full functionality

20. **Authorization Abstraction** (Day 3)
    - Copy from `symphainy_source`
    - Remove ALL business logic
    - Return raw authorization data

21. **Content Metadata Abstraction** (Day 4)
    - Copy from `symphainy_source`
    - Remove ID generation, validation, status
    - Return raw metadata

22. **Semantic Data Abstraction** (Day 5)
    - Copy from `symphainy_source`
    - Remove validation, business rules
    - Return raw semantic data

### Phase 7: Remaining Abstractions (Week 4+)

**Goal:** Add remaining abstractions as needed

23-30. **Routing, Task Management, Observability, Health, Alert Management, Log Aggregation, Knowledge Discovery, Metadata Management, Knowledge Governance**
    - Copy from `symphainy_source`
    - Review for business logic
    - Refactor as needed

---

## Part 6: Complete Task List

### Assessment Phase (Days 1-2)

- [x] Assess current Smart City services
- [ ] Complete abstraction inventory (this document)
- [ ] Review each abstraction for business logic
- [ ] Create detailed migration map for ALL components

### Refactoring Phase (Weeks 1-4)

**Week 1: Critical Abstractions + Business Logic Fixes**
- [ ] Add 6 critical missing abstractions
- [ ] Fix Auth Abstraction (remove business logic)
- [ ] Fix Tenant Abstraction (remove business logic)

**Week 2: Smart City Migration + Platform SDK**
- [ ] Refactor Security Guard (move + protocol + policy logic)
- [ ] Create Platform SDK foundation
- [ ] Move all Smart City roles to correct location

**Week 3: Minor Fixes + Important Abstractions**
- [ ] Fix File Storage Abstraction
- [ ] Fix Semantic Search Abstraction
- [ ] Add Authorization Abstraction
- [ ] Add Content Metadata Abstraction
- [ ] Add Semantic Data Abstraction

**Week 4+: Remaining Abstractions**
- [ ] Add remaining abstractions as needed

### Validation Phase (Ongoing)

- [ ] Ensure Runtime calls Smart City via SDK (not directly)
- [ ] Ensure Runtime calls Curator via SDK (not Consul directly)
- [ ] Run all validation tests
- [ ] Update documentation

---

## Summary

**Total Components to Refactor:**
- ✅ **17 existing abstractions** (4 need refactoring)
- ❌ **6 critical missing abstractions** (need to add)
- ❌ **15+ important missing abstractions** (need to add)
- ✅ **8 Smart City services** (all need location change, 1 needs major refactoring)
- ✅ **1 Platform SDK** (need to create)
- ✅ **1 Realm SDK** (need to create)

**Total: 40+ components**

**Timeline: 4+ weeks for complete refactoring**

**This is a comprehensive refactoring effort, but it's necessary for the architecture to work correctly.**
