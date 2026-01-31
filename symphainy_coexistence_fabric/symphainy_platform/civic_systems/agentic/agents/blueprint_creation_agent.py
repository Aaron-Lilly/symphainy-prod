"""
Blueprint Creation Agent - AI-Powered Coexistence Blueprint Design

Reasons about workflow transformation and designs intelligent coexistence blueprints
with human-positive responsibility matrices using multi-step LLM reasoning.

WHAT (Agent Role): I design coexistence blueprints with friction removal focus
HOW (Agent Implementation): I use LLM reasoning to analyze workflows, design intelligent
    phases, and create compelling blueprints with visual-ready output

Key Principle: Agentic forward pattern - agent reasons about specific context,
    designs phases intelligently, creates presentation-ready blueprints.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional
from utilities import get_logger
from ..agent_base import AgentBase
from ..models.agent_runtime_context import AgentRuntimeContext
from symphainy_platform.runtime.execution_context import ExecutionContext


class BlueprintCreationAgent(AgentBase):
    """
    Blueprint Creation Agent - AI-Powered Coexistence Blueprint Design.
    
    Uses multi-step LLM reasoning to:
    1. Analyze workflow context and friction points
    2. Design intelligent transformation phases
    3. Create human-positive responsibility matrices
    4. Generate presentation-ready blueprints
    
    ARCHITECTURAL PRINCIPLE: Agent reasons about specific context,
    not template-driven output.
    """
    
    def __init__(
        self,
        agent_id: str = "blueprint_creation_agent",
        capabilities: Optional[List[str]] = None,
        collaboration_router=None,
        public_works=None,
        **kwargs
    ):
        """Initialize Blueprint Creation Agent."""
        if capabilities is None:
            capabilities = [
                "blueprint_design",
                "workflow_transformation_reasoning",
                "phase_design",
                "responsibility_matrix_creation",
                "llm_reasoning"
            ]
        
        super().__init__(
            agent_id=agent_id,
            agent_type="specialized",
            capabilities=capabilities,
            collaboration_router=collaboration_router,
            public_works=public_works,
            **kwargs
        )
        self.public_works = public_works
        self.logger = get_logger(self.__class__.__name__)
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext,
        runtime_context: Optional[AgentRuntimeContext] = None
    ) -> Dict[str, Any]:
        """
        Process blueprint creation request with full LLM reasoning.
        
        Pattern:
        1. Gather workflow and coexistence context
        2. Reason about transformation strategy (LLM)
        3. Design intelligent phases (LLM)
        4. Create responsibility matrix (LLM)
        5. Generate presentation-ready blueprint
        """
        self.logger.info("Creating blueprint with AI-powered reasoning")
        
        workflow_id = request.get("workflow_id")
        coexistence_analysis_id = request.get("coexistence_analysis_id")
        blueprint_options = request.get("blueprint_options", {})
        
        # Step 1: Gather context
        workflow_data = {}
        if workflow_id:
            workflow_data = await self.use_tool(
                "operations_get_workflow",
                {"workflow_id": workflow_id},
                context
            ) or {}
        
        coexistence_data = {}
        if coexistence_analysis_id:
            coexistence_data = await self.use_tool(
                "operations_get_coexistence_analysis",
                {"analysis_id": coexistence_analysis_id},
                context
            ) or {}
        elif workflow_id:
            coexistence_data = await self.use_tool(
                "operations_analyze_coexistence",
                {"workflow_id": workflow_id},
                context
            ) or {}
        
        # Get platform context for richer blueprints
        platform_context = await self._gather_platform_context(context)
        
        # Step 2: Reason about transformation strategy (LLM)
        transformation_strategy = await self._reason_about_transformation(
            workflow_data=workflow_data,
            coexistence_data=coexistence_data,
            platform_context=platform_context,
            context=context
        )
        
        # Step 3: Design intelligent phases (LLM)
        phases = await self._design_intelligent_phases(
            workflow_data=workflow_data,
            coexistence_data=coexistence_data,
            transformation_strategy=transformation_strategy,
            context=context
        )
        
        # Step 4: Create responsibility matrix (LLM)
        responsibility_matrix = await self._create_intelligent_responsibility_matrix(
            phases=phases,
            coexistence_data=coexistence_data,
            transformation_strategy=transformation_strategy,
            context=context
        )
        
        # Step 5: Generate presentation-ready blueprint
        blueprint = await self._generate_presentation_blueprint(
            workflow_data=workflow_data,
            coexistence_data=coexistence_data,
            phases=phases,
            responsibility_matrix=responsibility_matrix,
            transformation_strategy=transformation_strategy,
            options=blueprint_options,
            context=context
        )
        
        self.logger.info(f"✅ Blueprint created with {len(phases)} phases")
        
        return {
            "artifact_type": "blueprint",
            "artifact": blueprint,
            "confidence": transformation_strategy.get("confidence", 0.85),
            "reasoning": transformation_strategy.get("reasoning", "")
        }
    
    async def _gather_platform_context(self, context: ExecutionContext) -> Dict[str, Any]:
        """Gather platform context for richer blueprints."""
        platform_context = {}
        
        if context.state_surface:
            try:
                session_state = await context.state_surface.get_session_state(
                    context.session_id,
                    context.tenant_id
                )
                platform_context = {
                    "content_summary": session_state.get("content_pillar_summary", {}),
                    "insights_summary": session_state.get("insights_pillar_summary", {}),
                    "journey_summary": session_state.get("journey_pillar_summary", {}),
                    "files_processed": session_state.get("content_pillar_summary", {}).get("files_uploaded", 0),
                    "quality_score": session_state.get("insights_pillar_summary", {}).get("overall_quality", 0)
                }
            except Exception as e:
                self.logger.debug(f"Could not get platform context: {e}")
        
        return platform_context
    
    async def _reason_about_transformation(
        self,
        workflow_data: Dict[str, Any],
        coexistence_data: Dict[str, Any],
        platform_context: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Reason about transformation strategy using LLM.
        
        Analyzes the specific workflow and friction points to determine
        the best transformation approach.
        """
        friction_points = coexistence_data.get("friction_points", [])
        human_focus_areas = coexistence_data.get("human_focus_areas", [])
        recommendations = coexistence_data.get("recommendations", [])
        
        system_message = """You are the Blueprint Creation Agent, an expert in designing 
human-AI coexistence transformations. Your role is to analyze workflow friction and 
design intelligent transformation strategies.

KEY PRINCIPLES:
- AI removes friction, humans focus on high-value work
- Never suggest replacing humans - design for augmentation
- Phases should be logical, sequential, and achievable
- Each phase should deliver measurable value
- Human oversight and decision-making authority is preserved

Analyze the workflow context and design a transformation strategy that:
1. Prioritizes the most impactful friction points
2. Sequences changes for minimal disruption
3. Maximizes human value preservation
4. Creates clear success criteria for each phase"""

        workflow_summary = {
            "workflow_id": workflow_data.get("workflow_id", "unknown"),
            "description": workflow_data.get("description", ""),
            "steps": len(workflow_data.get("steps", [])),
            "tasks": len(workflow_data.get("tasks", []))
        }
        
        user_message = f"""Analyze this workflow and design a transformation strategy:

WORKFLOW CONTEXT:
{json.dumps(workflow_summary, indent=2)}

FRICTION POINTS IDENTIFIED ({len(friction_points)}):
{json.dumps(friction_points[:5], indent=2)}

HUMAN FOCUS AREAS ({len(human_focus_areas)}):
{json.dumps(human_focus_areas[:5], indent=2)}

PLATFORM CONTEXT:
- Files processed: {platform_context.get('files_processed', 0)}
- Quality score: {platform_context.get('quality_score', 'N/A')}

Design a transformation strategy that includes:
1. Overall approach (incremental vs comprehensive)
2. Priority order for addressing friction points
3. Risk assessment for the transformation
4. Success metrics for the blueprint
5. Recommended number of phases (typically 3-5)

Return your analysis as a strategic recommendation."""

        try:
            reasoning_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=2000,
                temperature=0.3,
                context=context
            )
            
            # Determine recommended phases based on friction points
            recommended_phases = min(max(len(friction_points), 3), 5)
            
            return {
                "reasoning": reasoning_text,
                "approach": "incremental" if len(friction_points) > 3 else "comprehensive",
                "recommended_phases": recommended_phases,
                "priority_friction": friction_points[:recommended_phases] if friction_points else [],
                "confidence": 0.85 if friction_points else 0.70,
                "risk_level": "medium" if len(friction_points) > 5 else "low"
            }
            
        except Exception as e:
            self.logger.warning(f"LLM transformation reasoning failed: {e}")
            return {
                "reasoning": "Transformation strategy based on friction analysis",
                "approach": "incremental",
                "recommended_phases": 3,
                "priority_friction": friction_points[:3] if friction_points else [],
                "confidence": 0.70,
                "risk_level": "medium"
            }
    
    async def _design_intelligent_phases(
        self,
        workflow_data: Dict[str, Any],
        coexistence_data: Dict[str, Any],
        transformation_strategy: Dict[str, Any],
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """
        Design intelligent transformation phases using LLM.
        
        Creates phases that are specific to the workflow context,
        not generic templates.
        """
        friction_points = transformation_strategy.get("priority_friction", [])
        num_phases = transformation_strategy.get("recommended_phases", 3)
        approach = transformation_strategy.get("approach", "incremental")
        
        system_message = """You are the Blueprint Creation Agent designing transformation phases.

For each phase, design:
1. A compelling, specific name (not "Phase 1: Assessment")
2. Clear objectives tied to specific friction points
3. Concrete deliverables
4. Measurable success criteria
5. Human value preservation strategy
6. AI augmentation approach
7. Realistic duration estimate

IMPORTANT: Each phase should address specific friction points from the analysis.
Use human-positive language throughout (friction removal, augmentation, enablement)."""

        user_message = f"""Design {num_phases} transformation phases for this workflow:

TRANSFORMATION APPROACH: {approach}
FRICTION POINTS TO ADDRESS:
{json.dumps(friction_points, indent=2)}

WORKFLOW CONTEXT:
- Description: {workflow_data.get('description', 'Workflow optimization')}
- Current steps: {len(workflow_data.get('steps', []))}

Design {num_phases} phases that:
1. Each address specific friction points
2. Build on each other logically
3. Deliver value incrementally
4. Preserve human decision-making
5. Include clear milestones

Return as JSON array with this structure for each phase:
{{
  "phase_number": 1,
  "name": "Specific, compelling phase name",
  "objective": "What this phase achieves",
  "friction_addressed": ["specific friction 1", "specific friction 2"],
  "deliverables": ["deliverable 1", "deliverable 2"],
  "success_criteria": ["measurable criterion 1", "criterion 2"],
  "human_value": "What human value is preserved/enhanced",
  "ai_augmentation": "How AI assists in this phase",
  "duration_weeks": 4,
  "milestones": ["milestone 1", "milestone 2"]
}}"""

        try:
            response_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=3000,
                temperature=0.3,
                response_format={"type": "json_object"},
                context=context
            )
            
            # Parse phases from response
            phases = self._parse_phases_response(response_text, friction_points, num_phases)
            self.logger.info(f"✅ Designed {len(phases)} intelligent phases")
            return phases
            
        except Exception as e:
            self.logger.warning(f"LLM phase design failed: {e}")
            return self._create_fallback_phases(friction_points, num_phases)
    
    def _parse_phases_response(
        self,
        response_text: str,
        friction_points: List[Dict[str, Any]],
        num_phases: int
    ) -> List[Dict[str, Any]]:
        """Parse phases from LLM response."""
        try:
            if isinstance(response_text, str):
                result = json.loads(response_text)
            else:
                result = response_text
            
            # Handle both array and object with phases key
            if isinstance(result, list):
                phases = result
            elif isinstance(result, dict):
                phases = result.get("phases", [result])
            else:
                phases = []
            
            # Validate and enhance phases
            validated_phases = []
            for i, phase in enumerate(phases[:num_phases]):
                validated_phase = {
                    "phase_number": phase.get("phase_number", i + 1),
                    "name": phase.get("name", f"Phase {i + 1}"),
                    "objective": phase.get("objective", ""),
                    "friction_addressed": phase.get("friction_addressed", []),
                    "deliverables": phase.get("deliverables", []),
                    "success_criteria": phase.get("success_criteria", []),
                    "human_value": phase.get("human_value", "Domain expertise preserved"),
                    "ai_augmentation": phase.get("ai_augmentation", "Analysis support"),
                    "duration_weeks": phase.get("duration_weeks", 4),
                    "milestones": phase.get("milestones", []),
                    "status": "planned"
                }
                validated_phases.append(validated_phase)
            
            return validated_phases if validated_phases else self._create_fallback_phases(friction_points, num_phases)
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse phases: {e}")
            return self._create_fallback_phases(friction_points, num_phases)
    
    def _create_fallback_phases(
        self,
        friction_points: List[Dict[str, Any]],
        num_phases: int
    ) -> List[Dict[str, Any]]:
        """Create fallback phases when LLM fails."""
        phases = []
        
        # Create phases based on friction points
        for i in range(num_phases):
            friction = friction_points[i] if i < len(friction_points) else {}
            
            phase = {
                "phase_number": i + 1,
                "name": f"Phase {i + 1}: {friction.get('task_name', 'Optimization')}",
                "objective": f"Address {friction.get('friction_type', 'friction')} to enable human focus",
                "friction_addressed": [friction.get("description", "")] if friction else [],
                "deliverables": [
                    f"Friction removal implementation",
                    f"Human workflow enhancement",
                    f"Validation and feedback"
                ],
                "success_criteria": [
                    "Friction point resolved",
                    "Human efficiency improved",
                    "Stakeholder approval"
                ],
                "human_value": friction.get("human_value_freed", "Decision-making authority"),
                "ai_augmentation": "Analysis and automation support",
                "duration_weeks": 4,
                "milestones": ["Design", "Implementation", "Validation"],
                "status": "planned"
            }
            phases.append(phase)
        
        return phases
    
    async def _create_intelligent_responsibility_matrix(
        self,
        phases: List[Dict[str, Any]],
        coexistence_data: Dict[str, Any],
        transformation_strategy: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Create intelligent responsibility matrix using LLM.
        
        Designs specific human and AI responsibilities for each phase
        based on the transformation context.
        """
        system_message = """You are designing a human-AI responsibility matrix for a coexistence blueprint.

KEY PRINCIPLES:
- Humans retain all decision-making authority
- AI provides recommendations, humans approve
- Clear collaboration points for each phase
- Governance ensures transparency and override capability

Design responsibilities that are:
1. Specific to the phase objectives
2. Human-positive (augmentation, not replacement)
3. Clear about collaboration points
4. Focused on preserving human expertise"""

        phases_summary = [
            {
                "name": p.get("name"),
                "objective": p.get("objective"),
                "human_value": p.get("human_value"),
                "ai_augmentation": p.get("ai_augmentation")
            }
            for p in phases
        ]

        user_message = f"""Design a responsibility matrix for these phases:

PHASES:
{json.dumps(phases_summary, indent=2)}

For each phase, specify:
1. Human responsibilities (strategic, decision-making, validation)
2. AI responsibilities (analysis, processing, recommendations)
3. Collaboration points (where human-AI interaction occurs)

Return as JSON with this structure:
{{
  "responsibilities": [
    {{
      "phase": "phase name",
      "human": ["responsibility 1", "responsibility 2"],
      "ai": ["responsibility 1", "responsibility 2"],
      "collaboration": ["point 1", "point 2"]
    }}
  ],
  "governance": {{
    "human_override": true,
    "ai_transparency": true,
    "feedback_loop": true,
    "escalation_path": "description"
  }}
}}"""

        try:
            response_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"},
                context=context
            )
            
            # Parse response
            if isinstance(response_text, str):
                result = json.loads(response_text)
            else:
                result = response_text
            
            return {
                "matrix_type": "human_positive",
                "focus": "augmentation_not_replacement",
                "responsibilities": result.get("responsibilities", []),
                "governance": result.get("governance", {
                    "human_override": True,
                    "ai_transparency": True,
                    "feedback_loop": True,
                    "escalation_path": "Human decision-makers retain final authority"
                }),
                "generated_by": "ai_reasoning"
            }
            
        except Exception as e:
            self.logger.warning(f"LLM responsibility matrix failed: {e}")
            return self._create_fallback_matrix(phases)
    
    def _create_fallback_matrix(self, phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create fallback responsibility matrix."""
        responsibilities = []
        
        for phase in phases:
            responsibilities.append({
                "phase": phase.get("name"),
                "human": [
                    "Strategic oversight and direction",
                    "Quality validation and approval",
                    "Stakeholder communication",
                    phase.get("human_value", "Domain expertise")
                ],
                "ai": [
                    "Data processing and analysis",
                    "Pattern recognition",
                    "Recommendation generation",
                    phase.get("ai_augmentation", "Analysis support")
                ],
                "collaboration": [
                    "Review AI recommendations",
                    "Approve automated actions",
                    "Provide feedback for improvement"
                ]
            })
        
        return {
            "matrix_type": "human_positive",
            "focus": "augmentation_not_replacement",
            "responsibilities": responsibilities,
            "governance": {
                "human_override": True,
                "ai_transparency": True,
                "feedback_loop": True,
                "escalation_path": "Human decision-makers retain final authority"
            },
            "generated_by": "fallback"
        }
    
    async def _generate_presentation_blueprint(
        self,
        workflow_data: Dict[str, Any],
        coexistence_data: Dict[str, Any],
        phases: List[Dict[str, Any]],
        responsibility_matrix: Dict[str, Any],
        transformation_strategy: Dict[str, Any],
        options: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate a presentation-ready blueprint with visual elements.
        """
        # Calculate total duration
        total_weeks = sum(p.get("duration_weeks", 4) for p in phases)
        
        # Generate executive summary using LLM
        executive_summary = await self._generate_executive_summary(
            workflow_data, phases, transformation_strategy, context
        )
        
        # Build presentation-ready blueprint
        blueprint = {
            "blueprint_id": f"blueprint_{context.execution_id}",
            "workflow_id": workflow_data.get("workflow_id"),
            "created_at": datetime.utcnow().isoformat(),
            
            # Executive Summary (for presentation)
            "executive_summary": executive_summary,
            
            # Header
            "title": options.get("title", "Human-AI Coexistence Blueprint"),
            "subtitle": f"Transformation plan for {workflow_data.get('description', 'workflow optimization')}",
            "description": options.get("description", transformation_strategy.get("reasoning", "")[:500]),
            
            # Overview metrics (visual-friendly)
            "overview": {
                "total_phases": len(phases),
                "total_duration_weeks": total_weeks,
                "total_duration_display": f"{total_weeks} weeks (~{total_weeks // 4} months)",
                "friction_points_addressed": len(coexistence_data.get("friction_points", [])),
                "human_tasks_preserved": coexistence_data.get("human_tasks_count", 0),
                "ai_augmented_tasks": coexistence_data.get("ai_assisted_tasks_count", 0),
                "approach": transformation_strategy.get("approach", "incremental"),
                "risk_level": transformation_strategy.get("risk_level", "medium"),
                "confidence_score": transformation_strategy.get("confidence", 0.85)
            },
            
            # Phases (detailed)
            "phases": phases,
            
            # Responsibility Matrix
            "responsibility_matrix": responsibility_matrix,
            
            # Visual elements for UI
            "visualization": {
                "timeline": self._generate_timeline_data(phases),
                "phase_progress": [
                    {"phase": p["name"], "status": p.get("status", "planned"), "progress": 0}
                    for p in phases
                ],
                "metrics_dashboard": {
                    "friction_removed": 0,
                    "human_hours_freed": 0,
                    "ai_tasks_automated": 0
                }
            },
            
            # Transformation strategy reasoning
            "transformation_strategy": {
                "approach": transformation_strategy.get("approach"),
                "reasoning": transformation_strategy.get("reasoning"),
                "confidence": transformation_strategy.get("confidence")
            },
            
            # Coexistence state
            "coexistence_state": {
                "friction_points_addressed": len(coexistence_data.get("friction_points", [])),
                "human_focus_areas": coexistence_data.get("human_focus_areas", []),
                "opportunities": coexistence_data.get("coexistence_opportunities", [])
            }
        }
        
        return blueprint
    
    async def _generate_executive_summary(
        self,
        workflow_data: Dict[str, Any],
        phases: List[Dict[str, Any]],
        transformation_strategy: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate executive summary using LLM."""
        try:
            system_message = """You are creating an executive summary for a coexistence blueprint.
Write a compelling, concise summary that:
1. Explains the transformation value in business terms
2. Highlights key benefits (friction removal, human enablement)
3. Provides clear next steps
Keep it to 2-3 paragraphs maximum."""

            user_message = f"""Create an executive summary for this blueprint:

WORKFLOW: {workflow_data.get('description', 'Workflow optimization')}
PHASES: {len(phases)} phases planned
APPROACH: {transformation_strategy.get('approach', 'incremental')}

Phase highlights:
{json.dumps([{'name': p['name'], 'objective': p['objective']} for p in phases[:3]], indent=2)}

Write a compelling executive summary (2-3 paragraphs)."""

            summary_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=500,
                temperature=0.4,
                context=context
            )
            
            return {
                "summary": summary_text,
                "key_benefits": [
                    "Removes friction from repetitive tasks",
                    "Enables human focus on high-value work",
                    "Preserves decision-making authority"
                ],
                "next_steps": [
                    "Review blueprint with stakeholders",
                    "Approve Phase 1 kickoff",
                    "Allocate resources for implementation"
                ]
            }
            
        except Exception as e:
            self.logger.warning(f"Executive summary generation failed: {e}")
            return {
                "summary": f"This blueprint outlines a {len(phases)}-phase transformation to optimize the workflow through human-AI coexistence.",
                "key_benefits": ["Friction removal", "Human enablement", "AI augmentation"],
                "next_steps": ["Review", "Approve", "Implement"]
            }
    
    def _generate_timeline_data(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate timeline data for visualization."""
        timeline = []
        current_week = 0
        
        for phase in phases:
            duration = phase.get("duration_weeks", 4)
            timeline.append({
                "phase": phase["name"],
                "phase_number": phase["phase_number"],
                "start_week": current_week,
                "end_week": current_week + duration,
                "duration_weeks": duration,
                "milestones": phase.get("milestones", [])
            })
            current_week += duration
        
        return timeline
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Blueprint Creation Agent - AI-powered coexistence blueprint design with intelligent phase planning"
