"""
Outcomes Solution MCP Server

Exposes Outcomes Solution SOA APIs as MCP Tools for agent consumption.

Tool naming convention: outcomes_{action}
Example: outcomes_synthesize, outcomes_generate_roadmap
"""

from .outcomes_solution_mcp_server import OutcomesSolutionMCPServer

__all__ = ["OutcomesSolutionMCPServer"]
