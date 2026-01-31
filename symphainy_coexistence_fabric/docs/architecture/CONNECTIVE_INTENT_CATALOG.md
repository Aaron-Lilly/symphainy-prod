# Connective Intent Catalog

**Status:** Canonical (January 2026)
**Authors:** Platform Architecture Team
**Purpose:** Define the reusable Connective Intent Packages that form SymphAIny's industry utility infrastructure

---

## Overview

**Connective Intents** are the platform's product IP — reusable integration patterns that solve structural problems shared across entire industries. Unlike Domain Intents (client-owned business logic), Connective Intents are:

- **Platform-owned** but extensible
- **Industry-reusable** (same patterns apply to VLP, AAR, PSO, and hundreds of other clients)
- **The infrastructure moat** that makes SymphAIny inevitable

> **Key Insight:** Integration patterns are NOT client differentiation. They are reusable connective tissue between enterprise systems.

---

## 1. Connective Intent Categories

### 1.1 Legacy Ingestion Patterns

**Purpose:** Extract and normalize data from legacy systems without requiring rewrites.

| Intent Pattern | Description | Industry Application |
|---------------|-------------|---------------------|
| `mainframe_extraction` | Extract data from mainframe systems | VLP (policy systems), AAR (incident databases) |
| `cobol_file_parsing` | Parse COBOL copybook-defined files | VLP (legacy policy files) |
| `edi_normalization` | Normalize EDI transaction formats | VLP (carrier exchanges), PSO (utility feeds) |
| `flat_file_mapping` | Map fixed-width and delimited files | All industries |
| `database_extraction` | Extract from legacy RDBMS | All industries |

**Implemented in Content Framework:**
- `parse_content` — Universal file parsing
- `ingest_file` — System adapter pattern
- `create_deterministic_embeddings` — Structural fingerprinting

---

### 1.2 Schema Mapping Patterns

**Purpose:** Map between disparate data models without hardcoded transformations.

| Intent Pattern | Description | Industry Application |
|---------------|-------------|---------------------|
| `semantic_schema_mapping` | AI-assisted field mapping | All industries |
| `taxonomy_alignment` | Align domain taxonomies | VLP (product codes), PSO (permit types) |
| `reference_data_resolution` | Resolve reference data across systems | All industries |
| `hierarchical_flattening` | Flatten nested structures | AAR (organizational hierarchies) |
| `polymorphic_mapping` | Handle type variants | VLP (policy product types) |

**Implemented in Insights Framework:**
- `analyze_structured_data` — Pattern extraction
- `map_relationships` — Relationship discovery
- `interpret_data_guided` — Guided schema understanding

---

### 1.3 Event Normalization Patterns

**Purpose:** Normalize events from heterogeneous systems into a canonical event taxonomy.

| Intent Pattern | Description | Industry Application |
|---------------|-------------|---------------------|
| `event_taxonomy_mapping` | Map system events to canonical types | All industries |
| `temporal_normalization` | Normalize timestamps across timezones | AAR (incident timelines), VLP (policy dates) |
| `correlation_id_generation` | Generate cross-system correlation IDs | All industries |
| `event_deduplication` | Detect and handle duplicate events | All industries |
| `event_enrichment` | Enrich events with context | AAR (location, personnel) |

**Implemented in Insights Framework:**
- `visualize_lineage` — Provenance tracking
- `assess_data_quality` — Event quality assessment

---

### 1.4 Process Choreography Patterns

**Purpose:** Orchestrate multi-system processes without tight coupling.

| Intent Pattern | Description | Industry Application |
|---------------|-------------|---------------------|
| `saga_orchestration` | Coordinate long-running processes | VLP (policy issuance), PSO (permit approval) |
| `compensation_handling` | Handle rollback across systems | VLP (premium reversals) |
| `parallel_execution` | Execute independent steps in parallel | All industries |
| `conditional_routing` | Route based on business rules | All industries |
| `human_in_loop` | Integrate human approval steps | AAR (review cycles), PSO (inspections) |

**Implemented in Operations Framework:**
- `create_workflow` — Process abstraction
- `generate_sop` — Operational documentation
- `analyze_coexistence` — Human-AI choreography

**Implemented in Coexistence:**
- `guide_agent` — Conversation orchestration
- `route_to_liaison` — Agent handoff patterns

---

### 1.5 Migration Choreography Patterns

**Purpose:** Orchestrate system migrations without business disruption.

| Intent Pattern | Description | Industry Application |
|---------------|-------------|---------------------|
| `dual_write_orchestration` | Write to legacy and target simultaneously | VLP (policy migration) |
| `parallel_run_governance` | Run both systems and compare results | VLP (claims processing) |
| `cutover_coordination` | Coordinate the final switchover | All industries |
| `rollback_orchestration` | Coordinate rollback if issues detected | All industries |
| `data_reconciliation` | Reconcile data between systems | All industries |

**Implemented in Operations Framework:**
- `create_workflow` (migration workflow patterns)
- `generate_sop` (migration runbooks)

---

### 1.6 System Abstraction Patterns

**Purpose:** Abstract system-specific details behind stable interfaces.

