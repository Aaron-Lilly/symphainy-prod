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
import uuid

from utilities import get_logger
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.artifact_plane import ArtifactPlane
# Note: RoadmapGenerationService, POCGenerationService, SolutionSynthesisService were stubs
# and have been deleted. Their functionality is now in intent services (generate_roadmap_service,
# create_poc_service, create_solution_service). The orchestrator uses agents + intent services.
from symphainy_platform.foundations.libraries.reporting.report_generator_service import ReportGeneratorService
from symphainy_platform.foundations.libraries.visualization.outcome_visual_service import VisualGenerationService
from symphainy_platform.foundations.libraries.export.export_service import ExportService
from symphainy_platform.foundations.libraries.coexistence.coexistence_analysis_service import CoexistenceAnalysisService
from ..agents.outcomes_synthesis_agent import OutcomesSynthesisAgent
from ..agents.poc_generation_agent import POCGenerationAgent
from ..agents.outcomes_liaison_agent import OutcomesLiaisonAgent

# Optional agent imports - make them optional to allow testing without full implementation
try:
    from ..agents.blueprint_creation_agent import BlueprintCreationAgent
except ImportError:
    BlueprintCreationAgent = None  # Will be checked before use

try:
    from ..agents.roadmap_generation_agent import RoadmapGenerationAgent
