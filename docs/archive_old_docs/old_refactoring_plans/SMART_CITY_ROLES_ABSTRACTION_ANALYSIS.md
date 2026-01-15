# Smart City Roles - Public Works Abstraction Analysis

**Date:** January 2026  
**Status:** 🔴 **COMPREHENSIVE ANALYSIS**  
**Purpose:** Identify abstraction requirements and business logic issues for each Smart City role

---

## Executive Summary

**The Problem:** Each Smart City role needs specific Public Works abstractions, but:
- ❌ Some abstractions are **missing** (events, messaging, telemetry, workflow)
- ❌ Some abstractions contain **business logic** (should be pure infrastructure)
- ❌ Some abstractions are **not swappable** (tightly coupled to specific technologies)

**The Fix:** 
1. **Add missing abstractions** (events, messaging, telemetry, workflow, session)
2. **Refactor existing abstractions** to remove business logic
3. **Ensure abstractions are swappable** (technology-agnostic interfaces)

---

## Analysis by Smart City Role

### 1. Security Guard (Identity, authN/Z, zero trust)

**Responsibility:** Identity, authentication, authorization, zero trust

**Required Abstractions:**

1. ✅ **Auth Abstraction** - Authentication (EXISTS, but needs refactoring)
   - **Issue:** Contains business logic (tenant creation, role extraction)
   - **Fix:** Return raw auth provider data, move business logic to Security Guard

2. ❌ **Authorization Abstraction** - Authorization (MISSING)
   - **Needed:** Permission checking, role resolution
   - **Should be:** Pure infrastructure (Supabase → Auth0 → AWS IAM)
   - **Business Logic:** Permission model, role hierarchy (belongs in Security Guard)

3. ✅ **Tenant Abstraction** - Tenant data (EXISTS, but needs refactoring)
   - **Issue:** Contains business logic (access validation)
   - **Fix:** Return raw tenant data, move validation to Security Guard

**Current State:**
- ✅ Auth Abstraction exists but has business logic
- ✅ Tenant Abstraction exists but has business logic
- ❌ Authorization Abstraction missing

**Refactoring Needed:**
- **Auth Abstraction:** Remove tenant creation, role extraction → return raw data
- **Tenant Abstraction:** Remove access validation → return raw data
- **Security Guard:** Add business logic (policy validation, role resolution, access validation)

---

### 2. Data Steward (Data boundaries, contracts, provenance)

**Responsibility:** Data boundaries, contracts, provenance tracking

**Required Abstractions:**

1. ✅ **File Storage Abstraction** - File operations (EXISTS, minor issues)
   - **Status:** Mostly OK, minor business logic (content type inference, metadata structuring)
   - **Fix:** Make content type inference optional, accept metadata as-is

2. ❌ **Content Metadata Abstraction** - Content metadata (MISSING in `symphainy_source_code`)
   - **Needed:** Semantic embeddings, content metadata, lineage
   - **Exists in:** `symphainy_source` (ArangoDB-based)
   - **Should be:** Pure infrastructure (ArangoDB → MongoDB → PostgreSQL)

3. ❌ **Metadata Management Abstraction** - Generic metadata (MISSING in `symphainy_source_code`)
   - **Needed:** Generic metadata operations, provenance tracking
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure

4. ❌ **Knowledge Governance Abstraction** - Data governance (MISSING in `symphainy_source_code`)
   - **Needed:** Policies, compliance, quality metrics
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure (but governance rules belong in Data Steward)

5. ✅ **State Abstraction** - State storage (EXISTS, mostly OK)
   - **Status:** Pure infrastructure, good example
   - **Use Case:** Store data provenance, lineage

**Current State:**
- ✅ File Storage Abstraction exists (minor issues)
- ✅ State Abstraction exists (good)
- ❌ Content Metadata Abstraction missing
- ❌ Metadata Management Abstraction missing
- ❌ Knowledge Governance Abstraction missing

**Refactoring Needed:**
- **File Storage Abstraction:** Make content type inference optional
- **Add Missing Abstractions:** Content Metadata, Metadata Management, Knowledge Governance
- **Data Steward:** Add business logic (data boundaries, contracts, provenance rules)

---

### 3. Librarian (Semantic schemas & meaning)

