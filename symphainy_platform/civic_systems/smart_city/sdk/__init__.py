"""
Smart City SDK - Coordination Logic

SDKs prepare execution contracts. Runtime validates and executes them.

Used by: Experience, Solution, Realms
Provides: Coordination, orchestration, service discovery

⚠️ CRITICAL: SDKs must NOT depend on Runtime.
SDKs may depend on:
- Public Works abstractions
- Registries
- Policy libraries
- Context objects
"""

from .security_guard_sdk import SecurityGuardSDK
from .traffic_cop_sdk import TrafficCopSDK
from .post_office_sdk import PostOfficeSDK

__all__ = [
    "SecurityGuardSDK",
    "TrafficCopSDK",
    "PostOfficeSDK",
]
