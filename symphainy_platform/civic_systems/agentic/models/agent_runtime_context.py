"""
Agent Runtime Context Model - Layer 3: Journey/Session Scoped

Agent Runtime Context represents ephemeral, session-scoped information.
This is what the agent should know right now.

WHAT (Model Role): I define ephemeral context for agent execution
HOW (Model Implementation): I am assembled at runtime, never stored

Key Principle: This is ephemeral, replaceable, and should never be baked into agent definition.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class AgentRuntimeContext:
    """
    Agent Runtime Context - Journey/Session scoped ephemeral information.
    
    This is Layer 3 of the 4-layer model:
    - Layer 1: AgentDefinition (Platform DNA - stable identity)
    - Layer 2: AgentPosture (Tenant/Solution - behavioral tuning)
    - Layer 3: AgentRuntimeContext (Journey/Session - ephemeral)
    - Layer 4: Prompt Assembly (derived at runtime)
    
    This context is:
    - Assembled at runtime from request/context
    - Never persisted to storage
    - Fed by landing page questions / journey setup
    - Replaced for each new request
    
    Attributes:
        business_context: Business context (industry, systems, constraints)
        journey_goal: Current journey goal
        available_artifacts: List of available artifact IDs
        human_preferences: Human preferences (detail_level, wants_visuals, etc.)
        session_state: Optional session state (for stateful agents)
    """
    
    business_context: Dict[str, Any] = field(default_factory=dict)  # industry, systems, constraints
    journey_goal: str = ""
    available_artifacts: List[str] = field(default_factory=list)
    human_preferences: Dict[str, Any] = field(default_factory=dict)  # detail_level, wants_visuals, etc.
    session_state: Optional[Dict[str, Any]] = None  # For stateful agents
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "business_context": self.business_context,
            "journey_goal": self.journey_goal,
            "available_artifacts": self.available_artifacts,
            "human_preferences": self.human_preferences,
            "session_state": self.session_state
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentRuntimeContext":
        """Create from dictionary."""
        return cls(
            business_context=data.get("business_context", {}),
            journey_goal=data.get("journey_goal", ""),
            available_artifacts=data.get("available_artifacts", []),
            human_preferences=data.get("human_preferences", {}),
            session_state=data.get("session_state")
        )
    
    @classmethod
    async def from_request(
        cls,
        request: Dict[str, Any],
        context: Optional[Any] = None
    ) -> "AgentRuntimeContext":
        """
        Create runtime context from request and execution context.
        
        This is the primary way to create runtime context - from user input
        and execution context, not from stored configuration.
        
        Sources (in priority order):
        1. Request dict (explicit parameters) - highest priority
        2. ExecutionContext.metadata
        3. Session state (via context.state_surface)
        4. Intent.parameters (via context.intent)
        
        Args:
            request: Request dictionary
            context: ExecutionContext (optional)
        
        Returns:
            AgentRuntimeContext instance
        """
        # Start with empty defaults
        business_context = {}
        journey_goal = ""
        available_artifacts = []
        human_preferences = {}
        session_state = None
        
        # Source 4: Extract from Intent.parameters (lowest priority, used as fallback)
        if context and hasattr(context, 'intent') and context.intent:
            intent_params = context.intent.parameters or {}
            business_context = intent_params.get("business_context", {})
            journey_goal = intent_params.get("journey_goal", intent_params.get("goal", ""))
            available_artifacts = intent_params.get("available_artifacts", [])
            human_preferences = intent_params.get("human_preferences", {})
        
        # Source 3: Extract from session state (via context.state_surface)
        if context and hasattr(context, 'state_surface') and context.state_surface:
            try:
                session_state_data = await context.state_surface.get_session_state(
                    context.session_id,
                    context.tenant_id
                )
                if session_state_data:
                    # Extract runtime context fields from session state
                    if not business_context:
                        business_context = session_state_data.get("business_context", {})
                    if not journey_goal:
                        journey_goal = session_state_data.get("journey_goal", session_state_data.get("goal", ""))
                    if not available_artifacts:
                        available_artifacts = session_state_data.get("available_artifacts", [])
                    if not human_preferences:
                        human_preferences = session_state_data.get("human_preferences", {})
                    session_state = session_state_data
            except Exception:
                # Non-critical: if session state retrieval fails, continue with other sources
                pass
        
        # Source 2: Extract from ExecutionContext.metadata
        if context and hasattr(context, 'metadata') and context.metadata:
            if not business_context:
                business_context = context.metadata.get("business_context", {})
            if not journey_goal:
                journey_goal = context.metadata.get("journey_goal", context.metadata.get("goal", ""))
            if not available_artifacts:
                available_artifacts = context.metadata.get("available_artifacts", [])
            if not human_preferences:
                human_preferences = context.metadata.get("human_preferences", {})
        
        # Source 1: Extract from request dict (highest priority - overrides all)
        if request.get("business_context"):
            business_context = request.get("business_context", {})
        if request.get("journey_goal") or request.get("goal"):
            journey_goal = request.get("journey_goal", request.get("goal", ""))
        if request.get("available_artifacts"):
            available_artifacts = request.get("available_artifacts", [])
        if request.get("human_preferences"):
            human_preferences = request.get("human_preferences", {})
        if request.get("session_state"):
            session_state = request.get("session_state")
        
        return cls(
            business_context=business_context,
            journey_goal=journey_goal,
            available_artifacts=available_artifacts,
            human_preferences=human_preferences,
            session_state=session_state
        )
