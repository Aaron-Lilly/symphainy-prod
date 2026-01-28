"""
Roadmap Generation Agent - Strategic Planning and Roadmap Design

Reasons about strategic planning and designs implementation roadmaps
with clear phases and milestones.

WHAT (Agent Role): I design strategic roadmaps with phases and milestones
HOW (Agent Implementation): I use MCP tools to gather context and generate roadmaps
"""

import sys
from pathlib import Path

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
from ..agent_base import AgentBase
from ..models.agent_runtime_context import AgentRuntimeContext
from symphainy_platform.runtime.execution_context import ExecutionContext


class RoadmapGenerationAgent(AgentBase):
    """
    Roadmap Generation Agent - Designs strategic roadmaps.
    
    Purpose: Reason about strategic planning and design implementation
    roadmaps with clear phases and milestones.
    
    Capabilities:
    - Roadmap design
    - Strategic planning
    - Phase design
    - Milestone planning
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
                "milestone_planning"
            ]
        
        super().__init__(
            agent_id=agent_id,
            agent_type="specialized",
            capabilities=capabilities,
            collaboration_router=collaboration_router,
            **kwargs
        )
        self.public_works = public_works
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext,
        runtime_context: Optional[AgentRuntimeContext] = None
    ) -> Dict[str, Any]:
        """
        Process roadmap generation request.
        
        Args:
            request: Request with goals and roadmap options
            context: Execution context
            runtime_context: Optional runtime context
        
        Returns:
            Dict with roadmap artifact
        """
        goals = request.get("goals", [])
        timeline = request.get("timeline", "12 months")
        roadmap_options = request.get("roadmap_options", {})
        
        # 1. Get pillar summaries for context
        pillar_summaries = {}
        try:
            pillar_summaries = await self.use_tool(
                "outcomes_get_pillar_summaries",
                {"session_id": context.session_id},
                context
            )
        except Exception:
            pass
        
        # 2. Analyze goals and determine phases
        phases = await self._design_phases(
            goals=goals,
            timeline=timeline,
            pillar_summaries=pillar_summaries,
            options=roadmap_options
        )
        
        # 3. Create milestones for each phase
        milestones = await self._create_milestones(
            phases=phases,
            goals=goals
        )
        
        # 4. Identify dependencies and risks
        dependencies = self._identify_dependencies(phases)
        risks = self._identify_risks(phases, goals)
        
        # 5. Build roadmap
        roadmap = {
            "roadmap_id": f"roadmap_{context.execution_id}",
            "title": roadmap_options.get("title", "Strategic Roadmap"),
            "description": roadmap_options.get("description", "Implementation roadmap with phases and milestones"),
            "timeline": timeline,
            "goals": goals,
            "phases": phases,
            "milestones": milestones,
            "dependencies": dependencies,
            "risks": risks,
            "strategic_plan": {
                "plan_id": f"plan_{context.execution_id}",
                "objectives": [goal.get("objective", goal) if isinstance(goal, dict) else goal for goal in goals],
                "key_results": self._extract_key_results(phases)
            }
        }
        
        return {
            "artifact_type": "roadmap",
            "artifact": roadmap,
            "confidence": 0.82
        }
    
    async def _design_phases(
        self,
        goals: List[Any],
        timeline: str,
        pillar_summaries: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Design phases based on goals and context."""
        phases = []
        
        # Parse timeline to estimate phase count
        months = self._parse_timeline(timeline)
        phase_count = min(max(len(goals), 3), 5)  # 3-5 phases
        phase_duration = months // phase_count
        
        for i, goal in enumerate(goals[:phase_count]):
            goal_text = goal.get("objective", goal) if isinstance(goal, dict) else str(goal)
            
            phase = {
                "phase_number": i + 1,
                "name": f"Phase {i + 1}",
                "duration": f"{phase_duration} months",
                "objective": goal_text,
                "deliverables": [
                    f"Complete {goal_text}",
                    f"Validate outcomes",
                    f"Document learnings"
                ],
                "success_criteria": [
                    f"Goal '{goal_text}' achieved",
                    "Stakeholder approval",
                    "Quality standards met"
                ],
                "status": "planned"
            }
            phases.append(phase)
        
        # Add default phases if no goals provided
        if not phases:
            phases = [
                {
                    "phase_number": 1,
                    "name": "Phase 1: Discovery",
                    "duration": "2 months",
                    "objective": "Understand current state and requirements",
                    "deliverables": ["Requirements document", "Current state analysis"],
                    "success_criteria": ["Clear understanding documented"],
                    "status": "planned"
                },
                {
                    "phase_number": 2,
                    "name": "Phase 2: Design",
                    "duration": "3 months",
                    "objective": "Design solution architecture",
                    "deliverables": ["Solution design", "Implementation plan"],
                    "success_criteria": ["Design approved"],
                    "status": "planned"
                },
                {
                    "phase_number": 3,
                    "name": "Phase 3: Implementation",
                    "duration": "4 months",
                    "objective": "Build and deploy solution",
                    "deliverables": ["Working solution", "Documentation"],
                    "success_criteria": ["Solution deployed and operational"],
                    "status": "planned"
                }
            ]
        
        return phases
    
    async def _create_milestones(
        self,
        phases: List[Dict[str, Any]],
        goals: List[Any]
    ) -> List[Dict[str, Any]]:
        """Create milestones for roadmap."""
        milestones = []
        
        for phase in phases:
            # Start milestone
            milestones.append({
                "milestone_id": f"m_{phase['phase_number']}_start",
                "name": f"{phase['name']} Kickoff",
                "phase": phase["phase_number"],
                "type": "start",
                "criteria": "Team aligned and resources allocated"
            })
            
            # Completion milestone
            milestones.append({
                "milestone_id": f"m_{phase['phase_number']}_complete",
                "name": f"{phase['name']} Complete",
                "phase": phase["phase_number"],
                "type": "completion",
                "criteria": " and ".join(phase.get("success_criteria", ["Phase objectives met"]))
            })
        
        return milestones
    
    def _identify_dependencies(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify phase dependencies."""
        dependencies = []
        
        for i, phase in enumerate(phases):
            if i > 0:
                dependencies.append({
                    "phase": phase["phase_number"],
                    "depends_on": phases[i - 1]["phase_number"],
                    "type": "sequential",
                    "description": f"Phase {phase['phase_number']} requires Phase {phases[i-1]['phase_number']} completion"
                })
        
        return dependencies
    
    def _identify_risks(
        self,
        phases: List[Dict[str, Any]],
        goals: List[Any]
    ) -> List[Dict[str, Any]]:
        """Identify potential risks."""
        risks = [
            {
                "risk_id": "r_resource",
                "category": "Resource",
                "description": "Resource availability may impact timeline",
                "probability": "medium",
                "impact": "medium",
                "mitigation": "Early resource planning and backup allocation"
            },
            {
                "risk_id": "r_scope",
                "category": "Scope",
                "description": "Scope creep may delay delivery",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Clear scope definition and change management"
            },
            {
                "risk_id": "r_technical",
                "category": "Technical",
                "description": "Technical challenges may arise",
                "probability": "low",
                "impact": "high",
                "mitigation": "Technical spikes and proof of concepts"
            }
        ]
        
        return risks
    
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
            return 12  # Default to 12 months
    
    def _extract_key_results(self, phases: List[Dict[str, Any]]) -> List[str]:
        """Extract key results from phases."""
        key_results = []
        for phase in phases:
            for deliverable in phase.get("deliverables", [])[:1]:
                key_results.append(deliverable)
        return key_results
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Roadmap Generation Agent - Designs strategic roadmaps with phases and milestones"
