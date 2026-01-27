"""
Guide Agent Journey Orchestrator

Composes AI-powered guidance operations:
1. initiate_guide_agent - Start agent conversation
2. process_guide_agent_message - Handle user messages
3. route_to_liaison_agent - Hand off to specialist

WHAT (Journey Role): I orchestrate AI-powered user guidance
HOW (Journey Implementation): I compose guide agent intents for assistance
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class GuideAgentJourney:
    """
    Guide Agent Journey Orchestrator.
    
    Handles AI-powered guidance:
    - Initiate conversations
    - Process user messages
    - Route to specialized agents
    
    MCP Tools:
    - coexist_init_guide: Start guide agent
    - coexist_send_message: Send message to agent
    - coexist_route_liaison: Route to specialist
    """
    
    JOURNEY_ID = "guide_agent"
    JOURNEY_NAME = "Guide Agent Interaction"
    
    # Liaison agent types
    LIAISON_TYPES = {
        "content": "Content Liaison Agent",
        "insights": "Insights Liaison Agent",
        "journey": "Journey Liaison Agent",
        "operations": "Operations Liaison Agent",
        "outcomes": "Outcomes Liaison Agent"
    }
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        agent_framework: Optional[Any] = None
    ):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.agent_framework = agent_framework
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        
        # In-memory session store (production would use state surface)
        self._agent_sessions: Dict[str, Dict] = {}
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compose guide agent journey."""
        journey_params = journey_params or {}
        action = journey_params.get("action", "initiate")
        journey_execution_id = generate_event_id()
        
        self.logger.info(f"Composing journey: {self.journey_name}, action: {action}")
        
        try:
            if action == "initiate":
                return await self._initiate_guide_agent(context, journey_params, journey_execution_id)
            elif action == "message":
                return await self._process_message(context, journey_params, journey_execution_id)
            elif action == "route_liaison":
                return await self._route_to_liaison(context, journey_params, journey_execution_id)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    async def _initiate_guide_agent(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Initiate a guide agent conversation."""
        trigger_source = params.get("trigger_source", "chat_open")
        current_pillar = params.get("current_pillar")
        conversation_mode = params.get("conversation_mode", "guided")
        
        # Create agent session
        agent_session_id = f"agent_{generate_event_id()}"
        
        # Store session
        self._agent_sessions[agent_session_id] = {
            "created_at": self.clock.now_utc().isoformat(),
            "session_id": context.session_id,
            "conversation_history": [],
            "mode": conversation_mode
        }
        
        # Generate contextual greeting
        greeting = "Hello! I'm your Guide through the Symphainy platform. I can help you understand coexistence concepts, navigate to the right solutions, or answer questions about your current journey. What would you like to explore today?"
        
        if current_pillar:
            greeting = f"Hello! I see you're in the {current_pillar.title()} pillar. I can help you with {current_pillar}-specific questions, explain concepts, or navigate elsewhere. What would you like to do?"
        
        suggestions = [
            "What is coexistence?",
            "Help me find a solution for my needs",
            "Show me what I can do here",
            "Explain the current pillar"
        ]
        
        agent_session = {
            "session_info": {
                "agent_session_id": agent_session_id,
                "created_at": self.clock.now_utc().isoformat(),
                "expires_at": None  # No expiry for now
            },
            "initial_message": {
                "role": "assistant",
                "content": greeting,
                "suggestions": suggestions
            },
            "agent_capabilities": [
                "Platform navigation assistance",
                "Coexistence concept explanation",
                "Solution recommendations",
                "Journey guidance",
                "Artifact explanation"
            ],
            "context_awareness": {
                "knows_current_pillar": current_pillar is not None,
                "current_pillar": current_pillar
            }
        }
        
        semantic_payload = {
            "agent_type": "guide_agent",
            "conversation_mode": conversation_mode,
            "journey_execution_id": journey_execution_id
        }
        
        artifact = create_structured_artifact(
            result_type="guide_agent_session",
            semantic_payload=semantic_payload,
            renderings=agent_session
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"agent_session": artifact},
            "events": [{"type": "guide_agent_initiated", "agent_session_id": agent_session_id}]
        }
    
    async def _process_message(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Process a user message."""
        agent_session_id = params.get("agent_session_id")
        message = params.get("message", "")
        
        if not agent_session_id or agent_session_id not in self._agent_sessions:
            raise ValueError("Invalid or expired agent session")
        
        if not message.strip():
            raise ValueError("Message cannot be empty")
        
        # Generate message ID
        message_id = f"msg_{generate_event_id()}"
        
        # Simple response generation (production would use LLM)
        response_content, suggestions, actions = self._generate_response(message)
        
        # Store in conversation history
        session = self._agent_sessions[agent_session_id]
        session["conversation_history"].append({
            "role": "user",
            "content": message,
            "timestamp": self.clock.now_utc().isoformat()
        })
        session["conversation_history"].append({
            "role": "assistant",
            "content": response_content,
            "timestamp": self.clock.now_utc().isoformat()
        })
        
        conversation_turn = {
            "response": {
                "role": "assistant",
                "content": response_content,
                "timestamp": self.clock.now_utc().isoformat()
            },
            "suggestions": suggestions,
            "detected_intent": {
                "intent_type": "general_query",
                "confidence": 0.8
            },
            "actions": actions
        }
        
        semantic_payload = {
            "message_id": message_id,
            "response_type": "conversational",
            "journey_execution_id": journey_execution_id
        }
        
        artifact = create_structured_artifact(
            result_type="guide_agent_response",
            semantic_payload=semantic_payload,
            renderings=conversation_turn
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"conversation_turn": artifact},
            "events": [{"type": "guide_agent_message_processed", "message_id": message_id}]
        }
    
    def _generate_response(self, message: str) -> tuple:
        """Generate a response to the user message (simplified)."""
        message_lower = message.lower()
        
        # Check for coexistence questions
        if "coexistence" in message_lower or "what is" in message_lower:
            return (
                "**Coexistence** in the Symphainy platform means enabling your existing systems to work together with modern AI capabilities without replacing them.\n\nThink of it like this: instead of ripping out your legacy systems, we help you build bridges between them and modern tools. The platform coordinates work that crosses these boundaries.\n\nWould you like me to show you an example?",
                ["Show me an example", "How does it work?", "Take me to coexistence analysis"],
                []
            )
        
        # Check for navigation requests
        if "content" in message_lower or "upload" in message_lower:
            return (
                "I'll help you get to the Content pillar where you can upload your files. Click the button below to navigate there!",
                ["What can I upload?", "What file types are supported?"],
                [{"action_type": "navigate", "label": "Go to Content", "intent": "navigate_to_solution", "parameters": {"solution_id": "content_solution"}}]
            )
        
        # Check for help requests
        if "help" in message_lower or "what can" in message_lower:
            return (
                "I can help you with several things:\n\n• **Navigation** - Help you find the right solution or pillar\n• **Explanation** - Explain coexistence concepts\n• **Guidance** - Guide you through your journey\n• **Recommendations** - Suggest solutions based on your goals\n\nWhat would you like to explore?",
                ["Explain coexistence", "Show me solutions", "Help me get started"],
                []
            )
        
        # Default response
        return (
            "I'd be happy to help you with that. Could you tell me more about what you're looking for? I can help with navigation, explain concepts, or guide you through the platform.",
            ["What is coexistence?", "Show me solutions", "Help me upload a file"],
            []
        )
    
    async def _route_to_liaison(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Route to a specialized liaison agent."""
        agent_session_id = params.get("agent_session_id")
        liaison_type = params.get("liaison_type")
        handoff_reason = params.get("handoff_reason", "user_request")
        
        if not liaison_type or liaison_type not in self.LIAISON_TYPES:
            raise ValueError(f"Invalid liaison type. Valid types: {list(self.LIAISON_TYPES.keys())}")
        
        liaison_name = self.LIAISON_TYPES[liaison_type]
        liaison_session_id = f"liaison_{generate_event_id()}"
        
        # Generate liaison greeting
        liaison_greeting = f"Hi! I'm the {liaison_name}, and I specialize in {liaison_type} operations. "
        
        if liaison_type == "content":
            liaison_greeting += "I can help you upload files, parse content, and create embeddings. What would you like to do?"
        elif liaison_type == "insights":
            liaison_greeting += "I can help you analyze data, assess quality, and discover patterns. What data would you like to explore?"
        elif liaison_type in ["journey", "operations"]:
            liaison_greeting += "I can help you analyze workflows, create SOPs, and identify coexistence opportunities. What process would you like to examine?"
        elif liaison_type == "outcomes":
            liaison_greeting += "I can help you create POCs, generate roadmaps, and synthesize solutions. What outcome are you working toward?"
        
        guide_farewell = "I'm connecting you with our specialist who can help you better with this. They'll take great care of you! I'll be here if you need general guidance again."
        
        handoff = {
            "handoff_confirmation": {
                "success": True,
                "from_agent_id": agent_session_id,
                "to_agent_id": liaison_session_id,
                "liaison_type": liaison_type,
                "handoff_reason": handoff_reason
            },
            "liaison_session": {
                "liaison_session_id": liaison_session_id,
                "liaison_type": liaison_type,
                "liaison_name": liaison_name,
                "created_at": self.clock.now_utc().isoformat()
            },
            "liaison_greeting": {
                "role": "assistant",
                "content": liaison_greeting,
                "suggestions": self._get_liaison_suggestions(liaison_type)
            },
            "guide_farewell": {
                "role": "assistant",
                "content": guide_farewell,
                "from_agent": "guide_agent"
            }
        }
        
        semantic_payload = {
            "handoff_type": "specialist_routing",
            "from_agent": "guide_agent",
            "to_agent": f"{liaison_type}_liaison",
            "journey_execution_id": journey_execution_id
        }
        
        artifact = create_structured_artifact(
            result_type="liaison_agent_handoff",
            semantic_payload=semantic_payload,
            renderings=handoff
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"liaison_handoff": artifact},
            "events": [{"type": "liaison_handoff_completed", "liaison_type": liaison_type}]
        }
    
    def _get_liaison_suggestions(self, liaison_type: str) -> List[str]:
        """Get suggestions for liaison agent."""
        suggestions = {
            "content": ["Upload a file", "Parse existing content", "Create embeddings"],
            "insights": ["Analyze data quality", "Explore patterns", "Create visualizations"],
            "journey": ["Upload an SOP", "Analyze a workflow", "Create coexistence blueprint"],
            "operations": ["Upload an SOP", "Analyze a workflow", "Create coexistence blueprint"],
            "outcomes": ["Create a POC", "Generate roadmap", "Synthesize solution"]
        }
        return suggestions.get(liaison_type, ["How can I help?"])
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA API definitions for MCP tool registration."""
        return {
            "initiate_guide_agent": {
                "handler": self._handle_initiate,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "trigger_source": {"type": "string"},
                        "current_pillar": {"type": "string"},
                        "conversation_mode": {"type": "string"},
                        "user_context": {"type": "object"}
                    }
                },
                "description": "Start a conversation with the Guide Agent"
            },
            "process_guide_agent_message": {
                "handler": self._handle_message,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_session_id": {"type": "string"},
                        "message": {"type": "string"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["agent_session_id", "message"]
                },
                "description": "Send a message to the Guide Agent"
            },
            "route_to_liaison_agent": {
                "handler": self._handle_route,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_session_id": {"type": "string"},
                        "liaison_type": {"type": "string", "enum": ["content", "insights", "journey", "operations", "outcomes"]},
                        "handoff_reason": {"type": "string"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["liaison_type"]
                },
                "description": "Route to a specialist Liaison Agent"
            }
        }
    
    async def _handle_initiate(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "initiate", **kwargs})
    
    async def _handle_message(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "message", **kwargs})
    
    async def _handle_route(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "route_liaison", **kwargs})
    
    def _create_context(self, kwargs: Dict) -> ExecutionContext:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="coexistence"
        )
        context.state_surface = self.state_surface
        return context
