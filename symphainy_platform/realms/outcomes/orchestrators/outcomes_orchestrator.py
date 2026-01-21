"""
Outcomes Orchestrator - Coordinates Outcomes/Synthesis Operations

Coordinates enabling services for roadmap generation, POC creation, and solution synthesis.

WHAT (Orchestrator Role): I coordinate outcomes/synthesis operations
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

from utilities import get_logger
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.artifact_plane import ArtifactPlane
from ..enabling_services.roadmap_generation_service import RoadmapGenerationService
from ..enabling_services.poc_generation_service import POCGenerationService
from ..enabling_services.solution_synthesis_service import SolutionSynthesisService
from ..enabling_services.report_generator_service import ReportGeneratorService
from ..enabling_services.visual_generation_service import VisualGenerationService


class OutcomesOrchestrator:
    """
    Outcomes Orchestrator - Coordinates outcomes/synthesis operations.
    
    Coordinates:
    - Outcome synthesis from other realms
    - Roadmap generation
    - POC proposal creation
    - Solution creation
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Outcomes Orchestrator.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Initialize Artifact Plane (for artifact management)
        self.artifact_plane = None
        if public_works:
            self.logger.info(f"Public Works available: {hasattr(public_works, 'artifact_storage_abstraction')}, {hasattr(public_works, 'state_abstraction')}")
            if hasattr(public_works, 'artifact_storage_abstraction') and hasattr(public_works, 'state_abstraction'):
                artifact_storage = getattr(public_works, 'artifact_storage_abstraction', None)
                state_management = getattr(public_works, 'state_abstraction', None)
                self.logger.info(f"Artifact storage: {artifact_storage is not None}, State management: {state_management is not None}")
                if artifact_storage and state_management:
                    try:
                        self.artifact_plane = ArtifactPlane(
                            artifact_storage=artifact_storage,
                            state_management=state_management
                        )
                        self.logger.info("✅ Artifact Plane initialized successfully")
                    except Exception as e:
                        self.logger.error(f"Failed to initialize Artifact Plane: {e}", exc_info=True)
                else:
                    self.logger.warning(f"Artifact Plane dependencies not available: storage={artifact_storage is not None}, state={state_management is not None}")
            else:
                self.logger.warning("Public Works missing Artifact Plane dependencies")
        else:
            self.logger.warning("Public Works not available for Artifact Plane")
        
        # Initialize enabling services with Public Works
        self.roadmap_generation_service = RoadmapGenerationService(public_works=public_works)
        self.poc_generation_service = POCGenerationService(public_works=public_works)
        self.solution_synthesis_service = SolutionSynthesisService(public_works=public_works)
        self.report_generator_service = ReportGeneratorService(public_works=public_works)
        self.visual_generation_service = VisualGenerationService(public_works=public_works)
    
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
        
        if intent_type == "synthesize_outcome":
            return await self._handle_synthesize_outcome(intent, context)
        elif intent_type == "generate_roadmap":
            return await self._handle_generate_roadmap(intent, context)
        elif intent_type == "create_poc":
            return await self._handle_create_poc(intent, context)
        elif intent_type == "create_solution":
            return await self._handle_create_solution(intent, context)
        else:
            raise ValueError(f"Unknown intent type: {intent_type}")
    
    async def _handle_synthesize_outcome(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle synthesize_outcome intent - synthesize outputs from other realms.
        
        Reads pillar summaries from State Surface and generates summary visualization.
        """
        # Read session state to get pillar summaries
        session_state = await context.state_surface.get_session_state(
            context.session_id,
            context.tenant_id
        )
        
        if not session_state:
            session_state = {}
        
        # Extract pillar summaries from session state
        content_summary = session_state.get("content_pillar_summary", {})
        insights_summary = session_state.get("insights_pillar_summary", {})
        journey_summary = session_state.get("journey_pillar_summary", {})
        
        # Generate summary report
        summary_result = await self.report_generator_service.generate_pillar_summary(
            content_summary=content_summary,
            insights_summary=insights_summary,
            journey_summary=journey_summary,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Generate summary visualization
        pillar_outputs = {
            "content_pillar": content_summary,
            "insights_pillar": insights_summary,
            "journey_pillar": journey_summary
        }
        
        visual_result = None
        try:
            visual_result = await self.visual_generation_service.generate_summary_visual(
                pillar_outputs=pillar_outputs,
                tenant_id=context.tenant_id,
                context=context
            )
        except Exception as e:
            self.logger.warning(f"Failed to generate summary visualization: {e}")
        
        # Extract semantic payload
        semantic_payload = {
            "solution_id": summary_result.get("solution_id"),
            "session_id": context.session_id,
            "status": summary_result.get("status")
        }
        
        # Collect renderings
        renderings = {
            "synthesis": summary_result,
            "content_summary": content_summary,
            "insights_summary": insights_summary,
            "journey_summary": journey_summary
        }
        
        if visual_result and visual_result.get("success"):
            renderings["summary_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        # Create structured artifact
        structured_artifact = create_structured_artifact(
            result_type="solution",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        return {
            "artifacts": {
                "solution": structured_artifact
            },
            "events": [
                {
                    "type": "outcome_synthesized",
                    "session_id": context.session_id
                }
            ]
        }
    
    async def _handle_generate_roadmap(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle generate_roadmap intent - generate strategic roadmap from pillar outputs.
        """
        # Read session state to get pillar summaries
        session_state = await context.state_surface.get_session_state(
            context.session_id,
            context.tenant_id
        )
        
        if not session_state:
            session_state = {}
        
        # Extract pillar summaries
        content_summary = session_state.get("content_pillar_summary", {})
        insights_summary = session_state.get("insights_pillar_summary", {})
        journey_summary = session_state.get("journey_pillar_summary", {})
        
        # Additional context from intent parameters
        additional_context = intent.parameters.get("additional_context", {})
        roadmap_options = intent.parameters.get("roadmap_options", {})
        
        # Generate roadmap
        roadmap_result = await self.roadmap_generation_service.generate_roadmap(
            content_summary=content_summary,
            insights_summary=insights_summary,
            journey_summary=journey_summary,
            additional_context=additional_context,
            roadmap_options=roadmap_options,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Generate roadmap visualization
        visual_result = None
        try:
            visual_result = await self.visual_generation_service.generate_roadmap_visual(
                roadmap_data=roadmap_result,
                tenant_id=context.tenant_id,
                context=context
            )
        except Exception as e:
            self.logger.warning(f"Failed to generate roadmap visualization: {e}")
        
        # Extract roadmap_id
        roadmap_id = roadmap_result.get("roadmap_id")
        
        # Collect full artifact payload for Artifact Plane
        artifact_payload = {
            "roadmap": roadmap_result,
            "strategic_plan": roadmap_result.get("strategic_plan")
        }
        
        if visual_result and visual_result.get("success"):
            artifact_payload["roadmap_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        # Store artifact in Artifact Plane (not execution state)
        if self.artifact_plane:
            try:
                artifact_result = await self.artifact_plane.create_artifact(
                    artifact_type="roadmap",
                    artifact_id=roadmap_id,
                    payload=artifact_payload,
                    context=context,
                    metadata={
                        "regenerable": True,
                        "retention_policy": "session"
                    }
                )
                
                stored_artifact_id = artifact_result.get("artifact_id", roadmap_id)
                
                # Return artifact_id reference (not full artifact)
                # Full artifact is in Artifact Plane, retrievable by artifact_id
                return {
                    "artifacts": {
                        "roadmap_id": stored_artifact_id,
                        "roadmap": {
                            "result_type": "roadmap",
                            "semantic_payload": {
                                "roadmap_id": stored_artifact_id,
                                "execution_id": context.execution_id,
                                "session_id": context.session_id
                            },
                            "renderings": {}
                        }
                    },
                    "events": [
                        {
                            "type": "roadmap_generated",
                            "roadmap_id": stored_artifact_id,
                            "session_id": context.session_id
                        }
                    ]
                }
            except Exception as e:
                self.logger.error(f"Failed to store roadmap in Artifact Plane: {e}", exc_info=True)
                # Fall through to old behavior
        
        # Fallback: Store in execution state (old behavior - should not happen in production)
        self.logger.warning("Artifact Plane not available, falling back to execution state storage")
        semantic_payload = {
            "roadmap_id": roadmap_id,
            "session_id": context.session_id,
            "status": roadmap_result.get("status")
        }
        renderings = {
            "roadmap": roadmap_result,
            "strategic_plan": roadmap_result.get("strategic_plan")
        }
        if visual_result and visual_result.get("success"):
            renderings["roadmap_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        structured_artifact = create_structured_artifact(
            result_type="roadmap",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        return {
            "artifacts": {
                "roadmap": structured_artifact,
                "roadmap_id": roadmap_id
            },
            "events": [
                {
                    "type": "roadmap_generated",
                    "roadmap_id": roadmap_id,
                    "session_id": context.session_id
                }
            ]
        }
    
    async def _handle_create_poc(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle create_poc intent - create POC proposal from pillar outputs.
        """
        # Read session state to get pillar summaries
        session_state = await context.state_surface.get_session_state(
            context.session_id,
            context.tenant_id
        )
        
        if not session_state:
            session_state = {}
        
        # Extract pillar summaries
        content_summary = session_state.get("content_pillar_summary", {})
        insights_summary = session_state.get("insights_pillar_summary", {})
        journey_summary = session_state.get("journey_pillar_summary", {})
        
        # Additional context from intent parameters
        additional_context = intent.parameters.get("additional_context", {})
        poc_options = intent.parameters.get("poc_options", {})
        
        # Generate POC proposal
        poc_result = await self.poc_generation_service.generate_poc_proposal(
            content_summary=content_summary,
            insights_summary=insights_summary,
            journey_summary=journey_summary,
            additional_context=additional_context,
            poc_options=poc_options,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Generate POC visualization
        visual_result = None
        try:
            visual_result = await self.visual_generation_service.generate_poc_visual(
                poc_data=poc_result,
                tenant_id=context.tenant_id,
                context=context
            )
        except Exception as e:
            self.logger.warning(f"Failed to generate POC visualization: {e}")
        
        # Extract proposal_id from POC result
        proposal_id = poc_result.get("proposal_id")
        
        # Collect full artifact payload for Artifact Plane
        artifact_payload = {
            "poc_proposal": poc_result,
            "proposal": poc_result.get("proposal")
        }
        
        if visual_result and visual_result.get("success"):
            artifact_payload["poc_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        # Store artifact in Artifact Plane (not execution state)
        if self.artifact_plane:
            try:
                artifact_result = await self.artifact_plane.create_artifact(
                    artifact_type="poc",
                    artifact_id=proposal_id,
                    payload=artifact_payload,
                    context=context,
                    metadata={
                        "regenerable": True,
                        "retention_policy": "session"
                    }
                )
                
                stored_artifact_id = artifact_result.get("artifact_id", proposal_id)
                
                # Return artifact_id reference (not full artifact)
                return {
                    "artifacts": {
                        "proposal_id": stored_artifact_id,
                        "poc_id": stored_artifact_id,
                        "poc": {
                            "result_type": "poc",
                            "semantic_payload": {
                                "proposal_id": stored_artifact_id,
                                "poc_id": stored_artifact_id,
                                "execution_id": context.execution_id,
                                "session_id": context.session_id
                            },
                            "renderings": {}
                        }
                    },
                    "events": [
                        {
                            "type": "poc_proposal_created",
                            "proposal_id": stored_artifact_id,
                            "session_id": context.session_id
                        }
                    ]
                }
            except Exception as e:
                self.logger.error(f"Failed to store POC in Artifact Plane: {e}", exc_info=True)
                # Fall through to old behavior
        
        # Fallback: Store in execution state (old behavior)
        self.logger.warning("Artifact Plane not available, falling back to execution state storage")
        semantic_payload = {
            "poc_id": proposal_id,
            "proposal_id": proposal_id,
            "session_id": context.session_id,
            "status": poc_result.get("status")
        }
        renderings = {
            "poc_proposal": poc_result,
            "proposal": poc_result.get("proposal")
        }
        if visual_result and visual_result.get("success"):
            renderings["poc_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        structured_artifact = create_structured_artifact(
            result_type="poc",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        return {
            "artifacts": {
                "poc": structured_artifact,
                "proposal_id": proposal_id,
                "poc_id": proposal_id
            },
            "events": [
                {
                    "type": "poc_proposal_created",
                    "proposal_id": proposal_id,
                    "session_id": context.session_id
                }
            ]
        }
    
    async def _handle_create_solution(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle create_solution intent - create platform solution from roadmap/POC/blueprint.
        
        Uses Solution SDK to create and register solutions.
        """
        # Get solution source (roadmap, poc, or blueprint)
        solution_source = intent.parameters.get("solution_source")  # "roadmap", "poc", or "blueprint"
        source_id = intent.parameters.get("source_id")  # roadmap_id, proposal_id, or blueprint_id
        
        if not solution_source or not source_id:
            raise ValueError("solution_source and source_id are required for create_solution intent")
        
        if solution_source not in ["roadmap", "poc", "blueprint"]:
            raise ValueError(f"Invalid solution_source: {solution_source}. Must be 'roadmap', 'poc', or 'blueprint'")
        
        # Retrieve artifact from Artifact Plane (not execution state)
        source_data = None
        
        self.logger.info(f"Retrieving {solution_source} artifact: {source_id} (Artifact Plane available: {self.artifact_plane is not None})")
        
        if self.artifact_plane:
            try:
                self.logger.info(f"Attempting Artifact Plane retrieval for {solution_source}: {source_id}")
                artifact_result = await self.artifact_plane.get_artifact(
                    artifact_id=source_id,
                    tenant_id=context.tenant_id,
                    include_payload=True,
                    include_visuals=False
                )
                
                if artifact_result and artifact_result.get("payload"):
                    # Extract the actual artifact data from payload
                    payload = artifact_result["payload"]
                    
                    # Get artifact data based on type
                    if solution_source == "roadmap":
                        source_data = payload.get("roadmap") or payload.get("strategic_plan")
                    elif solution_source == "poc":
                        source_data = payload.get("poc_proposal") or payload.get("proposal")
                    elif solution_source == "blueprint":
                        source_data = payload.get("blueprint")
                    else:
                        # Fallback: use payload directly
                        source_data = payload
                    
                    if source_data:
                        self.logger.info(f"✅ Retrieved {solution_source} from Artifact Plane: {source_id}")
                    else:
                        self.logger.warning(f"Artifact payload found but no {solution_source} data in payload")
                else:
                    self.logger.warning(f"Artifact {source_id} not found in Artifact Plane (result: {artifact_result is not None})")
            except Exception as e:
                self.logger.error(f"Failed to retrieve artifact from Artifact Plane: {e}", exc_info=True)
                # Fall through to fallback strategies
        else:
            self.logger.warning("Artifact Plane not available, using execution state fallback")
        
        # Fallback: Try execution state (for backward compatibility during migration)
        if not source_data:
            self.logger.info(f"Trying execution state fallback for {solution_source}: {source_id}")
            # Try using source_id as execution_id (if roadmap was stored in execution state)
            execution_state = await context.state_surface.get_execution_state(
                source_id,
                context.tenant_id
            )
            if execution_state:
                self.logger.info(f"Found execution state for {source_id}")
                artifacts = execution_state.get("artifacts", {})
                artifact = artifacts.get(solution_source)
                if artifact:
                    if isinstance(artifact, dict) and "renderings" in artifact:
                        renderings = artifact.get("renderings", {})
                        source_data = renderings.get(solution_source) or renderings.get("roadmap") or renderings.get("poc_proposal")
                    else:
                        source_data = artifact
                    if source_data:
                        self.logger.info(f"✅ Retrieved {solution_source} from execution state: {source_id}")
            else:
                self.logger.warning(f"Execution state not found for {source_id}")
        
        if not source_data:
            raise ValueError(
                f"Source {solution_source} with id {source_id} not found in Artifact Plane or execution state. "
                f"Please ensure the {solution_source} was created successfully."
            )
        
        # Create solution via SolutionSynthesisService
        solution_result = await self.solution_synthesis_service.create_solution_from_artifact(
            solution_source=solution_source,
            source_id=source_id,
            source_data=source_data,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "solution": solution_result,
                "solution_id": solution_result.get("solution_id")
            },
            "events": [
                {
                    "type": "solution_created",
                    "solution_id": solution_result.get("solution_id"),
                    "source": solution_source,
                    "source_id": source_id,
                    "session_id": context.session_id
                }
            ]
        }
    
    def _define_soa_api_handlers(self) -> Dict[str, Any]:
        """
        Define Outcomes Orchestrator SOA APIs.
        
        UNIFIED PATTERN: MCP Server automatically registers these as MCP Tools.
        
        Returns:
            Dict of SOA API definitions with handlers, input schemas, and descriptions
        """
        return {
            "synthesize_outcome": {
                "handler": self._handle_synthesize_outcome_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input_data": {
                            "type": "object",
                            "description": "Input data for synthesis (pillar summaries from session state)"
                        },
                        "outcome_type": {
                            "type": "string",
                            "description": "Type of outcome to synthesize",
                            "enum": ["summary", "report", "visualization"]
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": []
                },
                "description": "Synthesize an outcome from input data (pillar summaries)"
            },
            "generate_roadmap": {
                "handler": self._handle_generate_roadmap_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_context": {
                            "type": "object",
                            "description": "Project context (pillar summaries, additional context)"
                        },
                        "roadmap_type": {
                            "type": "string",
                            "description": "Type of roadmap",
                            "enum": ["strategic", "tactical", "execution"]
                        },
                        "roadmap_options": {
                            "type": "object",
                            "description": "Optional roadmap generation options"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": []
                },
                "description": "Generate a strategic roadmap from pillar outputs"
            },
            "create_poc": {
                "handler": self._handle_create_poc_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "poc_requirements": {
                            "type": "object",
                            "description": "POC requirements (pillar summaries, additional context)"
                        },
                        "poc_name": {
                            "type": "string",
                            "description": "POC name"
                        },
                        "poc_options": {
                            "type": "object",
                            "description": "Optional POC generation options"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": []
                },
                "description": "Create a Proof of Concept proposal"
            }
        }
    
    async def _handle_synthesize_outcome_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle synthesize_outcome SOA API (dual call pattern)."""
        if intent and context:
            return await self._handle_synthesize_outcome(intent, context)
        else:
            input_data = kwargs.get("input_data", {})
            outcome_type = kwargs.get("outcome_type", "summary")
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent_obj = IntentFactory.create_intent(
                intent_type="synthesize_outcome",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "input_data": input_data,
                    "outcome_type": outcome_type
                }
            )
            
            exec_context = ExecutionContext(
                execution_id="synthesize_outcome",
                intent=intent_obj,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
            
            return await self._handle_synthesize_outcome(intent_obj, exec_context)
    
    async def _handle_generate_roadmap_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle generate_roadmap SOA API (dual call pattern)."""
        if intent and context:
            return await self._handle_generate_roadmap(intent, context)
        else:
            project_context = kwargs.get("project_context", {})
            roadmap_type = kwargs.get("roadmap_type", "strategic")
            roadmap_options = kwargs.get("roadmap_options", {})
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent_obj = IntentFactory.create_intent(
                intent_type="generate_roadmap",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "additional_context": project_context,
                    "roadmap_options": roadmap_options,
                    "roadmap_type": roadmap_type
                }
            )
            
            exec_context = ExecutionContext(
                execution_id="generate_roadmap",
                intent=intent_obj,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
            
            return await self._handle_generate_roadmap(intent_obj, exec_context)
    
    async def _handle_create_poc_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle create_poc SOA API (dual call pattern)."""
        if intent and context:
            return await self._handle_create_poc(intent, context)
        else:
            poc_requirements = kwargs.get("poc_requirements", {})
            poc_name = kwargs.get("poc_name", "POC Proposal")
            poc_options = kwargs.get("poc_options", {})
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent_obj = IntentFactory.create_intent(
                intent_type="create_poc",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "additional_context": poc_requirements,
                    "poc_options": poc_options,
                    "poc_name": poc_name
                }
            )
            
            exec_context = ExecutionContext(
                execution_id="create_poc",
                intent=intent_obj,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
            
            return await self._handle_create_poc(intent_obj, exec_context)
