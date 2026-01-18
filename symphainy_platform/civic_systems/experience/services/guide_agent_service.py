"""
Guide Agent Service - Experience Service Layer

Service for Guide Agent interactions via Experience Service API.

WHAT (Service Role): I provide Guide Agent API for frontend
HOW (Service Implementation): I coordinate Guide Agent and provide REST API interface
"""

import sys
from pathlib import Path

# Add project root to path
# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.civic_systems.agentic.agents.guide_agent import GuideAgent
from symphainy_platform.runtime.execution_context import ExecutionContext


class GuideAgentService:
    """
    Guide Agent Service for Experience Service.
    
    Provides API layer for Guide Agent interactions.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Guide Agent Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Initialize Guide Agent
        self.guide_agent = GuideAgent(public_works=public_works)
        
        self.logger.info("✅ Guide Agent Service initialized")
    
    async def analyze_user_intent(
        self,
        message: str,
        user_context: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """
        Analyze user intent.
        
        Args:
            message: User's message
            user_context: Optional user context
            context: Execution context
        
        Returns:
            Dict with intent analysis results
        """
        try:
            result = await self.guide_agent.analyze_user_intent(
                message=message,
                user_context=user_context,
                context=context
            )
            
            return {
                "success": True,
                "intent_analysis": result
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze user intent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_journey_guidance(
        self,
        user_state: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """
        Get journey guidance.
        
        Args:
            user_state: Current user state
            context: Execution context
        
        Returns:
            Dict with journey guidance
        """
        try:
            result = await self.guide_agent.get_journey_guidance(
                user_state=user_state,
                context=context
            )
            
            return {
                "success": True,
                "guidance": result
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get journey guidance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_chat_message(
        self,
        message: str,
        session_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process chat message.
        
        Args:
            message: User's message
            session_id: Chat session identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with response and guidance
        """
        try:
            result = await self.guide_agent.process_chat_message(
                message=message,
                session_id=session_id,
                tenant_id=tenant_id,
                context=context
            )
            
            return {
                "success": True,
                "response": result.get("response"),
                "intent_analysis": result.get("intent_analysis"),
                "journey_guidance": result.get("journey_guidance"),
                "routing_info": result.get("routing_info"),
                "session_id": session_id
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to process chat message: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def get_conversation_history(
        self,
        session_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Get conversation history.
        
        Args:
            session_id: Chat session identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with conversation history
        """
        try:
            user_state = await self.guide_agent._get_user_state(
                session_id=session_id,
                tenant_id=tenant_id,
                context=context
            )
            
            conversation_history = user_state.get("conversation_history", [])
            
            return {
                "success": True,
                "session_id": session_id,
                "conversation_history": conversation_history,
                "user_state": user_state
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get conversation history: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def route_to_pillar_liaison(
        self,
        pillar: str,
        user_intent: Dict[str, Any],
        session_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Route to pillar liaison agent.
        
        Args:
            pillar: Pillar name
            user_intent: User intent analysis
            session_id: Chat session identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with routing information
        """
        try:
            result = await self.guide_agent.route_to_pillar_liaison(
                pillar=pillar,
                user_intent=user_intent,
                session_id=session_id,
                tenant_id=tenant_id,
                context=context
            )
            
            return {
                "success": result.get("success", True),
                "routing_info": result
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to route to pillar liaison: {e}")
            return {
                "success": False,
                "error": str(e)
            }
