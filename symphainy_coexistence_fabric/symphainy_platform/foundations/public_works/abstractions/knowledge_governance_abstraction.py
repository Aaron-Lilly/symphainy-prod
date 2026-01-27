"""
Knowledge Governance Abstraction - Pure Infrastructure (Layer 1)

Implements knowledge governance operations using ArangoDB and metadata adapters.
Returns raw data only - no business logic.

WHAT (Infrastructure Role): I provide knowledge governance storage services
HOW (Infrastructure Implementation): I use ArangoDB adapter and metadata adapter

NOTE: This is PURE INFRASTRUCTURE - no business logic.
Business logic (policy validation, metadata enhancement, status filtering) belongs in Platform SDK.
Domain logic (quality metrics, semantic tags) belongs in Realm services (flagged for future phases).
"""

from typing import Dict, Any, Optional, List, Any as AdapterType
from utilities import get_logger
from ..protocols.knowledge_governance_protocol import KnowledgeGovernanceProtocol, PolicyType


class KnowledgeGovernanceAbstraction(KnowledgeGovernanceProtocol):
    """
    Knowledge governance abstraction - pure infrastructure.
    
    Returns raw data only (Dict[str, Any] or List[Dict[str, Any]]), not business objects.
    Business logic (policy validation, metadata enhancement, status filtering) belongs in Platform SDK.
    Domain logic (quality metrics, semantic tags) belongs in Realm services.
    """
    
    def __init__(
        self,
        arango_adapter: AdapterType,
        metadata_adapter: Optional[AdapterType] = None
    ):
        """
        Initialize Knowledge Governance abstraction.
        
        Args:
            arango_adapter: ArangoDB adapter for governance data (Layer 0)
            metadata_adapter: Optional metadata adapter (Layer 0)
        """
        self.arango = arango_adapter
        self.metadata = metadata_adapter
        self.logger = get_logger(self.__class__.__name__)
        
        # Collection names for ArangoDB
        self.policies_collection = "governance_policies"
        self.assets_collection = "knowledge_assets"
        self.metadata_collection = "asset_metadata"
        self.relationships_collection = "policy_asset_relationships"
        
        self.logger.info("Knowledge Governance Abstraction initialized (pure infrastructure)")
    
    # ============================================================================
    # POLICY MANAGEMENT (Pure Infrastructure)
    # ============================================================================
    
    async def create_governance_policy(
        self,
        policy_name: str,
        policy_type: PolicyType,
        policy_data: Dict[str, Any],
        description: Optional[str] = None
    ) -> str:
        """
        Create governance policy - pure infrastructure only.
        
        Stores policy in ArangoDB (and optionally metadata adapter).
        Returns raw policy ID from adapter.
        
        NOTE: Policy validation is business logic and should be done in Platform SDK
        before calling this method.
        
        Args:
            policy_name: Name of the policy
            policy_type: Type of policy
            policy_data: Policy configuration data (should already be validated)
            description: Optional policy description
        
        Returns:
            Policy ID (from adapter)
        """
        try:
            # Generate policy ID (Platform SDK should provide, but fallback for infrastructure)
            policy_id = policy_data.get("policy_id") or policy_data.get("_key")
            if not policy_id:
                # Infrastructure fallback - Platform SDK should provide policy_id
                import uuid
                policy_id = str(uuid.uuid4())
            
            # Prepare policy document for ArangoDB (pass through all fields, no business logic)
            arango_policy = {
                "_key": policy_id,
                "name": policy_name,
                "type": policy_type.value,
                "data": policy_data,
                "description": description,
                **policy_data  # Pass through all fields
            }
            
            # Store in ArangoDB (pure infrastructure)
            result = await self.arango.create_document(
                self.policies_collection,
                arango_policy
            )
            
            # Optionally store in metadata adapter if available
            if self.metadata and hasattr(self.metadata, 'create_governance_policy'):
                try:
                    await self.metadata.create_governance_policy(policy_name, policy_data)
                except Exception as e:
                    self.logger.warning(f"Policy created in ArangoDB but metadata adapter failed: {e}")
            
            self.logger.info(f"Governance policy created: {policy_id}")
            
            # Return policy ID
            return policy_id
            
        except Exception as e:
            self.logger.error(f"Failed to create governance policy: {e}", exc_info=True)
            raise
    
    async def update_governance_policy(
        self,
        policy_id: str,
        policy_data: Dict[str, Any]
    ) -> bool:
        """
        Update governance policy - pure infrastructure only.
        
        Updates policy in ArangoDB (and optionally metadata adapter).
        Returns raw success status.
        
        Args:
            policy_id: ID of the policy to update
            policy_data: Updated policy data
        
        Returns:
            bool: True if successful
        """
        try:
            # Update in ArangoDB (pure infrastructure)
            arango_success = await self.arango.update_document(
                self.policies_collection,
                policy_id,
                policy_data
            )
            
            # Optionally update in metadata adapter if available
            metadata_success = True
            if self.metadata and hasattr(self.metadata, 'update_asset_metadata'):
                try:
                    metadata_success = await self.metadata.update_asset_metadata(
                        policy_id,
                        policy_data
                    )
                except Exception as e:
                    self.logger.warning(f"Policy updated in ArangoDB but metadata adapter failed: {e}")
            
            success = arango_success and metadata_success
            
            if success:
                self.logger.info(f"Governance policy updated: {policy_id}")
            else:
                self.logger.warning(f"Partial policy update: {policy_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update governance policy {policy_id}: {e}", exc_info=True)
            raise
    
    async def delete_governance_policy(self, policy_id: str) -> bool:
        """
        Delete governance policy - pure infrastructure only.
        
        Deletes policy from ArangoDB (and optionally metadata adapter).
        Returns raw success status.
        
        Args:
            policy_id: ID of the policy to delete
        
        Returns:
            bool: True if successful
        """
        try:
            # Delete from ArangoDB (pure infrastructure)
            arango_success = await self.arango.delete_document(
                self.policies_collection,
                policy_id
            )
            
            # Optionally delete from metadata adapter if available
            metadata_success = True
            if self.metadata and hasattr(self.metadata, 'delete_asset_metadata'):
                try:
                    metadata_success = await self.metadata.delete_asset_metadata(policy_id)
                except Exception as e:
                    self.logger.warning(f"Policy deleted from ArangoDB but metadata adapter failed: {e}")
            
            success = arango_success and metadata_success
            
            if success:
                self.logger.info(f"Governance policy deleted: {policy_id}")
            else:
                self.logger.warning(f"Partial policy deletion: {policy_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete governance policy {policy_id}: {e}", exc_info=True)
            raise
    
    async def get_governance_policies(
        self,
        policy_type: Optional[PolicyType] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get governance policies - pure infrastructure only.
        
        Retrieves policies from ArangoDB.
        Returns raw data from adapter.
        
        NOTE: Status filtering is business logic and should be done in Platform SDK
        after calling this method.
        
        Args:
            policy_type: Optional policy type filter (can be applied in query)
            status: Optional status filter (can be applied in query)
        
        Returns:
            List of raw policy dicts from ArangoDB
        """
        try:
            # Build filter conditions
            filter_conditions = {}
            if policy_type:
                filter_conditions["type"] = policy_type.value
            if status:
                filter_conditions["status"] = status
            
            # Get policies from ArangoDB (pure infrastructure)
            if filter_conditions:
                result = await self.arango.find_documents(
                    self.policies_collection,
                    filter_conditions=filter_conditions
                )
            else:
                # Get all policies
                result = await self.arango.find_documents(
                    self.policies_collection,
                    filter_conditions={}
                )
            
            self.logger.debug(f"Governance policies retrieved: {len(result)} policies")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get governance policies: {e}", exc_info=True)
            raise
    
    # ============================================================================
    # POLICY APPLICATION (Pure Infrastructure)
    # ============================================================================
    
    async def apply_governance_policy(
        self,
        asset_id: str,
        policy_id: str
    ) -> bool:
        """
        Apply governance policy to asset - pure infrastructure only.
        
        Creates policy-asset relationship in ArangoDB.
        Returns raw success status.
        
        Args:
            asset_id: ID of the knowledge asset
            policy_id: ID of the governance policy
        
        Returns:
            bool: True if successful
        """
        try:
            # Create policy-asset relationship in ArangoDB (pure infrastructure)
            relationship = {
                "_key": f"{asset_id}_{policy_id}",
                "asset_id": asset_id,
                "policy_id": policy_id,
                "status": "active"
            }
            
            result = await self.arango.create_document(
                self.relationships_collection,
                relationship
            )
            
            # Optionally create in metadata adapter if available
            if self.metadata and hasattr(self.metadata, 'apply_governance_policy'):
                try:
                    await self.metadata.apply_governance_policy(asset_id, policy_id)
                except Exception as e:
                    self.logger.warning(f"Policy relationship created in ArangoDB but metadata adapter failed: {e}")
            
            success = result is not None
            
            if success:
                self.logger.info(f"Governance policy applied: {policy_id} → {asset_id}")
            else:
                self.logger.error(f"Failed to apply governance policy: {policy_id} → {asset_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to apply governance policy: {e}", exc_info=True)
            raise
    
    async def remove_governance_policy(
        self,
        asset_id: str,
        policy_id: str
    ) -> bool:
        """
        Remove governance policy from asset - pure infrastructure only.
        
        Removes policy-asset relationship from ArangoDB.
        Returns raw success status.
        
        Args:
            asset_id: ID of the knowledge asset
            policy_id: ID of the governance policy
        
        Returns:
            bool: True if successful
        """
        try:
            # Remove relationship from ArangoDB (pure infrastructure)
            relationship_key = f"{asset_id}_{policy_id}"
            result = await self.arango.delete_document(
                self.relationships_collection,
                relationship_key
            )
            
            # Optionally remove from metadata adapter if available
            if self.metadata and hasattr(self.metadata, 'delete_asset_metadata'):
                try:
                    await self.metadata.delete_asset_metadata(asset_id)
                except Exception as e:
                    self.logger.warning(f"Policy relationship removed from ArangoDB but metadata adapter failed: {e}")
            
            if result:
                self.logger.info(f"Governance policy removed: {policy_id} → {asset_id}")
            else:
                self.logger.warning(f"Failed to remove governance policy: {policy_id} → {asset_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to remove governance policy: {e}", exc_info=True)
            raise
    
    async def get_asset_policies(self, asset_id: str) -> List[Dict[str, Any]]:
        """
        Get asset policies - pure infrastructure only.
        
        Retrieves policy-asset relationships from ArangoDB.
        Returns raw data from adapter.
        
        Args:
            asset_id: ID of the knowledge asset
        
        Returns:
            List of raw relationship dicts from ArangoDB
        """
        try:
            # Get relationships from ArangoDB (pure infrastructure)
            relationships = await self.arango.find_documents(
                self.relationships_collection,
                filter_conditions={"asset_id": asset_id}
            )
            
            self.logger.debug(f"Asset policies retrieved: {len(relationships)} policies")
            
            # Return raw data
            return relationships
            
        except Exception as e:
            self.logger.error(f"Failed to get asset policies {asset_id}: {e}", exc_info=True)
            raise
    
    # ============================================================================
    # ASSET METADATA MANAGEMENT (Pure Infrastructure)
    # ============================================================================
    
    async def create_asset_metadata(
        self,
        asset_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Create asset metadata - pure infrastructure only.
        
        Stores metadata in ArangoDB (and optionally metadata adapter).
        Returns raw success status.
        
        Args:
            asset_id: ID of the knowledge asset
            metadata: Metadata dictionary
        
        Returns:
            bool: True if successful
        """
        try:
            # Prepare metadata document for ArangoDB (pass through all fields, no business logic)
            arango_metadata = {
                "_key": asset_id,
                **metadata
            }
            
            # Store in ArangoDB (pure infrastructure)
            result = await self.arango.create_document(
                self.metadata_collection,
                arango_metadata
            )
            
            # Optionally store in metadata adapter if available
            if self.metadata and hasattr(self.metadata, 'create_asset_metadata'):
                try:
                    await self.metadata.create_asset_metadata(asset_id, metadata)
                except Exception as e:
                    self.logger.warning(f"Asset metadata created in ArangoDB but metadata adapter failed: {e}")
            
            success = result is not None
            
            if success:
                self.logger.info(f"Asset metadata created: {asset_id}")
            else:
                self.logger.error(f"Failed to create asset metadata: {asset_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to create asset metadata {asset_id}: {e}", exc_info=True)
            raise
    
    async def update_asset_metadata(
        self,
        asset_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update asset metadata - pure infrastructure only.
        
        Updates metadata in ArangoDB (and optionally metadata adapter).
        Returns raw success status.
        
        Args:
            asset_id: ID of the knowledge asset
            metadata: Updated metadata dictionary
        
        Returns:
            bool: True if successful
        """
        try:
            # Update in ArangoDB (pure infrastructure)
            arango_success = await self.arango.update_document(
                self.metadata_collection,
                asset_id,
                metadata
            )
            
            # Optionally update in metadata adapter if available
            metadata_success = True
            if self.metadata and hasattr(self.metadata, 'update_asset_metadata'):
                try:
                    metadata_success = await self.metadata.update_asset_metadata(asset_id, metadata)
                except Exception as e:
                    self.logger.warning(f"Asset metadata updated in ArangoDB but metadata adapter failed: {e}")
            
            success = arango_success and metadata_success
            
            if success:
                self.logger.info(f"Asset metadata updated: {asset_id}")
            else:
                self.logger.warning(f"Partial metadata update: {asset_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update asset metadata {asset_id}: {e}", exc_info=True)
            raise
    
    async def get_asset_metadata(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get asset metadata - pure infrastructure only.
        
        Retrieves metadata from ArangoDB (with metadata adapter fallback).
        Returns raw data from adapter.
        
        Args:
            asset_id: ID of the knowledge asset
        
        Returns:
            Raw metadata dict from ArangoDB or None if not found
        """
        try:
            # Try ArangoDB first (primary storage)
            result = await self.arango.get_document(
                self.metadata_collection,
                asset_id
            )
            
            # Fallback to metadata adapter if ArangoDB doesn't have it
            if not result and self.metadata and hasattr(self.metadata, 'get_asset_metadata'):
                try:
                    result = await self.metadata.get_asset_metadata(asset_id)
                except Exception as e:
                    self.logger.debug(f"Metadata adapter not available: {e}")
            
            if result:
                self.logger.debug(f"Asset metadata retrieved: {asset_id}")
            else:
                self.logger.warning(f"Asset metadata not found: {asset_id}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get asset metadata {asset_id}: {e}", exc_info=True)
            raise
    
    # ============================================================================
    # DOMAIN LOGIC METHODS (Flagged for Future Phases)
    # ============================================================================
    # NOTE: These methods contain domain logic (Content/Insights Pillar) and should
    # be moved to Realm services in future phases. They are kept here for backward
    # compatibility but should not be used by Smart City roles.
    # ============================================================================
    
    # ⏸️ FLAGGED FOR FUTURE PHASES:
    # - get_quality_metrics() - Domain logic (may be data quality analysis)
    # - add_semantic_tags() - Domain logic (Insights Pillar)
    # - get_semantic_tags() - Domain logic (Insights Pillar)
    # - search_by_semantic_tags() - Domain logic (Insights Pillar)
