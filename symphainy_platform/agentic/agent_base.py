"""
Agent Base - Phase 3

Agents are reasoning engines, not services.

WHAT: I provide intelligent reasoning capabilities
HOW: I take context in, reason, and return artifacts out (no side effects)

Critical Rule:
- Agents NEVER write to databases
- Agents NEVER emit events directly
- Agents NEVER orchestrate workflows
- Agents return reasoned artifacts
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from utilities import get_logger, get_clock, LogLevel, LogCategory


class AgentBase(ABC):
    """
    Base class for all agents.
    
    Agents are reasoning engines that:
    - Take context as input
    - Reason about the context
    - Return reasoned artifacts
    - Have NO side effects
    
    This cleanly solves:
    - Determinism vs expertise
    - Auditability
    - Repeatability
    """
    
    def __init__(
        self,
        agent_name: str,
        capabilities: List[str],
        description: Optional[str] = None
    ):
        """
        Initialize agent base.
        
        Args:
            agent_name: Unique name for the agent
            capabilities: List of agent capabilities
            description: Optional description of the agent
        """
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.description = description or f"Agent: {agent_name}"
        self.logger = get_logger(f"agent.{agent_name}", LogLevel.INFO, LogCategory.AGENT)
        self.clock = get_clock()
        
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize the agent.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info(f"Initializing agent: {self.agent_name}")
            self.is_initialized = True
            self.logger.info(f"Agent {self.agent_name} initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize agent {self.agent_name}: {e}", exc_info=e)
            return False
    
    @abstractmethod
    async def reason(
        self,
        context: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Reason about the context and return reasoned artifacts.
        
        This is the core method that all agents must implement.
        Agents take context, reason about it, and return artifacts.
        
        Args:
            context: Input context for reasoning
            **kwargs: Additional parameters for reasoning
        
        Returns:
            Dict containing reasoned artifacts:
            {
                "reasoning": "...",  # Reasoning process
                "artifacts": {...},  # Structured artifacts
                "confidence": 0.0,  # Confidence score (0-1)
                "metadata": {...}    # Additional metadata
            }
        
        Critical Rules:
        - NO side effects (no DB writes, no event emission, no orchestration)
        - Return reasoned artifacts only
        - All state changes must go through Runtime
        """
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information.
        
        Returns:
            Dict containing agent metadata
        """
        return {
            "agent_name": self.agent_name,
            "capabilities": self.capabilities,
            "description": self.description,
            "is_initialized": self.is_initialized
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        self.logger.info(f"Shutting down agent: {self.agent_name}")
        self.is_initialized = False
