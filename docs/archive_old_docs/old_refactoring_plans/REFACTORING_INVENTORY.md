# Complete Refactoring Inventory

**Date:** January 2026  
**Status:** 📋 **INVENTORY IN PROGRESS**  
**Purpose:** Complete inventory of Smart City services and abstractions from symphainy_source

---

## Smart City Services Inventory (8 Services)

### 1. Security Guard
**Location (old):** `/symphainy_source/symphainy-platform/backend/smart_city/services/security_guard/`  
**Target (new):** `civic_systems/smart_city/roles/security_guard/`

**Micro-Modules:**
- `initialization.py` - Security capabilities setup
- `authentication.py` - Token validation, user authentication (HAS BUSINESS LOGIC)
- `orchestration.py` - Policy enforcement orchestration
- `soa_mcp.py` - SOA API and MCP tool exposure
- `utilities.py` - Helper functions
- `authorization_module.py` - Authorization logic
- `session_management_module.py` - Session management
- `security_context_provider_module.py` - Security context creation (HAS BUSINESS LOGIC)

**Infrastructure Abstractions Used:**
- `auth_abstraction` (AuthenticationAbstraction)
- `tenant_abstraction` (TenancyAbstraction)
- `authorization_abstraction` (AuthorizationAbstraction)
- `session_abstraction` (SessionAbstraction)

**SOA APIs:**
- `authenticate()`, `validate_token()`, `check_permission()`, `validate_tenant_access()`

**MCP Tools:**
- `security_check`, `tenant_validation`, `policy_enforcement`

**Business Logic to Move to SDK:**
- Tenant resolution (`_resolve_tenant()`)
- Role/permission extraction (`_resolve_roles_permissions()`)
- SecurityContext creation (from raw auth data)
- Session creation with user context

**Policy Logic to Keep in Role:**
- `evaluate_auth()` - Policy decision (allowed/denied)
- `validate_tenant_access()` - Policy decision
- `check_permission()` - Policy decision

---

### 2. City Manager
**Location (old):** `/symphainy_source/symphainy-platform/backend/smart_city/services/city_manager/`  
**Target (new):** `civic_systems/smart_city/roles/city_manager/`

**Micro-Modules:**
- `initialization.py` - Platform initialization
- `bootstrapping.py` - Platform bootstrap
- `realm_orchestration.py` - Realm orchestration
- `platform_governance.py` - Platform governance
- `realm_activation_plan.py` - Realm activation
- `data_path_bootstrap.py` - Data path bootstrap
- `service_management.py` - Service management

**Infrastructure Abstractions Used:**
- `session_abstraction`
- `state_management_abstraction`
- `messaging_abstraction`
- `event_management_abstraction`
- `file_management_abstraction`
- `analytics_abstraction`
- `health_abstraction`
- `telemetry_abstraction`

**SOA APIs:**
- `bootstrap_platform()`, `activate_realm()`, `manage_services()`

**MCP Tools:**
- `platform_bootstrap`, `realm_activation`, `service_management`

**Business Logic to Move to SDK:**
- Platform bootstrap orchestration
- Realm activation logic
- Service management coordination

**Policy Logic to Keep in Role:**
- `validate_policy()` - Policy decision
- `govern_platform()` - Governance decision

---

### 3. Traffic Cop
**Location (old):** `/symphainy_source/symphainy-platform/backend/smart_city/services/traffic_cop/`  
**Target (new):** `civic_systems/smart_city/roles/traffic_cop/`

**Micro-Modules:**
- `initialization.py` - Traffic Cop initialization
- `session_management.py` - Session management
- `websocket_session_management.py` - WebSocket session management
- `load_balancing.py` - Load balancing
- `rate_limiting.py` - Rate limiting
- `api_routing.py` - API routing
- `state_sync.py` - State synchronization
- `analytics.py` - Traffic analytics
- `soa_mcp.py` - SOA API and MCP tool exposure

**Infrastructure Abstractions Used:**
- `session_abstraction`
- `state_management_abstraction`
- `messaging_abstraction`
- `file_management_abstraction`
- `analytics_abstraction`

**SOA APIs:**
- `create_session()`, `manage_session()`, `route_request()`, `balance_load()`

**MCP Tools:**
- `session_management`, `api_routing`, `load_balancing`

**Business Logic to Move to SDK:**
- Session creation with context
- Request routing logic
- Load balancing decisions

