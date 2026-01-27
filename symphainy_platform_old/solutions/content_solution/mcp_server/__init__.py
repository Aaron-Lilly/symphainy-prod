"""
Content Solution MCP Server

Exposes Content Solution SOA APIs as MCP Tools for agent consumption.
Journey orchestrators "provide" MCP tools through the solution server.
"""

from .content_solution_mcp_server import ContentSolutionMCPServer

__all__ = ["ContentSolutionMCPServer"]
