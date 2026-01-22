"""
Guide Agent - Global Concierge for Platform Navigation

Agent for guiding users through the platform and helping them navigate to the right pillars.

WHAT (Agent Role): I guide users through the platform and help them navigate
HOW (Agent Implementation): I analyze user intent, provide navigation guidance, and route to pillar liaison agents

Key Principle: Global concierge - helps users understand platform capabilities and navigate to appropriate pillars.
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

from typing import Dict, Any, Optional, List
from datetime import datetime
from ..agent_base import AgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import get_logger, generate_event_id


class GuideAgent(AgentBase):
    """
    Guide Agent - Global concierge for platform navigation.
    
    Provides:
    - Platform navigation guidance
    - User intent analysis
    - Pillar recommendation
    - Solution context understanding
    - User journey tracking
    - Routing to pillar liaison agents
    """
    
    def __init__(
        self,
        agent_id: str = "guide_agent",
        public_works: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize Guide Agent.
        
        Args:
            agent_id: Agent identifier
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="conversational",
            capabilities=[
                "platform_navigation",
                "intent_analysis",
                "journey_guidance",
                "pillar_routing",
                "user_onboarding",
                "solution_context"
            ],
            collaboration_router=None
        )
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Platform pillars and their capabilities
        self.pillars = {
            "content": {
                "name": "Content Pillar",
                "description": "Upload and parse files, generate semantic embeddings",
                "capabilities": ["file_upload", "file_parsing", "semantic_interpretation"],
                "liaison_agent": None  # Content may not need liaison agent
            },
            "insights": {
                "name": "Insights Pillar",
                "description": "Data quality assessment, interactive analysis, guided discovery",
                "capabilities": ["quality_assessment", "structured_analysis", "unstructured_analysis", "guided_discovery"],
                "liaison_agent": "insights_liaison"
            },
            "journey": {
                "name": "Operations Pillar",
                "description": "Workflow optimization, SOP generation, coexistence analysis",
                "capabilities": ["workflow_creation", "sop_generation", "coexistence_analysis", "blueprint_creation"],
                "liaison_agent": "journey_liaison"
            },
            "outcomes": {
                "name": "Business Outcomes Pillar",
                "description": "Solution synthesis, roadmap generation, POC creation",
                "capabilities": ["solution_synthesis", "roadmap_generation", "poc_creation"],
                "liaison_agent": None  # Outcomes may not need liaison agent
            }
        }
    
    async def analyze_user_intent(
        self,
        message: str,
        user_context: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """
        Analyze user intent to understand what they want to accomplish.
        
        Args:
            message: User's message
            user_context: Optional user context (current state, previous actions)
            context: Execution context
        
        Returns:
            Dict with intent analysis results
        """
        self.logger.info(f"Analyzing user intent: {message[:50]}...")
        
        # For MVP: Simple keyword-based intent analysis
        # In full implementation: Use LLM for better understanding
        
        message_lower = message.lower()
        
        # Determine intent category
        intent_category = "general"
        recommended_pillar = None
        confidence = 0.7
        
        # Check for pillar-specific keywords
        if any(word in message_lower for word in ["upload", "file", "parse", "data", "content"]):
            intent_category = "content_management"
            recommended_pillar = "content"
            confidence = 0.8
        
        elif any(word in message_lower for word in ["analyze", "insight", "quality", "assessment", "discovery", "interpret"]):
            intent_category = "data_analysis"
            recommended_pillar = "insights"
            confidence = 0.8
        
        elif any(word in message_lower for word in ["workflow", "sop", "process", "operation", "procedure", "blueprint"]):
            intent_category = "process_management"
            recommended_pillar = "journey"
            confidence = 0.8
        
        elif any(word in message_lower for word in ["solution", "roadmap", "poc", "outcome", "proposal", "plan"]):
            intent_category = "solution_planning"
            recommended_pillar = "outcomes"
            confidence = 0.8
        
        elif any(word in message_lower for word in ["help", "guide", "navigate", "what", "how", "where"]):
            intent_category = "navigation"
            confidence = 0.9
        
        # Extract key requirements
        requirements = []
        if "upload" in message_lower:
            requirements.append("file_upload")
        if "analyze" in message_lower or "analysis" in message_lower:
            requirements.append("data_analysis")
        if "workflow" in message_lower or "process" in message_lower:
            requirements.append("process_optimization")
        if "solution" in message_lower or "roadmap" in message_lower:
            requirements.append("solution_planning")
        
        return {
            "intent_category": intent_category,
            "recommended_pillar": recommended_pillar,
            "confidence": confidence,
            "requirements": requirements,
            "message": message,
            "analysis": {
                "understood": True,
                "needs_clarification": confidence < 0.7
            }
        }
    
    async def get_journey_guidance(
        self,
        user_state: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """
        Get journey guidance - recommend next pillar/action based on user's current state.
        
        Args:
            user_state: Current user state (what they've done, current pillar)
            context: Execution context
        
        Returns:
            Dict with journey guidance
        """
        self.logger.info("Generating journey guidance")
        
        if not user_state:
            user_state = {}
        
        current_pillar = user_state.get("current_pillar")
        completed_pillars = user_state.get("completed_pillars", [])
        user_goals = user_state.get("goals", [])
        
        # Determine recommended next step
        recommended_pillar = None
        recommended_action = None
        reasoning = ""
        
        # If user hasn't started, recommend Content pillar
        if not current_pillar and "content" not in completed_pillars:
            recommended_pillar = "content"
            recommended_action = "upload_files"
            reasoning = "Start by uploading your files to begin your journey"
        
        # If Content is done but Insights isn't, recommend Insights
        elif "content" in completed_pillars and "insights" not in completed_pillars:
            recommended_pillar = "insights"
            recommended_action = "assess_data_quality"
            reasoning = "Now that your files are uploaded, assess data quality and generate insights"
        
        # If Insights is done but Journey isn't, recommend Journey
        elif "insights" in completed_pillars and "journey" not in completed_pillars:
            recommended_pillar = "journey"
            recommended_action = "create_workflow"
            reasoning = "With insights in hand, optimize your processes and create workflows"
        
        # If Journey is done but Outcomes isn't, recommend Outcomes
        elif "journey" in completed_pillars and "outcomes" not in completed_pillars:
            recommended_pillar = "outcomes"
            recommended_action = "synthesize_outcome"
            reasoning = "Complete your journey by synthesizing outcomes and creating solutions"
        
        # If all pillars are done, suggest solution creation
        elif len(completed_pillars) >= 4:
            recommended_pillar = "outcomes"
            recommended_action = "create_solution"
            reasoning = "All pillars complete! Create your platform solution"
        
        # Default: stay in current pillar
        else:
            recommended_pillar = current_pillar or "content"
            recommended_action = "explore"
            reasoning = "Continue exploring current pillar capabilities"
        
        return {
            "recommended_pillar": recommended_pillar,
            "recommended_action": recommended_action,
            "reasoning": reasoning,
            "current_pillar": current_pillar,
            "completed_pillars": completed_pillars,
            "next_steps": self._get_pillar_next_steps(recommended_pillar)
        }
    
    def _get_pillar_next_steps(self, pillar: Optional[str]) -> List[str]:
        """Get next steps for a pillar."""
        if not pillar or pillar not in self.pillars:
            return []
        
        pillar_info = self.pillars[pillar]
        
        if pillar == "content":
            return [
                "Upload your files",
                "View parsed results",
                "See semantic interpretation"
            ]
        elif pillar == "insights":
            return [
                "Assess data quality",
                "Run interactive analysis",
                "Use guided discovery"
            ]
        elif pillar == "journey":
            return [
                "Create workflows",
                "Generate SOPs",
                "Analyze coexistence",
                "Create blueprints"
            ]
        elif pillar == "outcomes":
            return [
                "Synthesize outcomes",
                "Generate roadmap",
                "Create POC proposal",
                "Create solution"
            ]
        
        return []
    
    async def process_chat_message(
        self,
        message: str,
        session_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process chat message and provide guidance.
        
        Args:
            message: User's message
            session_id: Chat session identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with response and guidance
        """
        self.logger.info(f"Processing chat message in session {session_id}")
        
        # Get user state from session
        user_state = await self._get_user_state(session_id, tenant_id, context)
        
        # Analyze user intent
        intent_analysis = await self.analyze_user_intent(
            message=message,
            user_context=user_state,
            context=context
        )
        
        # Get journey guidance
        journey_guidance = await self.get_journey_guidance(
            user_state=user_state,
            context=context
        )
        
        # Generate response
        response = await self._generate_guidance_response(
            message=message,
            intent_analysis=intent_analysis,
            journey_guidance=journey_guidance,
            user_state=user_state
        )
        
        # Check if should route to pillar liaison agent
        should_route = intent_analysis.get("recommended_pillar") and \
                      intent_analysis.get("confidence", 0) > 0.7
        
        routing_info = None
        if should_route:
            recommended_pillar = intent_analysis["recommended_pillar"]
            pillar_info = self.pillars.get(recommended_pillar, {})
            liaison_agent = pillar_info.get("liaison_agent")
            
            if liaison_agent:
                routing_info = {
                    "should_route": True,
                    "pillar": recommended_pillar,
                    "liaison_agent": liaison_agent,
                    "routing_message": f"I can help you with {pillar_info['name']}. Would you like me to connect you with the {pillar_info['name']} specialist?"
                }
        
        return {
            "session_id": session_id,
            "response": response,
            "intent_analysis": intent_analysis,
            "journey_guidance": journey_guidance,
            "routing_info": routing_info,
            "user_state": user_state
        }
    
    async def _generate_guidance_response(
        self,
        message: str,
        intent_analysis: Dict[str, Any],
        journey_guidance: Dict[str, Any],
        user_state: Dict[str, Any]
    ) -> str:
        """Generate guidance response based on intent and journey state."""
        intent_category = intent_analysis.get("intent_category", "general")
        recommended_pillar = intent_analysis.get("recommended_pillar")
        confidence = intent_analysis.get("confidence", 0.7)
        
        # If high confidence and pillar identified, provide specific guidance
        if confidence > 0.7 and recommended_pillar:
            pillar_info = self.pillars.get(recommended_pillar, {})
            next_steps = journey_guidance.get("next_steps", [])
            
            response = f"I can help you with the {pillar_info['name']}. "
            response += f"{pillar_info['description']}. "
            
            if next_steps:
                response += f"Here's what you can do:\n"
                for i, step in enumerate(next_steps[:3], 1):
                    response += f"{i}. {step}\n"
            
            return response
        
        # If navigation question, provide platform overview
        if intent_category == "navigation":
            response = "I'm here to help you navigate the Symphainy Platform! "
            response += "We have four main pillars:\n\n"
            
            for pillar_key, pillar_info in self.pillars.items():
                response += f"**{pillar_info['name']}**: {pillar_info['description']}\n"
            
            response += "\nWhat would you like to do? I can guide you to the right place."
            return response
        
        # Default response
        response = "I understand you're looking for help. "
        response += f"Based on your message, I recommend starting with the {journey_guidance.get('recommended_pillar', 'Content')} pillar. "
        response += journey_guidance.get("reasoning", "This is a good starting point.")
        
        return response
    
    async def _get_user_state(
        self,
        session_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Get user state from session."""
        if not context or not context.state_surface:
            return {}
        
        try:
            session_state = await context.state_surface.get_session_state(
                session_id,
                tenant_id
            )
            
            if session_state:
                return session_state.get("guide_agent_state", {
                    "current_pillar": None,
                    "completed_pillars": [],
                    "goals": [],
                    "conversation_history": []
                })
        except Exception as e:
            self.logger.debug(f"Could not retrieve user state: {e}")
        
        return {
            "current_pillar": None,
            "completed_pillars": [],
            "goals": [],
            "conversation_history": []
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
        Route user to appropriate pillar liaison agent.
        
        Args:
            pillar: Pillar name to route to
            user_intent: User intent analysis
            session_id: Chat session identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with routing information
        """
        self.logger.info(f"Routing to {pillar} pillar liaison agent")
        
        pillar_info = self.pillars.get(pillar)
        if not pillar_info:
            return {
                "success": False,
                "error": f"Unknown pillar: {pillar}"
            }
        
        liaison_agent = pillar_info.get("liaison_agent")
        if not liaison_agent:
            return {
                "success": False,
                "error": f"No liaison agent available for {pillar} pillar"
            }
        
        # Update user state
        user_state = await self._get_user_state(session_id, tenant_id, context)
        user_state["current_pillar"] = pillar
        
        if context and context.state_surface:
            session_state = await context.state_surface.get_session_state(
                session_id,
                tenant_id
            ) or {}
            session_state["guide_agent_state"] = user_state
            await context.state_surface.store_session_state(
                session_id,
                tenant_id,
                session_state
            )
        
        return {
            "success": True,
            "pillar": pillar,
            "liaison_agent": liaison_agent,
            "pillar_info": pillar_info,
            "routing_message": f"Connecting you with the {pillar_info['name']} specialist..."
        }
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process a request using Guide Agent capabilities.
        
        Args:
            request: Request dictionary (should contain "message" and "session_id")
            context: Runtime execution context
        
        Returns:
            Dict with non-executing artifacts (guidance, recommendations)
        """
        message = request.get("message", "")
        session_id = request.get("session_id", context.session_id)
        
        # Process chat message
        result = await self.process_chat_message(
            message=message,
            session_id=session_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Return as non-executing artifact
        return {
            "artifact_type": "proposal",
            "artifact": {
                "response": result.get("response"),
                "intent_analysis": result.get("intent_analysis"),
                "journey_guidance": result.get("journey_guidance"),
                "routing_info": result.get("routing_info")
            },
            "confidence": result.get("intent_analysis", {}).get("confidence", 0.7)
        }
    
    async def discover_business_context(
        self,
        conversation_history: List[Dict[str, str]],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Discover provisional business context from conversation.
        
        ARCHITECTURAL PRINCIPLE: GuideAgent may discover context, but does not own it.
        Discovery context is provisional until committed by user/platform.
        
        Args:
            conversation_history: List of conversation messages [{"role": "user", "content": "..."}, ...]
            context: Execution context
        
        Returns:
            Dict with discovery context (provisional)
        """
        self.logger.info("Discovering business context from conversation")
        
        # Build conversation text for LLM
        conversation_text = "\n".join([
            f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}"
            for msg in conversation_history[-10:]  # Last 10 messages
        ])
        
        # Use LLM to infer business context from conversation
        discovery_prompt = f"""You are a discovery agent helping to understand a user's business context from their conversation.

Analyze the following conversation and extract:
1. Industry/domain (e.g., Insurance, Healthcare, Finance)
2. Legacy systems mentioned (e.g., Mainframe, Salesforce, SAP)
3. Business goals (what they want to achieve)
4. Constraints (regulatory, technical, business)
5. User preferences (detail level, wants visuals, explanation style)

Conversation:
{conversation_text}

Return a JSON object with:
{{
    "industry": "string or null",
    "systems": ["system1", "system2"],
    "goals": ["goal1", "goal2"],
    "constraints": ["constraint1", "constraint2"],
    "preferences": {{
        "detail_level": "summary|detailed|technical",
        "wants_visuals": true/false,
        "explanation_style": "simple|technical|business"
    }},
    "confidence": {{
        "industry": 0.0-1.0,
        "systems": 0.0-1.0,
        "goals": 0.0-1.0
    }}
}}

If information is not available, use null or empty arrays. Be conservative with confidence scores."""
        
        try:
            # Call LLM via AgentBase._call_llm
            discovery_result = await self._call_llm(
                prompt=discovery_prompt,
                system_message="You are a discovery agent that extracts business context from conversations. Return only valid JSON.",
                model="gpt-4o-mini",
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more consistent extraction
                context=context
            )
            
            # Parse LLM response (should be JSON)
            import json
            if isinstance(discovery_result, str):
                # Try to extract JSON from response
                try:
                    discovery_data = json.loads(discovery_result)
                except json.JSONDecodeError:
                    # Try to find JSON in the response
                    import re
                    json_match = re.search(r'\{.*\}', discovery_result, re.DOTALL)
                    if json_match:
                        discovery_data = json.loads(json_match.group())
                    else:
                        self.logger.warning("Could not parse discovery result as JSON, using defaults")
                        discovery_data = {}
            else:
                discovery_data = discovery_result
            
            # Build discovery context structure
            discovery_context = {
                "industry": discovery_data.get("industry"),
                "systems": discovery_data.get("systems", []),
                "goals": discovery_data.get("goals", []),
                "constraints": discovery_data.get("constraints", []),
                "preferences": discovery_data.get("preferences", {
                    "detail_level": "detailed",
                    "wants_visuals": True,
                    "explanation_style": "technical"
                }),
                "confidence": discovery_data.get("confidence", {
                    "industry": 0.5,
                    "systems": 0.5,
                    "goals": 0.5
                }),
                "source": "guide_agent",
                "discovered_at": datetime.now().isoformat(),
                "status": "provisional"
            }
            
            # Store in session state (discovery namespace)
            if context and context.state_surface:
                session_state = await context.state_surface.get_session_state(
                    context.session_id,
                    context.tenant_id
                ) or {}
                
                session_state["discovery_context"] = discovery_context
                
                await context.state_surface.store_session_state(
                    context.session_id,
                    context.tenant_id,
                    session_state
                )
                
                self.logger.info(f"✅ Discovery context stored in session {context.session_id}")
            
            return discovery_context
            
        except Exception as e:
            self.logger.error(f"Failed to discover business context: {e}", exc_info=True)
            # Return empty discovery context on error
            return {
                "industry": None,
                "systems": [],
                "goals": [],
                "constraints": [],
                "preferences": {
                    "detail_level": "detailed",
                    "wants_visuals": True,
                    "explanation_style": "technical"
                },
                "confidence": {
                    "industry": 0.0,
                    "systems": 0.0,
                    "goals": 0.0
                },
                "source": "guide_agent",
                "discovered_at": datetime.now().isoformat(),
                "status": "provisional",
                "error": str(e)
            }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Guide Agent - Global concierge for platform navigation and user guidance"
