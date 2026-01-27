"""
Operations Solution Journey Orchestrators

Journey orchestrators for the Operations Solution. Each orchestrator composes
intent services into coherent user journeys.

Architecture:
- Journeys are thin composers (no business logic)
- Journeys call intent services from Operations Realm
- Journeys expose SOA APIs for MCP server registration
- Journeys track telemetry and journey execution

Journeys:
- WorkflowManagementJourney: Create and manage workflows
- SOPManagementJourney: Generate and manage SOPs
- CoexistenceAnalysisJourney: Analyze coexistence opportunities
- ProcessOptimizationJourney: Optimize workflow processes
"""

from .workflow_management_journey import WorkflowManagementJourney
from .sop_management_journey import SOPManagementJourney
from .coexistence_analysis_journey import CoexistenceAnalysisJourney
from .process_optimization_journey import ProcessOptimizationJourney

__all__ = [
    "WorkflowManagementJourney",
    "SOPManagementJourney",
    "CoexistenceAnalysisJourney",
    "ProcessOptimizationJourney"
]
