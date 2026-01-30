"""
Content Capability Intent Services (New Architecture)

These intent services use the new PlatformIntentService base class
and receive PlatformContext (ctx) for execution.

Architecture:
    - Services extend PlatformIntentService
    - Services receive PlatformContext (ctx) at execute time
    - Services access platform via ctx.platform, ctx.governance, ctx.reasoning
"""

# Intent services will be added here as capabilities are rebuilt
# For now, we start with a test service to validate the wiring

from .echo_service import EchoService

__all__ = [
    "EchoService",
]
