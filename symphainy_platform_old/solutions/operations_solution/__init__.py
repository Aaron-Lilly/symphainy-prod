"""
Operations Solution

Platform construct that composes Operations Realm journeys, exposes SOA APIs,
and provides MCP server for agent integration.

The Operations Solution coordinates:
- Workflow Management Journey
- SOP Management Journey
- Coexistence Analysis Journey
- Process Optimization Journey

Naming Convention:
- Operations Realm = user-facing domain (workflows, SOPs, coexistence)
- OperationsSolution = platform construct (composes journeys)
- Journey = platform capability (invisible to users)
"""

from .operations_solution import OperationsSolution

__all__ = ["OperationsSolution"]