**Policy Logic to Keep in Role:**
- `validate_session()` - Policy decision
- `validate_rate_limit()` - Policy decision
- `validate_routing()` - Policy decision

---

### 4. Post Office
**Location (old):** `/symphainy_source/symphainy-platform/backend/smart_city/services/post_office/`  
**Target (new):** `civic_systems/smart_city/roles/post_office/`

**Micro-Modules:**
- `initialization.py` - Post Office initialization
- `event_routing.py` - Event routing
- `messaging.py` - Messaging
- `soa_mcp.py` - SOA API and MCP tool exposure

**Infrastructure Abstractions Used:**
- `messaging_abstraction`
- `event_management_abstraction`
- `session_abstraction`

**SOA APIs:**
- `publish_event()`, `send_message()`, `route_event()`

**MCP Tools:**
- `event_publishing`, `message_sending`, `event_routing`

**Business Logic to Move to SDK:**
- Event routing logic
- Message delivery coordination

**Policy Logic to Keep in Role:**
- `validate_event_publish()` - Policy decision
- `validate_message_send()` - Policy decision

---

### 5. Conductor
**Location (old):** `/symphainy_source/symphainy-platform/backend/smart_city/services/conductor/`  
**Target (new):** `civic_systems/smart_city/roles/conductor/`

**Micro-Modules:**
- (Need to check what modules exist)

**Infrastructure Abstractions Used:**
- `workflow_orchestration_abstraction`
- `state_management_abstraction`

**SOA APIs:**
- `orchestrate_workflow()`, `manage_saga()`

**MCP Tools:**
- `workflow_orchestration`, `saga_management`

**Business Logic to Move to SDK:**
- Workflow orchestration logic
- Saga coordination

**Policy Logic to Keep in Role:**
- `validate_workflow()` - Policy decision
- `validate_saga()` - Policy decision

---

### 6. Librarian
**Location (old):** `/symphainy_source/symphainy-platform/backend/smart_city/services/librarian/`  
**Target (new):** `civic_systems/smart_city/roles/librarian/`

**Micro-Modules:**
- `initialization.py` - Librarian initialization
- `semantic_data_storage.py` - Semantic data storage
- `content_metadata_storage.py` - Content metadata storage
- `search.py` - Search functionality
- `knowledge_management.py` - Knowledge management
- `utilities.py` - Helper functions
- `soa_mcp.py` - SOA API and MCP tool exposure

**Infrastructure Abstractions Used:**
- `semantic_search_abstraction`
- `semantic_data_abstraction`
- `content_metadata_abstraction`

**SOA APIs:**
- `search()`, `index_document()`, `govern_knowledge()`

**MCP Tools:**
- `semantic_search`, `knowledge_governance`

**Business Logic to Move to SDK:**
- Search result formatting
- Knowledge graph operations

**Policy Logic to Keep in Role:**
- `validate_search()` - Policy decision
- `validate_knowledge_access()` - Policy decision

---

### 7. Data Steward
**Location (old):** `/symphainy_source/symphainy-platform/backend/smart_city/services/data_steward/`  
**Target (new):** `civic_systems/smart_city/roles/data_steward/`

**Micro-Modules:**
- `initialization.py` - Data Steward initialization
- `file_lifecycle.py` - File lifecycle management (HAS BUSINESS LOGIC)
- `lineage_tracking.py` - Lineage tracking
- `policy_management.py` - Policy management
- `data_governance.py` - Data governance
- `parsed_file_processing.py` - Parsed file processing
- `data_query.py` - Data query
- `write_ahead_logging.py` - Write-ahead logging
- `soa_mcp.py` - SOA API and MCP tool exposure

**Infrastructure Abstractions Used:**
- `file_management_abstraction` (FileStorageAbstraction)
- `content_metadata_abstraction`
- `state_management_abstraction`
- `messaging_abstraction`

**SOA APIs:**
- `manage_data_lifecycle()`, `enforce_data_policy()`, `track_lineage()`

**MCP Tools:**
- `data_lifecycle`, `data_governance`, `lineage_tracking`

**Business Logic to Move to SDK:**
- File lifecycle orchestration
- Data policy enforcement logic
- Lineage tracking coordination

**Policy Logic to Keep in Role:**
- `validate_data_access()` - Policy decision
- `validate_data_policy()` - Policy decision

---

