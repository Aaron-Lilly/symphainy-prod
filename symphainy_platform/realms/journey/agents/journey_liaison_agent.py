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
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.agentic.agent_base import AgentBase


class JourneyLiaisonAgent(AgentBase):
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
        
        # Process message using LLM to understand intent (no execution)
        # ARCHITECTURAL PRINCIPLE: Liaison agents reason about conversation, don't execute
        
        # Use LLM to understand user intent and extract information
        intent_analysis = await self._understand_conversation_intent(
            message=message,
            conversation_history=conversation_history,
            sop_structure=sop_structure,
            context=context
        )
        
        # Update SOP structure based on LLM analysis (guidance only, not execution)
        updated = False
        if intent_analysis.get("extracted_title"):
            sop_structure["title"] = intent_analysis["extracted_title"]
            updated = True
        
        if intent_analysis.get("extracted_step"):
            step_number = len(sop_structure["steps"]) + 1
            sop_structure["steps"].append({
                "step_number": step_number,
                "name": intent_analysis["extracted_step"].get("name", f"Step {step_number}"),
                "description": intent_analysis["extracted_step"].get("description", ""),
                "checkpoint": intent_analysis["extracted_step"].get("checkpoint", False)
            })
            updated = True
        
        # Generate guidance response (no execution)
        response_message = intent_analysis.get("guidance_response", "How can I help you create an SOP?")
        
        # Check if requirements are complete (ready to delegate)
        if intent_analysis.get("requirements_complete", False):
            session_state["status"] = "ready_to_generate"
            response_message = "Great! I have enough information. Ready to generate the SOP when you say 'generate' or 'done'."
        
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
        Generate final SOP from chat session by delegating to SOPGenerationAgent.
        
        ARCHITECTURAL PRINCIPLE: Liaison agents delegate to specialist agents, don't execute.
        
        Args:
            session_id: Chat session identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with generated SOP
        """
        self.logger.info(f"Delegating SOP generation to specialist agent for session {session_id}")
        
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
        conversation_history = session_state.get("conversation_history", [])
        
        if not sop_structure.get("title"):
            raise ValueError("SOP title is required")
        
        if len(sop_structure.get("steps", [])) == 0:
            raise ValueError("At least one step is required")
        
        # Delegate to SOPGenerationAgent (specialist agent)
        if not self.sop_generation_agent:
            raise ValueError("SOPGenerationAgent not available - cannot generate SOP")
        
        # Use specialist agent to generate SOP
        agent_result = await self.sop_generation_agent.process_request(
            {
                "type": "generate_sop_from_requirements",
                "requirements": sop_structure,
                "conversation_history": conversation_history
            },
            context
        )
        
        # Extract SOP from agent result
        sop_outcome = agent_result.get("artifact", {})
        
        return {
            "sop_id": sop_outcome.get("sop_id"),
            "sop_data": sop_outcome.get("sop_data", {}),
            "status": "generated",
            "source": "chat",
            "session_id": session_id,
            "agent_reasoning": agent_result.get("reasoning", "")
        }
    
    async def _understand_conversation_intent(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        sop_structure: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Understand conversation intent using LLM (no execution).
        
        ARCHITECTURAL PRINCIPLE: Liaison agents reason about conversation, don't execute.
        
        Args:
            message: User message
            conversation_history: Conversation history
            sop_structure: Current SOP structure
            context: Execution context
        
        Returns:
            Dict with intent analysis and guidance
        """
        system_message = """You are a helpful assistant guiding users through SOP creation.

Your role is to:
1. Understand what the user is saying
2. Extract relevant information (title, steps, etc.)
3. Provide guidance on what information is still needed
4. Determine when requirements are complete

You do NOT generate SOPs - you only guide and gather requirements."""
        
        conversation_context = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('message', '')[:100]}"
            for msg in conversation_history[-5:]
        ])
        
        user_message = f"""Analyze this conversation:

Current SOP Structure:
- Title: {sop_structure.get('title', 'Not set')}
- Steps: {len(sop_structure.get('steps', []))} steps
- Description: {sop_structure.get('description', 'Not set')}

Recent Conversation:
{conversation_context}

Current Message: {message}

Analyze and provide:
1. Extracted title (if mentioned)
2. Extracted step (if mentioned)
3. Guidance response (what to ask next)
4. Requirements complete? (true/false)"""
        
        try:
            analysis_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=400,
                temperature=0.3,
                context=context
            )
            
            # Parse analysis (simple extraction - in full implementation, use structured output)
            extracted_title = None
            extracted_step = None
            guidance_response = analysis_text
            requirements_complete = False
            
            # Simple parsing
            if "title:" in analysis_text.lower():
                lines = analysis_text.split('\n')
                for line in lines:
                    if "title:" in line.lower():
                        extracted_title = line.split(":")[-1].strip()
            
            if "step:" in analysis_text.lower() or "extracted step" in analysis_text.lower():
                # Extract step information
                extracted_step = {
                    "name": f"Step {len(sop_structure.get('steps', [])) + 1}",
                    "description": message,
                    "checkpoint": False
                }
            
            if "complete" in analysis_text.lower() and "true" in analysis_text.lower():
                requirements_complete = True
            
            return {
                "extracted_title": extracted_title,
                "extracted_step": extracted_step,
                "guidance_response": guidance_response,
                "requirements_complete": requirements_complete
            }
        except Exception as e:
            self.logger.warning(f"LLM intent understanding failed: {e}")
            # Fallback: Simple pattern matching
            return {
                "extracted_title": None,
                "extracted_step": None,
                "guidance_response": "I'm here to help you create an SOP. What process would you like to document?",
                "requirements_complete": False
            }