| Intent Pattern | Description | Industry Application |
|---------------|-------------|---------------------|
| `policy_location_abstraction` | Abstract where a policy lives | VLP (multi-system policy) |
| `claims_system_abstraction` | Abstract claims system details | VLP (claims processing) |
| `document_store_abstraction` | Abstract document storage | All industries |
| `identity_federation` | Federate identity across systems | All industries |
| `audit_trail_abstraction` | Unified audit across systems | All industries |

**Implemented across frameworks as the Platform SDK's role.**

---

## 2. Industry-Specific Connective Packages

### 2.1 Life Insurance / TPA (VLP Demo)

| Package | Connective Intents Used |
|---------|------------------------|
| **Policy System Integration** | `mainframe_extraction`, `cobol_file_parsing`, `policy_location_abstraction` |
| **Claims Processing** | `claims_system_abstraction`, `event_taxonomy_mapping`, `saga_orchestration` |
| **Migration Orchestration** | `dual_write_orchestration`, `parallel_run_governance`, `cutover_coordination` |
| **Carrier Onboarding** | `edi_normalization`, `semantic_schema_mapping`, `reference_data_resolution` |

### 2.2 After Action Reports (AAR Demo)

| Package | Connective Intents Used |
|---------|------------------------|
| **Incident Data Collection** | `database_extraction`, `event_taxonomy_mapping`, `temporal_normalization` |
| **Timeline Reconstruction** | `correlation_id_generation`, `event_enrichment` |
| **Multi-Source Correlation** | `semantic_schema_mapping`, `hierarchical_flattening` |
| **Lessons Learned Extraction** | `human_in_loop`, Process choreography patterns |

### 2.3 Permits / Utility (PSO Demo)

| Package | Connective Intents Used |
|---------|------------------------|
| **Permit Document Ingestion** | `flat_file_mapping`, `semantic_schema_mapping` |
| **Field Normalization** | `taxonomy_alignment`, `reference_data_resolution` |
| **Workflow Orchestration** | `saga_orchestration`, `human_in_loop`, `conditional_routing` |
| **Compliance Tracking** | `audit_trail_abstraction`, `event_taxonomy_mapping` |

---

## 3. Implementation Status

### Fully Implemented (Content + Insights Frameworks)

| Category | Status | Notes |
|----------|--------|-------|
| Legacy Ingestion | ✅ | Via `parse_content`, `ingest_file` |
| Schema Mapping | ✅ | Via `analyze_structured_data`, `map_relationships` |
| Event Normalization | ✅ | Via `visualize_lineage`, `assess_data_quality` |

### Framework Ready (Operations Framework)

| Category | Status | Notes |
|----------|--------|-------|
| Process Choreography | ✅ Frameworks | Patterns defined; client implementations needed |
| Migration Choreography | ✅ Frameworks | Patterns defined; client implementations needed |
| System Abstraction | ✅ Frameworks | Patterns defined; client implementations needed |

### Partner/Client Implementations (Domain Layer)

| Category | Status | Notes |
|----------|--------|-------|
| VLP-specific adapters | 🔜 | TPA builds on our frameworks |
| AAR-specific adapters | 🔜 | Client builds on our frameworks |
| PSO-specific adapters | 🔜 | Client builds on our frameworks |

---

## 4. The Product Surface

### What We Sell

1. **Platform Runtime** (Core IP)
   - Intent language and execution
   - Governance and security
   - Observability

2. **Connective Intent Packages** (Product IP)
   - Legacy Ingestion Package
   - Schema Mapping Package
   - Event Normalization Package
   - Process Choreography Package
   - Migration Choreography Package
   - Industry-specific bundles (Insurance, Government, Utilities)

3. **Professional Services**
   - Custom Connective Implementations
   - Domain Intent Development
   - Migration Execution

### What Partners Build

- System-specific adapters
- Vendor-specific mappings
- Deployment configurations
- Operational runbooks

### What Clients Own

- Business workflows
- Domain rules
- Operational processes
- Competitive differentiators

---

## 5. Extensibility Model

### Adding New Connective Intents

1. **Identify the pattern** — Is this structural (applies across industries)?
2. **Abstract the interface** — Define the semantic contract
3. **Implement the framework** — Build the reusable pattern
4. **Document the extension point** — Where do implementations plug in?

### Partner Extension Points

```
Connective Intent Framework (Platform-owned)
    │
    └── Extension Point: Adapter Interface
            │
            └── Partner Implementation (Partner-owned)
                    │
                    └── Client Configuration (Client-owned)
```

---

## 6. References

- [THREE_LAYER_INTENT_MODEL.md](THREE_LAYER_INTENT_MODEL.md) — Intent classification
- [FOUR_FRAMEWORKS_ARCHITECTURE.md](FOUR_FRAMEWORKS_ARCHITECTURE.md) — Framework mapping
- [PLATFORM_SDK_ARCHITECTURE.md](PLATFORM_SDK_ARCHITECTURE.md) — SDK surface

---

## Summary

**Connective Intents are the infrastructure moat.** Every enterprise faces the same integration challenges:

- Legacy system extraction
- Schema mapping
- Event normalization
- Process choreography
- Migration orchestration

By productizing these as reusable Connective Intent Packages, SymphAIny becomes:

> **The semantic control plane of enterprise operations.**
