"""
Post Office Primitives - Event Routing Validation and Ordering Checks

Primitives for Post Office policy decisions (used by Runtime only).

WHAT (Smart City Role): I validate event routing and check ordering
HOW (Primitive Implementation): I provide pure functions, no side effects, deterministic

⚠️ CRITICAL: Primitives are used by Runtime only.
SDKs prepare execution contracts. Primitives validate them.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger


class RoutingPolicyStore:
    """
    Routing policy store interface (abstract).
    
    In MVP: Simple in-memory or Redis-based routing rules
    In full: ArangoDB graph-based routing policies
    """
    
    async def get_routing_policies(
        self,
        tenant_id: str,
        event_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get routing policies for tenant and event type.
        
        Args:
            tenant_id: Tenant identifier
            event_type: Event type
        
        Returns:
            List of routing policy dictionaries
        """
        # MVP: Return empty list (no routing policies in MVP)
        # Full: Query ArangoDB graph for routing policies
        return []
    
    async def validate_routing(
        self,
        policy: Dict[str, Any],
        event_type: str,
        tenant_id: str,
        target_stream: str
    ) -> bool:
        """
        Validate routing against policy.
        
        Args:
            policy: Routing policy dictionary
            event_type: Event type
            tenant_id: Tenant identifier
            target_stream: Target stream name
        
        Returns:
            True if routing is allowed, False otherwise
        """
        # MVP: Always allow (for MVP showcase)
        # Full: Evaluate routing policy rules
        return True


class PostOfficePrimitives:
    """
    Post Office Primitives - Policy Validation
    
    Pure functions for event routing validation and ordering checks.
    Used by Runtime only.
    """
    
    def __init__(self, routing_policy_store: Optional[RoutingPolicyStore] = None):
        """
        Initialize Post Office Primitives.
        
        Args:
            routing_policy_store: Optional routing policy store (for MVP, can be None)
        """
        self.routing_policy_store = routing_policy_store or RoutingPolicyStore()
        self.logger = get_logger(self.__class__.__name__)
    
    @staticmethod
    async def validate_event_routing(
        event_type: str,
        tenant_id: str,
        target_stream: str,
        execution_contract: Dict[str, Any],
        routing_policy_store: RoutingPolicyStore
    ) -> bool:
        """
        Validate event routing (Primitive - pure function, no side effects).
        
        This is called by Runtime to validate the execution contract
        prepared by Post Office SDK.
        
        Args:
            event_type: Event type identifier
            tenant_id: Tenant identifier
            target_stream: Target stream name
            execution_contract: Execution contract prepared by SDK
            routing_policy_store: Routing policy store instance
        
        Returns:
            True if routing is valid, False otherwise
        """
        try:
            # 1. Check required fields
            if execution_contract.get("action") != "route_event":
                return False
            
            # 2. Validate routing policies
            routing_policies = execution_contract.get("routing_policies", [])
            
            # If SDK prepared policies, use those
            if not routing_policies:
                routing_policies = await routing_policy_store.get_routing_policies(tenant_id, event_type)
            
            # Evaluate routing policies
            for policy in routing_policies:
                allowed = await routing_policy_store.validate_routing(
                    policy, event_type, tenant_id, target_stream
                )
                if not allowed:
                    return False
            
            # MVP: Default allow (for MVP showcase)
            return True
            
        except Exception as e:
            logger = get_logger("PostOfficePrimitives")
            logger.error(f"Event routing validation failed: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def check_event_order(
        event_type: str,
        tenant_id: str,
        previous_event_id: Optional[str],
        current_event_id: str,
        execution_contract: Dict[str, Any]
    ) -> bool:
        """
        Check event ordering (Primitive - pure function, no side effects).
        
        This validates that events are processed in the correct order.
        
        Args:
            event_type: Event type identifier
            tenant_id: Tenant identifier
            previous_event_id: Previous event ID (if any)
            current_event_id: Current event ID
            execution_contract: Execution contract prepared by SDK
        
        Returns:
            True if ordering is valid, False otherwise
        """
        try:
            # MVP: Simple ordering check (for MVP showcase)
            # Full: Sophisticated ordering validation with sequence numbers
            
            # If no previous event, ordering is valid
            if not previous_event_id:
                return True
            
            # Compare event IDs (Redis Stream IDs are lexicographically ordered)
            # In MVP: Simple comparison
            # Full: Use sequence numbers or timestamps from execution contract
            
            # MVP: Default allow (for MVP showcase)
            return True
            
        except Exception as e:
            logger = get_logger("PostOfficePrimitives")
            logger.error(f"Event ordering check failed: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def validate_stream_subscription(
        stream_name: str,
        tenant_id: str,
        execution_contract: Dict[str, Any],
        routing_policy_store: RoutingPolicyStore
    ) -> bool:
        """
        Validate stream subscription (Primitive).
        
        Args:
            stream_name: Stream name
            tenant_id: Tenant identifier
            execution_contract: Execution contract prepared by SDK
            routing_policy_store: Routing policy store instance
        
        Returns:
            True if subscription is valid, False otherwise
        """
        try:
            # 1. Check required fields
            if execution_contract.get("action") != "subscribe_to_stream":
                return False
            
            # 2. Validate subscription policies
            subscription_policies = execution_contract.get("subscription_policies", [])
            
            # Evaluate subscription policies
            for policy in subscription_policies:
                # MVP: Simple allow-all (for MVP showcase)
                # Full: Evaluate policy rules (e.g., check subscription limits, event type filters, etc.)
                # For MVP, we allow all policies - in full implementation, this would evaluate
                # policy rules against subscription limits and filters
                if not policy:
                    continue  # Skip empty policies
                # MVP: Allow all policies (no validation)
                # Full: Would validate policy rules here (e.g., max_subscriptions, event_type_filters, etc.)
            
            # 3. Validate stream access (tenant isolation)
            if not stream_name.startswith(f"events:{tenant_id}:"):
                # Allow if stream is tenant-scoped
                return False
            
            # MVP: Default allow (for MVP showcase)
            return True
            
        except Exception as e:
            logger = get_logger("PostOfficePrimitives")
            logger.error(f"Stream subscription validation failed: {e}", exc_info=True)
            return False
