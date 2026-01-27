"""
Agentic SDK - Agent Framework

Agents reason. They do not execute. Agents operate only inside Runtime execution.

WHAT (Agentic Role): I provide agent framework for reasoning and collaboration
HOW (Agentic Implementation): I provide agent base classes, collaboration, and platform integration

Key Principle: Agents may collaborate to produce proposals and reasoning artifacts,
but may not orchestrate execution or commit side effects; all agent collaboration
is policy-governed and ratified by Solution and Smart City.
"""

from .agent_base import AgentBase
from .agent_registry import AgentRegistry
from .agent_factory import AgentFactory

__all__ = [
    "AgentBase",
    "AgentRegistry",
    "AgentFactory",
]
