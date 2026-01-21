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
    def from_request(
        cls,
        request: Dict[str, Any],
        context: Optional[Any] = None
    ) -> "AgentRuntimeContext":
        """
        Create runtime context from request and execution context.
        
        This is the primary way to create runtime context - from user input
        and execution context, not from stored configuration.
        """
        return cls(
            business_context=request.get("business_context", {}),
            journey_goal=request.get("journey_goal", request.get("goal", "")),
            available_artifacts=request.get("available_artifacts", []),
            human_preferences=request.get("human_preferences", {}),
            session_state=request.get("session_state")
        )
