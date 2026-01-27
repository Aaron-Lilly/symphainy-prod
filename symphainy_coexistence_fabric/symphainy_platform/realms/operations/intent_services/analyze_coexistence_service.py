"""
Analyze Coexistence Intent Service

Implements the analyze_coexistence intent for the Operations Realm.

Contract: docs/intent_contracts/journey_coexistence_analysis/intent_analyze_coexistence.md

Purpose: Analyze workflow and SOP for coexistence opportunities. Identifies
where current processes and target processes can coexist during transformation.

WHAT (Intent Service Role): I analyze coexistence opportunities
HOW (Intent Service Implementation): I compare workflows and SOPs to identify
    coexistence patterns, opportunities, and transformation paths

Naming Convention:
- Realm: Operations Realm
- Artifacts: operations_coexistence_analysis
- Solution = platform construct (OperationsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class AnalyzeCoexistenceService(BaseIntentService):
    """
    Intent service for coexistence analysis.
    
    Analyzes coexistence between:
    - Current state workflow
    - Target state workflow/SOP
    
    Identifies:
    - Coexistence opportunities
    - Transformation paths
    - Risk areas
    - Integration points
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize AnalyzeCoexistenceService."""
        super().__init__(
            service_id="analyze_coexistence_service",
            intent_type="analyze_coexistence",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the analyze_coexistence intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            workflow_id = intent_params.get("workflow_id")
            sop_id = intent_params.get("sop_id")
            
            if not workflow_id and not sop_id:
                raise ValueError("At least one of workflow_id or sop_id is required")
            
            # Get workflow and SOP data
            workflow_data = await self._get_workflow_data(workflow_id, context) if workflow_id else None
            sop_data = await self._get_sop_data(sop_id, context) if sop_id else None
            
            # Analyze coexistence opportunities
            opportunities = await self._identify_opportunities(workflow_data, sop_data)
            
            # Identify transformation paths
            transformation_paths = await self._identify_transformation_paths(workflow_data, sop_data)
            
            # Assess risks
            risks = await self._assess_risks(workflow_data, sop_data, opportunities)
            
            # Identify integration points
            integration_points = await self._identify_integration_points(workflow_data, sop_data)
            
            # Generate coexistence recommendation
            recommendation = self._generate_recommendation(opportunities, risks)
            
            # Build analysis result
            analysis_id = f"coexistence_{generate_event_id()}"
            
            analysis = {
                "analysis_id": analysis_id,
                "workflow_id": workflow_id,
                "sop_id": sop_id,
                "opportunities": opportunities,
                "transformation_paths": transformation_paths,
                "risks": risks,
                "integration_points": integration_points,
                "recommendation": recommendation,
                "coexistence_score": self._calculate_coexistence_score(opportunities, risks),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Artifact Plane
            artifact_id = await self._store_analysis(analysis, context)
            
            self.logger.info(f"Coexistence analyzed: {analysis_id} ({len(opportunities)} opportunities)")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "analysis_id": analysis_id,
                    "opportunities_count": len(opportunities)
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "coexistence_analysis": analysis,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "coexistence_analyzed",
                        "analysis_id": analysis_id,
                        "coexistence_score": analysis["coexistence_score"]
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
        """Get workflow data."""
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
        
        return {"workflow_id": workflow_id, "steps": [], "name": f"Workflow {workflow_id}"}
    
    async def _get_sop_data(self, sop_id: str, context: ExecutionContext) -> Dict[str, Any]:
        """Get SOP data."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    sop = await artifact_plane.get_artifact(
                        artifact_id=sop_id,
                        tenant_id=context.tenant_id
                    )
                    if sop:
                        return sop.get("content", sop)
            except Exception:
                pass
        
        return {"sop_id": sop_id, "procedure_steps": [], "title": f"SOP {sop_id}"}
    
    async def _identify_opportunities(
        self,
        workflow_data: Optional[Dict[str, Any]],
        sop_data: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify coexistence opportunities."""
        opportunities = []
        
        workflow_steps = workflow_data.get("steps", []) if workflow_data else []
        sop_steps = sop_data.get("procedure_steps", []) if sop_data else []
        
        # Identify parallel execution opportunities
        if workflow_steps and sop_steps:
            opportunities.append({
                "opportunity_id": "parallel_1",
                "type": "parallel_execution",
                "description": "Steps can run in parallel during transition",
                "impact": "high",
                "effort": "medium"
            })
        
        # Identify phased rollout opportunities
        if len(workflow_steps) > 2 or len(sop_steps) > 2:
            opportunities.append({
                "opportunity_id": "phased_1",
                "type": "phased_rollout",
                "description": "Process can be transitioned in phases",
                "impact": "medium",
                "effort": "low"
            })
        
        # Identify data synchronization opportunities
        opportunities.append({
            "opportunity_id": "sync_1",
            "type": "data_synchronization",
            "description": "Data can be synchronized between systems during coexistence",
            "impact": "high",
            "effort": "high"
        })
        
        return opportunities
    
    async def _identify_transformation_paths(
        self,
        workflow_data: Optional[Dict[str, Any]],
        sop_data: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify transformation paths."""
        paths = []
        
        # Direct migration path
        paths.append({
            "path_id": "direct",
            "name": "Direct Migration",
            "description": "Direct cutover from current to target state",
            "duration_estimate": "2-4 weeks",
            "risk_level": "high",
            "recommended": False
        })
        
        # Parallel run path
        paths.append({
            "path_id": "parallel",
            "name": "Parallel Run",
            "description": "Run both systems in parallel during transition",
            "duration_estimate": "4-8 weeks",
            "risk_level": "medium",
            "recommended": True
        })
        
        # Phased migration path
        paths.append({
            "path_id": "phased",
            "name": "Phased Migration",
            "description": "Migrate in phases by process area",
            "duration_estimate": "8-12 weeks",
            "risk_level": "low",
            "recommended": True
        })
        
        return paths
    
    async def _assess_risks(
        self,
        workflow_data: Optional[Dict[str, Any]],
        sop_data: Optional[Dict[str, Any]],
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Assess coexistence risks."""
        risks = []
        
        # Data consistency risk
        risks.append({
            "risk_id": "data_consistency",
            "category": "data",
            "description": "Risk of data inconsistency during coexistence",
            "severity": "high",
            "mitigation": "Implement data synchronization and validation"
        })
        
        # Process confusion risk
        risks.append({
            "risk_id": "process_confusion",
            "category": "operational",
            "description": "Users may be confused about which process to follow",
            "severity": "medium",
            "mitigation": "Clear documentation and training"
        })
        
        # Integration failure risk
        risks.append({
            "risk_id": "integration_failure",
            "category": "technical",
            "description": "Risk of integration failures between systems",
            "severity": "medium",
            "mitigation": "Robust testing and fallback procedures"
        })
        
        return risks
    
    async def _identify_integration_points(
        self,
        workflow_data: Optional[Dict[str, Any]],
        sop_data: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify integration points between systems."""
        integration_points = []
        
        integration_points.append({
            "point_id": "entry",
            "name": "Process Entry Point",
            "description": "Where requests enter the process",
            "integration_type": "api",
            "priority": "high"
        })
        
        integration_points.append({
            "point_id": "data_exchange",
            "name": "Data Exchange Point",
            "description": "Where data is exchanged between systems",
            "integration_type": "event",
            "priority": "high"
        })
        
        integration_points.append({
            "point_id": "exit",
            "name": "Process Exit Point",
            "description": "Where process completes and results are returned",
            "integration_type": "api",
            "priority": "medium"
        })
        
        return integration_points
    
    def _generate_recommendation(
        self,
        opportunities: List[Dict[str, Any]],
        risks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate coexistence recommendation."""
        high_impact_opportunities = len([o for o in opportunities if o.get("impact") == "high"])
        high_severity_risks = len([r for r in risks if r.get("severity") == "high"])
        
        if high_severity_risks > high_impact_opportunities:
            approach = "conservative"
            strategy = "Phased migration with extensive parallel run"
        else:
            approach = "balanced"
            strategy = "Parallel run with phased cutover"
        
        return {
            "approach": approach,
            "strategy": strategy,
            "key_actions": [
                "Establish data synchronization mechanism",
                "Create clear process documentation",
                "Define rollback procedures",
                "Train users on both processes"
            ],
            "success_criteria": [
                "Zero data loss during transition",
                "< 5% increase in process errors",
                "User satisfaction > 80%"
            ]
        }
    
    def _calculate_coexistence_score(
        self,
        opportunities: List[Dict[str, Any]],
        risks: List[Dict[str, Any]]
    ) -> float:
        """Calculate coexistence viability score (0-100)."""
        opportunity_score = len([o for o in opportunities if o.get("impact") in ["high", "medium"]]) * 15
        risk_penalty = len([r for r in risks if r.get("severity") == "high"]) * 10
        
        score = min(100, max(0, 50 + opportunity_score - risk_penalty))
        return round(score, 1)
    
    async def _store_analysis(self, analysis: Dict[str, Any], context: ExecutionContext) -> Optional[str]:
        """Store analysis in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="coexistence_analysis",
                        content=analysis,
                        metadata={
                            "workflow_id": analysis.get("workflow_id"),
                            "sop_id": analysis.get("sop_id")
                        },
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store analysis: {e}")
        return None
