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
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from ..enabling_services.workflow_conversion_service import WorkflowConversionService
from ..enabling_services.coexistence_analysis_service import CoexistenceAnalysisService
from ..enabling_services.visual_generation_service import VisualGenerationService
from ..agents.journey_liaison_agent import JourneyLiaisonAgent
from symphainy_platform.realms.outcomes.enabling_services.solution_synthesis_service import SolutionSynthesisService
from symphainy_platform.civic_systems.artifact_plane.artifact_plane import ArtifactPlane


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
    
    def __init__(self, public_works: Optional[Any] = None, artifact_plane: Optional[ArtifactPlane] = None):
        """
        Initialize Journey Orchestrator.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
            artifact_plane: Artifact Plane for managing Purpose-Bound Outcomes
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        self.artifact_plane = artifact_plane
        
        # Initialize enabling services with Public Works
        self.workflow_conversion_service = WorkflowConversionService(public_works=public_works)
        self.visual_generation_service = VisualGenerationService(public_works=public_works)
        # Pass visual_generation_service to coexistence_analysis_service for blueprint charts
        self.coexistence_analysis_service = CoexistenceAnalysisService(
            public_works=public_works,
            visual_generation_service=self.visual_generation_service
        )
        # Initialize agents (agentic forward pattern)
        self.sop_generation_agent = SOPGenerationAgent(
            agent_definition_id="sop_generation_agent",
            public_works=public_works
        )
        self.journey_liaison_agent = JourneyLiaisonAgent(
            agent_definition_id="journey_liaison_agent",
            public_works=public_works,
            sop_generation_agent=self.sop_generation_agent
        )
        # Solution synthesis service for converting blueprints to solutions
        self.solution_synthesis_service = SolutionSynthesisService(public_works=public_works)
        
        # Initialize runtime context hydration service (for call site responsibility)
        from symphainy_platform.civic_systems.agentic.services.runtime_context_hydration_service import RuntimeContextHydrationService
        self.runtime_context_service = RuntimeContextHydrationService()
        
        # Initialize health monitoring and telemetry (lazy initialization)
        self.telemetry_service = None
        self.health_monitor = None
    
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
        # Initialize health monitoring and telemetry if not already done
        if not self.health_monitor:
            from symphainy_platform.civic_systems.agentic.telemetry.agentic_telemetry_service import AgenticTelemetryService
            from symphainy_platform.civic_systems.orchestrator_health import OrchestratorHealthMonitor
            
            if self.public_works:
                try:
                    self.telemetry_service = getattr(self.public_works, 'telemetry_service', None)
                except:
                    pass
            
            if not self.telemetry_service:
                self.telemetry_service = AgenticTelemetryService()
            
            self.health_monitor = OrchestratorHealthMonitor(telemetry_service=self.telemetry_service)
            await self.health_monitor.start_monitoring("journey_orchestrator")
        
        from datetime import datetime
        start_time = datetime.utcnow()
        intent_type = intent.intent_type
        success = True
        error_message = None
        result = None
        
        try:
            if intent_type == "optimize_process":
                result = await self._handle_optimize_process(intent, context)
            elif intent_type == "generate_sop":
                result = await self._handle_generate_sop(intent, context)
            elif intent_type == "create_workflow":
                result = await self._handle_create_workflow(intent, context)
            elif intent_type == "analyze_coexistence":
                result = await self._handle_analyze_coexistence(intent, context)
            # Note: create_blueprint moved to Outcomes Realm (blueprints are Purpose-Bound Outcomes)
            elif intent_type == "generate_sop_from_chat":
                result = await self._handle_generate_sop_from_chat(intent, context)
            elif intent_type == "sop_chat_message":
                result = await self._handle_sop_chat_message(intent, context)
            else:
                raise ValueError(f"Unknown intent type: {intent_type}")
            
            return result
            
        except Exception as e:
            success = False
            error_message = str(e)
            self.logger.error(f"Intent handling failed: {e}", exc_info=True)
            raise
        
        finally:
            # Record telemetry
            end_time = datetime.utcnow()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            try:
                await self.telemetry_service.record_orchestrator_execution(
                    orchestrator_id="journey_orchestrator",
                    orchestrator_name="Journey Orchestrator",
                    intent_type=intent_type,
                    latency_ms=latency_ms,
                    context=context,
                    success=success,
                    error_message=error_message
                )
                
                await self.health_monitor.record_intent_handled(
                    orchestrator_id="journey_orchestrator",
                    intent_type=intent_type,
                    success=success,
                    latency_ms=latency_ms
                )
            except Exception as e:
                self.logger.debug(f"Telemetry recording failed (non-critical): {e}")
    
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
                "optimization": create_structured_artifact(
                    result_type="optimization",
                    semantic_payload={
                        "workflow_id": workflow_id,
                        "optimization_id": optimization_result.get("optimization_id"),
                        "status": optimization_result.get("status")
                    },
                    renderings={"optimization": optimization_result}
                )
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
        
        # Extract semantic payload
        semantic_payload = {
            "sop_id": sop_result.get("sop_id"),
            "workflow_id": workflow_id,
            "title": sop_result.get("title"),
            "status": sop_result.get("status")
        }
        
        # Collect renderings
        renderings = {
            "sop": sop_result
        }
        
        if visual_result and visual_result.get("success"):
            renderings["sop_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        # Create structured artifact
        structured_artifact = create_structured_artifact(
            result_type="sop",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        return {
            "artifacts": {
                "sop": structured_artifact
            },
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
            self.logger.info(f"Parsing BPMN file: {workflow_file_path}")
            
            # Get BPMN file content
            bpmn_xml = None
            
            # Try to get from parsed file if workflow_file_path is a file_id
            if self.public_works:
                try:
                    # Check if it's a parsed file ID
                    from symphainy_platform.realms.content.enabling_services.file_parser_service import FileParserService
                    file_parser_service = FileParserService(public_works=self.public_works)
                    parsed_content = await file_parser_service.get_parsed_file(
                        parsed_file_id=workflow_file_path,
                        tenant_id=context.tenant_id,
                        context=context
                    )
                    
                    if parsed_content:
                        # Extract BPMN XML from parsed content
                        bpmn_xml = parsed_content.get("data") or parsed_content.get("content")
                        if isinstance(bpmn_xml, bytes):
                            bpmn_xml = bpmn_xml.decode('utf-8')
                        elif isinstance(bpmn_xml, dict):
                            # Try to get XML from metadata or content field
                            bpmn_xml = parsed_content.get("metadata", {}).get("bpmn_xml") or str(parsed_content.get("content", ""))
                except Exception as e:
                    self.logger.debug(f"Could not get parsed file: {e}, trying file storage")
            
            # If not found, try file storage abstraction
            if not bpmn_xml and self.public_works:
                try:
                    file_storage = self.public_works.get_file_storage_abstraction()
                    if file_storage:
                        # workflow_file_path might be a storage location
                        file_content = await file_storage.download_file(workflow_file_path)
                        if file_content:
                            if isinstance(file_content, bytes):
                                bpmn_xml = file_content.decode('utf-8')
                            else:
                                bpmn_xml = str(file_content)
                except Exception as e:
                    self.logger.warning(f"Could not get file from storage: {e}")
            
            # Parse BPMN XML via WorkflowConversionService
            if bpmn_xml:
                workflow_result = await self.workflow_conversion_service.parse_bpmn_file(
                    bpmn_xml=bpmn_xml,
                    workflow_id=None,  # Will be generated
                    tenant_id=context.tenant_id,
                    context=context
                )
                workflow_result["source_file"] = workflow_file_path
                workflow_result["workflow_type"] = workflow_type
            else:
                # Fallback: Create basic workflow structure if BPMN not available
                self.logger.warning(f"BPMN content not found for {workflow_file_path}, creating basic workflow structure")
                workflow_id = generate_event_id()
                workflow_result = {
                    "workflow_id": workflow_id,
                    "workflow_type": workflow_type,
                    "source_file": workflow_file_path,
                    "workflow_status": "created_from_file",
                    "workflow_content": {
                        "workflow_id": workflow_id,
                        "workflow_name": f"Workflow from {workflow_file_path.split('/')[-1]}",
                        "tasks": [],
                        "sequence_flows": []
                    }
                }
        
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
        
        workflow_id = workflow_result.get("workflow_id")
        
        # Extract semantic payload (the meaning)
        semantic_payload = {
            "workflow_id": workflow_id,
            "workflow_type": workflow_result.get("workflow_type"),
            "status": workflow_result.get("status"),
            "sop_id": sop_id,
            "source_file": workflow_result.get("source_file")
        }
        
        # Collect renderings (the views)
        renderings = {
            "workflow": workflow_result
        }
        
        if visual_result and visual_result.get("success"):
            renderings["workflow_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        # Create artifact in Artifact Plane (Purpose-Bound Outcome)
        artifact_id = None
        if self.artifact_plane:
            try:
                # Full artifact payload (semantic + renderings)
                artifact_payload = {
                    "result_type": "workflow",
                    "semantic_payload": semantic_payload,
                    "renderings": renderings
                }
                
                artifact_result = await self.artifact_plane.create_artifact(
                    artifact_type="workflow",
                    artifact_id=workflow_id,  # Use workflow_id as artifact_id
                    payload=artifact_payload,
                    context=context,
                    lifecycle_state="draft",  # Initial state
                    owner="client",
                    purpose="delivery",
                    source_artifact_ids=[sop_id] if sop_id else None  # Workflow depends on SOP if created from SOP
                )
                
                artifact_id = artifact_result.get("artifact_id")
                self.logger.info(f"✅ Workflow registered in Artifact Plane: {artifact_id}")
            except Exception as e:
                self.logger.warning(f"Failed to register workflow in Artifact Plane: {e}")
                # Continue with structured artifact for backward compatibility
        
        # Create structured artifact (for backward compatibility and execution state reference)
        structured_artifact = create_structured_artifact(
            result_type="workflow",
            semantic_payload=semantic_payload,
            renderings=renderings,
            metadata={"artifact_id": artifact_id} if artifact_id else None  # Include artifact_id reference
        )
        
        return {
            "artifacts": {
                "workflow": structured_artifact
            },
            "events": [
                {
                    "type": "workflow_created",
                    "sop_id": sop_id,
                    "workflow_id": workflow_id,
                    "artifact_id": artifact_id  # Include artifact_id in event
                }
            ]
        }
    
    async def _handle_analyze_coexistence(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle analyze_coexistence intent using agentic forward pattern.
        
        ARCHITECTURAL PRINCIPLE: Orchestrator delegates to Agent, Agent reasons and uses services as tools.
        """
        workflow_id = intent.parameters.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required for analyze_coexistence intent")
        
        # Assemble runtime context (call site responsibility)
        runtime_context = await self.runtime_context_service.create_runtime_context(
            request={"type": "analyze_coexistence", "workflow_id": workflow_id},
            context=context
        )
        
        # Use CoexistenceAnalysisAgent (agentic forward pattern)
        # Agent reasons about workflow, uses CoexistenceAnalysisService as tool via MCP
        # Pass runtime context (read-only) to agent
        agent_result = await self.coexistence_analysis_agent.process_request(
            {
                "type": "analyze_coexistence",
                "workflow_id": workflow_id
            },
            context,
            runtime_context=runtime_context
        )
        
        # Extract outcome from agent result
        analysis_result = agent_result.get("artifact", {})
        analysis_id = analysis_result.get("analysis_id") or f"analysis_{workflow_id}_{generate_event_id()}"
        
        # Extract semantic payload
        semantic_payload = {
            "workflow_id": workflow_id,
            "analysis_id": analysis_id,
            "status": analysis_result.get("analysis_status", "completed"),
            "friction_points_identified": analysis_result.get("friction_points_identified", 0),
            "human_focus_areas": analysis_result.get("human_focus_areas", [])
        }
        
        renderings = {
            "coexistence_analysis": analysis_result,
            "reasoning": agent_result.get("reasoning", "")
        }
        
        # Create artifact in Artifact Plane (Purpose-Bound Outcome)
        artifact_id = None
        if self.artifact_plane:
            try:
                # Full artifact payload (semantic + renderings)
                artifact_payload = {
                    "result_type": "coexistence_analysis",
                    "semantic_payload": semantic_payload,
                    "renderings": renderings
                }
                
                artifact_result = await self.artifact_plane.create_artifact(
                    artifact_type="coexistence_analysis",
                    artifact_id=analysis_id,  # Use analysis_id as artifact_id
                    payload=artifact_payload,
                    context=context,
                    lifecycle_state="draft",  # Initial state
                    owner="client",
                    purpose="decision_support",  # Analysis is for decision support
                    source_artifact_ids=[workflow_id] if workflow_id else None  # Analysis depends on workflow
                )
                
                artifact_id = artifact_result.get("artifact_id")
                self.logger.info(f"✅ Coexistence analysis registered in Artifact Plane: {artifact_id}")
            except Exception as e:
                self.logger.warning(f"Failed to register coexistence analysis in Artifact Plane: {e}")
                # Continue with structured artifact for backward compatibility
        
        # Create structured artifact (for backward compatibility and execution state reference)
        structured_artifact = create_structured_artifact(
            result_type="coexistence_analysis",
            semantic_payload=semantic_payload,
            renderings=renderings,
            metadata={"artifact_id": artifact_id} if artifact_id else None  # Include artifact_id reference
        )
        
        return {
            "artifacts": {
                "coexistence_analysis": structured_artifact
            },
            "events": [
                {
                    "type": "coexistence_analyzed",
                    "workflow_id": workflow_id,
                    "analysis_id": analysis_id,
                    "artifact_id": artifact_id  # Include artifact_id in event
                }
            ]
        }
    
    # Note: create_blueprint moved to Outcomes Realm (blueprints are Purpose-Bound Outcomes)
    # Use create_blueprint intent in Outcomes Realm instead
    
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
    
    async def _handle_generate_sop_from_structure_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle generate_sop_from_structure SOA API (dual call pattern)."""
        sop_structure = kwargs.get("sop_structure")
        requirements = kwargs.get("requirements", {})
        user_context = kwargs.get("user_context", {})
        tenant_id = user_context.get("tenant_id", context.tenant_id if context else "default")
        
        if not sop_structure:
            return {"success": False, "error": "sop_structure is required"}
        
        try:
            exec_context = context or ExecutionContext(
                execution_id="generate_sop_from_structure",
                tenant_id=tenant_id,
                session_id=user_context.get("session_id", "default")
            )
            
            # Use WorkflowConversionService to generate SOP
            sop_result = await self.workflow_conversion_service.generate_sop_from_structure(
                sop_structure=sop_structure,
                tenant_id=tenant_id,
                context=exec_context
            )
            
            return {
                "success": True,
                "sop": sop_result.get("sop", {}),
                "sop_id": sop_result.get("sop_id")
            }
        except Exception as e:
            self.logger.error(f"Failed to generate SOP from structure: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _define_soa_api_handlers(self) -> Dict[str, Any]:
        """
        Define Journey Orchestrator SOA APIs.
        
        UNIFIED PATTERN: MCP Server automatically registers these as MCP Tools.
        
        Returns:
            Dict of SOA API definitions with handlers, input schemas, and descriptions
        """
        return {
            "optimize_process": {
                "handler": self._handle_optimize_process_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow identifier to optimize"
                        },
                        "optimization_goals": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional optimization goals"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": ["workflow_id"]
                },
                "description": "Optimize a business process/workflow"
            },
            "generate_sop": {
                "handler": self._handle_generate_sop_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow identifier (optional if chat_mode=True)"
                        },
                        "process_description": {
                            "type": "string",
                            "description": "Process description (for chat mode)"
                        },
                        "chat_mode": {
                            "type": "boolean",
                            "description": "Use chat-based SOP generation",
                            "default": False
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": []
                },
                "description": "Generate Standard Operating Procedure"
            },
            "create_workflow": {
                "handler": self._handle_create_workflow_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sop_id": {
                            "type": "string",
                            "description": "SOP identifier (if creating from SOP)"
                        },
                        "workflow_definition": {
                            "type": "object",
                            "description": "Workflow definition (if creating from definition)"
                        },
                        "workflow_file_path": {
                            "type": "string",
                            "description": "Path to workflow file (BPMN, etc.)"
                        },
                        "workflow_name": {
                            "type": "string",
                            "description": "Workflow name"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": []
                },
                "description": "Create a workflow from SOP, definition, or file"
            },
            "generate_sop_from_structure": {
                "handler": self._handle_generate_sop_from_structure_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sop_structure": {
                            "type": "object",
                            "description": "SOP structure (title, description, steps, checkpoints, etc.)",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "steps": {"type": "array"},
                                "checkpoints": {"type": "array"},
                                "prerequisites": {"type": "array"},
                                "expected_outcomes": {"type": "array"}
                            },
                            "required": ["title", "steps"]
                        },
                        "requirements": {
                            "type": "object",
                            "description": "Original requirements (optional)"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context (includes tenant_id, session_id)"
                        }
                    },
                    "required": ["sop_structure"]
                },
                "description": "Generate SOP from structured requirements (from agent)"
            },
            "get_workflow": {
                "handler": self._handle_get_workflow_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow identifier"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context (includes tenant_id, session_id)"
                        }
                    },
                    "required": ["workflow_id"]
                },
                "description": "Get workflow data by workflow_id"
            },
            "analyze_coexistence": {
                "handler": self._handle_analyze_coexistence_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow identifier to analyze"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context (includes tenant_id, session_id)"
                        }
                    },
                    "required": ["workflow_id"]
                },
                "description": "Analyze workflow for coexistence (human-positive friction removal)"
            },
            "get_sop": {
                "handler": self._handle_get_sop_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sop_id": {
                            "type": "string",
                            "description": "SOP identifier"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context (includes tenant_id, session_id)"
                        }
                    },
                    "required": ["sop_id"]
                },
                "description": "Get SOP data by sop_id"
            }
        }
    
    async def _handle_optimize_process_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle optimize_process SOA API (dual call pattern)."""
        if intent and context:
            return await self._handle_optimize_process(intent, context)
        else:
            workflow_id = kwargs.get("workflow_id")
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent_obj = IntentFactory.create_intent(
                intent_type="optimize_process",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "workflow_id": workflow_id,
                    "optimization_goals": kwargs.get("optimization_goals", [])
                }
            )
            
            exec_context = ExecutionContext(
                execution_id="optimize_process",
                intent=intent_obj,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
            
            return await self._handle_optimize_process(intent_obj, exec_context)
    
    async def _handle_generate_sop_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle generate_sop SOA API (dual call pattern)."""
        if intent and context:
            return await self._handle_generate_sop(intent, context)
        else:
            workflow_id = kwargs.get("workflow_id")
            process_description = kwargs.get("process_description")
            chat_mode = kwargs.get("chat_mode", False)
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent_obj = IntentFactory.create_intent(
                intent_type="generate_sop",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "workflow_id": workflow_id,
                    "process_description": process_description,
                    "chat_mode": chat_mode
                }
            )
            
            exec_context = ExecutionContext(
                execution_id="generate_sop",
                intent=intent_obj,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
            
            return await self._handle_generate_sop(intent_obj, exec_context)
    
    async def _handle_create_workflow_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle create_workflow SOA API (dual call pattern)."""
        if intent and context:
            return await self._handle_create_workflow(intent, context)
        else:
            sop_id = kwargs.get("sop_id")
            workflow_definition = kwargs.get("workflow_definition")
            workflow_file_path = kwargs.get("workflow_file_path")
            workflow_name = kwargs.get("workflow_name")
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent_obj = IntentFactory.create_intent(
                intent_type="create_workflow",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "sop_id": sop_id,
                    "workflow_definition": workflow_definition,
                    "workflow_file_path": workflow_file_path,
                    "workflow_name": workflow_name
                }
            )
            
            exec_context = ExecutionContext(
                execution_id="create_workflow",
                intent=intent_obj,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
            
            return await self._handle_create_workflow(intent_obj, exec_context)
    
    async def _handle_get_workflow_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle get_workflow SOA API (dual call pattern)."""
        workflow_id = kwargs.get("workflow_id")
        user_context = kwargs.get("user_context", {})
        tenant_id = user_context.get("tenant_id", "default")
        session_id = user_context.get("session_id", "default")
        solution_id = user_context.get("solution_id", "default")
        
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        # Get workflow from execution state or artifact plane
        exec_context = ExecutionContext(
            execution_id="get_workflow",
            tenant_id=tenant_id,
            session_id=session_id,
            solution_id=solution_id
        )
        
        # Try to get workflow from execution state
        if exec_context.state_surface:
            execution_state = await exec_context.state_surface.get_execution_state(
                f"workflow_{workflow_id}",
                tenant_id
            )
            
            if execution_state and execution_state.get("artifacts", {}).get("workflow"):
                return {
                    "success": True,
                    "workflow": execution_state["artifacts"]["workflow"]
                }
        
        # Try to get workflow from artifact plane
        if self.artifact_plane:
            try:
                artifact = await self.artifact_plane.get_artifact(
                    artifact_id=workflow_id,
                    context=exec_context
                )
                if artifact and artifact.get("payload", {}).get("renderings", {}).get("workflow"):
                    return {
                        "success": True,
                        "workflow": artifact["payload"]["renderings"]["workflow"]
                    }
            except Exception as e:
                self.logger.warning(f"Failed to get workflow from artifact plane: {e}")
        
        # Fallback: Return basic structure
        self.logger.warning(f"Workflow {workflow_id} not found, returning basic structure")
        return {
            "success": True,
            "workflow": {
                "workflow_id": workflow_id,
                "description": "Workflow process",
                "steps": [],
                "status": "not_found"
            }
        }
    
    async def _handle_analyze_coexistence_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle analyze_coexistence SOA API (dual call pattern)."""
        if intent and context:
            return await self._handle_analyze_coexistence(intent, context)
        else:
            workflow_id = kwargs.get("workflow_id")
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent_obj = IntentFactory.create_intent(
                intent_type="analyze_coexistence",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "workflow_id": workflow_id
                }
            )
            
            exec_context = ExecutionContext(
                execution_id="analyze_coexistence",
                intent=intent_obj,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
            
            return await self._handle_analyze_coexistence(intent_obj, exec_context)
    
    async def _handle_get_sop_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle get_sop SOA API (dual call pattern)."""
        sop_id = kwargs.get("sop_id")
        user_context = kwargs.get("user_context", {})
        tenant_id = user_context.get("tenant_id", "default")
        session_id = user_context.get("session_id", "default")
        solution_id = user_context.get("solution_id", "default")
        
        if not sop_id:
            raise ValueError("sop_id is required")
        
        # Get SOP from execution state or artifact plane
        exec_context = ExecutionContext(
            execution_id="get_sop",
            tenant_id=tenant_id,
            session_id=session_id,
            solution_id=solution_id
        )
        
        # Try to get SOP from execution state
        if exec_context.state_surface:
            execution_state = await exec_context.state_surface.get_execution_state(
                f"sop_{sop_id}",
                tenant_id
            )
            
            if execution_state and execution_state.get("artifacts", {}).get("sop"):
                return {
                    "success": True,
                    "sop": execution_state["artifacts"]["sop"]
                }
        
        # Try to get SOP from artifact plane
        if self.artifact_plane:
            try:
                artifact = await self.artifact_plane.get_artifact(
                    artifact_id=sop_id,
                    context=exec_context
                )
                if artifact and artifact.get("payload", {}).get("renderings", {}).get("sop"):
                    return {
                        "success": True,
                        "sop": artifact["payload"]["renderings"]["sop"]
                    }
            except Exception as e:
                self.logger.warning(f"Failed to get SOP from artifact plane: {e}")
        
        # Fallback: Return basic structure
        self.logger.warning(f"SOP {sop_id} not found, returning basic structure")
        return {
            "success": True,
            "sop": {
                "sop_id": sop_id,
                "title": "SOP",
                "status": "not_found"
            }
        }