**Responsibility:** Semantic schemas, meaning, semantic search

**Required Abstractions:**

1. ✅ **Semantic Search Abstraction** - Search operations (EXISTS, minor issues)
   - **Issue:** Generates document IDs if missing (business logic)
   - **Fix:** Require document ID as parameter, don't generate

2. ❌ **Semantic Data Abstraction** - Semantic data operations (MISSING in `symphainy_source_code`)
   - **Needed:** Semantic embeddings, semantic graph operations
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure (Meilisearch → Elasticsearch → Pinecone)

3. ❌ **Content Metadata Abstraction** - Content metadata (MISSING in `symphainy_source_code`)
   - **Needed:** Semantic embeddings storage, content schemas
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure

4. ❌ **Knowledge Discovery Abstraction** - Knowledge discovery (MISSING in `symphainy_source_code`)
   - **Needed:** Knowledge graph operations, semantic relationships
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure

**Current State:**
- ✅ Semantic Search Abstraction exists (minor issues)
- ❌ Semantic Data Abstraction missing
- ❌ Content Metadata Abstraction missing
- ❌ Knowledge Discovery Abstraction missing

**Refactoring Needed:**
- **Semantic Search Abstraction:** Don't generate document IDs, require as parameter
- **Add Missing Abstractions:** Semantic Data, Content Metadata, Knowledge Discovery
- **Librarian:** Add business logic (semantic schema management, meaning resolution)

---

### 4. Traffic Cop (Sessions, execution IDs, correlation)

**Responsibility:** Sessions, execution IDs, correlation

**Required Abstractions:**

1. ✅ **State Abstraction** - Session state storage (EXISTS, mostly OK)
   - **Status:** Pure infrastructure, good example
   - **Use Case:** Store session data, execution IDs

2. ❌ **Session Abstraction** - Session management (MISSING in `symphainy_source_code`)
   - **Needed:** Session lifecycle, session data operations
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure (Redis → Memcached → DynamoDB)

3. ❌ **Session Management Abstraction** - Session lifecycle (MISSING in `symphainy_source_code`)
   - **Needed:** Session creation, expiration, cleanup
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure

**Current State:**
- ✅ State Abstraction exists (good)
- ❌ Session Abstraction missing
- ❌ Session Management Abstraction missing

**Refactoring Needed:**
- **Add Missing Abstractions:** Session, Session Management
- **Traffic Cop:** Add business logic (session semantics, execution ID generation, correlation)

---

### 5. Post Office (Event routing & ordering)

**Responsibility:** Event routing, ordering, messaging

**Required Abstractions:**

1. ❌ **Event Management Abstraction** - Event publishing/subscription (MISSING in `symphainy_source_code`)
   - **Needed:** Event publishing, subscription, routing
   - **Exists in:** `symphainy_source` (Redis-based)
   - **Should be:** Pure infrastructure (Redis → Kafka → RabbitMQ → AWS EventBridge)

2. ❌ **Messaging Abstraction** - Message queue operations (MISSING in `symphainy_source_code`)
   - **Needed:** Message publishing, consumption, queue management
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure (Redis → Kafka → RabbitMQ → SQS)

3. ❌ **Routing Abstraction** - Route discovery/management (MISSING in `symphainy_source_code`)
   - **Needed:** Route discovery, route management
   - **Exists in:** `symphainy_source` (Traefik-based)
   - **Should be:** Pure infrastructure (Traefik → nginx → Istio)

**Current State:**
- ❌ Event Management Abstraction missing
- ❌ Messaging Abstraction missing
- ❌ Routing Abstraction missing

**Refactoring Needed:**
- **Add Missing Abstractions:** Event Management, Messaging, Routing
- **Post Office:** Add business logic (event routing rules, ordering guarantees, delivery semantics)

---

### 6. Conductor (Workflow & saga primitives)

**Responsibility:** Workflow orchestration, saga primitives

**Required Abstractions:**

1. ❌ **Workflow Orchestration Abstraction** - Workflow operations (MISSING in `symphainy_source_code`)
   - **Needed:** Workflow definition, execution, state management
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure (custom → Temporal → AWS Step Functions)

