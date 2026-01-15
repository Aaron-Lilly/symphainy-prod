# E2E Client Data Flow Implementation Plan
## Upload → Parse → Data Mash

**Date:** January 2026  
**Status:** 🎯 **READY FOR IMPLEMENTATION**  
**Goal:** Complete E2E flow from file upload through parsing to Data Mash

---

## 🎯 Executive Summary

**Implement the complete E2E client data flow** that demonstrates the platform's core capability:
1. **Upload** - File ingestion (existing, needs integration)
2. **Parse** - Content extraction (✅ complete, needs wiring)
3. **Data Mash** - Semantic interpretation & canonical mapping (new)

**Key Principle:**
> **All data flows through Runtime (WAL + Saga), converges at File Storage, then follows platform-native parsing → data mash pipeline.**

---

## 📊 Current State Assessment

### ✅ What's Complete

1. **Parsing Services** - All 4 services implemented
   - Structured Parsing Service
   - Unstructured Parsing Service
   - Hybrid Parsing Service
   - Workflow/SOP Parsing Service

2. **Content Orchestrator** - Routes to parsing services

3. **File Storage** - GCS + Supabase metadata

4. **State Surface** - File storage methods available

5. **Runtime Plane** - Intent submission, WAL, Saga

### ⚠️ What's Missing

1. **Realm Structure** - Need Phase 5 structure (manager.py, orchestrator.py pattern)
2. **File Upload Integration** - Need to wire upload → file storage → parsing
3. **Data Mash Implementation** - Need to build Data Mash capability
4. **Insights Realm Services** - Need Data Quality, Semantic Interpretation, Mapping services
5. **E2E Wiring** - Need to connect all pieces

---

## 🏗️ Implementation Phases

### Phase 5.0: Establish Realm Structure (2-3 days)

**Goal:** Create Phase 5 realm structure for Content and Insights realms.

#### 5.0.1: Content Realm Manager

**Location:** `symphainy_platform/realms/content/manager.py`

```python
class ContentRealmManager:
    """
    Content Realm Manager - Lifecycle and Registration.
    
    WHAT: I manage Content Realm lifecycle
    HOW: I register capabilities with Curator and bind to Runtime
    """
    
    def __init__(
        self,
        curator: Any,
        runtime_service: Any,
        content_orchestrator: Any
    ):
        self.curator = curator
        self.runtime = runtime_service
        self.orchestrator = content_orchestrator
        self.logger = get_logger(self.__class__.__name__)
    
    async def initialize(self) -> bool:
        """Initialize and register Content Realm capabilities."""
        # Register capabilities with Curator
        await self.curator.register_capability(
            CapabilityDefinition(
                intent_type="content.upload",
                service_name="content_realm",
                handler="ContentOrchestrator.handle_upload",
                description="Upload and parse files"
            )
        )
        
        await self.curator.register_capability(
            CapabilityDefinition(
                intent_type="content.parse",
                service_name="content_realm",
                handler="ContentOrchestrator.parse_file",
                description="Parse files"
            )
        )
        
        return True
    
    async def shutdown(self) -> bool:
        """Shutdown Content Realm."""
        return True
```

#### 5.0.2: Content Realm Orchestrator (Update)

**Location:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Update to:**
- Handle Runtime intents
- Compose saga steps
- Call services (not orchestrate workflows)
- Never store state directly

```python
class ContentOrchestrator:
    """
    Content Orchestrator - Saga Composition.
    
    WHAT: I orchestrate Content Realm operations
    HOW: I compose saga steps, call services, attach agents
    """
    
    async def handle_upload_intent(
        self,
        intent_payload: Dict[str, Any],
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle upload intent from Runtime.
        
        Flow:
        1. Store file (via FileStorageAbstraction)
        2. Create file reference in State Surface
        3. Parse file (via Content Orchestrator)
        4. Return result
        """
        # Step 1: Store file
        file_data = intent_payload.get("file_data")
        filename = intent_payload.get("filename")
        tenant_id = execution_context.get("tenant_id")
        
        # Use FileStorageAbstraction (from Public Works)
        file_storage = execution_context.get("file_storage_abstraction")
        file_id = await file_storage.upload_file(
            file_path=filename,
            file_data=file_data,
            metadata={
                "tenant_id": tenant_id,
                "filename": filename
            }
        )
        
        # Step 2: Store in State Surface
        state_surface = execution_context.get("state_surface")
        file_reference = await state_surface.store_file(
            session_id=execution_context.get("session_id"),
            tenant_id=tenant_id,
            file_data=file_data,
            filename=filename,
            metadata={"file_id": file_id}
        )
        
        # Step 3: Parse
        parse_result = await self.parse_file(
            file_reference=file_reference,
            filename=filename,
            parsing_type=None,
            options={}
        )
        
        return {
            "success": True,
            "file_id": file_id,
            "file_reference": file_reference,
            "parse_result": parse_result
        }
```

