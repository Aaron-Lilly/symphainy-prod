"""
Solutions - Solution Layer for Platform

Solutions are the top-level organizational unit that compose journeys,
expose SOA APIs, and wire up with the frontend via Experience SDK.

WHAT (Solution Role): I compose journeys and expose capabilities
HOW (Solution Implementation): I coordinate journey orchestrators, expose SOA APIs and MCP tools

Key Principle: The platform runs Solutions; Solutions run systems.
Solutions bind domain services to external systems.
"""

from .content_solution import ContentSolution

__all__ = ["ContentSolution"]
