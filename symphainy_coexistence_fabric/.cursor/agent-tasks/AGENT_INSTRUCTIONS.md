# Agent Instructions: Intent Services Pilot

**Task:** Implement 2 intent services following contracts and architectural requirements

---

## Your Mission

You are implementing intent services for the SymphAIny Coexistence Fabric platform. Your task is to create 2 intent services that follow our contract-driven development approach.

---

## What to Build

### 1. `ingest_file` Intent Service
- **File:** `symphainy_platform/realms/content/intent_services/ingest_file_service.py`
- **Contract:** `docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md`
- **Extends:** `BaseIntentService`

### 2. `save_materialization` Intent Service
- **File:** `symphainy_platform/realms/content/intent_services/save_materialization_service.py`
- **Contract:** `docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md`
- **Extends:** `BaseIntentService`

---

## How to Approach This

### Step 1: Read the Contracts
1. Read the intent contract for each service
2. Understand the parameters, returns, and flow
3. Note the implementation details section

### Step 2: Review Base Classes
1. Read `symphainy_platform/bases/intent_service_base.py`
2. Understand what BaseIntentService provides
3. See what methods you need to implement

### Step 3: Review Architectural Requirements
1. Read `.cursor/ARCHITECTURAL_REQUIREMENTS.md`
2. Understand the patterns and constraints
3. Note what you MUST and MUST NOT do

### Step 4: Review Reference Implementations
1. Look at existing handlers in `symphainy_platform/realms/content/orchestrators/handlers/`
2. Understand the business logic
3. **But follow new architecture patterns** (BaseIntentService, not BaseContentHandler)

### Step 5: Implement
1. Create the intent service class
2. Extend BaseIntentService
3. Implement `execute()` method
4. Follow contract specifications exactly
5. Report telemetry
6. Register artifacts
7. Validate contract compliance

---

## Critical Rules

### ✅ MUST DO
- Extend BaseIntentService
- Implement contract specifications exactly
- Report telemetry via Nurse SDK (`self.record_telemetry()`)
- Register artifacts via State Surface (`self.register_artifact()`)
- Use Public Works abstractions only
- Validate parameters per contract
- Return structured artifacts per contract

### ❌ MUST NOT DO
- Access infrastructure directly (use Public Works only)
- Skip telemetry reporting
- Skip artifact registration
- Bypass Runtime Execution Engine
- Violate architectural patterns
- Use BaseContentHandler (use BaseIntentService instead)

---

## Key Patterns

### Telemetry Reporting
```python
await self.record_telemetry(
    telemetry_data={
        "action": "execute",
        "status": "started",
        "execution_id": context.execution_id
    },
    tenant_id=context.tenant_id
)
```

### Artifact Registration
```python
artifact = self.create_artifact_record(
    artifact_id=artifact_id,
    artifact_type="file",
    context=context,
    semantic_descriptor=SemanticDescriptor(schema="file_v1"),
    lifecycle_state=LifecycleState.PENDING
)

await self.register_artifact(artifact, context)
```

### Public Works Access
```python
# Get abstraction from Public Works
ingestion_abstraction = self.public_works.get_ingestion_abstraction()
file_storage = self.public_works.get_file_storage_abstraction()
```

---

## Questions?

If you encounter ambiguity:
1. Check the intent contract first
2. Check architectural requirements
3. Check base class documentation
4. Check reference implementations (for business logic only)
5. If still unclear, note it in your implementation comments

---

## Success Criteria

Your implementation is successful if:
- ✅ Code compiles without errors
- ✅ Follows BaseIntentService pattern
- ✅ Implements contract specifications
- ✅ Reports telemetry
- ✅ Registers artifacts
- ✅ Follows architectural requirements

---

**Good luck! Build with contracts, follow patterns, report telemetry, register artifacts.**
