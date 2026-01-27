"""
Pre-configured Agent Definitions

Agent definitions for common agents (Layer 1: Platform DNA).
"""

from .structured_extraction_agent_definition import STRUCTURED_EXTRACTION_AGENT_DEFINITION
from .guide_agent_definition import GUIDE_AGENT_DEFINITION
from .journey_liaison_agent_definition import JOURNEY_LIAISON_AGENT_DEFINITION
from .stateless_agent_definition import STATELESS_AGENT_DEFINITION

__all__ = [
    "STRUCTURED_EXTRACTION_AGENT_DEFINITION",
    "GUIDE_AGENT_DEFINITION",
    "JOURNEY_LIAISON_AGENT_DEFINITION",
    "STATELESS_AGENT_DEFINITION"
]
