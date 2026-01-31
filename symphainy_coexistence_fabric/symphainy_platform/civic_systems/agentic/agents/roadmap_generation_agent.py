"""
Roadmap Generation Agent - AI-Powered Strategic Planning and Roadmap Design

Reasons about strategic planning using LLM and designs intelligent implementation
roadmaps with context-aware phases, milestones, and risk analysis.

WHAT (Agent Role): I design strategic roadmaps with intelligent phases and milestones
HOW (Agent Implementation): I use LLM reasoning to analyze goals, design phases,
    identify context-specific risks, and create presentation-ready roadmaps

Key Principle: Agentic forward pattern - agent reasons about specific goals and context,
    designs phases intelligently, creates compelling roadmaps with clear value narrative.
"""

import sys
from pathlib import Path
import json
from datetime import datetime, timedelta

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


class RoadmapGenerationAgent(AgentBase):
    """
    Roadmap Generation Agent - AI-Powered Strategic Roadmap Design.
    
    Uses multi-step LLM reasoning to:
    1. Analyze goals and platform context
    2. Design intelligent phases with dependencies
    3. Create meaningful milestones
    4. Identify context-specific risks
    5. Generate presentation-ready roadmaps
    
    ARCHITECTURAL PRINCIPLE: Agent reasons about specific context,
    not template-driven output.
    """
    
    def __init__(
        self,
        agent_id: str = "roadmap_generation_agent",
        capabilities: Optional[List[str]] = None,
        collaboration_router=None,
        public_works=None,
        **kwargs
    ):
        """Initialize Roadmap Generation Agent."""
        if capabilities is None:
            capabilities = [
                "roadmap_design",
                "strategic_planning",
                "phase_design",
                "milestone_planning",
                "risk_analysis",
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
        Process roadmap generation request with full LLM reasoning.
        
        Pattern:
        1. Gather platform context
        2. Reason about strategic approach (LLM)
        3. Design intelligent phases (LLM)
        4. Create meaningful milestones (LLM)
        5. Identify context-specific risks (LLM)
        6. Generate presentation-ready roadmap
        """
        self.logger.info("Generating roadmap with AI-powered strategic reasoning")
        
        goals = request.get("goals", [])
        timeline = request.get("timeline", "12 months")
        roadmap_options = request.get("roadmap_options", {})
        
        # Step 1: Gather platform context
        platform_context = await self._gather_platform_context(context)
        
        # Step 2: Reason about strategic approach (LLM)
        strategic_analysis = await self._reason_about_strategy(
            goals=goals,
            timeline=timeline,
            platform_context=platform_context,
            context=context
        )
        
        # Step 3: Design intelligent phases (LLM)
        phases = await self._design_intelligent_phases(
            goals=goals,
            timeline=timeline,
            strategic_analysis=strategic_analysis,
            platform_context=platform_context,
            context=context
        )
        
        # Step 4: Create meaningful milestones (LLM)
        milestones = await self._create_intelligent_milestones(
            phases=phases,
            goals=goals,
            context=context
        )
        
        # Step 5: Identify context-specific risks (LLM)
        risks = await self._identify_intelligent_risks(
            goals=goals,
            phases=phases,
            platform_context=platform_context,
            context=context
        )
        
        # Step 6: Generate presentation-ready roadmap
        roadmap = await self._generate_presentation_roadmap(
            goals=goals,
            timeline=timeline,
            phases=phases,
            milestones=milestones,
            risks=risks,
            strategic_analysis=strategic_analysis,
            platform_context=platform_context,
            options=roadmap_options,
            context=context
        )
        
        self.logger.info(f"✅ Roadmap created with {len(phases)} phases, {len(milestones)} milestones")
        
        return {
            "artifact_type": "roadmap",
            "artifact": roadmap,
            "confidence": strategic_analysis.get("confidence", 0.85),
            "reasoning": strategic_analysis.get("reasoning", "")
        }
    
    async def _gather_platform_context(self, context: ExecutionContext) -> Dict[str, Any]:
        """Gather platform context for richer roadmaps."""
        platform_context = {}
        
        # Try to get pillar summaries
        try:
            pillar_summaries = await self.use_tool(
                "outcomes_get_pillar_summaries",
                {"session_id": context.session_id},
                context
            )
            if pillar_summaries:
                platform_context["pillar_summaries"] = pillar_summaries
        except Exception:
            pass
        
        # Try to get session state
        if context.state_surface:
            try:
                session_state = await context.state_surface.get_session_state(
                    context.session_id,
                    context.tenant_id
                )
                platform_context.update({
                    "content_summary": session_state.get("content_pillar_summary", {}),
                    "insights_summary": session_state.get("insights_pillar_summary", {}),
                    "journey_summary": session_state.get("journey_pillar_summary", {}),
                    "synthesis": session_state.get("synthesis", {}),
                    "files_processed": session_state.get("content_pillar_summary", {}).get("files_uploaded", 0),
                    "insights_generated": session_state.get("insights_pillar_summary", {}).get("insights_count", 0),
                    "workflows_created": session_state.get("journey_pillar_summary", {}).get("workflows_created", 0)
                })
            except Exception as e:
                self.logger.debug(f"Could not get platform context: {e}")
        
        return platform_context
    
    async def _reason_about_strategy(
        self,
        goals: List[Any],
        timeline: str,
        platform_context: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Reason about strategic approach using LLM.
        
        Analyzes goals and context to determine the best approach
        for the roadmap.
        """
        # Normalize goals to strings
        goal_texts = []
        for goal in goals:
            if isinstance(goal, dict):
                goal_texts.append(goal.get("objective", goal.get("description", str(goal))))
            else:
                goal_texts.append(str(goal))
        
        system_message = """You are the Roadmap Generation Agent, an expert in strategic planning 
and implementation roadmaps. Your role is to analyze goals and design intelligent roadmaps.

KEY PRINCIPLES:
- Goals should be sequenced for maximum value delivery
- Dependencies should be clear and logical
- Risk should be managed through proper phasing
- Each phase should deliver measurable value
- Timeline should be realistic and achievable

Analyze the goals and context to design a strategic approach that:
1. Prioritizes high-value outcomes
2. Manages complexity through phasing
3. Identifies critical dependencies
4. Accounts for resource constraints
5. Creates clear success metrics"""

        user_message = f"""Analyze these goals and design a strategic approach:

GOALS ({len(goal_texts)}):
{json.dumps(goal_texts, indent=2)}

TIMELINE: {timeline}

PLATFORM CONTEXT:
- Files processed: {platform_context.get('files_processed', 0)}
- Insights generated: {platform_context.get('insights_generated', 0)}
- Workflows created: {platform_context.get('workflows_created', 0)}

Design a strategic approach that includes:
1. Recommended number of phases (typically 3-5)
2. Goal prioritization and sequencing
3. Critical success factors
4. Key dependencies between goals
5. Timeline allocation strategy

Return your strategic analysis."""

        try:
            reasoning_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=2000,
                temperature=0.3,
                context=context
            )
            
            # Calculate recommended phases
            months = self._parse_timeline(timeline)
            recommended_phases = min(max(len(goals), 3), 5)
            
            return {
                "reasoning": reasoning_text,
                "recommended_phases": recommended_phases,
                "total_months": months,
                "approach": "phased" if len(goals) > 2 else "focused",
                "priority_goals": goal_texts[:recommended_phases],
                "confidence": 0.85 if goals else 0.70
            }
            
        except Exception as e:
            self.logger.warning(f"LLM strategic analysis failed: {e}")
            return {
                "reasoning": "Strategic analysis based on goal sequencing",
                "recommended_phases": min(max(len(goals), 3), 5),
                "total_months": self._parse_timeline(timeline),
                "approach": "phased",
                "priority_goals": goal_texts[:3],
                "confidence": 0.70
            }
    
    async def _design_intelligent_phases(
        self,
        goals: List[Any],
        timeline: str,
        strategic_analysis: Dict[str, Any],
        platform_context: Dict[str, Any],
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """
        Design intelligent phases using LLM.
        
        Creates phases that are specific to the goals and context,
        not generic templates.
        """
        goal_texts = strategic_analysis.get("priority_goals", [])
        num_phases = strategic_analysis.get("recommended_phases", 3)
        total_months = strategic_analysis.get("total_months", 12)
        
        system_message = """You are designing strategic roadmap phases.

For each phase, design:
1. A compelling, specific name tied to the goal
2. Clear objective derived from the goal
3. Concrete deliverables
4. Measurable success criteria
5. Realistic duration based on complexity
6. Prerequisites and dependencies
7. Resource requirements

IMPORTANT: Phases should be specific to the goals, not generic templates.
Each phase should deliver tangible value and build on previous phases."""

        user_message = f"""Design {num_phases} phases for this roadmap:

GOALS TO ACHIEVE:
{json.dumps(goal_texts, indent=2)}

TOTAL TIMELINE: {total_months} months
STRATEGIC APPROACH: {strategic_analysis.get('approach', 'phased')}

PLATFORM CONTEXT:
- Current state: {platform_context.get('files_processed', 0)} files, {platform_context.get('insights_generated', 0)} insights

Design {num_phases} phases that:
1. Map directly to the goals
2. Have logical dependencies
3. Fit within the timeline
4. Deliver value incrementally
5. Include clear success metrics

Return as JSON array with this structure for each phase:
{{
  "phase_number": 1,
  "name": "Specific phase name tied to goal",
  "objective": "Clear objective from goal",
  "goal_addressed": "which goal this addresses",
  "deliverables": ["deliverable 1", "deliverable 2"],
  "success_criteria": ["measurable criterion 1"],
  "duration_months": 3,
  "prerequisites": ["what must be done first"],
  "resources": ["resource 1", "resource 2"],
  "key_activities": ["activity 1", "activity 2"]
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
            phases = self._parse_phases_response(response_text, goal_texts, num_phases, total_months)
            self.logger.info(f"✅ Designed {len(phases)} intelligent phases")
            return phases
            
        except Exception as e:
            self.logger.warning(f"LLM phase design failed: {e}")
            return self._create_fallback_phases(goal_texts, num_phases, total_months)
    
    def _parse_phases_response(
        self,
        response_text: str,
        goal_texts: List[str],
        num_phases: int,
        total_months: int
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
                    "goal_addressed": phase.get("goal_addressed", goal_texts[i] if i < len(goal_texts) else ""),
                    "deliverables": phase.get("deliverables", []),
                    "success_criteria": phase.get("success_criteria", []),
                    "duration_months": phase.get("duration_months", total_months // num_phases),
                    "prerequisites": phase.get("prerequisites", []),
                    "resources": phase.get("resources", []),
                    "key_activities": phase.get("key_activities", []),
                    "status": "planned"
                }
                validated_phases.append(validated_phase)
            
            return validated_phases if validated_phases else self._create_fallback_phases(goal_texts, num_phases, total_months)
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse phases: {e}")
            return self._create_fallback_phases(goal_texts, num_phases, total_months)
    
    def _create_fallback_phases(
        self,
        goal_texts: List[str],
        num_phases: int,
        total_months: int
    ) -> List[Dict[str, Any]]:
        """Create fallback phases when LLM fails."""
        phases = []
        phase_duration = total_months // num_phases
        
        for i in range(num_phases):
            goal = goal_texts[i] if i < len(goal_texts) else f"Strategic objective {i + 1}"
            
            phase = {
                "phase_number": i + 1,
                "name": f"Phase {i + 1}: {goal[:50]}",
                "objective": goal,
                "goal_addressed": goal,
                "deliverables": [
                    f"Complete {goal}",
                    "Documentation and validation"
                ],
                "success_criteria": [
                    "Objective achieved",
                    "Stakeholder approval"
                ],
                "duration_months": phase_duration,
                "prerequisites": [f"Phase {i} completion"] if i > 0 else [],
                "resources": ["Project team", "Stakeholders"],
                "key_activities": ["Planning", "Execution", "Review"],
                "status": "planned"
            }
            phases.append(phase)
        
        return phases
    
    async def _create_intelligent_milestones(
        self,
        phases: List[Dict[str, Any]],
        goals: List[Any],
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """
        Create intelligent milestones using LLM.
        
        Designs milestones that are meaningful and tied to
        specific phase outcomes.
        """
        system_message = """You are creating milestones for a strategic roadmap.

For each phase, design milestones that:
1. Mark meaningful progress points
2. Are tied to specific deliverables
3. Have clear completion criteria
4. Are appropriate checkpoints for stakeholder review

Include both start and completion milestones, plus key mid-phase checkpoints."""

        phases_summary = [
            {
                "name": p.get("name"),
                "objective": p.get("objective"),
                "deliverables": p.get("deliverables", [])[:2],
                "duration_months": p.get("duration_months")
            }
            for p in phases
        ]

        user_message = f"""Create milestones for these phases:

PHASES:
{json.dumps(phases_summary, indent=2)}

For each phase, create 2-3 milestones including:
1. Phase kickoff milestone
2. Key checkpoint(s) during the phase
3. Phase completion milestone

Return as JSON array:
[{{
  "milestone_id": "unique_id",
  "name": "Milestone name",
  "phase_number": 1,
  "type": "kickoff|checkpoint|completion",
  "timing": "start|mid|end",
  "criteria": "What must be true for this milestone",
  "deliverables": ["associated deliverable"]
}}]"""

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
            
            # Parse milestones
            if isinstance(response_text, str):
                result = json.loads(response_text)
            else:
                result = response_text
            
            milestones = result.get("milestones", result) if isinstance(result, dict) else result
            
            if isinstance(milestones, list) and milestones:
                return milestones
            
        except Exception as e:
            self.logger.warning(f"LLM milestone creation failed: {e}")
        
        # Fallback milestones
        return self._create_fallback_milestones(phases)
    
    def _create_fallback_milestones(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create fallback milestones."""
        milestones = []
        
        for phase in phases:
            phase_num = phase.get("phase_number", 1)
            
            milestones.extend([
                {
                    "milestone_id": f"m_{phase_num}_start",
                    "name": f"{phase.get('name', f'Phase {phase_num}')} Kickoff",
                    "phase_number": phase_num,
                    "type": "kickoff",
                    "timing": "start",
                    "criteria": "Team aligned and resources allocated",
                    "deliverables": []
                },
                {
                    "milestone_id": f"m_{phase_num}_complete",
                    "name": f"{phase.get('name', f'Phase {phase_num}')} Complete",
                    "phase_number": phase_num,
                    "type": "completion",
                    "timing": "end",
                    "criteria": " and ".join(phase.get("success_criteria", ["Objectives met"])),
                    "deliverables": phase.get("deliverables", [])
                }
            ])
        
        return milestones
    
    async def _identify_intelligent_risks(
        self,
        goals: List[Any],
        phases: List[Dict[str, Any]],
        platform_context: Dict[str, Any],
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """
        Identify context-specific risks using LLM.
        
        Analyzes the specific goals and phases to identify
        relevant risks, not generic template risks.
        """
        system_message = """You are identifying risks for a strategic roadmap.

For each risk:
1. Make it specific to the goals and phases
2. Assess probability and impact realistically
3. Provide actionable mitigation strategies
4. Consider dependencies and complexity

Include risks related to:
- Resource constraints
- Technical challenges
- Timeline pressures
- Stakeholder alignment
- External dependencies"""

        goals_summary = [g.get("objective", g) if isinstance(g, dict) else str(g) for g in goals]
        phases_summary = [{"name": p.get("name"), "duration": p.get("duration_months")} for p in phases]

        user_message = f"""Identify risks for this roadmap:

GOALS:
{json.dumps(goals_summary, indent=2)}

PHASES ({len(phases)} total):
{json.dumps(phases_summary, indent=2)}

PLATFORM CONTEXT:
- Files processed: {platform_context.get('files_processed', 0)}
- Complexity indicators: {len(phases)} phases, {len(goals)} goals

Identify 3-5 specific risks with:
1. Risk description specific to these goals
2. Probability (low/medium/high)
3. Impact (low/medium/high)
4. Specific mitigation strategy

Return as JSON array:
[{{
  "risk_id": "unique_id",
  "category": "Resource|Technical|Timeline|Stakeholder|External",
  "title": "Risk title",
  "description": "Specific description tied to goals/phases",
  "probability": "low|medium|high",
  "impact": "low|medium|high",
  "mitigation": "Specific mitigation strategy",
  "affected_phases": [1, 2]
}}]"""

        try:
            response_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=1500,
                temperature=0.3,
                response_format={"type": "json_object"},
                context=context
            )
            
            # Parse risks
            if isinstance(response_text, str):
                result = json.loads(response_text)
            else:
                result = response_text
            
            risks = result.get("risks", result) if isinstance(result, dict) else result
            
            if isinstance(risks, list) and risks:
                return risks
            
        except Exception as e:
            self.logger.warning(f"LLM risk identification failed: {e}")
        
        # Fallback risks
        return self._create_fallback_risks(goals, phases)
    
    def _create_fallback_risks(
        self,
        goals: List[Any],
        phases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create fallback risks."""
        return [
            {
                "risk_id": "r_resource",
                "category": "Resource",
                "title": "Resource Availability",
                "description": f"Resources may be constrained across {len(phases)} phases",
                "probability": "medium",
                "impact": "medium",
                "mitigation": "Early resource planning and contingency allocation",
                "affected_phases": list(range(1, len(phases) + 1))
            },
            {
                "risk_id": "r_scope",
                "category": "Scope",
                "title": "Scope Management",
                "description": f"Managing scope across {len(goals)} goals requires vigilance",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Clear scope definition and formal change management",
                "affected_phases": list(range(1, len(phases) + 1))
            },
            {
                "risk_id": "r_dependencies",
                "category": "Technical",
                "title": "Phase Dependencies",
                "description": "Sequential phase dependencies may create bottlenecks",
                "probability": "low",
                "impact": "high",
                "mitigation": "Identify critical path and build buffer time",
                "affected_phases": [p["phase_number"] for p in phases if p.get("prerequisites")]
            }
        ]
    
    async def _generate_presentation_roadmap(
        self,
        goals: List[Any],
        timeline: str,
        phases: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]],
        risks: List[Dict[str, Any]],
        strategic_analysis: Dict[str, Any],
        platform_context: Dict[str, Any],
        options: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate a presentation-ready roadmap with visual elements.
        """
        # Calculate totals
        total_months = sum(p.get("duration_months", 3) for p in phases)
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=total_months * 30)
        
        # Normalize goals
        goal_texts = [g.get("objective", g) if isinstance(g, dict) else str(g) for g in goals]
        
        # Generate executive summary
        executive_summary = await self._generate_executive_summary(
            goals=goal_texts,
            phases=phases,
            timeline=timeline,
            strategic_analysis=strategic_analysis,
            context=context
        )
        
        # Build presentation-ready roadmap
        roadmap = {
            "roadmap_id": f"roadmap_{context.execution_id}",
            "created_at": datetime.utcnow().isoformat(),
            
            # Executive Summary
            "executive_summary": executive_summary,
            
            # Header
            "title": options.get("title", "Strategic Implementation Roadmap"),
            "subtitle": f"{len(phases)}-Phase Plan over {timeline}",
            "description": options.get("description", strategic_analysis.get("reasoning", "")[:500]),
            
            # Timeline overview (visual-friendly)
            "timeline_overview": {
                "total_duration": timeline,
                "total_months": total_months,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "phase_count": len(phases),
                "milestone_count": len(milestones),
                "risk_count": len(risks)
            },
            
            # Goals
            "goals": goal_texts,
            
            # Phases (detailed)
            "phases": phases,
            
            # Milestones
            "milestones": milestones,
            
            # Dependencies
            "dependencies": self._extract_dependencies(phases),
            
            # Risks
            "risks": risks,
            
            # Strategic plan
            "strategic_plan": {
                "plan_id": f"plan_{context.execution_id}",
                "approach": strategic_analysis.get("approach", "phased"),
                "objectives": goal_texts,
                "key_results": [p.get("deliverables", [""])[0] for p in phases if p.get("deliverables")],
                "success_metrics": [
                    criterion
                    for phase in phases
                    for criterion in phase.get("success_criteria", [])[:1]
                ]
            },
            
            # Visualization data for UI
            "visualization": {
                "timeline_chart": self._generate_timeline_chart(phases, start_date),
                "milestone_markers": self._generate_milestone_markers(milestones, phases),
                "risk_matrix": self._generate_risk_matrix(risks),
                "progress_tracking": {
                    "phases_completed": 0,
                    "milestones_achieved": 0,
                    "current_phase": 1
                }
            },
            
            # Strategic analysis reasoning
            "strategic_analysis": {
                "reasoning": strategic_analysis.get("reasoning"),
                "confidence": strategic_analysis.get("confidence"),
                "approach": strategic_analysis.get("approach")
            }
        }
        
        return roadmap
    
    async def _generate_executive_summary(
        self,
        goals: List[str],
        phases: List[Dict[str, Any]],
        timeline: str,
        strategic_analysis: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate executive summary using LLM."""
        try:
            system_message = """You are creating an executive summary for a strategic roadmap.
Write a compelling, concise summary that:
1. Explains the strategic value
2. Highlights the phased approach
3. Emphasizes achievable outcomes
Keep it to 2-3 paragraphs maximum."""

            user_message = f"""Create an executive summary for this roadmap:

GOALS: {json.dumps(goals[:3], indent=2)}
PHASES: {len(phases)} phases over {timeline}
APPROACH: {strategic_analysis.get('approach', 'phased')}

Key phase highlights:
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
                "key_highlights": [
                    f"{len(phases)} strategic phases",
                    f"Clear milestones and checkpoints",
                    f"Risk-managed approach"
                ],
                "recommended_actions": [
                    "Review roadmap with stakeholders",
                    "Confirm resource allocation",
                    "Approve Phase 1 kickoff"
                ]
            }
            
        except Exception as e:
            self.logger.warning(f"Executive summary generation failed: {e}")
            return {
                "summary": f"This roadmap outlines a {len(phases)}-phase implementation plan to achieve {len(goals)} strategic goals over {timeline}.",
                "key_highlights": [f"{len(phases)} phases", "Clear milestones", "Managed risk"],
                "recommended_actions": ["Review", "Approve", "Execute"]
            }
    
    def _extract_dependencies(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract dependencies from phases."""
        dependencies = []
        
        for i, phase in enumerate(phases):
            if i > 0:
                dependencies.append({
                    "phase": phase["phase_number"],
                    "depends_on": phases[i - 1]["phase_number"],
                    "type": "sequential",
                    "description": f"{phase.get('name')} depends on completion of {phases[i-1].get('name')}"
                })
        
        return dependencies
    
    def _generate_timeline_chart(
        self,
        phases: List[Dict[str, Any]],
        start_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate timeline chart data for visualization."""
        chart_data = []
        current_date = start_date
        
        for phase in phases:
            duration_months = phase.get("duration_months", 3)
            end_date = current_date + timedelta(days=duration_months * 30)
            
            chart_data.append({
                "phase": phase["name"],
                "phase_number": phase["phase_number"],
                "start_date": current_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration_months": duration_months,
                "status": phase.get("status", "planned")
            })
            
            current_date = end_date
        
        return chart_data
    
    def _generate_milestone_markers(
        self,
        milestones: List[Dict[str, Any]],
        phases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate milestone markers for visualization."""
        markers = []
        
        for milestone in milestones:
            phase_num = milestone.get("phase_number", 1)
            phase = next((p for p in phases if p.get("phase_number") == phase_num), {})
            
            markers.append({
                "id": milestone.get("milestone_id"),
                "name": milestone.get("name"),
                "phase_number": phase_num,
                "phase_name": phase.get("name", f"Phase {phase_num}"),
                "type": milestone.get("type"),
                "timing": milestone.get("timing"),
                "status": "pending"
            })
        
        return markers
    
    def _generate_risk_matrix(self, risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate risk matrix for visualization."""
        risk_levels = {"low": 1, "medium": 2, "high": 3}
        
        return {
            "risks": [
                {
                    "id": r.get("risk_id"),
                    "title": r.get("title"),
                    "probability_level": risk_levels.get(r.get("probability", "medium"), 2),
                    "impact_level": risk_levels.get(r.get("impact", "medium"), 2),
                    "category": r.get("category")
                }
                for r in risks
            ],
            "high_priority_count": len([r for r in risks if r.get("impact") == "high"]),
            "total_risks": len(risks)
        }
    
    def _parse_timeline(self, timeline: str) -> int:
        """Parse timeline string to months."""
        timeline_lower = timeline.lower()
        if "year" in timeline_lower:
            try:
                years = int(timeline_lower.split()[0])
                return years * 12
            except (ValueError, IndexError):
                return 12
        elif "month" in timeline_lower:
            try:
                return int(timeline_lower.split()[0])
            except (ValueError, IndexError):
                return 12
        else:
            return 12
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Roadmap Generation Agent - AI-powered strategic roadmap design with intelligent phase planning and risk analysis"
