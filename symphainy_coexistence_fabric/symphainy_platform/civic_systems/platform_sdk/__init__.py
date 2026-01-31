"""
Platform SDK - The Front Door for Building on Symphainy

The Platform SDK provides the unified execution context (ctx) that intent services
and capabilities use to interact with the platform.

Four Services on ctx:
- ctx.platform    — Capability-oriented operations (parse, analyze, visualize, etc.)
- ctx.governance  — Smart City SDKs (all 9 roles)
- ctx.reasoning   — Agentic (LLM, agents)
- ctx.experience  — Experience metadata

Plus Runtime-provided resources:
- ctx.state_surface  — State storage/retrieval (Runtime owns)
- ctx.wal            — Write-ahead log (Runtime owns)
- ctx.artifacts      — Artifact registry (Runtime owns)

Usage:
    # Intent service receives ctx
    async def execute(self, ctx: PlatformContext):
        # Parse a file
        parsed = await ctx.platform.parse(file_ref, file_type="pdf")
        
        # Store result via Runtime state
        await ctx.state_surface.store_file_reference(...)
        
        # Invoke an LLM
        result = await ctx.reasoning.llm.complete(prompt)
        
        # Check data boundary
        access = await ctx.governance.data_steward.request_data_access(...)
        
        return {"artifacts": {...}, "events": [...]}

See: docs/architecture/PLATFORM_SDK_ARCHITECTURE.md
"""

from .context import PlatformContext, PlatformContextFactory
from .services.governance_service import GovernanceService
from .services.reasoning_service import ReasoningService
from .services.platform_service import PlatformService
from .intent_service_base import PlatformIntentService

__all__ = [
    "PlatformContext",
    "PlatformContextFactory",
    "GovernanceService",
    "ReasoningService",
    "PlatformService",
    "PlatformIntentService",
]
