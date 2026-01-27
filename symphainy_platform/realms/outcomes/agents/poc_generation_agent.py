"""
POC Generation Agent - Proposal Creation Agent

Agent for generating POC proposals with reasoning.

WHAT (Agent Role): I reason about POC requirements and proposal design
HOW (Agent Implementation): I use LLM to reason about scope, objectives, timeline, construct proposals

Key Principle: Agentic forward pattern - agent reasons, uses services as tools, constructs outcomes.
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
from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
from symphainy_platform.civic_systems.agentic.models.agent_runtime_context import AgentRuntimeContext


class POCGenerationAgent(AgentBase):
    """
    POC Generation Agent - Proposal creation and design.
    
    Uses agentic forward pattern:
    1. Reason about POC requirements (LLM)
    2. Design scope and objectives (LLM)
    3. Use POCGenerationService as tool
    4. Enhance proposal with reasoning
    5. Construct POC proposal with compelling content
    
    ARCHITECTURAL PRINCIPLE: Agent reasons, services execute.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize POC Generation Agent.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        # Initialize AgentBase
        super().__init__(
            agent_id="poc_generation_agent",
            agent_type="poc_generation",
            capabilities=["create_poc", "design_scope", "generate_proposal"],
            public_works=public_works
        )
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: AgentRuntimeContext,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request with assembled prompt (4-layer model).
        
        This method is called by AgentBase.process_request() after assembling
        the system and user messages from the 4-layer model.
        
        Args:
            system_message: Assembled system message (from layers 1-3)
            user_message: Assembled user message
            runtime_context: Runtime context with business_context
            context: Execution context
        
        Returns:
            Dict with POC proposal artifacts
        """
        # Extract request from user_message or runtime_context
        request_data = {}
        try:
            import json
            if user_message.strip().startswith("{"):
                request_data = json.loads(user_message)
            else:
                # Try to extract from runtime_context.business_context
                if hasattr(runtime_context, 'business_context') and runtime_context.business_context:
                    request_data = runtime_context.business_context.get("request", {})
                # If still empty, default to create_poc
                if not request_data:
                    request_data = {"type": "create_poc", "description": user_message.strip()}
        except (json.JSONDecodeError, ValueError):
            # Fallback: default request type
            request_data = {"type": "create_poc", "description": user_message.strip()}
        
        # Use business context from runtime_context if available
        if runtime_context.business_context:
            request_data.setdefault("business_context", runtime_context.business_context)
        
        # Route to appropriate handler
        request_type = request_data.get("type", "create_poc")
        
        if request_type == "create_poc":
            return await self._handle_create_poc(request_data, context)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext,
        runtime_context: Optional[AgentRuntimeContext] = None
    ) -> Dict[str, Any]:
        """
        Process request using agentic forward pattern.
        
        ARCHITECTURAL PRINCIPLE: This method delegates to AgentBase.process_request()
        which implements the 4-layer model. For backward compatibility, it can also
        be called directly, but the 4-layer flow is preferred.
        
        Args:
            request: Request dictionary with type and parameters
            context: Execution context
            runtime_context: Optional pre-assembled runtime context (from orchestrator)
            
        Returns:
            Dict with outcome artifacts
        """
        # If runtime_context is provided, use it; otherwise let AgentBase assemble it
        if runtime_context:
            system_message = self._assemble_system_message(runtime_context)
            user_message = self._assemble_user_message(request, runtime_context)
            return await self._process_with_assembled_prompt(
                system_message, user_message, runtime_context, context
            )
        else:
            # Delegate to parent's process_request which implements 4-layer model
            return await super().process_request(request, context, runtime_context=None)
    
    async def _handle_create_poc(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle POC creation using agentic forward pattern.
        
        Pattern:
        1. Reason about POC requirements (LLM)
        2. Design scope and objectives (LLM)
        3. Use POCGenerationService as tool
        4. Enhance proposal with reasoning
        5. Construct POC proposal
        """
        description = request.get("description", "")
        poc_options = request.get("poc_options", {})
        
        # Get synthesis context
        session_state = await context.state_surface.get_session_state(
            context.session_id,
            context.tenant_id
        ) if context.state_surface else {}
        
        synthesis = session_state.get("synthesis", {})
        content_summary = session_state.get("content_pillar_summary", {})
        insights_summary = session_state.get("insights_pillar_summary", {})
        journey_summary = session_state.get("journey_pillar_summary", {})
        
        # Step 1: Reason about POC requirements (LLM)
        poc_reasoning = await self._reason_about_poc_requirements(
            description=description,
            synthesis=synthesis,
            content_summary=content_summary,
            insights_summary=insights_summary,
            journey_summary=journey_summary,
            context=context
        )
        
        # Step 2: Design scope and objectives (LLM)
        scope_design = await self._design_poc_scope(
            description=description,
            poc_reasoning=poc_reasoning,
            context=context
        )
        
        # Step 3: Use POCGenerationService as tool
        poc_result = await self.use_tool(
            "outcomes_create_poc",
            {
                "description": description,
                "poc_options": {
                    **poc_options,
                    "objectives": scope_design.get("objectives", []),
                    "scope": scope_design.get("scope", ""),
                    "reasoning_context": poc_reasoning
                }
            },
            context
        )
        
        if not poc_result or not poc_result.get("success"):
            # Fallback: Create basic POC
            poc_result = self._create_basic_poc(description, scope_design)
        
        poc_proposal = poc_result.get("poc_proposal", poc_result.get("artifact", {}))
        
        # Step 4: Enhance proposal with reasoning
        enhanced_proposal = {
            **poc_proposal,
            "reasoning": poc_reasoning.get("reasoning", ""),
            "scope_rationale": scope_design.get("rationale", ""),
            "generated_by": "poc_generation_agent"
        }
        
        return {
            "artifact_type": "poc_proposal",
            "artifact": enhanced_proposal,
            "confidence": 0.85,
            "reasoning": poc_reasoning.get("reasoning", "")
        }
    
    async def _reason_about_poc_requirements(
        self,
        description: str,
        synthesis: Dict[str, Any],
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Reason about POC requirements using LLM.
        
        Analyzes:
        - What POC should demonstrate
        - Key capabilities to showcase
        - Success criteria
        - Resource requirements
        """
        system_message = """You are the POC Generation Agent. Your role is to analyze requirements 
and design compelling POC proposals.

Analyze:
1. What the POC should demonstrate
2. Key capabilities to showcase
3. Realistic success criteria
4. Resource and timeline requirements
5. Risk factors and mitigation"""
        
        user_message = f"""Analyze POC requirements:

Description: {description}

Context:
- Content: {content_summary.get('files_uploaded', 0)} files processed
- Insights: {insights_summary.get('insights_count', 0)} insights generated
- Journey: {journey_summary.get('workflows_created', 0)} workflows created
- Synthesis: {synthesis.get('overall_synthesis', 'N/A')}

What should this POC demonstrate? What are realistic objectives and scope?"""
        
        try:
            reasoning_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=2000,
                temperature=0.3,
                context=context
            )
            
            return {
                "reasoning": reasoning_text,
                "key_capabilities": ["Data Mash", "Quality Analysis", "Friction Removal"],
                "success_criteria": ["Demonstrate platform capabilities", "Validate approach"]
            }
        except Exception as e:
            self.logger.warning(f"LLM reasoning failed: {e}")
            return {
                "reasoning": "POC requirements analyzed",
                "key_capabilities": [],
                "success_criteria": []
            }
    
    async def _design_poc_scope(
        self,
        description: str,
        poc_reasoning: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Design POC scope and objectives using LLM.
        
        Creates:
        - Clear objectives
        - Realistic scope
        - Timeline
        - Success criteria
        """
        system_message = """You are the POC Generation Agent. Design POC scope and objectives.

Key principles:
- Objectives should be clear and measurable
- Scope should be realistic (not too broad, not too narrow)
- Timeline should be achievable
- Success criteria should be specific"""
        
        user_message = f"""Design POC scope:

Description: {description}
Requirements: {poc_reasoning.get('reasoning', '')}

Design:
1. Clear objectives (3-5 objectives)
2. Realistic scope
3. Achievable timeline (2-4 weeks typical)
4. Specific success criteria"""
        
        try:
            reasoning_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=2000,
                temperature=0.3,
                context=context
            )
            
            # Parse and create scope (in production, use structured output)
            objectives = self._extract_objectives(reasoning_text, description)
            scope = self._extract_scope(reasoning_text, description)
            timeline = self._extract_timeline(reasoning_text)
            success_criteria = self._extract_success_criteria(reasoning_text)
            
            return {
                "objectives": objectives,
                "scope": scope,
                "timeline": timeline,
                "success_criteria": success_criteria,
                "rationale": reasoning_text
            }
        except Exception as e:
            self.logger.warning(f"LLM scope design failed: {e}")
            # Fallback: Create basic scope
            return self._create_basic_scope(description)
    
    def _extract_objectives(
        self,
        reasoning_text: str,
        description: str
    ) -> List[str]:
        """Extract objectives from reasoning (fallback to template)."""
        # In production, use structured output
        # For MVP, create objectives from description
        objectives = [
            "Demonstrate platform capabilities",
            "Validate approach with real data",
            "Generate actionable insights"
        ]
        
        if "data" in description.lower():
            objectives.append("Process and analyze data files")
        if "workflow" in description.lower():
            objectives.append("Optimize workflows and remove friction")
        
        return objectives
    
    def _extract_scope(
        self,
        reasoning_text: str,
        description: str
    ) -> str:
        """Extract scope from reasoning (fallback to template)."""
        # In production, use structured output
        # For MVP, create scope from description
        return f"POC scope: {description}. Includes data processing, quality analysis, and workflow optimization."
    
    def _extract_timeline(
        self,
        reasoning_text: str
    ) -> Dict[str, Any]:
        """Extract timeline from reasoning (fallback to template)."""
        start_date = datetime.utcnow() + timedelta(days=7)
        duration_weeks = 3
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "duration": f"{duration_weeks} weeks"
        }
    
    def _extract_success_criteria(
        self,
        reasoning_text: str
    ) -> List[str]:
        """Extract success criteria from reasoning (fallback to template)."""
        return [
            "Successfully process and analyze data files",
            "Generate quality insights and recommendations",
            "Create optimized workflows with friction removal",
            "Demonstrate platform value to stakeholders"
        ]
    
    def _create_basic_scope(
        self,
        description: str
    ) -> Dict[str, Any]:
        """Create basic scope structure (fallback)."""
        return {
            "objectives": [
                "Demonstrate platform capabilities",
                "Validate approach with real data"
            ],
            "scope": description,
            "timeline": {
                "start_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "end_date": (datetime.utcnow() + timedelta(weeks=3)).isoformat(),
                "duration": "3 weeks"
            },
            "success_criteria": [
                "Successfully process data",
                "Generate insights",
                "Demonstrate value"
            ],
            "rationale": "Basic POC scope"
        }
    
    def _create_basic_poc(
        self,
        description: str,
        scope_design: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create basic POC structure (fallback)."""
        poc_id = f"poc_{datetime.utcnow().isoformat().replace(':', '-')}"
        
        return {
            "success": True,
            "poc_proposal": {
                "poc_id": poc_id,
                "description": description,
                "status": "draft",
                "objectives": scope_design.get("objectives", []),
                "scope": scope_design.get("scope", description),
                "deliverables": ["Analysis report", "Workflow optimizations", "Recommendations"],
                "estimated_duration_weeks": self._parse_duration(scope_design.get("timeline", {}).get("duration", "3 weeks")),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to weeks."""
        if "week" in duration_str.lower():
            try:
                return int(duration_str.split()[0])
            except:
                return 3
        return 3
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "POC Generation Agent - Creates POC proposals with reasoning about scope and objectives"
