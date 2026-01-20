# Symphainy Platform Developer Guide

**Last Updated:** January 2026  
**Status:** Active Development - Platform 2.0  
**Version:** 2.0 (Breaking Changes - No Backwards Compatibility)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Platform Overview](#platform-overview)
3. [Architecture Fundamentals](#architecture-fundamentals)
4. [Four-Class Data Framework](#four-class-data-framework)
5. [Development Patterns](#development-patterns)
6. [Core APIs](#core-apis)
7. [Civic Systems](#civic-systems)
8. [Realms](#realms)
9. [Testing & Validation](#testing--validation)
10. [Common Workflows](#common-workflows)
11. [Troubleshooting](#troubleshooting)

---

## Quick Start

### For New Developers

1. **Read Architecture First:** Start with [architecture/north_star.md](architecture/north_star.md)
2. **Understand Data Framework:** Review [architecture/data_framework.md](architecture/data_framework.md)
3. **Follow Platform Rules:** Read [PLATFORM_RULES.md](PLATFORM_RULES.md)
4. **Check Current State:** Review [current_state/00_CURRENT_STATE_INDEX.md](current_state/00_CURRENT_STATE_INDEX.md)

### Essential Concepts

- **Runtime:** The only component allowed to own execution and state
- **Civic Systems:** Governance layer (Smart City, Experience, Artifact Plane, etc.)
- **Realms:** Domain services (Content, Insights, Journey, Outcomes)
- **Four-Class Data Framework:** Working Materials → Records of Fact → Purpose-Bound Outcomes → Platform DNA
- **Capability by Design, Implementation by Policy:** Real infrastructure with permissive MVP policies

---

## Platform Overview

### What is Symphainy?

> **Symphainy is a governed execution platform.**
> It runs **Solutions** safely — and those Solutions safely operate, connect to, and reason over external systems.

### Core Principles

1. **Explicit Execution:** Nothing executes without intent, policy, and attribution
2. **Governed by Design:** Governance is built-in, not bolted on
3. **Capability by Design, Implementation by Policy:** Real infrastructure with configurable policies
4. **Four-Class Data Framework:** Clear boundaries between data classes
5. **Public Works Pattern:** All infrastructure via swappable abstractions

### Platform Structure

```
Symphainy Platform
├── Runtime (Execution Authority)
├── Civic Systems (Governance)
│   ├── Smart City (Data Governance)
│   ├── Experience (User Exposure)
│   ├── Artifact Plane (Artifact Management)
│   └── ...
└── Realms (Domain Services)
    ├── Content (File Management)
    ├── Insights (Data Analysis)
    ├── Journey (Workflow Management)
    └── Outcomes (Solution Delivery)
```

---

## Architecture Fundamentals

### Runtime

**Runtime is the only component allowed to own execution and state.**

Runtime owns:
- Intent acceptance
- Execution lifecycle
- Session & tenant context
- Write-ahead log (WAL)
- Saga orchestration
- Retries & failure recovery
- Deterministic replay
- State transitions

**Key Rule:** If something runs and Runtime does not know about it, **it is a bug**.

### Civic Systems

**Civic Systems define how things are allowed to participate in execution.**

They do **not** own business logic or execution. They define **capability by design, constrained by policy**.

**Five Civic Systems:**

1. **Smart City** — Data governance, boundaries, contracts
2. **Experience** — User exposure, authentication, authorization
3. **Artifact Plane** — Artifact lifecycle, versioning, dependencies
4. **Public Works** — Infrastructure abstractions (storage, state, search)
5. **Curator** — Platform DNA promotion, registry management

### Realms

**Realms are domain services that execute business logic.**

Realms:
- Execute under Runtime authority
- Use Civic Systems for governance
- Produce Purpose-Bound Outcomes
- Operate within data boundaries

**Current Realms:**
- **Content:** File ingestion, parsing, management
- **Insights:** Data quality, interpretation, analysis
- **Journey:** Workflow creation, SOP generation, blueprints
- **Outcomes:** Solution delivery, roadmaps, POCs

---

## Four-Class Data Framework

The platform uses a **four-class data framework** to manage data with clear boundaries and lifecycles.

### Class 1: Working Materials

**Definition:** Temporary, time-bound data for processing (raw files, parsed results).

**Properties:**
- **Temporary:** TTL-bound (expires after TTL)
- **Time-bound:** Exists for processing duration
- **Material-dependent:** Requires source material

**Infrastructure:**
- **Storage:** GCS (temporary), Supabase (tracking)
- **TTL:** Enforced by policy (default: 30 days)
- **Lifecycle:** Created → Processed → Expired

**Examples:**
- Uploaded files
- Parsed content
- Temporary processing results

**API:**
```python
# Working Materials are created via Data Steward boundary contracts
# They expire automatically based on TTL policy
```

---

### Class 2: Records of Fact

**Definition:** Persistent, auditable conclusions or interpreted meaning.

**Properties:**
- **Persistent:** Never expires (permanent)
- **Meaning-based:** Stores conclusions, not materials
- **Material-independent:** Meaning persists without source

**Infrastructure:**
- **Storage:** Supabase (structured), ArangoDB (graph/lineage/embeddings)
- **TTL:** None (permanent)
- **Lifecycle:** Promoted from Working Material → Permanent

**Examples:**
- Semantic embeddings
- Interpretations
- Conclusions
- Deterministic representations

**API:**
```python
from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK

# Promote Working Material to Record of Fact
record_id = await data_steward_sdk.promote_to_record_of_fact(
    source_file_id="file_123",
    source_boundary_contract_id="contract_123",
    tenant_id="tenant_123",
    record_type="semantic_embedding",
    record_content={"embedding": [0.1, 0.2, 0.3]},
    promoted_by="system",
    promotion_reason="Promoted for persistent meaning",
    supabase_adapter=supabase_adapter
)
```

---

### Class 3: Purpose-Bound Outcomes

**Definition:** Intentional, human-facing deliverables with owner, purpose, and lifecycle.

**Properties:**
- **Lifecycle-managed:** draft → accepted → obsolete
- **Versioned:** Immutable past versions for accepted artifacts
- **Purpose-bound:** Created for a decision or delivery
- **Dependency-tracked:** Links to source artifacts

**Infrastructure:**
- **Storage:** Artifact Plane (Supabase metadata + GCS payloads)
- **Lifecycle:** Managed by Artifact Plane
- **Versioning:** Automatic for accepted artifacts

**Examples:**
- Blueprints
- Roadmaps
- POCs
- SOPs
- Analysis reports
- Visualizations

**API:**
```python
from symphainy_platform.civic_systems.artifact_plane.artifact_plane import ArtifactPlane

# Create Purpose-Bound Outcome
artifact_result = await artifact_plane.create_artifact(
    artifact_type="blueprint",
    artifact_id="blueprint_123",
    payload={
        "semantic_payload": {"blueprint_id": "blueprint_123"},
        "renderings": {"markdown": "# Blueprint\n\nContent..."}
    },
    context=execution_context,
    lifecycle_state="draft",
    owner="client",
    purpose="delivery",
    source_artifact_ids=["workflow_123"]  # Dependencies
)

# Transition lifecycle state
await artifact_plane.transition_lifecycle_state(
    artifact_id="blueprint_123",
    tenant_id="tenant_123",
    new_state="accepted",
    transitioned_by="user_123",
    reason="Approved for production"
)
```

**Lifecycle States:**
- `draft`: Initial state, can be modified
- `accepted`: Finalized, creates immutable version
- `obsolete`: No longer active

---

### Class 4: Platform DNA

**Definition:** Generalized, curated, de-identified capabilities promoted from outcomes.

**Properties:**
- **De-identified:** No client context
- **Generalizable:** Reusable across clients
- **Policy-approved:** Curator validates
- **Immutable:** Versioned, immutable registry entries

**Infrastructure:**
- **Storage:** Supabase registries (versioned, immutable)
- **Promotion:** Via Curator role (deliberate act)
- **Registries:** Solution, Intent, Realm registries

**Examples:**
- Generalized solutions
- Reusable workflows
- Platform capabilities

**API:**
```python
from symphainy_platform.civic_systems.smart_city.services.curator_service import CuratorService

# Promote Purpose-Bound Outcome to Platform DNA
registry_id = await curator_service.promote_to_platform_dna(
    artifact_id="blueprint_123",
    tenant_id="tenant_123",
    registry_type="solution",
    registry_name="Workflow Optimization Solution",
    promoted_by="curator_123",
    description="Generalized workflow optimization solution"
)
```

---

## Development Patterns

### Capability by Design, Implementation by Policy

**Principle:** Build real, robust infrastructure (secure by design), then configure permissive policies for MVP (open by policy), allowing for easy tightening in production without code changes.

**Example:**
```python
# Real policy evaluation infrastructure exists
class MaterializationPolicyStore:
    async def evaluate_policy(self, ...):
        # Real policy evaluation logic
        # MVP: Permissive policy (allows all types)
        # Production: Can tighten without code changes
        pass
```

**Benefits:**
- Infrastructure is production-ready
- Policies can be tightened without code changes
- MVP can be permissive, production can be strict
- No architectural debt from MVP shortcuts

### Public Works Pattern

**Principle:** All infrastructure via swappable abstractions (protocols).

**Example:**
```python
# Use protocols, not direct implementations
from symphainy_platform.foundations.public_works.protocols.artifact_storage_protocol import ArtifactStorageProtocol

class ArtifactPlane:
    def __init__(self, artifact_storage: ArtifactStorageProtocol):
        # Can swap implementations without code changes
        self.artifact_storage = artifact_storage
```

**Benefits:**
- Infrastructure is swappable
- Easy to test with mocks
- No vendor lock-in
- Clean separation of concerns

### Explicit Promotion Workflows

**Principle:** Data transitions are explicit and policy-governed.

**Workflows:**
1. **Working Material → Record of Fact:** Explicit via `DataStewardSDK.promote_to_record_of_fact()`
2. **Purpose-Bound Outcome → Platform DNA:** Explicit via `CuratorService.promote_to_platform_dna()`

**Key Rule:** Nothing moves automatically. All transitions are explicit and policy-mediated.

---

## Core APIs

### Artifact Plane API

**Purpose:** Manage Purpose-Bound Outcomes (artifacts).

**Key Methods:**
- `create_artifact()`: Create and register artifact
- `get_artifact()`: Retrieve artifact
- `list_artifacts()`: List artifacts with filtering
- `transition_lifecycle_state()`: Change lifecycle state
- `get_artifact_versions()`: Get all versions
- `validate_dependencies()`: Validate dependencies

**Documentation:** See [API_ARTIFACT_PLANE.md](API_ARTIFACT_PLANE.md)

### Data Steward SDK API

**Purpose:** Coordinate data boundaries, contracts, and provenance.

**Key Methods:**
- `promote_to_record_of_fact()`: Promote Working Material to Record of Fact
- `request_data_access()`: Request data access
- `authorize_materialization()`: Authorize materialization

**Documentation:** See [API_DATA_STEWARD_SDK.md](API_DATA_STEWARD_SDK.md)

### Curator Promotion API

**Purpose:** Promote Purpose-Bound Outcomes to Platform DNA.

**Key Methods:**
- `promote_to_platform_dna()`: Promote artifact to Platform DNA

**Documentation:** See [API_CURATOR_PROMOTION.md](API_CURATOR_PROMOTION.md)

---

## Civic Systems

### Smart City

**Role:** Data governance, boundaries, contracts.

**Components:**
- **Data Steward Primitives:** Policy decisions for data access
- **Data Steward SDK:** Coordination logic
- **Materialization Policy Store:** Database-backed policy store
- **Boundary Contract Store:** Data boundary contracts

**Key Features:**
- Materialization policy evaluation
- Boundary contract negotiation
- TTL enforcement
- Records of Fact promotion

### Artifact Plane

**Role:** Artifact lifecycle, versioning, dependencies.

**Components:**
- **ArtifactPlane:** Core artifact management
- **Lifecycle State Machine:** draft → accepted → obsolete
- **Versioning:** Immutable past versions
- **Dependency Tracking:** Artifact → artifact relationships

**Key Features:**
- Lifecycle state management
- Versioning for accepted artifacts
- Cross-realm artifact retrieval
- Dependency validation

### Curator

**Role:** Platform DNA promotion, registry management.

**Components:**
- **CuratorService:** Promotion workflow
- **CuratorPrimitives:** Policy decisions for promotion
- **Registry Tables:** solution_registry, intent_registry, realm_registry

**Key Features:**
- Promotion validation
- Generalization (de-identification)
- Registry entry creation
- Versioning

---

## Realms

### Content Realm

**Purpose:** File ingestion, parsing, management.

**Key Intents:**
- `ingest_file`: Upload and register file
- `parse_content`: Parse file content
- `extract_embeddings`: Extract embeddings (⚠️ Placeholder - needs implementation)
- `list_files`: List files
- `get_file`: Retrieve file

**Artifact Integration:**
- Files are Working Materials (TTL-bound)
- Parsed content can be promoted to Records of Fact
- Analysis reports are Purpose-Bound Outcomes

### Insights Realm

**Purpose:** Data quality, interpretation, analysis.

**Key Intents:**
- `assess_data_quality`: Assess data quality
- `interpret_data`: Interpret data semantically
- `analyze_structured`: Analyze structured data
- `analyze_unstructured`: Analyze unstructured data
- `visualize_lineage`: Visualize data lineage

**Artifact Integration:**
- Interpretations are Records of Fact
- Analysis reports are Purpose-Bound Outcomes (registered in Artifact Plane)

### Journey Realm

**Purpose:** Workflow creation, SOP generation, blueprints.

**Key Intents:**
- `create_workflow`: Create workflow from BPMN
- `generate_sop`: Generate SOP from interactive chat
- `create_blueprint`: Create blueprint from workflow
- `analyze_coexistence`: Analyze workflow coexistence

**Artifact Integration:**
- Workflows, SOPs, and blueprints are Purpose-Bound Outcomes (registered in Artifact Plane)
- All artifacts have lifecycle states and dependencies

### Outcomes Realm

**Purpose:** Solution delivery, roadmaps, POCs.

**Key Intents:**
- `generate_roadmap`: Generate roadmap
- `create_poc`: Create proof of concept
- `synthesize_outcome`: Synthesize outcome

**Artifact Integration:**
- Roadmaps, POCs, and outcomes are Purpose-Bound Outcomes (registered in Artifact Plane)

---

## Testing & Validation

### Test Structure

```
tests/
├── unit/              # Unit tests
│   ├── civic_systems/ # Civic Systems tests
│   ├── realms/        # Realm tests
│   └── foundations/   # Foundation tests
├── integration/       # Integration tests
│   └── test_architecture_integration.py
└── e2e/              # End-to-end tests
```

### Test Markers

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.e2e`: End-to-end tests
- `@pytest.mark.civic_systems`: Civic Systems tests
- `@pytest.mark.realms`: Realm tests

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m unit

# Run integration tests
pytest -m integration

# Run specific test file
pytest tests/integration/test_architecture_integration.py
```

### Test Requirements

1. **No Placeholders:** Tests must validate real functionality
2. **No Mocks in Production Code:** Mocks only in tests
3. **Real Implementations:** All code must work
4. **Policy Testing:** Test both MVP (permissive) and production (strict) policies

---

## Common Workflows

### Creating a Purpose-Bound Outcome

```python
# 1. Create artifact in Artifact Plane
artifact_result = await artifact_plane.create_artifact(
    artifact_type="blueprint",
    artifact_id="blueprint_123",
    payload={
        "semantic_payload": {"blueprint_id": "blueprint_123"},
        "renderings": {"markdown": "# Blueprint\n\nContent..."}
    },
    context=execution_context,
    lifecycle_state="draft",
    owner="client",
    purpose="delivery",
    source_artifact_ids=["workflow_123"]
)

# 2. Transition to accepted when ready
await artifact_plane.transition_lifecycle_state(
    artifact_id=artifact_result["artifact_id"],
    tenant_id="tenant_123",
    new_state="accepted",
    transitioned_by="user_123",
    reason="Approved for production"
)
```

### Promoting to Platform DNA

```python
# 1. Ensure artifact is in "accepted" state
await artifact_plane.transition_lifecycle_state(
    artifact_id="blueprint_123",
    tenant_id="tenant_123",
    new_state="accepted"
)

# 2. Promote to Platform DNA
registry_id = await curator_service.promote_to_platform_dna(
    artifact_id="blueprint_123",
    tenant_id="tenant_123",
    registry_type="solution",
    registry_name="Workflow Optimization Solution",
    promoted_by="curator_123"
)
```

### Promoting Working Material to Record of Fact

```python
# Promote Working Material to Record of Fact
record_id = await data_steward_sdk.promote_to_record_of_fact(
    source_file_id="file_123",
    source_boundary_contract_id="contract_123",
    tenant_id="tenant_123",
    record_type="semantic_embedding",
    record_content={"embedding": [0.1, 0.2, 0.3]},
    promoted_by="system",
    promotion_reason="Promoted for persistent meaning",
    supabase_adapter=supabase_adapter
)
```

---

## Troubleshooting

### Common Issues

**Issue: Artifact not found**
- Check artifact exists in Artifact Plane
- Verify tenant_id matches
- Check lifecycle state (may be obsolete)

**Issue: Promotion failed**
- Ensure artifact is in "accepted" state
- Verify artifact type matches registry type
- Check policy validation (CuratorPrimitives)

**Issue: Policy evaluation failed**
- Check MaterializationPolicyStore is initialized
- Verify policy exists in database
- Check fallback to MVP permissive policy

**Issue: Lifecycle transition failed**
- Verify current state allows transition
- Check policy allows transition
- Ensure artifact is current version (not past version)

### Debugging Tips

1. **Check Logs:** All components log errors with context
2. **Verify State:** Check database tables directly
3. **Test Policies:** Verify policy evaluation separately
4. **Check Dependencies:** Validate artifact dependencies

---

## Additional Resources

- **Architecture Guide:** [architecture/north_star.md](architecture/north_star.md)
- **Data Framework:** [architecture/data_framework.md](architecture/data_framework.md)
- **Platform Rules:** [PLATFORM_RULES.md](PLATFORM_RULES.md)
- **Migration Guides:**
  - [MIGRATION_GUIDE_LIFECYCLE_STATES.md](MIGRATION_GUIDE_LIFECYCLE_STATES.md)
  - [MIGRATION_GUIDE_PROMOTION_WORKFLOWS.md](MIGRATION_GUIDE_PROMOTION_WORKFLOWS.md)
- **API Documentation:**
  - [API_ARTIFACT_PLANE.md](API_ARTIFACT_PLANE.md)
  - [API_DATA_STEWARD_SDK.md](API_DATA_STEWARD_SDK.md)
  - [API_CURATOR_PROMOTION.md](API_CURATOR_PROMOTION.md)

---

**Remember:** We're building a platform that works. No shortcuts. No cheats. Capability by design, implementation by policy.
