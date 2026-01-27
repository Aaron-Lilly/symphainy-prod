# Content Orchestrator Micro-Module Refactoring Plan

## Status: ⏳ **IN PROGRESS**

**Date:** January 27, 2026

---

## Problem Statement

ContentOrchestrator has grown to 4,300+ lines with 33+ handler methods, making it:
- Hard to maintain
- Difficult to test
- Prone to merge conflicts
- Violates single responsibility principle

---

## Solution: Micro-Module Architecture

### Handler Module Structure

```
orchestrators/
├── content_orchestrator.py (refactored - ~200 lines)
└── handlers/
    ├── __init__.py
    ├── base_handler.py ✅
    ├── artifact_management_handlers.py ✅
    ├── ingestion_handlers.py ⏳
    ├── parsing_handlers.py ⏳
    ├── embedding_handlers.py ⏳
    ├── materialization_handlers.py ⏳
    ├── query_handlers.py ⏳
    └── bulk_handlers.py ⏳
```

### Handler Module Responsibilities

1. **artifact_management_handlers.py** ✅
   - `register_artifact`
   - `retrieve_artifact`
   - `retrieve_artifact_metadata`
   - `archive_artifact`
   - `delete_artifact`

2. **ingestion_handlers.py** ⏳
   - `ingest_file`

3. **parsing_handlers.py** ⏳
   - `parse_content`

4. **embedding_handlers.py** ⏳
   - `create_deterministic_embeddings`
   - `extract_embeddings`

5. **materialization_handlers.py** ⏳
   - `save_materialization`

6. **query_handlers.py** ⏳
   - `get_parsed_file`
   - `get_semantic_interpretation`
   - `list_files`

7. **bulk_handlers.py** ⏳
   - `bulk_ingest_files`
   - `bulk_parse_files`
   - `bulk_extract_embeddings`
   - `bulk_interpret_data`
   - `get_operation_status`

---

## Refactoring Steps

### Phase 1: Create Handler Modules ✅
- [x] Create `handlers/` directory
- [x] Create `base_handler.py` with `BaseContentHandler`
- [x] Create `artifact_management_handlers.py` ✅

### Phase 2: Create Remaining Handler Modules ⏳
- [ ] Create `ingestion_handlers.py`
- [ ] Create `parsing_handlers.py`
- [ ] Create `embedding_handlers.py`
- [ ] Create `materialization_handlers.py`
- [ ] Create `query_handlers.py`
- [ ] Create `bulk_handlers.py`

### Phase 3: Refactor ContentOrchestrator ⏳
- [ ] Update `__init__` to initialize handler modules
- [ ] Update `handle_intent` to delegate to handlers
- [ ] Remove handler method implementations (moved to modules)
- [ ] Keep only orchestration logic

### Phase 4: Remove Legacy Aliases ⏳
- [ ] Remove legacy intent aliases from `service_factory.py`
- [ ] Update all intent names to artifact-centric
- [ ] Remove backward compatibility code

### Phase 5: Update Remaining Implementations ⏳
- [ ] Complete artifact management handlers (retrieve, archive, delete)
- [ ] Update bulk operations vocabulary
- [ ] Verify all handlers use artifact-centric patterns

---

## Implementation Pattern

### Handler Module Pattern

```python
from .base_handler import BaseContentHandler

class IngestionHandlers(BaseContentHandler):
    async def handle_ingest_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        # Implementation
        pass
```

### Orchestrator Delegation Pattern

```python
class ContentOrchestrator:
    def __init__(self, public_works: Optional[Any] = None):
        # Initialize handlers
        self.artifact_handlers = ArtifactManagementHandlers(public_works)
        self.ingestion_handlers = IngestionHandlers(public_works)
        # ... etc
    
    async def handle_intent(self, intent: Intent, context: ExecutionContext):
        intent_type = intent.intent_type
        
        if intent_type == "register_artifact":
            return await self.artifact_handlers.handle_register_artifact(intent, context)
        elif intent_type == "ingest_file":
            return await self.ingestion_handlers.handle_ingest_file(intent, context)
        # ... etc
```

---

## Benefits

1. **Maintainability:** Each handler module is focused and testable
2. **Scalability:** Easy to add new handlers without bloating orchestrator
3. **Testability:** Handler modules can be tested independently
4. **Clarity:** Clear separation of concerns
5. **No Legacy Debt:** Clean artifact-centric architecture

---

## Next Steps

1. Create remaining handler modules (stubs first, then implementations)
2. Refactor ContentOrchestrator to delegate to handlers
3. Remove all legacy aliases
4. Complete artifact management implementations
5. Update bulk operations vocabulary

---

**Last Updated:** January 27, 2026  
**Owner:** Development Team
