"""
Journey Liaison Agent - Interactive SOP Generation Agent

Agent for interactive SOP generation via chat.

WHAT (Agent Role): I provide interactive SOP generation from chat
HOW (Agent Implementation): I reason about user requirements, build SOP through conversation

Key Principle: Agentic reasoning - uses conversation to understand requirements and build SOP.
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

from typing import Dict, Any, Optional, List

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.execution_context import ExecutionContext


class JourneyLiaisonAgent:
    """
    Journey Liaison Agent - Interactive SOP generation.
    
    Provides:
    - Interactive SOP generation session
    - Conversation-based requirement gathering
    - Step-by-step SOP building
    - SOP refinement through chat
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Journey Liaison Agent.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
    
    async def initiate_sop_chat(
        self,
        initial_requirements: Optional[str] = None,
        tenant_id: str = None,
        context: ExecutionContext = None
    ) -> Dict[str, Any]:
        """
        Initiate interactive SOP generation session.
        
        Args:
            initial_requirements: Optional initial requirements from user
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with chat session information
        """
        self.logger.info("Initiating SOP generation chat session")
        
        session_id = generate_event_id()
        
        # Initialize SOP structure
        sop_structure = {
            "title": None,
            "description": None,
            "steps": [],
            "checkpoints": [],
            "requirements": []
        }
        
        # Store session state
        if context and context.state_surface:
            session_state = {
                "sop_chat_session": {
                    "session_id": session_id,
                    "sop_structure": sop_structure,
                    "conversation_history": [],
                    "status": "gathering_requirements"
                }
            }
            await context.state_surface.store_session_state(
                context.session_id,
                context.tenant_id,
                session_state
            )
        
        # Process initial requirements if provided
        if initial_requirements:
            response = await self.process_chat_message(
                session_id=session_id,
                message=initial_requirements,
                tenant_id=tenant_id,
                context=context
            )
        else:
            response = {
                "message": "I'll help you create an SOP. What process would you like to document?",
                "suggestions": [
                    "Describe the process you want to document",
                    "Tell me about the steps involved",
                    "Share any specific requirements or checkpoints"
                ]
            }
        
        return {
            "session_id": session_id,
            "agent_type": "journey_liaison",
            "status": "active",
            "capabilities": [
                "gather_requirements",
                "build_sop_structure",
                "refine_sop",
                "generate_sop"
            ],
            "initial_response": response,
            "sop_structure": sop_structure
        }
    
    async def process_chat_message(
        self,
        session_id: str,
        message: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process a chat message and update SOP structure.
        
        Args:
            session_id: Chat session identifier
            message: User message
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with response and updated SOP structure
        """
        self.logger.info(f"Processing chat message in session {session_id}: {message[:50]}...")
        
        # Retrieve session state
        session_state = None
        if context and context.state_surface:
            full_state = await context.state_surface.get_session_state(
                context.session_id,
                context.tenant_id
            )
            if full_state:
                session_state = full_state.get("sop_chat_session", {})
        
        if not session_state:
            # Session not found, start new session
            return {
                "error": "Session not found. Please start a new SOP generation session.",
                "suggestion": "Use initiate_sop_chat to start a new session"
            }
        
        sop_structure = session_state.get("sop_structure", {
            "title": None,
            "description": None,
            "steps": [],
            "checkpoints": [],
            "requirements": []
        })
        conversation_history = session_state.get("conversation_history", [])
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "message": message,
            "timestamp": context.clock.now().isoformat() if hasattr(context, 'clock') else None
        })
        
        # Process message and update SOP structure
        # For MVP: Simple pattern matching
        # In full implementation: Use LLM to understand intent and extract information
        
        response_message = ""
        updated = False
        
        # Check if message contains title/name
        if not sop_structure["title"]:
            # Try to extract title from message
            if any(word in message.lower() for word in ["sop", "procedure", "process", "for"]):
                # Extract potential title
                words = message.split()
                if len(words) > 2:
                    sop_structure["title"] = " ".join(words[:5])  # Simple extraction
                    response_message = f"Got it! I'll create an SOP for '{sop_structure['title']}'. What are the main steps?"
                    updated = True
        
        # Check if message contains steps
        if any(word in message.lower() for word in ["step", "first", "then", "next", "after"]):
            # Extract step information
            step_text = message
            step_number = len(sop_structure["steps"]) + 1
            sop_structure["steps"].append({
                "step_number": step_number,
                "name": f"Step {step_number}",
                "description": step_text,
                "checkpoint": False
            })
            response_message = f"Added step {step_number}. What's the next step? (Say 'done' when finished)"
            updated = True
        
        # Check if user says done/finished
        if any(word in message.lower() for word in ["done", "finished", "complete", "that's all"]):
            if len(sop_structure["steps"]) > 0:
                response_message = "Great! I have enough information to generate the SOP. Generating now..."
                session_state["status"] = "ready_to_generate"
            else:
                response_message = "I need at least one step to generate the SOP. Can you describe the first step?"
        
        # Default response if no pattern matched
        if not response_message:
            if not sop_structure["title"]:
                response_message = "What process would you like to document? Please provide a title or description."
            elif len(sop_structure["steps"]) == 0:
                response_message = "What are the main steps in this process? Please describe them one by one."
            else:
                response_message = "Got it! Any additional steps or details? (Say 'done' when finished)"
        
        # Add agent response to history
        conversation_history.append({
            "role": "assistant",
            "message": response_message,
            "timestamp": context.clock.now().isoformat() if hasattr(context, 'clock') else None
        })
        
        # Update session state
        session_state["sop_structure"] = sop_structure
        session_state["conversation_history"] = conversation_history
        
        if context and context.state_surface:
            full_state = await context.state_surface.get_session_state(
                context.session_id,
                context.tenant_id
            ) or {}
            full_state["sop_chat_session"] = session_state
            await context.state_surface.store_session_state(
                context.session_id,
                context.tenant_id,
                full_state
            )
        
        return {
            "session_id": session_id,
            "response": response_message,
            "sop_structure": sop_structure,
            "updated": updated,
            "status": session_state.get("status", "gathering_requirements")
        }
    
    async def generate_sop_from_chat(
        self,
        session_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate final SOP from chat session.
        
        Args:
            session_id: Chat session identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with generated SOP
        """
        self.logger.info(f"Generating SOP from chat session {session_id}")
        
        # Retrieve session state
        session_state = None
        if context and context.state_surface:
            full_state = await context.state_surface.get_session_state(
                context.session_id,
                context.tenant_id
            )
            if full_state:
                session_state = full_state.get("sop_chat_session", {})
        
        if not session_state:
            raise ValueError(f"Session {session_id} not found")
        
        sop_structure = session_state.get("sop_structure", {})
        
        if not sop_structure.get("title"):
            raise ValueError("SOP title is required")
        
        if len(sop_structure.get("steps", [])) == 0:
            raise ValueError("At least one step is required")
        
        # Generate SOP document
        sop_id = generate_event_id()
        sop_data = {
            "id": sop_id,
            "title": sop_structure["title"],
            "description": sop_structure.get("description", ""),
            "steps": sop_structure["steps"],
            "checkpoints": sop_structure.get("checkpoints", []),
            "requirements": sop_structure.get("requirements", []),
            "source": "chat_generated",
            "session_id": session_id,
            "created_at": context.clock.now().isoformat() if hasattr(context, 'clock') else None
        }
        
        return {
            "sop_id": sop_id,
            "sop_data": sop_data,
            "status": "generated",
            "source": "chat",
            "session_id": session_id
        }
