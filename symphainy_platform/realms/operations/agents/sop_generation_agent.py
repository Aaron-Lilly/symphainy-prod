"""
SOP Generation Agent - Requirements Reasoning and SOP Construction

Agent for reasoning about SOP requirements and constructing comprehensive SOP documents.

WHAT (Agent Role): I reason about SOP requirements and construct SOP documents
HOW (Agent Implementation): I use LLM to reason about requirements, design SOP structure, use MCP tools to generate SOPs

Key Principle: Agentic forward pattern - agent reasons, uses services as tools, constructs outcomes.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
from symphainy_platform.civic_systems.agentic.models.agent_runtime_context import AgentRuntimeContext


class SOPGenerationAgent(AgentBase):
    """
    SOP Generation Agent - Requirements reasoning and SOP construction.
    
    Uses agentic forward pattern:
    1. Reason about requirements (LLM)
    2. Understand intent and context (LLM)
    3. Design SOP structure (LLM)
    4. Use MCP tools to generate SOP
    5. Construct SOP document
    
    ARCHITECTURAL PRINCIPLE: Agent reasons, services execute.
    """
    
    def __init__(
        self,
        agent_definition_id: str = "sop_generation_agent",
        public_works: Optional[Any] = None,
        agent_definition_registry: Optional[Any] = None,
        mcp_client_manager: Optional[Any] = None,
        telemetry_service: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize SOP Generation Agent.
        
        Args:
            agent_definition_id: Agent definition ID (loads from JSON config)
            public_works: Public Works Foundation Service (for accessing abstractions)
            agent_definition_registry: Registry for loading agent definitions
            mcp_client_manager: MCP Client Manager for tool access
            telemetry_service: Telemetry service
        """
        # Initialize AgentBase with 4-layer model support
        super().__init__(
            agent_id=agent_definition_id,
            agent_type="specialized",
            capabilities=["sop_design", "requirement_analysis", "sop_structure_creation"],
            agent_definition_id=agent_definition_id,
            public_works=public_works,
            agent_definition_registry=agent_definition_registry,
            mcp_client_manager=mcp_client_manager,
            telemetry_service=telemetry_service,
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
            Dict with SOP generation outcome artifacts
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
                # If still empty, default to generate_sop_from_requirements
                if not request_data:
                    request_data = {"type": "generate_sop_from_requirements"}
        except (json.JSONDecodeError, ValueError):
            # Fallback: default request type
            request_data = {"type": "generate_sop_from_requirements"}
        
        # Use business context from runtime_context if available
        if runtime_context.business_context:
            request_data.setdefault("business_context", runtime_context.business_context)
        
        # Route to appropriate handler
        request_type = request_data.get("type", "generate_sop_from_requirements")
        
        if request_type == "generate_sop_from_requirements":
            return await self._handle_generate_sop_from_requirements(request_data, context)
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
            Dict with SOP generation outcome artifacts
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
    
    async def _handle_generate_sop_from_requirements(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate SOP from requirements gathered through conversation.
        
        Pattern:
        1. Reason about requirements (LLM)
        2. Design SOP structure (LLM)
        3. Use MCP tool to generate SOP
        4. Construct SOP outcome
        """
        requirements = request.get("requirements", {})
        conversation_history = request.get("conversation_history", [])
        
        if not requirements:
            raise ValueError("requirements are required for SOP generation")
        
        self.logger.info("Generating SOP from requirements via agentic forward pattern")
        
        # Step 1: Reason about requirements (LLM)
        requirements_reasoning = await self._reason_about_requirements(
            requirements=requirements,
            conversation_history=conversation_history,
            context=context
        )
        
        # Step 2: Design SOP structure (LLM)
        sop_structure = await self._design_sop_structure(
            requirements=requirements,
            reasoning=requirements_reasoning,
            context=context
        )
        
        # Step 3: Use MCP tool to generate SOP
        sop_result = await self.use_tool(
            "journey_generate_sop_from_structure",
            {
                "sop_structure": sop_structure,
                "requirements": requirements
            },
            context
        )
        
        if not sop_result or not sop_result.get("success"):
            raise ValueError(f"Failed to generate SOP: {sop_result.get('error', 'Unknown error')}")
        
        # Step 4: Construct SOP outcome
        sop_data = sop_result.get("sop", {})
        
        outcome = {
            "sop_id": sop_data.get("sop_id") or sop_data.get("id"),
            "sop_data": sop_data,
            "sop_structure": sop_structure,
            "requirements_reasoning": requirements_reasoning,
            "status": "generated",
            "source": "agent_generated"
        }
        
        return {
            "artifact_type": "sop",
            "artifact": outcome,
            "reasoning": requirements_reasoning.get("reasoning", "")
        }
    
    async def _reason_about_requirements(
        self,
        requirements: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Reason about requirements using LLM.
        
        Args:
            requirements: Requirements dict (title, description, steps, etc.)
            conversation_history: Full conversation history
            context: Execution context
        
        Returns:
            Dict with requirements reasoning
        """
        # Extract key information from requirements
        title = requirements.get("title", "")
        description = requirements.get("description", "")
        steps = requirements.get("steps", [])
        checkpoints = requirements.get("checkpoints", [])
        
        # Build conversation context
        conversation_summary = ""
        if conversation_history:
            recent_messages = conversation_history[-10:]  # Last 10 messages
            conversation_summary = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('message', '')[:100]}"
                for msg in recent_messages
            ])
        
        system_message = """You are an SOP design specialist analyzing requirements to create a comprehensive Standard Operating Procedure.

Your task is to:
1. Understand the process being documented
2. Identify all necessary steps and their sequence
3. Determine checkpoints and validation points
4. Identify any missing information
5. Recommend best practices for the SOP structure

Return a structured analysis of the requirements."""
        
        user_message = f"""Analyze these SOP requirements:

Title: {title}
Description: {description}
Steps Provided: {len(steps)} steps
Checkpoints: {len(checkpoints)} checkpoints

Conversation Context:
{conversation_summary[:500]}

Analyze the requirements and provide:
1. Process understanding (what process is being documented?)
2. Completeness assessment (are all steps captured?)
3. Step sequence validation (is the order logical?)
4. Missing information (what else might be needed?)
5. Recommendations for improvement"""
        
        try:
            reasoning_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=800,
                temperature=0.3,
                context=context
            )
            
            return {
                "reasoning": reasoning_text,
                "requirements_analyzed": {
                    "title": title,
                    "steps_count": len(steps),
                    "checkpoints_count": len(checkpoints)
                }
            }
        except Exception as e:
            self.logger.warning(f"LLM reasoning failed: {e}")
            return {
                "reasoning": "Requirements analysis completed",
                "error": str(e)
            }
    
    async def _design_sop_structure(
        self,
        requirements: Dict[str, Any],
        reasoning: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Design SOP structure using LLM.
        
        Args:
            requirements: Requirements dict
            reasoning: Requirements reasoning
            context: Execution context
        
        Returns:
            Dict with designed SOP structure
        """
        title = requirements.get("title", "Standard Operating Procedure")
        description = requirements.get("description", "")
        steps = requirements.get("steps", [])
        checkpoints = requirements.get("checkpoints", [])
        
        system_message = """You are an SOP design specialist creating a well-structured Standard Operating Procedure.

Design a comprehensive SOP structure that includes:
1. Clear title and description
2. Well-defined steps with proper sequencing
3. Checkpoints and validation points
4. Prerequisites and requirements
5. Expected outcomes

Ensure the SOP is:
- Clear and actionable
- Complete and comprehensive
- Well-organized
- Human-readable"""
        
        steps_text = "\n".join([
            f"Step {i+1}: {step.get('name', step.get('description', ''))} - {step.get('description', '')}"
            for i, step in enumerate(steps)
        ])
        
        user_message = f"""Design SOP structure:

Requirements:
Title: {title}
Description: {description}

Steps:
{steps_text}

Reasoning Analysis:
{reasoning.get('reasoning', '')[:500]}

Design a complete SOP structure with:
1. Title and description
2. All steps (enhanced if needed)
3. Checkpoints
4. Prerequisites
5. Expected outcomes

Return a structured SOP design."""
        
        try:
            structure_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=1500,
                temperature=0.3,
                context=context
            )
            
            # Parse structure text to extract structured format
            # For MVP: Use requirements as base, enhance with LLM suggestions
            sop_structure = {
                "title": title,
                "description": description or structure_text[:200],
                "steps": [],
                "checkpoints": checkpoints,
                "prerequisites": [],
                "expected_outcomes": []
            }
            
            # Enhance steps with LLM suggestions
            for i, step in enumerate(steps):
                enhanced_step = {
                    "step_number": i + 1,
                    "name": step.get("name", f"Step {i+1}"),
                    "description": step.get("description", ""),
                    "checkpoint": step.get("checkpoint", False),
                    "actor": step.get("actor", "user")
                }
                sop_structure["steps"].append(enhanced_step)
            
            # If no steps provided, try to extract from structure_text
            if not sop_structure["steps"]:
                # Simple extraction - in full implementation, use better parsing
                lines = structure_text.split('\n')
                step_num = 1
                for line in lines:
                    if "step" in line.lower() or "1." in line or "-" in line:
                        sop_structure["steps"].append({
                            "step_number": step_num,
                            "name": f"Step {step_num}",
                            "description": line.strip(),
                            "checkpoint": False,
                            "actor": "user"
                        })
                        step_num += 1
            
            return sop_structure
            
        except Exception as e:
            self.logger.warning(f"SOP structure design failed: {e}")
            # Fallback: Use requirements as-is
            return {
                "title": requirements.get("title", "Standard Operating Procedure"),
                "description": requirements.get("description", ""),
                "steps": requirements.get("steps", []),
                "checkpoints": requirements.get("checkpoints", []),
                "prerequisites": [],
                "expected_outcomes": []
            }
    
    async def get_agent_description(self) -> str:
        """Get agent description (required by AgentBase)."""
        return "SOP Generation Agent - Generates Standard Operating Procedures from requirements"