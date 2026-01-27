"""
Outcomes Liaison Agent - Conversational Guidance for Outcomes Pillar

Agent for providing conversational guidance for Outcomes/Solution pillar operations.

WHAT (Agent Role): I provide conversational guidance for Outcomes pillar
HOW (Agent Implementation): I explain concepts, guide users, answer questions - no execution

Key Principle: Liaison agents explain, guide, and request - but never execute directly.
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


class OutcomesLiaisonAgent(AgentBase):
    """
    Outcomes Liaison Agent - Conversational guidance for Outcomes pillar.
    
    Provides:
    - Artifact generation guidance (Blueprint, POC, Roadmap)
    - Solution synthesis explanation
    - Export guidance
    - User support and explanation
    
    ARCHITECTURAL PRINCIPLE: Liaison agents explain, guide, and request - but never execute.
    """
    
    def __init__(
        self,
        agent_definition_id: str = "outcomes_liaison_agent",
        public_works: Optional[Any] = None,
        agent_definition_registry: Optional[Any] = None,
        mcp_client_manager: Optional[Any] = None,
        telemetry_service: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize Outcomes Liaison Agent.
        
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
            capabilities=["artifact_guidance", "solution_synthesis_explanation", "export_guidance"],
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
            Dict with guidance response
        """
        # Extract message from user_message
        message = user_message.strip()
        
        # Try to extract from runtime_context.business_context if available
        if hasattr(runtime_context, 'business_context') and runtime_context.business_context:
            message = runtime_context.business_context.get("message", message)
        
        # If message looks like JSON, try to parse it
        if message.startswith("{") or message.startswith("["):
            try:
                import json
                parsed = json.loads(message)
                if isinstance(parsed, dict):
                    message = parsed.get("message", parsed.get("text", message))
            except (json.JSONDecodeError, ValueError):
                pass  # Use message as-is
        
        # Build request from message
        request = {
            "type": "chat",
            "message": message
        }
        
        # Route to appropriate handler
        return await self._handle_guidance_request(request, context)
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request - conversational guidance only, no execution.
        
        Args:
            request: Request dictionary with type and parameters
            context: Execution context
            
        Returns:
            Dict with guidance response
        """
        request_type = request.get("type", "chat")
        message = request.get("message", "")
        
        if request_type == "chat" or request_type == "guidance":
            return await self._handle_guidance_request(request, context)
        elif request_type == "explain_artifacts":
            return await self._handle_explain_artifacts(request, context)
        elif request_type == "explain_synthesis":
            return await self._handle_explain_synthesis(request, context)
        else:
            return await self._handle_guidance_request(request, context)
    
    async def _handle_guidance_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle general guidance request using LLM.
        
        ARCHITECTURAL PRINCIPLE: Liaison agents reason about conversation, don't execute.
        """
        message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        
        system_message = """You are a helpful Outcomes/Solution pillar guide. You help users understand:
- Solution synthesis and pillar summaries
- Artifact generation options (Blueprint, POC, Roadmap)
- When to use each artifact type
- Export capabilities

You provide clear explanations and guidance. You do NOT execute actions - you only explain and guide."""
        
        conversation_context = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('message', '')[:100]}"
            for msg in conversation_history[-5:]
        ])
        
        user_message = f"""User question: {message}

Recent conversation:
{conversation_context}

Provide helpful guidance and explanation. Do NOT execute any actions."""
        
        try:
            response_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=500,
                temperature=0.3,
                context=context
            )
            
            return {
                "response": response_text,
                "type": "guidance",
                "suggestions": self._generate_suggestions(message)
            }
        except Exception as e:
            self.logger.warning(f"LLM guidance failed: {e}")
            return {
                "response": "I'm here to help you with Outcomes/Solution pillar operations. What would you like to know?",
                "type": "guidance",
                "suggestions": [
                    "What artifacts can I generate?",
                    "What is solution synthesis?",
                    "How do I export artifacts?"
                ]
            }
    
    async def _handle_explain_artifacts(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Explain artifact generation options (Blueprint, POC, Roadmap).
        """
        system_message = """You are explaining artifact generation options to a user.

The platform can generate three types of artifacts:
1. Coexistence Blueprint - Shows how to optimize workflows with human-positive friction removal
2. POC Proposal - Proof of concept proposal for testing the solution
3. Roadmap - Strategic roadmap for implementation

Explain when to use each and what they contain."""
        
        user_message = "Explain the artifact generation options (Blueprint, POC, Roadmap) and when to use each."
        
        try:
            explanation = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=600,
                temperature=0.3,
                context=context
            )
            
            return {
                "response": explanation,
                "type": "artifact_explanation",
                "artifacts": [
                    {
                        "type": "blueprint",
                        "name": "Coexistence Blueprint",
                        "description": "Shows how to optimize workflows with human-positive friction removal"
                    },
                    {
                        "type": "poc",
                        "name": "POC Proposal",
                        "description": "Proof of concept proposal for testing the solution"
                    },
                    {
                        "type": "roadmap",
                        "name": "Roadmap",
                        "description": "Strategic roadmap for implementation"
                    }
                ]
            }
        except Exception as e:
            self.logger.warning(f"Artifact explanation failed: {e}")
            return {
                "response": "You can generate three types of artifacts: Coexistence Blueprint (workflow optimization), POC Proposal (testing), and Roadmap (implementation strategy).",
                "type": "artifact_explanation"
            }
    
    async def _handle_explain_synthesis(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Explain solution synthesis.
        """
        system_message = """You are explaining solution synthesis to a user.

Solution synthesis combines insights from all pillars (Content, Insights, Journey) to create a comprehensive solution view.

Explain what synthesis does and how it helps users."""
        
        user_message = "Explain solution synthesis and how it works."
        
        try:
            explanation = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=500,
                temperature=0.3,
                context=context
            )
            
            return {
                "response": explanation,
                "type": "synthesis_explanation"
            }
        except Exception as e:
            self.logger.warning(f"Synthesis explanation failed: {e}")
            return {
                "response": "Solution synthesis combines insights from all pillars to create a comprehensive view of your solution.",
                "type": "synthesis_explanation"
            }
    
    def _generate_suggestions(self, message: str) -> List[str]:
        """Generate helpful suggestions based on message."""
        message_lower = message.lower()
        
        if "blueprint" in message_lower:
            return [
                "What is a coexistence blueprint?",
                "How do I create a blueprint?",
                "What does a blueprint contain?"
            ]
        elif "poc" in message_lower or "proof" in message_lower:
            return [
                "What is a POC proposal?",
                "How do I create a POC?",
                "What's in a POC proposal?"
            ]
        elif "roadmap" in message_lower:
            return [
                "What is a roadmap?",
                "How do I generate a roadmap?",
                "What does a roadmap contain?"
            ]
        elif "synthesis" in message_lower or "solution" in message_lower:
            return [
                "What is solution synthesis?",
                "How does synthesis work?",
                "What pillars are included in synthesis?"
            ]
        elif "export" in message_lower:
            return [
                "How do I export artifacts?",
                "What formats are supported?",
                "Can I download artifacts?"
            ]
        else:
            return [
                "What artifacts can I generate?",
                "What is solution synthesis?",
                "How do I export artifacts?"
            ]
    
    async def get_agent_description(self) -> str:
        """Get agent description (required by AgentBase)."""
        return "Outcomes Liaison Agent - Provides conversational guidance for Outcomes/Solution pillar operations"