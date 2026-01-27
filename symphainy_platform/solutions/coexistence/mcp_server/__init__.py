"""
Coexistence MCP Server

Exposes Coexistence SOA APIs as MCP Tools for agent consumption.
Tool naming: coexist_{action}
"""

from .coexistence_mcp_server import CoexistenceMCPServer

__all__ = ["CoexistenceMCPServer"]
