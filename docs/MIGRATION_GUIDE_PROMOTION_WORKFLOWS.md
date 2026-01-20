# Migration Guide: Promotion Workflows

## Overview

This guide explains how to use the new promotion workflows for moving data through the four-class framework.

## Promotion Workflows

### Working Material → Record of Fact

Promote temporary Working Materials to persistent Records of Fact:

```python
from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK

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

**Record Types:**
- `deterministic_embedding`: Deterministic representation
- `semantic_embedding`: Semantic embedding
- `interpretation`: Interpreted meaning
- `conclusion`: Final conclusion

---

### Purpose-Bound Outcome → Platform DNA

Promote accepted artifacts to Platform DNA:

```python
from symphainy_platform.civic_systems.smart_city.services.curator_service import CuratorService

# First, ensure artifact is in "accepted" state
await artifact_plane.transition_lifecycle_state(
    artifact_id="blueprint_123",
    tenant_id="tenant_123",
    new_state="accepted"
)

# Then promote to Platform DNA
registry_id = await curator_service.promote_to_platform_dna(
    artifact_id="blueprint_123",
    tenant_id="tenant_123",
    registry_type="solution",
    registry_name="Workflow Optimization Solution",
    promoted_by="curator_123"
)
```

**Registry Types:**
- `solution`: For blueprints and solutions
- `intent`: For workflows and intents
- `realm`: For journeys and realms

---

## Complete Workflow Example

```python
# 1. Create Purpose-Bound Outcome
artifact_result = await artifact_plane.create_artifact(
    artifact_type="blueprint",
    artifact_id="blueprint_123",
    payload={"test": "data"},
    context=context,
    lifecycle_state="draft"
)

# 2. Transition to accepted
await artifact_plane.transition_lifecycle_state(
    artifact_id=artifact_result["artifact_id"],
    tenant_id="tenant_123",
    new_state="accepted",
    transitioned_by="user_123"
)

# 3. Promote to Platform DNA
registry_id = await curator_service.promote_to_platform_dna(
    artifact_id=artifact_result["artifact_id"],
    tenant_id="tenant_123",
    registry_type="solution",
    registry_name="Test Solution"
)
```

## Best Practices

1. **Explicit Promotion**: Always use explicit promotion methods
2. **Lifecycle First**: Ensure artifacts are "accepted" before promoting to Platform DNA
3. **Generalization**: Platform DNA entries are automatically de-identified
4. **Versioning**: Registry entries are versioned and immutable
