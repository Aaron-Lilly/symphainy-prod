# Migration Guide: Lifecycle States

## Overview

This guide explains how to use the new lifecycle state management for artifacts in the Artifact Plane.

## Lifecycle States

Artifacts now have three lifecycle states:

- **`draft`**: Initial state, can be modified
- **`accepted`**: Finalized, creates immutable version
- **`obsolete`**: No longer active

## Creating Artifacts with Lifecycle States

When creating an artifact, specify the initial lifecycle state:

```python
artifact_result = await artifact_plane.create_artifact(
    artifact_type="blueprint",
    artifact_id="blueprint_123",
    payload={"test": "data"},
    context=context,
    lifecycle_state="draft"  # Initial state
)
```

**Default:** If not specified, artifacts are created in `"draft"` state.

## Transitioning Lifecycle States

Use `transition_lifecycle_state()` to change an artifact's lifecycle state:

```python
success = await artifact_plane.transition_lifecycle_state(
    artifact_id="blueprint_123",
    tenant_id="tenant_123",
    new_state="accepted",
    transitioned_by="user_123",
    reason="Approved for production"
)
```

**Valid Transitions:**
- `draft` → `accepted` (finalizes artifact, creates immutable version)
- `draft` → `obsolete` (marks as obsolete)
- `accepted` → `obsolete` (marks accepted artifact as obsolete)

## Versioning

When an artifact transitions to `"accepted"`, an immutable version is created:

- Past versions are read-only
- Only the current version can transition states
- Versions are linked via `parent_artifact_id`

**Example:**
```python
# Get all versions of an artifact
versions = await artifact_plane.get_artifact_versions(
    artifact_id="blueprint_123",
    tenant_id="tenant_123"
)
```

## Filtering by Lifecycle State

List artifacts filtered by lifecycle state:

```python
artifacts = await artifact_plane.list_artifacts(
    tenant_id="tenant_123",
    lifecycle_state="accepted"  # Only accepted artifacts
)
```

## Migration from Legacy Code

**Before:**
```python
# Old code (no lifecycle states)
artifact = create_artifact(...)
```

**After:**
```python
# New code (with lifecycle states)
artifact = await artifact_plane.create_artifact(
    ...,
    lifecycle_state="draft"  # Explicit state
)

# Transition when ready
await artifact_plane.transition_lifecycle_state(
    artifact_id=artifact["artifact_id"],
    tenant_id=tenant_id,
    new_state="accepted"
)
```

## Best Practices

1. **Start in Draft**: Create artifacts in `"draft"` state for review
2. **Explicit Transitions**: Always specify `transitioned_by` and `reason`
3. **Version Control**: Use `get_artifact_versions()` to track changes
4. **Filter Appropriately**: Use lifecycle state filters in queries
