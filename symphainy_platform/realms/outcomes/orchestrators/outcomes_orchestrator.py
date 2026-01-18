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
        
        # Extract semantic payload
        semantic_payload = {
            "roadmap_id": roadmap_result.get("roadmap_id"),
            "session_id": context.session_id,
            "status": roadmap_result.get("status")
        }
        
        # Collect renderings
        renderings = {
            "roadmap": roadmap_result,
            "strategic_plan": roadmap_result.get("strategic_plan")
        }
        
        if visual_result and visual_result.get("success"):
            renderings["roadmap_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        # Create structured artifact
        structured_artifact = create_structured_artifact(
            result_type="roadmap",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        return {
            "artifacts": {
                "roadmap": structured_artifact
            },
            "events": [
                {
                    "type": "roadmap_generated",
                    "roadmap_id": roadmap_result.get("roadmap_id"),
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
        
        # Extract semantic payload
        semantic_payload = {
            "poc_id": poc_result.get("proposal_id"),
            "session_id": context.session_id,
            "status": poc_result.get("status")
        }
        
        # Collect renderings
        renderings = {
            "poc_proposal": poc_result,
            "proposal": poc_result.get("proposal")
        }
        
        if visual_result and visual_result.get("success"):
            renderings["poc_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        # Create structured artifact
        structured_artifact = create_structured_artifact(
            result_type="poc",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        return {
            "artifacts": {
                "poc": structured_artifact
            },
            "events": [
                {
                    "type": "poc_proposal_created",
                    "proposal_id": poc_result.get("proposal_id"),
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
        Handle create_solution intent - create platform solution from roadmap/POC.
        
        Uses Solution SDK to create and register solutions.
        """
        # Get solution source (roadmap or POC)
        solution_source = intent.parameters.get("solution_source")  # "roadmap" or "poc"
        source_id = intent.parameters.get("source_id")  # roadmap_id or proposal_id
        
        if not solution_source or not source_id:
            raise ValueError("solution_source and source_id are required for create_solution intent")
        
        # Read source artifact from State Surface
        source_reference = f"{solution_source}:{context.tenant_id}:{context.session_id}:{source_id}"
        source_data = await context.state_surface.get_file(source_reference)
        
        if not source_data:
            # Try to get from execution state
            execution_state = await context.state_surface.get_execution_state(
                source_id,
                context.tenant_id
            )
            if execution_state:
                source_data = execution_state.get("artifacts", {}).get(solution_source)
        
        if not source_data:
            raise ValueError(f"Source {solution_source} with id {source_id} not found")
        
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
