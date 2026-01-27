"""
Semantic Profile Registry - Versioned and Scoped Semantic Interpretations

Enabling service for managing semantic profiles.

WHAT (Enabling Service Role): I manage versioned semantic profiles
HOW (Enabling Service Implementation): I store and retrieve profiles from registry

CTO Principle: Semantic profiles are versioned, scoped, contextual
Platform Enhancement: Map semantic profiles to AgentPosture
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class SemanticProfile:
    """
    Semantic Profile - Versioned, scoped semantic interpretation.
    
    CTO Principle: Semantic meaning is contextual and versioned
    Platform Enhancement: Links to AgentPosture for behavioral tuning
    """
    profile_name: str
    model_name: str
    prompt_template: Optional[str] = None
    semantic_version: str = "1.0.0"  # Platform-controlled
    agent_posture_config: Optional[Dict[str, Any]] = None  # Platform enhancement
    compliance_mode: Optional[str] = None
    created_at: Optional[str] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}
        if self.agent_posture_config is None:
            self.agent_posture_config = {}


class SemanticProfileRegistry:
    """
    Registry for semantic profiles.
    
    CTO Principle: Profiles are versioned and scoped
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Semantic Profile Registry.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.public_works = public_works
        self.registry_abstraction = None
        if public_works:
            self.registry_abstraction = getattr(public_works, 'registry_abstraction', None)
        
        # Default profiles (built-in)
        self._default_profiles = {
            "default": SemanticProfile(
                profile_name="default",
                model_name="text-embedding-ada-002",
                semantic_version="1.0.0",
                is_active=True
            ),
            "insurance": SemanticProfile(
                profile_name="insurance",
                model_name="text-embedding-ada-002",
                semantic_version="1.0.0",
                prompt_template="Extract insurance-specific semantic signals: policies, claims, coverage, premiums.",
                is_active=True
            ),
            "financial": SemanticProfile(
                profile_name="financial",
                model_name="text-embedding-ada-002",
                semantic_version="1.0.0",
                prompt_template="Extract financial-specific semantic signals: transactions, accounts, balances, statements.",
                is_active=True
            )
        }
    
    async def get_profile(
        self,
        profile_name: str,
        version: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Optional[SemanticProfile]:
        """
        Get semantic profile (latest version if version not specified).
        
        Args:
            profile_name: Profile name
            version: Optional version (default: latest)
            tenant_id: Optional tenant ID (for tenant-scoped profiles)
        
        Returns:
            SemanticProfile or None if not found
        """
        # Check default profiles first
        if profile_name in self._default_profiles:
            return self._default_profiles[profile_name]
        
        # Check registry if available
        if self.registry_abstraction:
            try:
                # Query registry for profile
                profile_data = await self.registry_abstraction.get_registry_entry(
                    entry_type="semantic_profile",
                    entry_key=profile_name,
                    version=version,
                    tenant_id=tenant_id
                )
                
                if profile_data:
                    return SemanticProfile(**profile_data)
            except Exception as e:
                # Log but don't fail
                from utilities import get_logger
                logger = get_logger(self.__class__.__name__)
                logger.debug(f"Failed to get profile from registry: {e}")
        
        return None
    
    async def register_profile(
        self,
        profile: SemanticProfile,
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Register new semantic profile.
        
        Args:
            profile: SemanticProfile to register
            tenant_id: Optional tenant ID (for tenant-scoped profiles)
        
        Returns:
            True if successful
        """
        # Store in registry if available
        if self.registry_abstraction:
            try:
                profile_dict = asdict(profile)
                success = await self.registry_abstraction.register_entry(
                    entry_type="semantic_profile",
                    entry_key=profile.profile_name,
                    entry_data=profile_dict,
                    version=profile.semantic_version,
                    tenant_id=tenant_id
                )
                return success
            except Exception as e:
                from utilities import get_logger
                logger = get_logger(self.__class__.__name__)
                logger.error(f"Failed to register profile: {e}", exc_info=True)
                return False
        
        return False
    
    async def list_profiles(
        self,
        tenant_id: Optional[str] = None,
        active_only: bool = True
    ) -> List[SemanticProfile]:
        """
        List all profiles for tenant.
        
        Args:
            tenant_id: Optional tenant ID
            active_only: If True, only return active profiles
        
        Returns:
            List of SemanticProfile objects
        """
        profiles = []
        
        # Add default profiles
        for profile in self._default_profiles.values():
            if not active_only or profile.is_active:
                profiles.append(profile)
        
        # Add registry profiles if available
        if self.registry_abstraction:
            try:
                registry_profiles = await self.registry_abstraction.list_registry_entries(
                    entry_type="semantic_profile",
                    tenant_id=tenant_id
                )
                
                for profile_data in registry_profiles:
                    profile = SemanticProfile(**profile_data)
                    if not active_only or profile.is_active:
                        profiles.append(profile)
            except Exception as e:
                from utilities import get_logger
                logger = get_logger(self.__class__.__name__)
                logger.debug(f"Failed to list profiles from registry: {e}")
        
        return profiles