#### 5.0.3: Insights Realm Structure

**Location:** `symphainy_platform/realms/insights/`

Create:
- `manager.py` - Lifecycle and registration
- `orchestrators/data_mash_orchestrator.py` - Data Mash orchestration
- `services/data_quality_service.py` - Data quality analysis
- `services/semantic_interpretation_service.py` - Semantic interpretation
- `services/semantic_mapping_service.py` - Canonical mapping

---

### Phase 5.1: Data Mash Implementation (5-7 days)

**Goal:** Implement Data Mash as first-class platform capability.

#### 5.1.1: DataMashSaga

**Location:** `symphainy_platform/runtime/saga.py`

```python
class DataMashSaga(Saga):
    """
    Data Mash Saga - Orchestrates Data Mash execution.
    
    Phases:
    1. INITIATED - Mash created, content references validated
    2. DATA_QUALITY - Data quality analysis complete
    3. SEMANTIC_INTERPRETATION - Semantic labels assigned
    4. SEMANTIC_MAPPING - Canonical model formed
    5. REGISTERED - Data product registered and exposed
    """
    
    async def execute_phase(
        self,
        phase: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute saga phase."""
        if phase == "DATA_QUALITY":
            return await self._execute_data_quality(context)
        elif phase == "SEMANTIC_INTERPRETATION":
            return await self._execute_semantic_interpretation(context)
        elif phase == "SEMANTIC_MAPPING":
            return await self._execute_semantic_mapping(context)
        elif phase == "REGISTERED":
            return await self._execute_registration(context)
        else:
            raise ValueError(f"Unknown phase: {phase}")
```

#### 5.1.2: Data Quality Service

**Location:** `symphainy_platform/realms/insights/services/data_quality_service.py`

```python
class DataQualityService:
    """
    Data Quality Service - First Cognitive Platform Step.
    
    WHAT: I analyze data quality
    HOW: I perform deterministic + light reasoning analysis
    """
    
    async def analyze_quality(
        self,
        parsed_artifacts: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None
    ) -> DataQualityReport:
        """
        Analyze data quality of parsed artifacts.
        
        Returns:
            DataQualityReport with:
            - Completeness
            - Structural consistency
            - Null density
            - Field entropy
            - Schema drift
            - Parser confidence scoring
        """
        # Implementation
        pass
```

#### 5.1.3: Semantic Interpretation Service

**Location:** `symphainy_platform/realms/insights/services/semantic_interpretation_service.py`

```python
class SemanticInterpretationService:
    """
    Semantic Interpretation Service - Expert Reasoning.
    
    WHAT: I interpret semantic meaning
    HOW: I use GroundedReasoningAgentBase for expert reasoning
    """
    
    def __init__(
        self,
        agent_foundation: Any,
        content_realm: Any
    ):
        self.agent_foundation = agent_foundation
        self.content_realm = content_realm
        self.logger = get_logger(self.__class__.__name__)
    
    async def interpret_semantics(
        self,
        deterministic_candidates: List[Dict[str, Any]],
        data_quality_report: DataQualityReport,
        domain_context: str
    ) -> SemanticInterpretationResult:
        """
        Interpret semantics using two-hop approach.
        
        Phase 3A: Get deterministic candidates from Content Realm
        Phase 3B: Use agent for expert reasoning
        """
        # Phase 3A: Get deterministic candidates (Content Realm)
        candidates = await self.content_realm.get_deterministic_labels(
            parsed_artifacts
        )
        
        # Phase 3B: Expert reasoning (Insights Realm + Agent)
        agent = self.agent_foundation.get_agent("semantic_interpreter_agent")
        interpretation = await agent.reason(
            context={
                "candidates": candidates,
                "quality_report": data_quality_report,
                "domain": domain_context
            }
        )
        
        return interpretation
```

