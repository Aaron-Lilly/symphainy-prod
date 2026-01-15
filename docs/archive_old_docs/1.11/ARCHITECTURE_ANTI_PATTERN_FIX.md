# Architecture Anti-Pattern Fix

## Issue Identified

The test was creating services **directly**, bypassing the Foundation layer. This is an anti-pattern in the new architecture where:

1. **Runtime Plane** creates StateSurface (single source of truth)
2. **Foundations** create services with StateSurface
3. **Services** should be accessed through Foundations, not created directly

## Anti-Pattern (Before)

```python
# ❌ WRONG: Creating service directly
structured_service = StructuredParsingService(
    state_surface=state_surface,
    platform_gateway=platform_gateway
)
```

## Correct Pattern (After)

```python
# ✅ CORRECT: Using Foundation layer
content_realm = ContentRealmFoundationService(
    state_surface=state_surface,
    platform_gateway=platform_gateway,
    curator=curator
)
await content_realm.initialize()

# Get service through Foundation
structured_service = content_realm.get_structured_service()
```

## Why This Matters

1. **Single Source of Truth**: StateSurface is created in Runtime Plane and passed through Foundations
2. **Proper Initialization**: Foundations ensure services are properly wired with all dependencies
3. **Service Registration**: Services are registered with Curator through Foundations
4. **Architecture Compliance**: Follows the same pattern as `main.py`

## Changes Made

1. ✅ Updated test to use `ContentRealmFoundationService`
2. ✅ Services now accessed through Foundation (not created directly)
3. ✅ Fixed import paths in `ContentRealmFoundationService`
4. ✅ Test now follows proper architecture pattern

## Remaining Issue

The test is still failing with "File not found" error, but this is now a **debugging issue**, not an architectural one. The architecture is correct - we just need to debug why files stored in StateSurface aren't being found when the service tries to retrieve them.

**Next Steps**:
1. Add debug logging to see what's in StateSurface memory store
2. Verify file references match exactly
3. Check if there's a timing issue with async operations

## Key Takeaway

**Everything must go through State Surface/Runtime Plane and Foundations**. Services should never be created directly - they must be created through their Foundation, which ensures proper wiring and architecture compliance.
