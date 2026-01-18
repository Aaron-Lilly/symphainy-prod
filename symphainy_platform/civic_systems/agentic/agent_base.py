"""
Agent Base - Core Agent Class

Base class for all agents with policy-governed collaboration support.

WHAT (Agent Role): I provide intelligent agent capabilities
HOW (Agent Implementation): I reason, collaborate, and produce proposals

Key Principle: Agents reason. They do not execute.
Agents may collaborate, but they may not commit.
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

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from utilities import get_logger

from symphainy_platform.runtime.execution_context import ExecutionContext
from .collaboration.contribution_request import ContributionRequest, ContributionResponse
from .collaboration.collaboration_router import CollaborationRouter


class AgentBase(ABC):
    """
    Base class for all agents.
    
    Provides:
    - Request processing (abstract)
    - Agent description (abstract)
    - Platform integration (tools, session state)
    - Policy-governed collaboration
    - Structured output (proposals, blueprints, ranked options)
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: List[str],
        collaboration_router: Optional[CollaborationRouter] = None
    ):
        """
        Initialize agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type (e.g., "stateless", "conversational")
            capabilities: List of agent capabilities
            collaboration_router: Optional collaboration router
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.collaboration_router = collaboration_router
        self.logger = get_logger(f"Agent:{agent_id}")
    
    @abstractmethod
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process a request using agent capabilities.
        
        Returns: Non-executing artifacts only (proposals, blueprints, ranked options).
        
        Args:
            request: Request dictionary
            context: Runtime execution context
        
        Returns:
            Dict with non-executing artifacts
        """
        pass
    
    @abstractmethod
    async def get_agent_description(self) -> str:
        """
        Get agent description for discovery.
        
        Returns:
            Agent description string
        """
        pass
    
    async def use_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Use a Smart City tool (via MCP).
        
        Args:
            tool_name: Tool name
            params: Tool parameters
            context: Execution context
        
        Returns:
            Tool result
        """
        # MVP: Basic tool integration placeholder
        # Full: Would integrate with MCP (Model Context Protocol) for tool discovery and execution
        # For MVP, we return a structured response indicating tool usage
        self.logger.info(f"Tool usage requested: {tool_name} with params: {params}")
        
        # In full implementation, this would:
        # 1. Discover tool via MCP adapter
        # 2. Validate tool access via Smart City primitives
        # 3. Execute tool via MCP
        # 4. Return tool result
        
        return {
            "tool": tool_name,
            "params": params,
            "result": "tool_execution_placeholder",
            "status": "not_implemented",
            "note": "MCP tool integration will be implemented in full version"
        }
    
    async def get_session_state(
        self,
        session_id: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """
        Get session state (via Runtime).
        
        Args:
            session_id: Session identifier
            context: Execution context
        
        Returns:
            Session state dictionary, or None if not found
        """
        if context.state_surface:
            return await context.state_surface.get_session_state(session_id, context.tenant_id)
        return None
    
    async def request_contribution(
        self,
        agent_type: str,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """
        Request a bounded contribution from another agent (Policy-Governed).
        
        This is NOT orchestration - it's reasoning collaboration.
        Returns non-executing artifacts only (proposals, blueprints).
        
        Flow:
        1. Agent emits contribution_request
        2. Runtime asks Smart City primitives: Is this allowed?
        3. If allowed, Runtime routes to target agent
        4. Target agent returns non-executing artifact
        5. No side effects, no execution, no commits
        
        Args:
            agent_type: Type of agent to request contribution from
            request: Contribution request (purpose, constraints, data)
            context: Execution context
        
        Returns:
            Non-executing artifact (proposal, blueprint, ranked options), or None if failed
        """
        if not self.collaboration_router:
            self.logger.warning("Collaboration router not available")
            return None
        
        # Create contribution request
        contribution_request = ContributionRequest.create(
            caller_agent_id=self.agent_id,
            target_agent_type=agent_type,
            purpose=request.get("purpose", "collaboration"),
            request_data=request.get("data", {}),
            constraints=request.get("constraints", {}),
            session_id=context.session_id,
            execution_id=context.execution_id
        )
        
        # Route via collaboration router (validated by Smart City)
        # Note: In full implementation, this would go through Runtime
        # For MVP: Direct routing
        # Get agent registry from context if available
        agent_registry = None
        if hasattr(context, "agent_registry"):
            agent_registry = context.agent_registry
        elif hasattr(context, "state_surface") and hasattr(context.state_surface, "agent_registry"):
            agent_registry = context.state_surface.agent_registry
        
        response = await self.collaboration_router.route_contribution_request(
            contribution_request,
            agent_registry=agent_registry
        )
        
        if response:
            return {
                "artifact_type": response.artifact_type,
                "artifact": response.artifact,
                "confidence": response.confidence,
                "notes": response.notes
            }
        
        return None
    
    async def process_contribution_request(
        self,
        request: ContributionRequest
    ) -> ContributionResponse:
        """
        Process a contribution request from another agent.
        
        This is called by CollaborationRouter when routing requests.
        
        Args:
            request: Contribution request
        
        Returns:
            Contribution response with non-executing artifact
        """
        # Default implementation: Return empty artifact
        # Subclasses should override this
        return ContributionResponse(
            request_id=request.request_id,
            target_agent_id=self.agent_id,
            artifact_type="proposal",
            artifact={},
            confidence=0.0,
            notes="Not implemented"
        )
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate agent output (ensures "No Commit" rule).
        
        Args:
            output: Agent output dictionary
        
        Returns:
            True if output is valid (non-executing), False otherwise
        """
        # Check for forbidden output types
        forbidden_keys = ["state_mutation", "service_invocation", "execution_commit"]
        for key in forbidden_keys:
            if key in output:
                self.logger.error(f"Agent output contains forbidden key: {key}")
                return False
        
        # Check for allowed output types
        allowed_types = ["proposal", "blueprint", "ranked_options", "suggested_intents"]
        artifact_type = output.get("artifact_type", "")
        
        if artifact_type not in allowed_types:
            # Execution plan is only allowed if Solution-owned
            if artifact_type == "execution_plan" and output.get("solution_owned", False):
                return True
            if artifact_type:
                self.logger.warning(f"Unknown artifact type: {artifact_type}")
        
        return True
