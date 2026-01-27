"""
Operations Realm - Workflow, SOP, and Coexistence Operations

The Operations Realm is responsible for managing workflows, SOPs, process optimization,
and coexistence analysis. This was previously called "Journey Realm" but renamed to
avoid collision with "journey" as a platform capability.

WHAT (Realm Role): I manage operational workflows, SOPs, and coexistence analysis
HOW (Realm Implementation): I provide intent services for process operations

Key Principles:
- Intent services are pure services (agents handled at orchestrator layer)
- All services use Public Works abstractions (no direct infrastructure)
- Artifacts stored in Artifact Plane (not execution state)
- Services exposed as SOA APIs by orchestrator, wrapped as MCP Tools for agents

Naming Convention:
- Realm name: Operations Realm (not Journey Realm)
- Solution: OperationsSolution (platform construct that composes journeys)
- Artifact prefix: operations_* (e.g., operations_workflow, operations_sop)
- "Journey" = platform capability (invisible to users)
- "Operations" = user-facing realm for workflows, SOPs, coexistence
"""

from .intent_services import (
    OptimizeProcessService,
    GenerateSOPService,
    CreateWorkflowService,
    AnalyzeCoexistenceService,
    GenerateSOPFromChatService,
    SOPChatMessageService
)

__all__ = [
    "OptimizeProcessService",
    "GenerateSOPService",
    "CreateWorkflowService",
    "AnalyzeCoexistenceService",
    "GenerateSOPFromChatService",
    "SOPChatMessageService"
]
