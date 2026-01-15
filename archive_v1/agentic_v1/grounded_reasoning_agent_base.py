"""
Grounded Reasoning Agent Base - Phase 3

Extends AgentBase with fact gathering and structured reasoning.

WHAT: I provide grounded reasoning with fact gathering
HOW: I gather facts via Runtime tools, extract structured facts, reason under constraints
"""

from typing import Dict, Any, Optional, List
from .agent_base import AgentBase
from symphainy_platform.runtime.runtime_service import RuntimeService
from symphainy_platform.runtime.state_surface import StateSurface
from utilities import get_logger, LogLevel, LogCategory


class GroundedReasoningAgentBase(AgentBase):
    """
    Base class for agents that need grounded reasoning.
    
    Extends AgentBase with:
    - Fact gathering (via Runtime tools)
    - Structured fact extraction
    - Reasoning under constraints
    - Optional validation (policy-controlled)
    
    This agent type is for agents that need to:
    - Gather facts from Runtime/State Surface
    - Extract structured information
    - Reason about facts with constraints
    - Optionally validate outputs
    """
    
    def __init__(
        self,
        agent_name: str,
        capabilities: List[str],
        runtime_service: RuntimeService,
        state_surface: StateSurface,
        description: Optional[str] = None,
        enable_validation: bool = False
    ):
        """
        Initialize grounded reasoning agent.
        
        Args:
            agent_name: Unique name for the agent
            capabilities: List of agent capabilities
            runtime_service: Runtime service for fact gathering
            state_surface: State surface for querying execution state
            description: Optional description of the agent
            enable_validation: Whether to enable policy-controlled validation
        """
        super().__init__(agent_name, capabilities, description)
        self.runtime_service = runtime_service
        self.state_surface = state_surface
        self.enable_validation = enable_validation
        
        # Override logger with grounded reasoning context
        self.logger = get_logger(f"grounded_agent.{agent_name}", LogLevel.INFO, LogCategory.AGENT)
    
    async def gather_facts(
        self,
        execution_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        fact_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Gather facts from Runtime and State Surface.
        
        This is the primary method for fact gathering.
        Agents use this to query execution state, session state, and other facts.
        
        Args:
            execution_id: Optional execution ID to query
            session_id: Optional session ID to query
            tenant_id: Tenant ID for isolation
            fact_types: Optional list of fact types to gather
        
        Returns:
            Dict containing gathered facts:
            {
                "execution_state": {...},  # If execution_id provided
                "session_state": {...},    # If session_id provided
                "facts": [...],            # Structured facts
                "metadata": {...}          # Fact gathering metadata
            }
        """
        facts = {
            "execution_state": None,
            "session_state": None,
            "facts": [],
            "metadata": {
                "execution_id": execution_id,
                "session_id": session_id,
                "tenant_id": tenant_id,
                "fact_types": fact_types
            }
        }
        
        try:
            # Gather execution state if execution_id provided
            if execution_id and tenant_id:
                execution_state = await self.state_surface.get_execution_state(
                    execution_id=execution_id,
                    tenant_id=tenant_id
                )
                facts["execution_state"] = execution_state
            
            # Gather session state if session_id provided
            if session_id and tenant_id:
                session_state = await self.state_surface.get_session_state(
                    session_id=session_id,
                    tenant_id=tenant_id
                )
                facts["session_state"] = session_state
            
            # Extract structured facts from gathered state
            facts["facts"] = await self._extract_structured_facts(facts)
            
            self.logger.info(
                "Facts gathered",
                metadata={
                    "execution_id": execution_id,
                    "session_id": session_id,
                    "fact_count": len(facts["facts"])
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error gathering facts: {e}", exc_info=e)
            facts["error"] = str(e)
        
        return facts
    
    async def _extract_structured_facts(self, gathered_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract structured facts from gathered data.
        
        This method can be overridden by subclasses to provide custom fact extraction.
        
        Args:
            gathered_data: Data gathered from Runtime/State Surface
        
        Returns:
            List of structured facts
        """
        facts = []
        
        # Extract facts from execution state
        if gathered_data.get("execution_state"):
            execution_state = gathered_data["execution_state"]
            if isinstance(execution_state, dict):
                # Extract key facts from execution state
                facts.append({
                    "type": "execution_state",
                    "data": execution_state,
                    "source": "state_surface"
                })
        
        # Extract facts from session state
        if gathered_data.get("session_state"):
            session_state = gathered_data["session_state"]
            if isinstance(session_state, dict):
                # Extract key facts from session state
                facts.append({
                    "type": "session_state",
                    "data": session_state,
                    "source": "state_surface"
                })
        
        return facts
    
    async def reason_with_facts(
        self,
        context: Dict[str, Any],
        execution_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Reason about context with grounded facts (helper method).
        
        This is a helper method that subclasses can use in their `reason()` implementation.
        It:
        1. Gathers facts from Runtime/State Surface
        2. Extracts structured facts
        3. Calls the subclass's reason() method with enriched context
        4. Optionally validates output
        
        Args:
            context: Input context for reasoning
            execution_id: Optional execution ID for fact gathering
            session_id: Optional session ID for fact gathering
            tenant_id: Tenant ID for isolation
            constraints: Optional constraints for reasoning
            **kwargs: Additional parameters
        
        Returns:
            Dict containing reasoned artifacts
        """
        # Gather facts
        facts = await self.gather_facts(
            execution_id=execution_id,
            session_id=session_id,
            tenant_id=tenant_id
        )
        
        # Combine context with facts
        reasoning_context = {
            "input_context": context,
            "facts": facts,
            "constraints": constraints or {}
        }
        
        # Call subclass's reason method with enriched context
        result = await self.reason(reasoning_context, **kwargs)
        
        # Optionally validate output
        if self.enable_validation:
            validation_result = await self._validate_output(result, constraints)
            result["validation"] = validation_result
        
        return result
    
    async def _validate_output(
        self,
        output: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate output against constraints (policy-controlled).
        
        This method can be overridden by subclasses to provide custom validation.
        
        Args:
            output: Output to validate
            constraints: Optional constraints
        
        Returns:
            Dict containing validation results
        """
        # Default validation (can be overridden)
        return {
            "valid": True,
            "constraints_met": True,
            "validation_details": {}
        }
    
    # Subclasses must implement reason() - it's abstract in parent
    # Subclasses can use reason_with_facts() helper if they want fact gathering
