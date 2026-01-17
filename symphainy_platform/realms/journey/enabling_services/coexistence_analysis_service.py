"""
Coexistence Analysis Service - Pure Data Processing for Coexistence Analysis

Enabling service for coexistence analysis operations.

WHAT (Enabling Service Role): I execute coexistence analysis
HOW (Enabling Service Implementation): I use Public Works abstractions for analysis

Key Principle: Pure data processing - no LLM, no business logic, no orchestration.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from utilities import get_logger, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext


class CoexistenceAnalysisService:
    """
    Coexistence Analysis Service - Pure data processing for coexistence analysis.
    
    Uses Public Works abstractions to analyze coexistence opportunities.
    Returns raw data only - no business logic.
    """
    
    def __init__(self, public_works: Optional[Any] = None, visual_generation_service: Optional[Any] = None):
        """
        Initialize Coexistence Analysis Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
            visual_generation_service: Visual Generation Service for creating workflow charts
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        self.visual_generation_service = visual_generation_service
        self.clock = get_clock()
    
    async def analyze_coexistence(
        self,
        workflow_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Analyze coexistence opportunities.
        
        Args:
            workflow_id: Workflow identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with coexistence analysis results
        """
        self.logger.info(f"Analyzing coexistence: {workflow_id} for tenant: {tenant_id}")
        
        # For MVP: Return placeholder
        # In full implementation: Analyze workflow for coexistence opportunities
        
        return {
            "workflow_id": workflow_id,
            "analysis_status": "completed",
            "coexistence_opportunities": [],
            "recommendations": []
        }
    
    async def create_blueprint(
        self,
        workflow_id: str,
        tenant_id: str,
        context: ExecutionContext,
        current_state_workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive coexistence blueprint with visual workflow charts and responsibility matrix.
        
        Args:
            workflow_id: Workflow identifier (coexistence state workflow)
            tenant_id: Tenant identifier
            context: Execution context
            current_state_workflow_id: Optional identifier for current state workflow (if different)
        
        Returns:
            Dict with comprehensive blueprint including:
            - Current state workflow chart
            - Coexistence state workflow chart
            - Transition roadmap
            - Responsibility matrix
        """
        self.logger.info(f"Creating blueprint: {workflow_id} for tenant: {tenant_id}")
        
        blueprint_id = f"blueprint_{workflow_id}_{self.clock.now_iso().replace(':', '-')}"
        
        # 1. Retrieve coexistence analysis results
        coexistence_analysis = await self._get_coexistence_analysis(workflow_id, tenant_id, context)
        
        # 2. Retrieve current state workflow (use workflow_id if no separate current_state_workflow_id)
        current_workflow_id = current_state_workflow_id or workflow_id
        current_state_workflow = await self._get_workflow_definition(current_workflow_id, tenant_id, context)
        
        # 3. Generate current state workflow chart
        current_state_chart = await self._generate_workflow_chart(
            current_state_workflow,
            f"{blueprint_id}_current_state",
            tenant_id,
            context
        )
        
        # 4. Design coexistence state workflow (enhance current with Symphainy)
        coexistence_state_workflow = await self._design_coexistence_workflow(
            current_state_workflow,
            coexistence_analysis,
            workflow_id
        )
        
        # 5. Generate coexistence state workflow chart
        coexistence_state_chart = await self._generate_workflow_chart(
            coexistence_state_workflow,
            f"{blueprint_id}_coexistence_state",
            tenant_id,
            context
        )
        
        # 6. Create transition roadmap
        roadmap = await self._create_transition_roadmap(
            coexistence_analysis,
            current_state_workflow,
            coexistence_state_workflow
        )
        
        # 7. Generate responsibility matrix
        responsibility_matrix = await self._generate_responsibility_matrix(
            coexistence_state_workflow,
            coexistence_analysis
        )
        
        # 8. Synthesize into comprehensive blueprint
        blueprint = {
            "blueprint_id": blueprint_id,
            "workflow_id": workflow_id,
            "current_state": {
                "description": current_state_workflow.get("description", "Existing process workflow"),
                "workflow_chart": current_state_chart,
                "workflow_definition": current_state_workflow
            },
            "coexistence_state": {
                "description": coexistence_state_workflow.get("description", "Recommended process with Symphainy integration"),
                "workflow_chart": coexistence_state_chart,
                "workflow_definition": coexistence_state_workflow
            },
            "roadmap": roadmap,
            "responsibility_matrix": responsibility_matrix,
            "sections": await self._generate_blueprint_sections(
                coexistence_analysis,
                current_state_workflow,
                coexistence_state_workflow,
                roadmap,
                responsibility_matrix
            ),
            "metadata": {
                "created_date": self.clock.now_iso(),
                "version": "1.0",
                "tenant_id": tenant_id
            }
        }
        
        return blueprint
    
    async def _get_coexistence_analysis(
        self,
        workflow_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Retrieve coexistence analysis results from execution state."""
        # Try to get from recent execution state
        execution_state = await context.state_surface.get_execution_state(
            f"coexistence_analysis_{workflow_id}",
            tenant_id
        )
        
        if execution_state and execution_state.get("artifacts", {}).get("coexistence_analysis"):
            return execution_state["artifacts"]["coexistence_analysis"]
        
        # Fallback: Return basic structure if analysis not found
        self.logger.warning(f"Coexistence analysis not found for {workflow_id}, using default structure")
        return {
            "workflow_id": workflow_id,
            "existing_processes": [],
            "integration_points": [],
            "conflicts": [],
            "dependencies": []
        }
    
    async def _get_workflow_definition(
        self,
        workflow_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Retrieve workflow definition from execution state."""
        # Try to get workflow from execution state
        execution_state = await context.state_surface.get_execution_state(
            f"workflow_{workflow_id}",
            tenant_id
        )
        
        if execution_state and execution_state.get("artifacts", {}).get("workflow"):
            return execution_state["artifacts"]["workflow"]
        
        # Fallback: Return basic workflow structure
        self.logger.warning(f"Workflow definition not found for {workflow_id}, using default structure")
        return {
            "workflow_id": workflow_id,
            "description": "Workflow process",
            "steps": [
                {"step": 1, "name": "Step 1", "actor": "human", "description": "Manual step"}
            ],
            "decision_points": 0,
            "actors": ["human"]
        }
    
    async def _generate_workflow_chart(
        self,
        workflow_definition: Dict[str, Any],
        chart_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate workflow chart using VisualGenerationService."""
        if not self.visual_generation_service:
            self.logger.warning("VisualGenerationService not available, returning placeholder")
            return {
                "image_base64": None,
                "storage_path": f"blueprints/{chart_id}.png"
            }
        
        try:
            result = await self.visual_generation_service.generate_workflow_visual(
                workflow_data=workflow_definition,
                tenant_id=tenant_id,
                context=context
            )
            
            if result.get("success"):
                return {
                    "image_base64": result.get("image_base64"),
                    "storage_path": result.get("storage_path")
                }
            else:
                self.logger.warning(f"Failed to generate workflow chart: {result.get('error')}")
                return {
                    "image_base64": None,
                    "storage_path": f"blueprints/{chart_id}.png"
                }
        except Exception as e:
            self.logger.error(f"Error generating workflow chart: {e}", exc_info=True)
            return {
                "image_base64": None,
                "storage_path": f"blueprints/{chart_id}.png"
            }
    
    async def _design_coexistence_workflow(
        self,
        current_workflow: Dict[str, Any],
        coexistence_analysis: Dict[str, Any],
        workflow_id: str
    ) -> Dict[str, Any]:
        """Design coexistence state workflow by enhancing current workflow with Symphainy."""
        current_steps = current_workflow.get("steps", [])
        coexistence_steps = []
        
        # Enhance each step with Symphainy capabilities
        for step in current_steps:
            step_name = step.get("name", "")
            step_actor = step.get("actor", "human")
            
            # If it's a manual data processing step, add Symphainy automation
            if "data" in step_name.lower() or "process" in step_name.lower():
                # Add Symphainy ingestion/parsing step before manual step
                coexistence_steps.append({
                    "step": len(coexistence_steps) + 1,
                    "name": f"Automated {step_name}",
                    "actor": "symphainy",
                    "description": f"Automated processing using Symphainy: {step.get('description', '')}"
                })
                # Keep manual step for exceptions
                coexistence_steps.append({
                    "step": len(coexistence_steps) + 1,
                    "name": f"{step_name} (Exceptions)",
                    "actor": "human",
                    "description": f"Manual review of exceptions: {step.get('description', '')}"
                })
            else:
                # Keep non-data steps as-is
                coexistence_steps.append({
                    **step,
                    "step": len(coexistence_steps) + 1
                })
        
        # Add integration points from coexistence analysis
        integration_points = coexistence_analysis.get("integration_points", [])
        external_systems = set()
        for point in integration_points:
            if point.get("type") == "external_system":
                external_systems.add(point.get("system_name", "External System"))
        
        actors = list(set(["human", "symphainy"] + current_workflow.get("actors", [])))
        if external_systems:
            actors.extend(list(external_systems))
        
        return {
            "workflow_id": workflow_id,
            "description": f"Enhanced workflow with Symphainy integration for {current_workflow.get('description', 'process')}",
            "steps": coexistence_steps,
            "decision_points": current_workflow.get("decision_points", 0) + len(integration_points),
            "actors": actors,
            "integration_points": integration_points
        }
    
    async def _create_transition_roadmap(
        self,
        coexistence_analysis: Dict[str, Any],
        current_workflow: Dict[str, Any],
        coexistence_workflow: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create phased transition roadmap from current to coexistence state."""
        start_date = datetime.utcnow() + timedelta(days=7)  # Start in 1 week
        
        phases = [
            {
                "phase": 1,
                "name": "Foundation Setup",
                "duration": "2 weeks",
                "objectives": [
                    "Set up Symphainy integration points",
                    "Configure data sync",
                    "Test file ingestion pipeline"
                ],
                "dependencies": [],
                "risks": ["Integration complexity"],
                "success_criteria": [
                    "Integration points operational",
                    "Data sync validated"
                ]
            },
            {
                "phase": 2,
                "name": "Parallel Operation",
                "duration": "4 weeks",
                "objectives": [
                    "Run both processes in parallel",
                    "Validate coexistence",
                    "Compare results"
                ],
                "dependencies": ["Phase 1"],
                "risks": ["Data inconsistency"],
                "success_criteria": [
                    "100% parallel execution",
                    "Results match"
                ]
            },
            {
                "phase": 3,
                "name": "Full Migration",
                "duration": "2 weeks",
                "objectives": [
                    "Switch to coexistence state",
                    "Decommission old process",
                    "Monitor performance"
                ],
                "dependencies": ["Phase 2"],
                "risks": ["Downtime"],
                "success_criteria": [
                    "Zero downtime migration",
                    "Performance maintained"
                ]
            }
        ]
        
        total_duration_weeks = sum([2, 4, 2])  # Sum of phase durations
        end_date = start_date + timedelta(weeks=total_duration_weeks)
        
        return {
            "description": "Phased transition from current to coexistence state",
            "phases": phases,
            "timeline": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_duration": f"{total_duration_weeks} weeks"
            }
        }
    
    async def _generate_responsibility_matrix(
        self,
        coexistence_workflow: Dict[str, Any],
        coexistence_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate responsibility matrix for coexistence state workflow."""
        responsibilities = []
        steps = coexistence_workflow.get("steps", [])
        integration_points = coexistence_analysis.get("integration_points", [])
        
        # Map integration points to external systems
        external_systems_map = {}
        for point in integration_points:
            step_name = point.get("point", "")
            system_name = point.get("system_name", "External System")
            if step_name not in external_systems_map:
                external_systems_map[step_name] = []
            external_systems_map[step_name].append(system_name)
        
        for step in steps:
            step_name = step.get("name", "")
            actor = step.get("actor", "")
            description = step.get("description", "")
            
            # Determine responsibilities based on actor
            human_responsibilities = []
            ai_symphainy_responsibilities = []
            external_systems = external_systems_map.get(step_name, [])
            
            if actor == "human":
                human_responsibilities = [
                    "Review and approve",
                    "Handle exceptions",
                    "Make decisions"
                ]
            elif actor == "symphainy":
                if "ingest" in step_name.lower() or "parse" in step_name.lower():
                    ai_symphainy_responsibilities = [
                        "Parse files (PDF, Excel, binary)",
                        "Extract structured data",
                        "Assess data quality"
                    ]
                elif "validate" in step_name.lower() or "quality" in step_name.lower():
                    ai_symphainy_responsibilities = [
                        "Validate data quality",
                        "Check business rules",
                        "Flag anomalies"
                    ]
                else:
                    ai_symphainy_responsibilities = [
                        "Automated processing",
                        "Generate insights",
                        "Optimize workflow"
                    ]
            
            # Add external system responsibilities if applicable
            external_system_responsibilities = []
            if external_systems:
                for system in external_systems:
                    if "billing" in system.lower():
                        external_system_responsibilities.append(f"{system} (retrieve account data)")
                    elif "crm" in system.lower():
                        external_system_responsibilities.append(f"{system} (generate and send communications)")
                    else:
                        external_system_responsibilities.append(f"{system} (process data)")
            
            responsibilities.append({
                "step": step_name,
                "human": human_responsibilities if human_responsibilities else [],
                "ai_symphainy": ai_symphainy_responsibilities if ai_symphainy_responsibilities else [],
                "external_systems": external_system_responsibilities
            })
        
        return {
            "description": "Clear delineation of responsibilities in coexistence state",
            "note": "Platform systems (storage, state management, etc.) are a black box and not listed here",
            "responsibilities": responsibilities
        }
    
    async def _generate_blueprint_sections(
        self,
        coexistence_analysis: Dict[str, Any],
        current_workflow: Dict[str, Any],
        coexistence_workflow: Dict[str, Any],
        roadmap: Dict[str, Any],
        responsibility_matrix: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate structured blueprint sections."""
        return [
            {
                "section": "Executive Summary",
                "content": f"This blueprint outlines the coexistence strategy for integrating Symphainy into the existing workflow process. The current state involves {len(current_workflow.get('steps', []))} steps, while the coexistence state enhances this with {len(coexistence_workflow.get('steps', []))} steps including automated processing."
            },
            {
                "section": "Current State Analysis",
                "content": f"Current process: {current_workflow.get('description', 'Existing workflow')}. The workflow includes {current_workflow.get('decision_points', 0)} decision points and involves {', '.join(current_workflow.get('actors', []))}."
            },
            {
                "section": "Coexistence State Design",
                "content": f"Recommended process: {coexistence_workflow.get('description', 'Enhanced workflow with Symphainy')}. This includes automated processing steps and integration with {len(coexistence_analysis.get('integration_points', []))} external systems."
            },
            {
                "section": "Transition Roadmap",
                "content": f"Phased approach over {roadmap['timeline']['total_duration']} with {len(roadmap['phases'])} phases: {', '.join([p['name'] for p in roadmap['phases']])}."
            },
            {
                "section": "Responsibility Matrix",
                "content": f"Clear delineation of responsibilities across {len(responsibility_matrix['responsibilities'])} workflow steps, with human, AI/Symphainy, and external system responsibilities clearly defined."
            },
            {
                "section": "Integration Requirements",
                "content": "Technical integration points and requirements",
                "integration_points": coexistence_analysis.get("integration_points", []),
                "resource_requirements": [
                    "Symphainy platform access",
                    "External system API access",
                    "Database connection pool"
                ]
            },
            {
                "section": "Risk Mitigation",
                "content": "Identified risks and mitigation strategies",
                "risks": coexistence_analysis.get("conflicts", []),
                "mitigations": [
                    "Automated testing in Phase 2",
                    "Rollback procedures",
                    "Monitoring and alerting"
                ]
            }
        ]
