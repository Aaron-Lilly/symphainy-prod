"""
Insights Orchestrator - Coordinates Insights Operations

Coordinates enabling services for data analysis and insights.

WHAT (Orchestrator Role): I coordinate insights operations
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

from typing import Dict, Any, Optional, List
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from symphainy_platform.runtime.intent_model import Intent
    from symphainy_platform.runtime.execution_context import ExecutionContext

from utilities import get_logger
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from ..enabling_services.data_analyzer_service import DataAnalyzerService
from ..enabling_services.metrics_calculator_service import MetricsCalculatorService
from ..enabling_services.data_quality_service import DataQualityService
from ..enabling_services.semantic_self_discovery_service import SemanticSelfDiscoveryService
from ..enabling_services.guided_discovery_service import GuidedDiscoveryService
from ..enabling_services.structured_analysis_service import StructuredAnalysisService
from ..enabling_services.unstructured_analysis_service import UnstructuredAnalysisService
from ..enabling_services.lineage_visualization_service import LineageVisualizationService
from ..enabling_services.structured_extraction_service import StructuredExtractionService
from ..agents.insights_liaison_agent import InsightsLiaisonAgent
from symphainy_platform.civic_systems.artifact_plane.artifact_plane import ArtifactPlane
from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK


class InsightsOrchestrator:
    """
    Insights Orchestrator - Coordinates insights operations.
    
    Coordinates:
    - Data analysis
    - Metrics calculation
    - Semantic mapping
    - Quality assessment
    - Data interpretation (self-discovery and guided)
    - Business analysis (structured and unstructured)
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Insights Orchestrator.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Initialize enabling services with Public Works
        self.data_analyzer_service = DataAnalyzerService(public_works=public_works)
        self.metrics_calculator_service = MetricsCalculatorService(public_works=public_works)
        self.data_quality_service = DataQualityService(public_works=public_works)
        self.semantic_self_discovery_service = SemanticSelfDiscoveryService(public_works=public_works)
        self.guided_discovery_service = GuidedDiscoveryService(public_works=public_works)
        self.structured_analysis_service = StructuredAnalysisService(public_works=public_works)
        self.unstructured_analysis_service = UnstructuredAnalysisService(public_works=public_works)
        self.lineage_visualization_service = LineageVisualizationService(public_works=public_works)
        self.structured_extraction_service = StructuredExtractionService(public_works=public_works)
        self.insights_liaison_agent = InsightsLiaisonAgent(public_works=public_works)
    
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
        
        if intent_type == "analyze_content":
            return await self._handle_analyze_content(intent, context)
        elif intent_type == "interpret_data":
            return await self._handle_interpret_data(intent, context)
        elif intent_type == "map_relationships":
            return await self._handle_map_relationships(intent, context)
        elif intent_type == "query_data":
            return await self._handle_query_data(intent, context)
        elif intent_type == "calculate_metrics":
            return await self._handle_calculate_metrics(intent, context)
        elif intent_type == "assess_data_quality":
            return await self._handle_assess_data_quality(intent, context)
        elif intent_type == "interpret_data_self_discovery":
            return await self._handle_self_discovery(intent, context)
        elif intent_type == "interpret_data_guided":
            return await self._handle_guided_discovery(intent, context)
        elif intent_type == "analyze_structured_data":
            return await self._handle_analyze_structured(intent, context)
        elif intent_type == "analyze_unstructured_data":
            return await self._handle_analyze_unstructured(intent, context)
        elif intent_type == "visualize_lineage":
            return await self._handle_visualize_lineage(intent, context)
        elif intent_type == "extract_structured_data":
            return await self._handle_extract_structured_data(intent, context)
        elif intent_type == "discover_extraction_pattern":
            return await self._handle_discover_extraction_pattern(intent, context)
        elif intent_type == "create_extraction_config":
            return await self._handle_create_extraction_config(intent, context)
        else:
            raise ValueError(f"Unknown intent type: {intent_type}")
    
    async def _handle_analyze_content(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle analyze_content intent."""
        parsed_file_id = intent.parameters.get("parsed_file_id")
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for analyze_content intent")
        
        # Analyze content via DataAnalyzerService
        analysis_result = await self.data_analyzer_service.analyze_content(
            parsed_file_id=parsed_file_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "analysis": analysis_result,
                "parsed_file_id": parsed_file_id
            },
            "events": [
                {
                    "type": "content_analyzed",
                    "parsed_file_id": parsed_file_id
                }
            ]
        }
    
    async def _handle_interpret_data(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle interpret_data intent."""
        parsed_file_id = intent.parameters.get("parsed_file_id")
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for interpret_data intent")
        
        # Interpret data via DataAnalyzerService
        interpretation_result = await self.data_analyzer_service.interpret_data(
            parsed_file_id=parsed_file_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "interpretation": interpretation_result,
                "parsed_file_id": parsed_file_id
            },
            "events": [
                {
                    "type": "data_interpreted",
                    "parsed_file_id": parsed_file_id
                }
            ]
        }
    
    async def _handle_map_relationships(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle map_relationships intent."""
        parsed_file_id = intent.parameters.get("parsed_file_id")
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for map_relationships intent")
        
        # Map relationships via DataAnalyzerService
        mapping_result = await self.data_analyzer_service.map_relationships(
            parsed_file_id=parsed_file_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "relationships": mapping_result,
                "parsed_file_id": parsed_file_id
            },
            "events": [
                {
                    "type": "relationships_mapped",
                    "parsed_file_id": parsed_file_id
                }
            ]
        }
    
    async def _handle_query_data(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle query_data intent."""
        query = intent.parameters.get("query")
        if not query:
            raise ValueError("query is required for query_data intent")
        
        # Query data via SemanticDataAbstraction
        query_result = await self.data_analyzer_service.query_data(
            query=query,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "query_results": query_result
            },
            "events": [
                {
                    "type": "data_queried",
                    "query": query
                }
            ]
        }
    
    async def _handle_calculate_metrics(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle calculate_metrics intent."""
        parsed_file_id = intent.parameters.get("parsed_file_id")
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for calculate_metrics intent")
        
        # Calculate metrics via MetricsCalculatorService
        metrics_result = await self.metrics_calculator_service.calculate_metrics(
            parsed_file_id=parsed_file_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "metrics": metrics_result,
                "parsed_file_id": parsed_file_id
            },
            "events": [
                {
                    "type": "metrics_calculated",
                    "parsed_file_id": parsed_file_id
                }
            ]
        }
    
    async def _handle_assess_data_quality(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle assess_data_quality intent."""
        parsed_file_id = intent.parameters.get("parsed_file_id")
        source_file_id = intent.parameters.get("source_file_id")
        parser_type = intent.parameters.get("parser_type", "unknown")
        deterministic_embedding_id = intent.parameters.get("deterministic_embedding_id")
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for assess_data_quality intent")
        
        if not source_file_id:
            raise ValueError("source_file_id is required for assess_data_quality intent")
        
        # Assess quality via DataQualityService
        quality_result = await self.data_quality_service.assess_data_quality(
            parsed_file_id=parsed_file_id,
            source_file_id=source_file_id,
            parser_type=parser_type,
            tenant_id=context.tenant_id,
            context=context,
            deterministic_embedding_id=deterministic_embedding_id
        )
        
        return {
            "artifacts": {
                "quality_assessment": quality_result.get("quality_assessment"),
                "parsed_file_id": parsed_file_id,
                "source_file_id": source_file_id,
                "deterministic_embedding_id": deterministic_embedding_id
            },
            "events": [
                {
                    "type": "data_quality_assessed",
                    "parsed_file_id": parsed_file_id,
                    "source_file_id": source_file_id,
                    "deterministic_embedding_id": deterministic_embedding_id
                }
            ]
        }
    
    async def _handle_self_discovery(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle interpret_data_self_discovery intent."""
        # Accept both parsed_file_id and parsed_result_id (aliases)
        parsed_file_id = intent.parameters.get("parsed_file_id") or intent.parameters.get("parsed_result_id")
        if not parsed_file_id:
            raise ValueError("parsed_file_id or parsed_result_id is required for interpret_data_self_discovery intent")
        
        discovery_options = intent.parameters.get("discovery_options", {})
        
        # Get embeddings from ArangoDB
        embeddings = await self._get_embeddings(parsed_file_id, context.tenant_id, context)
        
        # Discover semantics via SemanticSelfDiscoveryService
        discovery_result = await self.semantic_self_discovery_service.discover_semantics(
            parsed_file_id=parsed_file_id,
            embeddings=embeddings or [],
            discovery_options=discovery_options,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Track interpretation in Supabase for lineage and promote to Record of Fact
        interpretation_uuid = await self._track_interpretation(
            parsed_file_id=parsed_file_id,
            interpretation_type="self_discovery",
            interpretation_result=discovery_result,
            guide_id=None,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Promote interpretation to Record of Fact
        if interpretation_uuid and self.data_steward_sdk:
            await self._promote_interpretation_to_record_of_fact(
                interpretation_uuid=interpretation_uuid,
                parsed_file_id=parsed_file_id,
                interpretation_result=discovery_result,
                tenant_id=context.tenant_id,
                context=context
            )
        
        return {
            "artifacts": {
                "discovery": discovery_result,
                "parsed_file_id": parsed_file_id
            },
            "events": [
                {
                    "type": "semantics_discovered",
                    "parsed_file_id": parsed_file_id
                }
            ]
        }
    
    async def _handle_guided_discovery(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle interpret_data_guided intent."""
        # Accept both parsed_file_id and parsed_result_id (aliases)
        parsed_file_id = intent.parameters.get("parsed_file_id") or intent.parameters.get("parsed_result_id")
        guide_id = intent.parameters.get("guide_id")
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id or parsed_result_id is required for interpret_data_guided intent")
        
        if not guide_id:
            raise ValueError("guide_id is required for interpret_data_guided intent")
        
        matching_options = intent.parameters.get("matching_options", {})
        
        # Get embeddings from ArangoDB
        embeddings = await self._get_embeddings(parsed_file_id, context.tenant_id, context)
        
        # Interpret with guide via GuidedDiscoveryService
        interpretation_result = await self.guided_discovery_service.interpret_with_guide(
            parsed_file_id=parsed_file_id,
            guide_id=guide_id,
            embeddings=embeddings or [],
            matching_options=matching_options,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Get guide UUID from Supabase
        guide_uuid = await self._get_guide_uuid(guide_id, context.tenant_id)
        
        # Track interpretation in Supabase for lineage and promote to Record of Fact
        interpretation_uuid = await self._track_interpretation(
            parsed_file_id=parsed_file_id,
            interpretation_type="guided",
            interpretation_result=interpretation_result,
            guide_id=guide_uuid,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Promote interpretation to Record of Fact
        if interpretation_uuid and self.data_steward_sdk:
            await self._promote_interpretation_to_record_of_fact(
                interpretation_uuid=interpretation_uuid,
                parsed_file_id=parsed_file_id,
                interpretation_result=interpretation_result,
                tenant_id=context.tenant_id,
                context=context
            )
        
        return {
            "artifacts": {
                "interpretation": interpretation_result.get("interpretation"),
                "parsed_file_id": parsed_file_id,
                "guide_id": guide_id
            },
            "events": [
                {
                    "type": "data_interpreted_with_guide",
                    "parsed_file_id": parsed_file_id,
                    "guide_id": guide_id
                }
            ]
        }
    
    async def _handle_analyze_structured(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle analyze_structured_data intent."""
        # Accept both parsed_file_id and parsed_result_id (aliases)
        parsed_file_id = intent.parameters.get("parsed_file_id") or intent.parameters.get("parsed_result_id")
        if not parsed_file_id:
            raise ValueError("parsed_file_id or parsed_result_id is required for analyze_structured_data intent")
        
        analysis_options = intent.parameters.get("analysis_options", {})
        
        # Analyze structured data via StructuredAnalysisService
        analysis_result = await self.structured_analysis_service.analyze_structured_data(
            parsed_file_id=parsed_file_id,
            analysis_options=analysis_options,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Track analysis in Supabase for lineage
        analysis_uuid = await self._track_analysis(
            parsed_file_id=parsed_file_id,
            analysis_type="structured",
            analysis_result=analysis_result,
            deep_dive=False,
            agent_session_id=None,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Register as Purpose-Bound Outcome in Artifact Plane
        artifact_id = None
        if self.artifact_plane:
            try:
                # Create artifact payload
                artifact_payload = {
                    "result_type": "structured_analysis",
                    "analysis_result": analysis_result,
                    "parsed_file_id": parsed_file_id
                }
                
                artifact_result = await self.artifact_plane.create_artifact(
                    artifact_type="analysis_report",
                    artifact_id=f"structured_analysis_{parsed_file_id}",
                    payload=artifact_payload,
                    context=context,
                    lifecycle_state="draft",
                    owner="client",
                    purpose="decision_support",  # Analysis reports support decisions
                    source_artifact_ids=[parsed_file_id] if parsed_file_id else None
                )
                
                artifact_id = artifact_result.get("artifact_id")
                self.logger.info(f"✅ Structured analysis registered in Artifact Plane: {artifact_id}")
            except Exception as e:
                self.logger.warning(f"Failed to register structured analysis in Artifact Plane: {e}")
        
        return {
            "artifacts": {
                "structured_analysis": analysis_result,
                "parsed_file_id": parsed_file_id,
                "artifact_id": artifact_id  # Include artifact_id reference
            },
            "events": [
                {
                    "type": "structured_data_analyzed",
                    "parsed_file_id": parsed_file_id,
                    "artifact_id": artifact_id,
                    "analysis_uuid": analysis_uuid
                }
            ]
        }
    
    async def _handle_analyze_unstructured(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle analyze_unstructured_data intent."""
        # Accept both parsed_file_id and parsed_result_id (aliases)
        parsed_file_id = intent.parameters.get("parsed_file_id") or intent.parameters.get("parsed_result_id")
        if not parsed_file_id:
            raise ValueError("parsed_file_id or parsed_result_id is required for analyze_unstructured_data intent")
        
        analysis_options = intent.parameters.get("analysis_options", {})
        deep_dive = analysis_options.get("deep_dive", False)
        
        # Analyze unstructured data via UnstructuredAnalysisService
        analysis_result = await self.unstructured_analysis_service.analyze_unstructured_data(
            parsed_file_id=parsed_file_id,
            analysis_options=analysis_options,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Get agent session ID if deep dive was initiated
        agent_session_id = None
        if deep_dive and analysis_result.get("deep_dive"):
            agent_session_id = analysis_result["deep_dive"].get("session_id")
        
        # Track analysis in Supabase for lineage
        analysis_uuid = await self._track_analysis(
            parsed_file_id=parsed_file_id,
            analysis_type="unstructured",
            analysis_result=analysis_result,
            deep_dive=deep_dive,
            agent_session_id=agent_session_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Register as Purpose-Bound Outcome in Artifact Plane
        artifact_id = None
        if self.artifact_plane:
            try:
                # Create artifact payload
                artifact_payload = {
                    "result_type": "unstructured_analysis",
                    "analysis_result": analysis_result,
                    "parsed_file_id": parsed_file_id,
                    "deep_dive": deep_dive
                }
                
                artifact_result = await self.artifact_plane.create_artifact(
                    artifact_type="analysis_report",
                    artifact_id=f"unstructured_analysis_{parsed_file_id}",
                    payload=artifact_payload,
                    context=context,
                    lifecycle_state="draft",
                    owner="client",
                    purpose="decision_support",  # Analysis reports support decisions
                    source_artifact_ids=[parsed_file_id] if parsed_file_id else None
                )
                
                artifact_id = artifact_result.get("artifact_id")
                self.logger.info(f"✅ Unstructured analysis registered in Artifact Plane: {artifact_id}")
            except Exception as e:
                self.logger.warning(f"Failed to register unstructured analysis in Artifact Plane: {e}")
        
        return {
            "artifacts": {
                "unstructured_analysis": analysis_result,
                "parsed_file_id": parsed_file_id,
                "deep_dive_initiated": deep_dive,
                "artifact_id": artifact_id  # Include artifact_id reference
            },
            "events": [
                {
                    "type": "unstructured_data_analyzed",
                    "parsed_file_id": parsed_file_id,
                    "deep_dive": deep_dive,
                    "artifact_id": artifact_id,
                    "analysis_uuid": analysis_uuid
                }
            ]
        }
    
    async def _handle_visualize_lineage(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle visualize_lineage intent."""
        file_id = intent.parameters.get("file_id")
        if not file_id:
            raise ValueError("file_id is required for visualize_lineage intent")
        
        # Visualize lineage via LineageVisualizationService
        visualization_result = await self.lineage_visualization_service.visualize_lineage(
            file_id=file_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Register visualization as Purpose-Bound Outcome in Artifact Plane
        artifact_id = None
        if self.artifact_plane:
            try:
                # Create artifact payload
                artifact_payload = {
                    "result_type": "lineage_visualization",
                    "visualization_result": visualization_result,
                    "file_id": file_id
                }
                
                artifact_result = await self.artifact_plane.create_artifact(
                    artifact_type="visualization",
                    artifact_id=f"lineage_viz_{file_id}",
                    payload=artifact_payload,
                    context=context,
                    lifecycle_state="draft",
                    owner="client",
                    purpose="delivery",  # Visualizations are deliverables
                    source_artifact_ids=[file_id] if file_id else None
                )
                
                artifact_id = artifact_result.get("artifact_id")
                self.logger.info(f"✅ Lineage visualization registered in Artifact Plane: {artifact_id}")
            except Exception as e:
                self.logger.warning(f"Failed to register lineage visualization in Artifact Plane: {e}")
        
        return {
            "artifacts": {
                "lineage_visualization": visualization_result,
                "file_id": file_id,
                "artifact_id": artifact_id  # Include artifact_id reference
            },
            "events": [
                {
                    "type": "lineage_visualized",
                    "file_id": file_id,
                    "artifact_id": artifact_id
                }
            ]
        }
    
    async def _get_embeddings(
        self,
        parsed_file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Optional[List[Dict[str, Any]]]:
        """Get embeddings from ArangoDB for parsed file."""
        if not self.public_works:
            return None
        
        arango_adapter = self.public_works.get_arango_adapter()
        if not arango_adapter:
            return None
        
        try:
            # Query embeddings collection for this parsed_file_id
            if await arango_adapter.collection_exists("embeddings"):
                query = """
                FOR e IN embeddings
                FILTER e.parsed_file_id == @parsed_file_id
                RETURN e
                """
                bind_vars = {"parsed_file_id": parsed_file_id}
                
                embeddings = await arango_adapter.execute_aql(query, bind_vars=bind_vars)
                return embeddings if embeddings else None
        except Exception as e:
            self.logger.debug(f"Could not retrieve embeddings: {e}")
        
        return None
    
    async def _track_interpretation(
        self,
        parsed_file_id: str,
        interpretation_type: str,
        interpretation_result: Dict[str, Any],
        guide_id: Optional[str],
        tenant_id: str,
        context: ExecutionContext
    ):
        """
        Track interpretation in Supabase for lineage tracking.
        
        Args:
            parsed_file_id: Parsed file identifier
            interpretation_type: "self_discovery" or "guided"
            interpretation_result: Full interpretation results
            guide_id: Guide UUID (if guided discovery)
            tenant_id: Tenant identifier
            context: Execution context
        """
        if not self.public_works:
            self.logger.debug("Public Works not available, skipping lineage tracking")
            return
        
        supabase_adapter = self.public_works.get_supabase_adapter()
        if not supabase_adapter:
            self.logger.debug("Supabase adapter not available, skipping lineage tracking")
            return
        
        try:
            # Get file_id and parsed_result_id from Supabase
            file_id, parsed_result_uuid, embedding_uuid = await self._get_lineage_ids(
                parsed_file_id, tenant_id
            )
            
            # Extract confidence and coverage scores if available
            interpretation_data = interpretation_result.get("interpretation", interpretation_result)
            confidence_score = interpretation_data.get("confidence_score")
            coverage_score = interpretation_data.get("coverage_score")
            
            # Prepare interpretation record
            interpretation_record = {
                "id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "file_id": file_id or "",
                "parsed_result_id": parsed_result_uuid,
                "embedding_id": embedding_uuid,
                "guide_id": guide_id,
                "interpretation_type": interpretation_type,
                "interpretation_result": interpretation_result,
                "confidence_score": confidence_score,
                "coverage_score": coverage_score
            }
            
            # Insert into Supabase
            result = await supabase_adapter.execute_rls_policy(
                table="interpretations",
                operation="insert",
                user_context={"tenant_id": tenant_id},
                data=interpretation_record
            )
            
            if result.get("success"):
                interpretation_uuid = interpretation_record.get("id")
                self.logger.debug(f"Tracked interpretation in Supabase: {parsed_file_id} (UUID: {interpretation_uuid})")
                return interpretation_uuid
            else:
                self.logger.warning(f"Failed to track interpretation: {result.get('error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to track interpretation: {e}", exc_info=True)
            return None
    
    async def _track_analysis(
        self,
        parsed_file_id: str,
        analysis_type: str,
        analysis_result: Dict[str, Any],
        deep_dive: bool,
        agent_session_id: Optional[str],
        tenant_id: str,
        context: ExecutionContext
    ) -> Optional[str]:
        """
        Track analysis in Supabase for lineage tracking.
        
        Args:
            parsed_file_id: Parsed file identifier
            analysis_type: "structured" or "unstructured"
            analysis_result: Full analysis results
            deep_dive: Whether Insights Liaison Agent was used
            agent_session_id: Agent session ID if deep_dive=true
            tenant_id: Tenant identifier
            context: Execution context
        """
        if not self.public_works:
            self.logger.debug("Public Works not available, skipping lineage tracking")
            return
        
        supabase_adapter = self.public_works.get_supabase_adapter()
        if not supabase_adapter:
            self.logger.debug("Supabase adapter not available, skipping lineage tracking")
            return
        
        try:
            # Get file_id and parsed_result_id from Supabase
            file_id, parsed_result_uuid, embedding_uuid = await self._get_lineage_ids(
                parsed_file_id, tenant_id
            )
            
            # Prepare analysis record
            analysis_record = {
                "id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "file_id": file_id or "",
                "parsed_result_id": parsed_result_uuid,
                "interpretation_id": None,  # Can link to interpretation if available
                "analysis_type": analysis_type,
                "analysis_result": analysis_result,
                "deep_dive": deep_dive,
                "agent_session_id": agent_session_id
            }
            
            # Insert into Supabase
            result = await supabase_adapter.execute_rls_policy(
                table="analyses",
                operation="insert",
                user_context={"tenant_id": tenant_id},
                data=analysis_record
            )
            
            if result.get("success"):
                self.logger.debug(f"Tracked analysis in Supabase: {parsed_file_id}")
            else:
                self.logger.warning(f"Failed to track analysis: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Failed to track analysis: {e}", exc_info=True)
    
    async def _get_lineage_ids(
        self,
        parsed_file_id: str,
        tenant_id: str
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Get lineage IDs (file_id, parsed_result_uuid, embedding_uuid) from Supabase.
        
        Returns:
            Tuple of (file_id, parsed_result_uuid, embedding_uuid)
        """
        if not self.public_works:
            return (None, None, None)
        
        supabase_adapter = self.public_works.get_supabase_adapter()
        if not supabase_adapter:
            return (None, None, None)
        
        try:
            # Query parsed_results table
            query_result = await supabase_adapter.execute_rls_policy(
                table="parsed_results",
                operation="select",
                user_context={"tenant_id": tenant_id},
                data=None
            )
            
            file_id = None
            parsed_result_uuid = None
            embedding_uuid = None
            
            if query_result.get("success") and query_result.get("data"):
                matching_records = [
                    r for r in query_result["data"]
                    if r.get("parsed_result_id") == parsed_file_id and r.get("tenant_id") == tenant_id
                ]
                if matching_records:
                    parsed_result_uuid = matching_records[0].get("id")
                    file_id = matching_records[0].get("file_id")
                    
                    # Try to get embedding UUID
                    embedding_query = await supabase_adapter.execute_rls_policy(
                        table="embeddings",
                        operation="select",
                        user_context={"tenant_id": tenant_id},
                        data=None
                    )
                    if embedding_query.get("success") and embedding_query.get("data"):
                        embedding_matches = [
                            e for e in embedding_query["data"]
                            if e.get("parsed_result_id") == parsed_result_uuid
                        ]
                        if embedding_matches:
                            embedding_uuid = embedding_matches[0].get("id")
            
            return (file_id, parsed_result_uuid, embedding_uuid)
            
        except Exception as e:
            self.logger.debug(f"Could not get lineage IDs: {e}")
            return (None, None, None)
    
    async def _get_guide_uuid(
        self,
        guide_id: str,
        tenant_id: str
    ) -> Optional[str]:
        """Get guide UUID from guide_id string."""
        if not self.public_works:
            return None
        
        supabase_adapter = self.public_works.get_supabase_adapter()
        if not supabase_adapter:
            return None
        
        try:
            query_result = await supabase_adapter.execute_rls_policy(
                table="guides",
                operation="select",
                user_context={"tenant_id": tenant_id},
                data=None
            )
            
            if query_result.get("success") and query_result.get("data"):
                matching_records = [
                    r for r in query_result["data"]
                    if r.get("guide_id") == guide_id and r.get("tenant_id") == tenant_id
                ]
                if matching_records:
                    return matching_records[0].get("id")
        except Exception as e:
            self.logger.debug(f"Could not get guide UUID: {e}")
        
        return None
    
    async def _promote_interpretation_to_record_of_fact(
        self,
        interpretation_uuid: str,
        parsed_file_id: str,
        interpretation_result: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Optional[str]:
        """
        Promote interpretation to Record of Fact.
        
        Interpretations are persistent meaning (Records of Fact), not temporary Working Materials.
        They should be promoted immediately after creation.
        
        Args:
            interpretation_uuid: Interpretation UUID from Supabase
            parsed_file_id: Parsed file identifier
            interpretation_result: Full interpretation results
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Record of Fact ID or None if promotion failed
        """
        if not self.data_steward_sdk:
            self.logger.debug("Data Steward SDK not available, skipping promotion to Record of Fact")
            return None
        
        if not self.public_works:
            self.logger.debug("Public Works not available, skipping promotion to Record of Fact")
            return None
        
        supabase_adapter = self.public_works.get_supabase_adapter()
        if not supabase_adapter:
            self.logger.debug("Supabase adapter not available, skipping promotion to Record of Fact")
            return None
        
        try:
            # Get file_id and boundary contract info
            file_id, parsed_result_uuid, embedding_uuid = await self._get_lineage_ids(
                parsed_file_id, tenant_id
            )
            
            # Extract interpretation content
            interpretation_data = interpretation_result.get("interpretation", interpretation_result)
            
            # Promote to Record of Fact
            record_id = await self.data_steward_sdk.promote_to_record_of_fact(
                source_file_id=file_id or parsed_file_id,
                source_boundary_contract_id="system",  # System-generated interpretation
                tenant_id=tenant_id,
                record_type="interpretation",
                record_content=interpretation_data,
                interpretation_id=interpretation_uuid,
                confidence_score=interpretation_data.get("confidence_score"),
                promoted_by="system",
                promotion_reason="Interpretation created - persistent meaning",
                supabase_adapter=supabase_adapter
            )
            
            if record_id:
                self.logger.info(f"✅ Interpretation promoted to Record of Fact: {record_id}")
                return record_id
            else:
                self.logger.warning(f"Failed to promote interpretation to Record of Fact")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to promote interpretation to Record of Fact: {e}", exc_info=True)
            return None
    
    async def _handle_extract_structured_data(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Handle extract_structured_data intent (SOA API handler).
        
        Can be called from:
        - Intent handler (intent + context provided)
        - MCP tool (kwargs provided, need to create context)
        
        Args:
            intent: Optional Intent (if called from intent handler)
            context: Optional Execution context
            **kwargs: Parameters (pattern, data_source, extraction_config_id, user_context)
        
        Returns:
            Dict with extraction result
        """
        # Handle both intent-based and direct call patterns
        if intent and context:
            # Called from intent handler
            pattern = intent.parameters.get("pattern")
            data_source = intent.parameters.get("data_source", {})
            extraction_config_id = intent.parameters.get("extraction_config_id")
            tenant_id = context.tenant_id
            exec_context = context
        else:
            # Called from MCP tool (kwargs)
            pattern = kwargs.get("pattern")
            data_source = kwargs.get("data_source", {})
            extraction_config_id = kwargs.get("extraction_config_id")
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            # Create intent for ExecutionContext
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent = IntentFactory.create_intent(
                intent_type="extract_structured_data",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={
                    "pattern": pattern,
                    "data_source": data_source,
                    "extraction_config_id": extraction_config_id
                }
            )
            
            exec_context = ExecutionContext(
                execution_id=f"extract_{pattern}",
                intent=intent,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
        
        self.logger.info(f"Handling extract_structured_data: pattern={pattern}")
        
        if not pattern:
            raise ValueError("pattern parameter required")
        
        # Call structured extraction service
        result = await self.structured_extraction_service.extract_structured_data(
            pattern=pattern,
            data_source=data_source,
            extraction_config_id=extraction_config_id,
            tenant_id=tenant_id,
            context=exec_context
        )
        
        # If called from intent handler, return artifacts format
        if intent and context:
            artifact = create_structured_artifact(
                artifact_type="extraction_result",
                data=result,
                metadata={
                    "pattern": pattern,
                    "extraction_config_id": extraction_config_id,
                    "tenant_id": tenant_id
                }
            )
            return {
                "artifacts": [artifact],
                "events": []
            }
        else:
            # Called from MCP tool, return result directly
            return result
    
    async def _handle_discover_extraction_pattern(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Handle discover_extraction_pattern intent (SOA API handler).
        
        Args:
            intent: Optional Intent (if called from intent handler)
            context: Optional Execution context
            **kwargs: Parameters (data_source, user_context)
        
        Returns:
            Dict with discovered pattern
        """
        # Handle both intent-based and direct call patterns
        if intent and context:
            data_source = intent.parameters.get("data_source", {})
            tenant_id = context.tenant_id
            exec_context = context
        else:
            data_source = kwargs.get("data_source", {})
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            # Create intent for ExecutionContext
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent = IntentFactory.create_intent(
                intent_type="discover_extraction_pattern",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={"data_source": data_source}
            )
            
            exec_context = ExecutionContext(
                execution_id="discover_pattern",
                intent=intent,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
        
        self.logger.info("Handling discover_extraction_pattern")
        
        # Call structured extraction service
        result = await self.structured_extraction_service.discover_extraction_pattern(
            data_source=data_source,
            tenant_id=tenant_id,
            context=exec_context
        )
        
        # If called from intent handler, return artifacts format
        if intent and context:
            artifact = create_structured_artifact(
                artifact_type="discovered_pattern",
                data=result,
                metadata={"tenant_id": tenant_id}
            )
            return {
                "artifacts": [artifact],
                "events": []
            }
        else:
            # Called from MCP tool, return result directly
            return result
    
    async def _handle_create_extraction_config(
        self,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Handle create_extraction_config intent (SOA API handler).
        
        Args:
            intent: Optional Intent (if called from intent handler)
            context: Optional Execution context
            **kwargs: Parameters (target_model_file_id, user_context)
        
        Returns:
            Dict with created config
        """
        # Handle both intent-based and direct call patterns
        if intent and context:
            target_model_file_id = intent.parameters.get("target_model_file_id")
            tenant_id = context.tenant_id
            exec_context = context
        else:
            target_model_file_id = kwargs.get("target_model_file_id")
            user_context = kwargs.get("user_context", {})
            tenant_id = user_context.get("tenant_id", "default")
            session_id = user_context.get("session_id", "default")
            solution_id = user_context.get("solution_id", "default")
            
            # Create intent for ExecutionContext
            from symphainy_platform.runtime.intent_model import IntentFactory
            intent = IntentFactory.create_intent(
                intent_type="create_extraction_config",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id,
                parameters={"target_model_file_id": target_model_file_id}
            )
            
            exec_context = ExecutionContext(
                execution_id="create_extraction_config",
                intent=intent,
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id=solution_id
            )
        
        self.logger.info(f"Handling create_extraction_config: target_model={target_model_file_id}")
        
        if not target_model_file_id:
            raise ValueError("target_model_file_id parameter required")
        
        # Call structured extraction service
        result = await self.structured_extraction_service.create_extraction_config_from_target_model(
            target_model_file_id=target_model_file_id,
            tenant_id=tenant_id,
            context=exec_context
        )
        
        # If called from intent handler, return artifacts format
        if intent and context:
            artifact = create_structured_artifact(
                artifact_type="extraction_config",
                data=result,
                metadata={
                    "target_model_file_id": target_model_file_id,
                    "tenant_id": tenant_id
                }
            )
            return {
                "artifacts": [artifact],
                "events": []
            }
        else:
            # Called from MCP tool, return result directly
            return result
    
    def _define_soa_api_handlers(self) -> Dict[str, Any]:
        """
        Define Insights Orchestrator SOA APIs.
        
        UNIFIED PATTERN: MCP Server automatically registers these as MCP Tools.
        
        Returns:
            Dict of SOA API definitions with handlers, input schemas, and descriptions
        """
        return {
            "extract_structured_data": {
                "handler": self._handle_extract_structured_data,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "enum": ["variable_life_policy_rules", "aar", "pso", "custom"],
                            "description": "Extraction pattern name"
                        },
                        "data_source": {
                            "type": "object",
                            "description": "Data source (parsed_file_id, embeddings, etc.)",
                            "properties": {
                                "parsed_file_id": {"type": "string"},
                                "session_id": {"type": "string"}
                            }
                        },
                        "extraction_config_id": {
                            "type": ["string", "null"],
                            "description": "Optional custom extraction config ID"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context (includes workflow_id, session_id)"
                        }
                    },
                    "required": ["pattern", "data_source"]
                },
                "description": "Extract structured data using pre-configured or custom pattern"
            },
            "discover_extraction_pattern": {
                "handler": self._handle_discover_extraction_pattern,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "data_source": {
                            "type": "object",
                            "description": "Data source (parsed_file_id, embeddings, etc.)",
                            "properties": {
                                "parsed_file_id": {"type": "string"},
                                "session_id": {"type": "string"}
                            }
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": ["data_source"]
                },
                "description": "Discover extraction pattern from data (freeform analysis)"
            },
            "create_extraction_config": {
                "handler": self._handle_create_extraction_config,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target_model_file_id": {
                            "type": "string",
                            "description": "Parsed file ID of target data model"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": ["target_model_file_id"]
                },
                "description": "Create extraction configuration from target data model"
            }
        }