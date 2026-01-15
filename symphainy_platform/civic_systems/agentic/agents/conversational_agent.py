"""
Conversational Agent Base - Chat Agents with Varied State Awareness
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional
from ..agent_base import AgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext


class ConversationalAgentBase(AgentBase):
    """
    Base for conversational agents (session-aware).
    
    Purpose: Chat agents with multiple levels, varied state awareness.
    
    State Awareness Levels:
    - "full": Full session state awareness
    - "partial": Partial session state awareness
    - "none": No session state awareness
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: List[str],
        state_awareness: str = "full",
        collaboration_router=None,
        **kwargs
    ):
        """
        Initialize conversational agent.
        
        Args:
            agent_id: Agent identifier
            capabilities: Agent capabilities
            state_awareness: State awareness level ("full", "partial", "none")
            collaboration_router: Optional collaboration router
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="conversational",
            capabilities=capabilities,
            collaboration_router=collaboration_router
        )
        self.state_awareness = state_awareness
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process conversational request with state awareness.
        """
        # 1. Get session state (if state_awareness != "none")
        session_state = None
        if self.state_awareness != "none":
            session_state = await self.get_session_state(context.session_id, context)
        
        # 2. Process conversation
        message = request.get("message", "")
        response = await self.generate_response(
            message=message,
            session_state=session_state,
            context=context
        )
        
        # 3. Update session state (if state_awareness == "full")
        if self.state_awareness == "full" and context.state_surface:
            await self.update_session_state(context, response)
        
        # 4. Return structured output (non-executing)
        return {
            "artifact_type": "proposal",
            "artifact": {
                "response": response,
                "state_awareness": self.state_awareness
            },
            "confidence": 0.9
        }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return f"Conversational agent ({self.agent_id}) - Chat agent with {self.state_awareness} state awareness"
    
    async def generate_response(
        self,
        message: str,
        session_state: Optional[Dict[str, Any]],
        context: ExecutionContext
    ) -> str:
        """
        Generate conversational response (abstract method).
        
        Subclasses should implement this.
        
        Args:
            message: User message
            session_state: Optional session state
            context: Execution context
        
        Returns:
            Response string
        """
        # Default implementation: Echo message
        return f"Echo: {message}"
    
    async def update_session_state(
        self,
        context: ExecutionContext,
        response: str
    ) -> None:
        """
        Update session state with conversation history.
        
        Args:
            context: Execution context
            response: Agent response
        """
        if context.state_surface:
            current_state = await context.state_surface.get_session_state(
                context.session_id,
                context.tenant_id
            ) or {}
            
            # Update conversation history
            conversation_history = current_state.get("conversation_history", [])
            conversation_history.append({
                "response": response,
                "timestamp": context.created_at.isoformat()
            })
            
            current_state["conversation_history"] = conversation_history
            
            await context.state_surface.set_session_state(
                context.session_id,
                context.tenant_id,
                current_state
            )
