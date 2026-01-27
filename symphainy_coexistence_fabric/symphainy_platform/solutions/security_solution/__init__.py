"""
Security Solution

Platform construct that composes Security Realm journeys, exposes SOA APIs,
and provides MCP server for agent integration.

The Security Solution is foundational - all other solutions depend on it
for authentication and authorization.

Architecture:
- Wraps existing Security Guard SDK infrastructure
- Provides consistent solution pattern interface
- Enables MCP tools for agent-based security operations
- Composes Authentication and Registration journeys
"""

from .security_solution import SecuritySolution

__all__ = ["SecuritySolution"]
