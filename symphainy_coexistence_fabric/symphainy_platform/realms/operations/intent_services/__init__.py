"""
Operations Realm Intent Services

Intent services for the Operations Realm. Each service implements a single intent type
following the BaseIntentService pattern.

Architecture:
- Intent services are pure services (agents handled at orchestrator layer)
- All services use Public Works abstractions (no direct infrastructure)
- Artifacts stored in Artifact Plane (not execution state)
- Services are exposed as SOA APIs by orchestrator, wrapped as MCP Tools for agents

Services:
- OptimizeProcessService: Optimize workflow processes (friction removal)
- GenerateSOPService: Generate SOP from workflow
- CreateWorkflowService: Create workflow from SOP or BPMN
- AnalyzeCoexistenceService: Analyze coexistence opportunities
- GenerateSOPFromChatService: Start interactive SOP generation
- SOPChatMessageService: Process chat message in SOP session

Naming Convention:
- Realm name: Operations Realm
- Solution: OperationsSolution (platform construct)
- Artifact prefix: operations_*
"""

from .optimize_process_service import OptimizeProcessService
from .generate_sop_service import GenerateSOPService
from .create_workflow_service import CreateWorkflowService
from .analyze_coexistence_service import AnalyzeCoexistenceService
from .generate_sop_from_chat_service import GenerateSOPFromChatService
from .sop_chat_message_service import SOPChatMessageService

__all__ = [
    "OptimizeProcessService",
    "GenerateSOPService",
    "CreateWorkflowService",
    "AnalyzeCoexistenceService",
    "GenerateSOPFromChatService",
    "SOPChatMessageService"
]
