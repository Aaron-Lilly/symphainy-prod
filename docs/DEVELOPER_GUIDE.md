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
9. [Scalability & Production Readiness](#scalability--production-readiness)
10. [Implementing New Capabilities](#implementing-new-capabilities)
11. [Testing & Validation](#testing--validation)
12. [Common Workflows](#common-workflows)
13. [Troubleshooting](#troubleshooting)

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

## Scalability & Production Readiness

### Principles for Scale

When building features that will process thousands or hundreds of thousands of items, follow these principles:

1. **Never accumulate results in memory** - Stream or batch persist
2. **Always support resumability** - Long-running operations must be resumable
3. **Use connection pooling** - Never create connections per operation
4. **Implement rate limiting** - External APIs have limits
5. **Track costs** - Monitor and limit resource usage
6. **Classify errors** - Distinguish transient vs. permanent failures

### Bulk Operations Pattern

**Pattern:** All bulk operations should follow this structure:

```python
async def _handle_bulk_operation(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle bulk operation with resumability and memory efficiency.
    
    Intent parameters:
    - item_ids: List[str] (REQUIRED)
    - batch_size: int (optional, default: 10)
    - max_parallel: int (optional, default: 5)
    - resume_from_batch: int (optional) - Resume from batch number
    """
    item_ids = intent.parameters.get("item_ids")
    batch_size = intent.parameters.get("batch_size", 10)
    max_parallel = intent.parameters.get("max_parallel", 5)
    resume_from_batch = intent.parameters.get("resume_from_batch", 0)
    
    # Generate operation ID for progress tracking
    operation_id = generate_event_id()
    
    # Initialize progress tracking
    await context.state_surface.track_operation_progress(
        operation_id=operation_id,
        tenant_id=context.tenant_id,
        progress={
            "status": "running",
            "total": len(item_ids),
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "current_batch": resume_from_batch,
            "last_successful_batch": resume_from_batch - 1,
            "errors": [],
            "results": []  # Store only IDs, not full results
        }
    )
    
    import asyncio
    
    # Process in batches (skip if resuming)
    for batch_start in range(resume_from_batch * batch_size, len(item_ids), batch_size):
        batch = item_ids[batch_start:batch_start + batch_size]
        batch_num = (batch_start // batch_size) + 1
        
        semaphore = asyncio.Semaphore(max_parallel)
        
        async def process_single_item(item_id: str) -> Dict[str, Any]:
            """Process a single item."""
            async with semaphore:
                try:
                    # Process item
                    result = await self._process_item(item_id, context)
                    
                    # Update progress (incrementally, don't accumulate)
                    await context.state_surface.track_operation_progress(
                        operation_id=operation_id,
                        tenant_id=context.tenant_id,
                        progress={
                            "processed": batch_start + 1,
                            "succeeded": batch_start + 1,
                            "current_batch": batch_num
                        }
                    )
                    
                    return {"success": True, "item_id": item_id, "result_id": result.get("id")}
                except Exception as e:
                    # Classify error
                    error_type = "transient" if self._is_transient_error(e) else "permanent"
                    
                    # Update progress
                    await context.state_surface.track_operation_progress(
                        operation_id=operation_id,
                        tenant_id=context.tenant_id,
                        progress={
                            "processed": batch_start + 1,
                            "failed": 1,
                            "errors": [{"item_id": item_id, "error": str(e), "type": error_type}]
                        }
                    )
                    
                    return {"success": False, "item_id": item_id, "error": str(e)}
        
        # Process batch in parallel
        batch_results = await asyncio.gather(*[
            process_single_item(item_id)
            for item_id in batch
        ])
        
        # Persist batch results incrementally (don't accumulate)
        await self._persist_batch_results(batch_results, context)
        
        # Update last successful batch
        await context.state_surface.track_operation_progress(
            operation_id=operation_id,
            tenant_id=context.tenant_id,
            progress={"last_successful_batch": batch_num}
        )
    
    # Final status
    final_progress = await context.state_surface.get_operation_progress(operation_id, context.tenant_id)
    
    return {
        "artifacts": {
            "operation_id": operation_id,
            "total": final_progress["total"],
            "succeeded": final_progress["succeeded"],
            "failed": final_progress["failed"]
        }
    }
```

**Key Points:**
- ✅ Progress tracking for resumability
- ✅ Incremental persistence (no memory accumulation)
- ✅ Error classification
- ✅ Batch-based processing
- ✅ Semaphore for concurrency control

### Connection Pooling

**Pattern:** All database adapters must use connection pooling.

```python
# ArangoDB Adapter with Connection Pooling
class ArangoAdapter:
    def __init__(self, url: str, ...):
        self._client: Optional[ArangoClient] = None
        self._db: Optional[StandardDatabase] = None
        self._pool_size: int = 10  # Configurable
        self._max_overflow: int = 5
    
    async def connect(self) -> bool:
        """Connect with connection pooling."""
        self._client = ArangoClient(
            hosts=self.url,
            # Connection pool configuration
            max_retries=3,
            retry_delay=1.0
        )
        # Connection is pooled automatically by python-arango
        self._db = self._client.db(...)
        return True
```

**Supabase Adapter:**
```python
# Supabase client handles connection pooling internally
# But we should configure it properly
self.anon_client: Client = create_client(
    self.url, 
    self.anon_key,
    options={
        "db": {"schema": "public"},
        "auth": {"persist_session": False},  # Don't persist sessions
        "global": {"headers": {"x-client-info": "symphainy-platform"}}
    }
)
```

### Rate Limiting

**Pattern:** All external API calls must be rate-limited.

```python
from symphainy_platform.foundations.public_works.adapters.rate_limiter import RateLimiter

class EmbeddingService:
    def __init__(self, ...):
        # Rate limiter for embedding API
        self.rate_limiter = RateLimiter(
            max_calls=100,  # Per minute
            time_window=60,
            backoff_strategy="exponential"
        )
    
    async def create_embeddings(self, ...):
        # Rate limit check
        await self.rate_limiter.acquire()
        
        try:
            # Make API call
            result = await self._call_embedding_api(...)
            return result
        except RateLimitError:
            # Exponential backoff
            await self.rate_limiter.backoff()
            raise
```

### Cost Tracking

**Pattern:** Track costs for all billable operations.

```python
from symphainy_platform.civic_systems.smart_city.services.cost_tracking_service import CostTrackingService

class EmbeddingService:
    def __init__(self, cost_tracker: CostTrackingService, ...):
        self.cost_tracker = cost_tracker
    
    async def create_embeddings(self, tenant_id: str, ...):
        # Track cost
        cost_per_embedding = 0.0001  # Example: $0.0001 per embedding
        
        result = await self._create_embeddings(...)
        
        # Record cost
        await self.cost_tracker.record_cost(
            tenant_id=tenant_id,
            service="embedding",
            operation="create_embeddings",
            cost=cost_per_embedding * len(result["embeddings"]),
            metadata={"embedding_count": len(result["embeddings"])}
        )
        
        # Check budget
        budget_status = await self.cost_tracker.check_budget(tenant_id, "embedding")
        if budget_status["exceeded"]:
            raise BudgetExceededError(f"Embedding budget exceeded: {budget_status['current']}/{budget_status['limit']}")
        
        return result
```

### Error Classification

**Pattern:** Classify errors to determine retry strategy.

```python
def _is_transient_error(self, error: Exception) -> bool:
    """Classify error as transient (retryable) or permanent."""
    error_str = str(error).lower()
    
    # Transient errors (retryable)
    transient_indicators = [
        "timeout",
        "connection",
        "rate limit",
        "temporary",
        "503",
        "502",
        "429"  # Too many requests
    ]
    
    # Permanent errors (not retryable)
    permanent_indicators = [
        "invalid",
        "not found",
        "unauthorized",
        "forbidden",
        "400",
        "401",
        "403",
        "404"
    ]
    
    if any(indicator in error_str for indicator in transient_indicators):
        return True
    
    if any(indicator in error_str for indicator in permanent_indicators):
        return False
    
    # Default: assume transient (can be retried)
    return True
```

### Execution State Lifecycle

**Pattern:** Execution states must have TTL or archival strategy.

```python
# In state_surface.py
async def set_execution_state(
    self,
    execution_id: str,
    tenant_id: str,
    state: Dict[str, Any]
) -> bool:
    """Set execution state with appropriate TTL."""
    
    # Determine TTL based on execution status
    if state.get("status") == "completed":
        ttl = 30 * 24 * 3600  # 30 days for completed executions
    elif state.get("status") == "failed":
        ttl = 7 * 24 * 3600  # 7 days for failed executions
    else:
        ttl = None  # No TTL for running executions
    
    return await self.state_abstraction.store_state(
        state_id=f"execution:{tenant_id}:{execution_id}",
        state_data=state,
        metadata={"type": "execution_state", "tenant_id": tenant_id},
        ttl=ttl  # TTL for cleanup
    )
```

---

## Implementing New Capabilities

### Creating a New Enabling Service

**Pattern:** Enabling services are pure data processing (no business logic, no orchestration).

**Example: EmbeddingService**

```python
"""
Embedding Service - Pure Data Processing for Embedding Creation

Enabling service for creating semantic embeddings from parsed content.

WHAT (Enabling Service Role): I execute embedding creation
HOW (Enabling Service Implementation): I use Public Works abstractions and external APIs
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.foundations.public_works.abstractions.semantic_data_abstraction import SemanticDataAbstraction

class EmbeddingService:
    """
    Embedding Service - Pure data processing for embedding creation.
    
    Uses external APIs (OpenAI, Cohere, etc.) to create embeddings.
    Stores embeddings in ArangoDB via SemanticDataAbstraction.
    """
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        embedding_model: str = "text-embedding-ada-002",
        embedding_provider: str = "openai"
    ):
        """
        Initialize Embedding Service.
        
        Args:
            public_works: Public Works Foundation Service
            embedding_model: Embedding model name
            embedding_provider: Provider (openai, cohere, local)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        self.embedding_model = embedding_model
        self.embedding_provider = embedding_provider
        
        # Get SemanticDataAbstraction for storage
        self.semantic_data = None
        if public_works:
            self.semantic_data = public_works.get_semantic_data_abstraction()
        
        # Initialize rate limiter (if needed)
        # Initialize cost tracker (if needed)
    
    async def create_embeddings(
        self,
        parsed_content: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Create embeddings from parsed content.
        
        Args:
            parsed_content: Parsed content dictionary
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with embedding metadata and IDs
        """
        # Extract text content from parsed_content
        text_content = self._extract_text(parsed_content)
        
        # Create embeddings via provider
        embeddings = await self._call_embedding_api(text_content)
        
        # Store embeddings in ArangoDB via SemanticDataAbstraction
        embedding_documents = self._prepare_embedding_documents(
            embeddings=embeddings,
            parsed_content=parsed_content,
            tenant_id=tenant_id,
            context=context
        )
        
        await self.semantic_data.store_semantic_embeddings(
            embedding_documents=embedding_documents
        )
        
        return {
            "embedding_id": generate_event_id(),
            "embedding_count": len(embeddings),
            "model_name": self.embedding_model,
            "provider": self.embedding_provider
        }
    
    def _extract_text(self, parsed_content: Dict[str, Any]) -> str:
        """Extract text content from parsed content."""
        # Implementation: Extract text from structured_data, text_content, etc.
        pass
    
    async def _call_embedding_api(self, text: str) -> List[List[float]]:
        """Call embedding API (OpenAI, Cohere, etc.)."""
        # Implementation: Call external API with rate limiting
        pass
    
    def _prepare_embedding_documents(
        self,
        embeddings: List[List[float]],
        parsed_content: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """Prepare embedding documents for ArangoDB storage."""
        # Implementation: Create document structure with _key, content_id, embedding, etc.
        pass
```

**Key Principles:**
- ✅ Pure data processing (no orchestration)
- ✅ Uses Public Works abstractions
- ✅ Returns raw data only
- ✅ No business logic
- ✅ Rate limiting and cost tracking built-in

### Integrating Service into Orchestrator

**Pattern:** Orchestrators coordinate services, don't implement logic.

```python
# In content_orchestrator.py
async def _handle_extract_embeddings(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """Handle extract_embeddings intent."""
    parsed_file_id = intent.parameters.get("parsed_file_id")
    
    # Get parsed content
    parsed_content = await self._get_parsed_content(parsed_file_id, context)
    
    # Create embeddings via EmbeddingService
    embedding_result = await self.embedding_service.create_embeddings(
        parsed_content=parsed_content,
        tenant_id=context.tenant_id,
        context=context
    )
    
    # Track embedding in Supabase for lineage
    await self._track_embedding(
        embedding_id=embedding_result["embedding_id"],
        parsed_file_id=parsed_file_id,
        embedding_count=embedding_result["embedding_count"],
        model_name=embedding_result["model_name"],
        tenant_id=context.tenant_id,
        context=context
    )
    
    # Promote to Record of Fact
    if self.data_steward_sdk:
        await self.data_steward_sdk.promote_to_record_of_fact(
            source_file_id=parsed_content.get("file_id"),
            tenant_id=context.tenant_id,
            record_type="semantic_embedding",
            record_content=embedding_result,
            promoted_by="system",
            promotion_reason="Embeddings created for semantic analysis"
        )
    
    return {
        "artifacts": {
            "embedding_id": embedding_result["embedding_id"],
            "embedding_count": embedding_result["embedding_count"]
        }
    }
```

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
5. **Scale Testing:** Test with realistic data volumes (1K, 10K files)
6. **Failure Testing:** Test error handling, retries, resumability

### Testing at Scale

**Before Production:**
1. **1K File Test:** Run full pipeline with 1k files
   - Validate bulk operations
   - Check memory usage
   - Verify connection pooling
   - Measure performance

2. **10K File Test:** Validate production readiness
   - Test resumability
   - Test error handling
   - Validate cost tracking
   - Check database growth

3. **Failure Testing:** Test error scenarios
   - Partial failures in bulk operations
   - API rate limit handling
   - Connection failures
   - Resume from failures

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

### Core Documentation
- **Architecture Guide:** [architecture/north_star.md](architecture/north_star.md) - Authoritative architecture
- **Data Framework:** [architecture/data_framework.md](architecture/data_framework.md) - Four-class data model
- **Platform Rules:** [PLATFORM_RULES.md](PLATFORM_RULES.md) - Development standards
- **Implementation Plan:** [IMPLEMENTATION_PLAN_350K_SCALE.md](IMPLEMENTATION_PLAN_350K_SCALE.md) - Current work plan

### Migration Guides
- [MIGRATION_GUIDE_LIFECYCLE_STATES.md](MIGRATION_GUIDE_LIFECYCLE_STATES.md) - Using lifecycle states
- [MIGRATION_GUIDE_PROMOTION_WORKFLOWS.md](MIGRATION_GUIDE_PROMOTION_WORKFLOWS.md) - Promotion workflows

### API Documentation
- [API_ARTIFACT_PLANE.md](API_ARTIFACT_PLANE.md) - Artifact Plane API
- [API_DATA_STEWARD_SDK.md](API_DATA_STEWARD_SDK.md) - Data Steward SDK
- [API_CURATOR_PROMOTION.md](API_CURATOR_PROMOTION.md) - Curator promotion

### Reference Documents
- **Platform Audit:** [PLATFORM_AUDIT_AND_REFACTORING_PLAN.md](PLATFORM_AUDIT_AND_REFACTORING_PLAN.md) - Gap analysis
- **Architecture Implementation:** [ARCHITECTURE_IMPLEMENTATION_PLAN.md](ARCHITECTURE_IMPLEMENTATION_PLAN.md) - Completed work

---

## Quick Reference: Common Tasks

### Adding a New Intent Handler

1. **Add intent declaration** in realm's `declare_intents()` method
2. **Add handler method** in orchestrator (e.g., `_handle_my_intent()`)
3. **Route intent** in orchestrator's `handle_intent()` method
4. **Use enabling services** for business logic (don't implement in orchestrator)
5. **Return artifacts and events** (not side effects)
6. **Add tests** (unit + integration)

### Creating a Bulk Operation

1. **Follow bulk operations pattern** (see Scalability section)
2. **Add progress tracking** using `state_surface.track_operation_progress()`
3. **Support resumability** with `resume_from_batch` parameter
4. **Stream results** (don't accumulate in memory)
5. **Classify errors** (transient vs. permanent)
6. **Add tests** with realistic volumes (1K+ items)

### Adding External API Integration

1. **Create adapter** in `foundations/public_works/adapters/`
2. **Add rate limiting** for API calls
3. **Add cost tracking** for billable operations
4. **Implement retry logic** with exponential backoff
5. **Classify errors** (transient vs. permanent)
6. **Add tests** with mocked API responses

### Implementing Data Lifecycle

1. **Working Materials:** Created via boundary contracts, TTL enforced
2. **Records of Fact:** Promoted via `DataStewardSDK.promote_to_record_of_fact()`
3. **Purpose-Bound Outcomes:** Created in Artifact Plane, lifecycle managed
4. **Platform DNA:** Promoted via `CuratorService.promote_to_platform_dna()`

---

**Remember:** We're building a platform that works. No shortcuts. No cheats. Capability by design, implementation by policy. **Scale is a first-class concern.**
