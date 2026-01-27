"""
Coexistence Analysis Agent - Friction Removal Analysis Agent

Agent for analyzing workflows to identify friction points and human-positive optimization opportunities.

WHAT (Agent Role): I reason about workflow friction and human-positive optimization
HOW (Agent Implementation): I use LLM to reason about workflows, use MCP tools to call services, construct outcomes

Key Principle: Agentic forward pattern - agent reasons, uses services as tools, constructs outcomes.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
from symphainy_platform.civic_systems.agentic.models.agent_runtime_context import AgentRuntimeContext


class CoexistenceAnalysisAgent(AgentBase):
    """
    Coexistence Analysis Agent - Friction removal analysis.
    
    Uses agentic forward pattern:
    1. Reason about workflow (LLM)
    2. Use MCP tools to call CoexistenceAnalysisService
    3. Reason about friction points (LLM)
    4. Construct human-positive recommendations
    
    ARCHITECTURAL PRINCIPLE: Agent reasons, services execute.
    """
    
    def __init__(self, public_works: Optional[Any] = None, **kwargs):
        """
        Initialize Coexistence Analysis Agent.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
            **kwargs: Additional parameters for 4-layer model support
        """
        # Initialize AgentBase
        super().__init__(
            agent_id="coexistence_analysis_agent",
            agent_type="coexistence_analysis",
            capabilities=["analyze_friction", "identify_human_value", "generate_recommendations"],
            public_works=public_works,
            **kwargs
        )
        self.logger = get_logger(self.__class__.__name__)
    
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
            Dict with coexistence analysis outcome artifacts
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
                # If still empty, try to infer from user_message
                if not request_data:
                    # Check if user_message contains workflow_id
                    if "workflow_id" in user_message.lower():
                        # Try to extract with more flexible regex
                        import re
                        # Try multiple patterns
                        workflow_id_match = re.search(r'workflow_id["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', user_message, re.IGNORECASE)
                        if not workflow_id_match:
                            # Try UUID pattern
                            workflow_id_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', user_message, re.IGNORECASE)
                        if workflow_id_match:
                            request_data = {"type": "analyze_coexistence", "workflow_id": workflow_id_match.group(1)}
                    else:
                        # Try to find any UUID that might be workflow_id
                        import re
                        uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', user_message, re.IGNORECASE)
                        if uuid_match:
                            request_data = {"type": "analyze_coexistence", "workflow_id": uuid_match.group(1)}
                        else:
                            # Default: treat as analyze_coexistence request
                            request_data = {"type": "analyze_coexistence"}
        except (json.JSONDecodeError, ValueError):
            # Fallback: treat as analyze_coexistence request
            request_data = {"type": "analyze_coexistence"}
        
        # Use business context from runtime_context if available
        if runtime_context.business_context:
            request_data.setdefault("business_context", runtime_context.business_context)
        
        # Route to appropriate handler
        request_type = request_data.get("type", "analyze_coexistence")
        
        if request_type == "analyze_coexistence":
            return await self._handle_analyze_coexistence(request_data, context)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext,
        runtime_context: Optional[Any] = None
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
    
    async def _handle_analyze_coexistence(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle coexistence analysis using agentic forward pattern.
        
        Pattern:
        1. Get workflow via MCP tool
        2. Reason about workflow structure (LLM)
        3. Use CoexistenceAnalysisService as tool via MCP
        4. Reason about friction points and human value (LLM)
        5. Construct outcome with human-positive recommendations
        """
        workflow_id = request.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required for coexistence analysis")
        
        self.logger.info(f"Analyzing coexistence for workflow {workflow_id} via agentic forward pattern")
        
        # Step 1: Get workflow data via MCP tool
        workflow_data = await self.use_tool(
            "journey_get_workflow",
            {"workflow_id": workflow_id},
            context
        )
        
        if not workflow_data or not workflow_data.get("success"):
            raise ValueError(f"Failed to retrieve workflow {workflow_id}")
        
        workflow = workflow_data.get("workflow", {})
        
        # Step 2: Reason about workflow structure (LLM)
        workflow_reasoning = await self._reason_about_workflow(workflow, context)
        
        # Step 3: Use CoexistenceAnalysisService as tool via MCP
        service_result = await self.use_tool(
            "journey_analyze_coexistence",
            {
                "workflow_id": workflow_id,
                "reasoning_context": workflow_reasoning
            },
            context
        )
        
        if not service_result or not service_result.get("success"):
            # Fallback: Use service result even if not perfect
            service_result = service_result or {}
        
        # Step 4: Reason about friction points and human value (LLM)
        friction_analysis = await self._reason_about_friction(
            workflow=workflow,
            service_analysis=service_result,
            reasoning_context=workflow_reasoning,
            context=context
        )
        
        # Step 5: Construct outcome with human-positive recommendations
        outcome = {
            "workflow_id": workflow_id,
            "analysis_status": "completed",
            "friction_points": friction_analysis.get("friction_points", []),
            "human_focus_areas": friction_analysis.get("human_focus_areas", []),
            "coexistence_opportunities": friction_analysis.get("opportunities", []),
            "recommendations": friction_analysis.get("recommendations", []),
            "reasoning": friction_analysis.get("reasoning", ""),
            "friction_points_identified": len(friction_analysis.get("friction_points", [])),
            "human_tasks_count": len(friction_analysis.get("human_focus_areas", [])),
            "ai_assisted_tasks_count": len([o for o in friction_analysis.get("opportunities", []) if o.get("type") == "friction_removal"]),
            "hybrid_tasks_count": len([o for o in friction_analysis.get("opportunities", []) if o.get("type") == "hybrid"])
        }
        
        return {
            "artifact_type": "coexistence_analysis",
            "artifact": outcome,
            "confidence": friction_analysis.get("confidence", 0.8),
            "reasoning": friction_analysis.get("reasoning", "")
        }
    
    async def _reason_about_workflow(
        self,
        workflow: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Reason about workflow structure using LLM.
        
        Identifies:
        - Task characteristics
        - Complexity indicators
        - Human value indicators
        - Friction indicators
        """
        system_message = """You are the Coexistence Analysis Agent. Your role is to analyze workflows 
and identify friction points that can be removed with AI assistance, enabling humans to focus on 
high-value work.

Key principles:
- AI removes friction, humans focus on high-value work
- Never suggest replacing humans - suggest removing friction
- Emphasize human value: decision-making, judgment, strategic analysis
- Identify repetitive tasks that create friction
- Recommend AI assistance for friction removal, not automation for replacement

Analyze the workflow structure and identify:
1. Task characteristics (repetitive, complex, requires judgment)
2. Friction indicators (manual data entry, repetitive validation, error-prone steps)
3. Human value indicators (decision-making, strategic thinking, judgment calls)
4. Complexity factors (dependencies, exceptions, edge cases)

Return structured analysis."""
        
        workflow_summary = {
            "workflow_id": workflow.get("workflow_id", "unknown"),
            "steps": workflow.get("steps", []),
            "tasks": workflow.get("tasks", []),
            "description": workflow.get("description", "")
        }
        
        user_message = f"""Analyze this workflow structure:

{workflow_summary}

Identify:
1. Tasks that are repetitive or create friction
2. Tasks that require human judgment or strategic thinking
3. Opportunities for AI to remove friction (not replace humans)
4. How removing friction would enable humans to focus on high-value work

Return your analysis in structured format."""
        
        try:
            reasoning_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=1500,
                temperature=0.3,
                context=context
            )
            
            # Parse reasoning (in production, use structured output)
            # For MVP, extract key insights
            return {
                "reasoning": reasoning_text,
                "workflow_characteristics": self._extract_characteristics(workflow),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.warning(f"LLM reasoning failed, using fallback: {e}")
            return {
                "reasoning": "Workflow analysis completed",
                "workflow_characteristics": self._extract_characteristics(workflow),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _reason_about_friction(
        self,
        workflow: Dict[str, Any],
        service_analysis: Dict[str, Any],
        reasoning_context: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Reason about friction points and human value using LLM.
        
        Generates:
        - Friction points with human-positive messaging
        - Human focus areas
        - Recommendations with friction removal focus
        """
        system_message = """You are the Coexistence Analysis Agent. Your role is to identify friction 
points and generate human-positive recommendations.

CRITICAL: Always use human-positive messaging:
- "Remove friction from X" NOT "Automate X"
- "Enable human focus on Y" NOT "Replace human with AI"
- "AI assistance" NOT "AI automation"
- "Frees humans for high-value work" NOT "Reduces human effort"

Identify friction points and explain:
1. What friction exists (repetitive, manual, error-prone)
2. How AI can remove that friction
3. What high-value work humans can focus on instead
4. Why this is human-positive (collaboration, not replacement)

Return structured recommendations with human-positive messaging."""
        
        user_message = f"""Based on this workflow analysis:

Workflow: {workflow.get('workflow_id', 'unknown')}
Service Analysis: {service_analysis}

Generate:
1. Friction points (with descriptions of friction type)
2. Human focus areas (tasks requiring judgment, decision-making)
3. Recommendations (how to remove friction, enable human focus)

Use human-positive messaging throughout. Emphasize collaboration and human value."""
        
        try:
            reasoning_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=2000,
                temperature=0.3,
                context=context
            )
            
            # Parse LLM output and structure it
            # For MVP, extract and structure the recommendations
            friction_points = self._extract_friction_points(service_analysis, reasoning_text)
            human_focus_areas = self._extract_human_focus_areas(service_analysis, reasoning_text)
            recommendations = self._extract_recommendations(service_analysis, reasoning_text)
            
            return {
                "friction_points": friction_points,
                "human_focus_areas": human_focus_areas,
                "opportunities": service_analysis.get("coexistence_opportunities", []),
                "recommendations": recommendations,
                "reasoning": reasoning_text,
                "confidence": 0.85
            }
        except Exception as e:
            self.logger.warning(f"LLM reasoning failed, using service analysis: {e}")
            # Fallback: Use service analysis with human-positive transformation
            return self._transform_service_analysis_to_human_positive(service_analysis)
    
    def _extract_characteristics(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Extract workflow characteristics for reasoning context."""
        steps = workflow.get("steps", []) or workflow.get("tasks", [])
        return {
            "total_steps": len(steps),
            "step_types": [s.get("type", "unknown") for s in steps],
            "actors": list(set([s.get("actor", "unknown") for s in steps])),
            "complexity_indicators": {
                "decision_points": workflow.get("decision_points", 0),
                "dependencies": len(workflow.get("dependencies", []))
            }
        }
    
    def _extract_friction_points(
        self,
        service_analysis: Dict[str, Any],
        reasoning_text: str
    ) -> List[Dict[str, Any]]:
        """Extract friction points from service analysis and LLM reasoning."""
        friction_points = []
        
        # Get opportunities from service analysis
        opportunities = service_analysis.get("coexistence_opportunities", [])
        friction_opportunities = [o for o in opportunities if o.get("opportunity_type") == "friction_removal"]
        
        for opp in friction_opportunities:
            friction_points.append({
                "task_id": opp.get("task_id"),
                "task_name": opp.get("task_name"),
                "friction_type": opp.get("friction_type", "repetitive_data_processing"),
                "description": opp.get("description", ""),
                "human_value_freed": opp.get("human_value_freed", "decision_making_strategic_analysis"),
                "resolved": False  # Will be resolved when blueprint is created
            })
        
        return friction_points
    
    def _extract_human_focus_areas(
        self,
        service_analysis: Dict[str, Any],
        reasoning_text: str
    ) -> List[Dict[str, Any]]:
        """Extract human focus areas from service analysis and LLM reasoning."""
        human_focus_areas = []
        
        # Get opportunities from service analysis
        opportunities = service_analysis.get("coexistence_opportunities", [])
        human_opportunities = [o for o in opportunities if o.get("opportunity_type") == "human_focus"]
        
        for opp in human_opportunities:
            human_focus_areas.append({
                "task_id": opp.get("task_id"),
                "task_name": opp.get("task_name"),
                "value_type": opp.get("value_type", "strategic_decision_making"),
                "description": opp.get("description", ""),
                "why_human": "Requires judgment, strategic thinking, or decision-making"
            })
        
        return human_focus_areas
    
    def _extract_recommendations(
        self,
        service_analysis: Dict[str, Any],
        reasoning_text: str
    ) -> List[Dict[str, Any]]:
        """Extract recommendations from service analysis, ensuring human-positive messaging."""
        recommendations = []
        
        # Get recommendations from service analysis
        service_recommendations = service_analysis.get("recommendations", [])
        
        for rec in service_recommendations:
            # Ensure human-positive messaging
            description = rec.get("description", "")
            if "automate" in description.lower() and "remove friction" not in description.lower():
                # Transform to friction removal messaging
                description = description.replace("Automate", "Remove friction from")
                description = description.replace("automate", "remove friction from")
                if "enable humans" not in description.lower():
                    description += ", enabling humans to focus on high-value work"
            
            recommendations.append({
                "type": rec.get("type", "friction_removal"),
                "priority": rec.get("priority", "medium"),
                "description": description,
                "impact": rec.get("impact", "medium"),
                "effort": rec.get("effort", "medium"),
                "human_benefit": rec.get("human_benefit", "Frees time for high-value human work")
            })
        
        return recommendations
    
    def _transform_service_analysis_to_human_positive(
        self,
        service_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform service analysis to human-positive format (fallback when LLM fails)."""
        opportunities = service_analysis.get("coexistence_opportunities", [])
        
        friction_points = [
            {
                "task_id": o.get("task_id"),
                "task_name": o.get("task_name"),
                "friction_type": o.get("friction_type", "repetitive_data_processing"),
                "description": o.get("description", ""),
                "human_value_freed": o.get("human_value_freed", "decision_making_strategic_analysis"),
                "resolved": False
            }
            for o in opportunities if o.get("opportunity_type") == "friction_removal"
        ]
        
        human_focus_areas = [
            {
                "task_id": o.get("task_id"),
                "task_name": o.get("task_name"),
                "value_type": o.get("value_type", "strategic_decision_making"),
                "description": o.get("description", ""),
                "why_human": "High-value work requiring judgment and strategic thinking"
            }
            for o in opportunities if o.get("opportunity_type") == "human_focus"
        ]
        
        recommendations = [
            {
                "type": r.get("type", "friction_removal"),
                "priority": r.get("priority", "medium"),
                "description": r.get("description", ""),
                "impact": r.get("impact", "medium"),
                "effort": r.get("effort", "medium"),
                "human_benefit": r.get("human_benefit", "Frees time for high-value human work")
            }
            for r in service_analysis.get("recommendations", [])
        ]
        
        return {
            "friction_points": friction_points,
            "human_focus_areas": human_focus_areas,
            "opportunities": opportunities,
            "recommendations": recommendations,
            "reasoning": "Analysis completed with human-positive friction removal focus",
            "confidence": 0.75
        }
    
    def _assemble_user_message(
        self,
        request: Dict[str, Any],
        runtime_context: Any
    ) -> str:
        """
        Assemble user message from request, ensuring workflow_id is preserved.
        
        Override to ensure workflow_id from request is included in user message
        so it can be extracted later.
        """
        # Get base message from parent
        base_message = super()._assemble_user_message(request, runtime_context)
        
        # Ensure workflow_id is in the message if it's in the request
        workflow_id = request.get("workflow_id")
        if workflow_id and "workflow_id" not in base_message.lower():
            # Add workflow_id to message as JSON for easy extraction
            import json
            request_json = json.dumps({"type": "analyze_coexistence", "workflow_id": workflow_id})
            return f"{request_json}\n\n{base_message}"
        
        return base_message
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Coexistence Analysis Agent - Analyzes workflows to identify friction points and human-positive optimization opportunities"
