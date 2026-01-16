"""
Platform SDK - Boundary Zone for Translation and Coordination

The Platform SDK is the explicit boundary zone where:
- Raw infrastructure data is translated into runtime-ready objects
- Smart City governance decisions are coordinated
- Business logic from old abstractions/services is recreated as translation logic

WHAT (SDK Role): I translate and coordinate between Runtime, Smart City, and Infrastructure
HOW (SDK Implementation): I use Smart City roles and abstractions to provide runtime-ready objects
"""

from .platform_sdk import PlatformSDK

__all__ = ['PlatformSDK']