2. ❌ **Task Management Abstraction** - Task operations (MISSING in `symphainy_source_code`)
   - **Needed:** Task creation, status tracking, task queues
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure

3. ✅ **State Abstraction** - Saga state storage (EXISTS, mostly OK)
   - **Status:** Pure infrastructure, good example
   - **Use Case:** Store saga state, workflow state

**Current State:**
- ✅ State Abstraction exists (good)
- ❌ Workflow Orchestration Abstraction missing
- ❌ Task Management Abstraction missing

**Refactoring Needed:**
- **Add Missing Abstractions:** Workflow Orchestration, Task Management
- **Conductor:** Add business logic (saga patterns, workflow semantics, compensation logic)

---

### 7. Nurse (Telemetry, retries, self-healing)

**Responsibility:** Telemetry, retries, self-healing

**Required Abstractions:**

1. ❌ **Telemetry Abstraction** - Telemetry collection (MISSING in `symphainy_source_code`)
   - **Needed:** Metrics, traces, spans collection
   - **Exists in:** `symphainy_source` (OpenTelemetry-based)
   - **Should be:** Pure infrastructure (OpenTelemetry → Datadog → New Relic)

2. ❌ **Observability Abstraction** - Observability data storage (MISSING in `symphainy_source_code`)
   - **Needed:** Observability data storage, querying
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure (Tempo → Jaeger → AWS X-Ray)

3. ❌ **Health Abstraction** - Health checks (MISSING in `symphainy_source_code`)
   - **Needed:** Health check operations, health status
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure

4. ❌ **Alert Management Abstraction** - Alert operations (MISSING in `symphainy_source_code`)
   - **Needed:** Alert creation, alert routing, alert management
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure (Prometheus → Datadog → PagerDuty)

5. ❌ **Log Aggregation Abstraction** - Log operations (MISSING in `symphainy_source_code`)
   - **Needed:** Log collection, log querying, log aggregation
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure (Loki → ELK → CloudWatch)

**Current State:**
- ❌ Telemetry Abstraction missing
- ❌ Observability Abstraction missing
- ❌ Health Abstraction missing
- ❌ Alert Management Abstraction missing
- ❌ Log Aggregation Abstraction missing

**Refactoring Needed:**
- **Add Missing Abstractions:** Telemetry, Observability, Health, Alert Management, Log Aggregation
- **Nurse:** Add business logic (retry policies, self-healing rules, alert routing)

---

### 8. City Manager (Global policy, tenancy, escalation)

**Responsibility:** Global policy, tenancy, escalation

**Required Abstractions:**

1. ✅ **Tenant Abstraction** - Tenant data (EXISTS, but needs refactoring)
   - **Issue:** Contains business logic (access validation, configuration)
   - **Fix:** Return raw tenant data, move business logic to City Manager

2. ❌ **Policy Abstraction** - Policy engine operations (MISSING in `symphainy_source_code`)
   - **Needed:** Policy storage, policy evaluation, policy management
   - **Exists in:** `symphainy_source`
   - **Should be:** Pure infrastructure (but policy rules belong in City Manager)

3. ✅ **Auth Abstraction** - User data (EXISTS, but needs refactoring)
   - **Issue:** Contains business logic (tenant creation, role assignment)
   - **Fix:** Return raw user data, move business logic to City Manager

4. ✅ **State Abstraction** - Policy state storage (EXISTS, mostly OK)
   - **Status:** Pure infrastructure, good example
   - **Use Case:** Store policy state, tenant configuration

**Current State:**
- ✅ Tenant Abstraction exists but has business logic
- ✅ Auth Abstraction exists but has business logic
- ✅ State Abstraction exists (good)
- ❌ Policy Abstraction missing

**Refactoring Needed:**
- **Tenant Abstraction:** Remove access validation, configuration → return raw data
- **Auth Abstraction:** Remove tenant creation, role assignment → return raw data
- **Add Missing Abstraction:** Policy
- **City Manager:** Add business logic (global policy, tenant management, escalation rules)

---

## Summary: Missing Abstractions

### Critical Missing Abstractions (Required for Phase 2/3)