### 8. Nurse
**Location (old):** `/symphainy_source/symphainy-platform/backend/smart_city/services/nurse/`  
**Target (new):** `civic_systems/smart_city/roles/nurse/`

**Micro-Modules:**
- `initialization.py` - Nurse initialization
- `observability.py` - Observability
- `telemetry_health.py` - Telemetry and health
- `tracing.py` - Tracing
- `orchestration.py` - Orchestration
- `diagnostics.py` - Diagnostics
- `alert_management.py` - Alert management
- `utilities.py` - Helper functions
- `soa_mcp.py` - SOA API and MCP tool exposure

**Infrastructure Abstractions Used:**
- `telemetry_abstraction`
- `health_abstraction`
- `observability_abstraction`

**SOA APIs:**
- `collect_telemetry()`, `check_health()`, `trace_execution()`

**MCP Tools:**
- `telemetry_collection`, `health_monitoring`, `tracing`

**Business Logic to Move to SDK:**
- Telemetry aggregation
- Health check coordination

**Policy Logic to Keep in Role:**
- `validate_telemetry()` - Policy decision
- `validate_health()` - Policy decision

---

## Infrastructure Abstractions Inventory

### Critical Abstractions (Need Refactoring)

1. **Auth Abstraction** (`auth_abstraction.py`)
   - **Business Logic:** Creates tenants, extracts roles, creates SecurityContext
   - **Fix:** Return raw user data only, move business logic to SDK

2. **Tenant Abstraction** (`tenant_abstraction.py`)
   - **Business Logic:** Validates access, manages configuration
   - **Fix:** Return raw tenant data only, move business logic to SDK

3. **Content Metadata Abstraction** (`content_metadata_abstraction.py`)
   - **Business Logic:** Generates IDs, validates content, manages status
   - **Fix:** Return raw metadata only, move business logic to SDK

4. **Semantic Data Abstraction** (`semantic_data_abstraction.py`)
   - **Business Logic:** Validates embeddings, applies business rules
   - **Fix:** Return raw semantic data only, move business logic to SDK

5. **Workflow Orchestration Abstraction** (`workflow_orchestration_abstraction.py`)
   - **Business Logic:** Defines workflows, executes workflows
   - **Fix:** Return raw workflow data only, move business logic to SDK

6. **Authorization Abstraction** (`authorization_abstraction.py`)
   - **Business Logic:** Checks permissions, validates access
   - **Fix:** Return raw authorization data only, move business logic to SDK

### Missing Abstractions (Need to Create)

1. **Event Management Abstraction** - For Post Office
2. **Messaging Abstraction** - For Post Office
3. **Session Abstraction** - For Traffic Cop
4. **Telemetry Abstraction** - For Nurse
5. **Health Abstraction** - For Nurse
6. **Policy Abstraction** - For City Manager
7. **Workflow Orchestration Abstraction** - For Conductor (may exist, need to check)

---

## Migration Map

### Policy Logic → Smart City Roles
- Auth policy decisions → Security Guard (`evaluate_auth()`, `validate_tenant_access()`)
- Platform policy decisions → City Manager (`validate_policy()`)
- Data access policy → Data Steward (`validate_data_access()`)
- Search policy → Librarian (`validate_search()`)
- Event policy → Post Office (`validate_event_publish()`)
- Workflow policy → Conductor (`validate_workflow()`)
- Session policy → Traffic Cop (`validate_session()`)
- Telemetry policy → Nurse (`validate_telemetry()`)

### Translation Logic → Platform SDK
- SecurityContext creation → Platform SDK (`resolve_security_context()`)
- Tenant resolution → Platform SDK (`resolve_tenant()`)
- Role/permission extraction → Platform SDK (`resolve_roles_permissions()`)
- Session creation → Platform SDK (`create_session_with_context()`)
- Event routing → Platform SDK (`route_event()`)
- Workflow orchestration → Platform SDK (`orchestrate_workflow()`)

### Business Logic → Domain Services
- File lifecycle orchestration → Content Realm (if needed)
- Data policy enforcement → Content Realm (if needed)
- Knowledge graph operations → Insights Realm (if needed)

---

## Next Steps

1. ✅ Complete inventory (this document)
2. ⏳ Refactor abstractions (remove business logic)
3. ⏳ Create Platform SDK (translation logic)
4. ⏳ Refactor Smart City roles (to primitives)
5. ⏳ Ensure all adapter → abstraction flows work
6. ⏳ Integration and testing
