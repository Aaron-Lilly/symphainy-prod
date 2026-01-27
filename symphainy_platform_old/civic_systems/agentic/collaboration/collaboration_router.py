"""
Collaboration Router - Routes Agent Collaboration Requests (Smart City Validated)
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from .contribution_request import ContributionRequest, ContributionResponse
from .collaboration_policy import AgentCollaborationPolicy


class CollaborationRouter:
    """
    Routes agent collaboration requests (validated by Smart City).
    
    Flow:
    1. Agent emits contribution_request
    2. Router asks Smart City primitives: Is this allowed?
    3. If allowed, Router routes to target agent
    4. Target agent returns non-executing artifact
    5. No side effects, no execution, no commits
    """
    
    def __init__(
        self,
        collaboration_policy: Optional[AgentCollaborationPolicy] = None,
        smart_city_primitives: Optional[Any] = None  # Smart City primitives for validation
    ):
        """
        Initialize collaboration router.
        
        Args:
            collaboration_policy: Agent collaboration policy
            smart_city_primitives: Smart City primitives for validation
        """
        self.collaboration_policy = collaboration_policy
        self.smart_city_primitives = smart_city_primitives
        self.logger = get_logger(self.__class__.__name__)
    
    async def route_contribution_request(
        self,
        request: ContributionRequest,
        agent_registry: Any  # AgentRegistry instance
    ) -> Optional[ContributionResponse]:
        """
        Route contribution request to target agent (validated by Smart City).
        
        Args:
            request: Contribution request
            agent_registry: Agent registry to find target agent
        
        Returns:
            Contribution response, or None if routing failed
        """
        try:
            # 1. Validate via collaboration policy
            if self.collaboration_policy:
                allowed = self.collaboration_policy.can_request(
                    caller_agent_type=request.caller_agent_id.split(":")[0],  # Extract type
                    target_agent_type=request.target_agent_type,
                    purpose=request.purpose
                )
                if not allowed:
                    self.logger.warning(f"Collaboration request denied by policy: {request.request_id}")
                    return None
            
            # 2. Validate via Smart City primitives (if available)
            if self.smart_city_primitives:
                # Validate collaboration request via Smart City primitives
                # In full implementation, this would check:
                # - Agent collaboration policies
                # - Tenant permissions
                # - Resource access rules
                # For MVP: Basic validation (allow if primitives are available)
                try:
                    # MVP: Basic validation - check if primitives are available
                    # Full: Would call specific Smart City primitive methods
                    # Example: await self.smart_city_primitives.validate_agent_collaboration(...)
                    if hasattr(self.smart_city_primitives, "validate_agent_collaboration"):
                        validation_result = await self.smart_city_primitives.validate_agent_collaboration(
                            caller_agent_id=request.caller_agent_id,
                            target_agent_type=request.target_agent_type,
                            purpose=request.purpose
                        )
                        if not validation_result:
                            self.logger.warning(f"Smart City validation denied collaboration: {request.request_id}")
                            return None
                    # MVP: If validation method doesn't exist, allow (for MVP showcase)
                except Exception as e:
                    self.logger.warning(f"Smart City validation failed (non-fatal for MVP): {e}")
                    # MVP: Allow on validation error (for MVP showcase)
                    # Full: Would deny on validation error (fail secure)
            
            # 3. Find target agent
            target_agent = agent_registry.get_agent_by_type(request.target_agent_type)
            if not target_agent:
                self.logger.warning(f"Target agent not found: {request.target_agent_type}")
                return None
            
            # 4. Route request to target agent
            # Target agent processes request and returns non-executing artifact
            response = await target_agent.process_contribution_request(request)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to route contribution request: {e}", exc_info=True)
            return None