1. ❌ **Event Management Abstraction** - Post Office
2. ❌ **Messaging Abstraction** - Post Office
3. ❌ **Telemetry Abstraction** - Nurse
4. ❌ **Session Abstraction** - Traffic Cop
5. ❌ **Workflow Orchestration Abstraction** - Conductor
6. ❌ **Policy Abstraction** - City Manager

### Important Missing Abstractions (Required for Full Functionality)

7. ❌ **Authorization Abstraction** - Security Guard
8. ❌ **Content Metadata Abstraction** - Data Steward, Librarian
9. ❌ **Semantic Data Abstraction** - Librarian
10. ❌ **Routing Abstraction** - Post Office
11. ❌ **Task Management Abstraction** - Conductor
12. ❌ **Observability Abstraction** - Nurse
13. ❌ **Health Abstraction** - Nurse
14. ❌ **Alert Management Abstraction** - Nurse
15. ❌ **Log Aggregation Abstraction** - Nurse

---

## Summary: Business Logic Issues

### Critical Issues (Block Phase 2/3)

1. 🔴 **Auth Abstraction** - Creates tenants, manages relationships, extracts roles
2. 🔴 **Tenant Abstraction** - Validates access, manages configuration

### Moderate Issues (Should Fix)

3. 🟡 **Semantic Search Abstraction** - Generates document IDs
4. 🟡 **File Storage Abstraction** - Infers content types, structures metadata

### Good Examples (No Issues)

5. ✅ **State Abstraction** - Pure infrastructure
6. ✅ **Service Discovery Abstraction** - Pure infrastructure (minor validation OK)

---

## Refactoring Priority

### Phase 1: Critical Missing Abstractions (Week 1)

1. **Event Management Abstraction** - Copy from `symphainy_source`, ensure pure infrastructure
2. **Telemetry Abstraction** - Copy from `symphainy_source`, ensure pure infrastructure
3. **Session Abstraction** - Copy from `symphainy_source`, ensure pure infrastructure
4. **Policy Abstraction** - Copy from `symphainy_source`, ensure pure infrastructure

### Phase 2: Critical Business Logic Fixes (Week 1-2)

5. **Auth Abstraction** - Remove business logic, return raw data
6. **Tenant Abstraction** - Remove business logic, return raw data

### Phase 3: Important Missing Abstractions (Week 2-3)

7. **Messaging Abstraction** - Copy from `symphainy_source`
8. **Workflow Orchestration Abstraction** - Copy from `symphainy_source`
9. **Authorization Abstraction** - Copy from `symphainy_source`
10. **Content Metadata Abstraction** - Copy from `symphainy_source`

### Phase 4: Moderate Fixes (Week 3)

11. **Semantic Search Abstraction** - Don't generate IDs
12. **File Storage Abstraction** - Make content type inference optional

### Phase 5: Remaining Abstractions (Week 4+)

13. **Routing Abstraction** - Copy from `symphainy_source`
14. **Task Management Abstraction** - Copy from `symphainy_source`
15. **Observability Abstraction** - Copy from `symphainy_source`
16. **Health Abstraction** - Copy from `symphainy_source`
17. **Alert Management Abstraction** - Copy from `symphainy_source`
18. **Log Aggregation Abstraction** - Copy from `symphainy_source`
19. **Semantic Data Abstraction** - Copy from `symphainy_source`
20. **Knowledge Discovery Abstraction** - Copy from `symphainy_source`

---

## Conclusion

**You are absolutely right - there's a lot more to unpack.**

**Critical Findings:**
- ❌ **6 critical abstractions missing** (events, telemetry, session, workflow, policy, messaging)
- 🔴 **2 critical business logic issues** (auth, tenant)
- 🟡 **2 moderate business logic issues** (semantic search, file storage)
- ❌ **15+ important abstractions missing** for full functionality

**Impact:**
- **Blocks Phase 2/3** - Runtime and Smart City roles can't function without these abstractions
- **Prevents swappability** - Business logic in abstractions makes them not swappable
- **Violates architecture** - Abstractions should be pure infrastructure

**Recommendation:**
1. **Start with Phase 1** - Add 4 critical missing abstractions
2. **Fix Phase 2** - Remove business logic from Auth and Tenant abstractions
3. **Continue with Phase 3+** - Add remaining abstractions as needed

**This is a significant refactoring effort, but it's necessary for the architecture to work correctly.**
