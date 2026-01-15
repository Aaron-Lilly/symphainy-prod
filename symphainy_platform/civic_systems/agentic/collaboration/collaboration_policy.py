"""
Agent Collaboration Policy - Policy-Governed Agent Interaction Rules
"""

from typing import Dict, Any, List, Optional
from utilities import get_logger


class AgentCollaborationPolicy:
    """
    Agent collaboration policy (from Curator/Policy Registry).
    
    Defines who can talk to whom, for what purpose, with what constraints.
    """
    
    def __init__(self, policy_data: Dict[str, Any]):
        """
        Initialize collaboration policy.
        
        Args:
            policy_data: Policy data from Curator/Policy Registry
        """
        self.policy_data = policy_data
        self.logger = get_logger(self.__class__.__name__)
    
    def can_request(
        self,
        caller_agent_type: str,
        target_agent_type: str,
        purpose: str
    ) -> bool:
        """
        Check if caller agent can request contribution from target agent.
        
        Args:
            caller_agent_type: Type of calling agent
            target_agent_type: Type of target agent
            purpose: Purpose of the request
        
        Returns:
            True if request is allowed, False otherwise
        """
        # Get policy for caller agent
        caller_policy = self.policy_data.get("agent_collaboration", {}).get(caller_agent_type, {})
        
        # Check if caller can request this type of contribution
        may_request = caller_policy.get("may_request", [])
        if target_agent_type not in may_request and purpose not in may_request:
            return False
        
        # Check constraints
        constraints = caller_policy.get("constraints", {})
        max_depth = constraints.get("max_depth", 2)
        no_execution = constraints.get("no_execution", True)
        output_type = constraints.get("output_type", "proposal_only")
        
        # MVP: Simple allow (for MVP showcase)
        # Full: Evaluate all constraints
        return True
    
    def get_constraints(
        self,
        caller_agent_type: str
    ) -> Dict[str, Any]:
        """
        Get constraints for caller agent.
        
        Args:
            caller_agent_type: Type of calling agent
        
        Returns:
            Constraints dictionary
        """
        caller_policy = self.policy_data.get("agent_collaboration", {}).get(caller_agent_type, {})
        return caller_policy.get("constraints", {})
    
    @classmethod
    def from_curator(
        cls,
        curator_data: Dict[str, Any]
    ) -> "AgentCollaborationPolicy":
        """
        Create collaboration policy from Curator data.
        
        Args:
            curator_data: Policy data from Curator
        
        Returns:
            AgentCollaborationPolicy instance
        """
        return cls(policy_data=curator_data)
