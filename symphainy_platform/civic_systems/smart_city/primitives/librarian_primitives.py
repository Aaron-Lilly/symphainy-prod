"""
Librarian Primitives - Policy Decisions for Knowledge Discovery

Primitives for Librarian policy decisions (used by Runtime only).
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from dataclasses import dataclass

from utilities import get_logger


@dataclass
class SchemaAccessValidation:
    """Schema access validation result."""
    is_allowed: bool
    schema_id: str
    reason: Optional[str] = None


@dataclass
class KnowledgePermissionCheck:
    """Knowledge permission check result."""
    is_allowed: bool
    query: str
    reason: Optional[str] = None


class LibrarianPrimitives:
    """
    Librarian Primitives - Policy Decisions
    
    Makes policy decisions for knowledge discovery.
    """
    
    def __init__(self, policy_store: Optional[Any] = None):
        self.policy_store = policy_store
        self.logger = get_logger(self.__class__.__name__)
    
    async def validate_schema_access(
        self,
        schema_id: str,
        user_id: str,
        tenant_id: str,
        action: str
    ) -> SchemaAccessValidation:
        """Validate schema access (policy decision)."""
        # MVP: Basic validation
        if not schema_id:
            return SchemaAccessValidation(
                is_allowed=False,
                schema_id=schema_id,
                reason="Schema ID is required"
            )
        
        return SchemaAccessValidation(
            is_allowed=True,
            schema_id=schema_id
        )
    
    async def check_knowledge_permission(
        self,
        query: str,
        user_id: str,
        tenant_id: str
    ) -> KnowledgePermissionCheck:
        """Check knowledge permission (policy decision)."""
        # MVP: Basic validation
        if not query:
            return KnowledgePermissionCheck(
                is_allowed=False,
                query=query,
                reason="Query is required"
            )
        
        return KnowledgePermissionCheck(
            is_allowed=True,
            query=query
        )
