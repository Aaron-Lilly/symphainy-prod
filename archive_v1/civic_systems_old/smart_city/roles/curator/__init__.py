"""
Curator Role - Capability and service registry management.

Curator owns:
- Capability Registry (Supabase)
- Service Registry (Supabase - projection of Consul + governance)
- Agent Registry (Supabase)
- Contract Registry (Supabase)

Curator uses Consul (via Public Works) for service liveness.
Curator composes Runtime Registry Views (policy-aware, ephemeral).
"""
