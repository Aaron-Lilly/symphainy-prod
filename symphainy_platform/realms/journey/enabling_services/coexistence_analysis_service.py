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
        Analyze coexistence opportunities (human+AI optimization).
        
        ARCHITECTURAL PRINCIPLE: Analyzes workflow structure to identify coexistence opportunities.
        
        Args:
            workflow_id: Workflow identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with coexistence analysis results
        """
        self.logger.info(f"Analyzing coexistence: {workflow_id} for tenant: {tenant_id}")
        
        try:
            # Get workflow data
            workflow_data = context.metadata.get(f"workflow_{workflow_id}", {})
            workflow_content = workflow_data.get("workflow_content", {})
            tasks = workflow_data.get("tasks", []) or workflow_content.get("tasks", [])
            
            coexistence_opportunities = []
            integration_points = []
            conflicts = []
            dependencies = []
            recommendations = []
            
            # Analyze each task for coexistence opportunities
            for task in tasks:
                task_name = task.get("name", "")
                task_type = task.get("type", "unknown")
                task_actor = task.get("actor", "human")
                
                # Identify friction removal opportunities (AI assistance to remove repetitive tasks)
                if any(keyword in task_name.lower() for keyword in ["data", "extract", "parse", "validate", "transform", "analyze", "process"]):
                    coexistence_opportunities.append({
                        "task_id": task.get("id"),
                        "task_name": task_name,
                        "opportunity_type": "friction_removal",
                        "description": f"Task '{task_name}' has friction that can be removed with AI assistance, freeing humans for high-value work",
                        "current_actor": task_actor,
                        "recommended_actor": "symphainy",
                        "friction_type": "repetitive_data_processing",
                        "human_value_freed": "decision_making_strategic_analysis",
                        "effort": "medium"
                    })
                    
                    # Add integration point
                    integration_points.append({
                        "point": task_name,
                        "type": "symphainy_assistance",
                        "system_name": "Symphainy Platform",
                        "description": f"AI assistance for {task_name} to remove friction and enable human focus on high-value work"
                    })
                    
                    recommendations.append({
                        "type": "friction_removal",
                        "priority": "high",
                        "description": f"Remove friction from '{task_name}' with AI assistance, enabling humans to focus on decision-making and strategic analysis",
                        "impact": "high",
                        "effort": "medium",
                        "human_benefit": "Frees time for high-value human work"
                    })
                
                # Identify human focus areas (high-value work that requires human judgment)
                elif any(keyword in task_name.lower() for keyword in ["approve", "review", "decide", "judge", "evaluate", "sign"]):
                    coexistence_opportunities.append({
                        "task_id": task.get("id"),
                        "task_name": task_name,
                        "opportunity_type": "human_focus",
                        "description": f"Task '{task_name}' is high-value work requiring human judgment and decision-making",
                        "current_actor": task_actor,
                        "recommended_actor": "human",
                        "value_type": "strategic_decision_making",
                        "effort": "low"
                    })
                    
                    recommendations.append({
                        "type": "human_focus",
                        "priority": "high",
                        "description": f"Maintain human focus on '{task_name}' - this is high-value work requiring judgment and strategic thinking",
                        "impact": "high",
                        "effort": "low",
                        "human_benefit": "Core human value - decision-making and judgment"
                    })
                
                # Identify hybrid opportunities (AI removes friction, human provides oversight)
                elif any(keyword in task_name.lower() for keyword in ["verify", "check", "validate", "confirm"]):
                    coexistence_opportunities.append({
                        "task_id": task.get("id"),
                        "task_name": task_name,
                        "opportunity_type": "hybrid",
                        "description": f"Task '{task_name}' can use AI to remove friction from initial processing, with human oversight for final verification and quality assurance",
                        "current_actor": task_actor,
                        "recommended_actor": "hybrid",
                        "friction_removed": "repetitive_verification_work",
                        "human_value": "quality_assurance_oversight",
                        "effort": "medium"
                    })
                    
                    integration_points.append({
                        "point": task_name,
                        "type": "hybrid_processing",
                        "system_name": "Symphainy + Human",
                        "description": f"AI removes friction from {task_name}, human provides oversight and quality assurance"
                    })
                    
                    recommendations.append({
                        "type": "hybrid",
                        "priority": "medium",
                        "description": f"Implement hybrid approach for '{task_name}': AI removes friction from processing, human provides oversight and final verification",
                        "impact": "medium",
                        "effort": "medium",
                        "human_benefit": "Focuses human time on quality assurance rather than repetitive checking"
                    })
            
            # Identify dependencies between tasks
            for i, task1 in enumerate(tasks):
                for j, task2 in enumerate(tasks[i+1:], i+1):
                    # Simple dependency detection (in production would use workflow structure)
                    if task1.get("id") and task2.get("id"):
                        dependencies.append({
                            "from_task": task1.get("id"),
                            "to_task": task2.get("id"),
                            "dependency_type": "sequential",
                            "description": f"{task1.get('name')} must complete before {task2.get('name')}"
                        })
            
            # Identify potential friction points and dependencies
            # Friction points occur when removing friction from one task might affect dependent tasks
            for opp in coexistence_opportunities:
                if opp.get("opportunity_type") == "friction_removal":
                    # Check if removing friction from this task might affect human-dependent tasks
                    task_id = opp.get("task_id")
                    dependent_tasks = [d for d in dependencies if d.get("to_task") == task_id]
                    if dependent_tasks:
                        conflicts.append({
                            "type": "friction_removal_dependency",
                            "description": f"Removing friction from '{opp.get('task_name')}' may affect dependent tasks that require human input",
                            "affected_tasks": [d.get("from_task") for d in dependent_tasks],
                            "severity": "medium",
                            "mitigation": "Ensure dependent tasks can handle AI-assisted input while maintaining human oversight where needed"
                        })
            
            return {
                "workflow_id": workflow_id,
                "analysis_status": "completed",
                "coexistence_opportunities": coexistence_opportunities,
                "integration_points": integration_points,
                "conflicts": conflicts,
                "dependencies": dependencies,
                "recommendations": recommendations,
                "opportunities_count": len(coexistence_opportunities),
                "friction_points": [o for o in coexistence_opportunities if o.get("opportunity_type") == "friction_removal"],
                "human_focus_areas": [o for o in coexistence_opportunities if o.get("opportunity_type") == "human_focus"],
                "friction_removal_potential": len([o for o in coexistence_opportunities if o.get("opportunity_type") == "friction_removal"]) / len(tasks) if tasks else 0.0,
                "human_tasks_count": len([o for o in coexistence_opportunities if o.get("opportunity_type") == "human_focus"]),
                "ai_assisted_tasks_count": len([o for o in coexistence_opportunities if o.get("opportunity_type") == "friction_removal"]),
                "hybrid_tasks_count": len([o for o in coexistence_opportunities if o.get("opportunity_type") == "hybrid"])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze coexistence: {e}", exc_info=True)
            return {
                "workflow_id": workflow_id,
                "analysis_status": "error",
                "coexistence_opportunities": [],
                "recommendations": [],
                "error": str(e)
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
            
            # If it's a manual data processing step, add AI assistance to remove friction
            if "data" in step_name.lower() or "process" in step_name.lower():
                # Add AI-assisted step to remove friction from repetitive processing
                coexistence_steps.append({
                    "step": len(coexistence_steps) + 1,
                    "name": f"AI-Assisted {step_name}",
                    "actor": "symphainy",
                    "description": f"AI removes friction from repetitive processing, enabling human focus on exceptions and high-value work: {step.get('description', '')}"
                })
                # Keep human step for exceptions and oversight
                coexistence_steps.append({
                    "step": len(coexistence_steps) + 1,
                    "name": f"{step_name} (Human Oversight)",
                    "actor": "human",
                    "description": f"Human oversight for exceptions and quality assurance: {step.get('description', '')}"
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
            "description": f"Optimized workflow with AI assistance to remove friction, enabling human focus on high-value work: {current_workflow.get('description', 'process')}",
            "steps": coexistence_steps,
            "decision_points": current_workflow.get("decision_points", 0) + len(integration_points),
            "actors": actors,
            "integration_points": integration_points,
            "friction_removed": len([s for s in coexistence_steps if s.get("actor") == "symphainy"]),
            "human_focus_areas": len([s for s in coexistence_steps if s.get("actor") == "human"])
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
                    "Review and approve (high-value decision-making)",
                    "Handle exceptions (strategic problem-solving)",
                    "Make decisions (judgment and analysis)",
                    "Quality assurance oversight"
                ]
            elif actor == "symphainy":
                if "ingest" in step_name.lower() or "parse" in step_name.lower():
                    ai_symphainy_responsibilities = [
                        "Remove friction from file parsing (PDF, Excel, binary)",
                        "Extract structured data (repetitive processing)",
                        "Assess data quality (initial screening)"
                    ]
                elif "validate" in step_name.lower() or "quality" in step_name.lower():
                    ai_symphainy_responsibilities = [
                        "Remove friction from validation (initial checks)",
                        "Check business rules (automated verification)",
                        "Flag anomalies (for human review)"
                    ]
                else:
                    ai_symphainy_responsibilities = [
                        "Remove friction from repetitive processing",
                        "Generate insights (data analysis)",
                        "Optimize workflow (identify improvements)"
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
            "description": "Clear delineation of responsibilities in optimized state - AI removes friction, humans focus on high-value work",
            "note": "Platform systems (storage, state management, etc.) are a black box and not listed here. This matrix emphasizes human-positive coexistence: AI handles repetitive tasks, humans focus on decision-making and strategic work.",
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
                "content": f"This blueprint outlines a human-positive coexistence strategy that uses AI to remove friction from repetitive tasks, enabling humans to focus on high-value work. The current state involves {len(current_workflow.get('steps', []))} steps, while the optimized state includes {len(coexistence_workflow.get('steps', []))} steps with AI assistance removing friction from {coexistence_workflow.get('friction_removed', 0)} tasks, freeing humans to focus on {coexistence_workflow.get('human_focus_areas', 0)} high-value areas."
            },
            {
                "section": "Current State Analysis",
                "content": f"Current process: {current_workflow.get('description', 'Existing workflow')}. The workflow includes {current_workflow.get('decision_points', 0)} decision points and involves {', '.join(current_workflow.get('actors', []))}. This analysis identifies friction points where repetitive tasks can be assisted by AI, freeing human time for strategic work."
            },
            {
                "section": "Coexistence State Design",
                "content": f"Optimized process: {coexistence_workflow.get('description', 'Workflow with AI friction removal')}. This design uses AI to remove friction from repetitive tasks, enabling humans to focus on decision-making, strategic analysis, and quality assurance. Integration with {len(coexistence_analysis.get('integration_points', []))} external systems supports seamless coexistence."
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
