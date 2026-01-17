"""
Journey Orchestrator - Coordinates Journey/Coexistence Operations

Coordinates enabling services for workflow optimization, SOP management, and coexistence analysis.

WHAT (Orchestrator Role): I coordinate journey/coexistence operations
HOW (Orchestrator Implementation): I route intents to enabling services and compose results

⚠️ CRITICAL: Orchestrators coordinate within a single intent only.
They may NOT spawn long-running sagas, manage retries, or track cross-intent progress.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from ..enabling_services.workflow_conversion_service import WorkflowConversionService
from ..enabling_services.coexistence_analysis_service import CoexistenceAnalysisService
from ..enabling_services.visual_generation_service import VisualGenerationService
from ..agents.journey_liaison_agent import JourneyLiaisonAgent
from symphainy_platform.realms.outcomes.enabling_services.solution_synthesis_service import SolutionSynthesisService


class JourneyOrchestrator:
    """
    Journey Orchestrator - Coordinates journey/coexistence operations.
    
    Coordinates:
    - Workflow conversion
    - SOP generation
    - Coexistence analysis
    - Blueprint creation
    - Journey creation from blueprints
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Journey Orchestrator.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Initialize enabling services with Public Works
        self.workflow_conversion_service = WorkflowConversionService(public_works=public_works)
        self.visual_generation_service = VisualGenerationService(public_works=public_works)
        # Pass visual_generation_service to coexistence_analysis_service for blueprint charts
        self.coexistence_analysis_service = CoexistenceAnalysisService(
            public_works=public_works,
            visual_generation_service=self.visual_generation_service
        )
        self.journey_liaison_agent = JourneyLiaisonAgent(public_works=public_works)
        # Solution synthesis service for converting blueprints to solutions
        self.solution_synthesis_service = SolutionSynthesisService(public_works=public_works)
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent by coordinating enabling services.
        
        Args:
            intent: The intent to handle
            context: Runtime execution context
        
        Returns:
            Dict with "artifacts" and "events" keys
        """
        intent_type = intent.intent_type
        
        if intent_type == "optimize_process":
            return await self._handle_optimize_process(intent, context)
        elif intent_type == "generate_sop":
            return await self._handle_generate_sop(intent, context)
        elif intent_type == "create_workflow":
            return await self._handle_create_workflow(intent, context)
        elif intent_type == "analyze_coexistence":
            return await self._handle_analyze_coexistence(intent, context)
        elif intent_type == "create_blueprint":
            return await self._handle_create_blueprint(intent, context)
        elif intent_type == "create_solution_from_blueprint":
            return await self._handle_create_solution_from_blueprint(intent, context)
        elif intent_type == "generate_sop_from_chat":
            return await self._handle_generate_sop_from_chat(intent, context)
        elif intent_type == "sop_chat_message":
            return await self._handle_sop_chat_message(intent, context)
        else:
            raise ValueError(f"Unknown intent type: {intent_type}")
    
    async def _handle_optimize_process(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle optimize_process intent."""
        workflow_id = intent.parameters.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required for optimize_process intent")
        
        # Optimize workflow via WorkflowConversionService
        optimization_result = await self.workflow_conversion_service.optimize_workflow(
            workflow_id=workflow_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "optimization": optimization_result,
                "workflow_id": workflow_id
            },
            "events": [
                {
                    "type": "process_optimized",
                    "workflow_id": workflow_id
                }
            ]
        }
    
    async def _handle_generate_sop(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle generate_sop intent."""
        workflow_id = intent.parameters.get("workflow_id")
        chat_mode = intent.parameters.get("chat_mode", False)
        
        # If chat_mode is True or workflow_id is not provided, use chat generation
        if chat_mode or not workflow_id:
            return await self._handle_generate_sop_from_chat(intent, context)
        
        if not workflow_id:
            raise ValueError("workflow_id is required for generate_sop intent (or use chat_mode=True)")
        
        # Generate SOP via WorkflowConversionService
        sop_result = await self.workflow_conversion_service.generate_sop(
            workflow_id=workflow_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Generate SOP visualization
        visual_result = None
        try:
            visual_result = await self.visual_generation_service.generate_sop_visual(
                sop_data=sop_result,
                tenant_id=context.tenant_id,
                context=context
            )
        except Exception as e:
            self.logger.warning(f"Failed to generate SOP visualization: {e}")
        
        artifacts = {
            "sop": sop_result,
            "workflow_id": workflow_id
        }
        
        if visual_result and visual_result.get("success"):
            artifacts["sop_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        return {
            "artifacts": artifacts,
            "events": [
                {
                    "type": "sop_generated",
                    "workflow_id": workflow_id
                }
            ]
        }
    
    async def _handle_create_workflow(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle create_workflow intent.
        
        Supports two modes:
        1. From SOP: sop_id is provided
        2. From BPMN file: workflow_file_path is provided (and optionally workflow_type)
        """
        sop_id = intent.parameters.get("sop_id")
        workflow_file_path = intent.parameters.get("workflow_file_path")
        workflow_type = intent.parameters.get("workflow_type", "bpmn")
        
        if not sop_id and not workflow_file_path:
            raise ValueError("Either sop_id or workflow_file_path is required for create_workflow intent")
        
        # Mode 1: Create workflow from SOP
        if sop_id:
            # Create workflow via WorkflowConversionService
            workflow_result = await self.workflow_conversion_service.create_workflow(
                sop_id=sop_id,
                tenant_id=context.tenant_id,
                context=context
            )
        # Mode 2: Create workflow from BPMN file
        else:
            # Parse BPMN file and create workflow
            # For now, return a placeholder - full implementation would parse BPMN
            workflow_result = {
                "workflow_id": f"workflow_{workflow_file_path.split('/')[-1]}",
                "workflow_type": workflow_type,
                "source_file": workflow_file_path,
                "status": "created_from_file"
            }
            self.logger.info(f"Created workflow from file: {workflow_file_path}")
        
        # Generate workflow visualization
        visual_result = None
        try:
            visual_result = await self.visual_generation_service.generate_workflow_visual(
                workflow_data=workflow_result,
                tenant_id=context.tenant_id,
                context=context
            )
        except Exception as e:
            self.logger.warning(f"Failed to generate workflow visualization: {e}")
        
        artifacts = {
            "workflow": workflow_result,
            "sop_id": sop_id
        }
        
        if visual_result and visual_result.get("success"):
            artifacts["workflow_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        return {
            "artifacts": artifacts,
            "events": [
                {
                    "type": "workflow_created",
                    "sop_id": sop_id
                }
            ]
        }
    
    async def _handle_analyze_coexistence(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle analyze_coexistence intent."""
        workflow_id = intent.parameters.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required for analyze_coexistence intent")
        
        # Analyze coexistence via CoexistenceAnalysisService
        analysis_result = await self.coexistence_analysis_service.analyze_coexistence(
            workflow_id=workflow_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "coexistence_analysis": analysis_result,
                "workflow_id": workflow_id
            },
            "events": [
                {
                    "type": "coexistence_analyzed",
                    "workflow_id": workflow_id
                }
            ]
        }
    
    async def _handle_create_blueprint(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle create_blueprint intent."""
        workflow_id = intent.parameters.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required for create_blueprint intent")
        
        current_state_workflow_id = intent.parameters.get("current_state_workflow_id")
        
        # Create blueprint via CoexistenceAnalysisService
        blueprint_result = await self.coexistence_analysis_service.create_blueprint(
            workflow_id=workflow_id,
            tenant_id=context.tenant_id,
            context=context,
            current_state_workflow_id=current_state_workflow_id
        )
        
        return {
            "artifacts": {
                "blueprint": blueprint_result,
                "workflow_id": workflow_id
            },
            "events": [
                {
                    "type": "blueprint_created",
                    "workflow_id": workflow_id,
                    "blueprint_id": blueprint_result.get("blueprint_id")
                }
            ]
        }
    
    async def _handle_create_solution_from_blueprint(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle create_solution_from_blueprint intent - create platform solution from blueprint."""
        blueprint_id = intent.parameters.get("blueprint_id")
        if not blueprint_id:
            raise ValueError("blueprint_id is required for create_solution_from_blueprint intent")
        
        # Read blueprint from State Surface
        # Try to get from execution state first
        execution_state = await context.state_surface.get_execution_state(
            f"blueprint_{blueprint_id}",
            context.tenant_id
        )
        
        blueprint_data = None
        if execution_state and execution_state.get("artifacts", {}).get("blueprint"):
            blueprint_data = execution_state["artifacts"]["blueprint"]
        else:
            # Try to get from file reference
            blueprint_reference = f"blueprint:{context.tenant_id}:{context.session_id}:{blueprint_id}"
            blueprint_file = await context.state_surface.get_file(blueprint_reference)
            if blueprint_file:
                import json
                if isinstance(blueprint_file, bytes):
                    blueprint_data = json.loads(blueprint_file.decode('utf-8'))
                else:
                    blueprint_data = blueprint_file
        
        if not blueprint_data:
            raise ValueError(f"Blueprint {blueprint_id} not found")
        
        # Create solution via SolutionSynthesisService
        solution_result = await self.solution_synthesis_service.create_solution_from_artifact(
            solution_source="blueprint",
            source_id=blueprint_id,
            source_data=blueprint_data,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "solution": solution_result,
                "solution_id": solution_result.get("solution_id"),
                "blueprint_id": blueprint_id
            },
            "events": [
                {
                    "type": "solution_created_from_blueprint",
                    "solution_id": solution_result.get("solution_id"),
                    "blueprint_id": blueprint_id,
                    "session_id": context.session_id
                }
            ]
        }
    
    async def _handle_generate_sop_from_chat(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle generate_sop_from_chat intent - generate SOP from interactive chat."""
        session_id = intent.parameters.get("session_id")
        initial_requirements = intent.parameters.get("initial_requirements")
        
        # If no session_id, start new chat session
        if not session_id:
            chat_session = await self.journey_liaison_agent.initiate_sop_chat(
                initial_requirements=initial_requirements,
                tenant_id=context.tenant_id,
                context=context
            )
            
            return {
                "artifacts": {
                    "chat_session": chat_session,
                    "status": "chat_active"
                },
                "events": [
                    {
                        "type": "sop_chat_started",
                        "session_id": chat_session["session_id"]
                    }
                ]
            }
        
        # Generate SOP from existing chat session
        sop_result = await self.journey_liaison_agent.generate_sop_from_chat(
            session_id=session_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Generate SOP visualization
        visual_result = None
        try:
            visual_result = await self.visual_generation_service.generate_sop_visual(
                sop_data=sop_result["sop_data"],
                tenant_id=context.tenant_id,
                context=context
            )
        except Exception as e:
            self.logger.warning(f"Failed to generate SOP visualization: {e}")
        
        artifacts = {
            "sop": sop_result,
            "session_id": session_id,
            "source": "chat"
        }
        
        if visual_result and visual_result.get("success"):
            artifacts["sop_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        return {
            "artifacts": artifacts,
            "events": [
                {
                    "type": "sop_generated_from_chat",
                    "sop_id": sop_result["sop_id"],
                    "session_id": session_id
                }
            ]
        }
    
    async def _handle_sop_chat_message(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle sop_chat_message intent - process chat message in SOP generation session."""
        session_id = intent.parameters.get("session_id")
        message = intent.parameters.get("message")
        
        if not session_id:
            raise ValueError("session_id is required for sop_chat_message intent")
        if not message:
            raise ValueError("message is required for sop_chat_message intent")
        
        # Process chat message
        response = await self.journey_liaison_agent.process_chat_message(
            session_id=session_id,
            message=message,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "chat_response": response,
                "session_id": session_id
            },
            "events": [
                {
                    "type": "sop_chat_message_processed",
                    "session_id": session_id
                }
            ]
        }