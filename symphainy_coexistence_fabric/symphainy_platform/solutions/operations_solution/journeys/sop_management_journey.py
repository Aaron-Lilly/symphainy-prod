"""
SOP Management Journey Orchestrator

Composes SOP management operations into a coherent user journey.

WHAT (Journey Role): I compose SOP management operations
HOW (Journey Implementation): I orchestrate SOP service calls
    and expose SOA APIs for MCP server

Architecture:
- Journey is thin composer (delegates to intent services)
- Uses GenerateSOPService, GenerateSOPFromChatService, SOPChatMessageService
- Exposes generate_sop, start_sop_chat, sop_chat_message SOA APIs
- Records telemetry and journey execution
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utilities import get_logger, generate_event_id
from symphainy_platform.bases.orchestrator_base import BaseOrchestrator
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_coexistence_fabric.symphainy_platform.realms.operations import (
    GenerateSOPService,
    GenerateSOPFromChatService,
    SOPChatMessageService
)


class SOPManagementJourney(BaseOrchestrator):
    """
    SOP Management Journey Orchestrator.
    
    Composes:
    - GenerateSOPService for SOP generation from workflow
    - GenerateSOPFromChatService for interactive SOP creation
    - SOPChatMessageService for chat message processing
    
    SOA APIs:
    - generate_sop: Generate SOP from workflow
    - start_sop_chat: Start interactive SOP session
    - sop_chat_message: Process chat message
    """
    
    JOURNEY_ID = "journey_operations_sop_management"
    
    def __init__(self, public_works=None, state_surface=None):
        """Initialize SOPManagementJourney."""
        super().__init__(
            orchestrator_id="sop_management_journey",
            public_works=public_works
        )
        self.state_surface = state_surface
        
        # Initialize intent services
        self.generate_sop_service = GenerateSOPService(
            public_works=public_works,
            state_surface=state_surface
        )
        self.generate_sop_from_chat_service = GenerateSOPFromChatService(
            public_works=public_works,
            state_surface=state_surface
        )
        self.sop_chat_message_service = SOPChatMessageService(
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def compose_journey(
        self,
        journey_id: str,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose SOP management journey.
        
        Args:
            journey_id: The journey being composed
            context: Execution context
            journey_params: Journey-specific parameters
            
        Returns:
            Dict with artifacts and events
        """
        journey_execution_id = f"sop_journey_{generate_event_id()}"
        start_time = datetime.utcnow()
        
        self.logger.info(f"Starting SOP management journey: {journey_execution_id}")
        
        try:
            params = journey_params or {}
            
            if journey_id in ["sop_management", "generate_sop"]:
                result = await self.generate_sop_service.execute(context, params)
            elif journey_id in ["start_sop_chat", "generate_sop_from_chat"]:
                result = await self.generate_sop_from_chat_service.execute(context, params)
            elif journey_id == "sop_chat_message":
                result = await self.sop_chat_message_service.execute(context, params)
            else:
                raise ValueError(f"Unknown journey_id: {journey_id}")
            
            # Record telemetry
            end_time = datetime.utcnow()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            await self.record_telemetry(
                telemetry_data={
                    "journey_id": journey_id,
                    "journey_execution_id": journey_execution_id,
                    "latency_ms": latency_ms,
                    "status": "completed"
                },
                tenant_id=context.tenant_id
            )
            
            # Add journey metadata
            result["journey_execution_id"] = journey_execution_id
            result["journey_id"] = self.JOURNEY_ID
            
            return result
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={
                    "journey_id": journey_id,
                    "journey_execution_id": journey_execution_id,
                    "status": "failed",
                    "error": str(e)
                },
                tenant_id=context.tenant_id
            )
            raise
    
    def get_soa_apis(self) -> Dict[str, Callable]:
        """Get SOA APIs for this journey."""
        return {
            "generate_sop": self._handle_generate_sop_soa,
            "start_sop_chat": self._handle_start_sop_chat_soa,
            "sop_chat_message": self._handle_sop_chat_message_soa
        }
    
    async def _handle_generate_sop_soa(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """SOA API handler for generate_sop."""
        return await self.compose_journey(
            journey_id="generate_sop",
            context=context,
            journey_params=params
        )
    
    async def _handle_start_sop_chat_soa(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """SOA API handler for start_sop_chat."""
        return await self.compose_journey(
            journey_id="start_sop_chat",
            context=context,
            journey_params=params
        )
    
    async def _handle_sop_chat_message_soa(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """SOA API handler for sop_chat_message."""
        return await self.compose_journey(
            journey_id="sop_chat_message",
            context=context,
            journey_params=params
        )
