"""
Insights Solution MCP Server

Exposes Insights Solution SOA APIs as MCP Tools for agent consumption.

Tool naming convention: insights_{action}
Example: insights_assess_quality, insights_analyze_structured
"""

from .insights_solution_mcp_server import InsightsSolutionMCPServer

__all__ = ["InsightsSolutionMCPServer"]
