"""
Coexistence Analysis Service

Deterministic service for analyzing human-AI coexistence opportunities.
Uses State Surface for state storage.
Stores blueprints in GCS with references in State Surface.

WHAT (Journey Realm): I analyze coexistence opportunities
HOW (Service): I provide deterministic analysis algorithms
"""

import json
import uuid
from typing import Dict, Any, Optional

from utilities import get_logger, get_clock

logger = get_logger(__name__)


class CoexistenceAnalysisService:
    """
    Coexistence Analysis Service.
    
    Provides deterministic coexistence analysis capabilities:
    - Analyze workflows/SOPs for coexistence opportunities
    - Generate coexistence blueprints
    - Optimize coexistence patterns
    
    Pattern:
    - Deterministic analysis algorithms
    - Stateless (uses State Surface for state)
    - Input → Output
    - No orchestration
    - No reasoning (agents provide reasoning, service executes)
    """
    
    def __init__(
        self,
        state_surface: Any,
        file_storage_abstraction: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize Coexistence Analysis Service.
        
        Args:
            state_surface: State Surface instance for state storage
            file_storage_abstraction: File Storage Abstraction for artifact storage
            platform_gateway: Platform Gateway for accessing abstractions
        """
        self.state_surface = state_surface
        self.file_storage = file_storage_abstraction
        self.platform_gateway = platform_gateway
        self.logger = logger
        self.clock = get_clock()
        
        # Coexistence patterns
        self.coexistence_patterns = {
            "collaborative": {
                "description": "AI and humans work together on shared tasks",
                "characteristics": ["shared_decision_making", "complementary_skills", "mutual_learning"]
            },
            "delegated": {
                "description": "AI handles specific tasks while humans oversee",
                "characteristics": ["task_automation", "human_oversight", "clear_boundaries"]
            },
            "augmented": {
                "description": "AI enhances human capabilities without replacing them",
                "characteristics": ["capability_enhancement", "human_centric", "seamless_integration"]
            },
            "autonomous": {
                "description": "AI operates independently with minimal human intervention",
                "characteristics": ["independent_operation", "self_monitoring", "human_override"]
            }
        }
        
        self.logger.info("✅ Coexistence Analysis Service initialized")
    
    async def analyze_coexistence(
        self,
        current_state: Dict[str, Any],
        target_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze coexistence opportunities.
        
        Args:
            current_state: Current state (workflow/SOP content)
            target_state: Optional target state for comparison
        
        Returns:
            Dict with analysis results (for agent to use for reasoning)
        """
        try:
            self.logger.info("Analyzing coexistence opportunities")
            
            # Extract process steps from current state
            process_steps = self._extract_process_steps(current_state)
            
            # Identify coexistence opportunities (deterministic algorithm)
            opportunities = []
            for i, step in enumerate(process_steps):
                opportunity = {
                    "step_id": f"step_{i+1}",
                    "step_description": step.get("description", ""),
                    "coexistence_pattern": self._identify_pattern(step),
                    "ai_capability": self._identify_ai_capability(step),
                    "human_role": self._identify_human_role(step),
                    "optimization_potential": self._calculate_optimization_potential(step)
                }
                opportunities.append(opportunity)
            
            # Generate analysis result
            analysis_result = {
                "analysis_id": str(uuid.uuid4()),
                "current_state_summary": {
                    "total_steps": len(process_steps),
                    "process_type": current_state.get("type", "unknown")
                },
                "opportunities": opportunities,
                "recommended_patterns": self._recommend_patterns(opportunities),
                "created_at": self.clock.now_iso()
            }
            
            if target_state:
                analysis_result["target_state_summary"] = {
                    "total_steps": len(self._extract_process_steps(target_state)),
                    "process_type": target_state.get("type", "unknown")
                }
            
            self.logger.info(f"✅ Coexistence analysis complete: {len(opportunities)} opportunities identified")
            
            return {
                "success": True,
                "analysis_result": analysis_result
            }
        
        except Exception as e:
            self.logger.error(f"Failed to analyze coexistence: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_blueprint(
        self,
        analysis_result: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate coexistence blueprint from analysis.
        
        Args:
            analysis_result: Analysis result from analyze_coexistence()
            options: Optional blueprint generation options
        
        Returns:
            Dict with blueprint_structure (for orchestrator to store)
        """
        try:
            self.logger.info("Generating coexistence blueprint")
            
            # Extract opportunities from analysis
            opportunities = analysis_result.get("opportunities", [])
            recommended_patterns = analysis_result.get("recommended_patterns", [])
            
            # Generate blueprint structure (deterministic algorithm)
            blueprint_structure = {
                "blueprint_id": str(uuid.uuid4()),
                "blueprint_name": f"Coexistence Blueprint - {self.clock.now_iso()}",
                "analysis_id": analysis_result.get("analysis_id"),
                "recommended_patterns": recommended_patterns,
                "implementation_plan": self._generate_implementation_plan(opportunities, recommended_patterns),
                "optimization_metrics": self._calculate_optimization_metrics(opportunities),
                "created_at": self.clock.now_iso()
            }
            
            self.logger.info("✅ Coexistence blueprint generated")
            
            return {
                "success": True,
                "blueprint_structure": blueprint_structure
            }
        
        except Exception as e:
            self.logger.error(f"Failed to generate blueprint: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def optimize_coexistence(
        self,
        blueprint_reference: str,
        session_id: str,
        tenant_id: str,
        optimization_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize coexistence blueprint.
        
        Args:
            blueprint_reference: State Surface reference to blueprint
            session_id: Session identifier
            tenant_id: Tenant identifier
            optimization_criteria: Optimization criteria (efficiency, cost, quality, etc.)
        
        Returns:
            Dict with optimized blueprint structure
        """
        try:
            self.logger.info(f"Optimizing coexistence blueprint: {blueprint_reference}")
            
            # Get blueprint from State Surface (reference) → retrieve from GCS
            blueprint_metadata = await self.state_surface.get_file_metadata(blueprint_reference)
            
            if not blueprint_metadata:
                return {
                    "success": False,
                    "error": "Blueprint reference not found"
                }
            
            storage_location = blueprint_metadata.get("storage_location")
            if not storage_location:
                return {
                    "success": False,
                    "error": "Blueprint storage location not found"
                }
            
            # Retrieve blueprint artifact
            blueprint_data_bytes = await self.file_storage.download_file(storage_location)
            if not blueprint_data_bytes:
                return {
                    "success": False,
                    "error": "Failed to retrieve blueprint artifact"
                }
            
            blueprint_content = json.loads(blueprint_data_bytes.decode('utf-8'))
            
            # Optimize blueprint (deterministic algorithm)
            optimized_blueprint = self._optimize_blueprint_algorithm(blueprint_content, optimization_criteria)
            
            self.logger.info("✅ Blueprint optimized")
            
            return {
                "success": True,
                "optimized_blueprint": optimized_blueprint
            }
        
        except Exception as e:
            self.logger.error(f"Failed to optimize blueprint: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_process_steps(self, state: Dict[str, Any]) -> list:
        """Extract process steps from state (workflow or SOP)."""
        steps = []
        
        # Try workflow format
        if "nodes" in state:
            for node in state.get("nodes", []):
                if node.get("node_type") == "task":
                    steps.append({
                        "description": node.get("label", ""),
                        "node_id": node.get("node_id")
                    })
        
        # Try SOP format
        elif "sections" in state:
            procedures = state.get("sections", {}).get("procedures", [])
            for procedure in procedures:
                if isinstance(procedure, dict):
                    steps.append({
                        "description": procedure.get("description", ""),
                        "step": procedure.get("step")
                    })
                elif isinstance(procedure, str):
                    steps.append({"description": procedure})
        
        return steps
    
    def _identify_pattern(self, step: Dict[str, Any]) -> str:
        """Identify coexistence pattern for a step (deterministic algorithm)."""
        description = step.get("description", "").lower()
        
        # Simple pattern identification based on keywords
        if any(keyword in description for keyword in ["automate", "automatic", "system"]):
            return "autonomous"
        elif any(keyword in description for keyword in ["assist", "help", "support"]):
            return "augmented"
        elif any(keyword in description for keyword in ["delegate", "assign", "handoff"]):
            return "delegated"
        else:
            return "collaborative"
    
    def _identify_ai_capability(self, step: Dict[str, Any]) -> str:
        """Identify AI capability for a step (deterministic algorithm)."""
        description = step.get("description", "").lower()
        
        # Simple capability identification
        if any(keyword in description for keyword in ["analyze", "process", "extract"]):
            return "data_processing"
        elif any(keyword in description for keyword in ["generate", "create", "write"]):
            return "content_generation"
        elif any(keyword in description for keyword in ["validate", "check", "verify"]):
            return "validation"
        else:
            return "general_assistance"
    
    def _identify_human_role(self, step: Dict[str, Any]) -> str:
        """Identify human role for a step (deterministic algorithm)."""
        description = step.get("description", "").lower()
        
        # Simple role identification
        if any(keyword in description for keyword in ["review", "approve", "decide"]):
            return "decision_maker"
        elif any(keyword in description for keyword in ["execute", "perform", "complete"]):
            return "executor"
        else:
            return "collaborator"
    
    def _calculate_optimization_potential(self, step: Dict[str, Any]) -> float:
        """Calculate optimization potential for a step (0-1 scale)."""
        # Simple scoring algorithm
        description = step.get("description", "").lower()
        
        score = 0.5  # Base score
        
        # Increase score for automation keywords
        if any(keyword in description for keyword in ["manual", "repetitive", "routine"]):
            score += 0.3
        
        # Increase score for data processing keywords
        if any(keyword in description for keyword in ["data", "process", "analyze"]):
            score += 0.2
        
        return min(1.0, score)
    
    def _recommend_patterns(self, opportunities: list) -> list:
        """Recommend coexistence patterns based on opportunities."""
        pattern_counts = {}
        for opp in opportunities:
            pattern = opp.get("coexistence_pattern", "collaborative")
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Sort by count
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [pattern for pattern, count in sorted_patterns[:3]]  # Top 3 patterns
    
    def _generate_implementation_plan(
        self,
        opportunities: list,
        recommended_patterns: list
    ) -> Dict[str, Any]:
        """Generate implementation plan (deterministic algorithm)."""
        phases = []
        
        for i, pattern in enumerate(recommended_patterns):
            phase = {
                "phase_id": f"phase_{i+1}",
                "pattern": pattern,
                "steps": [opp for opp in opportunities if opp.get("coexistence_pattern") == pattern],
                "estimated_effort": len([opp for opp in opportunities if opp.get("coexistence_pattern") == pattern]) * 2
            }
            phases.append(phase)
        
        return {
            "phases": phases,
            "total_phases": len(phases),
            "estimated_total_effort": sum(phase["estimated_effort"] for phase in phases)
        }
    
    def _calculate_optimization_metrics(self, opportunities: list) -> Dict[str, Any]:
        """Calculate optimization metrics (deterministic algorithm)."""
        total_opportunities = len(opportunities)
        avg_optimization_potential = sum(opp.get("optimization_potential", 0) for opp in opportunities) / total_opportunities if total_opportunities > 0 else 0
        
        return {
            "total_opportunities": total_opportunities,
            "average_optimization_potential": avg_optimization_potential,
            "estimated_efficiency_gain": avg_optimization_potential * 0.3,  # 30% of potential
            "estimated_cost_reduction": avg_optimization_potential * 0.2   # 20% of potential
        }
    
    def _optimize_blueprint_algorithm(
        self,
        blueprint: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize blueprint based on criteria (deterministic algorithm)."""
        optimized = blueprint.copy()
        
        # Apply optimization based on criteria
        if criteria.get("prioritize_efficiency"):
            # Reorder phases by efficiency potential
            phases = optimized.get("implementation_plan", {}).get("phases", [])
            phases.sort(key=lambda p: sum(step.get("optimization_potential", 0) for step in p.get("steps", [])), reverse=True)
            optimized["implementation_plan"]["phases"] = phases
        
        if criteria.get("prioritize_cost_reduction"):
            # Adjust effort estimates
            for phase in optimized.get("implementation_plan", {}).get("phases", []):
                phase["estimated_effort"] = int(phase["estimated_effort"] * 0.9)  # 10% reduction
        
        optimized["optimized_at"] = self.clock.now_iso()
        optimized["optimization_criteria"] = criteria
        
        return optimized
