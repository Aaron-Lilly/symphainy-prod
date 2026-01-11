"""
Agentic Foundation - Phase 3

Agents are reasoning engines, not services.

Provides:
- AgentBase: Context-in, reasoning-out, no side effects
- GroundedReasoningAgentBase: Fact gathering, structured extraction, reasoning under constraints
- AgentFoundationService: Orchestrates agent capabilities
"""

from .agent_base import AgentBase
from .grounded_reasoning_agent_base import GroundedReasoningAgentBase
from .foundation_service import AgentFoundationService

__all__ = [
    "AgentBase",
    "GroundedReasoningAgentBase",
    "AgentFoundationService",
]
