"""
Knowledge Governance Protocol - Abstraction Contract (Layer 2)

Defines the contract for knowledge governance operations.
Enables swappability between ArangoDB, Supabase, etc.

WHAT (Infrastructure Role): I define the contract for knowledge governance operations
HOW (Infrastructure Implementation): I specify the interface for governance and metadata management

NOTE: Only includes governance-related methods.
Domain logic methods (quality metrics, semantic tags) are flagged for future phases.
"""

from typing import Protocol, Dict, Any, List, Optional
from enum import Enum


class PolicyType(Enum):
    """Policy type enumeration."""
    ACCESS_CONTROL = "access_control"
    DATA_QUALITY = "data_quality"
    RETENTION = "retention"
    CLASSIFICATION = "classification"
    COMPLIANCE = "compliance"


class KnowledgeGovernanceProtocol(Protocol):
    """Protocol for knowledge governance operations (governance methods only)."""
    
    # ============================================================================
    # POLICY MANAGEMENT (Governance)
    # ============================================================================
    
    async def create_governance_policy(
        self,
        policy_name: str,
        policy_type: PolicyType,
        policy_data: Dict[str, Any],
        description: Optional[str] = None
    ) -> str:
        """
        Create a governance policy.
        
        Args:
            policy_name: Name of the policy
            policy_type: Type of policy
            policy_data: Policy configuration data
            description: Optional policy description
        
        Returns:
            Policy ID
        """
        ...
    
    async def update_governance_policy(
        self,
        policy_id: str,
        policy_data: Dict[str, Any]
    ) -> bool:
        """
        Update a governance policy.
        
        Args:
            policy_id: ID of the policy to update
            policy_data: Updated policy data
        
        Returns:
            Success status
        """
        ...
    
    async def delete_governance_policy(self, policy_id: str) -> bool:
        """
        Delete a governance policy.
        
        Args:
            policy_id: ID of the policy to delete
        
        Returns:
            Success status
        """
        ...
    
    async def get_governance_policies(
        self,
        policy_type: Optional[PolicyType] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get governance policies.
        
        Args:
            policy_type: Optional policy type filter
            status: Optional status filter
        
        Returns:
            List of governance policies
        """
        ...
    
    # ============================================================================
    # POLICY APPLICATION (Governance)
    # ============================================================================
    
    async def apply_governance_policy(
        self,
        asset_id: str,
        policy_id: str
    ) -> bool:
        """
        Apply a governance policy to a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            policy_id: ID of the governance policy
        
        Returns:
            Success status
        """
        ...
    
    async def remove_governance_policy(
        self,
        asset_id: str,
        policy_id: str
    ) -> bool:
        """
        Remove a governance policy from a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            policy_id: ID of the governance policy
        
        Returns:
            Success status
        """
        ...
    
    async def get_asset_policies(self, asset_id: str) -> List[Dict[str, Any]]:
        """
        Get policies applied to a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
        
        Returns:
            List of applied policies
        """
        ...
    
    # ============================================================================
    # ASSET METADATA MANAGEMENT (Governance)
    # ============================================================================
    
    async def create_asset_metadata(
        self,
        asset_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Create metadata for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            metadata: Metadata dictionary
        
        Returns:
            Success status
        """
        ...
    
    async def update_asset_metadata(
        self,
        asset_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update metadata for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            metadata: Updated metadata dictionary
        
        Returns:
            Success status
        """
        ...
    
    async def get_asset_metadata(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
        
        Returns:
            Metadata dictionary or None if not found
        """
        ...