#### 5.1.4: Semantic Mapping Service

**Location:** `symphainy_platform/realms/insights/services/semantic_mapping_service.py`

```python
class SemanticMappingService:
    """
    Semantic Mapping Service - Canonical Model Formation.
    
    WHAT: I create canonical data models
    HOW: I group interpreted fields into entities and map to canonical schemas
    """
    
    async def create_canonical_model(
        self,
        interpretations: List[SemanticInterpretationResult],
        target_domain: str
    ) -> CanonicalModel:
        """
        Create canonical model from semantic interpretations.
        
        Returns:
            CanonicalModel with:
            - Entity definitions
            - Field mappings
            - Schema version
        """
        # Implementation
        pass
```

#### 5.1.5: Data Mash Orchestrator

**Location:** `symphainy_platform/realms/insights/orchestrators/data_mash_orchestrator.py`

```python
class DataMashOrchestrator:
    """
    Data Mash Orchestrator - Coordinates Data Mash execution.
    
    WHAT: I orchestrate Data Mash operations
    HOW: I compose saga steps, call services, attach agents
    """
    
    async def create_mash(
        self,
        content_refs: List[str],
        options: Dict[str, Any],
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create Data Mash.
        
        Flow:
        1. Validate content references
        2. Start DataMashSaga
        3. Execute phases:
           - Data Quality
           - Semantic Interpretation
           - Semantic Mapping
           - Registration
        4. Return mash result
        """
        # Implementation
        pass
```

---

### Phase 5.2: E2E Integration (2-3 days)

**Goal:** Wire everything together for complete E2E flow.

#### 5.2.1: Runtime Intent Handlers

**Update Runtime Service** to handle:
- `content.upload` - File upload intent
- `content.parse` - Parse file intent
- `data_mash.create` - Create Data Mash intent

#### 5.2.2: Experience Plane Integration

**Create Experience Plane handlers:**
- `POST /api/v1/content/upload` - File upload
- `POST /api/v1/data-mash/create` - Create Data Mash

#### 5.2.3: End-to-End Flow

```
1. User uploads file
   ↓
2. Experience Plane → Runtime Intent: "content.upload"
   ↓
3. Runtime creates saga, logs to WAL
   ↓
4. Content Realm Manager handles intent
   ↓
5. Content Orchestrator:
   - Stores file (FileStorageAbstraction)
   - Stores in State Surface
   - Parses file (Content Orchestrator)
   ↓
6. Parsed artifacts stored (GCS + Supabase)
   ↓
7. User initiates Data Mash
   ↓
8. Experience Plane → Runtime Intent: "data_mash.create"
   ↓
9. Runtime creates DataMashSaga
   ↓
10. Insights Realm Manager handles intent
    ↓
11. Data Mash Orchestrator:
    - Phase 1: Data Quality (Insights Realm)
    - Phase 2: Semantic Interpretation (Content + Insights + Agent)
    - Phase 3: Semantic Mapping (Insights Realm)
    - Phase 4: Registration (Runtime)
    ↓
12. Data Mash result returned
```

---

## ✅ Implementation Checklist

### Phase 5.0: Realm Structure
- [ ] Create Content Realm Manager
- [ ] Update Content Orchestrator (saga composition pattern)
- [ ] Create Insights Realm Manager
- [ ] Create Insights Realm Orchestrator skeleton
- [ ] Register realms with Curator

### Phase 5.1: Data Mash
- [ ] Create DataMashSaga
- [ ] Create Data Quality Service
- [ ] Create Semantic Interpretation Service
- [ ] Create Semantic Mapping Service
- [ ] Create Data Mash Orchestrator
- [ ] Register Data Mash intent with Curator

### Phase 5.2: E2E Integration
- [ ] Wire file upload → file storage → parsing
- [ ] Wire parsing → Data Mash initiation
- [ ] Create Experience Plane handlers
- [ ] End-to-end testing

---

## 🚀 Next Steps

1. **Start with Phase 5.0** - Establish realm structure
2. **Implement Phase 5.1** - Data Mash capability
3. **Complete Phase 5.2** - E2E integration
4. **Test end-to-end** - Validate complete flow

---

**Status:** ✅ **READY TO START PHASE 5.0**
