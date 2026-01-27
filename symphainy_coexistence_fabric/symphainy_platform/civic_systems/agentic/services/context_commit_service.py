"""
Context Commit Service

Service for committing discovery context to authoritative committed context.

ARCHITECTURAL PRINCIPLE: Discovery context is provisional until committed.
Commit gate validates, applies policy, and creates authoritative context.

WHAT (Service Role): I commit discovery context to authoritative context
HOW (Service Implementation): I validate, apply policy, and store committed_context
"""

import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from datetime import datetime
from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext


class ContextCommitService:
    """
    Service for committing discovery context to authoritative context.
    
    Process:
    1. Validate discovery context structure
    2. Apply policy filtering (Smart City, etc.)
    3. Apply realm scoping
    4. Store in session.committed_context
    5. Log commit event
    """
    
    def __init__(self):
        """Initialize Context Commit Service."""
        self.logger = get_logger(self.__class__.__name__)
    
    async def commit_discovery_context(
        self,
        discovery_context: Dict[str, Any],
        context: ExecutionContext,
        user_edits: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Commit discovery context to authoritative context.
        
        Args:
            discovery_context: Discovery context (provisional)
            context: Execution context
            user_edits: Optional user edits to discovery context
        
        Returns:
            Dict with committed context
        """
        self.logger.info(f"Committing discovery context for session {context.session_id}")
        
        # Apply user edits if provided
        if user_edits:
            discovery_context = {**discovery_context, **user_edits}
            self.logger.debug("Applied user edits to discovery context")
        
        # Validate discovery context structure
        validated_context = self._validate_discovery_context(discovery_context)
        
        # Apply policy filtering (Smart City, etc.)
        policy_filtered = await self._apply_policy(validated_context, context)
        
        # Apply realm scoping
        realm_scoped = self._apply_realm_scoping(policy_filtered, context)
        
        # Create committed context
        committed_context = {
            "business_context": {
                "industry": realm_scoped.get("industry"),
                "systems": realm_scoped.get("systems", []),
                "constraints": realm_scoped.get("constraints", [])
            },
            "journey_goal": realm_scoped.get("goals", [""])[0] if realm_scoped.get("goals") else "",
            "human_preferences": realm_scoped.get("preferences", {
                "detail_level": "detailed",
                "wants_visuals": True,
                "explanation_style": "technical"
            }),
            "committed_at": datetime.now().isoformat(),
            "committed_by": getattr(context, 'user_id', 'system'),
            "source": "discovery_commit",
            "discovery_source": discovery_context.get("source", "unknown")
        }
        
        # Store in session state (committed namespace)
        if context and context.state_surface:
            session_state = await context.state_surface.get_session_state(
                context.session_id,
                context.tenant_id
            ) or {}
            
            session_state["committed_context"] = committed_context
            
            await context.state_surface.store_session_state(
                context.session_id,
                context.tenant_id,
                session_state
            )
            
            self.logger.info(f"✅ Committed context stored in session {context.session_id}")
            
            # Log commit event (if WAL available)
            if hasattr(context, 'wal') and context.wal:
                try:
                    await context.wal.append_event({
                        "type": "context_committed",
                        "session_id": context.session_id,
                        "tenant_id": context.tenant_id,
                        "committed_context": committed_context,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    self.logger.debug(f"Could not log commit event: {e}")
        
        return committed_context
    
    def _validate_discovery_context(self, discovery_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate discovery context structure.
        
        Args:
            discovery_context: Discovery context
        
        Returns:
            Validated discovery context
        """
        # Ensure required fields exist
        validated = {
            "industry": discovery_context.get("industry"),
            "systems": discovery_context.get("systems", []),
            "goals": discovery_context.get("goals", []),
            "constraints": discovery_context.get("constraints", []),
            "preferences": discovery_context.get("preferences", {
                "detail_level": "detailed",
                "wants_visuals": True,
                "explanation_style": "technical"
            }),
            "confidence": discovery_context.get("confidence", {}),
            "source": discovery_context.get("source", "unknown"),
            "discovered_at": discovery_context.get("discovered_at"),
            "status": discovery_context.get("status", "provisional")
        }
        
        # Validate types
        if validated["systems"] and not isinstance(validated["systems"], list):
            validated["systems"] = []
        if validated["goals"] and not isinstance(validated["goals"], list):
            validated["goals"] = []
        if validated["constraints"] and not isinstance(validated["constraints"], list):
            validated["constraints"] = []
        
        return validated
    
    async def _apply_policy(
        self,
        discovery_context: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Apply policy filtering (Smart City, etc.).
        
        Args:
            discovery_context: Discovery context
            context: Execution context
        
        Returns:
            Policy-filtered discovery context
        """
        # For MVP: No policy filtering (permissive)
        # In full implementation: Apply Smart City policy, tenant policies, etc.
        
        filtered = discovery_context.copy()
        
        # Example: Filter systems based on tenant policy
        # if context.tenant_id and has_policy(context.tenant_id, "allowed_systems"):
        #     allowed_systems = get_policy(context.tenant_id, "allowed_systems")
        #     filtered["systems"] = [s for s in filtered["systems"] if s in allowed_systems]
        
        return filtered
    
    def _apply_realm_scoping(
        self,
        discovery_context: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Apply realm scoping.
        
        Args:
            discovery_context: Discovery context
            context: Execution context
        
        Returns:
            Realm-scoped discovery context
        """
        # For MVP: No realm scoping
        # In full implementation: Scope context to specific realms based on solution_id
        
        scoped = discovery_context.copy()
        
        # Example: Scope systems to realm
        # if context.solution_id:
        #     realm_systems = get_realm_systems(context.solution_id)
        #     scoped["systems"] = [s for s in scoped["systems"] if s in realm_systems]
        
        return scoped
