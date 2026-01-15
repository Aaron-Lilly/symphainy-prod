"""
Data Mash Orchestrator

Coordinates Data Mash execution through saga composition.

WHAT (Insights Realm): I orchestrate Data Mash operations
HOW (Orchestrator): I compose saga steps, call services, attach agents
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger, get_clock

from symphainy_platform.runtime.data_mash_saga import DataMashSaga, DataMashPhase


class DataMashOrchestrator:
    """
    Data Mash Orchestrator - Coordinates Data Mash execution.
    
    Orchestrates the Data Mash flow:
    1. Data Quality Analysis
    2. Semantic Interpretation
    3. Semantic Mapping
    4. Registration
    """
    
    def __init__(
        self,
        data_quality_service: Optional[Any] = None,
        semantic_interpretation_service: Optional[Any] = None,
        semantic_mapping_service: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        saga_coordinator: Optional[Any] = None
    ):
        """
        Initialize Data Mash Orchestrator.
        
        Args:
            data_quality_service: Data Quality Service instance
            semantic_interpretation_service: Semantic Interpretation Service instance
            semantic_mapping_service: Semantic Mapping Service instance
            state_surface: State Surface instance
            saga_coordinator: Saga Coordinator instance (for creating DataMashSaga)
        """
        self.data_quality_service = data_quality_service
        self.semantic_interpretation_service = semantic_interpretation_service
        self.semantic_mapping_service = semantic_mapping_service
        self.state_surface = state_surface
        self.saga_coordinator = saga_coordinator
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("✅ Data Mash Orchestrator initialized")
    
    async def create_mash(
        self,
        content_refs: List[str],
        options: Dict[str, Any],
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create Data Mash using DataMashSaga.
        
        Flow:
        1. Create DataMashSaga
        2. Execute Data Quality phase
        3. Execute Semantic Interpretation phase
        4. Execute Semantic Mapping phase
        5. Execute Registration phase
        
        Args:
            content_refs: List of content references (file_ids or parsed_file_ids)
            options: Mash options (target_domain, confidence_level, etc.)
            execution_context: Execution context with tenant_id, session_id, etc.
        
        Returns:
            Dict with mash_id and mash_result
        """
        try:
            tenant_id = execution_context.get("tenant_id")
            session_id = execution_context.get("session_id")
            
            # Create DataMashSaga
            if not self.saga_coordinator:
                return {
                    "success": False,
                    "error": "Saga Coordinator not available"
                }
            
            base_saga = await self.saga_coordinator.create_saga(
                tenant_id=tenant_id,
                session_id=session_id,
                saga_name="data_mash",
                context={
                    "content_refs": content_refs,
                    "options": options,
                    "execution_context": execution_context
                }
            )
            
            data_mash_saga = DataMashSaga(
                saga=base_saga,
                data_mash_orchestrator=self
            )
            
            mash_id = data_mash_saga.saga_id
            self.logger.info(f"Creating Data Mash: {mash_id} (content_refs: {len(content_refs)})")
            
            # Phase 1: Data Quality Analysis
            quality_result = await data_mash_saga.execute_phase(
                phase=DataMashPhase.DATA_QUALITY,
                context={
                    "content_refs": content_refs,
                    "options": options,
                    "execution_context": execution_context
                }
            )
            
            if not quality_result.get("success"):
                return quality_result
            
            quality_report = quality_result.get("quality_report")
            
            # Phase 2: Semantic Interpretation
            # TODO: Get deterministic candidates from Content Realm
            deterministic_candidates = []
            
            interpretation_result = await data_mash_saga.execute_phase(
                phase=DataMashPhase.SEMANTIC_INTERPRETATION,
                context={
                    "quality_report": quality_report,
                    "deterministic_candidates": deterministic_candidates,
                    "options": options,
                    "execution_context": execution_context
                }
            )
            
            if not interpretation_result.get("success"):
                return interpretation_result
            
            interpretation = interpretation_result.get("interpretation")
            
            # Phase 3: Semantic Mapping
            mapping_result = await data_mash_saga.execute_phase(
                phase=DataMashPhase.SEMANTIC_MAPPING,
                context={
                    "interpretations": [interpretation],
                    "options": options,
                    "execution_context": execution_context
                }
            )
            
            if not mapping_result.get("success"):
                return mapping_result
            
            canonical_model = mapping_result.get("canonical_model")
            
            # Phase 4: Registration
            registration_result = await data_mash_saga.execute_phase(
                phase=DataMashPhase.REGISTERED,
                context={
                    "canonical_model": canonical_model,
                    "options": options,
                    "execution_context": execution_context
                }
            )
            
            if not registration_result.get("success"):
                return registration_result
            
            # Store final state in State Surface
            if self.state_surface:
                await self.state_surface.set_execution_state(
                    execution_id=mash_id,
                    tenant_id=tenant_id,
                    state={
                        "mash_id": mash_id,
                        "content_refs": content_refs,
                        "quality_report": quality_report,
                        "interpretation": interpretation,
                        "canonical_model": canonical_model,
                        "status": "completed",
                        "created_at": self.clock.now_iso()
                    }
                )
            
            return {
                "success": True,
                "mash_id": mash_id,
                "mash_result": {
                    "quality_report": quality_report,
                    "interpretation": interpretation,
                    "canonical_model": canonical_model
                }
            }
        
        except Exception as e:
            self.logger.error(f"❌ Data Mash creation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Data Mash creation failed: {str(e)}"
            }