except ImportError:
    RoadmapGenerationAgent = None  # Will be checked before use


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
        # Note: Legacy roadmap/POC/solution services were stubs and deleted
        # Use intent services (generate_roadmap, create_poc, create_solution) instead
        self.roadmap_generation_service = None  # Deprecated - use intent services
        self.poc_generation_service = None  # Deprecated - use intent services
        self.solution_synthesis_service = None  # Deprecated - use intent services
        self.report_generator_service = ReportGeneratorService(public_works=public_works)
        self.visual_generation_service = VisualGenerationService(public_works=public_works)
        self.export_service = ExportService(public_works=public_works)
        
        # Initialize agents (agentic forward pattern)
        self.outcomes_synthesis_agent = OutcomesSynthesisAgent(public_works=public_works)
        self.blueprint_creation_agent = BlueprintCreationAgent(public_works=public_works) if BlueprintCreationAgent else None
        self.roadmap_generation_agent = RoadmapGenerationAgent(public_works=public_works) if RoadmapGenerationAgent else None
        self.poc_generation_agent = POCGenerationAgent(public_works=public_works)
        self.outcomes_liaison_agent = OutcomesLiaisonAgent(
            agent_definition_id="outcomes_liaison_agent",
            public_works=public_works
        )
        
        # CoexistenceAnalysisService (used as tool by BlueprintCreationAgent)
        self.coexistence_analysis_service = CoexistenceAnalysisService(
            public_works=public_works,
            visual_generation_service=self.visual_generation_service
        )
        
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
            await self.health_monitor.start_monitoring("outcomes_orchestrator")
        
        from datetime import datetime
        start_time = datetime.utcnow()
        intent_type = intent.intent_type
        success = True
        error_message = None
        result = None
        
        try:
            if intent_type == "synthesize_outcome":
                result = await self._handle_synthesize_outcome(intent, context)
            elif intent_type == "generate_roadmap":
                result = await self._handle_generate_roadmap(intent, context)
            elif intent_type == "create_poc":
                result = await self._handle_create_poc(intent, context)
            elif intent_type == "create_blueprint":
                result = await self._handle_create_blueprint(intent, context)
            elif intent_type == "create_solution":
                result = await self._handle_create_solution(intent, context)
            elif intent_type == "export_to_migration_engine":
                result = await self._handle_export_to_migration_engine(intent, context)
            elif intent_type == "export_artifact":
                result = await self._handle_export_artifact(intent, context)
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
                    orchestrator_id="outcomes_orchestrator",
                    orchestrator_name="Outcomes Orchestrator",
                    intent_type=intent_type,
                    latency_ms=latency_ms,
                    context=context,
                    success=success,
                    error_message=error_message
                )
                
                await self.health_monitor.record_intent_handled(
                    orchestrator_id="outcomes_orchestrator",
                    intent_type=intent_type,
                    success=success,
                    latency_ms=latency_ms
                )
            except Exception as e:
                self.logger.debug(f"Telemetry recording failed (non-critical): {e}")
    
    async def _handle_synthesize_outcome(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle synthesize_outcome intent using agentic forward pattern.
        
        ARCHITECTURAL PRINCIPLE: Orchestrator delegates to Agent, Agent reasons and uses services as tools.
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
        
        # Use OutcomesSynthesisAgent (agentic forward pattern)
        # Agent reasons about synthesis, uses ReportGeneratorService as tool via MCP
        synthesis_result = await self.outcomes_synthesis_agent.process_request(
            {
                "type": "synthesize_outcome",
                "content_summary": content_summary,
                "insights_summary": insights_summary,
                "journey_summary": journey_summary
            },
            context
        )
        
        # Generate realm-specific summary visuals using agent
        visuals_result = await self.outcomes_synthesis_agent.process_request(
            {
                "type": "generate_summary_visuals",
                "content_summary": content_summary,
                "insights_summary": insights_summary,
                "journey_summary": journey_summary
            },
            context
        )
        
        # Extract results
        synthesis = synthesis_result.get("artifact", {})
        realm_visuals = visuals_result.get("artifact", {})
        
        # Generate summary report (for backward compatibility)
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
        
        # Collect renderings (use agent results)
        renderings = {
            "synthesis": synthesis if synthesis else summary_result,
            "content_summary": content_summary,
            "insights_summary": insights_summary,
            "journey_summary": journey_summary,
            "realm_visuals": realm_visuals,  # Realm-specific visual data (tutorial format)
            "reasoning": synthesis_result.get("reasoning", "")
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
        Handle generate_roadmap intent using agentic forward pattern.
        
        ARCHITECTURAL PRINCIPLE: Orchestrator delegates to Agent, Agent reasons and uses services as tools.
        """
        goals = intent.parameters.get("goals", [])
        if not goals or len(goals) == 0:
            raise ValueError("Goals are required for roadmap generation")
        
        roadmap_options = intent.parameters.get("roadmap_options", {})
        
        # Use RoadmapGenerationAgent (agentic forward pattern)
        # Agent reasons about goals, designs phases, uses RoadmapGenerationService as tool via MCP
        if not self.roadmap_generation_agent:
            # Fallback: Use service directly if agent not available
            # Service requires content_summary, insights_summary, journey_summary, additional_context
            roadmap_result = await self.roadmap_generation_service.generate_roadmap(
                content_summary={"goals": goals},
                insights_summary={},
                journey_summary={},
                additional_context={"roadmap_options": roadmap_options},
                roadmap_options=roadmap_options,
                tenant_id=context.tenant_id,
                context=context
            )
            return {
                "artifacts": {
                    "roadmap": roadmap_result
                },
                "events": []
            }
        
        agent_result = await self.roadmap_generation_agent.process_request(
            {
                "type": "generate_roadmap",
                "goals": goals,
                "roadmap_options": roadmap_options
            },
            context
        )
        
        # Extract roadmap from agent result
        roadmap_result = agent_result.get("artifact", {})
        
        # Ensure roadmap_id exists
        roadmap_id = roadmap_result.get("roadmap_id") or f"roadmap_{str(uuid.uuid4())}"
        if not roadmap_result.get("roadmap_id"):
            roadmap_result["roadmap_id"] = roadmap_id
        
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
        Handle create_poc intent using agentic forward pattern.
        
        ARCHITECTURAL PRINCIPLE: Orchestrator delegates to Agent, Agent reasons and uses services as tools.
        """
        description = intent.parameters.get("description", "")
        if not description:
            raise ValueError("Description is required for POC creation")
        
        poc_options = intent.parameters.get("poc_options", {})
        
        # Use POCGenerationAgent (agentic forward pattern)
        # Agent reasons about POC requirements, designs scope, uses POCGenerationService as tool via MCP
        if not self.poc_generation_agent:
            # Fallback: Use service directly if agent not available
            poc_result = await self.poc_generation_service.generate_poc_proposal(
                content_summary={"description": description},
                insights_summary={},
                journey_summary={},
                additional_context={"poc_options": poc_options},
                poc_options=poc_options,
                tenant_id=context.tenant_id,
                context=context
            )
            return {
                "artifacts": {
                    "poc": poc_result
                },
                "events": []
            }
        
        try:
            agent_result = await self.poc_generation_agent.process_request(
                {
                    "type": "create_poc",
                    "description": description,
                    "poc_options": poc_options
                },
                context
            )
            
            # Extract POC proposal from agent result
            if not agent_result:
                raise ValueError("POC generation agent returned no result")
            
            poc_result = agent_result.get("artifact", {}) if agent_result else {}
        except (AttributeError, TypeError, ValueError) as e:
            # Fallback to service if agent fails
            # Fallbacks must obey the same semantic contract as primary agent execution.
            self.logger.warning(f"POC agent failed: {e}, falling back to service")
            poc_result = await self.poc_generation_service.generate_poc_proposal(
                content_summary={"description": description},
                insights_summary={},
                journey_summary={},
                additional_context={"poc_options": poc_options},
                poc_options=poc_options,
                tenant_id=context.tenant_id,
                context=context
            )
            # Ensure fallback produces structured artifact with same semantic contract
            poc_result = {
                "generation_mode": "agent_fallback",
                "confidence": "degraded",
                "semantic_payload": poc_result.get("semantic_payload", poc_result),
                "renderings": poc_result.get("renderings", {})
            }
        
        # Ensure poc_id/proposal_id exists
        proposal_id = poc_result.get("poc_id") or poc_result.get("proposal_id") or f"poc_{str(uuid.uuid4())}"
        if not poc_result.get("poc_id") and not poc_result.get("proposal_id"):
            poc_result["poc_id"] = proposal_id
            poc_result["proposal_id"] = proposal_id
        
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
    
    async def _handle_export_to_migration_engine_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle export_to_migration_engine SOA API (dual call pattern)."""
        if intent and context:
            return await self._handle_export_to_migration_engine(intent, context)
        else:
            solution_id = kwargs.get("solution_id")
            export_format = kwargs.get("export_format", "json")
            include_mappings = kwargs.get("include_mappings", True)
            include_rules = kwargs.get("include_rules", True)
            include_staged_data = kwargs.get("include_staged_data", False)
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent_obj = IntentFactory.create_intent(
                intent_type="export_to_migration_engine",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "solution_id": solution_id,
                    "export_format": export_format,
                    "include_mappings": include_mappings,
                    "include_rules": include_rules,
                    "include_staged_data": include_staged_data
                }
            )
            
            exec_context = ExecutionContext(
                execution_id="export_to_migration_engine",
                intent=intent_obj,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
            
            return await self._handle_export_to_migration_engine(intent_obj, exec_context)
    
    async def _handle_create_blueprint(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle create_blueprint intent using agentic forward pattern.
        
        ARCHITECTURAL PRINCIPLE: 
        - Blueprints are Purpose-Bound Outcomes, belong in Outcomes Realm
        - Orchestrator delegates to Agent, Agent reasons and uses services as tools
        """
        workflow_id = intent.parameters.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required for create_blueprint intent")
        
        current_state_workflow_id = intent.parameters.get("current_state_workflow_id")
        
        # Use BlueprintCreationAgent (agentic forward pattern)
        # Agent reasons about transformation, designs phases, uses CoexistenceAnalysisService as tool via MCP
        if not self.blueprint_creation_agent:
            raise NotImplementedError("BlueprintCreationAgent not available - file not implemented")
        agent_result = await self.blueprint_creation_agent.process_request(
            {
                "type": "create_blueprint",
                "workflow_id": workflow_id,
                "current_state_workflow_id": current_state_workflow_id
            },
            context
        )
        
        # Extract blueprint from agent result
        blueprint_result = agent_result.get("artifact", {})
        
        # Ensure blueprint_id exists
        blueprint_id = blueprint_result.get("blueprint_id") or f"blueprint_{workflow_id}_{str(uuid.uuid4())}"
        if not blueprint_result.get("blueprint_id"):
            blueprint_result["blueprint_id"] = blueprint_id
        
        # Store in Artifact Plane (same pattern as roadmap/POC)
        artifact_payload = {
            "blueprint": blueprint_result,
            "current_state": blueprint_result.get("current_state", {}),
            "coexistence_state": blueprint_result.get("coexistence_state", {}),
            "roadmap": blueprint_result.get("roadmap", {}),
            "responsibility_matrix": blueprint_result.get("responsibility_matrix", {}),
            "sections": blueprint_result.get("sections", [])
        }
        
        if self.artifact_plane:
            try:
                artifact_result = await self.artifact_plane.create_artifact(
                    artifact_type="blueprint",
                    artifact_id=blueprint_id,
                    payload=artifact_payload,
                    context=context,
                    metadata={
                        "regenerable": True,
                        "retention_policy": "session"
                    }
                )
                
                stored_artifact_id = artifact_result.get("artifact_id", blueprint_id)
                
                return {
                    "artifacts": {
                        "blueprint_id": stored_artifact_id,
                        "blueprint": {
                            "result_type": "blueprint",
                            "semantic_payload": {
                                "blueprint_id": stored_artifact_id,
                                "execution_id": context.execution_id,
                                "session_id": context.session_id
                            },
                            "renderings": {}
                        }
                    },
                    "events": [
                        {
                            "type": "blueprint_created",
                            "blueprint_id": stored_artifact_id,
                            "session_id": context.session_id
                        }
                    ]
                }
            except Exception as e:
                self.logger.error(f"Failed to store blueprint in Artifact Plane: {e}", exc_info=True)
                # Fall through to fallback
        
        # Fallback (should not happen in production)
        self.logger.warning("Artifact Plane not available, falling back to execution state storage")
        return {
            "artifacts": {
                "blueprint": blueprint_result,
                "blueprint_id": blueprint_id
            },
            "events": [
                {
                    "type": "blueprint_created",
                    "blueprint_id": blueprint_id,
                    "session_id": context.session_id
                }
            ]
        }
    
    async def _handle_export_artifact(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle export_artifact intent."""
        from symphainy_platform.foundations.libraries.export.export_service import ExportService
        
        export_service = ExportService(public_works=self.public_works)
        
        artifact_type = intent.parameters.get("artifact_type")
        artifact_id = intent.parameters.get("artifact_id")
        export_format = intent.parameters.get("export_format", "json")
        
        if not artifact_type or not artifact_id:
            raise ValueError("artifact_type and artifact_id are required")
        
        if artifact_type not in ["blueprint", "poc", "roadmap"]:
            raise ValueError(f"Invalid artifact_type: {artifact_type}. Must be 'blueprint', 'poc', or 'roadmap'")
        
        export_result = await export_service.export_artifact(
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            export_format=export_format,
            context=context
        )
        
        return {
            "artifacts": {
                "export": export_result
            },
            "events": [
                {
                    "type": "artifact_exported",
                    "artifact_type": artifact_type,
                    "artifact_id": artifact_id,
                    "export_format": export_format
                }
            ]
        }
    
    async def _handle_create_blueprint_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle create_blueprint SOA API (dual call pattern)."""
        if intent and context:
            return await self._handle_create_blueprint(intent, context)
        else:
            workflow_id = kwargs.get("workflow_id")
            current_state_workflow_id = kwargs.get("current_state_workflow_id")
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent_obj = IntentFactory.create_intent(
                intent_type="create_blueprint",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "workflow_id": workflow_id,
                    "current_state_workflow_id": current_state_workflow_id
                }
            )
            
            exec_context = ExecutionContext(
                execution_id="create_blueprint",
                intent=intent_obj,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
            
            return await self._handle_create_blueprint(intent_obj, exec_context)
    
    async def _handle_get_pillar_summaries_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle get_pillar_summaries SOA API (dual call pattern)."""
        session_id = kwargs.get("session_id")
        user_context = kwargs.get("user_context", {})
        tenant_id = user_context.get("tenant_id", "default")
        solution_id = user_context.get("solution_id", "default")
        
        if not session_id:
            raise ValueError("session_id is required")
        
        exec_context = ExecutionContext(
            execution_id="get_pillar_summaries",
            tenant_id=tenant_id,
            session_id=session_id,
            solution_id=solution_id
        )
        
        # Get session state
        if exec_context.state_surface:
            session_state = await exec_context.state_surface.get_session_state(
                session_id,
                tenant_id
            )
            
            if session_state:
                return {
                    "success": True,
                    "pillar_summaries": {
                        "content": session_state.get("content_pillar_summary", {}),
                        "insights": session_state.get("insights_pillar_summary", {}),
                        "journey": session_state.get("journey_pillar_summary", {})
                    }
                }
        
        # Return empty summaries if not found
        return {
            "success": True,
            "pillar_summaries": {
                "content": {},
                "insights": {},
                "journey": {}
            }
        }
    
    async def _handle_export_artifact_soa(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle export_artifact SOA API (dual call pattern)."""
        if intent and context:
            return await self._handle_export_artifact(intent, context)
        else:
            artifact_type = kwargs.get("artifact_type")
            artifact_id = kwargs.get("artifact_id")
            export_format = kwargs.get("export_format", "json")
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent_obj = IntentFactory.create_intent(
                intent_type="export_artifact",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "artifact_type": artifact_type,
                    "artifact_id": artifact_id,
                    "export_format": export_format
                }
            )
            
            exec_context = ExecutionContext(
                execution_id="export_artifact",
                intent=intent_obj,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
            
            return await self._handle_export_artifact(intent_obj, exec_context)