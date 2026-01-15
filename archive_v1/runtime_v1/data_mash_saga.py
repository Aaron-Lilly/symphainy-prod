"""
Data Mash Saga - Specialized Saga for Data Mash Execution

WHAT (Runtime): I orchestrate Data Mash execution through saga phases
HOW (Saga): I coordinate Data Mash phases and track execution state
"""

from typing import Dict, Any, Optional
from enum import Enum
from utilities import get_logger, get_clock

from .saga import Saga, SagaState, SagaStep, generate_step_id


class DataMashPhase(str, Enum):
    """Data Mash execution phases."""
    INITIATED = "initiated"
    DATA_QUALITY = "data_quality"
    SEMANTIC_INTERPRETATION = "semantic_interpretation"
    SEMANTIC_MAPPING = "semantic_mapping"
    REGISTERED = "registered"
    FAILED = "failed"


class DataMashSaga:
    """
    Data Mash Saga - Orchestrates Data Mash execution.
    
    Phases:
    1. INITIATED - Mash created, content references validated
    2. DATA_QUALITY - Data quality analysis complete
    3. SEMANTIC_INTERPRETATION - Semantic labels assigned
    4. SEMANTIC_MAPPING - Canonical model formed
    5. REGISTERED - Data product registered and exposed
    """
    
    def __init__(
        self,
        saga: Saga,
        data_mash_orchestrator: Any
    ):
        """
        Initialize Data Mash Saga.
        
        Args:
            saga: Base Saga instance
            data_mash_orchestrator: Data Mash Orchestrator instance
        """
        self.saga = saga
        self.orchestrator = data_mash_orchestrator
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.current_phase = DataMashPhase.INITIATED
    
    @property
    def saga_id(self) -> str:
        """Get saga ID."""
        return self.saga.saga_id
    
    @property
    def tenant_id(self) -> str:
        """Get tenant ID."""
        return self.saga.tenant_id
    
    @property
    def session_id(self) -> str:
        """Get session ID."""
        return self.saga.session_id
    
    async def execute_phase(
        self,
        phase: DataMashPhase,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a Data Mash phase.
        
        Args:
            phase: Phase to execute
            context: Execution context
        
        Returns:
            Phase execution result
        """
        try:
            self.logger.info(f"Executing Data Mash phase: {phase.value} (saga: {self.saga_id})")
            
            # Add saga step for this phase
            step = SagaStep(
                step_id=generate_step_id(),
                step_name=f"data_mash_{phase.value}",
                step_type="data_mash_phase",
                inputs=context,
                status="running",
                started_at=self.clock.now_utc()
            )
            
            self.saga.steps.append(step)
            
            # Execute phase-specific logic
            if phase == DataMashPhase.DATA_QUALITY:
                result = await self._execute_data_quality(context)
            elif phase == DataMashPhase.SEMANTIC_INTERPRETATION:
                result = await self._execute_semantic_interpretation(context)
            elif phase == DataMashPhase.SEMANTIC_MAPPING:
                result = await self._execute_semantic_mapping(context)
            elif phase == DataMashPhase.REGISTERED:
                result = await self._execute_registration(context)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown phase: {phase}"
                }
            
            # Update step status
            step.status = "completed" if result.get("success", False) else "failed"
            step.outputs = result
            step.completed_at = self.clock.now_utc()
            if not result.get("success", False):
                step.error = result.get("error", "Phase execution failed")
            
            # Update current phase
            if result.get("success", False):
                self.current_phase = phase
            else:
                self.current_phase = DataMashPhase.FAILED
            
            self.logger.info(f"Data Mash phase {phase.value} completed: {result.get('success', False)}")
            return result
        
        except Exception as e:
            self.logger.error(f"❌ Data Mash phase {phase.value} failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Phase execution failed: {str(e)}"
            }
    
    async def _execute_data_quality(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Data Quality phase.
        
        Args:
            context: Execution context with content_refs, options, etc.
        
        Returns:
            Data quality analysis result
        """
        try:
            content_refs = context.get("content_refs", [])
            options = context.get("options", {})
            execution_context = context.get("execution_context", {})
            
            # Call Data Mash Orchestrator's data quality service
            if not self.orchestrator or not self.orchestrator.data_quality_service:
                return {
                    "success": False,
                    "error": "Data Quality Service not available"
                }
            
            # TODO: Load parsed artifacts from content_refs
            # For now, placeholder
            parsed_artifacts = []
            
            quality_report = await self.orchestrator.data_quality_service.analyze_quality(
                parsed_artifacts=parsed_artifacts,
                options=options
            )
            
            return {
                "success": True,
                "phase": "data_quality",
                "quality_report": quality_report.to_dict() if hasattr(quality_report, 'to_dict') else quality_report
            }
        
        except Exception as e:
            self.logger.error(f"Data Quality phase failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Data Quality phase failed: {str(e)}"
            }
    
    async def _execute_semantic_interpretation(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Semantic Interpretation phase.
        
        Args:
            context: Execution context with quality_report, deterministic_candidates, etc.
        
        Returns:
            Semantic interpretation result
        """
        try:
            quality_report = context.get("quality_report")
            deterministic_candidates = context.get("deterministic_candidates", [])
            options = context.get("options", {})
            domain_context = options.get("target_domain", "general")
            
            if not self.orchestrator or not self.orchestrator.semantic_interpretation_service:
                return {
                    "success": False,
                    "error": "Semantic Interpretation Service not available"
                }
            
            interpretation_result = await self.orchestrator.semantic_interpretation_service.interpret_semantics(
                deterministic_candidates=deterministic_candidates,
                data_quality_report=quality_report,
                domain_context=domain_context
            )
            
            return {
                "success": True,
                "phase": "semantic_interpretation",
                "interpretation": interpretation_result.to_dict() if hasattr(interpretation_result, 'to_dict') else interpretation_result
            }
        
        except Exception as e:
            self.logger.error(f"Semantic Interpretation phase failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Semantic Interpretation phase failed: {str(e)}"
            }
    
    async def _execute_semantic_mapping(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Semantic Mapping phase.
        
        Args:
            context: Execution context with interpretations, etc.
        
        Returns:
            Canonical model result
        """
        try:
            interpretations = context.get("interpretations", [])
            options = context.get("options", {})
            target_domain = options.get("target_domain", "general")
            
            if not self.orchestrator or not self.orchestrator.semantic_mapping_service:
                return {
                    "success": False,
                    "error": "Semantic Mapping Service not available"
                }
            
            canonical_model = await self.orchestrator.semantic_mapping_service.create_canonical_model(
                interpretations=interpretations,
                target_domain=target_domain
            )
            
            return {
                "success": True,
                "phase": "semantic_mapping",
                "canonical_model": canonical_model.to_dict() if hasattr(canonical_model, 'to_dict') else canonical_model
            }
        
        except Exception as e:
            self.logger.error(f"Semantic Mapping phase failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Semantic Mapping phase failed: {str(e)}"
            }
    
    async def _execute_registration(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Registration phase.
        
        Args:
            context: Execution context with canonical_model, etc.
        
        Returns:
            Registration result
        """
        try:
            canonical_model = context.get("canonical_model")
            mash_id = self.saga_id
            
            # Registration is handled by Data Mash Orchestrator
            # This phase just confirms registration is complete
            
            return {
                "success": True,
                "phase": "registered",
                "mash_id": mash_id,
                "canonical_model": canonical_model
            }
        
        except Exception as e:
            self.logger.error(f"Registration phase failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Registration phase failed: {str(e)}"
            }
    
    def get_current_phase(self) -> DataMashPhase:
        """Get current phase."""
        return self.current_phase
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "saga_id": self.saga_id,
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "current_phase": self.current_phase.value,
            "saga": self.saga.to_dict()
        }
