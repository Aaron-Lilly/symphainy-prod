"""
Optimize Process Intent Service

Implements the optimize_process intent for the Operations Realm.

Contract: docs/intent_contracts/journey_coexistence_analysis/intent_optimize_process.md

Purpose: Optimize workflow processes by identifying friction points and generating
optimization recommendations.

WHAT (Intent Service Role): I optimize workflow processes
HOW (Intent Service Implementation): I analyze workflows for friction points
    and generate optimization recommendations

Naming Convention:
- Realm: Operations Realm
- Artifacts: operations_optimization
- Solution = platform construct (OperationsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class OptimizeProcessService(BaseIntentService):
    """
    Intent service for process optimization.
    
    Analyzes workflows for:
    - Friction points
    - Bottlenecks
    - Redundant steps
    - Optimization opportunities
    
    Generates optimization recommendations with expected impact.
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize OptimizeProcessService."""
        super().__init__(
            service_id="optimize_process_service",
            intent_type="optimize_process",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the optimize_process intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            workflow_id = intent_params.get("workflow_id")
            if not workflow_id:
                raise ValueError("workflow_id is required for process optimization")
            
            optimization_focus = intent_params.get("optimization_focus", "general")
            
            # Get workflow data
            workflow_data = await self._get_workflow_data(workflow_id, context)
            
            # Identify friction points
            friction_points = await self._identify_friction_points(workflow_data)
            
            # Identify bottlenecks
            bottlenecks = await self._identify_bottlenecks(workflow_data)
            
            # Generate optimization recommendations
            recommendations = await self._generate_recommendations(
                friction_points, bottlenecks, optimization_focus
            )
            
            # Calculate expected impact
            expected_impact = self._calculate_expected_impact(recommendations)
            
            # Build optimization result
            optimization_id = f"optimization_{generate_event_id()}"
            
            optimization = {
                "optimization_id": optimization_id,
                "workflow_id": workflow_id,
                "friction_points": friction_points,
                "bottlenecks": bottlenecks,
                "recommendations": recommendations,
                "expected_impact": expected_impact,
                "optimization_focus": optimization_focus,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Artifact Plane
            artifact_id = await self._store_optimization(optimization, context)
            
            self.logger.info(f"Process optimized: {optimization_id} ({len(recommendations)} recommendations)")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "optimization_id": optimization_id,
                    "recommendations_count": len(recommendations)
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "optimization": optimization,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "process_optimized",
                        "optimization_id": optimization_id,
                        "workflow_id": workflow_id
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _get_workflow_data(self, workflow_id: str, context: ExecutionContext) -> Dict[str, Any]:
        """Get workflow data from artifact plane or state surface."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    workflow = await artifact_plane.get_artifact(
                        artifact_id=workflow_id,
                        tenant_id=context.tenant_id
                    )
                    if workflow:
                        return workflow.get("content", workflow)
            except Exception:
                pass
        
        if context.state_surface:
            try:
                workflow = await context.state_surface.get_execution_state(
                    key=f"workflow_{workflow_id}",
                    tenant_id=context.tenant_id
                )
                if workflow:
                    return workflow
            except Exception:
                pass
        
        # Return placeholder workflow structure
        return {
            "workflow_id": workflow_id,
            "steps": [
                {"step_id": "1", "name": "Step 1", "duration_minutes": 30},
                {"step_id": "2", "name": "Step 2", "duration_minutes": 45},
                {"step_id": "3", "name": "Step 3", "duration_minutes": 20}
            ],
            "transitions": []
        }
    
    async def _identify_friction_points(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify friction points in workflow."""
        friction_points = []
        steps = workflow_data.get("steps", [])
        
        for i, step in enumerate(steps):
            # Check for long duration steps
            duration = step.get("duration_minutes", 0)
            if duration > 60:
                friction_points.append({
                    "friction_id": f"friction_{i}",
                    "step_id": step.get("step_id"),
                    "step_name": step.get("name"),
                    "friction_type": "long_duration",
                    "description": f"Step takes {duration} minutes (>60 min threshold)",
                    "severity": "high" if duration > 120 else "medium"
                })
            
            # Check for manual steps (based on naming)
            step_name = step.get("name", "").lower()
            if any(word in step_name for word in ["manual", "review", "approve", "check"]):
                friction_points.append({
                    "friction_id": f"friction_manual_{i}",
                    "step_id": step.get("step_id"),
                    "step_name": step.get("name"),
                    "friction_type": "manual_intervention",
                    "description": "Manual intervention required",
                    "severity": "medium"
                })
        
        return friction_points
    
    async def _identify_bottlenecks(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify bottlenecks in workflow."""
        bottlenecks = []
        steps = workflow_data.get("steps", [])
        
        # Find steps with high resource requirements or dependencies
        for i, step in enumerate(steps):
            dependencies = step.get("dependencies", [])
            if len(dependencies) > 2:
                bottlenecks.append({
                    "bottleneck_id": f"bottleneck_{i}",
                    "step_id": step.get("step_id"),
                    "step_name": step.get("name"),
                    "bottleneck_type": "dependency_bottleneck",
                    "description": f"Step has {len(dependencies)} dependencies",
                    "impact": "high" if len(dependencies) > 4 else "medium"
                })
        
        return bottlenecks
    
    async def _generate_recommendations(
        self,
        friction_points: List[Dict[str, Any]],
        bottlenecks: List[Dict[str, Any]],
        focus: str
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Recommendations for friction points
        for fp in friction_points:
            if fp["friction_type"] == "long_duration":
                recommendations.append({
                    "recommendation_id": f"rec_{fp['friction_id']}",
                    "target": fp["step_name"],
                    "action": "Consider breaking down into smaller steps or automating",
                    "expected_improvement": "30-50% time reduction",
                    "priority": "high" if fp["severity"] == "high" else "medium"
                })
            elif fp["friction_type"] == "manual_intervention":
                recommendations.append({
                    "recommendation_id": f"rec_{fp['friction_id']}",
                    "target": fp["step_name"],
                    "action": "Evaluate automation opportunities or parallel processing",
                    "expected_improvement": "Reduced manual effort",
                    "priority": "medium"
                })
        
        # Recommendations for bottlenecks
        for bn in bottlenecks:
            recommendations.append({
                "recommendation_id": f"rec_{bn['bottleneck_id']}",
                "target": bn["step_name"],
                "action": "Reduce dependencies or enable parallel execution",
                "expected_improvement": "Improved throughput",
                "priority": "high" if bn["impact"] == "high" else "medium"
            })
        
        return recommendations
    
    def _calculate_expected_impact(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate expected impact of recommendations."""
        high_priority = len([r for r in recommendations if r.get("priority") == "high"])
        medium_priority = len([r for r in recommendations if r.get("priority") == "medium"])
        
        return {
            "total_recommendations": len(recommendations),
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "estimated_improvement": "20-40% process efficiency gain" if high_priority > 0 else "10-20% improvement",
            "implementation_effort": "high" if high_priority > 3 else "medium" if high_priority > 0 else "low"
        }
    
    async def _store_optimization(self, optimization: Dict[str, Any], context: ExecutionContext) -> Optional[str]:
        """Store optimization in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="optimization_report",
                        content=optimization,
                        metadata={"workflow_id": optimization.get("workflow_id")},
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store optimization: {e}")
        return None
