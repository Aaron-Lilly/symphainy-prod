"""
Insights Solution - Insights Realm Platform Solution

The platform Solution that composes Insights Realm journeys, exposes SOA APIs,
and wires up with the frontend via Experience SDK.

Key Components:
- InsightsSolution: Main solution class
- Journey Orchestrators: Compose intent services into journeys
- InsightsSolutionMCPServer: Exposes SOA APIs as MCP tools

Naming Convention:
- Realm: Insights Realm
- Solution: Platform construct (InsightsSolution)
- Artifacts: insights_* prefix (e.g., insights_quality_report, insights_analysis)
"""

from .insights_solution import InsightsSolution

__all__ = ["InsightsSolution"]
