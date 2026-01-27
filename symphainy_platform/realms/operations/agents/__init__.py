"""
Operations Realm Agents

Agents for Operations Realm capabilities:
- Coexistence analysis and friction removal
- SOP generation
- Interactive SOP building (liaison)
- Workflow optimization
"""

# Operations Realm agents (migrated from journey realm)
from .coexistence_analysis_agent import CoexistenceAnalysisAgent
from .sop_generation_agent import SOPGenerationAgent
from .operations_liaison_agent import OperationsLiaisonAgent

# Import from Agentic SDK
try:
    from symphainy_platform.civic_systems.agentic.agents.workflow_optimization_specialist import WorkflowOptimizationSpecialist
except ImportError:
    WorkflowOptimizationSpecialist = None

__all__ = [
    "CoexistenceAnalysisAgent",
    "SOPGenerationAgent", 
    "OperationsLiaisonAgent",
    "WorkflowOptimizationSpecialist"
]
