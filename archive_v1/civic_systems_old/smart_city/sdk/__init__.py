"""
Smart City SDK - Boundary zone for Realms.

NOTE: No role-specific SDKs exist here. All SDK methods go in Platform SDK.

Platform SDK (civic_systems/platform_sdk/platform_sdk.py) contains:
- Security Guard methods (ensure_user_can, validate_tenant_access)
- Data Steward methods (file operations, metadata queries)
- Traffic Cop methods (session management)
- Post Office methods (event publishing, message delivery)
- Conductor methods (workflow orchestration)
- Librarian methods (search queries)
- Nurse methods (telemetry collection)
- City Manager methods (policy management)
- Curator methods (capability registration, runtime view composition)

All SDK methods translate Realm intent → runtime contract shape.
They query registries, call Public Works abstractions, prepare context.
They do NOT execute anything.
They do NOT call primitives directly (that's Runtime's job).
"""
