"""
Semantic Interpretation Service

Expert reasoning for semantic interpretation using two-hop approach.

WHAT (Insights Realm): I interpret semantic meaning
HOW (Service): I use GroundedReasoningAgentBase for expert reasoning
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from utilities import get_logger, get_clock


@dataclass
class SemanticInterpretationResult:
    """Semantic Interpretation Result."""
    field: str
    final_label: str
    justification: List[str]
    confidence: float
    candidates: List[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "field": self.field,
            "final_label": self.final_label,
            "justification": self.justification,
            "confidence": self.confidence,
            "candidates": self.candidates or []
        }


class SemanticInterpretationService:
    """
    Semantic Interpretation Service - Expert Reasoning.
    
    Interprets semantics using two-hop approach:
    - Phase 3A: Get deterministic candidates from Content Realm
    - Phase 3B: Use agent for expert reasoning
    """
    
    def __init__(
        self,
        agent_foundation: Optional[Any] = None,
        content_realm: Optional[Any] = None
    ):
        """
        Initialize Semantic Interpretation Service.
        
        Args:
            agent_foundation: Agent Foundation Service (for agents)
            content_realm: Content Realm (for deterministic labeling)
        """
        self.agent_foundation = agent_foundation
        self.content_realm = content_realm
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.logger.info("✅ Semantic Interpretation Service initialized")
    
    async def interpret_semantics(
        self,
        deterministic_candidates: List[Dict[str, Any]],
        data_quality_report: Any,
        domain_context: str
    ) -> SemanticInterpretationResult:
        """
        Interpret semantics using two-hop approach.
        
        Args:
            deterministic_candidates: Deterministic label candidates from Content Realm
            data_quality_report: Data Quality Report
            domain_context: Domain context (e.g., "insurance")
        
        Returns:
            SemanticInterpretationResult with final interpretation
        """
        try:
            # Phase 3A: Get deterministic candidates (if not provided)
            if not deterministic_candidates and self.content_realm:
                # TODO: Call Content Realm for deterministic labeling
                deterministic_candidates = []
            
            # Phase 3B: Expert reasoning (if agent available)
            if self.agent_foundation:
                try:
                    agent = self.agent_foundation.get_agent("semantic_interpreter_agent")
                    if agent:
                        # Use agent for expert reasoning
                        interpretation = await agent.reason(
                            context={
                                "candidates": deterministic_candidates,
                                "quality_report": data_quality_report.to_dict() if hasattr(data_quality_report, 'to_dict') else data_quality_report,
                                "domain": domain_context
                            }
                        )
                        # TODO: Parse agent response into SemanticInterpretationResult
                        return SemanticInterpretationResult(
                            field="field1",
                            final_label="Policy Number",
                            justification=["Field entropy aligns with policy numbering patterns"],
                            confidence=0.93,
                            candidates=deterministic_candidates
                        )
                except Exception as e:
                    self.logger.warning(f"Agent reasoning failed, using deterministic: {e}")
            
            # Fallback: Use deterministic candidates
            if deterministic_candidates:
                best_candidate = max(deterministic_candidates, key=lambda x: x.get("confidence", 0))
                return SemanticInterpretationResult(
                    field=best_candidate.get("field", "unknown"),
                    final_label=best_candidate.get("label", "unknown"),
                    justification=["Deterministic labeling"],
                    confidence=best_candidate.get("confidence", 0.0),
                    candidates=deterministic_candidates
                )
            
            # No candidates available
            return SemanticInterpretationResult(
                field="unknown",
                final_label="unknown",
                justification=["No candidates available"],
                confidence=0.0,
                candidates=[]
            )
        
        except Exception as e:
            self.logger.error(f"❌ Semantic interpretation failed: {e}", exc_info=True)
            return SemanticInterpretationResult(
                field="unknown",
                final_label="unknown",
                justification=[f"Interpretation failed: {str(e)}"],
                confidence=0.0,
                candidates=[]
            )
